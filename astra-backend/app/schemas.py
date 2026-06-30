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

    id:                                int
    forecast_time:                     datetime
    prediction_horizon_minutes:        int
    predicted_kp_index:                Optional[float] = None
    predicted_proton_flux:             Optional[float] = None
    predicted_solar_storm_probability: Optional[float] = None
    risk_level:                        RiskLevel
    confidence_score:                  float = Field(ge=0.0, le=1.0)
    model_version:                     Optional[str] = None
    created_at:                        datetime


class ForecastListResponse(BaseModel):
    total:     int
    forecasts: list[ForecastResponse]


# ── History ───────────────────────────────────────────────────────────────────

class ObservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    observation_time:   datetime
    source:             DataSource
    solar_wind_speed:   Optional[float] = None
    solar_wind_density: Optional[float] = None
    bz_component:       Optional[float] = None
    bt_total:           Optional[float] = None
    kp_index:           Optional[float] = None
    proton_flux_10mev:  Optional[float] = None
    proton_flux_50mev:  Optional[float] = None
    proton_flux_100mev: Optional[float] = None


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

    id:           int
    alert_level:  RiskLevel
    alert_type:   str
    message:      str
    triggered_at: datetime
    resolved_at:  Optional[datetime] = None
    is_active:    bool


class AlertListResponse(BaseModel):
    total:  int
    alerts: list[AlertResponse]