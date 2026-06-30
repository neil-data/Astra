-- ASTRA data_pipeline schema
-- Reconstructed: raw_observations, cme_events, processed_features
-- These are separate from astra-backend's own tables (raw_space_weather_observations,
-- space_weather_forecasts, etc.) since the data_pipeline service was built independently.

-- 1. Raw observations from NOAA SWPC, GOES-16, NASA DONKI
CREATE TABLE IF NOT EXISTS raw_observations (
    id           BIGSERIAL PRIMARY KEY,
    source       VARCHAR(50) NOT NULL,
    observed_at  TIMESTAMPTZ NOT NULL,
    payload      JSONB NOT NULL,
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (source, observed_at)
);

CREATE INDEX IF NOT EXISTS idx_raw_observations_observed_at
    ON raw_observations (observed_at DESC);

CREATE INDEX IF NOT EXISTS idx_raw_observations_source
    ON raw_observations (source);

-- 2. CME events from NASA DONKI
CREATE TABLE IF NOT EXISTS cme_events (
    id                  BIGSERIAL PRIMARY KEY,
    event_id            VARCHAR(100) NOT NULL UNIQUE,
    start_time          TIMESTAMPTZ,
    speed               FLOAT,
    half_angle          FLOAT,
    type                VARCHAR(50),
    estimated_arrival   TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cme_events_start_time
    ON cme_events (start_time DESC);

-- 3. Processed / engineered features (lag windows, rolling stats)
CREATE TABLE IF NOT EXISTS processed_features (
    observed_at          TIMESTAMPTZ PRIMARY KEY,
    bz_avg               FLOAT,
    bt_avg                FLOAT,
    solar_wind_speed     FLOAT,
    solar_wind_density   FLOAT,
    kp_index             FLOAT,
    proton_flux_10mev    FLOAT,
    proton_flux_100mev   FLOAT
);

CREATE INDEX IF NOT EXISTS idx_processed_features_observed_at
    ON processed_features (observed_at DESC);