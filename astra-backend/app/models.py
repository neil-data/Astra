# astra-backend/models.py

from sqlalchemy import (
    Column, Integer, BigInteger, String, Float, Text,
    Boolean, DateTime, ForeignKey, JSON, func
)
from sqlalchemy.orm import relationship
from database import Base  # ← use Base from database.py, not redefined here


# 1. RAW SPACE WEATHER OBSERVATIONS
class RawSpaceWeatherObservation(Base):
    __tablename__ = "raw_space_weather_observations"

    id               = Column(BigInteger, primary_key=True, autoincrement=True)
    source           = Column(String(100), nullable=False)  # NOAA / DONKI / GOES / DSCOVR
    observation_time = Column(DateTime, nullable=False, index=True)

    # Solar wind
    solar_wind_speed   = Column(Float)
    solar_wind_density = Column(Float)

    # IMF components
    bz_component = Column(Float)  # Bz GSM
    bt_total     = Column(Float)  # IMF total field

    # Geomagnetic indices
    kp_index = Column(Float)
    ap_index = Column(Float)

    # GOES-16 proton flux (MeV channels)
    proton_flux_10mev  = Column(Float)  # >10 MeV
    proton_flux_50mev  = Column(Float)  # >50 MeV
    proton_flux_100mev = Column(Float)  # >100 MeV

    # Storm/flare metadata
    geomagnetic_storm_level = Column(String(50))
    raw_payload             = Column(JSON)  # full API response stored

    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    features = relationship(
        "ProcessedSpaceWeatherFeature",
        back_populates="observation",
        lazy="selectin"
    )


# 2. PROCESSED FEATURES
class ProcessedSpaceWeatherFeature(Base):
    __tablename__ = "processed_space_weather_features"

    id             = Column(BigInteger, primary_key=True, autoincrement=True)
    observation_id = Column(BigInteger, ForeignKey("raw_space_weather_observations.id"), nullable=False)

    time_window_start = Column(DateTime)
    time_window_end   = Column(DateTime)

    feature_vector         = Column(JSON, nullable=False)  # full lag/rolling feature dict
    solar_activity_score   = Column(Float)
    geomagnetic_risk_score = Column(Float)
    flare_probability      = Column(Float)
    is_normalized          = Column(Boolean, default=False)

    created_at = Column(DateTime, server_default=func.now())

    observation = relationship(
        "RawSpaceWeatherObservation",
        back_populates="features",
        lazy="selectin"
    )
    forecasts = relationship(
        "SpaceWeatherForecast",
        back_populates="feature",
        lazy="selectin"
    )


# 3. FORECAST RESULTS
class SpaceWeatherForecast(Base):
    __tablename__ = "space_weather_forecasts"

    id         = Column(BigInteger, primary_key=True, autoincrement=True)
    feature_id = Column(BigInteger, ForeignKey("processed_space_weather_features.id"), nullable=False)

    forecast_time                   = Column(DateTime, nullable=False, index=True)
    prediction_horizon_minutes      = Column(Integer, nullable=False)  # 60 / 180 / 1440

    predicted_kp_index              = Column(Float)
    predicted_proton_flux           = Column(Float)
    predicted_solar_storm_probability = Column(Float)

    risk_level       = Column(String(20), nullable=False)  # LOW / MEDIUM / HIGH / EXTREME
    confidence_score = Column(Float)
    model_version    = Column(String(50))

    created_at = Column(DateTime, server_default=func.now())

    feature = relationship(
        "ProcessedSpaceWeatherFeature",
        back_populates="forecasts",
        lazy="selectin"
    )
    alerts = relationship(
        "SpaceWeatherAlert",
        back_populates="forecast",
        lazy="selectin"
    )


# 4. ALERTS
class SpaceWeatherAlert(Base):
    __tablename__ = "space_weather_alerts"

    id          = Column(BigInteger, primary_key=True, autoincrement=True)
    forecast_id = Column(BigInteger, ForeignKey("space_weather_forecasts.id"), nullable=False)

    alert_level = Column(String(20), nullable=False)   # HIGH / EXTREME
    alert_type  = Column(String(100))                  # PROTON_FLUX / CME_ARRIVAL / KP_SPIKE
    message     = Column(Text, nullable=False)

    is_active   = Column(Boolean, default=True)

    triggered_at = Column(DateTime, server_default=func.now())
    resolved_at  = Column(DateTime, nullable=True)

    forecast = relationship(
        "SpaceWeatherForecast",
        back_populates="alerts",
        lazy="selectin"
    )