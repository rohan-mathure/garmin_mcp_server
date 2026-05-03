"""Time-series trend tools — query local TimescaleDB."""

import os

import psycopg2

from garmin_mcp.server import mcp

VALID_METRICS = {
    # daily_metrics
    "steps",
    "calories_active",
    "calories_bmr",
    "distance_meters",
    "resting_hr",
    "min_hr",
    "max_hr",
    "avg_stress",
    "sleep_score",
    "sleep_duration_seconds",
    "spo2_avg",
    # body_metrics
    "weight_kg",
    "body_fat_pct",
    "hrv_weekly_avg",
    "vo2max",
    "training_readiness_score",
}

METRIC_TABLE = {
    **{m: "daily_metrics" for m in [
        "steps", "calories_active", "calories_bmr", "distance_meters",
        "resting_hr", "min_hr", "max_hr", "avg_stress",
        "sleep_score", "sleep_duration_seconds", "spo2_avg",
    ]},
    **{m: "body_metrics" for m in [
        "weight_kg", "body_fat_pct", "hrv_weekly_avg", "vo2max", "training_readiness_score",
    ]},
}


def _get_conn() -> psycopg2.extensions.connection:
    """Get TimescaleDB connection."""
    url = os.environ.get("TIMESCALE_URL")
    if not url:
        raise RuntimeError("TIMESCALE_URL env var not set")
    return psycopg2.connect(url)


@mcp.tool()
def get_metric_trend(metric: str, days: int = 30) -> list[dict]:
    """Time-series for one health metric over last N days.

    Available metrics: steps, calories_active, calories_bmr, distance_meters,
    resting_hr, min_hr, max_hr, avg_stress, sleep_score, sleep_duration_seconds,
    spo2_avg, weight_kg, body_fat_pct, hrv_weekly_avg, vo2max, training_readiness_score.
    """
    if metric not in VALID_METRICS:
        return [{"error": f"Unknown metric '{metric}'. Valid: {sorted(VALID_METRICS)}"}]

    table = METRIC_TABLE[metric]

    try:
        with _get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT date, {metric}
                    FROM {table}
                    WHERE date >= NOW() - INTERVAL %s
                      AND {metric} IS NOT NULL
                    ORDER BY date
                    """,
                    (f"{days} days",),
                )
                return [{"date": str(r[0]), "value": r[1]} for r in cur.fetchall()]
    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool()
def query_health_db(sql: str) -> list[dict]:
    """Read-only SQL (SELECT/WITH only) against local TimescaleDB.

    Tables: daily_metrics, body_metrics, activities.
    TimescaleDB functions: time_bucket(), first(), last().
    """
    stripped = sql.strip().upper()
    if not (stripped.startswith("SELECT") or stripped.startswith("WITH")):
        return [{"error": "Only SELECT/WITH queries allowed."}]

    try:
        with _get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                cols = [d[0] for d in cur.description]
                return [dict(zip(cols, row)) for row in cur.fetchall()]
    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool()
def get_health_summary(days: int = 30) -> dict:
    """Aggregated health stats across all metrics for the last N days."""
    try:
        with _get_conn() as conn:
            with conn.cursor() as cur:
                # Daily stats
                cur.execute(
                    """
                    SELECT
                        ROUND(AVG(steps)) as avg_steps,
                        MAX(steps) as max_steps,
                        ROUND(AVG(resting_hr)) as avg_resting_hr,
                        ROUND(AVG(sleep_duration_seconds)/3600.0, 1) as avg_sleep_hours,
                        ROUND(AVG(avg_stress)) as avg_stress,
                        ROUND(AVG(spo2_avg), 1) as avg_spo2,
                        COUNT(*) as days_with_data
                    FROM daily_metrics
                    WHERE date >= NOW() - INTERVAL %s
                    """,
                    (f"{days} days",),
                )
                daily_row = cur.fetchone()
                daily = dict(
                    zip([
                        "avg_steps", "max_steps", "avg_resting_hr", "avg_sleep_hours",
                        "avg_stress", "avg_spo2", "days_with_data"
                    ], daily_row)
                ) if daily_row else {}

                # Body stats
                cur.execute(
                    """
                    SELECT
                        ROUND(AVG(weight_kg), 1) as avg_weight_kg,
                        ROUND(AVG(vo2max), 1) as avg_vo2max,
                        ROUND(AVG(hrv_weekly_avg), 1) as avg_hrv,
                        ROUND(AVG(training_readiness_score)) as avg_readiness
                    FROM body_metrics
                    WHERE date >= NOW() - INTERVAL %s
                    """,
                    (f"{days} days",),
                )
                body_row = cur.fetchone()
                body = dict(
                    zip([
                        "avg_weight_kg", "avg_vo2max", "avg_hrv", "avg_readiness"
                    ], body_row)
                ) if body_row else {}

                # Activities
                cur.execute(
                    """
                    SELECT
                        COUNT(*) as total_activities,
                        ROUND(SUM(distance_meters)/1000.0, 1) as total_km,
                        ROUND(AVG(avg_hr)) as avg_activity_hr,
                        COUNT(DISTINCT activity_type) as activity_types
                    FROM activities
                    WHERE start_time >= NOW() - INTERVAL %s
                    """,
                    (f"{days} days",),
                )
                acts_row = cur.fetchone()
                acts = dict(
                    zip([
                        "total_activities", "total_km", "avg_activity_hr", "activity_types"
                    ], acts_row)
                ) if acts_row else {}

                return {
                    "period_days": days,
                    "daily": daily,
                    "body": body,
                    "activities": acts,
                }
    except Exception as e:
        return {"error": str(e)}
