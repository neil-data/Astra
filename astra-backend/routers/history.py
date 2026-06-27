# astra-backend/routers/history.py

from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from database import get_db
from models import RawSpaceWeatherObservation
from schemas import HistoryResponse, ObservationResponse

router = APIRouter(prefix="/history", tags=["History"])

ALLOWED_SOURCES = ["NOAA", "GOES", "DONKI", "DSCOVR"]


# ── Request Schema ────────────────────────────────────────────────────────────

class ObservationCreate(BaseModel):
    source:                  str
    observation_time:        datetime
    solar_wind_speed:        Optional[float] = None
    solar_wind_density:      Optional[float] = None
    bz_component:            Optional[float] = None
    bt_total:                Optional[float] = None
    kp_index:                Optional[float] = None
    ap_index:                Optional[float] = None
    proton_flux_10mev:       Optional[float] = None
    proton_flux_50mev:       Optional[float] = None
    proton_flux_100mev:      Optional[float] = None
    geomagnetic_storm_level: Optional[str]   = None
    raw_payload:             Optional[dict]  = None


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


# ── POST /history ─────────────────────────────────────────────────────────────

@router.post("", status_code=201)
async def create_observation(
    body: ObservationCreate,
    db: AsyncSession = Depends(get_db)
):
    if body.source.upper() not in ALLOWED_SOURCES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid source. Allowed: {ALLOWED_SOURCES}"
        )

    # check duplicate
    result = await db.execute(
        select(RawSpaceWeatherObservation)
        .where(RawSpaceWeatherObservation.source == body.source.upper())
        .where(RawSpaceWeatherObservation.observation_time == body.observation_time)
    )
    existing = result.scalars().first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Observation already exists."
        )

    observation = RawSpaceWeatherObservation(
        source                  = body.source.upper(),
        observation_time        = body.observation_time,
        solar_wind_speed        = body.solar_wind_speed,
        solar_wind_density      = body.solar_wind_density,
        bz_component            = body.bz_component,
        bt_total                = body.bt_total,
        kp_index                = body.kp_index,
        ap_index                = body.ap_index,
        proton_flux_10mev       = body.proton_flux_10mev,
        proton_flux_50mev       = body.proton_flux_50mev,
        proton_flux_100mev      = body.proton_flux_100mev,
        geomagnetic_storm_level = body.geomagnetic_storm_level,
        raw_payload             = body.raw_payload
    )

    db.add(observation)
    await db.commit()
    await db.refresh(observation)

    return {
        "status":           "success",
        "observation_id":   observation.id,
        "observation_time": observation.observation_time
    }