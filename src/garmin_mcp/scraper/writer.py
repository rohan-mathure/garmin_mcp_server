"""Upsert writers for TimescaleDB tables."""

import logging
import os
from datetime import datetime

import psycopg2
from psycopg2.extras import execute_values

logger = logging.getLogger(__name__)


def _get_conn() -> psycopg2.extensions.connection:
    """Open TimescaleDB connection."""
    return psycopg2.connect(os.environ["TIMESCALE_URL"])


def upsert_daily(row: dict) -> None:
    """Insert or replace a daily_metrics row."""
    with _get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO daily_metrics
                (date, steps, calories_active, calories_bmr, distance_meters,
                 resting_hr, min_hr, max_hr, avg_stress,
                 sleep_score, sleep_duration_seconds, spo2_avg)
                VALUES
                (%(date)s, %(steps)s, %(calories_active)s, %(calories_bmr)s,
                 %(distance_meters)s, %(resting_hr)s, %(min_hr)s, %(max_hr)s,
                 %(avg_stress)s, %(sleep_score)s, %(sleep_duration_seconds)s, %(spo2_avg)s)
                ON CONFLICT (date) DO UPDATE SET
                    steps = EXCLUDED.steps,
                    calories_active = EXCLUDED.calories_active,
                    calories_bmr = EXCLUDED.calories_bmr,
                    distance_meters = EXCLUDED.distance_meters,
                    resting_hr = EXCLUDED.resting_hr,
                    min_hr = EXCLUDED.min_hr,
                    max_hr = EXCLUDED.max_hr,
                    avg_stress = EXCLUDED.avg_stress,
                    sleep_score = EXCLUDED.sleep_score,
                    sleep_duration_seconds = EXCLUDED.sleep_duration_seconds,
                    spo2_avg = EXCLUDED.spo2_avg,
                    scraped_at = NOW()
                """,
                row,
            )
        conn.commit()


def upsert_body(row: dict) -> None:
    """Insert or replace a body_metrics row."""
    with _get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO body_metrics
                (date, weight_kg, body_fat_pct, hrv_weekly_avg, vo2max, training_readiness_score)
                VALUES
                (%(date)s, %(weight_kg)s, %(body_fat_pct)s, %(hrv_weekly_avg)s, %(vo2max)s, %(training_readiness_score)s)
                ON CONFLICT (date) DO UPDATE SET
                    weight_kg = EXCLUDED.weight_kg,
                    body_fat_pct = EXCLUDED.body_fat_pct,
                    hrv_weekly_avg = EXCLUDED.hrv_weekly_avg,
                    vo2max = EXCLUDED.vo2max,
                    training_readiness_score = EXCLUDED.training_readiness_score,
                    scraped_at = NOW()
                """,
                row,
            )
        conn.commit()


def upsert_activity(row: dict) -> None:
    """Insert or replace an activities row."""
    with _get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO activities
                (activity_id, start_time, activity_type, name, duration_seconds, distance_meters,
                 avg_hr, max_hr, avg_pace_seconds_per_km, elevation_gain_meters, calories, avg_power)
                VALUES
                (%(activity_id)s, %(start_time)s, %(activity_type)s, %(name)s, %(duration_seconds)s, %(distance_meters)s,
                 %(avg_hr)s, %(max_hr)s, %(avg_pace_seconds_per_km)s, %(elevation_gain_meters)s, %(calories)s, %(avg_power)s)
                ON CONFLICT (activity_id, start_time) DO UPDATE SET
                    activity_type = EXCLUDED.activity_type,
                    name = EXCLUDED.name,
                    duration_seconds = EXCLUDED.duration_seconds,
                    distance_meters = EXCLUDED.distance_meters,
                    avg_hr = EXCLUDED.avg_hr,
                    max_hr = EXCLUDED.max_hr,
                    avg_pace_seconds_per_km = EXCLUDED.avg_pace_seconds_per_km,
                    elevation_gain_meters = EXCLUDED.elevation_gain_meters,
                    calories = EXCLUDED.calories,
                    avg_power = EXCLUDED.avg_power,
                    scraped_at = NOW()
                """,
                row,
            )
        conn.commit()
