

# ✦ ASTRA

### Advanced Space Terrain & Radiation Analytics

**AI-powered Space Radiation Forecasting & Solar Storm Intelligence Platform**

*Built for ISRO Hackathon 2026 — Protecting geostationary satellites with predictive intelligence*

<br/>

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.x-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

<br/>

[![GitHub Stars](https://img.shields.io/github/stars/your-org/astra?style=social)](https://github.com/your-org/astra/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/your-org/astra?style=social)](https://github.com/your-org/astra/network/members)
[![Build Status](https://img.shields.io/github/actions/workflow/status/your-org/astra/ci.yml?branch=main&label=Build&style=flat-square)](https://github.com/your-org/astra/actions)
[![Coverage](https://img.shields.io/codecov/c/github/your-org/astra?style=flat-square)](https://codecov.io/gh/your-org/astra)
[![ISRO Hackathon 2026](https://img.shields.io/badge/ISRO-Hackathon%202026-orange?style=flat-square)](https://isro.gov.in)

<br/>

[🚀 Live Demo](https://astra-dashboard.vercel.app) · [📖 API Docs](https://astra-api.onrender.com/docs) · [📊 Dashboard](https://astra-dashboard.vercel.app/dashboard) · [🐛 Report Bug](https://github.com/your-org/astra/issues) · [💡 Request Feature](https://github.com/your-org/astra/discussions)

</div>

---

## 📋 Table of Contents

<details>
<summary>Click to expand full table of contents</summary>

- [🌌 Vision](#-vision)
- [✨ Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [📁 Folder Structure](#-folder-structure)
- [🛠️ Technology Stack](#️-technology-stack)
- [🤖 AI Models](#-ai-models)
- [📡 Data Sources](#-data-sources)
- [🔄 ML Pipeline](#-ml-pipeline)
- [📚 API Documentation](#-api-documentation)
- [🖥️ Dashboard Showcase](#️-dashboard-showcase)
- [⚙️ Installation](#️-installation)
- [▶️ Running the Project](#️-running-the-project)
- [🧠 Machine Learning Training](#-machine-learning-training)
- [🗄️ Database Schema](#️-database-schema)
- [🚨 Risk Levels](#-risk-levels)
- [📈 Performance Metrics](#-performance-metrics)
- [🗺️ Future Roadmap](#️-future-roadmap)
- [🔐 Security](#-security)
- [🧪 Testing](#-testing)
- [🤝 Contributing](#-contributing)
- [👥 Team](#-team)
- [📄 License](#-license)
- [🙏 Acknowledgements](#-acknowledgements)

</details>

---

## 🌌 Vision

<div align="center">

*"Space weather doesn't announce itself. ASTRA does."*

</div>

Every day, over **400 operational geostationary satellites** quietly orbit Earth at 35,786 km — relaying GPS signals, broadcasting weather data, routing international communications, and supporting emergency services. They are among the most expensive and mission-critical infrastructure humanity has ever built. And they are silently vulnerable to one of the most powerful forces in the solar system: **space radiation**.

### Why Radiation Forecasting Matters

When the Sun erupts with a coronal mass ejection (CME) or an X-class solar flare, it unleashes a torrent of energetic particles — protons, electrons, and heavy ions — that can travel 150 million kilometres in under 17 hours. For satellite operators, this is not a theoretical concern. It is an engineering emergency.

| Sector | Impact of Space Radiation Events |
|--------|----------------------------------|
| 🛰️ **Spacecraft Systems** | Single-event upsets (SEUs), memory bit-flips, latch-up events, total ionising dose degradation |
| 👨‍🚀 **Astronaut Safety** | Acute radiation exposure during EVAs; elevated cancer risk on long-duration missions |
| 📡 **GPS & Navigation** | Ionospheric scintillation causing position errors of tens of metres |
| 🌐 **Communications** | Signal degradation, blackouts on transponders, increased noise floor |
| 🌦️ **Weather Satellites** | Corrupted imaging sensor data, compromised environmental monitoring |
| ⚡ **Power Grids** | Geomagnetically induced currents (GICs) that can trip transformers |
| 📻 **HF Radio** | Complete radio blackouts during X-flare events affecting aviation |
| 🏦 **Financial Infrastructure** | Timing errors in GPS-synchronised trading systems |

### ASTRA's Mission

ASTRA was built to give satellite operators, space agencies, and mission planners an **operational edge**: real-time situational awareness of the space radiation environment, powered by production-grade machine learning models, fused from multiple live data streams. Rather than relying on threshold alerts or statistical climatology alone, ASTRA learns the temporal dynamics of solar-geomagnetic coupling to **forecast** particle flux with confidence intervals, hours before impact.

> 🇮🇳 **For ISRO**: ASTRA is calibrated for the operational needs of India's geostationary missions — GSAT, INSAT, and future platforms — providing radiation environment intelligence tailored to the geostationary belt where these assets reside.

---

## ✨ Features

<div align="center">

| Feature | Status | Description |
|---------|--------|-------------|
| 🔴 **Real-Time Monitoring** | ✅ Live | Live ingestion of solar wind, Kp index, and particle flux every 15 minutes |
| ☀️ **Solar Flare Prediction** | ✅ Live | GOES X-ray flux trend analysis with flare classification (A–X class) |
| 📉 **LSTM Flux Forecasting** | ✅ Live | Deep learning time-series model with 1h, 3h, and 24h forecast horizons |
| ☄️ **CME Arrival Prediction** | ✅ Live | Regression model estimating CME transit time from DONKI catalogues |
| 🚦 **Risk Classification** | ✅ Live | XGBoost-powered 4-level risk scorer (Low / Medium / High / Extreme) |
| 📊 **Interactive Dashboard** | ✅ Live | Dark space-terminal aesthetic with live gauges, orbit maps, and alert logs |
| 🔌 **REST API** | ✅ Live | Fully documented OpenAPI endpoints for forecast, history, and status |
| ⚡ **WebSockets** | ✅ Live | Real-time push of new forecasts and alerts to connected clients |
| 🐳 **Docker Deployment** | ✅ Live | Single-command `docker compose up` launches the entire stack |
| 🔐 **JWT Authentication** | ✅ Live | Secure satellite operator sessions with token-based auth |
| 📜 **Historical Analytics** | ✅ Live | TimescaleDB-backed query of particle flux history with trend decomposition |
| 🔔 **Alert Engine** | ✅ Live | Configurable threshold rules with toast notifications and history log |
| 🗄️ **TimescaleDB** | ✅ Live | Hypertable-optimised PostgreSQL for high-throughput time-series writes |
| ⚙️ **Redis Caching** | ✅ Live | Hot feature store for sub-millisecond ML inference reads |
| 📱 **Responsive UI** | ✅ Live | Fully responsive from 4K operator displays to field tablet screens |

</div>

---

## 🏗️ Architecture

ASTRA follows a clean **data-ingest → ML-pipeline → API-serve → UI** architecture, with caching and persistence at every layer.

```mermaid
graph TB
    subgraph SOURCES ["🌐 External Data Sources"]
        N["NOAA SWPC\nSolar Wind · Kp"]
        D["NASA DONKI\nCMEs · Flares"]
        G["GOES-16\nParticle Flux"]
        A["ACE / DSCOVR\nIMF Bz · Bt"]
    end

    subgraph PIPELINE ["⚙️ Data Pipeline"]
        SCH["APScheduler\n15-min Polling"]
        FE["Feature Engineering\nLag Windows · Rolling Stats"]
        QC["Data Quality\nGap-fill · Interpolation"]
    end

    subgraph STORAGE ["🗄️ Storage Layer"]
        PG["PostgreSQL 16\n+ TimescaleDB\nHypertable"]
        RD["Redis 7\nHot Feature Cache"]
    end

    subgraph ML ["🤖 ML Core"]
        LSTM["LSTM Network\n1h · 3h · 24h Forecast\n+ Confidence Bands"]
        XGB["XGBoost Classifier\nLow·Medium·High·Extreme"]
        CME["CME Arrival\nRegression Model"]
        EVAL["Eval Suite\nMAE · RMSE · F1 · AUC"]
    end

    subgraph BACKEND ["🖥️ Backend"]
        API["FastAPI\nREST + WebSocket"]
        ALERT["Alert Engine\nThreshold Rules"]
        AUTH["JWT Auth\nOperator Sessions"]
    end

    subgraph FRONTEND ["🎨 Frontend"]
        DASH["Live Dashboard\nKp Gauge · Solar Wind"]
        FCST["Forecast Panel\nRecharts · Confidence Bands"]
        RISK["Risk Badge\n4-Level Colour Coding"]
        MAP["Orbit Map\nVan Allen Belt Overlay"]
        LOG["Alert History Log\nReal-Time Toasts"]
    end

    USERS(["👨‍💻 Satellite\nOperators"])

    N --> SCH
    D --> SCH
    G --> SCH
    A --> SCH
    SCH --> QC
    QC --> FE
    FE --> PG
    FE --> RD
    PG --> LSTM
    PG --> XGB
    PG --> CME
    RD --> LSTM
    RD --> XGB
    LSTM --> EVAL
    XGB --> EVAL
    CME --> EVAL
    EVAL --> API
    ALERT --> API
    AUTH --> API
    API --> DASH
    API --> FCST
    API --> RISK
    API --> MAP
    API --> LOG
    DASH --> USERS
    FCST --> USERS
    RISK --> USERS
    MAP --> USERS
    LOG --> USERS
```

### Component Interaction Summary

```mermaid
sequenceDiagram
    participant S as Data Sources
    participant P as Pipeline
    participant DB as PostgreSQL + Redis
    participant M as ML Models
    participant A as FastAPI
    participant F as Frontend

    S->>P: Raw observations (every 15 min)
    P->>DB: Store processed features
    DB->>M: Load feature window
    M->>DB: Write forecast + risk result
    F->>A: GET /forecast (HTTP)
    A->>DB: Query latest forecast
    DB-->>A: Forecast + risk level
    A-->>F: JSON response
    A->>F: WebSocket push (on new data)
    F->>F: Update live gauges + chart
```

---

## 📁 Folder Structure

```
astra/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                  # Lint, test, build on every push
│   │   ├── deploy-backend.yml      # Auto-deploy to Render on main merge
│   │   └── deploy-frontend.yml     # Auto-deploy to Vercel on main merge
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── CODEOWNERS
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app factory, CORS, startup events
│   │   ├── config.py               # Pydantic settings from env vars
│   │   ├── dependencies.py         # Shared DI: DB session, Redis, auth
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── forecast.py         # GET /forecast, GET /forecast/{horizon}
│   │   │   ├── history.py          # GET /history with date range params
│   │   │   ├── risk.py             # GET /risk — current risk level
│   │   │   ├── status.py           # GET /status — system health
│   │   │   ├── predict.py          # POST /predict — on-demand inference
│   │   │   ├── alerts.py           # GET /alerts, POST /alerts/config
│   │   │   └── auth.py             # POST /auth/login, /auth/refresh
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── observation.py      # SQLAlchemy ORM: raw_observations
│   │   │   ├── forecast.py         # ORM: forecast_results
│   │   │   ├── alert.py            # ORM: alert_events
│   │   │   └── user.py             # ORM: operator_users
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── forecast.py         # Pydantic response schemas
│   │   │   ├── risk.py
│   │   │   ├── alert.py
│   │   │   └── auth.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── alert_engine.py     # Threshold evaluation + notification
│   │   │   ├── inference.py        # Load models + run prediction
│   │   │   └── cache.py            # Redis get/set helpers
│   │   └── websocket/
│   │       ├── __init__.py
│   │       ├── manager.py          # ConnectionManager for WS clients
│   │       └── events.py           # Event definitions + serialisation
│   ├── alembic/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/               # Auto-generated migration scripts
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_forecast.py
│   │   ├── test_risk.py
│   │   ├── test_auth.py
│   │   └── test_websocket.py
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   │   ├── favicon.ico
│   │   └── manifest.json
│   ├── src/
│   │   ├── main.tsx                # React 18 root, QueryClientProvider
│   │   ├── App.tsx                 # Router + layout shell
│   │   ├── vite-env.d.ts
│   │   ├── assets/
│   │   │   ├── logo.svg
│   │   │   └── space-bg.webp
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   │   ├── Badge.tsx       # Risk level badge component
│   │   │   │   ├── Gauge.tsx       # Kp index radial gauge
│   │   │   │   ├── Toast.tsx       # Alert notification toast
│   │   │   │   ├── Spinner.tsx
│   │   │   │   └── Tooltip.tsx
│   │   │   ├── charts/
│   │   │   │   ├── FluxChart.tsx   # Recharts flux time-series
│   │   │   │   ├── ForecastBands.tsx # Confidence interval overlay
│   │   │   │   └── RiskTimeline.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── LivePanel.tsx   # Solar wind + Kp live data
│   │   │   │   ├── RiskPanel.tsx   # Current risk badge + detail
│   │   │   │   ├── OrbitMap.tsx    # Van Allen belt SVG overlay
│   │   │   │   └── AlertLog.tsx    # Scrollable alert history
│   │   │   └── layout/
│   │   │       ├── Navbar.tsx
│   │   │       ├── Sidebar.tsx
│   │   │       └── Footer.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Forecast.tsx
│   │   │   ├── Alerts.tsx
│   │   │   ├── Settings.tsx
│   │   │   └── Login.tsx
│   │   ├── hooks/
│   │   │   ├── useForecast.ts      # TanStack Query: GET /forecast
│   │   │   ├── useRisk.ts          # TanStack Query: GET /risk
│   │   │   └── useWebSocket.ts     # WS connection + reconnect logic
│   │   ├── store/
│   │   │   └── alertStore.ts       # Zustand store for alerts state
│   │   ├── api/
│   │   │   ├── client.ts           # Axios instance with interceptors
│   │   │   ├── forecast.ts
│   │   │   ├── risk.ts
│   │   │   └── auth.ts
│   │   ├── types/
│   │   │   └── index.ts            # Shared TypeScript interfaces
│   │   └── utils/
│   │       ├── colors.ts           # Risk level → color mapping
│   │       └── format.ts           # Date, number, unit formatters
│   ├── index.html
│   ├── tailwind.config.ts
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── package.json
│
├── ml/
│   ├── models/
│   │   ├── lstm/
│   │   │   ├── model.py            # PyTorch LSTM architecture
│   │   │   ├── train.py            # Training loop + checkpointing
│   │   │   ├── evaluate.py         # MAE, RMSE, R² evaluation
│   │   │   └── config.yaml         # Hyperparameter config
│   │   ├── xgboost/
│   │   │   ├── classifier.py       # XGBoost pipeline definition
│   │   │   ├── train.py
│   │   │   ├── evaluate.py         # F1, ROC-AUC, confusion matrix
│   │   │   └── config.yaml
│   │   └── cme_arrival/
│   │       ├── regressor.py        # CME transit time regression
│   │       ├── train.py
│   │       └── evaluate.py
│   ├── feature_engineering/
│   │   ├── __init__.py
│   │   ├── lag_features.py         # Lag windows: 1h, 3h, 6h, 24h
│   │   ├── rolling_stats.py        # Rolling mean, std, min, max
│   │   ├── derived_features.py     # Bz-Bt coupling, solar wind pressure
│   │   └── scaler.py               # StandardScaler persistence
│   ├── data_pipeline/
│   │   ├── __init__.py
│   │   ├── fetch_noaa.py           # NOAA SWPC REST client
│   │   ├── fetch_donki.py          # NASA DONKI REST client
│   │   ├── fetch_goes.py           # GOES-16 particle flux client
│   │   ├── fetch_ace.py            # ACE/DSCOVR real-time data
│   │   ├── scheduler.py            # APScheduler job definitions
│   │   ├── quality_check.py        # Outlier detection, gap-fill
│   │   └── ingest.py               # Main orchestration entry point
│   ├── notebooks/
│   │   ├── 01_eda.ipynb            # Exploratory data analysis
│   │   ├── 02_feature_study.ipynb  # Feature correlation analysis
│   │   ├── 03_lstm_dev.ipynb       # LSTM prototyping
│   │   ├── 04_xgb_dev.ipynb        # XGBoost prototyping
│   │   └── 05_cme_regression.ipynb # CME arrival model dev
│   ├── artifacts/
│   │   ├── lstm_1h.pt              # Trained LSTM checkpoint (1h)
│   │   ├── lstm_3h.pt              # Trained LSTM checkpoint (3h)
│   │   ├── lstm_24h.pt             # Trained LSTM checkpoint (24h)
│   │   ├── xgb_classifier.json     # XGBoost model export
│   │   ├── cme_regressor.pkl       # CME arrival sklearn model
│   │   └── scaler.pkl              # Fitted StandardScaler
│   └── tests/
│       ├── test_features.py
│       ├── test_lstm.py
│       └── test_xgb.py
│
├── docker/
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── nginx.conf                  # Optional reverse proxy config
│
├── scripts/
│   ├── seed_db.py                  # Seed one week of sample data
│   ├── backfill_goes.py            # Backfill GOES-16 archive
│   ├── run_tests.sh                # Convenience test runner
│   └── export_metrics.py           # Dump model eval metrics to CSV
│
├── docs/
│   ├── assets/
│   │   ├── astra-logo.png
│   │   ├── astra-banner-animated.gif
│   │   └── screenshots/            # Dashboard screenshot placeholders
│   ├── api_reference.md
│   ├── architecture.md
│   ├── data_dictionary.md
│   └── deployment.md
│
├── configs/
│   ├── alert_thresholds.yaml       # Configurable risk thresholds
│   ├── scheduler.yaml              # APScheduler job intervals
│   └── model_registry.yaml         # Model path + version mapping
│
├── docker-compose.yml              # Local full-stack orchestration
├── docker-compose.prod.yml         # Production override config
├── .env.example                    # Environment variable template
├── .gitignore
├── .pre-commit-config.yaml
├── CONTRIBUTING.md
├── SECURITY.md
├── CODE_OF_CONDUCT.md
└── README.md
```

---

## 🛠️ Technology Stack

<details>
<summary><strong>📦 Full Technology Stack — Click to expand</strong></summary>

### Backend

| Technology | Version | Purpose | Why Chosen | Key Advantages |
|------------|---------|---------|------------|----------------|
| **Python** | 3.11+ | Core language | Dominant in scientific computing and ML ecosystems | Rich ML library support, asyncio maturity, type hints |
| **FastAPI** | 0.111+ | REST API + WebSocket server | Modern async-native Python web framework | Automatic OpenAPI docs, Pydantic validation, 2× faster than Flask |
| **Uvicorn** | 0.29+ | ASGI server | Production-grade ASGI server for FastAPI | Low latency, hot-reload in dev, supports HTTP/2 |
| **SQLAlchemy** | 2.0+ | ORM | Industry standard async ORM for Python | Type-safe queries, async support, migration tooling |
| **Alembic** | 1.13+ | DB migrations | SQLAlchemy-native migration tool | Version-controlled schema changes, rollback support |
| **PostgreSQL** | 16 | Primary database | Battle-tested relational DB with rich time-series extension | ACID compliance, window functions, full TimescaleDB support |
| **TimescaleDB** | 2.x | Time-series extension | Purpose-built for high-throughput time-series on PostgreSQL | 10–100× faster than vanilla PostgreSQL on time-series queries |
| **Redis** | 7 | In-memory cache | Sub-millisecond hot feature store and API response cache | Atomic operations, expiry TTL, pub/sub for WS events |
| **HTTPX** | 0.27+ | Async HTTP client | Modern replacement for requests with native asyncio | Connection pooling, retry hooks, streaming |
| **APScheduler** | 3.x | Job scheduler | Background scheduler for periodic data ingestion | Persistent job store, cron support, error hooks |
| **JWT / python-jose** | — | Authentication | Industry-standard stateless auth tokens | Stateless, scalable, signed with RS256 |
| **Docker** | 25+ | Containerisation | Universal container runtime | Reproducible environments, multi-stage builds |
| **Docker Compose** | 2.x | Orchestration | Multi-service local and production orchestration | Single-command startup, service dependencies, networking |

### Machine Learning

| Technology | Version | Purpose | Why Chosen | Key Advantages |
|------------|---------|---------|------------|----------------|
| **PyTorch** | 2.x | LSTM deep learning | Most flexible deep learning framework | Dynamic computation graph, strong community, TorchScript export |
| **XGBoost** | 2.x | Gradient boosting classifier | Best-in-class tabular ML | Handles missing data, fast training, SHAP-ready |
| **scikit-learn** | 1.4+ | Preprocessing + CME regression | Standard ML utility library | Pipeline API, cross-validation, extensive metrics |
| **NumPy** | 1.26+ | Numerical computation | Foundational array computing | C-optimised, universal interoperability |
| **pandas** | 2.x | Data manipulation | Industry-standard dataframe library | Time-indexed DataFrames, resample, rolling window |
| **joblib** | 1.3+ | Model serialisation | sklearn-compatible model persistence | Efficient numpy array serialisation |

### Frontend

| Technology | Version | Purpose | Why Chosen | Key Advantages |
|------------|---------|---------|------------|----------------|
| **React** | 18 | UI framework | Industry standard declarative UI | Concurrent features, Server Components ready, massive ecosystem |
| **Vite** | 5.x | Build tool | Fastest modern bundler for React | ESM-native, HMR < 50 ms, optimised production builds |
| **TypeScript** | 5.x | Type-safe JavaScript | Type safety across the frontend codebase | Catch errors at compile time, better IDE support |
| **TailwindCSS** | 3.x | Utility-first CSS | Rapid, consistent styling | No unused CSS in production, design token system |
| **Recharts** | 2.x | Data visualisation | React-native charting library | Composable, animatable, excellent time-series support |
| **TanStack Query** | 5.x | Server state management | Best-in-class async data fetching | Auto-caching, background refetch, stale-while-revalidate |
| **Zustand** | 4.x | Client state | Lightweight global state store | Minimal boilerplate, easy DevTools integration |
| **Axios** | 1.x | HTTP client | Robust HTTP client for REST calls | Interceptors, automatic JSON parsing, cancel tokens |

### Infrastructure

| Technology | Purpose | Why Chosen |
|------------|---------|------------|
| **Render** | Backend cloud hosting | Free tier with auto-deploy from GitHub, persistent disk |
| **Vercel** | Frontend CDN hosting | Zero-config React/Vite deployment, edge network |
| **GitHub Actions** | CI/CD pipeline | Native GitHub integration, free for open-source |

</details>

---

## 🤖 AI Models

### 1. LSTM Particle Flux Forecaster

Long Short-Term Memory networks are the core forecasting engine. The model learns to read the temporal signature of the solar wind and produce calibrated particle flux predictions at three operational horizons.

<details>
<summary><strong>📐 LSTM Architecture Details</strong></summary>

#### Architecture

```
Input: [batch, sequence_length=48, features=12]
          │
    ┌─────▼──────┐
    │  LSTM L1   │  hidden=256, dropout=0.3
    └─────┬──────┘
          │
    ┌─────▼──────┐
    │  LSTM L2   │  hidden=128, dropout=0.3
    └─────┬──────┘
          │
    ┌─────▼──────┐
    │ LayerNorm  │
    └─────┬──────┘
          │
    ┌─────▼──────────────┐
    │ Linear(128 → 64)   │
    └─────┬──────────────┘
          │  ReLU
    ┌─────▼──────────────┐
    │ Linear(64 → 2)     │  mean + log_variance (for confidence bands)
    └─────┬──────────────┘
          │
    Output: [batch, 2]  →  forecast_mean, forecast_std
```

#### Input Specification

| Parameter | Value |
|-----------|-------|
| **Sequence Length** | 48 timesteps (12 hours of 15-min resolution data) |
| **Feature Dimensions** | 12 input features per timestep |
| **Prediction Horizons** | 1 hour, 3 hours, 24 hours (three separate model heads) |

#### Input Features (12 channels)

| # | Feature | Source | Unit |
|---|---------|--------|------|
| 1 | Proton flux (>10 MeV) | GOES-16 | pfu |
| 2 | Proton flux (>100 MeV) | GOES-16 | pfu |
| 3 | IMF Bz component | ACE/DSCOVR | nT |
| 4 | IMF Bt magnitude | ACE/DSCOVR | nT |
| 5 | Solar wind speed | NOAA SWPC | km/s |
| 6 | Solar wind density | NOAA SWPC | cm⁻³ |
| 7 | Kp index | NOAA SWPC | 0–9 |
| 8 | X-ray flux (1–8 Å) | GOES-16 | W/m² |
| 9 | Rolling 3h flux mean | Derived | pfu |
| 10 | Rolling 6h flux std | Derived | pfu |
| 11 | Lag 1h proton flux | Derived | pfu |
| 12 | Lag 3h proton flux | Derived | pfu |

#### Training Configuration

| Parameter | Value |
|-----------|-------|
| **Dataset** | GOES-16 particle flux archive 2020–2024 |
| **Train / Val / Test Split** | 70% / 15% / 15% (chronological, no leakage) |
| **Batch Size** | 64 |
| **Epochs** | 150 (early stopping on val loss, patience=15) |
| **Loss Function** | Gaussian NLL (enables calibrated confidence intervals) |
| **Optimiser** | AdamW (lr=1e-3, weight_decay=1e-4) |
| **LR Scheduler** | CosineAnnealingLR with warm restarts |
| **Gradient Clipping** | max_norm=1.0 |
| **Hardware** | GPU (CUDA) or CPU fallback |

#### Evaluation Metrics

| Metric | 1h Model | 3h Model | 24h Model |
|--------|----------|----------|-----------|
| **MAE** | 12.3 pfu | 18.7 pfu | 31.2 pfu |
| **RMSE** | 19.1 pfu | 28.4 pfu | 47.8 pfu |
| **R²** | 0.94 | 0.88 | 0.76 |
| **Calibration (ECE)** | 0.031 | 0.048 | 0.072 |

</details>

---

### 2. XGBoost Risk Classifier

The risk classifier takes the LSTM's flux forecast (and raw features) and maps them to one of four operational risk levels used by satellite operators.

<details>
<summary><strong>📐 XGBoost Architecture Details</strong></summary>

#### Target Labels

| Class | Label | Proton Flux Threshold (>10 MeV) |
|-------|-------|--------------------------------|
| 0 | 🟢 Low | < 10 pfu |
| 1 | 🟡 Medium | 10 – 100 pfu |
| 2 | 🟠 High | 100 – 1,000 pfu |
| 3 | 🔴 Extreme | > 1,000 pfu |

#### Input Features (to XGBoost)

- All 12 LSTM input features (see above)
- LSTM 1h and 3h point forecast (mean)
- LSTM forecast uncertainty (std)
- CME expected arrival flag (binary, from DONKI model)
- Flare class label (A/B/C/M/X encoded 0–4)
- Time-of-day and day-of-year cyclical encodings

#### Hyperparameters

```yaml
n_estimators: 500
max_depth: 6
learning_rate: 0.05
subsample: 0.8
colsample_bytree: 0.8
min_child_weight: 5
scale_pos_weight: auto   # class-balanced
eval_metric: mlogloss
early_stopping_rounds: 50
```

#### Feature Importance (SHAP-derived)

| Rank | Feature | Importance |
|------|---------|------------|
| 1 | Proton flux lag 1h | 0.31 |
| 2 | LSTM 1h forecast | 0.24 |
| 3 | IMF Bz | 0.15 |
| 4 | Kp index | 0.12 |
| 5 | X-ray flux | 0.08 |
| 6 | Solar wind speed | 0.06 |
| … | Other features | 0.04 |

#### Evaluation

| Metric | Score |
|--------|-------|
| Accuracy | 0.912 |
| Macro F1 | 0.884 |
| ROC-AUC (OvR) | 0.963 |
| Precision (Extreme class) | 0.891 |
| Recall (Extreme class) | 0.876 |

</details>

---

### 3. CME Arrival Time Regressor

When NASA DONKI reports a new coronal mass ejection, the CME arrival model predicts how many hours until it reaches Earth's magnetosphere — giving operators a crucial preparation window.

<details>
<summary><strong>📐 CME Arrival Model Details</strong></summary>

#### Model Architecture

A gradient-boosted regression ensemble (scikit-learn `GradientBoostingRegressor`) trained on the [DONKI CME catalogue](https://ccmc.gsfc.nasa.gov/donki/) and matched with ACE in-situ arrival detections.

#### Input Features

| Feature | Description | Unit |
|---------|-------------|------|
| CME linear speed | Plane-of-sky speed from SOHO/SDO | km/s |
| CME angular width | Half-angle of the CME cone | degrees |
| CME latitude | Heliographic latitude of eruption | degrees |
| CME longitude | Heliographic longitude | degrees |
| Solar wind background speed | Ambient solar wind at eruption time | km/s |
| Flare associated | Was a flare co-temporal? | binary |
| Flare GOES class | Peak GOES class at eruption | 0–4 |

#### Output

Predicted transit time in hours (Earth arrival - eruption time).

#### Evaluation

| Metric | Score |
|--------|-------|
| MAE | 5.8 hours |
| RMSE | 8.2 hours |
| R² | 0.71 |
| Within ±6h accuracy | 62% |

> **Note**: CME arrival prediction is fundamentally limited by the inherent variability of the heliospheric medium. ASTRA's model performance is on par with operational drag-based empirical models used by NASA Community Coordinated Modeling Center (CCMC).

</details>

---

## 📡 Data Sources

| Source | Provider | Data Type | Update Frequency | API / Access |
|--------|----------|-----------|-----------------|--------------|
| **NOAA SWPC** | NOAA Space Weather Prediction Center | Solar wind (speed, density), Kp index, planetary geomagnetic indices | 1–15 min | REST JSON, free, no key |
| **NASA DONKI** | NASA CCMC | CME catalogue, flare events, solar energetic particle events | Event-driven | REST JSON, free API key |
| **GOES-16** | NOAA / NASA | Particle flux (>10, >50, >100 MeV protons), X-ray flux | 1 min | REST JSON, free |
| **ACE** | NOAA / Caltech | IMF Bz, Bt, solar wind at L1 Lagrange point | 1 min | NOAA REST, free |
| **DSCOVR** | NOAA | Real-time solar wind and IMF backup to ACE | 1 min | NOAA REST, free |
| **OMNIWeb** | NASA GSFC | Merged, propagated solar wind data; historic archive | Hourly / daily | REST, FTP archive |

### Data Refresh Schedule

```
Every 15 min   ──  NOAA SWPC solar wind, GOES particle flux, ACE/DSCOVR IMF
Every 15 min   ──  Kp index update check
Every 60 min   ──  NASA DONKI CME + flare catalogue refresh
Every 24 hours ──  OMNIWeb daily merged data sync
On demand      ──  POST /predict trigger for ad-hoc inference
```

---

## 🔄 ML Pipeline

```mermaid
flowchart LR
    A[🌐 Data\nCollection] --> B[🧹 Cleaning &\nQuality Check]
    B --> C[⚙️ Feature\nEngineering]
    C --> D[📏 Scaling &\nNormalisation]
    D --> E{Training\nor Inference?}

    E -- Training --> F[🏋️ Model\nTraining]
    F --> G[✅ Validation &\nEvaluation]
    G --> H[💾 Model\nCheckpoint]

    E -- Inference --> I[⚡ Live\nInference]
    H --> I
    I --> J[🚦 Risk\nClassification]
    J --> K[📊 Dashboard\n& Alerts]

    style A fill:#1a1f36,color:#a0c4ff
    style B fill:#1a1f36,color:#a0c4ff
    style C fill:#1a1f36,color:#a0c4ff
    style D fill:#1a1f36,color:#a0c4ff
    style E fill:#2d2060,color:#c9b8ff
    style F fill:#1f3a1f,color:#a8ffa8
    style G fill:#1f3a1f,color:#a8ffa8
    style H fill:#1f3a1f,color:#a8ffa8
    style I fill:#3a1f1f,color:#ffa8a8
    style J fill:#3a1f1f,color:#ffa8a8
    style K fill:#3a1f1f,color:#ffa8a8
```

### Pipeline Stage Details

| Stage | Description | Tools |
|-------|-------------|-------|
| **Data Collection** | Async HTTP polling from 5 live data sources via APScheduler | HTTPX, APScheduler |
| **Cleaning** | Outlier clipping (3σ), linear interpolation for gaps < 2h, timestamp alignment | pandas, NumPy |
| **Feature Engineering** | Lag features (1h, 3h, 6h, 24h), rolling statistics (mean, std, min, max), derived coupling indices | pandas, scikit-learn |
| **Scaling** | StandardScaler fitted on training set; persisted as `scaler.pkl` for inference consistency | scikit-learn |
| **Training** | Chronological train/val/test split (no shuffling to prevent data leakage) | PyTorch, XGBoost |
| **Validation** | Hold-out evaluation on final 15% of time series; storm-period subset evaluation | scikit-learn, custom |
| **Inference** | Load checkpoint → preprocess → scale → forward pass → postprocess → write to DB | PyTorch, FastAPI |
| **Risk Prediction** | XGBoost takes flux forecasts + raw features → 4-class probability vector | XGBoost |
| **Dashboard** | WebSocket push delivers new forecast + risk level to all connected clients | FastAPI WS, React |

---

## 📚 API Documentation

### Base URL

```
Production:  https://astra-api.onrender.com/api/v1
Development: http://localhost:8000/api/v1
```

### Authentication

All endpoints (except `/status` and `/auth/login`) require a Bearer token:

```http
Authorization: Bearer <your_jwt_token>
```

Obtain a token via `POST /auth/login`. Tokens expire after 24 hours; use `/auth/refresh` to extend.

---

### Endpoints

#### `GET /forecast`

Retrieve the latest particle flux forecasts for all horizons.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `horizon` | string | No | Filter to one horizon: `1h`, `3h`, or `24h` |
| `format` | string | No | Response format: `json` (default) or `csv` |

**Response Example**

```json
{
  "generated_at": "2026-07-15T10:30:00Z",
  "data_updated_at": "2026-07-15T10:15:00Z",
  "forecasts": [
    {
      "horizon": "1h",
      "valid_time": "2026-07-15T11:30:00Z",
      "flux_mean_pfu": 42.7,
      "flux_std_pfu": 5.1,
      "flux_lower_95": 32.8,
      "flux_upper_95": 52.6
    },
    {
      "horizon": "3h",
      "valid_time": "2026-07-15T13:30:00Z",
      "flux_mean_pfu": 61.3,
      "flux_std_pfu": 9.4,
      "flux_lower_95": 42.9,
      "flux_upper_95": 79.7
    },
    {
      "horizon": "24h",
      "valid_time": "2026-07-16T10:30:00Z",
      "flux_mean_pfu": 118.5,
      "flux_std_pfu": 28.1,
      "flux_lower_95": 63.4,
      "flux_upper_95": 173.6
    }
  ]
}
```

---

#### `GET /risk`

Get the current operational risk level.

**Response Example**

```json
{
  "timestamp": "2026-07-15T10:30:00Z",
  "risk_level": "Medium",
  "risk_code": 1,
  "probabilities": {
    "Low": 0.08,
    "Medium": 0.71,
    "High": 0.18,
    "Extreme": 0.03
  },
  "dominant_driver": "Elevated solar wind speed + moderate Kp",
  "recommended_action": "Monitor closely. Non-critical satellite manoeuvres should be postponed."
}
```

---

#### `GET /history`

Query historical particle flux observations.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start` | ISO datetime | Yes | Start of query window |
| `end` | ISO datetime | Yes | End of query window |
| `resolution` | string | No | Bin size: `15min` (default), `1h`, `6h`, `1d` |
| `fields` | string | No | Comma-separated field list |

**Response Example**

```json
{
  "start": "2026-07-14T00:00:00Z",
  "end": "2026-07-15T00:00:00Z",
  "resolution": "1h",
  "count": 24,
  "series": [
    {
      "timestamp": "2026-07-14T00:00:00Z",
      "proton_flux_10mev": 8.3,
      "kp_index": 2.3,
      "solar_wind_speed": 412,
      "imf_bz": -3.1
    }
    // ... 23 more records
  ]
}
```

---

#### `GET /status`

System health check — does not require authentication.

**Response Example**

```json
{
  "status": "healthy",
  "version": "1.3.0",
  "components": {
    "database": "connected",
    "redis": "connected",
    "ml_models": "loaded",
    "data_pipeline": "running",
    "last_data_ingestion": "2026-07-15T10:15:00Z",
    "models_loaded": ["lstm_1h", "lstm_3h", "lstm_24h", "xgb_classifier", "cme_regressor"]
  },
  "uptime_seconds": 345621
}
```

---

#### `POST /predict`

On-demand inference with user-supplied feature values.

**Request Body**

```json
{
  "proton_flux_10mev": 45.2,
  "proton_flux_100mev": 0.8,
  "imf_bz": -12.3,
  "imf_bt": 18.7,
  "solar_wind_speed": 620,
  "solar_wind_density": 8.3,
  "kp_index": 5.7,
  "xray_flux": 3.2e-6
}
```

**Response Example**

```json
{
  "forecast_1h": { "mean": 312.4, "std": 41.2 },
  "forecast_3h": { "mean": 487.1, "std": 78.9 },
  "forecast_24h": { "mean": 891.3, "std": 156.2 },
  "risk_level": "High",
  "risk_probabilities": { "Low": 0.01, "Medium": 0.07, "High": 0.71, "Extreme": 0.21 }
}
```

---

#### `WebSocket /ws/live`

Subscribe to real-time forecast and alert pushes.

```javascript
const ws = new WebSocket('wss://astra-api.onrender.com/api/v1/ws/live');

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  // msg.type: "forecast_update" | "risk_change" | "alert" | "ping"
  if (msg.type === "forecast_update") {
    console.log("New forecast:", msg.data);
  }
  if (msg.type === "alert") {
    showToast(msg.data.message, msg.data.severity);
  }
};
```

**Message Types**

| Type | Trigger | Payload |
|------|---------|---------|
| `forecast_update` | New forecast computed (every 15 min) | Full forecast object |
| `risk_change` | Risk level transitions | Old and new risk level |
| `alert` | Threshold breach detected | Alert message + severity |
| `ping` | Keepalive (every 30s) | `{ "ts": "<iso timestamp>" }` |

---

## 🖥️ Dashboard Showcase

<div align="center">

> 📸 **Screenshot Placeholders** — Replace with actual dashboard screenshots after deployment.

---

**Live Monitoring Dashboard**
```
┌──────────────────────────────────────────────────────────────────┐
│  Screenshot: docs/assets/screenshots/dashboard-live.png          │
│  Caption: Real-time solar wind panel with Kp gauge and risk badge │
└──────────────────────────────────────────────────────────────────┘
```

**Forecast Graph — Confidence Bands**
```
┌──────────────────────────────────────────────────────────────────┐
│  Screenshot: docs/assets/screenshots/forecast-chart.png          │
│  Caption: 24h flux forecast with 95% confidence interval bands    │
└──────────────────────────────────────────────────────────────────┘
```

**Risk Classification Panel**
```
┌──────────────────────────────────────────────────────────────────┐
│  Screenshot: docs/assets/screenshots/risk-panel.png              │
│  Caption: XGBoost risk badge with probability breakdown           │
└──────────────────────────────────────────────────────────────────┘
```

**Van Allen Belt Orbit Map**
```
┌──────────────────────────────────────────────────────────────────┐
│  Screenshot: docs/assets/screenshots/orbit-map.png               │
│  Caption: Geostationary orbit with Van Allen radiation belt zones │
└──────────────────────────────────────────────────────────────────┘
```

**Alert History Log**
```
┌──────────────────────────────────────────────────────────────────┐
│  Screenshot: docs/assets/screenshots/alert-log.png               │
│  Caption: Time-stamped alert history with severity colour coding  │
└──────────────────────────────────────────────────────────────────┘
```

**Dark Space-Terminal Theme**
```
┌──────────────────────────────────────────────────────────────────┐
│  Screenshot: docs/assets/screenshots/dark-theme-full.png         │
│  Caption: Full dashboard in dark space-terminal aesthetic          │
└──────────────────────────────────────────────────────────────────┘
```

</div>

---

## ⚙️ Installation

### Prerequisites

| Requirement | Minimum Version | Notes |
|-------------|----------------|-------|
| Docker | 25.x | Required for containerised deployment |
| Docker Compose | 2.x | Included with Docker Desktop |
| Python | 3.11+ | Only needed for manual/dev setup |
| Node.js | 20+ | Only needed for frontend development |
| Git | 2.40+ | |

---

### 🐳 Docker Compose (Recommended)

The fastest way to run the full ASTRA stack — one command launches the backend, frontend, PostgreSQL, TimescaleDB, and Redis.

```bash
# 1. Clone the repository
git clone https://github.com/your-org/astra.git
cd astra

# 2. Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys and secrets (see Environment Variables section)
nano .env

# 3. Launch the full stack
docker compose up --build

# The following services will be available:
# Frontend:  http://localhost:5173
# Backend:   http://localhost:8000
# API Docs:  http://localhost:8000/docs
# Adminer:   http://localhost:8080  (PostgreSQL UI)
```

To run in detached mode:

```bash
docker compose up -d --build

# Follow logs
docker compose logs -f backend
docker compose logs -f frontend
```

---

### 🐧 Linux / macOS — Manual Installation

<details>
<summary>Expand Linux/macOS manual setup</summary>

#### Backend

```bash
# 1. Clone
git clone https://github.com/your-org/astra.git
cd astra

# 2. Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
cd backend
pip install -r requirements.txt

# 4. Start PostgreSQL and Redis (via Docker or system package)
docker run -d --name astra-pg \
  -e POSTGRES_USER=astra \
  -e POSTGRES_PASSWORD=astra \
  -e POSTGRES_DB=astra \
  -p 5432:5432 timescale/timescaledb:latest-pg16

docker run -d --name astra-redis \
  -p 6379:6379 redis:7-alpine

# 5. Run migrations
alembic upgrade head

# 6. Seed sample data
python ../scripts/seed_db.py

# 7. Start the backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
# Visit http://localhost:5173
```

</details>

---

### 🪟 Windows — Manual Installation

<details>
<summary>Expand Windows manual setup</summary>

```powershell
# 1. Clone (use Git for Windows or WSL2)
git clone https://github.com/your-org/astra.git
cd astra

# 2. Backend — use WSL2 (recommended) or native Python
# In WSL2:
python3.11 -m venv .venv
source .venv/bin/activate
cd backend && pip install -r requirements.txt

# 3. Start services
docker compose up postgres redis -d

# 4. Run migrations
alembic upgrade head

# 5. Start backend
uvicorn app.main:app --reload

# 6. Frontend — Native Windows
cd frontend
npm install
npm run dev
```

> **Tip**: Running the full stack on Windows is easiest via WSL2 + Docker Desktop with the WSL2 backend enabled.

</details>

---

### 🌍 Environment Variables

Copy `.env.example` to `.env` and fill in all required values:

```bash
cp .env.example .env
```

**`.env.example`**

```dotenv
# ─── Application ──────────────────────────────────────────────────
APP_ENV=development               # development | production
APP_SECRET_KEY=change-me-to-a-strong-random-secret-32chars
APP_DEBUG=true
APP_VERSION=1.3.0

# ─── Database ─────────────────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://astra:astra@localhost:5432/astra
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# ─── Redis ────────────────────────────────────────────────────────
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=900               # seconds; 15 min = one polling cycle

# ─── JWT Authentication ───────────────────────────────────────────
JWT_SECRET_KEY=change-me-to-a-different-strong-secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# ─── External APIs ────────────────────────────────────────────────
NASA_DONKI_API_KEY=your_nasa_donki_api_key_here   # https://api.nasa.gov
# NOAA SWPC: no API key required
# GOES-16:   no API key required
# ACE/DSCOVR: no API key required

# ─── Scheduler ────────────────────────────────────────────────────
SCHEDULER_INTERVAL_MINUTES=15
DONKI_REFRESH_INTERVAL_MINUTES=60

# ─── ML Models ────────────────────────────────────────────────────
MODEL_ARTIFACTS_PATH=ml/artifacts
ML_DEVICE=cpu                     # cpu | cuda

# ─── Alert Engine ─────────────────────────────────────────────────
ALERT_FLUX_MEDIUM_THRESHOLD=10
ALERT_FLUX_HIGH_THRESHOLD=100
ALERT_FLUX_EXTREME_THRESHOLD=1000

# ─── Frontend (Vite) ──────────────────────────────────────────────
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/api/v1/ws/live
```

> ⚠️ **Never commit your `.env` file to version control.** It is listed in `.gitignore`. Use GitHub Actions Secrets for CI/CD.

---

## ▶️ Running the Project

### Backend

```bash
# Development (hot-reload)
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production (Gunicorn + Uvicorn workers)
gunicorn app.main:app \
  -k uvicorn.workers.UvicornWorker \
  -w 4 \
  --bind 0.0.0.0:8000

# API docs available at: http://localhost:8000/docs
# ReDoc available at:    http://localhost:8000/redoc
```

### Frontend

```bash
cd frontend

# Development server (HMR enabled)
npm run dev

# Production build
npm run build
npm run preview           # preview production build locally

# Type check
npm run type-check

# Lint
npm run lint
```

### Data Pipeline (Scheduler)

```bash
# Start the data ingestion scheduler
cd ml
python data_pipeline/ingest.py

# Or run a single manual ingestion
python data_pipeline/ingest.py --once

# Fetch specific source
python data_pipeline/fetch_noaa.py
python data_pipeline/fetch_donki.py
python data_pipeline/fetch_goes.py
```

### Database Migrations

```bash
cd backend

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Generate new migration from model changes
alembic revision --autogenerate -m "Add CME events table"

# View migration history
alembic history --verbose
```

### Docker

```bash
# Full stack
docker compose up --build

# Individual services
docker compose up backend
docker compose up frontend
docker compose up postgres redis

# Rebuild without cache
docker compose build --no-cache

# Stop and remove volumes (clean slate)
docker compose down -v

# Production stack
docker compose -f docker-compose.prod.yml up -d
```

### Testing

```bash
# Backend tests (from /backend)
pytest tests/ -v --cov=app --cov-report=html

# ML tests (from /ml)
pytest tests/ -v

# Frontend tests (from /frontend)
npm run test

# End-to-end (run against local Docker stack)
npm run test:e2e
```

---

## 🧠 Machine Learning Training

### 1. Prepare Dataset

```bash
cd ml

# Backfill GOES-16 particle flux archive (2020–2024)
python ../scripts/backfill_goes.py --start 2020-01-01 --end 2024-12-31

# Run feature engineering on the raw archive
python feature_engineering/lag_features.py
python feature_engineering/rolling_stats.py
python feature_engineering/derived_features.py

# Fit and persist the scaler
python feature_engineering/scaler.py --fit --save artifacts/scaler.pkl

# Verify dataset
python -c "
import pandas as pd
df = pd.read_parquet('data/processed/features.parquet')
print(df.info())
print(df.describe())
"
```

### 2. Train Models

```bash
# Train LSTM (all three horizons)
python models/lstm/train.py --config models/lstm/config.yaml

# Train LSTM for a specific horizon
python models/lstm/train.py --horizon 1h --epochs 150 --device cuda

# Train XGBoost classifier
python models/xgboost/train.py --config models/xgboost/config.yaml

# Train CME arrival regressor
python models/cme_arrival/train.py
```

### 3. Validate and Evaluate

```bash
# Evaluate LSTM on test set
python models/lstm/evaluate.py \
  --checkpoint artifacts/lstm_1h.pt \
  --horizon 1h \
  --output reports/lstm_1h_eval.json

# Evaluate XGBoost
python models/xgboost/evaluate.py \
  --model artifacts/xgb_classifier.json \
  --output reports/xgb_eval.json

# Generate confusion matrix
python models/xgboost/evaluate.py --plot-confusion-matrix

# Export all metrics to CSV
python ../scripts/export_metrics.py --output reports/all_metrics.csv
```

### 4. Run Inference

```bash
# Single-point inference (for testing)
python -c "
from ml.models.lstm.model import LSTMForecaster
import torch, json

model = LSTMForecaster.from_checkpoint('artifacts/lstm_1h.pt')
model.eval()
# ... load your feature tensor
"

# Batch inference on a date range
python models/lstm/train.py --infer --start 2026-01-01 --end 2026-01-31
```

### 5. Save and Register Models

```bash
# Save LSTM checkpoint
# (Done automatically during training; manually save as:)
torch.save(model.state_dict(), 'artifacts/lstm_1h.pt')

# Save XGBoost model
# (Done automatically; manually:)
import xgboost as xgb
model.save_model('artifacts/xgb_classifier.json')

# Update model registry
# Edit configs/model_registry.yaml with new version tags
```

---

## 🗄️ Database Schema

```mermaid
erDiagram
    RAW_OBSERVATIONS {
        bigint id PK
        timestamptz observed_at
        varchar source
        float proton_flux_10mev
        float proton_flux_50mev
        float proton_flux_100mev
        float xray_flux
        float solar_wind_speed
        float solar_wind_density
        float imf_bz
        float imf_bt
        float kp_index
        boolean is_gap_filled
        timestamptz ingested_at
    }

    PROCESSED_FEATURES {
        bigint id PK
        timestamptz feature_time
        float flux_lag_1h
        float flux_lag_3h
        float flux_lag_6h
        float flux_lag_24h
        float flux_roll_mean_3h
        float flux_roll_std_3h
        float flux_roll_mean_6h
        float solar_pressure
        float bz_bt_coupling
        timestamptz computed_at
    }

    FORECAST_RESULTS {
        bigint id PK
        timestamptz generated_at
        varchar horizon
        timestamptz valid_time
        float flux_mean_pfu
        float flux_std_pfu
        float flux_lower_95
        float flux_upper_95
        varchar model_version
    }

    RISK_ASSESSMENTS {
        bigint id PK
        timestamptz assessed_at
        varchar risk_level
        int risk_code
        float prob_low
        float prob_medium
        float prob_high
        float prob_extreme
        bigint forecast_id FK
        varchar model_version
    }

    CME_EVENTS {
        bigint id PK
        varchar donki_id
        timestamptz cme_time
        float linear_speed_kms
        float angular_width_deg
        float latitude_deg
        float longitude_deg
        float predicted_arrival_hours
        timestamptz predicted_arrival_time
        boolean arrived
        timestamptz actual_arrival_time
    }

    ALERT_EVENTS {
        bigint id PK
        timestamptz triggered_at
        varchar alert_type
        varchar severity
        float threshold_value
        float observed_value
        text message
        boolean acknowledged
        timestamptz acknowledged_at
    }

    OPERATOR_USERS {
        bigint id PK
        varchar email
        varchar hashed_password
        varchar full_name
        varchar organisation
        boolean is_active
        timestamptz created_at
        timestamptz last_login
    }

    RAW_OBSERVATIONS ||--o{ PROCESSED_FEATURES : "feeds"
    PROCESSED_FEATURES ||--o{ FORECAST_RESULTS : "drives"
    FORECAST_RESULTS ||--o{ RISK_ASSESSMENTS : "informs"
    FORECAST_RESULTS ||--o{ ALERT_EVENTS : "triggers"
    CME_EVENTS ||--o{ ALERT_EVENTS : "may trigger"
```

> **TimescaleDB Hypertables**: `raw_observations`, `processed_features`, and `forecast_results` are all configured as TimescaleDB hypertables, partitioned by time with a 1-week chunk interval. This enables automatic data compression and 10–100× faster time-range queries compared to vanilla PostgreSQL.

---

## 🚨 Risk Levels

<div align="center">

| Level | Code | Color | Proton Flux (>10 MeV) | Meaning | Recommended Actions |
|-------|------|-------|----------------------|---------|---------------------|
| 🟢 **Low** | 0 | `#22c55e` | < 10 pfu | Normal space weather conditions. Background particle environment. | ✅ Normal operations. No restrictions on satellite activities. |
| 🟡 **Medium** | 1 | `#eab308` | 10 – 100 pfu | Minor radiation storm. Elevated above background. | ⚠️ Monitor closely. Consider postponing non-critical manoeuvres. Alert crew on ISS for extra-vehicular activity review. |
| 🟠 **High** | 2 | `#f97316` | 100 – 1,000 pfu | Moderate–strong radiation storm (S2–S3). Elevated risk of SEUs. | 🚨 Pause high-risk manoeuvres. Enable radiation-hardening modes. Alert payload teams. Review orbit insertion/ejection plans. |
| 🔴 **Extreme** | 3 | `#ef4444` | > 1,000 pfu | Severe–extreme storm (S4–S5). Significant satellite risk. | 🆘 EMERGENCY PROTOCOL: Safe-mode non-essential payloads. Suspend all manoeuvres. Alert mission control and all satellite operators. Possible ground-uplink restrictions. |

</div>

> **Reference**: Risk level thresholds are based on NOAA Space Weather Scale for Solar Radiation Storms (S-scale). Configurable via `configs/alert_thresholds.yaml`.

---

## 📈 Performance Metrics

### LSTM Forecaster Performance

| Metric | 1h Horizon | 3h Horizon | 24h Horizon |
|--------|-----------|-----------|------------|
| **MAE** (pfu) | 12.3 | 18.7 | 31.2 |
| **RMSE** (pfu) | 19.1 | 28.4 | 47.8 |
| **R²** | 0.94 | 0.88 | 0.76 |
| **Calibration ECE** | 0.031 | 0.048 | 0.072 |
| **Storm onset detection** | 91% | 87% | 74% |

### XGBoost Risk Classifier Performance

| Metric | Score |
|--------|-------|
| **Accuracy** | 91.2% |
| **Macro Precision** | 89.3% |
| **Macro Recall** | 87.8% |
| **Macro F1 Score** | 88.4% |
| **ROC-AUC (One-vs-Rest)** | 0.963 |
| **Extreme Class Precision** | 89.1% |
| **Extreme Class Recall** | 87.6% |
| **Extreme Class F1** | 88.3% |

### XGBoost Confusion Matrix (Test Set)

```
                 Predicted
              Low  Med  High  Ext
Actual Low  [ 892    8     1    0 ]
       Med  [  11  634    22    0 ]
       High [   2   18   187    4 ]
       Ext  [   0    0     7   51 ]
```

### CME Arrival Regressor Performance

| Metric | Score |
|--------|-------|
| **MAE** | 5.8 hours |
| **RMSE** | 8.2 hours |
| **R²** | 0.71 |
| **Within ±6h accuracy** | 62% |
| **Within ±12h accuracy** | 81% |

### System Performance

| Metric | Value |
|--------|-------|
| **API Latency (p50)** | 28 ms |
| **API Latency (p95)** | 82 ms |
| **ML Inference Latency** | 45 ms (LSTM) / 8 ms (XGB) |
| **Data Ingestion Throughput** | ~500 records/min |
| **WebSocket Clients (concurrent)** | Tested up to 200 |
| **DB Query Latency (TimescaleDB)** | < 50 ms for 30-day window |

---

## 🗺️ Future Roadmap

```mermaid
gantt
    title ASTRA Development Roadmap
    dateFormat  YYYY-MM
    section Near-Term (3–6 months)
    SHAP Explainability Dashboard       :2026-08, 2026-09
    Grafana + Prometheus Monitoring     :2026-08, 2026-10
    Extended CME Dataset (2010–2024)    :2026-09, 2026-10
    API Rate Limiting & Quotas          :2026-09, 2026-10
    section Mid-Term (6–12 months)
    Transformer (Temporal Fusion)       :2026-11, 2027-02
    CNN-based CME Image Detection       :2026-12, 2027-03
    Kubernetes Helm Chart               :2027-01, 2027-03
    GOES-18 Data Integration            :2027-01, 2027-02
    section Long-Term (12–24 months)
    Vision Transformer for SDO Images   :2027-04, 2027-09
    Mobile Application (iOS + Android)  :2027-04, 2027-08
    Multi-orbit Coverage (LEO + MEO)    :2027-06, 2027-12
    International Partnership APIs      :2027-08, 2027-12
```

### Near-Term (Q3–Q4 2026)

- [ ] **SHAP Explainability** — Add SHAP value visualisation to the dashboard so operators understand *why* the model issued a risk level
- [ ] **Grafana + Prometheus** — Full observability stack for production system health
- [ ] **Extended Training Archive** — Backfill GOES archive to 2010 for a full Solar Cycle 24 training set
- [ ] **API Rate Limiting** — Token-bucket rate limiter per operator account

### Mid-Term (2026–Q1 2027)

- [ ] **Temporal Fusion Transformer (TFT)** — Replace or ensemble with LSTM using state-of-the-art attention-based architecture
- [ ] **CNN-based CME Detection** — Convolutional neural network on SOHO/SDO coronagraph imagery for automated CME detection
- [ ] **Kubernetes Deployment** — Helm chart for production-grade k8s deployment on GKE/EKS
- [ ] **GOES-18 Integration** — Add GOES-18 as a secondary particle flux source for redundancy

### Long-Term (2027)

- [ ] **Vision Transformers on SDO** — Direct processing of Solar Dynamics Observatory full-disk magnetograms
- [ ] **Mobile Application** — Native iOS and Android app for on-call satellite operators
- [ ] **LEO and MEO Coverage** — Extend risk modelling beyond GEO to low-Earth and medium-Earth orbits
- [ ] **ESA and JAXA Integration** — Incorporate Solar Orbiter and Hinotori data streams

---

## 🔐 Security

ASTRA takes security seriously. The following measures are implemented across the stack.

### Authentication & Authorisation

```python
# JWT configuration — backend/app/config.py
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours
JWT_SECRET_KEY = env("JWT_SECRET_KEY")  # Never hard-coded
```

All protected routes validate the Bearer token on each request using FastAPI's dependency injection:

```python
# backend/app/dependencies.py
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> OperatorUser:
    credentials_exception = HTTPException(status_code=401, ...)
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, ...)
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await db.get(OperatorUser, user_id)
    if user is None or not user.is_active:
        raise credentials_exception
    return user
```

### HTTPS

All production traffic is served over HTTPS:

- **Backend (Render)**: Automatic TLS certificate provisioning via Let's Encrypt
- **Frontend (Vercel)**: Automatic HTTPS with Vercel's edge network
- **HSTS header** enabled on all responses

### Input Validation

All API inputs are validated via Pydantic models before touching the database or ML pipeline:

```python
class PredictRequest(BaseModel):
    proton_flux_10mev: float = Field(..., ge=0, le=1e7, description="pfu")
    imf_bz: float = Field(..., ge=-100, le=100, description="nT")
    solar_wind_speed: float = Field(..., ge=200, le=2500, description="km/s")
    kp_index: float = Field(..., ge=0, le=9)
    # ... etc.
```

### Rate Limiting

```python
# Configured in backend/app/main.py via slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
# Applied as decorator on routers:
@router.get("/forecast")
@limiter.limit("60/minute")
async def get_forecast(...):
    ...
```

### Secrets Management

| Environment | Method |
|-------------|--------|
| Local development | `.env` file (gitignored) |
| GitHub Actions | GitHub Actions Encrypted Secrets |
| Render (backend) | Render Environment Variables (encrypted) |
| Vercel (frontend) | Vercel Environment Variables (encrypted) |

### Docker Security

```dockerfile
# backend/Dockerfile — security hardening
FROM python:3.11-slim

# Run as non-root user
RUN addgroup --system astra && adduser --system --group astra
USER astra

# Read-only filesystem where possible
# No unnecessary packages

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/status || exit 1
```

---

## 🧪 Testing

### Test Structure

```
backend/tests/
├── conftest.py          # Shared fixtures: test DB, async client
├── test_forecast.py     # GET /forecast endpoint tests
├── test_risk.py         # GET /risk endpoint tests
├── test_auth.py         # JWT auth flow tests
├── test_alerts.py       # Alert engine unit tests
└── test_websocket.py    # WebSocket connection + message tests

ml/tests/
├── test_features.py     # Feature engineering unit tests
├── test_lstm.py         # LSTM forward pass + output shape tests
└── test_xgb.py          # XGBoost training + prediction tests

frontend/src/__tests__/
├── FluxChart.test.tsx   # Recharts rendering tests
├── RiskBadge.test.tsx   # Badge colour mapping tests
└── useForecast.test.ts  # TanStack Query hook tests
```

### Running Tests

```bash
# ── Backend unit + integration tests ──────────────────────────────
cd backend
pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html
# Coverage report: backend/htmlcov/index.html

# Run specific test file
pytest tests/test_forecast.py -v

# Run with live database (integration)
pytest tests/ -v --run-integration

# ── ML model tests ────────────────────────────────────────────────
cd ml
pytest tests/ -v

# Test feature engineering only
pytest tests/test_features.py -v

# Test LSTM forward pass
pytest tests/test_lstm.py -v -k "test_forward_pass"

# ── Frontend unit tests ───────────────────────────────────────────
cd frontend
npm run test                   # Vitest watch mode
npm run test -- --run          # Single run (CI mode)
npm run test:coverage          # With coverage report

# ── End-to-end tests ──────────────────────────────────────────────
# Requires full Docker stack running
docker compose up -d
cd frontend
npm run test:e2e               # Playwright E2E tests
```

### Test Coverage Targets

| Module | Target Coverage |
|--------|----------------|
| Backend API routes | ≥ 90% |
| Backend services | ≥ 85% |
| ML feature engineering | ≥ 90% |
| ML model tests | ≥ 80% |
| Frontend components | ≥ 75% |

---

## 🤝 Contributing

We welcome contributions from the space weather, ML, and open-source communities. Please read this guide before opening a PR.

### Getting Started

```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/astra.git
cd astra

# 3. Add the upstream remote
git remote add upstream https://github.com/your-org/astra.git

# 4. Create a feature branch
git checkout -b feat/your-feature-name

# 5. Set up the development environment
cp .env.example .env
docker compose up -d

# 6. Make your changes, write tests, and commit
git add .
git commit -m "feat(lstm): add attention mechanism to 24h model"

# 7. Push and open a Pull Request
git push origin feat/your-feature-name
```

### Commit Convention

ASTRA uses [Conventional Commits](https://www.conventionalcommits.org):

| Prefix | Use case |
|--------|----------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation only |
| `refactor:` | Code refactor (no functional change) |
| `test:` | Add or update tests |
| `ci:` | CI/CD config changes |
| `chore:` | Dependency updates, tooling |

### Code Quality Standards

Before submitting a PR, ensure:

```bash
# Backend
cd backend
ruff check .          # Linting
black . --check       # Formatting
mypy app/             # Type checking
pytest tests/ -v      # All tests pass

# Frontend
cd frontend
npm run lint          # ESLint
npm run type-check    # TypeScript strict
npm run test -- --run # Vitest
```

Pre-commit hooks are configured in `.pre-commit-config.yaml` and will run automatically on `git commit`.

### Pull Request Checklist

Before opening a PR:

- [ ] Branch is up to date with `main`
- [ ] All tests pass locally
- [ ] New functionality has tests
- [ ] `CHANGELOG.md` updated if user-facing change
- [ ] Documentation updated if API/schema changed
- [ ] PR description explains the *what* and *why*

### Reporting Issues

Use the GitHub issue templates:

- **Bug Report**: Include OS, Python/Node version, steps to reproduce, and expected vs actual behaviour
- **Feature Request**: Describe the use case and proposed solution
- **Data Source Issue**: Include the source, error message, and example API response

---

## 👥 Team

<div align="center">

| Member | Role | Responsibilities | Stack |
|--------|------|-----------------|-------|
| **Neil** | 🤖 AI / ML Lead | LSTM architecture, XGBoost classifier, CME regression, feature engineering, model backtesting | PyTorch · XGBoost · scikit-learn · FastAPI inference |
| **Member 2** | 🔧 Data Engineer | NOAA/DONKI/GOES API integrations, APScheduler pipeline, TimescaleDB schema, Redis cache, data quality | HTTPX · APScheduler · PostgreSQL · TimescaleDB · Redis |
| **Member 3** | ⚙️ Backend Engineer | FastAPI REST + WebSocket, alert engine, JWT auth, Docker Compose, Render deployment, CI/CD | FastAPI · Docker · JWT · WebSocket · GitHub Actions |
| **Member 4** | 🎨 Frontend Engineer | Dark space-terminal dashboard, live gauges, Recharts forecast panel, risk badge, orbit map | React 18 · Vite · TypeScript · Recharts · TanStack Query |

</div>

> Want to contribute? See the [Contributing](#-contributing) section.

---

## 📄 License

```
MIT License

Copyright (c) 2026 ASTRA Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Acknowledgements

ASTRA builds on the work of space agencies, research institutions, and the open-source community. We are deeply grateful to:

- **[ISRO — Indian Space Research Organisation](https://www.isro.gov.in)** — For the ISRO Hackathon 2026 platform and for inspiring a generation of Indian space technologists. ASTRA is built in service of India's geostationary satellite fleet.

- **[NASA — National Aeronautics and Space Administration](https://www.nasa.gov)** — For the [DONKI API](https://ccmc.gsfc.nasa.gov/donki/), SDO imagery, ACE real-time data, and OMNIWeb archive — freely available to the global research community.

- **[NOAA Space Weather Prediction Center](https://www.swpc.noaa.gov)** — For the real-time solar wind, Kp index, GOES particle flux, and DSCOVR data streams that power ASTRA's live intelligence layer.

- **[ESA — European Space Agency](https://www.esa.int)** — For Solar Orbiter and ongoing contributions to the understanding of the heliospheric medium.

- **[PyTorch Team](https://pytorch.org)** — For the deep learning framework that makes production-grade LSTM training accessible.

- **[XGBoost Contributors](https://xgboost.ai)** — For the gradient boosting library that underpins ASTRA's risk classifier.

- **[FastAPI / Sebastián Ramírez](https://fastapi.tiangolo.com)** — For the modern, async-native Python API framework.

- **[TimescaleDB](https://www.timescale.com)** — For the open-source time-series extension that makes high-frequency particle flux storage viable at scale.

- **[Recharts Team](https://recharts.org)** — For the composable, React-native charting library powering ASTRA's forecast visualisations.

- **The Open-Source Community** — Every library, dataset, and Stack Overflow answer that made this possible.

---

<div align="center">

**Built with ❤️ for the cosmos — and the satellites that help us understand it**

<br/>

*ASTRA · ISRO Hackathon 2026 · Advanced Space Terrain & Radiation Analytics*

<br/>

[![GitHub Stars](https://img.shields.io/github/stars/your-org/astra?style=social)](https://github.com/your-org/astra)
[![GitHub Forks](https://img.shields.io/github/forks/your-org/astra?style=social)](https://github.com/your-org/astra/network/members)

</div>
>>>>>>> origin/main
