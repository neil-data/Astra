# astra-backend/routers/risk.py

from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import SpaceWeatherForecast, SpaceWeatherAlert
from schemas import RiskResponse, AlertListResponse

router = APIRouter(prefix="/risk", tags=["Risk"])

ALLOWED_SOURCES = ["NOAA", "GOES", "DONKI", "DSCOVR"]


# ── Helpers ───────────────────────────────────────────────────────────────────

def calculate_risk_level(kp_index: float, proton_flux: float):
    score   = 0.0
    factors = []

    if kp_index >= 8:
        score += 0.5
        factors.append("Extreme geomagnetic activity")
    elif kp_index >= 6:
        score += 0.35
        factors.append("Elevated geomagnetic activity")
    elif kp_index >= 4:
        score += 0.2
        factors.append("Moderate geomagnetic activity")

    if proton_flux >= 100000:
        score += 0.5
        factors.append("Severe proton radiation")
    elif proton_flux >= 10000:
        score += 0.3
        factors.append("Elevated proton radiation")
    elif proton_flux >= 1000:
        score += 0.15
        factors.append("Moderate proton radiation")

    score = min(score, 1.0)

    if score >= 0.8:   level = "EXTREME"
    elif score >= 0.6: level = "HIGH"
    elif score >= 0.3: level = "MEDIUM"
    else:              level = "LOW"

    return level, score, factors


def get_recommended_action(risk_level: str) -> str:
    return {
        "LOW":     "Normal operations.",
        "MEDIUM":  "Monitor space weather conditions.",
        "HIGH":    "Prepare mitigation procedures and monitor satellite systems.",
        "EXTREME": "Activate emergency protocols and restrict sensitive operations.",
    }[risk_level]


# ── GET /risk/current ─────────────────────────────────────────────────────────

@router.get("/current", response_model=RiskResponse)
async def get_current_risk(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SpaceWeatherForecast)
        .order_by(SpaceWeatherForecast.forecast_time.desc())
        .limit(1)
    )
    forecast = result.scalars().first()

    if not forecast:
        raise HTTPException(status_code=404, detail="No forecast available")

    level, score, factors = calculate_risk_level(
        forecast.predicted_kp_index or 0,
        forecast.predicted_proton_flux or 0
    )

    return RiskResponse(
        current_risk_level=level,
        risk_score=score,
        contributing_factors=factors,
        recommended_action=get_recommended_action(level),
        last_updated=forecast.created_at
    )


# ── GET /risk/history ─────────────────────────────────────────────────────────

@router.get("/history", response_model=list[RiskResponse])
async def get_risk_history(
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(SpaceWeatherForecast)
        .order_by(SpaceWeatherForecast.forecast_time.desc())
        .limit(limit)
    )
    forecasts = result.scalars().all()

    responses = []
    for forecast in forecasts:
        level, score, factors = calculate_risk_level(
            forecast.predicted_kp_index or 0,
            forecast.predicted_proton_flux or 0
        )
        responses.append(RiskResponse(
            current_risk_level=level,
            risk_score=score,
            contributing_factors=factors,
            recommended_action=get_recommended_action(level),
            last_updated=forecast.created_at
        ))

    return responses


# ── GET /risk/alerts ──────────────────────────────────────────────────────────

@router.get("/alerts", response_model=AlertListResponse)
async def get_active_alerts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SpaceWeatherAlert)
        .where(SpaceWeatherAlert.is_active == True)
        .order_by(SpaceWeatherAlert.triggered_at.desc())
    )
    alerts = result.scalars().all()

    return AlertListResponse(total=len(alerts), alerts=alerts)


# ── POST /risk/alerts ─────────────────────────────────────────────────────────

@router.post("/alerts")
async def trigger_alert_engine(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SpaceWeatherForecast)
        .order_by(SpaceWeatherForecast.forecast_time.desc())
        .limit(1)
    )
    latest_forecast = result.scalars().first()

    if not latest_forecast:
        raise HTTPException(status_code=404, detail="No forecast available.")

    result = await db.execute(
        select(SpaceWeatherAlert)
        .where(SpaceWeatherAlert.is_active == True)
        .limit(1)
    )
    active_alert = result.scalars().first()

    risk = latest_forecast.risk_level.upper() if latest_forecast.risk_level else "LOW"

    if risk in ("HIGH", "EXTREME"):
        if active_alert:
            return {"status": "unchanged", "message": "Alert already active."}

        new_alert = SpaceWeatherAlert(
            forecast_id  = latest_forecast.id,
            alert_level  = risk,
            alert_type   = "RADIATION_RISK",
            message      = f"{risk} space weather risk detected.",
            is_active    = True,
            triggered_at = datetime.now(timezone.utc)
        )
        db.add(new_alert)
        await db.commit()

        return {
            "status":        "created",
            "alert_level":   risk,
            "forecast_time": latest_forecast.forecast_time
        }

    if active_alert:
        active_alert.is_active   = False
        active_alert.resolved_at = datetime.now(timezone.utc)
        await db.commit()
        return {"status": "resolved", "message": "Alert resolved successfully."}

    return {"status": "no_action", "message": "No active alerts."}