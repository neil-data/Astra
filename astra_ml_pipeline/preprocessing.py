"""
preprocessing.py
=================
Data cleaning, feature engineering, scaling, and sliding-window
construction for the CME Arrival Time + Solar Flare Prediction LSTM.

Follows the spec:
- Remove missing values
- Normalize features using Min-Max or Standard Scaling
- Create sliding windows (chronological, no shuffling)
- Split data chronologically (train/val/test, no random shuffle — prevents
  lookahead leakage across the time series)
"""

import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.preprocessing import StandardScaler

_THIS_DIR = Path(__file__).resolve().parent            # ml/feature_engineering/
_ML_DIR = _THIS_DIR.parent                               # ml/
_DATA_PIPELINE_DIR = _ML_DIR / "data_pipeline"
_ARTIFACT_DIR = _ML_DIR / "artifacts"

# ──────────────────────────────────────────────────────────────────────
# Feature configuration — maps directly to the 12 core input parameters
# from the spec (timestamp excluded as a feature; used only for indexing)
# ──────────────────────────────────────────────────────────────────────

FEATURE_COLUMNS = [
    "xray_flux",
    "proton_flux",
    "electron_flux",
    "solar_wind_speed",
    "solar_wind_density",
    "solar_wind_temperature",
    "imf_bz",
    "imf_bt",
    "sunspot_number",
    "cme_speed",
    "cme_width",
    "f107_flux",
    # extra engineered context features below augment beyond the base 12
    "euv_flux",
    "magnetic_field_strength",
]

# Spec calls for ~12 features; the first 12 above match the spec list
# exactly. euv_flux / magnetic_field_strength are included as optional
# extras — toggle SPEC_MODE=True to use exactly the 12-feature spec shape.
SPEC_MODE = True
if SPEC_MODE:
    FEATURE_COLUMNS = FEATURE_COLUMNS[:12]

FLARE_CLASS_MAP = {"None": 0, "B": 1, "C": 2, "M": 3, "X": 4}
N_FLARE_CLASSES = len(FLARE_CLASS_MAP)


def load_raw(path=None):
    path = path or str(_DATA_PIPELINE_DIR / "synthetic_space_weather.parquet")
    df = pd.read_parquet(path)
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Remove / interpolate missing values. Real data sources have gaps
    from instrument dropouts; synthetic data is clean but we still run
    the full pipeline so it's a true drop-in replacement for real data."""
    df = df.copy()

    # Linear interpolation for short gaps (<= 2 hours at 5-min cadence = 24 rows)
    for col in FEATURE_COLUMNS:
        df[col] = df[col].interpolate(method="linear", limit=24, limit_direction="both")

    # Drop any remaining rows with NaN in feature columns (gaps too long to fill)
    before = len(df)
    df = df.dropna(subset=FEATURE_COLUMNS).reset_index(drop=True)
    dropped = before - len(df)
    if dropped:
        print(f"[clean] Dropped {dropped} rows with unrecoverable missing values")

    return df


