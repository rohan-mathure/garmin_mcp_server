"""Collect activities from Garmin."""

import asyncio
from datetime import datetime

from garminconnect import Garmin


async def collect_recent_activities(garmin: Garmin, limit: int = 20) -> list[dict]:
    """Fetch recent activities from Garmin."""
    activities = await asyncio.to_thread(garmin.get_activities, 0, limit)

    results = []
    for activity in activities:
        start_time = activity.get("startTimeInSeconds")
        if not start_time:
            continue

        row = {
            "activity_id": activity.get("activityId"),
            "start_time": None,  # Set below after conversion
            "activity_type": activity.get("activityType", {}).get("typeKey"),
            "name": activity.get("activityName"),
            "duration_seconds": activity.get("duration"),
            "distance_meters": activity.get("distance"),
            "avg_hr": activity.get("avgHR"),
            "max_hr": activity.get("maxHR"),
            "avg_pace_seconds_per_km": activity.get("avgPace"),
            "elevation_gain_meters": activity.get("elevationGain"),
            "calories": activity.get("calories"),
            "avg_power": activity.get("avgPower"),
        }
        # Convert Unix timestamp to TIMESTAMPTZ string
        dt = datetime.fromtimestamp(start_time / 1000.0, tz=datetime.now().astimezone().tzinfo)
        row["start_time"] = dt.isoformat()

        results.append(row)

    return results
