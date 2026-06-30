# Fetches CME and solar flare data from NASA DONKI API.
# CMEs → cme_events table + raw_observations
# Flares → raw_observations only

import asyncio
import json
import os
from datetime import datetime, timedelta, timezone

import asyncpg
import httpx
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
NASA_API_KEY  = os.getenv("NASA_API_KEY")

BASE_URL    = "https://api.nasa.gov/DONKI"
MAX_RETRIES = 3


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def date_range(days: int = 7) -> tuple[str, str]:
    end   = datetime.now(timezone.utc).date()
    start = end - timedelta(days=days)
    return str(start), str(end)


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%dT%H:%MZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    logger.warning(f"Could not parse datetime: {value}")
    return None


# -----------------------------------------------------------------------------
# HTTP fetch with exponential backoff
# -----------------------------------------------------------------------------

async def fetch_with_retry(client: httpx.AsyncClient, url: str, params: dict) -> list:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"Fetching {url} (attempt {attempt})")
            response = await client.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            logger.success(f"Fetched {len(data)} records from {url}")
            return data if isinstance(data, list) else []
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            wait = 2 ** attempt
            logger.warning(f"Attempt {attempt} failed: {e}. Retrying in {wait}s...")
            if attempt == MAX_RETRIES:
                logger.error(f"All {MAX_RETRIES} attempts failed for {url}")
                raise
            await asyncio.sleep(wait)


# -----------------------------------------------------------------------------
# Insert raw JSON into raw_observations
# -----------------------------------------------------------------------------

async def insert_raw(conn: asyncpg.Connection, source: str, observed_at: datetime, payload: dict) -> None:
    await conn.execute(
        """
        INSERT INTO raw_observations (source, observed_at, payload)
        VALUES ($1, $2, $3::jsonb)
        ON CONFLICT (source, observed_at) DO NOTHING
        """,
        source, observed_at, json.dumps(payload)
    )


# -----------------------------------------------------------------------------
# Parse and insert CME records into cme_events
# -----------------------------------------------------------------------------

async def insert_cme_events(conn: asyncpg.Connection, records: list) -> int:
    inserted = 0
    for item in records:
        event_id = item.get("activityID")
        if not event_id:
            logger.warning("CME record missing activityID — skipping")
            continue

        start_time = parse_dt(item.get("startTime"))
        if not start_time:
            logger.warning(f"CME {event_id} missing startTime — skipping")
            continue

        # Pull first analysis block if present
        analyses  = item.get("cmeAnalyses") or []
        analysis  = analyses[0] if analyses else {}
        speed      = analysis.get("speed")
        half_angle = analysis.get("halfAngle")
        cme_type   = analysis.get("type")

        # Estimated Earth arrival from linkedEvents or analysis
        estimated_arrival = parse_dt(analysis.get("estimatedShockArrivalTime"))

        await conn.execute(
            """
            INSERT INTO cme_events
                (event_id, start_time, speed, half_angle, type, estimated_arrival)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (event_id) DO NOTHING
            """,
            event_id, start_time,
            float(speed) if speed is not None else None,
            float(half_angle) if half_angle is not None else None,
            cme_type,
            estimated_arrival
        )

        # Also store raw payload
        await insert_raw(conn, "NASA_DONKI_CME", start_time, item)
        inserted += 1

    return inserted


# -----------------------------------------------------------------------------
# Insert raw flare records into raw_observations
# -----------------------------------------------------------------------------

async def insert_flare_raws(conn: asyncpg.Connection, records: list) -> int:
    inserted = 0
    for item in records:
        observed_at = parse_dt(item.get("beginTime"))
        if not observed_at:
            logger.warning("Flare record missing beginTime — skipping")
            continue
        await insert_raw(conn, "NASA_DONKI_FLR", observed_at, item)
        inserted += 1
    return inserted


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

async def main():
    logger.info("ASTRA · fetch_donki.py starting")

    start, end = date_range(days=7)
    params = {"startDate": start, "endDate": end, "api_key": NASA_API_KEY}

    async with httpx.AsyncClient() as client:
        cme_data, flare_data = await asyncio.gather(
            fetch_with_retry(client, f"{BASE_URL}/CME", params),
            fetch_with_retry(client, f"{BASE_URL}/FLR", params),
        )

    logger.info(f"Fetched → CMEs: {len(cme_data)} | Flares: {len(flare_data)}")

    conn = await asyncpg.connect(DATABASE_URL)
    try:
        cme_count   = await insert_cme_events(conn, cme_data)
        flare_count = await insert_flare_raws(conn, flare_data)
        logger.success(f"Inserted → cme_events: {cme_count} | flare raw_observations: {flare_count}")
    finally:
        await conn.close()

    logger.info("fetch_donki.py complete")


if __name__ == "__main__":
    asyncio.run(main())