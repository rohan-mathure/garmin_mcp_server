-- TimescaleDB hypertables for Garmin health metrics

CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Daily health metrics — hypertable partitioned by date
CREATE TABLE IF NOT EXISTS daily_metrics (
    date                    DATE NOT NULL,
    steps                   INTEGER,
    calories_active         INTEGER,
    calories_bmr            INTEGER,
    distance_meters         REAL,
    resting_hr              INTEGER,
    min_hr                  INTEGER,
    max_hr                  INTEGER,
    avg_stress              INTEGER,
    sleep_score             INTEGER,
    sleep_duration_seconds  INTEGER,
    spo2_avg                REAL,
    scraped_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (date)
);
SELECT create_hypertable('daily_metrics', 'date', if_not_exists => TRUE);

-- Body composition — hypertable by date
CREATE TABLE IF NOT EXISTS body_metrics (
    date                        DATE NOT NULL,
    weight_kg                   REAL,
    body_fat_pct                REAL,
    hrv_weekly_avg              REAL,
    vo2max                      REAL,
    training_readiness_score    INTEGER,
    scraped_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (date)
);
SELECT create_hypertable('body_metrics', 'date', if_not_exists => TRUE);

-- Activity summaries — hypertable by start_time
CREATE TABLE IF NOT EXISTS activities (
    activity_id                 BIGINT NOT NULL,
    start_time                  TIMESTAMPTZ NOT NULL,
    activity_type               TEXT,
    name                        TEXT,
    duration_seconds            REAL,
    distance_meters             REAL,
    avg_hr                      INTEGER,
    max_hr                      INTEGER,
    avg_pace_seconds_per_km     REAL,
    elevation_gain_meters       REAL,
    calories                    INTEGER,
    avg_power                   REAL,
    scraped_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (activity_id, start_time)
);
SELECT create_hypertable('activities', 'start_time', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_activities_type ON activities(activity_type, start_time DESC);
