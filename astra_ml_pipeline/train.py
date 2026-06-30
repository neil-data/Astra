"""
train.py
========
Trains the dual-head CMEFlareLSTM model with:

  Loss functions (per spec):
    - Classification: Categorical Cross-Entropy
    - Regression:      MSE (primary) + MAE (tracked)
  Optimizer: Adam, lr=0.001 (per spec)

  Evaluation metrics (per spec):
    - Regression:     MAE, RMSE, R²
    - Classification: Accuracy, Precision, Recall, F1, ROC-AUC

Multi-task loss combines both heads:
    total_loss = w_flare * CE(flare_logits, y_flare)
               + w_arrival * MaskedMSE(arrival_pred, y_arrival, cme_mask)
               + w_inflight * BCE(in_flight_logit, cme_mask)

The arrival regression loss is MASKED to only the rows where a CME is
actually in flight (cm_mask=True) — predicting "hours until arrival"
is meaningless when no CME exists, so those rows don't contribute
gradient to the regression head.
"""

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, mean_absolute_error, mean_squared_error, r2_score,
    confusion_matrix,
)
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from model import CMEFlareLSTM

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
DATA_PATH = "./data/processed_windows.npz"
ARTIFACT_DIR = "./artifacts"
FLARE_CLASS_NAMES = ["None", "B", "C", "M", "X"]
ARRIVAL_SCALE_HOURS = 100.0  # normalises arrival-hours target to roughly [0,1]
                              # so its MSE loss is on a comparable scale to
                              # the classification cross-entropy loss


class WindowDataset(Dataset):
    def __init__(self, X, y_flare, y_arrival, cme_mask):
        self.X = torch.from_numpy(X).float()
        self.y_flare = torch.from_numpy(y_flare).long()
        # Normalize arrival hours to roughly [0, 1] scale (divide by 100h
        # cap) so the regression loss is comparable in magnitude to the
        # classification cross-entropy loss during multi-task training.
        # Inverted back to hours at evaluation/inference time.
        y_arrival_scaled = np.where(y_arrival >= 0, y_arrival / ARRIVAL_SCALE_HOURS, -1.0)
        self.y_arrival = torch.from_numpy(y_arrival_scaled).float()
        self.cme_mask = torch.from_numpy(cme_mask.astype(np.float32)).float()

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y_flare[idx], self.y_arrival[idx], self.cme_mask[idx]


def load_data(batch_size=256):
    data = np.load(DATA_PATH, allow_pickle=True)
    train_ds = WindowDataset(data["X_train"], data["yf_train"], data["ya_train"], data["cm_train"])
    val_ds = WindowDataset(data["X_val"], data["yf_val"], data["ya_val"], data["cm_val"])
    test_ds = WindowDataset(data["X_test"], data["yf_test"], data["ya_test"], data["cm_test"])

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)   # shuffle OK within
                                                                                 # train split only —
                                                                                 # windows themselves
                                                                                 # were built chronologically
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False)
    return train_loader, val_loader, test_loader, data["feature_columns"]


def compute_multitask_loss(flare_logits, arrival_pred, in_flight_logit,
                            y_flare, y_arrival, cme_mask,
                            ce_loss_fn, mse_loss_fn, bce_loss_fn,
                            w_flare=1.0, w_arrival=1.0, w_inflight=0.3):
    loss_flare = ce_loss_fn(flare_logits, y_flare)

    loss_inflight = bce_loss_fn(in_flight_logit.squeeze(-1), cme_mask)

    # Masked regression loss: only rows where CME is in flight
    mask = cme_mask.bool()
    if mask.sum() > 0:
        loss_arrival = mse_loss_fn(arrival_pred.squeeze(-1)[mask], y_arrival[mask])
    else:
        loss_arrival = torch.tensor(0.0, device=flare_logits.device)

    total = w_flare * loss_flare + w_arrival * loss_arrival + w_inflight * loss_inflight
    return total, loss_flare.item(), loss_arrival.item(), loss_inflight.item()


