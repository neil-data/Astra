# Gap detection, null checks, range anomaly detection, and gap filling
# for the processed_features time-series table.

import asyncio
import os
from datetime import datetime, timezone

import asyncpg
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Expected cadence — gaps larger than this are flagged
MAX_GAP_MINUTES = 16

# Gap fill limit — only interpolate gaps shorter than this
MAX_FILL_MINUTES = 120  # 2 hours

BASE_COLS = [
    "bz_avg",
    "bt_avg",
    "solar_wind_speed",
    "solar_wind_density",
    "kp_index",
    "proton_flux_10mev",
    "proton_flux_100mev",
]

NULL_CHECK_COLS = ["bz_avg", "kp_index", "proton_flux_10mev"]


# -----------------------------------------------------------------------------
# check_gaps — find observation gaps larger than 16 min in last N hours
# -----------------------------------------------------------------------------

async def check_gaps(conn: asyncpg.Connection, hours: int = 6) -> list[dict]:
    logger.info(f"check_gaps: scanning last {hours}h for gaps > {MAX_GAP_MINUTES} min")

    rows = await conn.fetch(
        """
        SELECT observed_at
        FROM   processed_features
        WHERE  observed_at >= NOW() - ($1 || ' hours')::INTERVAL
        ORDER  BY observed_at ASC
        """,
        str(hours)
    )

    if len(rows) < 2:
        logger.warning("check_gaps: not enough rows to detect gaps")
        return []

    timestamps = [r["observed_at"] for r in rows]
    gaps = []

    for i in range(1, len(timestamps)):
        delta_minutes = (timestamps[i] - timestamps[i - 1]).total_seconds() / 60
        if delta_minutes > MAX_GAP_MINUTES:
            gap = {
                "start":        timestamps[i - 1].isoformat(),
                "end":          timestamps[i].isoformat(),
                "gap_minutes":  round(delta_minutes, 2),
            }
            gaps.append(gap)
            logger.warning(f"Gap detected: {gap['start']} → {gap['end']} ({gap['gap_minutes']} min)")

    logger.info(f"check_gaps: found {len(gaps)} gap(s)")
    return gaps


# -----------------------------------------------------------------------------
# check_nulls — count nulls in key columns across last 100 rows
# -----------------------------------------------------------------------------

async def check_nulls(conn: asyncpg.Connection) -> dict[str, int]:
    logger.info("check_nulls: checking last 100 rows")

    rows = await conn.fetch(
        f"""
        SELECT {', '.join(NULL_CHECK_COLS)}
        FROM   processed_features
        ORDER  BY observed_at DESC
        LIMIT  100
        """
    )

    df = pd.DataFrame(rows, columns=NULL_CHECK_COLS)
    null_counts = df.isnull().sum().to_dict()

    for col, count in null_counts.items():
        if count > 0:
            logger.warning(f"check_nulls: {col} has {count} nulls in last 100 rows")
        else:
            logger.debug(f"check_nulls: {col} — no nulls")

    return {col: int(count) for col, count in null_counts.items()}


# -----------------------------------------------------------------------------
# check_range_anomalies — validate physical bounds on key columns
# -----------------------------------------------------------------------------

RANGE_RULES = {
    "kp_index":           lambda v: 0 <= v <= 9,
    "proton_flux_10mev":  lambda v: v > 0,
    "solar_wind_speed":   lambda v: 200 <= v <= 900,
}

async def check_range_anomalies(conn: asyncpg.Connection) -> list[dict]:
    logger.info("check_range_anomalies: validating physical bounds")

    cols = ", ".join(["observed_at"] + list(RANGE_RULES.keys()))
    rows = await conn.fetch(
        f"""
        SELECT {cols}
        FROM   processed_features
        WHERE  observed_at >= NOW() - INTERVAL '24 hours'
        ORDER  BY observed_at DESC
        """
    )

    anomalies = []

    for row in rows:
        for col, rule in RANGE_RULES.items():
            value = row[col]
            if value is None:
                continue
            if not rule(value):
                anomaly = {
                    "observed_at": row["observed_at"].isoformat(),
                    "column":      col,
                    "value":       value,
                }
                anomalies.append(anomaly)
                logger.warning(f"Range anomaly: {col}={value} at {anomaly['observed_at']}")

    logger.info(f"check_range_anomalies: found {len(anomalies)} anomalie(s)")
    return anomalies


