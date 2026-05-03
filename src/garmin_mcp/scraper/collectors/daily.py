"""Collect daily health metrics from Garmin."""

import asyncio
from datetime import date, timedelta

from garminconnect import Garmin


async def collect_daily_for_date(garmin: Garmin, d: str) -> dict:
    """Fetch and normalize daily metrics for a single date (YYYY-MM-DD)."""
    summary = await asyncio.to_thread(garmin.get_user_summary, d)
    hr = await asyncio.to_thread(garmin.get_heart_rates, d)
    sleep = await asyncio.to_thread(garmin.get_sleep_data, d)
    stress = await asyncio.to_thread(garmin.get_stress_data, d)
    spo2 = await asyncio.to_thread(garmin.get_spo2_data, d)

    return {
        "date": d,
        "steps": summary.get("totalSteps"),
        "calories_active": summary.get("activeKilocalories"),
        "calories_bmr": summary.get("bmrKilocalories"),
        "distance_meters": summary.get("totalDistance"),
        "resting_hr": hr.get("lastSevenDaysAvgResting") if hr else None,
        "min_hr": hr.get("minHeartRate") if hr else None,
        "max_hr": hr.get("maxHeartRate") if hr else None,
        "avg_stress": stress.get("avgStress") if stress else None,
        "sleep_score": sleep.get("overallSleep", {}).get("qualityScore") if sleep else None,
        "sleep_duration_seconds": sleep.get("overallSleep", {}).get("totalNumberOfSeconds")
        if sleep
        else None,
        "spo2_avg": spo2.get("currentSpO2") if spo2 else None,
    }


async def collect_daily_range(garmin: Garmin, days: int = 7) -> list[dict]:
    """Collect last N days of daily metrics (idempotent — covers yesterday if today runs early)."""
    today = date.today()
    results = []
    for i in range(days):
        d = (today - timedelta(days=i)).isoformat()
        try:
            row = await collect_daily_for_date(garmin, d)
            results.append(row)
        except Exception as e:
            # Log but don't fail entire collection
            import logging

            logging.warning(f"Failed to collect daily metrics for {d}: {e}")
    return results