def run_epoch(model, loader, optimizer, ce_loss_fn, mse_loss_fn, bce_loss_fn, train=True):
    model.train() if train else model.eval()
    total_loss, total_flare, total_arrival, total_inflight = 0.0, 0.0, 0.0, 0.0
    n_batches = 0

    context = torch.enable_grad() if train else torch.no_grad()
    with context:
        for X, y_flare, y_arrival, cme_mask in loader:
            X = X.to(DEVICE)
            y_flare = y_flare.to(DEVICE)
            y_arrival = y_arrival.to(DEVICE)
            cme_mask = cme_mask.to(DEVICE)

            if train:
                optimizer.zero_grad()

            flare_logits, arrival_pred, in_flight_logit = model(X)
            loss, lf, la, li = compute_multitask_loss(
                flare_logits, arrival_pred, in_flight_logit,
                y_flare, y_arrival, cme_mask,
                ce_loss_fn, mse_loss_fn, bce_loss_fn,
            )

            if train:
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()

            total_loss += loss.item()
            total_flare += lf
            total_arrival += la
            total_inflight += li
            n_batches += 1

    return (total_loss / n_batches, total_flare / n_batches,
            total_arrival / n_batches, total_inflight / n_batches)


def compute_class_weights(loader, n_classes=5):
    """Inverse-frequency class weights for the flare CE loss, computed
    from the training set so the rare X-class flares aren't drowned out
    by the abundant C-class examples."""
    counts = np.zeros(n_classes)
    for _, y_flare, _, _ in loader:
        for c in y_flare.numpy():
            counts[c] += 1
    counts = np.maximum(counts, 1)
    weights = counts.sum() / (n_classes * counts)
    return torch.tensor(weights, dtype=torch.float32)


@torch.no_grad()
def evaluate_full(model, loader):
    """Full evaluation suite matching the spec metrics."""
    model.eval()
    all_flare_true, all_flare_pred, all_flare_probs = [], [], []
    all_arrival_true, all_arrival_pred, all_inflight_mask = [], [], []

    for X, y_flare, y_arrival, cme_mask in loader:
        X = X.to(DEVICE)
        out = model.predict(X)

        all_flare_true.append(y_flare.numpy())
        all_flare_pred.append(out["flare_class_pred"].cpu().numpy())
        all_flare_probs.append(out["flare_probs"].cpu().numpy())

        all_arrival_true.append(y_arrival.numpy())
        all_arrival_pred.append(out["cme_arrival_hours_pred"].cpu().numpy())
        all_inflight_mask.append(cme_mask.numpy().astype(bool))

    y_flare_true = np.concatenate(all_flare_true)
    y_flare_pred = np.concatenate(all_flare_pred)
    flare_probs = np.concatenate(all_flare_probs)

    y_arrival_true = np.concatenate(all_arrival_true) * ARRIVAL_SCALE_HOURS
    y_arrival_pred = np.concatenate(all_arrival_pred) * ARRIVAL_SCALE_HOURS
    inflight_mask = np.concatenate(all_inflight_mask)

    # ── Classification metrics ─────────────────────────────────────
    acc = accuracy_score(y_flare_true, y_flare_pred)
    precision = precision_score(y_flare_true, y_flare_pred, average="macro", zero_division=0)
    recall = recall_score(y_flare_true, y_flare_pred, average="macro", zero_division=0)
    f1 = f1_score(y_flare_true, y_flare_pred, average="macro", zero_division=0)

    try:
        roc_auc = roc_auc_score(y_flare_true, flare_probs, multi_class="ovr", average="macro")
    except ValueError:
        roc_auc = float("nan")  # if a class is missing from this split

    cm = confusion_matrix(y_flare_true, y_flare_pred, labels=list(range(len(FLARE_CLASS_NAMES))))

    # ── Regression metrics (only on rows where a CME is actually in flight) ──
    if inflight_mask.sum() > 0:
        yat = y_arrival_true[inflight_mask]
        yap = y_arrival_pred[inflight_mask]
        mae = mean_absolute_error(yat, yap)
        rmse = float(np.sqrt(mean_squared_error(yat, yap)))
        r2 = r2_score(yat, yap)
    else:
        mae = rmse = r2 = float("nan")

    return {
        "classification": {
            "accuracy": float(acc),
            "precision_macro": float(precision),
            "recall_macro": float(recall),
            "f1_macro": float(f1),
            "roc_auc_macro_ovr": float(roc_auc),
            "confusion_matrix": cm.tolist(),
            "class_names": FLARE_CLASS_NAMES,
        },
        "regression": {
            "mae_hours": float(mae),
            "rmse_hours": float(rmse),
            "r2": float(r2),
            "n_evaluated_inflight_rows": int(inflight_mask.sum()),
        },
    }


