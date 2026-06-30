# APScheduler AsyncIOScheduler — orchestrates all data pipeline jobs.
# CMD entry point: python -u scheduler.py

import asyncio
import os

import asyncpg
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from loguru import logger
from redis.asyncio import from_url

import feature_engineering
import fetch_donki
import fetch_goes
import fetch_noaa

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL    = os.getenv("REDIS_URL")


# -----------------------------------------------------------------------------
# Job wrapper — isolates failures so one bad job never kills the scheduler
# -----------------------------------------------------------------------------

async def run_job(name: str, coro) -> None:
    logger.info(f"[{name}] starting")
    try:
        await coro()
        logger.success(f"[{name}] completed successfully")
    except Exception as e:
        logger.error(f"[{name}] failed: {e}")


# -----------------------------------------------------------------------------
# Startup checks — verify DB and Redis before scheduler starts
# -----------------------------------------------------------------------------

async def check_postgres() -> None:
    logger.info("Startup: verifying PostgreSQL connection...")
    conn = await asyncpg.connect(DATABASE_URL)
    version = await conn.fetchval("SELECT version()")
    await conn.close()
    logger.success(f"PostgreSQL OK — {version}")


async def check_redis() -> None:
    logger.info("Startup: verifying Redis connection...")
    async with from_url(REDIS_URL, decode_responses=True) as r:
        pong = await r.ping()
    if not pong:
        raise ConnectionError("Redis ping returned False")
    logger.success("Redis OK — PONG received")


async def verify_connections() -> None:
    await check_postgres()
    await check_redis()


# -----------------------------------------------------------------------------
# Scheduler setup
# -----------------------------------------------------------------------------

def build_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()

    jobs = [
        {
            "name":     "fetch_noaa",
            "coro":     fetch_noaa.main,
            "minutes":  15,
        },
        {
            "name":     "fetch_goes",
            "coro":     fetch_goes.main,
            "minutes":  15,
        },
        {
            "name":     "fetch_donki",
            "coro":     fetch_donki.main,
            "minutes":  60,
        },
        {
            "name":     "feature_engineering",
            "coro":     feature_engineering.main,
            "minutes":  20,
        },
    ]

    for job in jobs:
        scheduler.add_job(
            run_job,
            trigger="interval",
            minutes=job["minutes"],
            args=[job["name"], job["coro"]],
            id=job["name"],
            name=job["name"],
            max_instances=1,          # prevent overlap if job runs long
            misfire_grace_time=60,    # allow up to 60s late start
        )

    return scheduler


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

async def main() -> None:
    logger.info("=" * 60)
    logger.info("ASTRA · Data Pipeline Scheduler starting")
    logger.info("=" * 60)

    # Verify connections before anything starts
    await verify_connections()

    # Build and start scheduler
    scheduler = build_scheduler()
    scheduler.start()

    # Log all registered jobs
    logger.info("Registered jobs:")
    for job in scheduler.get_jobs():
        logger.info(f"  ▸ {job.id:<25} every {job.trigger}")

    # Run all jobs immediately on startup so we don't wait for first interval
    logger.info("Running all jobs immediately on startup...")
    await asyncio.gather(
        run_job("fetch_noaa",          fetch_noaa.main),
        run_job("fetch_goes",          fetch_goes.main),
        run_job("fetch_donki",         fetch_donki.main),
        run_job("feature_engineering", feature_engineering.main),
    )
    logger.success("Startup run complete — scheduler is live")

    # Keep event loop alive
    try:
        while True:
            await asyncio.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutdown signal received — stopping scheduler")
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped. Goodbye 🛰️")


if __name__ == "__main__":
    asyncio.run(main())