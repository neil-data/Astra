<a name="readme-top"></a>
<div align="center">

<img src=".github/assets/banner.svg" alt="ASTRA — Advanced Space Terrain and Radiation Analytics" width="100%" />

<br/>

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-REST%20%2B%20WS-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=0A0E1A)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-LSTM-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![TimescaleDB](https://img.shields.io/badge/TimescaleDB-PG16-FDB515?style=for-the-badge&logo=postgresql&logoColor=0A0E1A)](https://www.timescale.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

<p>
  <a href="https://astra-five-green.vercel.app"><strong>🚀 Live Demo</strong></a> ·
  <a href="https://github.com/neil-data/Astra.git"><strong>📦 Source</strong></a> ·
  <a href="#-api-reference"><strong>📚 API Docs</strong></a>
</p>

<p><em>Built for the <strong>Bharatiya Antariksh Hackathon 2026</strong> (ISRO × Hack2Skill) — Team <strong>VoidArchitects</strong></em></p>

</div>

<br/>

> ### ⚡ TL;DR
> Geostationary satellites sit in one of the harshest radiation environments in Earth orbit. **ASTRA** watches the Sun in real time, feeds live solar-wind and X-ray telemetry into an LSTM + XGBoost forecasting core, and turns raw particle-flux readings into a **1h / 3h / 24h risk forecast** — with a four-level operator alert (`LOW` → `MEDIUM` → `HIGH` → `EXTREME`) delivered before the storm actually arrives.

<br/>

## 📋 Table of Contents

- [🌌 Overview](#overview)
- [🖥️ Preview](#preview)
- [✨ Features](#features)
- [🏗️ Architecture](#architecture)
- [🔁 End-to-End Data Flow](#data-flow)
- [🚨 Alert Lifecycle](#alert-lifecycle)
- [🧠 Machine Learning](#machine-learning)
- [🛠️ Tech Stack](#tech-stack)
- [📁 Project Structure](#project-structure)
- [📡 Data Sources](#data-sources)
- [📚 API Reference](#api-reference)
- [⚡ Getting Started](#getting-started)
- [🔐 Environment Variables](#environment-variables)
- [☁️ Deployment](#deployment)
- [🤝 Contributing](#contributing)
- [👥 Team](#team)

<br/>

<a name="overview"></a>

## 🌌 Overview

**ASTRA — Advanced Space Terrain & Radiation Analytics** is an AI-powered space-weather forecasting platform built for the problem statement *"Forecasting Energetic Particle Radiation Environment for ISRO's Geostationary Satellites."*

Solar flares and coronal mass ejections (CMEs) can upset onboard electronics, degrade solar arrays, and force satellite operators into a defensive safe-mode with little warning. Unlike existing tools that only surface raw space-weather numbers, ASTRA continuously ingests live telemetry, runs it through trained ML models, and converts it directly into an **actionable, operator-ready risk level** — closing the gap between *"a storm is coming"* and *"the satellite already knows."*

|  |  |
|---|---|
| **Services** | 4 — backend API · data pipeline · ML pipeline · frontend dashboard |
| **Data sources** | NOAA SWPC · NASA DONKI · GOES-16 · ACE/DSCOVR |
| **Forecast horizons** | 1h · 3h · 24h |
| **Models** | LSTM (proton flux) · XGBoost (risk classification) · regression (CME arrival) |
| **Alert levels** | 🟢 LOW · 🟡 MEDIUM · 🟠 HIGH · 🔴 EXTREME |
| **Live channel** | REST API + WebSocket (`/ws/live`) |

> **Note:** ASTRA is a research/forecasting platform built for a hackathon, not a certified operational space-weather warning system. For mission-critical decisions, always cross-reference official NOAA SWPC and ISRO advisories.

<br/>

<a name="preview"></a>

## 🖥️ Preview

<div align="center">
<img src=".github/assets/dashboard-preview.png" alt="ASTRA dashboard, forecast, alerts, and history views" width="100%" />
<sub>Console dashboard · predictive forecast panel · operator alert console · historical telemetry matrix</sub>
</div>

<br/>

<a name="features"></a>

## ✨ Features

| | |
|---|---|
| 🛰️ **Real-time monitoring** | Continuously polls NOAA SWPC, NASA DONKI, GOES-16 and ACE/DSCOVR for solar and space-weather parameters |
| 🔗 **Multi-source data fusion** | Normalizes and quality-checks readings from four independent feeds into one consistent time series |
| 🧠 **AI-powered forecasting** | Predicts radiation intensity at 1h, 3h and 24h horizons using an LSTM deep-learning core |
| 📈 **Proton flux prediction** | LSTM sequence model trained on rolling windows of solar-wind and X-ray features |
| 🧮 **Risk classification** | XGBoost model maps predicted flux into actionable `LOW / MEDIUM / HIGH / EXTREME` categories |
| ☄️ **CME arrival prediction** | Regression head estimates hours-to-arrival for an in-transit coronal mass ejection |
| 🚨 **Four-level alert engine** | Automatically raises operator alerts as thresholds are crossed |
| 💻 **Live dashboard** | React 19 + TypeScript SPA with live KPIs, timelines, and a 3D satellite hero |
| 🕓 **Historical analytics** | Trend visualization over stored telemetry for situational awareness |
| 🔌 **REST + WebSocket API** | FastAPI backend with auto-generated Swagger docs and a `/ws/live` push stream |
| 🔐 **Secure & scalable** | JWT auth, role-based access, and a fully containerized Docker Compose stack |

<br/>

<a name="architecture"></a>

## 🏗️ Architecture

ASTRA is a four-service pipeline: telemetry is **ingested → stored → forecast → served**, end to end, from raw solar-wind readings to a risk badge on an operator's screen.

```mermaid
flowchart TB
    NOAA["NOAA SWPC<br/>Solar wind · Bz/Bt · Kp"]:::source
    GOES["GOES-16<br/>Proton / electron flux"]:::source
    DONKI["NASA DONKI<br/>CME &amp; flare events"]:::source
    ACE["ACE / DSCOVR<br/>Solar wind · IMF · particles"]:::source

    SCHED["Scheduler<br/>(APScheduler)"]:::pipeline
    QUAL["Data Quality Checks"]:::pipeline
    FEAT["Feature Engineering"]:::pipeline

    DB[("TimescaleDB")]:::storage
    CACHE[("Redis Cache")]:::storage

    LSTM["LSTM<br/>Proton Flux Forecast"]:::ml
    XGB["XGBoost<br/>Risk Classification"]:::ml
    REG["Regression<br/>CME Arrival"]:::ml
    ALERT["Alert Engine<br/>LOW → EXTREME"]:::ml

    API["FastAPI REST"]:::backend
    WS["WebSocket /ws/live"]:::backend

    UI["React Dashboard<br/>Vite · TanStack Query · Three.js"]:::frontend

    NOAA --> SCHED
    GOES --> SCHED
    DONKI --> SCHED
    ACE --> SCHED
    SCHED --> QUAL --> FEAT --> DB
    FEAT -.-> CACHE
    DB --> LSTM --> ALERT
    DB --> XGB --> ALERT
    DB --> REG --> ALERT
    ALERT --> DB
    DB --> API
    CACHE --> API
    API --> WS
    API --> UI
    WS --> UI

    classDef source fill:#161B33,stroke:#4FD1E8,color:#E8ECF4,stroke-width:1px
    classDef pipeline fill:#1B2340,stroke:#4FD1E8,color:#E8ECF4,stroke-width:1px
    classDef storage fill:#0A0E1A,stroke:#F5A623,color:#E8ECF4,stroke-width:2px
    classDef ml fill:#2A1B33,stroke:#F5A623,color:#E8ECF4,stroke-width:1px
    classDef backend fill:#0F2A2E,stroke:#34D399,color:#E8ECF4,stroke-width:1px
    classDef frontend fill:#141A2E,stroke:#E8ECF4,color:#E8ECF4,stroke-width:2px
```

### Component Breakdown

| Service | Responsibility | Key Tech | Entry Point |
|---|---|---|---|
| **`astra-backend`** | REST API + WebSocket broadcaster | FastAPI, async SQLAlchemy, Redis | `main.py` |
| **`data_pipeline`** | Scheduled ingestion, validation, feature engineering | httpx, asyncpg, APScheduler, loguru | `scheduler.py` |
| **`astra_ml_pipeline`** | Model training & forecast generation | PyTorch, XGBoost, pandas, scikit-learn | `train.py`, `run_forecast.py` |
| **`astra_frontend`** | Dashboard SPA | React 19, Vite, Three.js, TanStack Query | `src/App.tsx` |

### Layered View

| Layer | Components | Purpose |
|---|---|---|
| **Acquisition** | NOAA SWPC, GOES-16, NASA DONKI, ACE/DSCOVR clients | Pull raw solar & particle telemetry on a fixed schedule |
| **Validation & Enrichment** | Data quality checks, feature engineering | Reject bad readings, derive model-ready features |
| **Persistence** | TimescaleDB (time-series), Redis (hot cache) | Durable history + low-latency reads for the API |
| **Intelligence** | LSTM, XGBoost, regression, alert engine | Turn stored features into forecasts and risk labels |
| **Delivery** | FastAPI REST, WebSocket `/ws/live` | Serve forecasts/alerts to clients, push live updates |
| **Presentation** | React 19 dashboard | Visualize KPIs, forecasts, alerts, and history for operators |

For a deeper dive, see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

<br/>

<a name="data-flow"></a>

## 🔁 End-to-End Data Flow

The sequence below traces a single telemetry reading from ingestion to the moment an operator sees a risk badge update on the dashboard.

```mermaid
sequenceDiagram
    autonumber
    participant Src as External Feeds<br/>(NOAA · GOES · DONKI · ACE/DSCOVR)
    participant Sched as data_pipeline<br/>(APScheduler)
    participant DQ as Data Quality
    participant FE as Feature Engineering
    participant DB as TimescaleDB
    participant ML as astra_ml_pipeline<br/>(LSTM · XGBoost · Regression)
    participant Alert as Alert Engine
    participant API as FastAPI Backend
    participant Cache as Redis
    participant WS as WebSocket /ws/live
    participant UI as React Dashboard

    Src->>Sched: Poll on schedule (cron interval)
    Sched->>DQ: Raw observation batch
    DQ->>FE: Validated readings
    FE->>DB: Write engineered features
    ML->>DB: Pull rolling feature window
    ML->>ML: Forecast flux (1h/3h/24h) + classify risk + estimate CME arrival
    ML->>DB: Persist tagged forecast
    ML->>Alert: New forecast available
    Alert->>Alert: Compare risk_level vs active alert
    Alert->>DB: Create / resolve alert record
    API->>DB: Query latest forecast & alerts
    API->>Cache: Read/write hot values
    API->>WS: Broadcast updated risk state
    WS->>UI: Push live update
    UI->>API: (fallback) REST polling for KPIs & history
```

<br/>

<a name="alert-lifecycle"></a>

## 🚨 Alert Lifecycle

The alert engine polls the latest forecast on a fixed interval and reconciles it against any currently active alert, only opening or closing alerts when the risk level actually changes.

```mermaid
stateDiagram-v2
    [*] --> LOW
    LOW --> MEDIUM: predicted risk crosses MEDIUM threshold
    MEDIUM --> HIGH: predicted risk crosses HIGH threshold
    HIGH --> EXTREME: predicted risk crosses EXTREME threshold
    EXTREME --> HIGH: risk subsides
    HIGH --> MEDIUM: risk subsides
    MEDIUM --> LOW: risk subsides
    HIGH --> [*]: alert resolved (is_active = false)
    EXTREME --> [*]: alert resolved (is_active = false)
```

| Alert Level | Signal | Operator Action Implied |
|---|---|---|
| 🟢 **LOW** | Nominal solar wind / flux, no active alert | Routine monitoring |
| 🟡 **MEDIUM** | Elevated flux or a watch-worthy DONKI event | Increase monitoring cadence |
| 🟠 **HIGH** | `alert_level` in `{HIGH, EXTREME}` per `alert_engine.py` | Prepare contingency / safe-mode readiness |
| 🔴 **EXTREME** | Highest classified risk from the XGBoost head | Consider defensive safe-mode for affected assets |

Every alert record stores the triggering forecast (`forecast_id`), predicted Kp index, predicted proton flux, a human-readable message, and `triggered_at` / `resolved_at` timestamps, so the full history of an event is auditable end to end.

<br/>

<a name="machine-learning"></a>

## 🧠 Machine Learning

The forecasting core combines a sequence model with a classifier so raw flux predictions become an actionable risk label, not just a number.

```
Input (batch, timesteps, features)
        │
   LSTM(128) → Dropout(0.2)
        │
   LSTM(64)  → Dropout(0.2)
        │
   Dense(32) + ReLU        ← shared trunk
        │
        ├── Proton flux forecast (1h / 3h / 24h)   → fed into
        ├── XGBoost risk classifier                → LOW / MEDIUM / HIGH / EXTREME
        └── CME arrival regressor                    → hours-to-arrival
```

```mermaid
flowchart LR
    RAW["Rolling feature window<br/>(TimescaleDB)"] --> L1["LSTM(128)<br/>+ Dropout(0.2)"]
    L1 --> L2["LSTM(64)<br/>+ Dropout(0.2)"]
    L2 --> D["Dense(32) + ReLU<br/>(shared trunk)"]
    D --> F1["Flux Forecast<br/>1h / 3h / 24h"]
    D --> F2["XGBoost<br/>Risk Classifier"]
    D --> F3["Regression<br/>CME Arrival (hrs)"]
    F1 --> F2
    F1 --> OUT[("Forecast written<br/>back to DB")]
    F2 --> OUT
    F3 --> OUT
    OUT --> API2["Served via<br/>FastAPI"]
```

- **LSTM head** predicts future proton flux intensity at three forecast horizons from a rolling window of solar-wind and X-ray features
- **XGBoost head** classifies the predicted flux into one of four actionable risk categories operators can act on immediately
- **Regression head** estimates hours-to-arrival for an in-transit CME, feeding early warnings into the alert engine

### Model Summary

| Model | Task | Input | Output | Library |
|---|---|---|---|---|
| **LSTM** (2-layer, 128→64 units) | Sequence forecasting | Rolling window of solar-wind + X-ray features | Proton flux at 1h / 3h / 24h | PyTorch |
| **XGBoost** | Multi-class classification | Forecasted flux + auxiliary features | `LOW` / `MEDIUM` / `HIGH` / `EXTREME` | XGBoost |
| **Regression head** | Time-to-event estimation | In-transit CME parameters | Hours-to-arrival | scikit-learn |

Training and inference both live in `astra_ml_pipeline/`; the serving loop periodically pulls fresh features from TimescaleDB and writes tagged forecasts back to the database for the API to serve.

<br/>

<a name="tech-stack"></a>

## 🛠️ Tech Stack

<table>
<tr><td valign="top">

**Backend**
- FastAPI · Uvicorn
- SQLAlchemy 2.0 (async)
- asyncpg · Redis (redis-py)
- Pydantic v2
- python-jose · passlib[bcrypt] (JWT auth)
- httpx

</td><td valign="top">

**Machine Learning**
- PyTorch (LSTM)
- XGBoost
- NumPy · Pandas · scikit-learn
- PyArrow · joblib

</td></tr>
<tr><td valign="top">

**Frontend**
- React 19 · TypeScript 5.8
- Vite 6 · Express (`server.ts`)
- TanStack Query 5 · react-router-dom 7
- Recharts · Three.js
- Tailwind CSS · Gemini API insights

</td><td valign="top">

**Data & Infrastructure**
- PostgreSQL 16 + TimescaleDB
- Redis 7 · Apache Kafka (stream ingestion)
- APScheduler · loguru
- Docker & Docker Compose
- GitHub Actions (CI) · Render.com

</td></tr>
</table>

<br/>

<a name="project-structure"></a>

## 📁 Project Structure

<details>
<summary><strong>Click to expand the monorepo layout</strong></summary>

```
Astra-main/
├── astra-backend/              # FastAPI REST + WebSocket service
│   ├── routers/                 # forecast · history · risk · status
│   ├── main.py                  # app entrypoint & router registration
│   ├── database.py              # async SQLAlchemy engine/session
│   ├── models.py / schemas.py   # ORM models & Pydantic schemas
│   ├── websocket.py             # /ws/live broadcaster
│   ├── alert_engine.py          # four-level risk alert logic
│   ├── config.py                # env-driven Settings
│   └── Dockerfile
│
├── data_pipeline/               # Scheduled ingestion worker
│   ├── fetch_noaa.py            # solar wind · Bz/Bt · Kp
│   ├── fetch_goes.py            # GOES-16 proton/electron flux
│   ├── fetch_donki.py           # NASA DONKI CME & flare events
│   ├── feature_engineering.py
│   ├── data_quality.py
│   ├── scheduler.py             # APScheduler job orchestration
│   └── schema.sql
│
├── astra_ml_pipeline/           # Forecast modeling service
│   ├── model.py                 # LSTM architecture
│   ├── train.py / preprocessing.py
│   ├── inference.py / run_forecast.py
│   ├── cme_pipeline.py          # CME arrival regression
│   └── artifacts/               # saved model weights & metrics
│
├── astra_frontend/              # React 19 + TypeScript SPA
│   ├── src/components/          # Dashboard · Login · charts · 3D canvases
│   ├── src/App.tsx / main.tsx
│   ├── server.ts                # Express dev/serve entry (port 3000)
│   └── Dockerfile                # multi-stage → nginx production build
│
├── docs/                        # ARCHITECTURE.md · API.md
├── .github/
│   ├── workflows/ci.yml         # lint + typecheck on push/PR
│   └── assets/                  # banner & preview images
├── docker-compose.yml           # postgres · redis · backend · data pipeline
└── render.yaml                  # Render.com deployment manifest
```

</details>

<br/>

<a name="data-sources"></a>

## 📡 Data Sources

| Source | Provider | Data | Fetched By |
|---|---|---|---|
| **NOAA SWPC** | NOAA | Solar wind plasma, IMF Bz/Bt, Kp index | `fetch_noaa.py` |
| **GOES-16** | NOAA / NASA | Integral proton & electron flux (10/50/100 MeV) | `fetch_goes.py` |
| **NASA DONKI** | NASA | CME events & solar flare catalog | `fetch_donki.py` |
| **ACE / DSCOVR** | NASA / NOAA | Upstream solar wind, IMF, and energetic particles | data pipeline |

A free `NASA_API_KEY` (instant signup, no card required) is available at [api.nasa.gov](https://api.nasa.gov) for DONKI access.

<br/>

<a name="api-reference"></a>

## 📚 API Reference

Base URL (local): `http://localhost:8000` · Interactive docs: `http://localhost:8000/docs`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/status` | Service info & uptime |
| `GET` | `/api/v1/health` | Database & cache connectivity check |
| `GET` | `/api/v1/forecast/latest` | Latest radiation / space-weather forecast |
| `GET` | `/api/v1/forecast/summary` | Forecasts at 60 / 180 / 1440-minute horizons |
| `GET` | `/api/v1/history?limit=` | Raw stored telemetry observations |
| `GET` | `/api/v1/risk/current` | Current radiation risk assessment |
| `GET` | `/api/v1/risk/alerts` | Active geostationary radiation risk alerts |
| `WS`  | `/ws/live` | Real-time push stream of risk updates |

### Typical Client Call Pattern

```mermaid
flowchart LR
    C["Client<br/>(Dashboard / 3rd-party)"] -->|"GET /api/v1/forecast/latest"| API["FastAPI"]
    C -->|"GET /api/v1/risk/alerts"| API
    C -->|"WS connect /ws/live"| API
    API -->|"JSON forecast"| C
    API -->|"JSON alerts"| C
    API -->|"push: risk update"| C
```

Full request/response shapes are documented in [`docs/API.md`](docs/API.md).

<br/>

<a name="getting-started"></a>

## ⚡ Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) & Docker Compose — for the backend stack
- [Node.js 20+](https://nodejs.org/) — for the frontend
- [Python 3.11+](https://www.python.org/) — for the ML pipeline (if running outside Docker)
- A free NASA API key from [api.nasa.gov](https://api.nasa.gov) (optional — `DEMO_KEY` works for light use)

### 1 · Backend stack (Docker Compose)

`docker-compose.yml` brings up Postgres (TimescaleDB), Redis, the backend API, and the data pipeline worker together:

```bash
git clone https://github.com/neil-data/Astra.git
cd Astra-main
cp .env.example .env      # fill in NASA_API_KEY, JWT_SECRET_KEY, etc.
docker compose up --build
```

### 2 · Frontend (run separately)

```bash
cd astra_frontend
npm install
npm run dev
```

### 3 · ML forecasting loop (optional, run separately)

```bash
cd astra_ml_pipeline
pip install -r requirements.txt --break-system-packages
python run_forecast.py
```

### Local URLs

| Service | URL |
|---|---|
| Backend API | http://localhost:8000 |
| Swagger / OpenAPI docs | http://localhost:8000/docs |
| Frontend (dev) | http://localhost:3000 |

<br/>

<a name="environment-variables"></a>

## 🔐 Environment Variables

Copy `.env.example` → `.env` at the repo root for Docker Compose, and/or per-service `.env` files for standalone runs.

| Variable | Example | Used By |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://astra_user:astra_pass@postgres:5432/astra_db` | backend, ML pipeline |
| `DATABASE_URL_SYNC` | `postgresql://astra_user:astra_pass@postgres:5432/astra_db` | data pipeline |
| `REDIS_URL` | `redis://redis:6379` | backend, data pipeline |
| `JWT_SECRET_KEY` / `JWT_ALGORITHM` / `JWT_EXPIRY` | — | backend auth |
| `NASA_API_KEY` | `DEMO_KEY` | data pipeline (DONKI) |
| `VITE_API_BASE` / `VITE_API_URL` | `http://localhost:8000` | frontend |
| `GEMINI_API_KEY` | — | frontend AI insights panel |

<br/>

<a name="deployment"></a>

## ☁️ Deployment

- **Live demo:** [astra-five-green.vercel.app](https://astra-five-green.vercel.app)
- `render.yaml` defines a production topology on [Render](https://render.com/):
  - **`astra-backend`** — Dockerized web service, health-checked on `/api/v1/health`
  - **`astra-data-pipeline`** — background ingestion worker
  - **`astra-redis`** / **`astra-db`** — managed Redis and PostgreSQL

```mermaid
flowchart TB
    subgraph Render["Render.com"]
        BE["astra-backend<br/>(web service)"]
        DP["astra-data-pipeline<br/>(background worker)"]
        RDB[("astra-db<br/>PostgreSQL/Timescale")]
        RCACHE[("astra-redis")]
    end
    subgraph Vercel["Vercel"]
        FE["astra_frontend<br/>(static / SSR)"]
    end

    DP --> RDB
    BE --> RDB
    BE --> RCACHE
    FE -->|REST + WS| BE
```

**CI:** every push/PR to `main` runs `.github/workflows/ci.yml` — flake8 syntax checks on the backend and a TypeScript type-check (`tsc --noEmit`) on the frontend.

<br/>

<a name="contributing"></a>

## 🤝 Contributing

1. Fork the repo and create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes, keeping services in their existing folders
3. Make sure CI checks pass locally before pushing:
   - Backend: `flake8 astra-backend --select=E9,F63,F7,F82`
   - Frontend: `cd astra_frontend && npm run lint`
4. Open a pull request against `main` with a clear description of the change

There's no automated test suite yet — contributions that add one (`pytest` for the Python services, `vitest`/`playwright` for the frontend) are especially welcome.

<br/>

<a name="team"></a>

## 👥 Team VoidArchitects

Built for the **Bharatiya Antariksh Hackathon 2026** — Problem Statement: *Forecasting Energetic Particle Radiation Environment for ISRO's Geostationary Satellites*.

| Role | Name | Institution |
|---|---|---|
| Team Leader | Neil Banerjee | Institute of Advanced Research (IAR), Gandhinagar |
| Member | Devashya Jethva | Institute of Advanced Research (IAR), Gandhinagar |
| Member | Rajvardhansingh Chauhan | Institute of Advanced Research (IAR), Gandhinagar |
| Member | Manthan Balani | Institute of Advanced Research (IAR), Gandhinagar |

<br/>

## 🙏 Acknowledgments

- [NOAA Space Weather Prediction Center](https://www.swpc.noaa.gov/) — solar wind, Kp index, and GOES data
- [NASA DONKI](https://ccmc.gsfc.nasa.gov/tools/DONKI/) — CME and solar flare event catalog
- Built for geostationary satellite radiation-risk monitoring in the context of ISRO missions
- The open-source projects this is built on: FastAPI, PyTorch, XGBoost, React, TimescaleDB, and the rest of the stack listed above

<br/>

<div align="center">

<sub>Built for a future where solar storms don't catch satellites off guard. 🛰️</sub>

<br/>

[⬆ Back to top](#readme-top)

</div>