def add_horizon_targets(df: pd.DataFrame, samples_per_hour: int, flare_horizon_hours: float = 1.0) -> pd.DataFrame:
    """Build supervised targets:
    1) flare_class_future — flare class label `flare_horizon_hours` ahead
       (classification). Spec example: "Past 24 hours -> LSTM -> Predict
       next hour flare", so the default horizon is 1 hour.
    2) cme_arrival_hours_target — hours-to-arrival, forward-filled from the
       most recent active CME in flight, decremented per step (regression).
       This lets every row (not just CME onset rows) carry a meaningful
       'time until arrival' countdown target whenever a CME is in transit.
    """
    df = df.copy()

    # ── Flare classification target: class `flare_horizon_hours` ahead ──
    flare_steps_ahead = int(round(flare_horizon_hours * samples_per_hour))
    df["flare_class_future_code"] = df["flare_class_code"].shift(-flare_steps_ahead)

    # ── CME arrival countdown target ──────────────────────────────────
    # For each CME onset row, propagate a decreasing "hours until arrival"
    # countdown forward through the rows until the predicted arrival index.
    countdown = np.full(len(df), np.nan)
    onset_rows = df.index[df["is_cme_onset"] == 1].tolist()

    for idx in onset_rows:
        transit_h = df.loc[idx, "cme_arrival_hours_true"]
        if pd.isna(transit_h):
            continue
        n_steps = int(round(transit_h * samples_per_hour))
        end_idx = min(idx + n_steps, len(df) - 1)
        for j, row_idx in enumerate(range(idx, end_idx + 1)):
            hours_remaining = transit_h - (j / samples_per_hour)
            if hours_remaining < 0:
                break
            # If multiple CMEs overlap, keep the soonest-arriving one
            if np.isnan(countdown[row_idx]) or hours_remaining < countdown[row_idx]:
                countdown[row_idx] = hours_remaining

    df["cme_arrival_hours_target"] = countdown
    # Rows with no CME currently in flight: target = -1 sentinel (handled
    # separately at train time via a "cme_in_flight" mask)
    df["cme_in_flight"] = (~df["cme_arrival_hours_target"].isna()).astype(int)
    df["cme_arrival_hours_target"] = df["cme_arrival_hours_target"].fillna(-1.0)

    return df


def make_sliding_windows(
    df: pd.DataFrame,
    sequence_length: int = 24,
    flare_horizon_steps: int = 1,
):
    """
    Build (samples, sequence_length, n_features) windows.

    Returns:
        X            -> (N, seq_len, n_features) input windows
        y_flare      -> (N,) future flare class code (classification target)
        y_arrival    -> (N,) hours-to-CME-arrival countdown (regression target,
                         -1 if no CME in flight at that point)
        cme_mask     -> (N,) boolean, True where a CME is actively in flight
                         (used to mask the regression loss to only meaningful rows)
        timestamps   -> (N,) timestamp marking the END of each window (prediction time)
    """
    feature_arr = df[FEATURE_COLUMNS].values.astype(np.float32)
    flare_target = df["flare_class_future_code"].values
    arrival_target = df["cme_arrival_hours_target"].values.astype(np.float32)
    in_flight = df["cme_in_flight"].values.astype(bool)
    timestamps = df["timestamp"].values

    n = len(df)
    X, y_flare, y_arrival, cme_mask, ts_out = [], [], [], [], []

    last_valid_start = n - sequence_length - flare_horizon_steps
    for start in range(0, max(last_valid_start, 0)):
        end = start + sequence_length
        target_idx = end - 1 + flare_horizon_steps  # the row whose future label we predict

        if target_idx >= n:
            continue
        if np.isnan(flare_target[target_idx]):
            continue  # near the end of the series, future label unavailable

        window = feature_arr[start:end]
        if np.isnan(window).any():
            continue

        X.append(window)
        y_flare.append(int(flare_target[target_idx]))
        y_arrival.append(arrival_target[end - 1])  # countdown AS OF the window's last timestep
        cme_mask.append(in_flight[end - 1])
        ts_out.append(timestamps[end - 1])

    return (
        np.array(X, dtype=np.float32),
        np.array(y_flare, dtype=np.int64),
        np.array(y_arrival, dtype=np.float32),
        np.array(cme_mask, dtype=bool),
        np.array(ts_out),
    )


def chronological_split(n, train_frac=0.70, val_frac=0.15):
    """Returns index boundaries for chronological train/val/test split.
    NEVER shuffle time series data — this would leak future information
    into training via overlapping windows and adjacent storm events."""
    train_end = int(n * train_frac)
    val_end = int(n * (train_frac + val_frac))
    return train_end, val_end


def fit_scaler(X_train: np.ndarray) -> StandardScaler:
    """Fit StandardScaler on TRAINING data only, flattened across the
    sequence dimension, then reused (transform-only) on val/test to
    prevent any leakage of val/test statistics into the scaler."""
    n, seq_len, n_features = X_train.shape
    scaler = StandardScaler()
    scaler.fit(X_train.reshape(-1, n_features))
    return scaler


