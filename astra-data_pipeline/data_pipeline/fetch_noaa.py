# Fetches live solar wind plasma, IMF Bz/Bt, and Kp index from NOAA SWPC
# and inserts raw records into the raw_observations table.

import asyncio
import json
import os
from datetime import datetime, timezone

import asyncpg
import httpx
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

ENDPOINTS = {
    "NOAA_PLASMA":  "https://services.swpc.noaa.gov/products/solar-wind/plasma-7-day.json",
    "NOAA_MAG":     "https://services.swpc.noaa.gov/products/solar-wind/mag-7-day.json",
    "NOAA_KP":      "https://services.swpc.noaa.gov/json/planetary_k_index_1m.json",
}

MAX_RETRIES = 3


# -----------------------------------------------------------------------------
# HTTP fetch with exponential backoff
# -----------------------------------------------------------------------------

async def fetch_with_retry(client: httpx.AsyncClient, url: str) -> list:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"Fetching {url} (attempt {attempt})")
            response = await client.get(url, timeout=30)
            response.raise_for_status()
            logger.success(f"Fetched {url}")
            return response.json()
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            wait = 2 ** attempt
            logger.warning(f"Attempt {attempt} failed for {url}: {e}. Retrying in {wait}s...")
            if attempt == MAX_RETRIES:
                logger.error(f"All {MAX_RETRIES} attempts failed for {url}")
                raise
            await asyncio.sleep(wait)


# -----------------------------------------------------------------------------
# Parsers — each returns a list of (source, observed_at, payload) tuples
# -----------------------------------------------------------------------------

def parse_plasma(data: list) -> list[tuple]:
    # Row format: [time_tag, density, speed, temperature]
    headers = data[0]
    rows = []
    for row in data[1:]:
        record = dict(zip(headers, row))
        try:
            observed_at = datetime.strptime(
                record["time_tag"], "%Y-%m-%d %H:%M:%S.%f"
            ).replace(tzinfo=timezone.utc)
        except ValueError:
            observed_at = datetime.strptime(
                record["time_tag"], "%Y-%m-%d %H:%M:%S"
            ).replace(tzinfo=timezone.utc)
        rows.append(("NOAA_PLASMA", observed_at, record))
    return rows


def parse_mag(data: list) -> list[tuple]:
    # Row format: [time_tag, bx, by, bz, lon, lat, bt]
    headers = data[0]
    rows = []
    for row in data[1:]:
        record = dict(zip(headers, row))
        try:
            observed_at = datetime.strptime(
                record["time_tag"], "%Y-%m-%d %H:%M:%S.%f"
            ).replace(tzinfo=timezone.utc)
        except ValueError:
            observed_at = datetime.strptime(
                record["time_tag"], "%Y-%m-%d %H:%M:%S"
            ).replace(tzinfo=timezone.utc)
        rows.append(("NOAA_MAG", observed_at, record))
    return rows


def parse_kp(data: list) -> list[tuple]:
    # Each item is a dict with time_tag and kp_index
    rows = []
    for item in data:
        observed_at = datetime.strptime(
            item["time_tag"], "%Y-%m-%dT%H:%M:%S"
        ).replace(tzinfo=timezone.utc)
        rows.append(("NOAA_KP", observed_at, item))
    return rows


# -----------------------------------------------------------------------------
# DB insert — upsert on (source, observed_at) to avoid duplicates on re-poll
# -----------------------------------------------------------------------------

async def insert_observations(conn: asyncpg.Connection, rows: list[tuple]) -> int:
    query = """
        INSERT INTO raw_observations (source, observed_at, payload)
        VALUES ($1, $2, $3::jsonb)
        ON CONFLICT (source, observed_at) DO NOTHING
    """
    records = [(source, observed_at, json.dumps(payload)) for source, observed_at, payload in rows]
    await conn.executemany(query, records)
    return len(records)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

async def main():
    logger.info("ASTRA · fetch_noaa.py starting")

    async with httpx.AsyncClient() as client:
        plasma_raw, mag_raw, kp_raw = await asyncio.gather(
            fetch_with_retry(client, ENDPOINTS["NOAA_PLASMA"]),
            fetch_with_retry(client, ENDPOINTS["NOAA_MAG"]),
            fetch_with_retry(client, ENDPOINTS["NOAA_KP"]),
        )

    plasma_rows = parse_plasma(plasma_raw)
    mag_rows    = parse_mag(mag_raw)
    kp_rows     = parse_kp(kp_raw)

    logger.info(f"Parsed → plasma: {len(plasma_rows)} | mag: {len(mag_rows)} | kp: {len(kp_rows)}")

    conn = await asyncpg.connect(DATABASE_URL)
    try:
        inserted = 0
        inserted += await insert_observations(conn, plasma_rows)
        inserted += await insert_observations(conn, mag_rows)
        inserted += await insert_observations(conn, kp_rows)
        logger.success(f"Inserted {inserted} rows into raw_observations")
    finally:
        await conn.close()

    logger.info("fetch_noaa.py complete")


if __name__ == "__main__":
    asyncio.run(main())