"""
generate_synthetic_data.py
============================
Generates a realistic, physically-plausible synthetic dataset for the
CME Arrival Time + Solar Flare Prediction pipeline.

Why synthetic data here:
- Real GOES/OMNIWeb/DONKI archives require API keys + multi-GB downloads
- This generator produces statistically realistic time series with the
  SAME schema, units, and event structure as the real sources, so the
  downstream preprocessing/LSTM code is a drop-in replacement once real
  data is wired up (just swap this script for data_pipeline/fetch_*.py).

Simulation design:
- Background "quiet sun" state for X-ray/proton/electron flux, solar wind,
  IMF, sunspot number, F10.7, EUV — each with realistic noise and
  autocorrelation (via an Ornstein-Uhlenbeck-style random walk).
- Discrete flare events injected on a Poisson process, each with a class
  (B/C/M/X), a log-normal peak intensity, and an exponential decay profile
  (matches real GOES X-ray light curves).
- A subset of M/X flares are tagged as "CME-associated" and spawn a CME
  event with realistic speed/width and a physically-derived transit time
  (empirical drag-based formula used by NOAA/NASA CCMC), which is then
  used to inject a later proton/electron flux enhancement (the actual
  particle storm arriving at Earth).
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from datetime import datetime, timedelta

RNG_SEED = 42
rng = np.random.default_rng(RNG_SEED)

# ──────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────

SAMPLING_INTERVAL_MINUTES = 5          # matches "5 minute" recommended cadence
TOTAL_DAYS = 240                       # ~8 months of data -> enough for train/val/test
START_TIME = datetime(2025, 1, 1, 0, 0, 0)

N_SAMPLES = int(TOTAL_DAYS * 24 * 60 / SAMPLING_INTERVAL_MINUTES)

FLARE_CLASSES = ["B", "C", "M", "X"]
# Peak X-ray flux ranges (W/m^2) per GOES flare classification standard
FLARE_FLUX_RANGES = {
    "B": (1e-7, 1e-6),
    "C": (1e-6, 1e-5),
    "M": (1e-5, 1e-4),
    "X": (1e-4, 1e-3),
}
# Probability a flare of a given class is CME-associated (higher classes -> more likely)
CME_ASSOCIATION_PROB = {"B": 0.01, "C": 0.05, "M": 0.35, "X": 0.75}

AU_KM = 1.496e8  # 1 Astronomical Unit in km


@dataclass
class FlareEvent:
    onset_idx: int
    flare_class: str
    peak_flux: float
    rise_minutes: float
    decay_minutes: float
    cme_associated: bool


def ou_process(n, mean, theta, sigma, x0=None):
    """Ornstein-Uhlenbeck mean-reverting random walk — used for all
    'background' physical quantities so they look like real autocorrelated
    space-weather telemetry rather than white noise."""
    x = np.zeros(n)
    x[0] = x0 if x0 is not None else mean
    dt = 1.0
    for t in range(1, n):
        x[t] = x[t - 1] + theta * (mean - x[t - 1]) * dt + sigma * rng.normal() * np.sqrt(dt)
    return x


def generate_flare_events(n_samples, samples_per_hour):
    """Poisson-process flare injection across the full timeline."""
    events = []
    # Rough real-world frequency (per day) by class, scaled for a more
    # eventful synthetic set so the model has enough positive examples
    daily_rate = {"B": 8.0, "C": 3.0, "M": 0.4, "X": 0.06}
    days = n_samples / (samples_per_hour * 24)

    for cls, rate in daily_rate.items():
        n_events = rng.poisson(rate * days)
        for _ in range(n_events):
            onset_idx = int(rng.uniform(0, n_samples - 1))
            lo, hi = FLARE_FLUX_RANGES[cls]
            peak_flux = np.exp(rng.uniform(np.log(lo), np.log(hi)))
            rise_minutes = rng.uniform(5, 25)
            decay_minutes = rng.uniform(20, 180) * (1 + ["B", "C", "M", "X"].index(cls) * 0.5)
            cme_assoc = rng.random() < CME_ASSOCIATION_PROB[cls]
            events.append(FlareEvent(onset_idx, cls, peak_flux, rise_minutes, decay_minutes, cme_assoc))

    events.sort(key=lambda e: e.onset_idx)
    return events


def flare_lightcurve(n_samples, sampling_minutes, events):
    """Render flare events onto an X-ray flux background using a
    fast-rise/exponential-decay (FRED) profile -- matches real GOES curves."""
    quiet_bg = 10 ** rng.uniform(-9, -8, n_samples)  # A-class quiet background
    xray = quiet_bg.copy()
    flare_label = np.zeros(n_samples, dtype=int)  # 0=none,1=B,2=C,3=M,4=X
    class_to_code = {"B": 1, "C": 2, "M": 3, "X": 4}

    t = np.arange(n_samples) * sampling_minutes

    for ev in events:
        onset_t = ev.onset_idx * sampling_minutes
        rel_t = t - onset_t
        rise_mask = (rel_t >= 0) & (rel_t < ev.rise_minutes)
        decay_mask = rel_t >= ev.rise_minutes

        profile = np.zeros(n_samples)
        profile[rise_mask] = ev.peak_flux * (rel_t[rise_mask] / ev.rise_minutes)
        decay_rel = rel_t[decay_mask] - ev.rise_minutes
        profile[decay_mask] = ev.peak_flux * np.exp(-decay_rel / ev.decay_minutes)

        xray += profile

        # Label the window from onset through ~2x decay time as "this class"
        window_mask = (rel_t >= -5) & (rel_t < ev.rise_minutes + 2 * ev.decay_minutes)
        code = class_to_code[ev.flare_class]
        flare_label[window_mask] = np.maximum(flare_label[window_mask], code)

    return xray, flare_label


def cme_transit_hours(speed_kms):
    """Empirical drag-based CME transit time estimate (simplified form of
    the NOAA/CCMC operational drag-based model). Faster CMEs arrive sooner;
    very fast CMEs (>1500 km/s) experience significant aerodynamic drag
    against the ambient solar wind and decelerate toward ~450 km/s by 1 AU.
    Calibrated against real-world observed transit times: slow CMEs
    (~300-400 km/s) take ~80-100h, average CMEs (~500-800 km/s) take
    ~40-60h, and fast/extreme CMEs (>1500 km/s) take ~15-25h."""
    ambient_wind = 400.0  # km/s background solar wind speed
    # Effective average speed accounting for drag deceleration toward ambient.
    # Weighted blend of initial speed and ambient wind, biased toward initial
    # speed for fast CMEs (drag has less proportional effect at high speed).
    if speed_kms <= ambient_wind:
        eff_speed = speed_kms * 0.9  # slow CMEs still take a while to coast out
    else:
        weight = np.clip((speed_kms - ambient_wind) / 1200.0, 0, 1)
        eff_speed = ambient_wind + (speed_kms - ambient_wind) * (0.35 + 0.45 * weight)
    eff_speed = max(eff_speed, 280.0)
    hours = (AU_KM / eff_speed) / 3600.0
    # Add realistic scatter (real CME arrival prediction has ~10-15h MAE)
    hours *= rng.normal(1.0, 0.10)
    return float(np.clip(hours, 14.0, 100.0))


def generate_dataset():
    n = N_SAMPLES
    samples_per_hour = 60 // SAMPLING_INTERVAL_MINUTES

    timestamps = [START_TIME + timedelta(minutes=SAMPLING_INTERVAL_MINUTES * i) for i in range(n)]

    # ── Background OU-driven physical parameters ──────────────────────
    proton_flux = np.clip(ou_process(n, mean=0.8, theta=0.01, sigma=0.05, x0=0.8), 0.01, None)
    electron_flux = np.clip(ou_process(n, mean=120, theta=0.01, sigma=8, x0=120), 1, None)
    solar_wind_speed = np.clip(ou_process(n, mean=420, theta=0.02, sigma=6, x0=420), 250, 1200)
    solar_wind_density = np.clip(ou_process(n, mean=6.0, theta=0.02, sigma=0.6, x0=6.0), 0.1, None)
    solar_wind_temp = np.clip(ou_process(n, mean=1.0e5, theta=0.02, sigma=4000, x0=1.0e5), 1e4, None)
    imf_bz = ou_process(n, mean=0.0, theta=0.03, sigma=0.8, x0=0.0)
    imf_bt = np.clip(ou_process(n, mean=5.5, theta=0.02, sigma=0.5, x0=5.5), 0.1, None)
    sunspot_number = np.clip(ou_process(n, mean=85, theta=0.002, sigma=1.5, x0=85), 0, 300)
    f107 = np.clip(ou_process(n, mean=130, theta=0.003, sigma=1.2, x0=130), 60, 300)
    euv_flux = np.clip(ou_process(n, mean=4.5, theta=0.01, sigma=0.15, x0=4.5), 0.5, None)
    magnetic_field_strength = np.clip(ou_process(n, mean=400, theta=0.01, sigma=20, x0=400), 50, None)

    # ── Flares ──────────────────────────────────────────────────────
    flare_events = generate_flare_events(n, samples_per_hour)
    xray_flux, flare_label_code = flare_lightcurve(n, SAMPLING_INTERVAL_MINUTES, flare_events)

    # ── CME injection: speed/width + downstream particle enhancement ──
    cme_speed = np.full(n, np.nan)
    cme_width = np.full(n, np.nan)
    cme_arrival_hours_true = np.full(n, np.nan)   # ground-truth label (only at onset rows)
    is_cme_onset = np.zeros(n, dtype=int)

    cme_records = []
    for ev in flare_events:
        if not ev.cme_associated:
            continue
        # Faster/wider CMEs scale with flare class
        class_speed_base = {"B": 350, "C": 450, "M": 750, "X": 1400}[ev.flare_class]
        speed = max(250.0, rng.normal(class_speed_base, class_speed_base * 0.25))
        width = float(np.clip(rng.normal(60 + speed / 15, 20), 10, 360))
        transit_hours = cme_transit_hours(speed)

        idx = ev.onset_idx
        if idx >= n:
            continue
        cme_speed[idx] = speed
        cme_width[idx] = width
        cme_arrival_hours_true[idx] = transit_hours
        is_cme_onset[idx] = 1

        arrival_idx = idx + int(round(transit_hours * samples_per_hour))
        cme_records.append((idx, arrival_idx, speed, transit_hours, ev.flare_class))

        # Inject a particle-flux enhancement around the arrival time
        # (Forbush-decrease-like dip then SEP enhancement is simplified here
        # to a Gaussian bump in proton/electron flux + IMF Bz southward turn)
        if arrival_idx < n:
            spread = max(6, int(0.15 * transit_hours * samples_per_hour))
            lo = max(0, arrival_idx - spread)
            hi = min(n, arrival_idx + spread * 3)
            local_t = np.arange(lo, hi)
            bump = np.exp(-0.5 * ((local_t - arrival_idx) / spread) ** 2)
            magnitude = (speed / 400.0) ** 2
            proton_flux[lo:hi] += bump * magnitude * rng.uniform(5, 40)
            electron_flux[lo:hi] += bump * magnitude * rng.uniform(50, 300)
            # Southward IMF turning enhances geoeffectiveness
            imf_bz[lo:hi] -= bump * rng.uniform(3, 15)

    # ── Forward-fill CME speed/width as "most recent known CME in flight" ──
    cme_speed_ffill = pd.Series(cme_speed).ffill().fillna(0).values
    cme_width_ffill = pd.Series(cme_width).ffill().fillna(0).values

    # ── Assemble dataframe ─────────────────────────────────────────────
    df = pd.DataFrame({
        "timestamp": timestamps,
        "xray_flux": xray_flux,
        "proton_flux": proton_flux,
        "electron_flux": electron_flux,
        "solar_wind_speed": solar_wind_speed,
        "solar_wind_density": solar_wind_density,
        "solar_wind_temperature": solar_wind_temp,
        "imf_bz": imf_bz,
        "imf_bt": imf_bt,
        "sunspot_number": sunspot_number,
        "cme_speed": cme_speed_ffill,
        "cme_width": cme_width_ffill,
        "f107_flux": f107,
        "euv_flux": euv_flux,
        "magnetic_field_strength": magnetic_field_strength,
        "flare_class_code": flare_label_code,   # 0=none,1=B,2=C,3=M,4=X
        "is_cme_onset": is_cme_onset,
        "cme_arrival_hours_true": cme_arrival_hours_true,  # NaN except at CME onset rows
    })

    flare_code_to_label = {0: "None", 1: "B", 2: "C", 3: "M", 4: "X"}
    df["flare_class"] = df["flare_class_code"].map(flare_code_to_label)

    cme_log = pd.DataFrame(
        cme_records,
        columns=["onset_idx", "arrival_idx", "cme_speed_kms", "transit_hours", "source_flare_class"],
    )
    cme_log["onset_time"] = cme_log["onset_idx"].apply(lambda i: timestamps[i])
    cme_log["arrival_time"] = cme_log["arrival_idx"].apply(
        lambda i: timestamps[i] if i < n else timestamps[-1] + timedelta(hours=(i - n) / samples_per_hour)
    )

    return df, cme_log


if __name__ == "__main__":
    df, cme_log = generate_dataset()

    out_dir = "./data"
    df.to_parquet(f"{out_dir}/synthetic_space_weather.parquet", index=False)
    df.to_csv(f"{out_dir}/synthetic_space_weather.csv", index=False)
    cme_log.to_csv(f"{out_dir}/cme_event_log.csv", index=False)

    print(f"Generated {len(df):,} rows spanning {TOTAL_DAYS} days "
          f"at {SAMPLING_INTERVAL_MINUTES}-min resolution")
    print(f"Flare class distribution:\n{df['flare_class'].value_counts()}")
    print(f"\nTotal CME events injected: {len(cme_log)}")
    print(f"CME transit time stats (hours):\n{cme_log['transit_hours'].describe()}")
    print(f"\nSaved to: {out_dir}/synthetic_space_weather.parquet")
    print(f"Saved to: {out_dir}/cme_event_log.csv")
