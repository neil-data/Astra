import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from config import settings
from database import check_db_connection, engine
from routers.status import router as status_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ASTRA")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("ASTRA starting up...")
    await check_db_connection()
    logger.info("ASTRA started successfully 🚀")
    yield
    logger.info("ASTRA shutting down...")
    await engine.dispose()
    logger.info("ASTRA stopped cleanly 🛑")

app = FastAPI(
    title=settings.app_name,
    description="AI-Based Space Radiation Forecasting System for ISRO Geostationary Satellites",
    version=settings.app_version,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(status_router, prefix="/api/v1", tags=["System"])

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")