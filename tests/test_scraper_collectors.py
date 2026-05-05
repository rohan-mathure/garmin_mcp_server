from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from garmin_mcp.scraper.collectors.activities import collect_recent_activities


@pytest.fixture
def mock_garmin():
    client = MagicMock()
    return client


@pytest.fixture
def patch_to_thread_collector(mocker):
    """Patch asyncio.to_thread to call the function directly."""

    async def _passthrough(fn, *args, **kwargs):
        return fn(*args, **kwargs)

    return mocker.patch("asyncio.to_thread", new=AsyncMock(side_effect=_passthrough))


async def test_collect_valid_activity(mock_garmin, patch_to_thread_collector):
    """Valid activity with start_time is collected."""
    timestamp_ms = 1704067200000  # 2024-01-01 00:00:00 UTC
    mock_garmin.get_activities.return_value = [
        {
            "activityId": 123,
            "startTimeInSeconds": timestamp_ms,
            "activityType": {"typeKey": "running"},
            "activityName": "Morning Run",
            "duration": 3600,
            "distance": 10000,
            "avgHR": 150,
            "maxHR": 180,
            "avgPace": 360,
            "elevationGain": 100,
            "calories": 500,
            "avgPower": None,
        }
    ]

    result = await collect_recent_activities(mock_garmin, limit=20)

    assert len(result) == 1
    assert result[0]["activity_id"] == 123
    assert result[0]["activity_type"] == "running"
    assert result[0]["name"] == "Morning Run"
    assert result[0]["duration_seconds"] == 3600
    assert result[0]["distance_meters"] == 10000
    assert result[0]["start_time"] is not None
    assert isinstance(result[0]["start_time"], str)


async def test_skip_activity_missing_start_time(mock_garmin, patch_to_thread_collector):
    """Activity without start_time is skipped."""
    mock_garmin.get_activities.return_value = [
        {
            "activityId": 123,
            "startTimeInSeconds": None,
            "activityType": {"typeKey": "running"},
            "activityName": "Run",
            "duration": 3600,
            "distance": 10000,
        }
    ]

    result = await collect_recent_activities(mock_garmin, limit=20)

    assert len(result) == 0


async def test_skip_activity_zero_start_time(mock_garmin, patch_to_thread_collector):
    """Activity with zero start_time is skipped."""
    mock_garmin.get_activities.return_value = [
        {
            "activityId": 123,
            "startTimeInSeconds": 0,
            "activityType": {"typeKey": "running"},
            "activityName": "Run",
        }
    ]

    result = await collect_recent_activities(mock_garmin, limit=20)

    assert len(result) == 0


async def test_mixed_valid_and_invalid_activities(mock_garmin, patch_to_thread_collector):
    """Only valid activities are collected."""
    timestamp_ms = 1704067200000
    mock_garmin.get_activities.return_value = [
        {
            "activityId": 1,
            "startTimeInSeconds": timestamp_ms,
            "activityType": {"typeKey": "running"},
            "activityName": "Valid Run",
        },
        {
            "activityId": 2,
            "startTimeInSeconds": None,
            "activityType": {"typeKey": "cycling"},
            "activityName": "Invalid Activity",
        },
        {
            "activityId": 3,
            "startTimeInSeconds": timestamp_ms + 3600000,
            "activityType": {"typeKey": "walking"},
            "activityName": "Another Valid Run",
        },
    ]

    result = await collect_recent_activities(mock_garmin, limit=20)

    assert len(result) == 2
    assert result[0]["activity_id"] == 1
    assert result[1]["activity_id"] == 3


async def test_timestamp_conversion(mock_garmin, patch_to_thread_collector):
    """Timestamp is correctly converted from milliseconds to ISO format."""
    timestamp_ms = 1704067200000  # 2024-01-01 00:00:00 UTC
    mock_garmin.get_activities.return_value = [
        {
            "activityId": 123,
            "startTimeInSeconds": timestamp_ms,
            "activityType": {"typeKey": "running"},
            "activityName": "Run",
        }
    ]

    result = await collect_recent_activities(mock_garmin, limit=20)

    assert len(result) == 1
    # Verify ISO format with timezone offset
    assert "T" in result[0]["start_time"]
    # Check for timezone info (+ or - offset, or Z for UTC)
    assert (
        "+" in result[0]["start_time"]
        or "-" in result[0]["start_time"]
        or "Z" in result[0]["start_time"]
    )


async def test_null_optional_fields(mock_garmin, patch_to_thread_collector):
    """Optional fields are None when not provided."""
    timestamp_ms = 1704067200000
    mock_garmin.get_activities.return_value = [
        {
            "activityId": 123,
            "startTimeInSeconds": timestamp_ms,
            "activityType": {"typeKey": "running"},
            "activityName": "Run",
        }
    ]

    result = await collect_recent_activities(mock_garmin, limit=20)

    assert len(result) == 1
    assert result[0]["duration_seconds"] is None
    assert result[0]["distance_meters"] is None
    assert result[0]["avg_hr"] is None
    assert result[0]["calories"] is None


async def test_empty_activities_list(mock_garmin, patch_to_thread_collector):
    """Empty activities list returns empty result."""
    mock_garmin.get_activities.return_value = []

    result = await collect_recent_activities(mock_garmin, limit=20)

    assert len(result) == 0


async def test_activity_type_missing(mock_garmin, patch_to_thread_collector):
    """Activity without activityType dict is handled."""
    timestamp_ms = 1704067200000
    mock_garmin.get_activities.return_value = [
        {
            "activityId": 123,
            "startTimeInSeconds": timestamp_ms,
            "activityName": "Run",
        }
    ]

    result = await collect_recent_activities(mock_garmin, limit=20)

    assert len(result) == 1
    assert result[0]["activity_type"] is None
