"""
fix_feature_id_nullable.py
===========================
One-off migration: makes space_weather_forecasts.feature_id nullable
on the live Render database, matching the updated models.py.

Run once:
    $env:DATABASE_URL = "postgresql+asyncpg://...your external url..."
    python fix_feature_id_nullable.py
"""

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text


async def migrate():
    url = os.environ["DATABASE_URL"]
    engine = create_async_engine(url)
    async with engine.begin() as conn:
        await conn.execute(
            text("ALTER TABLE space_weather_forecasts ALTER COLUMN feature_id DROP NOT NULL;")
        )
    await engine.dispose()
    print("space_weather_forecasts.feature_id is now nullable.")


if __name__ == "__main__":
    asyncio.run(migrate())