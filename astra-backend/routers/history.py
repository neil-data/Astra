# astra-backend/routers/history.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from database import get_db
from models import RawSpaceWeatherObservation
from schemas import HistoryResponse, ObservationResponse

router = APIRouter(prefix="/history", tags=["History"])

ALLOWED_SOURCES = ["NOAA", "GOES", "DONKI", "DSCOVR"]

# ── GET /history ──────────────────────────────────────────────────────────────

@router.get("", response_model=HistoryResponse)
async def get_history(
    source: Optional[str] = Query(default=None, description="Filter by source: NOAA, GOES, DONKI, DSCOVR"),
    limit:  int = Query(default=20, ge=1, le=100),
    skip:   int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    if source and source.upper() not in ALLOWED_SOURCES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid source. Allowed: {ALLOWED_SOURCES}"
        )

    stmt = select(RawSpaceWeatherObservation).order_by(
        RawSpaceWeatherObservation.observation_time.desc()
    )

    if source:
        stmt = stmt.where(RawSpaceWeatherObservation.source == source.upper())

    stmt = stmt.offset(skip).limit(limit)

    result = await db.execute(stmt)
    observations = result.scalars().all()

    return HistoryResponse(total=len(observations), observations=observations)


# ── GET /history/latest ───────────────────────────────────────────────────────

@router.get("/latest", response_model=ObservationResponse)
async def get_latest_observation(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(RawSpaceWeatherObservation)
        .order_by(RawSpaceWeatherObservation.observation_time.desc())
        .limit(1)
    )
    observation = result.scalars().first()

    if not observation:
        raise HTTPException(status_code=404, detail="No observation data found")

    return observation


# ── GET /history/{observation_id} ─────────────────────────────────────────────

@router.get("/{observation_id}", response_model=ObservationResponse)
async def get_observation_by_id(
    observation_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(RawSpaceWeatherObservation)
        .where(RawSpaceWeatherObservation.id == observation_id)
    )
    observation = result.scalars().first()

    if not observation:
        raise HTTPException(
            status_code=404,
            detail=f"Observation '{observation_id}' not found"
        )

    return observation