# astra-backend/routers/forecast.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import SpaceWeatherForecast
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