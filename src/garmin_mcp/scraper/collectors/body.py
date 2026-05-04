"""Collect body metrics from Garmin."""

import asyncio

from garminconnect import Garmin


async def collect_body_for_date(garmin: Garmin, d: str) -> dict:
    """Fetch and normalize body metrics for a single date (YYYY-MM-DD)."""
    weight_data = await asyncio.to_thread(garmin.get_body_composition, d)
    hrv_data = await asyncio.to_thread(garmin.get_hrv_data, d)
    vo2 = await asyncio.to_thread(garmin.get_vo2max_summary_by_date, d)
    readiness = await asyncio.to_thread(garmin.get_training_readiness, d)

    return {
        "date": d,
        "weight_kg": weight_data.get("weight") if weight_data else None,
        "body_fat_pct": weight_data.get("bodyFat") if weight_data else None,
        "hrv_weekly_avg": hrv_data.get("weeklyAvg") if hrv_data else None,
        "vo2max": vo2.get("vo2Max") if vo2 else None,
        "training_readiness_score": readiness.get("trainingReadiness", {}).get("value")
        if readiness
        else None,
    }
