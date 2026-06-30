"""
run_forecast.py
================
Bridge script: pulls the latest 24 observations from PostgreSQL,
maps them to the 12 features the CMEFlareLSTM model expects,
runs inference, and writes the resulting forecast into the
space_weather_forecasts table via the ASTRA backend's REST API
(POST /api/v1/forecast is not used here directly because it
runs its own mock logic — instead we insert the row directly
via asyncpg so the real model output is what gets stored).

Usage:
    python run_forecast.py
    python run_forecast.py --loop --interval 300   # run every 5 min
"""

import argparse
import asyncio
import os
from datetime import datetime, timezone

import numpy as np
import asyncpg

from inference import CMEFlarePredictor, FEATURE_COLUMNS, SEQUENCE_LENGTH

DATABASE_URL = os.getenv(
    "DATABASE_URL_SYNC",
    "postgresql://astra_user:astra_pass@localhost:5432/astra_db"
)

# Map model's 12 expected features to what's actually available in the
# raw_space_weather_observations table. Anything not present gets a
# sane default constant (these are columns M2's data_pipeline doesn't
# currently populate, e.g. xray_flux, electron_flux, sunspot_number).
DB_COLUMN_MAP = {
    "xray_flux": None,                 # not in DB -> default
    "proton_flux": "proton_flux_10mev",
    "electron_flux": None,             # not in DB -> default
    "solar_wind_speed": "solar_wind_speed",
    "solar_wind_density": "solar_wind_density",
    "solar_wind_temperature": None,    # not in DB -> default
    "imf_bz": "bz_component",
    "imf_bt": "bt_total",
    "sunspot_number": None,            # not in DB -> default
    "cme_speed": None,                 # not in DB -> default
    "cme_width": None,                 # not in DB -> default
    "f107_flux": None,                 # not in DB -> default
}

DEFAULT_VALUES = {
    "xray_flux": 1e-7,
    "electron_flux": 100.0,
    "solar_wind_temperature": 100000.0,
    "sunspot_number": 50.0,
    "cme_speed": 400.0,
    "cme_width": 30.0,
    "f107_flux": 120.0,
}


async def fetch_recent_observations(conn, limit=SEQUENCE_LENGTH):
    rows = await conn.fetch(
        """
        SELECT observation_time, solar_wind_speed, solar_wind_density,
               bz_component, bt_total, proton_flux_10mev
        FROM raw_space_weather_observations
        ORDER BY observation_time DESC
        LIMIT $1
        """,
        limit
    )
    return list(reversed(rows))  # chronological order, oldest first


def build_feature_window(rows) -> np.ndarray:
    """Convert DB rows into the (24, 12) array the model expects."""
    window = np.zeros((SEQUENCE_LENGTH, len(FEATURE_COLUMNS)), dtype=np.float32)

    # If we have fewer than 24 rows, repeat the earliest row to pad
    if len(rows) == 0:
        raise ValueError("No observations in database yet.")

    padded_rows = rows.copy()
    while len(padded_rows) < SEQUENCE_LENGTH:
        padded_rows.insert(0, padded_rows[0])
    padded_rows = padded_rows[-SEQUENCE_LENGTH:]

    for t, row in enumerate(padded_rows):
        for f_idx, feature_name in enumerate(FEATURE_COLUMNS):
            db_col = DB_COLUMN_MAP.get(feature_name)
            if db_col is None:
                window[t, f_idx] = DEFAULT_VALUES.get(feature_name, 0.0)
            else:
                value = row[db_col]
                window[t, f_idx] = float(value) if value is not None else DEFAULT_VALUES.get(feature_name, 0.0)

    return window


def map_flare_to_risk(predicted_flare_class: str, cme_in_flight_prob: float) -> str:
    """Translate model output into ASTRA's LOW/MEDIUM/HIGH/EXTREME scale."""
    flare_risk = {"None": "LOW", "B": "LOW", "C": "MEDIUM", "M": "HIGH", "X": "EXTREME"}
    base = flare_risk.get(predicted_flare_class, "LOW")

    if cme_in_flight_prob >= 0.7 and base in ("LOW", "MEDIUM"):
        # an incoming CME bumps risk up a tier even if flare class is mild
        bump = {"LOW": "MEDIUM", "MEDIUM": "HIGH"}
        base = bump.get(base, base)

    return base


async def insert_forecast(conn, horizon_minutes, result, risk_level):
    await conn.execute(
        """
        INSERT INTO space_weather_forecasts
            (feature_id, forecast_time, prediction_horizon_minutes,
             predicted_kp_index, predicted_proton_flux,
             predicted_solar_storm_probability, risk_level,
             confidence_score, model_version)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """,
        None,
        datetime.now(timezone.utc).replace(tzinfo=None),
        horizon_minutes,
        None,  # predicted_kp_index not produced by this model directly
        None,  # predicted_proton_flux not produced by this model directly
        result["cme_in_flight_probability"],
        risk_level,
        max(result["flare_class_probabilities"].values()),
        "cme_flare_lstm_v1"
    )


async def run_once():
    predictor = CMEFlarePredictor()
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        rows = await fetch_recent_observations(conn)
        window = build_feature_window(rows)
        result = predictor.predict_from_window(window)

        risk_level = map_flare_to_risk(
            result["predicted_flare_class"],
            result["cme_in_flight_probability"]
        )

        print("Prediction:", result)
        print("Mapped risk level:", risk_level)

        for horizon in (60, 180, 1440):
            await insert_forecast(conn, horizon, result, risk_level)

        print(f"Inserted forecasts for horizons 60/180/1440 at {datetime.now(timezone.utc)}")

    finally:
        await conn.close()


async def run_loop(interval_seconds: int):
    while True:
        try:
            await run_once()
        except Exception as e:
            print(f"run_forecast error: {e}")
        await asyncio.sleep(interval_seconds)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--loop", action="store_true", help="Run continuously")
    parser.add_argument("--interval", type=int, default=300, help="Seconds between runs in loop mode")
    args = parser.parse_args()

    if args.loop:
        asyncio.run(run_loop(args.interval))
    else:
        asyncio.run(run_once())