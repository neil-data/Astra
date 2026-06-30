# astra-backend/websocket.py

import asyncio
import logging
from datetime import datetime

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import async_session
from models import SpaceWeatherForecast

logger = logging.getLogger(__name__)


# ── Connection Manager ────────────────────────────────────────────────────────

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("Client connected. Active: %s", len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info("Client disconnected. Active: %s", len(self.active_connections))

    async def broadcast(self, payload: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(payload)
            except Exception:
                pass


manager = ConnectionManager()


# ── Risk Helper ───────────────────────────────────────────────────────────────

def calculate_risk_level(kp_index: float, proton_flux: float) -> str:
    score = 0
    if kp_index >= 8:      score += 2
    elif kp_index >= 6:    score += 1
    if proton_flux >= 100000: score += 2
    elif proton_flux >= 10000: score += 1
    if score >= 4: return "EXTREME"
    if score >= 2: return "HIGH"
    if score >= 1: return "MEDIUM"
    return "LOW"


# ── DB Helper ─────────────────────────────────────────────────────────────────

async def get_latest_forecast():
    async with async_session() as db:
        result = await db.execute(
            select(SpaceWeatherForecast)
            .order_by(SpaceWeatherForecast.forecast_time.desc())
            .limit(1)
        )
        return result.scalars().first()


# ── WebSocket Endpoint ────────────────────────────────────────────────────────

async def live_websocket(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            forecast = await get_latest_forecast()

            if forecast:
                risk_level = calculate_risk_level(
                    forecast.predicted_kp_index or 0,
                    forecast.predicted_proton_flux or 0
                )
                payload = {
                    "risk_level":  risk_level,
                    "kp_index":    forecast.predicted_kp_index,
                    "proton_flux": forecast.predicted_proton_flux,
                    "timestamp":   forecast.forecast_time.isoformat()
                }
            else:
                payload = {
                    "risk_level":  "LOW",
                    "kp_index":    None,
                    "proton_flux": None,
                    "timestamp":   datetime.utcnow().isoformat(),
                    "message":     "No forecast data yet"
                }

            await websocket.send_json(payload)
            await asyncio.sleep(30)

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
        manager.disconnect(websocket)

    except Exception as e:
        logger.exception("WebSocket error: %s", str(e))
        manager.disconnect(websocket)
        try:
            await websocket.close()
        except Exception:
            pass