# ASTRA — Data Pipeline

> **Advanced Space Terrain & Radiation Analytics**  
> ISRO Hackathon 2026 · M2 Data Engineer Module

---

## Overview

The ASTRA Data Pipeline is the backbone of the ASTRA system. It continuously ingests live space radiation and solar weather data from three real satellite and government data sources, stores it in a time-series database, and prepares engineered features for the ML forecasting layer.

Once started, the pipeline runs fully autonomously — fetching, storing, and processing real data every 15 minutes with zero manual intervention.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    DATA SOURCES                         │
│  NOAA SWPC        GOES-16 Satellite    NASA DONKI       │
│  (Solar wind,     (Proton/Electron     (CME Events,     │
│   Kp Index, IMF)   Particle Flux)       Solar Flares)   │
└────────┬──────────────────┬──────────────────┬──────────┘
         │                  │                  │
         ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────┐
│                   APScheduler                           │
│         fetch_noaa   fetch_goes   fetch_donki           │
│         (15 min)     (15 min)     (60 min)              │
└─────────────────────────────┬───────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│              PostgreSQL 16 + TimescaleDB                │
│   raw_observations    processed_features                │
│   forecast_results    cme_events    flare_events        │
└───────────────────────┬─────────────────────────────────┘
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
┌─────────────────────┐  ┌───────────────────┐
│  Feature Engineering │  │    Redis Cache    │
│  (lag + rolling)     │  │  (hot features)   │
│  every 20 min        │  │  TTL: 30 min      │
└─────────────────────┘  └───────────────────┘
```

---

## Tech Stack

| Component       | Technology                    | Purpose                          |
|-----------------|-------------------------------|----------------------------------|
| Database        | PostgreSQL 16 + TimescaleDB   | Time-series storage              |
| Cache           | Redis 7                       | Hot feature store for ML         |
| HTTP Client     | httpx (async)                 | Non-blocking API calls           |
| Scheduler       | APScheduler AsyncIOScheduler  | Automated job execution          |
| DB Driver       | asyncpg                       | Async PostgreSQL connection      |
| Data Processing | pandas + numpy                | Feature engineering              |
| Logging         | loguru                        | Structured pipeline logging      |
| Container       | Docker + Docker Compose       | Unified environment              |

---

## Data Sources

| Source       | Endpoint                              | Data Collected                        | Auth     | Schedule |
|--------------|---------------------------------------|---------------------------------------|----------|----------|
| NOAA SWPC    | services.swpc.noaa.gov                | Solar wind plasma, IMF Bz/Bt, Kp index | None   | 15 min   |
| GOES-16      | services.swpc.noaa.gov/json/goes      | Proton flux (10/100 MeV), electron flux | None  | 15 min   |
| NASA DONKI   | api.nasa.gov/DONKI                    | CME events, solar flare events        | Free key | 60 min   |

---

## Project Structure

```
data_pipeline/
│
├── scheduler.py            Entry point — orchestrates all jobs via APScheduler
├── fetch_noaa.py           Fetches solar wind, Kp index, IMF Bz/Bt from NOAA SWPC
├── fetch_goes.py           Fetches GOES-16 proton and electron particle flux
├── fetch_donki.py          Fetches CME events and solar flares from NASA DONKI
├── feature_engineering.py  Computes lag windows and rolling statistics for ML
├── cache.py                Redis cache layer for hot ML inference features
├── data_quality.py         Gap detection, null checks, and interpolation
├── Dockerfile              Python 3.11-slim container definition
├── requirements.txt        Pinned Python dependencies
└── README.md               This file
```

---

## Database Schema

### `raw_observations` — TimescaleDB Hypertable
Stores raw JSON payloads from every API source.

| Column       | Type        | Description                          |
|--------------|-------------|--------------------------------------|
| id           | BIGSERIAL   | Primary key                          |
| source       | VARCHAR     | e.g. NOAA_PLASMA, GOES16_PROTON      |
| observed_at  | TIMESTAMPTZ | Observation timestamp (partition key)|
| payload      | JSONB       | Raw API response                     |
| created_at   | TIMESTAMPTZ | Insert timestamp                     |

---

### `processed_features` — TimescaleDB Hypertable
ML-ready engineered features with lag and rolling window variants.

| Column                        | Type    | Description                    |
|-------------------------------|---------|--------------------------------|
| observed_at                   | TIMESTAMPTZ | Feature timestamp          |
| bz_avg                        | FLOAT   | IMF Bz (southward component)   |
| bt_avg                        | FLOAT   | IMF total field magnitude      |
| solar_wind_speed              | FLOAT   | Solar wind speed (km/s)        |
| kp_index                      | FLOAT   | Planetary geomagnetic index    |
| proton_flux_10mev             | FLOAT   | GOES-16 proton flux at 10 MeV  |
| proton_flux_100mev            | FLOAT   | GOES-16 proton flux at 100 MeV |
| *_lag_1h / *_lag_3h           | FLOAT   | 1h and 3h lag features         |
| *_rolling_mean/std/max_3h-6h  | FLOAT   | Rolling statistics             |
| is_interpolated               | BOOLEAN | True if gap-filled             |

---

### `forecast_results`
Stores ML model predictions written by the ML team.

| Column               | Type    | Description                         |
|----------------------|---------|-------------------------------------|
| forecast_at          | TIMESTAMPTZ | When forecast was made          |
| horizon              | VARCHAR | 1h / 3h / 24h                       |
| proton_flux_forecast | FLOAT   | Predicted flux value                |
| risk_level           | VARCHAR | Low / Medium / High / Extreme       |
| confidence           | FLOAT   | Model confidence score (0.0 – 1.0)  |
| model_version        | VARCHAR | Version string for tracking         |

---

### `cme_events`
Coronal Mass Ejection events from NASA DONKI.

### `flare_events`
Solar flare events from NASA DONKI.

---

## Setup & Installation

### Prerequisites
- Docker Desktop installed and running
- NASA API key — register free at [api.nasa.gov](https://api.nasa.gov) (instant, no credit card)

---

### Step 1 — Configure environment

Copy the example file:
```bash
copy .env.example .env
```

Edit `.env` with your values:
```env
DATABASE_URL=postgresql://astra:astra_secret@postgres:5432/astra
REDIS_URL=redis://redis:6379
NASA_API_KEY=your_nasa_api_key_here
LOG_LEVEL=INFO
ENVIRONMENT=dev
```

> **Important:** Inside Docker, use `postgres` and `redis` as hostnames — not `localhost`.

---

### Step 2 — Start containers

```bash
docker compose up -d
```

This starts three containers:
- `astra_postgres` — PostgreSQL 16 with TimescaleDB
- `astra_redis` — Redis 7
- `astra_data_pipeline` — Python pipeline scheduler

First run takes 5–10 minutes to download images.

---

### Step 3 — Apply database schema

**PowerShell:**
```powershell
Get-Content schema.sql | docker exec -i astra_postgres psql -U astra -d astra
```

**Linux/Mac:**
```bash
docker exec -i astra_postgres psql -U astra -d astra < schema.sql
```

---

### Step 4 — Verify setup

Check all containers are running:
```bash
docker ps
```

Check pipeline logs:
```bash
docker logs astra_data_pipeline
```

Check tables were created:
```bash
docker exec -it astra_postgres psql -U astra -d astra -c "\dt"
```

Check live data is arriving:
```bash
docker exec -it astra_postgres psql -U astra -d astra -c "SELECT source, COUNT(*) FROM raw_observations GROUP BY source;"
```

---

## Scheduler Jobs

| Job                 | Interval | Description                                    |
|---------------------|----------|------------------------------------------------|
| fetch_noaa          | 15 min   | Solar wind plasma, IMF Bz/Bt, Kp index         |
| fetch_goes          | 15 min   | GOES-16 proton and electron particle flux       |
| fetch_donki         | 60 min   | CME events and solar flares from NASA           |
| feature_engineering | 20 min   | Lag + rolling window feature computation        |

All jobs execute immediately on startup then repeat on their schedule.  
If one job fails, the others continue unaffected.

---

## Redis Cache Keys

| Key                        | TTL    | Content                              |
|----------------------------|--------|--------------------------------------|
| `astra:latest_features`    | 30 min | Most recent processed_features row   |
| `astra:forecast:1h`        | 20 min | Latest 1-hour forecast               |
| `astra:forecast:3h`        | 20 min | Latest 3-hour forecast               |
| `astra:forecast:24h`       | 20 min | Latest 24-hour forecast              |

---

## Useful Commands

| Task                          | Command                                                      |
|-------------------------------|--------------------------------------------------------------|
| Start all containers          | `docker compose up -d`                                       |
| Stop all containers           | `docker compose down`                                        |
| Watch live logs               | `docker logs -f astra_data_pipeline`                         |
| Rebuild after code change     | `docker compose up -d --build`                               |
| Restart pipeline only         | `docker compose restart data_pipeline`                       |
| Connect to PostgreSQL         | `docker exec -it astra_postgres psql -U astra -d astra`      |
| Ping Redis                    | `docker exec -it astra_redis redis-cli ping`                 |
| Run fetcher manually          | `docker exec -it astra_data_pipeline python fetch_noaa.py`   |

---

## Data Quality

The `data_quality.py` module runs automatic checks:

- **Gap detection** — finds gaps larger than 16 minutes in time-series data
- **Null checks** — flags missing values in critical columns
- **Range anomaly detection** — validates physical limits (e.g. Kp index 0–9)
- **Gap interpolation** — linear interpolation for gaps under 2 hours, flagged with `is_interpolated = true`

---

## For Teammates

### M1 — Neil (ML Lead)
- Training data lives in `processed_features` table
- Connection string: `postgresql://astra:astra_secret@postgres:5432/astra`
- Key feature columns: `bz_avg`, `bt_avg`, `solar_wind_speed`, `solar_wind_density`, `kp_index`, `proton_flux_10mev`, `proton_flux_100mev`
- All lag and rolling variants available as separate columns
- Write model predictions to `forecast_results` table with `horizon` = `1h`, `3h`, or `24h`

