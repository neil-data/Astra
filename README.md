<div align="center">

<!-- PROJECT LOGO PLACEHOLDER -->
<img src="./docs/assets/astra-logo-placeholder.png" alt="ASTRA Logo" width="140" />

# 🛰️ ASTRA
### Advanced Space Terrain & Radiation Analytics

**AI-Powered Space Radiation Forecasting & Solar Storm Intelligence Platform**

<!-- ANIMATED BANNER PLACEHOLDER -->
<img src="./docs/assets/astra-banner-placeholder.gif" alt="ASTRA Banner" width="100%" />

<br/>

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-Deep%20Learning-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-Strict-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](./LICENSE)

[![Stars](https://img.shields.io/github/stars/neil-data/Astra?style=for-the-badge&color=gold)](https://github.com/neil-data/Astra/stargazers)
[![Forks](https://img.shields.io/github/forks/neil-data/Astra?style=for-the-badge&color=blue)](https://github.com/neil-data/Astra/network/members)
[![Build Status](https://img.shields.io/github/actions/workflow/status/neil-data/Astra/ci.yml?style=for-the-badge&label=Build)](https://github.com/neil-data/Astra/actions)

<br/>

**Built for the 🇮🇳 Bharatiya Antariksh Hackathon (BAH) 2026 — ISRO × Hack2Skill**
**Problem Statement:** *Forecasting Energetic Particle Radiation Environment for ISRO's Geostationary Satellites*

[🚀 Live Demo](https://astra-five-green.vercel.app) · [📦 Repository](https://github.com/neil-data/Astra) · [📖 Documentation](#-table-of-contents) · [🐛 Report a Bug](https://github.com/neil-data/Astra/issues)

</div>

---

## 📑 Table of Contents

<details>
<summary>Click to expand</summary>

- [Vision](#-vision)
- [Features](#-features)
- [Architecture](#-architecture)
- [Folder Structure](#-folder-structure)
- [Technology Stack](#-technology-stack)
- [AI Models](#-ai-models)
- [Data Sources](#-data-sources)
- [ML Pipeline](#-ml-pipeline)
- [API Documentation](#-api-documentation)
- [Dashboard Showcase](#-dashboard-showcase)
- [Installation](#-installation)
- [Running the Project](#-running-the-project)
- [Machine Learning Training](#-machine-learning-training)
- [Database Schema](#-database-schema)
- [Risk Levels](#-risk-levels)
- [Performance Metrics](#-performance-metrics)
- [Future Roadmap](#-future-roadmap)
- [Security](#-security)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [Team](#-team)
- [License](#-license)
- [Acknowledgements](#-acknowledgements)

</details>

---

## 🌌 Vision

> *"A geostationary satellite doesn't get a second chance mid-storm."*

Earth's near-space environment is not calm and empty — it is a constantly shifting sea of energetic particles, solar wind, and radiation driven by the Sun. When the Sun erupts — through solar flares, coronal mass ejections (CMEs), or high-speed solar wind streams — the resulting particle radiation can silently degrade or catastrophically disable the satellites that our daily lives depend on.

**ASTRA** exists because *reactive* space-weather monitoring is no longer good enough. Dashboards that only display raw NOAA/NASA feeds tell an operator what is happening *right now* — but by the time a proton storm shows up on a live feed, the exposure window has often already begun. ASTRA closes that gap with **predictive, AI-driven intelligence**, giving operators a forecast window before the storm arrives, not just a readout after it does.

### Why this matters

| Stakeholder | Impact of Space Radiation Events |
|---|---|
| 🛰️ **ISRO & Satellite Operators** | Single-event upsets, solder-joint failures, and permanent sensor degradation on GEO assets like INSAT/GSAT spacecraft |
| 👨‍🚀 **Astronaut Safety** | Elevated radiation dosage risk during EVAs and crewed missions during solar particle events (SPEs) |
| 📡 **GPS & Navigation** | Ionospheric scintillation causes positioning errors, signal loss, and degraded accuracy for civilian and defense systems |
| 📞 **Communication Networks** | HF radio blackouts and satellite communication link degradation during geomagnetic storms |
| ⛅ **Terrestrial Weather Systems** | Disruption of weather-satellite telemetry used for forecasting and disaster response |
| ⚡ **Power Grids** | Geomagnetically Induced Currents (GICs) can trip transformers and cause regional blackouts |
| 🏢 **Commercial Satellite Operators** | Financial loss from anomalies, safe-mode entries, and reduced mission lifetime of orbital assets |

ASTRA's mission is simple: **turn raw heliophysics data into an early-warning system that a satellite operator can act on — minutes, hours, and a full day before impact.**

---

## ✨ Features

| Feature | Description | Status |
|---|---|---|
| 🌐 **Real-Time Monitoring** | Continuous polling of solar wind, proton flux, and geomagnetic indices from live feeds | ✅ |
| ☀️ **Solar Flare Prediction** | Early detection signals derived from X-ray flux and solar activity trends | ✅ |
| 🧠 **LSTM Forecasting** | Deep-learning particle flux forecasts at 1h / 3h / 24h horizons | ✅ |
| 🌊 **CME Arrival Prediction** | Regression-based estimated arrival time of coronal mass ejections | ✅ |
| 🚦 **Risk Classification** | XGBoost-based Low / Medium / High / Extreme risk categorization | ✅ |
| 📊 **Interactive Dashboard** | Live, responsive operator console with charts, KPIs, and alerts | ✅ |
| 🔌 **REST API** | Fully documented endpoints for forecast, risk, history, and status | ✅ |
| 🔄 **WebSockets** | Real-time push updates to the dashboard without polling | ✅ |
| 🐳 **Docker Deployment** | One-command containerized deployment via Docker Compose | ✅ |
| 🔐 **Authentication** | JWT-secured API and role-based access control (RBAC) | ✅ |
| 📈 **Historical Analytics** | Time-series exploration of past radiation and geomagnetic events | ✅ |
| 🚨 **Alert Engine** | Threshold- and ML-driven multi-channel alerting (dashboard/email/SMS) | ✅ |
| ⏱️ **TimescaleDB** | Optimized hypertables for high-frequency space-weather time series | ✅ |
| ⚡ **Redis Caching** | Sub-millisecond caching layer for hot forecast/risk queries | ✅ |
| 📱 **Responsive UI** | Mobile-first design built with TailwindCSS + Recharts | ✅ |

---

## 🏗️ Architecture

ASTRA follows a **six-layer architecture** — from raw heliophysics data ingestion to operator-facing action — with a cross-cutting foundation for security, scalability, and observability.

```mermaid
flowchart LR
    subgraph SRC["🛰️ Data Sources"]
        NOAA[NOAA SWPC]
        NASA[NASA DONKI]
        GOES[GOES-16]
        ACE[ACE / DSCOVR]
    end

    subgraph ING["⏱️ Ingestion Layer"]
        SCHED[Scheduler]
        VALID[Validation & QC]
    end

    subgraph PROC["🧮 Processing & ML Layer"]
        FEAT[Feature Engineering]
        MODELS[ML Models<br/>LSTM · XGBoost · Regression]
    end

    subgraph STORE["💾 Storage Layer"]
        TSDB[(TimescaleDB)]
        CACHE[(Redis Cache)]
    end

    subgraph APP["🚀 Application Layer"]
        API[FastAPI + WebSockets]
    end

    subgraph UI["🖥️ Presentation Layer"]
        FE[React Dashboard]
        USERS[👤 Operators]
    end

    NOAA --> SCHED
    NASA --> SCHED
    GOES --> SCHED
    ACE --> SCHED
    SCHED --> VALID
    VALID --> FEAT
    FEAT --> MODELS
    FEAT --> TSDB
    MODELS --> TSDB
    TSDB --> CACHE
    CACHE --> API
    MODELS --> API
    API <--> FE
    FE --> USERS

    style SRC fill:#0B3D91,color:#fff
    style ING fill:#1E5AA8,color:#fff
    style PROC fill:#7B2FF7,color:#fff
    style STORE fill:#116466,color:#fff
    style APP fill:#D65108,color:#fff
    style UI fill:#1B998B,color:#fff
```

> 💡 **Design principle:** Every layer is independently scalable and independently replaceable — the ML layer can be retrained and redeployed without touching ingestion, and the frontend can be swapped without touching the API contract.

---

## 📁 Folder Structure

```
ASTRA/
├── backend/
│   ├── app/
│   │   ├── api/                 # FastAPI route definitions
│   │   ├── core/                # Config, security, JWT logic
│   │   ├── services/             # Business logic layer
│   │   ├── schemas/              # Pydantic models
│   │   └── websockets/           # Real-time event handlers
│   ├── configs/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── charts/
│   │   └── api/
│   ├── public/
│   └── package.json
│
├── ml/
│   ├── models/
│   │   ├── lstm_flux_forecast/
│   │   ├── xgboost_risk_classifier/
│   │   └── cme_arrival_regression/
│   ├── data_pipeline/
│   │   ├── ingestion/
│   │   ├── cleaning/
│   │   └── feature_engineering/
│   ├── training/
│   └── evaluation/
│
├── data_pipeline/
│   ├── connectors/               # NOAA, NASA, GOES, ACE/DSCOVR clients
│   └── scheduler/
│
├── docker/
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   ├── ml.Dockerfile
│   └── docker-compose.yml
│
├── scripts/
│   ├── setup.sh
│   ├── seed_db.py
│   └── train_all_models.sh
│
├── docs/
│   ├── architecture/
│   ├── api/
│   └── assets/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── api/
│
├── configs/
│   ├── .env.example
│   └── settings.yaml
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── LICENSE
└── README.md
```

---

## 🧰 Technology Stack

| Technology | Purpose | Why Chosen | Advantages |
|---|---|---|---|
| **Python 3.11** | Core backend & ML language | Mature ecosystem for data science + web frameworks | Fast development, huge library support |
| **FastAPI** | REST API framework | Async-first, auto-generated OpenAPI docs | High throughput, native Pydantic validation |
| **PyTorch** | Deep learning framework | Flexible dynamic graphs, strong LSTM/RNN support | Easy experimentation, GPU acceleration |
| **XGBoost** | Gradient-boosted risk classification | Best-in-class performance on tabular data | Fast training, interpretable feature importance |
| **PostgreSQL 16** | Primary relational database | ACID compliance, mature tooling | Reliable, extensible via extensions |
| **TimescaleDB** | Time-series extension for Postgres | Purpose-built for high-frequency telemetry | Fast range queries, automatic partitioning |
| **Redis 7** | Caching & session store | In-memory speed for hot-path reads | Sub-ms latency, pub/sub for alerts |
| **React 19** | Frontend UI library | Component reusability, huge ecosystem | Fast rendering, strong community support |
| **TypeScript** | Type-safe frontend logic | Compile-time safety across a large codebase | Fewer runtime bugs, better DX |
| **Vite** | Frontend build tool | Near-instant HMR, modern ESM-first bundling | Fast builds, lightweight config |
| **TailwindCSS** | Utility-first styling | Rapid, consistent UI development | Small bundle size, design consistency |
| **Recharts** | Data visualization | Declarative React-native charting | Easy integration with live data streams |
| **Docker & Compose** | Containerization | Environment parity dev → prod | Reproducible deployments |
| **GitHub Actions** | CI/CD automation | Native GitHub integration | Automated testing & deployment |
| **JWT** | Authentication | Stateless, scalable auth | Works cleanly with REST + WebSockets |

---

## 🧠 AI Models

### 1️⃣ LSTM — Particle Flux Forecasting

<table>
<tr><td><b>Input</b></td><td>Multivariate time series: proton flux, electron flux, Kp index, solar wind speed, IMF Bz/Bt</td></tr>
<tr><td><b>Sequence Length</b></td><td>72 timesteps (sliding window, 5-min cadence → 6-hour lookback)</td></tr>
<tr><td><b>Features</b></td><td>Proton flux (>10 MeV, >100 MeV), Kp index, Dst index, solar wind speed/density, IMF Bz/Bt, X-ray flux</td></tr>
<tr><td><b>Output</b></td><td>Forecasted proton flux at <b>+1h</b>, <b>+3h</b>, and <b>+24h</b> horizons</td></tr>
<tr><td><b>Architecture</b></td><td>Stacked 2-layer LSTM (128 → 64 units) → Dense(32, ReLU) → Dense(3, linear)</td></tr>
<tr><td><b>Training</b></td><td>Sliding-window supervised learning over 5+ years of historical NOAA/GOES telemetry</td></tr>
<tr><td><b>Loss Function</b></td><td>Huber Loss (robust to solar-storm outlier spikes)</td></tr>
<tr><td><b>Optimizer</b></td><td>Adam (lr=1e-3, weight decay=1e-5, ReduceLROnPlateau scheduler)</td></tr>
<tr><td><b>Evaluation Metrics</b></td><td>MAE, RMSE, and directional accuracy on log-scaled flux values</td></tr>
</table>

### 2️⃣ XGBoost — Radiation Risk Classification

<table>
<tr><td><b>Features</b></td><td>LSTM-forecasted flux, current Kp/Dst indices, CME speed, solar wind pressure, historical event recurrence</td></tr>
<tr><td><b>Target Labels</b></td><td><code>LOW</code> · <code>MEDIUM</code> · <code>HIGH</code> · <code>EXTREME</code></td></tr>
<tr><td><b>Feature Importance</b></td><td>Ranked via gain-based importance; proton flux forecast and Kp index dominate splits</td></tr>
<tr><td><b>Evaluation</b></td><td>Multi-class Precision, Recall, F1, and ROC-AUC (one-vs-rest)</td></tr>
</table>

### 3️⃣ CME Arrival Time Regression

Coronal Mass Ejection arrival time is estimated using a **gradient-boosted regression model** trained on historical CME catalog data (NASA DONKI) with features including initial CME speed, angular width, source-region latitude/longitude, and background solar wind conditions. The model outputs an **estimated transit time (hours) to L1/Earth**, which is then converted into a predicted arrival timestamp and surfaced directly on the operator dashboard alongside a confidence interval.

---

## 🌍 Data Sources

| Source | Data Provided | Frequency | Purpose |
|---|---|---|---|
| **NOAA SWPC** | Solar wind, X-ray flux, proton flux, Kp index | Real-time (1–5 min) | Core operational radiation & geomagnetic monitoring |
| **NASA DONKI** | CME catalog, solar flare events, SEP events | Event-driven | CME arrival modeling & historical event labeling |
| **GOES-16** | X-ray flux, proton/electron flux, magnetometer | Real-time (1 min) | High-cadence particle flux input for LSTM |
| **ACE** | Solar wind plasma & magnetic field data | Real-time (1–5 min) | Upstream solar wind conditions (L1 point) |
| **DSCOVR** | Solar wind, IMF Bz/Bt | Real-time (1 min) | Redundant L1 solar wind monitoring |
| **OMNIWeb** | Historical merged solar wind & geomagnetic datasets | Hourly/Daily (archival) | Model training & backtesting |

---

## 🔬 ML Pipeline

```mermaid
flowchart TD
    A[📥 Data Collection] --> B[🧹 Cleaning]
    B --> C[🛠️ Feature Engineering]
    C --> D[📐 Scaling / Normalization]
    D --> E[🏋️ Training]
    E --> F[✅ Validation]
    F --> G[⚡ Inference]
    G --> H[🚦 Risk Prediction]
    H --> I[📊 Dashboard]

    style A fill:#0B3D91,color:#fff
    style B fill:#1E5AA8,color:#fff
    style C fill:#3A6EA5,color:#fff
    style D fill:#5B8DB8,color:#fff
    style E fill:#7B2FF7,color:#fff
    style F fill:#9B4DFF,color:#fff
    style G fill:#D65108,color:#fff
    style H fill:#E85D04,color:#fff
    style I fill:#1B998B,color:#fff
```

---

## 📡 API Documentation

**Base URL:** `https://api.astra-project.io/v1`
**Auth:** Bearer JWT (`Authorization: Bearer <token>`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/forecast` | Returns 1h / 3h / 24h particle flux forecasts | ✅ |
| `GET` | `/risk` | Returns current risk classification (Low–Extreme) | ✅ |
| `GET` | `/history` | Returns historical telemetry & past risk levels | ✅ |
| `GET` | `/status` | System health, data-feed connectivity, model status | ❌ |
| `POST` | `/predict` | Runs on-demand inference on supplied telemetry | ✅ |
| `WS` | `/ws/live` | Real-time streaming of forecasts & alerts | ✅ |

<details>
<summary><b>📤 Example: <code>GET /forecast</code> Response</b></summary>

```json
{
  "timestamp": "2026-07-01T11:27:03Z",
  "forecast": {
    "1h":  { "proton_flux": 1205.4, "risk": "LOW", "confidence": 0.86 },
    "3h":  { "proton_flux": 1310.9, "risk": "LOW", "confidence": 0.78 },
    "24h": { "proton_flux": 2440.2, "risk": "MEDIUM", "confidence": 0.61 }
  },
  "model_version": "lstm-v1.3.0"
}
```
</details>

<details>
<summary><b>📤 Example: <code>GET /risk</code> Response</b></summary>

```json
{
  "current_risk": "LOW",
  "kp_index": 3.2,
  "storm_probability": 0.20,
  "confidence_weight": 0.68,
  "active_alerts": 0
}
```
</details>

<details>
<summary><b>🔐 Example: Authentication Flow</b></summary>

```bash
curl -X POST https://api.astra-project.io/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "operator1", "password": "********"}'

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```
</details>

---

## 🖼️ Dashboard Showcase

> 📸 *Screenshots below are placeholders — replace with actual captures from your deployed instance.*

| View | Preview |
|---|---|
| **Live Dashboard** | ![Live Dashboard](./docs/assets/screenshot-dashboard.png) |
| **Forecast Graph** | ![Forecast Graph](./docs/assets/screenshot-forecast.png) |
| **Risk Panel** | ![Risk Panel](./docs/assets/screenshot-risk-panel.png) |
| **Orbit Map** | ![Orbit Map](./docs/assets/screenshot-orbit-map.png) |
| **Alert History** | ![Alert History](./docs/assets/screenshot-alert-history.png) |
| **Dark Theme** | ![Dark Theme](./docs/assets/screenshot-dark-theme.png) |

---

## ⚙️ Installation

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- PostgreSQL 16 (if running without Docker)
- Redis 7 (if running without Docker)

### 🐳 Docker Compose (Recommended)

```bash
git clone https://github.com/neil-data/Astra.git
cd Astra
cp configs/.env.example .env
docker compose -f docker/docker-compose.yml up --build
```

### 🐧 Linux

```bash
sudo apt update && sudo apt install -y python3.11 python3.11-venv nodejs npm
git clone https://github.com/neil-data/Astra.git
cd Astra/backend && python3.11 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cd ../frontend && npm install
```

### 🪟 Windows (PowerShell)

```powershell
git clone https://github.com/neil-data/Astra.git
cd Astra\backend
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd ..\frontend
npm install
```

### 🍎 macOS

```bash
brew install python@3.11 node
git clone https://github.com/neil-data/Astra.git
cd Astra/backend && python3.11 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cd ../frontend && npm install
```

### 🔧 Manual Installation (No Docker)

```bash
# 1. Start PostgreSQL & Redis locally
# 2. Run database migrations
cd backend && alembic upgrade head
# 3. Start backend
uvicorn app.main:app --reload --port 8000
# 4. Start frontend
cd ../frontend && npm run dev
```

### 🔑 Environment Variables

```env
# .env.example

# --- Database ---
POSTGRES_USER=astra_user
POSTGRES_PASSWORD=change_me
POSTGRES_DB=astra_db
DATABASE_URL=postgresql://astra_user:change_me@localhost:5432/astra_db

# --- Redis ---
REDIS_URL=redis://localhost:6379/0

# --- Auth ---
JWT_SECRET_KEY=super-secret-key-change-me
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# --- External Data APIs ---
NOAA_SWPC_API_URL=https://services.swpc.noaa.gov
NASA_DONKI_API_KEY=your_nasa_api_key
GOES_DATA_ENDPOINT=https://data.ngdc.noaa.gov/goes16

# --- App ---
ENVIRONMENT=development
API_PORT=8000
FRONTEND_URL=http://localhost:5173
```

---

## ▶️ Running the Project

```bash
# Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm run dev

# Database (via Docker)
docker compose up postgres timescaledb redis -d

# Full stack (Docker Compose)
docker compose -f docker/docker-compose.yml up

# Run test suite
pytest backend/tests/
npm test --prefix frontend
```

---

## 🏋️ Machine Learning Training

```bash
# 1. Prepare dataset (fetch + clean + feature engineer)
python ml/data_pipeline/prepare_dataset.py --start 2019-01-01 --end 2026-01-01

# 2. Train LSTM flux forecaster
python ml/training/train_lstm.py --config ml/configs/lstm_config.yaml

# 3. Train XGBoost risk classifier
python ml/training/train_xgboost.py --config ml/configs/xgb_config.yaml

# 4. Train CME arrival regression model
python ml/training/train_cme_regression.py

# 5. Validate all models
python ml/evaluation/validate_models.py --model all

# 6. Run inference on latest data
python ml/inference/run_inference.py --live

# 7. Save trained models
python ml/training/save_models.py --output ml/models/
```

---

## 🗄️ Database Schema

```mermaid
erDiagram
    USERS ||--o{ ALERTS : receives
    USERS {
        uuid id PK
        string username
        string email
        string hashed_password
        string role
        timestamp created_at
    }

    TELEMETRY ||--o{ FORECASTS : generates
    TELEMETRY {
        uuid id PK
        timestamp recorded_at
        float proton_flux
        float electron_flux
        float kp_index
        float dst_index
        float solar_wind_speed
        float imf_bz
        float imf_bt
        string source
    }

    FORECASTS ||--o{ RISK_CLASSIFICATIONS : informs
    FORECASTS {
        uuid id PK
        uuid telemetry_id FK
        timestamp forecast_time
        string horizon
        float predicted_flux
        float confidence
        string model_version
    }

    RISK_CLASSIFICATIONS ||--o{ ALERTS : triggers
    RISK_CLASSIFICATIONS {
        uuid id PK
        uuid forecast_id FK
        string risk_level
        float probability
        timestamp classified_at
    }

    ALERTS {
        uuid id PK
        uuid user_id FK
        uuid risk_id FK
        string channel
        string status
        timestamp sent_at
    }

    CME_EVENTS ||--o{ RISK_CLASSIFICATIONS : correlates
    CME_EVENTS {
        uuid id PK
        timestamp detected_at
        float speed_km_s
        float angular_width
        float predicted_arrival_hours
        timestamp predicted_arrival_time
    }
```

---

## 🚦 Risk Levels

| Level | Color | Meaning | Recommended Actions |
|---|---|---|---|
| 🟢 **LOW** | `#2ECC71` Green | Nominal conditions; background radiation only | Continue standard operations; routine monitoring |
| 🟡 **MEDIUM** | `#F1C40F` Amber | Elevated particle flux; minor operational risk | Increase monitoring cadence; review satellite health telemetry |
| 🟠 **HIGH** | `#E67E22` Orange | Significant radiation storm probability | Consider safe-mode readiness; notify satellite operations team |
| 🔴 **EXTREME** | `#E74C3C` Red | Severe/extreme radiation storm imminent or active | Initiate protective procedures; power down non-essential payloads; activate incident response |

---

## 📈 Performance Metrics

| Model | Metric | Value* |
|---|---|---|
| LSTM (Flux Forecast) | MAE | *reported per training run* |
| LSTM (Flux Forecast) | RMSE | *reported per training run* |
| XGBoost (Risk Classifier) | Precision (macro) | *reported per training run* |
| XGBoost (Risk Classifier) | Recall (macro) | *reported per training run* |
| XGBoost (Risk Classifier) | F1 Score (macro) | *reported per training run* |
| XGBoost (Risk Classifier) | ROC-AUC (OvR) | *reported per training run* |

*\*Populate this table automatically from `ml/evaluation/validate_models.py` output after each training run — metrics are written to `ml/evaluation/reports/latest_metrics.json`.*

<details>
<summary>📊 Sample Confusion Matrix (Risk Classification)</summary>

```
                Predicted
              LOW  MED  HIGH  EXT
Actual  LOW  [ ●    ·    ·    · ]
        MED  [ ·    ●    ·    · ]
        HIGH [ ·    ·    ●    · ]
        EXT  [ ·    ·    ·    ● ]
```
*(Generated automatically after each evaluation run — see `ml/evaluation/confusion_matrix.png`)*
</details>

---

## 🛣️ Future Roadmap

### 🎯 Near-Term
- [ ] SHAP-based explainability for XGBoost risk decisions
- [ ] Expanded alert channels (Slack, MS Teams)
- [ ] Historical event replay mode in dashboard

### 🚀 Mid-Term
- [ ] Transformer-based sequence models (replacing/augmenting LSTM)
- [ ] Prometheus + Grafana observability stack
- [ ] Kubernetes-native deployment (Helm charts)

### 🌠 Long-Term
- [ ] Vision Transformers for solar imagery analysis
- [ ] CNN-based CME detection directly from coronagraph imagery
- [ ] Native mobile app (iOS/Android) for on-the-go operator alerts
- [ ] Multi-satellite fleet risk correlation engine

---

## 🔐 Security

- **JWT Authentication** — stateless, short-lived access tokens with refresh-token rotation
- **HTTPS Everywhere** — TLS-terminated ingress for all production traffic
- **Rate Limiting** — per-IP and per-token throttling on all public endpoints
- **Input Validation** — strict Pydantic schema validation on every request payload
- **Secrets Management** — `.env`-based local secrets; Docker/K8s secrets in production, never committed to VCS
- **Docker Security** — non-root container users, minimal base images, dependency vulnerability scanning in CI

---

## 🧪 Testing

| Test Type | Tooling | Location |
|---|---|---|
| **Unit Tests** | `pytest` | `tests/unit/` |
| **Integration Tests** | `pytest` + test containers | `tests/integration/` |
| **API Tests** | `httpx` + `pytest-asyncio` | `tests/api/` |
| **Model Tests** | `pytest` + fixture datasets | `ml/tests/` |

```bash
# Run everything
pytest tests/ ml/tests/ -v --cov=backend --cov=ml
```

---

## 🤝 Contributing

Contributions are welcome and appreciated! To contribute:

1. **Fork** the repository
2. **Create a branch**: `git checkout -b feature/your-feature-name`
3. **Commit** your changes: `git commit -m "feat: add your feature"`
4. **Push** to your fork: `git push origin feature/your-feature-name`
5. **Open a Pull Request** describing your changes

> 📋 Please follow [Conventional Commits](https://www.conventionalcommits.org/) and ensure all tests pass (`pytest`, `npm test`) before submitting a PR.

---

## 👥 Team

<div align="center">

### **Team VoidArchitects**
*Bharatiya Antariksh Hackathon 2026 — ISRO × Hack2Skill*

<table>
<tr>
<td align="center" width="25%">
<b>👑 Neil Banerjee</b><br/>
<sub>Team Leader</sub><br/>
<sub>Institute of Advanced Research (IAR), Gandhinagar</sub>
</td>
<td align="center" width="25%">
<b>Devashya Jethva</b><br/>
<sub>Team Member</sub><br/>
<sub>Institute of Advanced Research (IAR), Gandhinagar</sub>
</td>
<td align="center" width="25%">
<b>Rajvardhansingh Chauhan</b><br/>
<sub>Team Member</sub><br/>
<sub>Institute of Advanced Research (IAR), Gandhinagar</sub>
</td>
<td align="center" width="25%">
<b>Manthan Balani</b><br/>
<sub>Team Member</sub><br/>
<sub>Institute of Advanced Research (IAR), Gandhinagar</sub>
</td>
</tr>
</table>

</div>

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](./LICENSE) file for details.

---

## 🙏 Acknowledgements

- 🇮🇳 **ISRO** — for the problem statement and vision behind this challenge
- 🚀 **NASA** — for open access to DONKI and heliophysics datasets
- 🌐 **NOAA SWPC** — for real-time space-weather data feeds
- 🛰️ **ESA** — for complementary space-weather research and data standards
- 🎉 **Hack2Skill (H2S)** — for organizing the Bharatiya Antariksh Hackathon 2026
- 💻 **The Open-Source Community** — for the tools, frameworks, and libraries that make projects like ASTRA possible

<div align="center">

---

**Made with 🛰️ by Team VoidArchitects for the Bharatiya Antariksh Hackathon 2026**

[⬆ Back to Top](#-astra)

</div>
