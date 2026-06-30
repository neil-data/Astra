# ASTRA REST API Reference

The ASTRA backend API exposes REST endpoints for retrieving space weather telemetry, historical logs, risk alerts, and system health status.

Interactive Swagger documentation is available locally at: `http://localhost:8000/docs`.

## Endpoints Summary

### Telemetry & Forecasts
* **`GET /api/v1/forecast/latest`**
  Returns the latest radiation and space weather forecasts.
  * *Response Shape:*
    ```json
    {
      "id": 9,
      "forecast_time": "2026-06-30T10:09:10Z",
      "prediction_horizon_minutes": 1440,
      "predicted_kp_index": null,
      "predicted_proton_flux": null,
      "predicted_solar_storm_probability": 0.73,
      "risk_level": "MEDIUM",
      "confidence_score": 0.42,
      "model_version": "cme_flare_lstm_v1",
      "created_at": "2026-06-30T10:09:10Z"
    }
    ```

* **`GET /api/v1/forecast/summary`**
  Returns simulated or ML-predicted weather forecasts for 60min, 180min, and 1440min horizons.
  * *Response Shape:*
    ```json
    {
      "summary": {
        "60min": {
          "risk_level": "LOW",
          "predicted_kp": 3.0,
          "storm_probability": 0.35,
          "confidence": 0.95,
          "forecast_time": "..."
        },
        ...
      }
    }
    ```

### Historical Data
* **`GET /api/v1/history?limit=50`**
  Pulls raw space weather observations stored in TimescaleDB.
  * *Response Shape:*
    ```json
    {
      "total": 1,
      "observations": [
        {
          "observation_time": "2026-06-28T11:00:00Z",
          "source": "GOES",
          "solar_wind_speed": 520.0,
          "solar_wind_density": 12.5,
          "bz_component": -18.7,
          "bt_total": 22.1,
          "kp_index": 7.2,
          "proton_flux_10mev": 15000.0,
          "proton_flux_50mev": 850.0,
          "proton_flux_100mev": 320.0
        }
      ]
    }
    ```

### Alerts & Shield Status
* **`GET /api/v1/risk/alerts`**
  Returns active geostationary radiation risk warnings.
  * *Response Shape:*
    ```json
    {
      "total": 0,
      "alerts": []
    }
    ```

### System Health
* **`GET /api/v1/status`**
  System information and service uptime.
  * *Response Shape:*
    ```json
    {
      "app_name": "ASTRA",
      "version": "1.0.0",
      "environment": "development",
      "uptime_seconds": 3385,
      "uptime_human": "00:56:25"
    }
    ```

* **`GET /api/v1/health`**
  Database and Cache connectivity status.
  * *Response Shape:*
    ```json
    {
      "status": "healthy",
      "services": {
        "postgres": { "status": "up", "detail": "up" },
        "redis": { "status": "up", "detail": "up" }
      },
      "timestamp": "2026-06-30T11:12:45Z"
    }
    ```

## Live WebSocket Feeds

* **`WS /ws/live`**
  WebSocket protocol handshake. Broadcasts real-time telemetry changes to active console dashboard sessions.
