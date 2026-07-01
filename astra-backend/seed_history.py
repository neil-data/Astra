"""
seed_history.py
================
Pushes synthetic-but-realistic space weather observations to the live
ASTRA backend via POST /api/v1/history, so /api/v1/forecast/* has data
to work with.

Usage:
    pip install requests --break-system-packages   (if not already installed)
    python seed_history.py
"""

import requests
import numpy as np
from datetime import datetime, timedelta

# ── Config ──────────────────────────────────────────────────────────
API_BASE = "https://astra-backend-u2uf.onrender.com/api/v1"
HISTORY_ENDPOINT = f"{API_BASE}/history"

DAYS_BACK = 7                # how much history to backfill
INTERVAL_MINUTES = 60        # one observation per hour
SOURCE = "NOAA"               # NOAA, GOES, DONKI, or DSCOVR

rng = np.random.default_rng(42)


def ou_step(prev, mean, theta, sigma):
    return prev + theta * (mean - prev) + sigma * rng.normal()


def generate_observations():
    n = int(DAYS_BACK * 24 * 60 / INTERVAL_MINUTES)
    start = datetime.utcnow() - timedelta(days=DAYS_BACK)

    solar_wind_speed = 420.0
    solar_wind_density = 6.0
    bz = 0.0
    bt = 5.5
    kp = 3.0
    ap = 15.0
    p10 = 0.8
    p50 = 0.3
    p100 = 0.1

    rows = []
    for i in range(n):
        ts = start + timedelta(minutes=INTERVAL_MINUTES * i)

        solar_wind_speed = float(np.clip(ou_step(solar_wind_speed, 420, 0.05, 8), 250, 900))
        solar_wind_density = float(np.clip(ou_step(solar_wind_density, 6.0, 0.05, 0.8), 0.1, 30))
        bz = float(np.clip(ou_step(bz, 0.0, 0.08, 1.2), -20, 20))
        bt = float(np.clip(ou_step(bt, 5.5, 0.05, 0.6), 0.1, 40))
        kp = float(np.clip(ou_step(kp, 3.0, 0.05, 0.6), 0, 9))
        ap = float(np.clip(ou_step(ap, 15, 0.05, 3), 0, 400))
        p10 = float(np.clip(ou_step(p10, 0.8, 0.05, 0.1), 0.01, 1000))
        p50 = float(np.clip(ou_step(p50, 0.3, 0.05, 0.05), 0.01, 500))
        p100 = float(np.clip(ou_step(p100, 0.1, 0.05, 0.02), 0.01, 200))

        storm_level = None
        if kp >= 7:
            storm_level = "G3"
        elif kp >= 6:
            storm_level = "G2"
        elif kp >= 5:
            storm_level = "G1"

        rows.append({
            "source": SOURCE,
            "observation_time": ts.isoformat(),
            "solar_wind_speed": round(solar_wind_speed, 2),
            "solar_wind_density": round(solar_wind_density, 2),
            "bz_component": round(bz, 2),
            "bt_total": round(bt, 2),
            "kp_index": round(kp, 2),
            "ap_index": round(ap, 2),
            "proton_flux_10mev": round(p10, 4),
            "proton_flux_50mev": round(p50, 4),
            "proton_flux_100mev": round(p100, 4),
            "geomagnetic_storm_level": storm_level,
            "raw_payload": {"synthetic": True}
        })

    return rows


def push_observations(rows):
    ok, skipped, failed = 0, 0, 0
    for row in rows:
        try:
            resp = requests.post(HISTORY_ENDPOINT, json=row, timeout=15)
            if resp.status_code == 201:
                ok += 1
            elif resp.status_code == 409:
                skipped += 1  # already exists
            else:
                failed += 1
                print(f"FAILED [{resp.status_code}] {row['observation_time']}: {resp.text}")
        except requests.RequestException as e:
            failed += 1
            print(f"ERROR {row['observation_time']}: {e}")

    print(f"\nDone. Inserted: {ok}, Skipped (duplicates): {skipped}, Failed: {failed}")


if __name__ == "__main__":
    print(f"Generating {DAYS_BACK} days of synthetic observations at {INTERVAL_MINUTES}-min intervals...")
    rows = generate_observations()
    print(f"Pushing {len(rows)} observations to {HISTORY_ENDPOINT} ...")
    push_observations(rows)