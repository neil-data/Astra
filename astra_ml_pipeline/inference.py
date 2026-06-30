"""
inference.py
============
Production inference wrapper for the CMEFlareLSTM model — this is the
module that gets imported by ASTRA's FastAPI backend
(backend/app/services/inference.py) to serve the /predict and /forecast
endpoints with live CME arrival + flare class predictions.

Usage:
    from inference import CMEFlarePredictor

    predictor = CMEFlarePredictor()
    result = predictor.predict_from_window(feature_window)  # (24, 12) array
    # or, for a raw recent dataframe:
    result = predictor.predict_from_recent_data(df_last_24h)
"""

import numpy as np
import torch
import joblib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from model import CMEFlareLSTM

ARTIFACT_DIR = "./artifacts"
FEATURE_COLUMNS = [
    "xray_flux", "proton_flux", "electron_flux",
    "solar_wind_speed", "solar_wind_density", "solar_wind_temperature",
    "imf_bz", "imf_bt", "sunspot_number",
    "cme_speed", "cme_width", "f107_flux",
]
FLARE_CLASS_NAMES = ["None", "B", "C", "M", "X"]
ARRIVAL_SCALE_HOURS = 100.0
SEQUENCE_LENGTH = 24


class CMEFlarePredictor:
    def __init__(self, model_path=None, scaler_path=None, device="cpu"):
        model_path = model_path or f"{ARTIFACT_DIR}/cme_flare_lstm.pt"
        scaler_path = scaler_path or f"{ARTIFACT_DIR}/feature_scaler.pkl"

        self.device = torch.device(device)
        self.scaler = joblib.load(scaler_path)

        self.model = CMEFlareLSTM(n_features=len(FEATURE_COLUMNS))
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()

    def _scale(self, window: np.ndarray) -> np.ndarray:
        """window: (sequence_length, n_features) raw values -> scaled."""
        flat = window.reshape(-1, window.shape[-1])
        scaled = self.scaler.transform(flat)
        return scaled.reshape(window.shape).astype(np.float32)

    @torch.no_grad()
    def predict_from_window(self, window: np.ndarray) -> dict:
        """
        window: numpy array of shape (sequence_length=24, n_features=12),
                in the same raw units/order as FEATURE_COLUMNS, most-recent
                timestep LAST (i.e. window[-1] = now).
        """
        if window.shape != (SEQUENCE_LENGTH, len(FEATURE_COLUMNS)):
            raise ValueError(
                f"Expected window shape ({SEQUENCE_LENGTH}, {len(FEATURE_COLUMNS)}), "
                f"got {window.shape}"
            )

        scaled = self._scale(window)
        x = torch.from_numpy(scaled).unsqueeze(0).to(self.device)  # (1, 24, 12)

        out = self.model.predict(x)

        flare_idx = int(out["flare_class_pred"].item())
        flare_probs = out["flare_probs"].squeeze(0).cpu().numpy()
        arrival_hours = float(out["cme_arrival_hours_pred"].item()) * ARRIVAL_SCALE_HOURS
        in_flight_prob = float(out["cme_in_flight_prob"].item())

        return {
            "predicted_flare_class": FLARE_CLASS_NAMES[flare_idx],
            "flare_class_probabilities": {
                cls: round(float(p), 4) for cls, p in zip(FLARE_CLASS_NAMES, flare_probs)
            },
            "cme_in_flight_probability": round(in_flight_prob, 4),
            "cme_predicted_arrival_hours": round(max(arrival_hours, 0.0), 2),
            "cme_predicted_arrival_note": (
                "Meaningful only when cme_in_flight_probability is high; "
                "interpret as 'if a CME is currently in transit, this is "
                "the estimated remaining hours until Earth arrival.'"
            ),
        }

    def predict_from_recent_data(self, df, feature_columns=None) -> dict:
        """
        df: pandas DataFrame with at least the last 24 rows of feature data,
            columns matching FEATURE_COLUMNS (or pass feature_columns to map).
        """
        cols = feature_columns or FEATURE_COLUMNS
        if len(df) < SEQUENCE_LENGTH:
            raise ValueError(f"Need at least {SEQUENCE_LENGTH} rows, got {len(df)}")

        window = df[cols].tail(SEQUENCE_LENGTH).values.astype(np.float32)
        return self.predict_from_window(window)


if __name__ == "__main__":
    # Smoke test: run inference on the last window of the test split
    import pandas as pd

    print("Loading predictor...")
    predictor = CMEFlarePredictor()

    df = pd.read_parquet("/home/claude/cme_predictor/data/synthetic_space_weather.parquet")
    df = df.sort_values("timestamp").reset_index(drop=True)

    # Grab a window right before a known CME onset for a sanity check
    cme_log = pd.read_csv("/home/claude/cme_predictor/data/cme_event_log.csv")
    sample_onset_idx = int(cme_log.iloc[len(cme_log) // 2]["onset_idx"])

    window_df = df.iloc[max(0, sample_onset_idx - SEQUENCE_LENGTH):sample_onset_idx]
    if len(window_df) == SEQUENCE_LENGTH:
        result = predictor.predict_from_recent_data(window_df)
        print("\nPrediction just before a known CME onset:")
        print(json.dumps(result, indent=2))

        actual = cme_log.iloc[len(cme_log) // 2]
        print(f"\nActual: flare_class={actual['source_flare_class']}, "
              f"true_transit_hours={actual['transit_hours']:.1f}")

    # Also test on a quiet-sun window
    quiet_window = df.iloc[100:100 + SEQUENCE_LENGTH]
    result_quiet = predictor.predict_from_recent_data(quiet_window)
    print("\nPrediction on a quiet-sun window (no CME expected):")
    print(json.dumps(result_quiet, indent=2))