def train_model(epochs=25, batch_size=256, lr=0.001, patience=6):
    print(f"Using device: {DEVICE}")
    train_loader, val_loader, test_loader, feature_columns = load_data(batch_size=batch_size)
    n_features = len(feature_columns)
    print(f"Features ({n_features}): {list(feature_columns)}")

    model = CMEFlareLSTM(n_features=n_features).to(DEVICE)

    # ── Loss functions per spec ─────────────────────────────────────
    class_weights = compute_class_weights(train_loader, n_classes=len(FLARE_CLASS_NAMES)).to(DEVICE)
    print(f"Flare class weights (inverse-frequency): {class_weights.cpu().numpy().round(3)}")
    ce_loss_fn = nn.CrossEntropyLoss(weight=class_weights)  # Categorical Cross-Entropy (classification)
    mse_loss_fn = nn.MSELoss()              # MSE (regression, primary loss)
    bce_loss_fn = nn.BCEWithLogitsLoss()    # auxiliary in-flight gate

    # ── Optimizer per spec: Adam, lr=0.001 ──────────────────────────
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=3
    )

    best_val_loss = float("inf")
    best_state = None
    epochs_no_improve = 0
    history = []

    for epoch in range(1, epochs + 1):
        train_loss, train_lf, train_la, train_li = run_epoch(
            model, train_loader, optimizer, ce_loss_fn, mse_loss_fn, bce_loss_fn, train=True
        )
        val_loss, val_lf, val_la, val_li = run_epoch(
            model, val_loader, optimizer, ce_loss_fn, mse_loss_fn, bce_loss_fn, train=False
        )
        scheduler.step(val_loss)

        history.append({
            "epoch": epoch, "train_loss": train_loss, "val_loss": val_loss,
            "train_flare_ce": train_lf, "val_flare_ce": val_lf,
            "train_arrival_mse": train_la, "val_arrival_mse": val_la,
        })

        print(f"Epoch {epoch:02d}/{epochs} | "
              f"train_loss={train_loss:.4f} val_loss={val_loss:.4f} | "
              f"val_flare_CE={val_lf:.4f} val_arrival_MSE={val_la:.4f}")

        if val_loss < best_val_loss - 1e-4:
            best_val_loss = val_loss
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
            epochs_no_improve = 0
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= patience:
                print(f"Early stopping at epoch {epoch} (no improvement for {patience} epochs)")
                break

    # Restore best checkpoint
    if best_state is not None:
        model.load_state_dict(best_state)

    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    torch.save(model.state_dict(), f"{ARTIFACT_DIR}/cme_flare_lstm.pt")
    with open(f"{ARTIFACT_DIR}/training_history.json", "w") as f:
        json.dump(history, f, indent=2)

    print(f"\nSaved best model to {ARTIFACT_DIR}/cme_flare_lstm.pt")

    # ── Final evaluation on test set ────────────────────────────────
    print("\n" + "=" * 60)
    print("FINAL TEST SET EVALUATION")
    print("=" * 60)
    metrics = evaluate_full(model, test_loader)

    print("\n--- Classification (Flare Class) ---")
    for k, v in metrics["classification"].items():
        if k not in ("confusion_matrix", "class_names"):
            print(f"  {k:20s}: {v:.4f}" if isinstance(v, float) else f"  {k:20s}: {v}")
    print(f"  confusion_matrix (rows=true, cols=pred, order={FLARE_CLASS_NAMES}):")
    for row in metrics["classification"]["confusion_matrix"]:
        print("   ", row)

    print("\n--- Regression (CME Arrival Hours) ---")
    for k, v in metrics["regression"].items():
        print(f"  {k:30s}: {v:.4f}" if isinstance(v, float) else f"  {k:30s}: {v}")

    with open(f"{ARTIFACT_DIR}/test_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\nSaved full test metrics to {ARTIFACT_DIR}/test_metrics.json")

    return model, metrics


if __name__ == "__main__":
    train_model(epochs=25, batch_size=256, lr=0.001, patience=6)