# -----------------------------------------------------------------------------
# fill_gaps — linear interpolation for gaps under 2 hours
# -----------------------------------------------------------------------------

async def fill_gaps(conn: asyncpg.Connection) -> int:
    logger.info("fill_gaps: fetching last 24h for interpolation")

    rows = await conn.fetch(
        f"""
        SELECT observed_at, {', '.join(BASE_COLS)}
        FROM   processed_features
        WHERE  observed_at >= NOW() - INTERVAL '24 hours'
        ORDER  BY observed_at ASC
        """
    )

    if len(rows) < 2:
        logger.warning("fill_gaps: not enough rows to interpolate")
        return 0

    df = pd.DataFrame(rows, columns=["observed_at", *BASE_COLS])
    df["observed_at"] = pd.to_datetime(df["observed_at"], utc=True)
    df = df.set_index("observed_at")

    # Build a 1-min resolution index to detect and fill gaps
    full_index = pd.date_range(
        start=df.index.min(),
        end=df.index.max(),
        freq="15min",
        tz="UTC"
    )

    df_reindexed = df.reindex(full_index)
    missing_mask = df_reindexed.isnull().any(axis=1) & ~df.index.isin(df_reindexed.dropna().index)

    # Only fill rows where the surrounding gap is under MAX_FILL_MINUTES
    inserted = 0
    for ts in df_reindexed[missing_mask].index:
        # Find nearest known timestamps before and after
        before = df.index[df.index < ts]
        after  = df.index[df.index > ts]

        if before.empty or after.empty:
            continue

        gap_minutes = (after[0] - before[-1]).total_seconds() / 60
        if gap_minutes > MAX_FILL_MINUTES:
            logger.debug(f"fill_gaps: skipping {ts} — gap {gap_minutes:.0f} min exceeds limit")
            continue

        # Linear interpolation between nearest neighbours
        t0, t1   = before[-1], after[0]
        row0     = df.loc[t0]
        row1     = df.loc[t1]
        alpha    = (ts - t0).total_seconds() / (t1 - t0).total_seconds()
        interp   = {col: row0[col] + alpha * (row1[col] - row0[col])
                    for col in BASE_COLS
                    if pd.notna(row0[col]) and pd.notna(row1[col])}

        if not interp:
            continue

        cols_sql   = ", ".join(interp.keys())
        placeholders = ", ".join(f"${i+2}" for i in range(len(interp)))
        values     = [ts] + list(interp.values())

        await conn.execute(
            f"""
            INSERT INTO processed_features (observed_at, {cols_sql}, is_interpolated)
            VALUES ($1, {placeholders}, TRUE)
            ON CONFLICT (observed_at) DO NOTHING
            """,
            *values
        )
        inserted += 1
        logger.debug(f"fill_gaps: interpolated row at {ts}")

    logger.success(f"fill_gaps: inserted {inserted} interpolated rows")
    return inserted


# -----------------------------------------------------------------------------
# run_all_checks — orchestrate all checks and return summary
# -----------------------------------------------------------------------------

async def run_all_checks(conn: asyncpg.Connection) -> dict:
    logger.info("run_all_checks: starting full data quality pass")

    gaps       = await check_gaps(conn)
    nulls      = await check_nulls(conn)
    anomalies  = await check_range_anomalies(conn)
    filled     = await fill_gaps(conn)

    summary = {
        "gaps_detected":      len(gaps),
        "gaps":               gaps,
        "null_counts":        nulls,
        "anomalies_detected": len(anomalies),
        "anomalies":          anomalies,
        "rows_interpolated":  filled,
    }

    logger.info(
        f"run_all_checks complete — "
        f"gaps: {summary['gaps_detected']} | "
        f"anomalies: {summary['anomalies_detected']} | "
        f"interpolated: {summary['rows_interpolated']}"
    )

    return summary


# -----------------------------------------------------------------------------
# Standalone entry point
# -----------------------------------------------------------------------------

async def main():
    logger.info("ASTRA · data_quality.py starting")
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        summary = await run_all_checks(conn)
        logger.info(f"Summary: {summary}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())