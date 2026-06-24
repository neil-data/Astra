from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
import time
import redis.asyncio as aioredis

from database import get_db
from config import settings

router = APIRouter()

APP_START_TIME = time.time()

async def check_postgres(db: AsyncSession):
    try:
        await db.execute(text("SELECT 1"))
        return True, "up"
    except Exception as e:
        return False, str(e)

async def check_redis():
    try:
        client = aioredis.from_url(settings.redis_url, decode_responses=True)
        await client.ping()
        await client.aclose()
        return True, "up"
    except Exception as e:
        return False, str(e)

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    pg_ok, pg_msg = await check_postgres(db)
    redis_ok, redis_msg = await check_redis()
    overall = "healthy" if pg_ok and redis_ok else "degraded"
    return {
        "status": overall,
        "services": {
            "postgres": {"status": "up" if pg_ok else "down", "detail": pg_msg},
            "redis": {"status": "up" if redis_ok else "down", "detail": redis_msg}
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/status")
async def system_status():
    uptime = int(time.time() - APP_START_TIME)
    hours, remainder = divmod(uptime, 3600)
    minutes, seconds = divmod(remainder, 60)
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "uptime_seconds": uptime,
        "uptime_human": f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    }