-- =============================================================================
-- Run order:
--   1. Ensure TimescaleDB extension is available in your PostgreSQL 16 image.
--      (docker image: timescale/timescaledb:latest-pg16)
--   2. psql -U <user> -d <db> -f astra_schema.sql
-- =============================================================================


-- ---------------------------------------------------------------------------
-- 0. Extension
-- ---------------------------------------------------------------------------

CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;


-- ---------------------------------------------------------------------------
-- 1. raw_observations
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS raw_observations (
    id          BIGSERIAL       NOT NULL,
    source      VARCHAR(64)     NOT NULL,
    observed_at TIMESTAMPTZ     NOT NULL,
    payload     JSONB           NOT NULL,
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    PRIMARY KEY (id, observed_at)
);

SELECT create_hypertable(
    'raw_observations',
    'observed_at',
    chunk_time_interval => INTERVAL '7 days',
    if_not_exists       => TRUE
);

CREATE INDEX IF NOT EXISTS idx_raw_obs_observed_at
    ON raw_observations (observed_at DESC);

CREATE INDEX IF NOT EXISTS idx_raw_obs_source
    ON raw_observations (source, observed_at DESC);

CREATE INDEX IF NOT EXISTS idx_raw_obs_payload_gin
    ON raw_observations USING GIN (payload);

-- Required for ON CONFLICT (source, observed_at) DO NOTHING in fetch_noaa.py
ALTER TABLE raw_observations
    ADD CONSTRAINT uq_raw_obs_source_observed_at UNIQUE (source, observed_at);


-- ---------------------------------------------------------------------------
-- 2. processed_features
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS processed_features (
    id                          BIGSERIAL   NOT NULL,
    observed_at                 TIMESTAMPTZ NOT NULL,

    -- ── Raw feature values ─────────────────────────────────────────────────
    bz_avg                      FLOAT,
    bt_avg                      FLOAT,
    solar_wind_speed            FLOAT,
    solar_wind_density          FLOAT,
    kp_index                    FLOAT,
    proton_flux_10mev           FLOAT,
    proton_flux_100mev          FLOAT,

    -- ── 1-hour lag ─────────────────────────────────────────────────────────
    bz_avg_lag_1h               FLOAT,
    bt_avg_lag_1h               FLOAT,
    solar_wind_speed_lag_1h     FLOAT,
    solar_wind_density_lag_1h   FLOAT,
    kp_index_lag_1h             FLOAT,
    proton_flux_10mev_lag_1h    FLOAT,
    proton_flux_100mev_lag_1h   FLOAT,

    -- ── 3-hour lag ─────────────────────────────────────────────────────────
    bz_avg_lag_3h               FLOAT,
    bt_avg_lag_3h               FLOAT,
    solar_wind_speed_lag_3h     FLOAT,
    solar_wind_density_lag_3h   FLOAT,
    kp_index_lag_3h             FLOAT,
    proton_flux_10mev_lag_3h    FLOAT,
    proton_flux_100mev_lag_3h   FLOAT,

    -- ── 3-hour rolling mean ────────────────────────────────────────────────
    bz_avg_rolling_mean_3h              FLOAT,
    bt_avg_rolling_mean_3h              FLOAT,
    solar_wind_speed_rolling_mean_3h    FLOAT,
    solar_wind_density_rolling_mean_3h  FLOAT,
    kp_index_rolling_mean_3h            FLOAT,
    proton_flux_10mev_rolling_mean_3h   FLOAT,
    proton_flux_100mev_rolling_mean_3h  FLOAT,

    -- ── 3-hour rolling std ─────────────────────────────────────────────────
    bz_avg_rolling_std_3h               FLOAT,
    bt_avg_rolling_std_3h               FLOAT,
    solar_wind_speed_rolling_std_3h     FLOAT,
    solar_wind_density_rolling_std_3h   FLOAT,
    kp_index_rolling_std_3h             FLOAT,
    proton_flux_10mev_rolling_std_3h    FLOAT,
    proton_flux_100mev_rolling_std_3h   FLOAT,

    -- ── 6-hour rolling max ─────────────────────────────────────────────────
    bz_avg_rolling_max_6h               FLOAT,
    bt_avg_rolling_max_6h               FLOAT,
    solar_wind_speed_rolling_max_6h     FLOAT,
    solar_wind_density_rolling_max_6h   FLOAT,
    kp_index_rolling_max_6h             FLOAT,
    proton_flux_10mev_rolling_max_6h    FLOAT,
    proton_flux_100mev_rolling_max_6h   FLOAT,

    -- ── Legacy rolling columns (kept for backward compat) ──────────────────
    bz_avg_roll_3h              FLOAT,
    bt_avg_roll_3h              FLOAT,
    solar_wind_speed_roll_3h    FLOAT,
    solar_wind_density_roll_3h  FLOAT,
    kp_index_roll_3h            FLOAT,
    proton_flux_10mev_roll_3h   FLOAT,
    proton_flux_100mev_roll_3h  FLOAT,

    -- ── Quality flag ───────────────────────────────────────────────────────
    is_interpolated             BOOLEAN     NOT NULL DEFAULT FALSE,

    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (id, observed_at)
);

