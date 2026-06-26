# astra-backend/alert_engine.py

import asyncio
import logging
from datetime import datetime

from sqlalchemy import select
from database import async_session
from models import SpaceWeatherForecast, SpaceWeatherAlert

logger = logging.getLogger(__name__)

CHECK_INTERVAL = 300  # 5 minutes

HIGH_RISK_LEVELS = {"HIGH", "EXTREME"}


# ── Helpers ───────────────────────────────────────────────────────────────────

async def get_latest_forecast():
    async with async_session() as db:
        result = await db.execute(
            select(SpaceWeatherForecast)
            .order_by(SpaceWeatherForecast.forecast_time.desc())
            .limit(1)
        )
        return result.scalars().first()


async def get_active_alert():
    async with async_session() as db:
        result = await db.execute(
            select(SpaceWeatherAlert)
            .where(SpaceWeatherAlert.is_active == True)
            .order_by(SpaceWeatherAlert.triggered_at.desc())
            .limit(1)
        )
        return result.scalars().first()


async def create_alert(forecast: SpaceWeatherForecast):
    async with async_session() as db:
        alert = SpaceWeatherAlert(
            forecast_id  = forecast.id,
            alert_level  = forecast.risk_level,
            alert_type   = "RADIATION_RISK",
            message      = (
                f"Radiation risk level {forecast.risk_level} detected. "
                f"Predicted Kp: {forecast.predicted_kp_index}, "
                f"Proton flux: {forecast.predicted_proton_flux}"
            ),
            is_active    = True,
            triggered_at = datetime.utcnow()
        )
        db.add(alert)
        await db.commit()
        logger.warning(
            "Alert created: %s | Kp=%s | Flux=%s",
            forecast.risk_level,
            forecast.predicted_kp_index,
            forecast.predicted_proton_flux
        )


async def resolve_alert(alert: SpaceWeatherAlert):
    async with async_session() as db:
        result = await db.execute(
            select(SpaceWeatherAlert)
            .where(SpaceWeatherAlert.id == alert.id)
        )
        db_alert = result.scalars().first()
        if db_alert:
            db_alert.is_active   = False
            db_alert.resolved_at = datetime.utcnow()
            await db.commit()
            logger.info("Alert resolved: ID %s", alert.id)


# ── Core logic ────────────────────────────────────────────────────────────────

async def process_alerts():
    forecast     = await get_latest_forecast()
    active_alert = await get_active_alert()

    if not forecast:
        logger.info("Alert Engine: no forecast data yet")
        return

    risk = forecast.risk_level

    if risk in HIGH_RISK_LEVELS:
        if not active_alert:
            await create_alert(forecast)
        else:
            logger.info("Alert Engine: alert already active for %s", risk)

    else:
        if active_alert:
            await resolve_alert(active_alert)
        else:
            logger.info("Alert Engine: risk is %s — no action needed", risk)


# ── Background runner ─────────────────────────────────────────────────────────

async def run_alert_engine():
    logger.info("Alert Engine started — checking every %ss", CHECK_INTERVAL)
    while True:
        try:
            await process_alerts()
        except Exception as e:
            logger.exception("Alert Engine error: %s", str(e))
        await asyncio.sleep(CHECK_INTERVAL)