# ASTRA System Architecture

This document describes the high-level architecture of ASTRA (Advanced Space Terrain & Radiation Analytics).

## System Overview

ASTRA is an AI-powered space weather forecasting and radiation analytics platform designed to monitor geomagnetic radiation and forecast risk levels for geostationary satellites.

```
                    ┌─────────────────────────┐
                    │     Space Weather       │
                    │   Monitoring Sensors    │
                    │ (NOAA, GOES, DONKI, etc)│
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │      Data Pipeline      │
                    │   (scheduler, fetches)  │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   Postgres/TimescaleDB  │
                    │      (Storage)          │
                    └──────┬───────────▲──────┘
                           │           │
            ┌──────────────┘           └──────────────┐
            ▼                                         ▼
┌───────────────────────┐                 ┌───────────────────────┐
│     ML Pipeline       │                 │      Backend API      │
│  (CME & Kp forecasts) │                 │   (FastAPI/WebSockets)│
└───────────────────────┘                 └───────────┬───────────┘
                                                      │
                                                      ▼
                                          ┌───────────────────────┐
                                          │     React Frontend    │
                                          │   (Dashboard Console) │
                                          └───────────────────────┘
```

## Service Directory

The system is composed of four principal components:

1. **`astra-backend`**: FastAPI web application that exposes REST endpoints for current telemetry, historical observations, forecast summaries, risk alerts, and system health. It also establishes a live WebSocket server to broadcast real-time updates.
2. **`data_pipeline`**: Background worker script that periodically fetches real-time observations from external NOAA, GOES, and DONKI space weather API resources, validates data quality, and commits them to the database.
3. **`astra_ml_pipeline`**: Contains deep learning models (LSTM) to classify CME events and forecast Kp indexes. It runs a background forecasting loop that periodically generates forecasts from raw observations and writes predictions to the database.
4. **`astra_frontend`**: React and TypeScript Single Page Application (SPA) built using Vite, TanStack Query, Recharts, and GSAP/Lenis for premium, high-performance UI and animations.
