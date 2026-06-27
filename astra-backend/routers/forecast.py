# astra-backend/routers/forecast.py

from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import SpaceWeatherForecast, ProcessedSpaceWeatherFeature
from schemas import ForecastResponse, ForecastListResponse

router = APIRouter(prefix="/forecast", tags=["Forecast"])

ALLOWED_HORIZONS = [60, 180, 1440]


# ── GET /forecast ─────────────────────────────────────────────────────────────

@router.get("", response_model=ForecastListResponse)
async def get_forecasts(
    horizon: int = Query(default=60, description="Prediction horizon in minutes"),
    limit:   int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    if horizon not in ALLOWED_HORIZONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid horizon. Allowed: {ALLOWED_HORIZONS}"
        )

    result = await db.execute(
        select(SpaceWeatherForecast)
        .where(SpaceWeatherForecast.prediction_horizon_minutes == horizon)
        .order_by(SpaceWeatherForecast.forecast_time.desc())
        .limit(limit)
    )
    forecasts = result.scalars().all()

    return ForecastListResponse(total=len(forecasts), forecasts=forecasts)


# ── GET /forecast/latest ──────────────────────────────────────────────────────

@router.get("/latest", response_model=ForecastResponse)
async def get_latest_forecast(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SpaceWeatherForecast)
        .order_by(SpaceWeatherForecast.forecast_time.desc())
        .limit(1)
    )
    forecast = result.scalars().first()

    if not forecast:
        raise HTTPException(status_code=404, detail="No forecast data found")

    return forecast


# ── GET /forecast/summary ─────────────────────────────────────────────────────

@router.get("/summary")
async def get_forecast_summary(db: AsyncSession = Depends(get_db)):
    summary = {}

    for horizon in ALLOWED_HORIZONS:
        result = await db.execute(
            select(SpaceWeatherForecast)
            .where(SpaceWeatherForecast.prediction_horizon_minutes == horizon)
            .order_by(SpaceWeatherForecast.forecast_time.desc())
            .limit(1)
        )
        forecast = result.scalars().first()
        label = f"{horizon}min"
        summary[label] = {
            "risk_level":        forecast.risk_level if forecast else "N/A",
            "predicted_kp":      forecast.predicted_kp_index if forecast else None,
            "storm_probability": forecast.predicted_solar_storm_probability if forecast else None,
            "confidence":        forecast.confidence_score if forecast else None,
            "forecast_time":     forecast.forecast_time.isoformat() if forecast else None,
        }

    return {"summary": summary}


# ── GET /forecast/{forecast_id} ───────────────────────────────────────────────

@router.get("/{forecast_id}", response_model=ForecastResponse)
async def get_forecast_by_id(
    forecast_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(SpaceWeatherForecast)
        .where(SpaceWeatherForecast.id == forecast_id)
    )
    forecast = result.scalars().first()

    if not forecast:
        raise HTTPException(
            status_code=404,
            detail=f"Forecast '{forecast_id}' not found"
        )

    return forecast


# ── POST /forecast ────────────────────────────────────────────────────────────

@router.post("", status_code=201)
async def create_forecast(
    horizon: int = Query(default=60, description="Prediction horizon: 60 / 180 / 1440"),
    db: AsyncSession = Depends(get_db)
):
    if horizon not in ALLOWED_HORIZONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid horizon. Allowed: {ALLOWED_HORIZONS}"
        )

    result = await db.execute(
        select(ProcessedSpaceWeatherFeature)
        .order_by(ProcessedSpaceWeatherFeature.created_at.desc())
        .limit(1)
    )
    feature = result.scalars().first()

    if not feature:
        raise HTTPException(
            status_code=404,
            detail="No processed features available."
        )

    feature_vector    = feature.feature_vector or {}
    kp_index          = feature_vector.get("kp_index", 2.0)
    storm_probability = feature_vector.get("flare_probability", 0.1)
    confidence        = feature_vector.get("solar_activity_score", 0.75)

    if kp_index >= 8 or storm_probability >= 0.8:
        risk_level = "EXTREME"
    elif kp_index >= 6 or storm_probability >= 0.6:
        risk_level = "HIGH"
    elif kp_index >= 4 or storm_probability >= 0.3:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    forecast = SpaceWeatherForecast(
        feature_id                        = feature.id,
        forecast_time                     = datetime.now(timezone.utc),
        prediction_horizon_minutes        = horizon,
        predicted_kp_index                = kp_index,
        predicted_proton_flux             = feature_vector.get("proton_flux_10mev"),
        predicted_solar_storm_probability = storm_probability,
        risk_level                        = risk_level,
        confidence_score                  = min(max(confidence, 0.0), 1.0),
        model_version                     = "mock-v0.1"
    )

    db.add(forecast)
    await db.commit()
    await db.refresh(forecast)

    return {
        "status":             "success",
        "forecast_id":        forecast.id,
        "risk_level":         risk_level,
        "predicted_kp_index": kp_index,
        "storm_probability":  storm_probability,
        "confidence":         forecast.confidence_score,
        "horizon_minutes":    horizon,
        "forecast_time":      forecast.forecast_time
    }