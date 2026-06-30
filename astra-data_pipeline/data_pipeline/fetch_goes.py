# Fetches GOES-16 integral proton and electron flux data from NOAA.
# Raw JSON → raw_observations
# Proton flux (10MeV + 100MeV) → upsert into processed_features

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
    "GOES16_PROTON":   "https://services.swpc.noaa.gov/json/goes/primary/integral-protons-1-day.json",
    "GOES16_ELECTRON": "https://services.swpc.noaa.gov/json/goes/primary/integral-electrons-1-day.json",
}

# GOES proton channel labels → map to our schema columns
PROTON_CHANNEL_MAP = {
    "P2":  "proton_flux_10mev",   # ≥10  MeV channel
    "P7":  "proton_flux_100mev",  # ≥100 MeV channel
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
# Parse timestamp from GOES record
# -----------------------------------------------------------------------------

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
# Parse proton records → group by observed_at, extract 10MeV and 100MeV
# -----------------------------------------------------------------------------

def parse_proton_flux(records: list) -> dict[datetime, dict]:
    """
    Returns { observed_at: { proton_flux_10mev: float, proton_flux_100mev: float } }
    GOES JSON rows have 'energy' field indicating channel e.g. '>=10 MeV'
    """
    grouped: dict[datetime, dict] = {}

    for row in records:
        observed_at = parse_dt(row.get("time_tag"))
        if not observed_at:
            continue

        energy  = row.get("energy", "")
        flux    = row.get("flux")

        if flux is None:
            continue

        try:
            flux = float(flux)
        except (ValueError, TypeError):
            continue

        if observed_at not in grouped:
            grouped[observed_at] = {}

        if ">=10 MeV" in energy or "P2" in energy:
            grouped[observed_at]["proton_flux_10mev"] = flux
        elif ">=100 MeV" in energy or "P7" in energy:
            grouped[observed_at]["proton_flux_100mev"] = flux

    return grouped


# -----------------------------------------------------------------------------
# Upsert proton flux into processed_features
# -----------------------------------------------------------------------------

async def upsert_processed_features(conn: asyncpg.Connection, flux_map: dict[datetime, dict]) -> int:
    upserted = 0
    for observed_at, fluxes in flux_map.items():
        flux_10  = fluxes.get("proton_flux_10mev")
        flux_100 = fluxes.get("proton_flux_100mev")

        if flux_10 is None and flux_100 is None:
            continue

        await conn.execute(
            """
            INSERT INTO processed_features (observed_at, proton_flux_10mev, proton_flux_100mev)
            VALUES ($1, $2, $3)
            ON CONFLICT (observed_at)
            DO UPDATE SET
                proton_flux_10mev  = COALESCE(EXCLUDED.proton_flux_10mev,  processed_features.proton_flux_10mev),
                proton_flux_100mev = COALESCE(EXCLUDED.proton_flux_100mev, processed_features.proton_flux_100mev)
            """,
            observed_at, flux_10, flux_100
        )
        upserted += 1

    return upserted


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

async def main():
    logger.info("ASTRA · fetch_goes.py starting")

    async with httpx.AsyncClient() as client:
        proton_data, electron_data = await asyncio.gather(
            fetch_with_retry(client, ENDPOINTS["GOES16_PROTON"]),
            fetch_with_retry(client, ENDPOINTS["GOES16_ELECTRON"]),
        )

    logger.info(f"Fetched → proton: {len(proton_data)} rows | electron: {len(electron_data)} rows")

    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # ── Raw inserts ───────────────────────────────────────────────────────
        raw_count = 0
        for row in proton_data:
            observed_at = parse_dt(row.get("time_tag"))
            if observed_at:
                await insert_raw(conn, "GOES16_PROTON", observed_at, row)
                raw_count += 1

        for row in electron_data:
            observed_at = parse_dt(row.get("time_tag"))
            if observed_at:
                await insert_raw(conn, "GOES16_ELECTRON", observed_at, row)
                raw_count += 1

        logger.success(f"Inserted {raw_count} rows into raw_observations")

        # ── Processed features upsert ─────────────────────────────────────────
        flux_map  = parse_proton_flux(proton_data)
        upserted  = await upsert_processed_features(conn, flux_map)
        logger.success(f"Upserted {upserted} rows into processed_features")

    finally:
        await conn.close()

    logger.info("fetch_goes.py complete")


if __name__ == "__main__":
    asyncio.run(main())