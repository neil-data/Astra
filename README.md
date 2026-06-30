# ASTRA — Advanced Space Terrain & Radiation Analytics

ASTRA is an artificial intelligence-powered radiation forecasting and space weather analytics platform designed for geostationary satellites (GEO-STAT) operated by ISRO. The system ingests sensor feeds, runs predictive LSTM sequence networks to evaluate solar wind and Coronal Mass Ejection (CME) risk profiles, classifies radiation alerts, and provides a mission control console. ASTRA was built for the ISRO Bharatiya Antariksh Hackathon 2026.

## Architecture

For a comprehensive layout and topology details, please refer to [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

The platform is built as a microservices-based monorepo consisting of:
* **`astra-backend`**: Core REST API and real-time WebSocket server.
* **`data_pipeline`**: Ingests, cleans, and scales raw sensor feeds from NOAA/GOES.
* **`astra_ml_pipeline`**: Fits and executes LSTM forecasting model networks.
* **`astra_frontend`**: React and TypeScript space weather control dashboard.

## Tech Stack

| Service | Primary Technology |
|---|---|
| **Backend API** | Python, FastAPI, SQLAlchemy, WebSockets, Uvicorn |
| **Storage & Caching** | PostgreSQL (TimescaleDB), Redis |
| **Data Ingestion** | Python, APScheduler, HTTPX |
| **AI/ML Pipeline** | PyTorch, LSTM, Pandas, Scikit-learn, PyArrow |
| **Frontend UI** | React, TypeScript, Vite, TanStack Query, Recharts, GSAP, Lenis |
| **Orchestration** | Docker, Docker Compose |

## Project Structure

```
ASTRA/
├── .github/workflows/ci.yml         # CI Lint & Build Workflows
├── astra-backend/                   # FastAPI Web API
│   ├── app/                         # Backend Application Code
│   │   ├── routers/                 # API Endpoint Handlers
│   │   └── ...
│   ├── Dockerfile
│   └── requirements.txt
├── astra_frontend/                  # React Single Page App
│   ├── src/                         # UI Components & Hooks
│   ├── public/                      # Static Assets
│   └── Dockerfile
├── astra_ml_pipeline/               # PyTorch LSTM ML Pipeline
│   ├── artifacts/                   # Pre-trained Model Weights
│   ├── data/                        # Datasets & Scalers
│   ├── run_forecast.py              # Forecast Inference Loop
│   └── Dockerfile
├── data_pipeline/                   # Background Ingestion Pipeline
│   ├── scheduler.py                 # Scheduled Job Worker
│   └── Dockerfile
├── docs/                            # Design & API Specifications
│   ├── ARCHITECTURE.md
│   └── API.md
├── docker-compose.yml               # Local Development Orchestrator
├── render.yaml                      # Render Infrastructure Blueprint
└── README.md
```

## Local Development Setup

### Prerequisites
* Docker & Docker Compose
* Node.js v18+ & Python 3.11 (if running locally outside containers)

### Step-by-Step Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-org/astra.git
   cd ASTRA
   ```

2. **Setup Environment Variables:**
   Copy the example environment files in each service directory (and at the root level) to `.env`:
   ```bash
   cp .env.example .env
   cp astra-backend/.env.example astra-backend/.env
   cp astra_frontend/.env.example astra_frontend/.env
   cp astra_ml_pipeline/.env.example astra_ml_pipeline/.env
   cp data_pipeline/.env.example data_pipeline/.env
   ```

3. **Orchestrate via Docker Compose:**
   Build and start all services locally:
   ```bash
   docker-compose up --build
   ```

4. **Run ML Training Pipeline (Optional/Manual):**
   If you want to re-train the models locally:
   ```bash
   cd astra_ml_pipeline
   python generate_synthetic_data.py
   python preprocessing.py
   python train.py
   ```

5. **Access the Interfaces:**
   * **Frontend Dashboard:** `http://localhost:3000`
   * **Backend API Docs:** `http://localhost:8000/docs`

## API Reference

Endpoint details can be found in [docs/API.md](docs/API.md). The interactive OpenAPI specification is hosted locally at `http://localhost:8000/docs`.

## Deployment

### Render (Blueprint Deploy)
The repository contains a `render.yaml` configuration defining the Render Blueprint.
1. Connect your GitHub repository to Render.
2. Create a new **Blueprint Route**.
3. Render will deploy the PostgreSQL database, Redis instance, FastAPI server, background workers, and the Nginx frontend in a unified pipeline.

*Note: Since Render's free tier has regional Redis limitations, you can configure Redis using external add-ons (such as Upstash Redis or Redis Enterprise Cloud) and supply the connection string as `REDIS_URL` in the environment variables.*

## Team
* **M1 (AI/ML)**: Model design, LSTM forecast modeling, CME prediction.
* **M2 (Data)**: Ingestion tasks, features pipeline, data quality assertions.
* **M3 (Backend)**: API infrastructure, WebSockets, timeseries schema configurations.
* **M4 (Frontend)**: Real-time telemetry widgets, charts, and control dashboard console.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