### M3 — Backend Engineer
- Database: `postgresql://astra:astra_secret@postgres:5432/astra`
- Redis: `redis://redis:6379`
- Docker network: `astra_astra_net`
- Use `cache.py` functions to read hot features for low-latency inference serving
- Risk levels for frontend: `Low` / `Medium` / `High` / `Extreme`

### M4 — Frontend Engineer
- All data is served via the M3 REST API and WebSocket
- Forecast horizons: `1h`, `3h`, `24h`
- Risk badge values: `Low`, `Medium`, `High`, `Extreme`
- Live Kp index and solar wind speed available for gauges

---

## Live Data Sample

First run results (auto-updates every 15 minutes):

| Source          | Rows   |
|-----------------|--------|
| NOAA_PLASMA     | 9,625  |
| NOAA_MAG        | 9,657  |
| NOAA_KP         | 358    |
| GOES16_PROTON   | 287    |
| GOES16_ELECTRON | 287    |
| NASA_DONKI_CME  | 52     |
| NASA_DONKI_FLR  | 2      |
| **Total**       | **20,268** |

---

## Environment Variables

| Variable       | Required | Description                                    |
|----------------|----------|------------------------------------------------|
| DATABASE_URL   | Yes      | PostgreSQL connection string                   |
| REDIS_URL      | Yes      | Redis connection string                        |
| NASA_API_KEY   | Yes      | Free key from api.nasa.gov                     |
| LOG_LEVEL      | No       | INFO (default) / DEBUG / WARNING               |
| ENVIRONMENT    | No       | dev / prod                                     |

---

## Built By

**M2 — Data Engineer**  
ASTRA Team · ISRO Hackathon 2026  
Stack: Python · PostgreSQL · TimescaleDB · Redis · Docker