# Reads last 48h from processed_features, computes lag + rolling features,
# upserts results back into processed_features.

import asyncio
import os

import asyncpg
import pandas as pd
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

BASE_COLS = [
    "bz_avg",
    "bt_avg",
    "solar_wind_speed",
    "solar_wind_density",
    "kp_index",
    "proton_flux_10mev",
    "proton_flux_100mev",
]

# 15-min cadence → 1h = 4 periods, 3h = 12, 6h = 24
PERIODS_1H = 4
PERIODS_3H = 12
PERIODS_6H = 24


# -----------------------------------------------------------------------------
# Fetch last 48h from processed_features
# -----------------------------------------------------------------------------

async def fetch_features(conn: asyncpg.Connection) -> pd.DataFrame:
    logger.info("Fetching last 48h from processed_features")
    rows = await conn.fetch(
        """
        SELECT observed_at, bz_avg, bt_avg, solar_wind_speed, solar_wind_density,
               kp_index, proton_flux_10mev, proton_flux_100mev
        FROM   processed_features
        WHERE  observed_at >= NOW() - INTERVAL '48 hours'
        ORDER  BY observed_at ASC
        """
    )
    df = pd.DataFrame(rows, columns=[
        "observed_at", *BASE_COLS
    ])
    df["observed_at"] = pd.to_datetime(df["observed_at"], utc=True)
    df = df.set_index("observed_at").sort_index()
    logger.info(f"Fetched {len(df)} rows")
    return df


# -----------------------------------------------------------------------------
# Compute lag + rolling features
# -----------------------------------------------------------------------------

def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Computing lag and rolling features")

    for col in BASE_COLS:
        if col not in df.columns:
            logger.warning(f"Column {col} missing — skipping")
            continue

        df[f"{col}_lag_1h"]        = df[col].shift(PERIODS_1H)
        df[f"{col}_lag_3h"]        = df[col].shift(PERIODS_3H)
        df[f"{col}_rolling_mean_3h"] = df[col].rolling(PERIODS_3H, min_periods=1).mean()
        df[f"{col}_rolling_std_3h"]  = df[col].rolling(PERIODS_3H, min_periods=1).std()
        df[f"{col}_rolling_max_6h"]  = df[col].rolling(PERIODS_6H, min_periods=1).max()

    logger.info(f"Feature matrix shape: {df.shape}")
    return df


# -----------------------------------------------------------------------------
# Upsert computed features back into processed_features
# -----------------------------------------------------------------------------

async def upsert_features(conn: asyncpg.Connection, df: pd.DataFrame) -> int:
    df = df.reset_index()  # bring observed_at back as column

    # Build dynamic column list — only engineered columns, not base cols
    engineered_cols = [c for c in df.columns if c != "observed_at" and c not in BASE_COLS]

    if not engineered_cols:
        logger.warning("No engineered columns to upsert")
        return 0

    set_clause = ", ".join(
        f"{col} = EXCLUDED.{col}" for col in engineered_cols
    )
    col_list   = ", ".join(engineered_cols)
    placeholders = ", ".join(f"${i+2}" for i in range(len(engineered_cols)))

    query = f"""
        INSERT INTO processed_features (observed_at, {col_list})
        VALUES ($1, {placeholders})
        ON CONFLICT (observed_at)
        DO UPDATE SET {set_clause}
    """

    records = []
    for _, row in df.iterrows():
        values = [row["observed_at"]] + [
            float(row[c]) if pd.notna(row[c]) else None
            for c in engineered_cols
        ]
        records.append(values)

    await conn.executemany(query, records)
    logger.success(f"Upserted {len(records)} rows into processed_features")
    return len(records)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

async def main():
    logger.info("ASTRA · feature_engineering.py starting")

    conn = await asyncpg.connect(DATABASE_URL)
    try:
        df = await fetch_features(conn)

        if df.empty:
            logger.warning("No data in last 48h — skipping feature computation")
            return

        df = compute_features(df)
        await upsert_features(conn, df)

    finally:
        await conn.close()

    logger.info("feature_engineering.py complete")


if __name__ == "__main__":
    asyncio.run(main())