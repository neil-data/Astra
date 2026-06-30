import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from config import settings
from database import check_db_connection, engine

# Routers
from routers.status import router as status_router
from routers.forecast import router as forecast_router
from routers.history import router as history_router
from routers.risk import router as risk_router

# WebSocket
from websocket import live_websocket


# =====================================================
# Logging
# =====================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ASTRA")


# =====================================================
# Application Lifespan
# =====================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events.
    """

    logger.info("ASTRA starting up...")

    await check_db_connection()

    logger.info("ASTRA started successfully 🚀")

    yield

    logger.info("ASTRA shutting down...")

    await engine.dispose()

    logger.info("ASTRA stopped cleanly 🛑")


# =====================================================
# FastAPI Application
# =====================================================

app = FastAPI(
    title=settings.app_name,
    description=(
        "AI-Based Space Radiation Forecasting System "
        "for ISRO Geostationary Satellites"
    ),
    version=settings.app_version,
    lifespan=lifespan,
)


# =====================================================
# CORS Middleware
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Development Mode
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================
# API Routers
# =====================================================

app.include_router(
    status_router,
    prefix="/api/v1",
    tags=["System"],
)

app.include_router(
    forecast_router,
    prefix="/api/v1",
)

app.include_router(
    history_router,
    prefix="/api/v1",
)

app.include_router(
    risk_router,
    prefix="/api/v1",
)


# =====================================================
# WebSocket Route
# =====================================================

@app.websocket("/ws/live")
async def websocket_live(
    websocket: WebSocket,
):
    """
    Real-time risk stream.
    """

    await live_websocket(
        websocket
    )


# =====================================================
# Root Redirect
# =====================================================

@app.get(
    "/",
    include_in_schema=False,
)
async def root():
    """
    Redirect root to Swagger UI.
    """

    return RedirectResponse(
        url="/docs"
    )