# Redis async cache layer for hot features and forecast risk results.

import json
import os

import asyncpg
from dotenv import load_dotenv
from loguru import logger
from redis.asyncio import Redis, from_url

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

TTL_FEATURES = 60 * 30   # 30 minutes
TTL_FORECAST = 60 * 20   # 20 minutes

KEY_LATEST_FEATURES  = "astra:latest_features"
KEY_FORECAST_PREFIX  = "astra:forecast"
KEY_PATTERN_ALL      = "astra:*"


# -----------------------------------------------------------------------------
# Connection helper — create a fresh client per call (stateless module design)
# -----------------------------------------------------------------------------

def _client() -> Redis:
    return from_url(REDIS_URL, decode_responses=True)


# -----------------------------------------------------------------------------
# Latest features
# -----------------------------------------------------------------------------

async def set_latest_features(features: dict) -> None:
    async with _client() as r:
        await r.set(KEY_LATEST_FEATURES, json.dumps(features), ex=TTL_FEATURES)
    logger.info(f"Cache SET {KEY_LATEST_FEATURES} (TTL {TTL_FEATURES}s)")


async def get_latest_features() -> dict | None:
    async with _client() as r:
        raw = await r.get(KEY_LATEST_FEATURES)
    if raw is None:
        logger.debug(f"Cache MISS {KEY_LATEST_FEATURES}")
        return None
    logger.debug(f"Cache HIT {KEY_LATEST_FEATURES}")
    return json.loads(raw)


# -----------------------------------------------------------------------------
# Forecast risk cache
# -----------------------------------------------------------------------------

async def set_risk_cache(horizon: str, risk: str, confidence: float) -> None:
    key     = f"{KEY_FORECAST_PREFIX}:{horizon}"
    payload = json.dumps({"horizon": horizon, "risk": risk, "confidence": confidence})
    async with _client() as r:
        await r.set(key, payload, ex=TTL_FORECAST)
    logger.info(f"Cache SET {key} (TTL {TTL_FORECAST}s)")


async def get_risk_cache(horizon: str) -> dict | None:
    key = f"{KEY_FORECAST_PREFIX}:{horizon}"
    async with _client() as r:
        raw = await r.get(key)
    if raw is None:
        logger.debug(f"Cache MISS {key}")
        return None
    logger.debug(f"Cache HIT {key}")
    return json.loads(raw)


# -----------------------------------------------------------------------------
# Invalidate all astra:* keys
# -----------------------------------------------------------------------------

async def invalidate_all() -> int:
    async with _client() as r:
        keys = await r.keys(KEY_PATTERN_ALL)
        if not keys:
            logger.info("invalidate_all: no astra:* keys found")
            return 0
        deleted = await r.delete(*keys)
    logger.info(f"invalidate_all: deleted {deleted} keys")
    return deleted


# -----------------------------------------------------------------------------
# Push latest row from processed_features into Redis
# -----------------------------------------------------------------------------

async def push_latest_features_from_db(db_conn: asyncpg.Connection) -> bool:
    logger.info("Fetching latest row from processed_features")
    row = await db_conn.fetchrow(
        """
        SELECT *
        FROM   processed_features
        ORDER  BY observed_at DESC
        LIMIT  1
        """
    )
    if row is None:
        logger.warning("push_latest_features_from_db: no rows in processed_features")
        return False

    features = {
        k: (v.isoformat() if hasattr(v, "isoformat") else v)
        for k, v in dict(row).items()
    }
    await set_latest_features(features)
    logger.success(f"Pushed features for observed_at={features.get('observed_at')} to Redis")
    return True