SELECT create_hypertable(
    'processed_features',
    'observed_at',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists       => TRUE
);

CREATE INDEX IF NOT EXISTS idx_proc_feat_observed_at
    ON processed_features (observed_at DESC);

CREATE INDEX IF NOT EXISTS idx_proc_feat_interpolated
    ON processed_features (is_interpolated, observed_at DESC);

-- Required for ON CONFLICT (observed_at) DO UPDATE in fetch_goes.py + feature_engineering.py
ALTER TABLE processed_features
    ADD CONSTRAINT uq_proc_feat_observed_at UNIQUE (observed_at);


-- ---------------------------------------------------------------------------
-- 3. forecast_results
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS forecast_results (
    id                      BIGSERIAL       NOT NULL PRIMARY KEY,
    forecast_at             TIMESTAMPTZ     NOT NULL,
    horizon                 VARCHAR(8)      NOT NULL,
    proton_flux_forecast    FLOAT,
    risk_level              VARCHAR(16),
    confidence              FLOAT           CHECK (confidence BETWEEN 0.0 AND 1.0),
    model_version           VARCHAR(32),
    created_at              TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_forecast_forecast_at
    ON forecast_results (forecast_at DESC);

CREATE INDEX IF NOT EXISTS idx_forecast_horizon
    ON forecast_results (horizon, forecast_at DESC);

CREATE INDEX IF NOT EXISTS idx_forecast_risk_level
    ON forecast_results (risk_level, forecast_at DESC);


-- ---------------------------------------------------------------------------
-- 4. cme_events
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS cme_events (
    id                  BIGSERIAL       NOT NULL PRIMARY KEY,
    event_id            VARCHAR(64)     NOT NULL UNIQUE,
    start_time          TIMESTAMPTZ     NOT NULL,
    speed               FLOAT,
    half_angle          FLOAT,
    type                VARCHAR(32),
    estimated_arrival   TIMESTAMPTZ,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cme_start_time
    ON cme_events (start_time DESC);

CREATE INDEX IF NOT EXISTS idx_cme_estimated_arrival
    ON cme_events (estimated_arrival DESC);

CREATE INDEX IF NOT EXISTS idx_cme_event_id
    ON cme_events (event_id);


-- ---------------------------------------------------------------------------
-- 5. flare_events
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS flare_events (
    id              BIGSERIAL       NOT NULL PRIMARY KEY,
    event_id        VARCHAR(64)     NOT NULL UNIQUE,
    begin_time      TIMESTAMPTZ     NOT NULL,
    peak_time       TIMESTAMPTZ,
    end_time        TIMESTAMPTZ,
    class_type      VARCHAR(8),
    source_location VARCHAR(16),
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_flare_begin_time
    ON flare_events (begin_time DESC);

CREATE INDEX IF NOT EXISTS idx_flare_class_type
    ON flare_events (class_type, begin_time DESC);