def apply_scaler(X: np.ndarray, scaler: StandardScaler) -> np.ndarray:
    n, seq_len, n_features = X.shape
    flat = X.reshape(-1, n_features)
    flat_scaled = scaler.transform(flat)
    return flat_scaled.reshape(n, seq_len, n_features).astype(np.float32)


def run_preprocessing_pipeline(
    sequence_length: int = 24,
    samples_per_hour: int = 12,  # 5-min cadence -> 12 samples/hour
    save_dir: str = "./data",
):
    print("[1/6] Loading raw synthetic dataset...")
    df = load_raw()

    print("[2/6] Cleaning (interpolation + dropna)...")
    df = clean(df)

    print("[3/6] Building supervised targets (flare horizon + CME countdown)...")
    df = add_horizon_targets(df, samples_per_hour=samples_per_hour)

    print(f"[4/6] Building sliding windows (sequence_length={sequence_length})...")
    X, y_flare, y_arrival, cme_mask, timestamps = make_sliding_windows(
        df, sequence_length=sequence_length
    )
    print(f"        X shape: {X.shape}  (samples, timesteps, features)")
    print(f"        Flare class distribution in windows: "
          f"{dict(zip(*np.unique(y_flare, return_counts=True)))}")
    print(f"        Windows with CME in flight: {cme_mask.sum()} / {len(cme_mask)}")

    print("[5/6] Chronological train/val/test split...")
    train_end, val_end = chronological_split(len(X))
    X_train, X_val, X_test = X[:train_end], X[train_end:val_end], X[val_end:]
    yf_train, yf_val, yf_test = y_flare[:train_end], y_flare[train_end:val_end], y_flare[val_end:]
    ya_train, ya_val, ya_test = y_arrival[:train_end], y_arrival[train_end:val_end], y_arrival[val_end:]
    cm_train, cm_val, cm_test = cme_mask[:train_end], cme_mask[train_end:val_end], cme_mask[val_end:]
    ts_train, ts_val, ts_test = timestamps[:train_end], timestamps[train_end:val_end], timestamps[val_end:]

    print("[6/6] Fitting StandardScaler on TRAIN split only, applying to all splits...")
    scaler = fit_scaler(X_train)
    X_train_s = apply_scaler(X_train, scaler)
    X_val_s = apply_scaler(X_val, scaler)
    X_test_s = apply_scaler(X_test, scaler)

    joblib.dump(scaler, f"{save_dir}/../artifacts/feature_scaler.pkl")

    np.savez_compressed(
        f"{save_dir}/processed_windows.npz",
        X_train=X_train_s, X_val=X_val_s, X_test=X_test_s,
        yf_train=yf_train, yf_val=yf_val, yf_test=yf_test,
        ya_train=ya_train, ya_val=ya_val, ya_test=ya_test,
        cm_train=cm_train, cm_val=cm_val, cm_test=cm_test,
        ts_train=ts_train, ts_val=ts_val, ts_test=ts_test,
        feature_columns=np.array(FEATURE_COLUMNS),
    )

    print(f"\nSaved processed windows to {save_dir}/processed_windows.npz")
    print(f"Train: {len(X_train)}  Val: {len(X_val)}  Test: {len(X_test)}")
    print(f"Feature scaler saved to {save_dir}/../artifacts/feature_scaler.pkl")

    return {
        "X_train": X_train_s, "X_val": X_val_s, "X_test": X_test_s,
        "yf_train": yf_train, "yf_val": yf_val, "yf_test": yf_test,
        "ya_train": ya_train, "ya_val": ya_val, "ya_test": ya_test,
        "cm_train": cm_train, "cm_val": cm_val, "cm_test": cm_test,
    }


if __name__ == "__main__":
    run_preprocessing_pipeline(sequence_length=24, samples_per_hour=12)
