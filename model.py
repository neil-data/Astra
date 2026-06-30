"""
model.py
========
LSTM architecture for joint Solar Flare Classification + CME Arrival
Time Regression, following the spec exactly:

    Input Layer
      |
    LSTM (128)
      |
    Dropout (0.2)
      |
    LSTM (64)
      |
    Dense (32)
      |
    Dense (1)              <- regression head (CME arrival hours)
    Dense (4) + Softmax     <- classification head (flare class: B/C/M/X)

Implemented as a single shared-trunk, dual-head network: the LSTM trunk
learns a shared temporal representation of the last `sequence_length`
timesteps, and two task-specific heads branch off the final Dense(32)
layer. This mirrors real operational systems where flare and CME-arrival
forecasting draw on the same underlying solar-wind/X-ray feature window.
"""

import torch
import torch.nn as nn


class CMEFlareLSTM(nn.Module):
    def __init__(
        self,
        n_features: int = 12,
        lstm1_hidden: int = 128,
        lstm2_hidden: int = 64,
        dense_hidden: int = 32,
        dropout: float = 0.2,
        n_flare_classes: int = 5,   # None, B, C, M, X
    ):
        super().__init__()

        # ── LSTM (128) ──────────────────────────────────────────────
        self.lstm1 = nn.LSTM(
            input_size=n_features,
            hidden_size=lstm1_hidden,
            batch_first=True,
        )

        # ── Dropout (0.2) ───────────────────────────────────────────
        self.dropout1 = nn.Dropout(dropout)

        # ── LSTM (64) ───────────────────────────────────────────────
        self.lstm2 = nn.LSTM(
            input_size=lstm1_hidden,
            hidden_size=lstm2_hidden,
            batch_first=True,
        )
        self.dropout2 = nn.Dropout(dropout)

        # ── Dense (32) — shared trunk output ───────────────────────
        self.dense_shared = nn.Linear(lstm2_hidden, dense_hidden)
        self.relu = nn.ReLU()

        # ── Head A: CME Arrival Time Regression — Dense(1) ─────────
        self.regression_head = nn.Linear(dense_hidden, 1)

        # ── Head B: Flare Classification — Dense(4 classes used here: B/C/M/X)
        #    (None/quiet-sun is folded in as a 5th class so the model can
        #     also recognise "no flare expected" rather than being forced
        #     to always pick a flare class)
        self.classification_head = nn.Linear(dense_hidden, n_flare_classes)
        # Softmax applied via CrossEntropyLoss at train time (expects logits)

        # ── Auxiliary: "is a CME currently in flight" gate ──────────
        # Used to mask the regression loss — predicting arrival hours
        # only makes sense when a CME is actually in transit.
        self.cme_in_flight_head = nn.Linear(dense_hidden, 1)

    def forward(self, x):
        """
        x: (batch, sequence_length, n_features)
        Returns:
            flare_logits: (batch, n_flare_classes)   raw logits, softmax at inference
            arrival_hours: (batch, 1)                 predicted hours-to-arrival
            in_flight_logit: (batch, 1)                raw logit, sigmoid at inference
        """
        out, _ = self.lstm1(x)              # (batch, seq, 128)
        out = self.dropout1(out)
        out, _ = self.lstm2(out)             # (batch, seq, 64)
        out = self.dropout2(out)

        last_step = out[:, -1, :]            # (batch, 64) — final timestep representation
        shared = self.relu(self.dense_shared(last_step))  # (batch, 32)

        arrival_hours = self.regression_head(shared)        # (batch, 1)
        flare_logits = self.classification_head(shared)     # (batch, n_flare_classes)
        in_flight_logit = self.cme_in_flight_head(shared)   # (batch, 1)

        return flare_logits, arrival_hours, in_flight_logit

    @torch.no_grad()
    def predict(self, x):
        """Inference-time convenience wrapper: applies softmax/sigmoid
        and returns human-readable outputs."""
        self.eval()
        flare_logits, arrival_hours, in_flight_logit = self.forward(x)
        flare_probs = torch.softmax(flare_logits, dim=-1)
        flare_pred = torch.argmax(flare_probs, dim=-1)
        in_flight_prob = torch.sigmoid(in_flight_logit).squeeze(-1)
        return {
            "flare_class_pred": flare_pred,
            "flare_probs": flare_probs,
            "cme_arrival_hours_pred": arrival_hours.squeeze(-1),
            "cme_in_flight_prob": in_flight_prob,
        }


if __name__ == "__main__":
    # Quick architecture sanity check
    model = CMEFlareLSTM(n_features=12)
    dummy = torch.randn(8, 24, 12)  # (batch=8, seq_len=24, features=12) per spec
    flare_logits, arrival_hours, in_flight = model(dummy)
    print("flare_logits shape :", flare_logits.shape)   # (8, 5)
    print("arrival_hours shape:", arrival_hours.shape)  # (8, 1)
    print("in_flight shape    :", in_flight.shape)      # (8, 1)

    n_params = sum(p.numel() for p in model.parameters())
    print(f"\nTotal trainable parameters: {n_params:,}")
