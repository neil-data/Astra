# astra-backend/schemas.py

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


# ── Enums ─────────────────────────────────────────────────────────────────────

class RiskLevel(str, Enum):
    LOW     = "LOW"
    MEDIUM  = "MEDIUM"
    HIGH    = "HIGH"
    EXTREME = "EXTREME"


class DataSource(str, Enum):
    NOAA   = "NOAA"
    GOES   = "GOES"
    DONKI  = "DONKI"
    DSCOVR = "DSCOVR"


# ── Forecast ──────────────────────────────────────────────────────────────────

class ForecastResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    forecast_id:               int
    forecast_time:             datetime
    prediction_horizon_minutes: int               # 60 / 180 / 1440
    predicted_kp_index:        Optional[float]
    predicted_proton_flux:     Optional[float]
    predicted_storm_probability: Optional[float]
    risk_level:                RiskLevel
    confidence_score:          float = Field(ge=0.0, le=1.0)
    model_version:             Optional[str]
    created_at:                datetime


class ForecastListResponse(BaseModel):
    total:     int
    forecasts: list[ForecastResponse]


# ── History ───────────────────────────────────────────────────────────────────

class ObservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    observation_time:   datetime
    source:             DataSource
    solar_wind_speed:   Optional[float]
    solar_wind_density: Optional[float]
    bz_component:       Optional[float]
    bt_total:           Optional[float]
    kp_index:           Optional[float]
    proton_flux_10mev:  Optional[float]
    proton_flux_50mev:  Optional[float]
    proton_flux_100mev: Optional[float]


class HistoryResponse(BaseModel):
    total:        int
    observations: list[ObservationResponse]


# ── Risk ──────────────────────────────────────────────────────────────────────

class RiskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    current_risk_level:   RiskLevel
    risk_score:           float = Field(ge=0.0, le=1.0)
    contributing_factors: list[str]
    recommended_action:   str
    last_updated:         datetime


# ── Alerts ────────────────────────────────────────────────────────────────────

class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    alert_id:    int
    alert_level: RiskLevel
    alert_type:  str
    message:     str
    triggered_at: datetime
    resolved_at:  Optional[datetime]
    is_active:   bool


class AlertListResponse(BaseModel):
    total:  int
    alerts: list[AlertResponse]