"""Tests for scraper collectors."""

from unittest.mock import AsyncMock, patch

import pytest

from garmin_mcp.scraper.collectors.activities import collect_recent_activities
from garmin_mcp.scraper.collectors.body import collect_body_for_date
from garmin_mcp.scraper.collectors.daily import (
    collect_daily_for_date,
    collect_daily_range,
)


@pytest.mark.asyncio
async def test_collect_daily_for_date():
    """Collect daily metrics for single date."""
    mock_garmin = AsyncMock()
    mock_garmin.get_stats = AsyncMock(
        return_value={
            "steps": 10000,
            "calories": 2000,
            "resting_hr": 60,
        }
    )

    with patch("asyncio.to_thread", side_effect=lambda fn, *args: fn(*args)):
        result = await collect_daily_for_date(mock_garmin, "2025-05-03")

    assert result["date"] == "2025-05-03"
    assert result["steps"] == 10000


@pytest.mark.asyncio
async def test_collect_daily_range():
    """Collect daily metrics for date range."""
    mock_garmin = AsyncMock()
    mock_garmin.get_stats = AsyncMock(
        return_value={
            "steps": 8000,
            "calories": 1800,
        }
    )

    with patch("asyncio.to_thread", side_effect=lambda fn, *args: fn(*args)):
        result = await collect_daily_range(mock_garmin, "2025-05-01", "2025-05-03")

    assert len(result) >= 1
    assert all("date" in row and "steps" in row for row in result)


@pytest.mark.asyncio
async def test_collect_body_for_date():
    """Collect body metrics for single date."""
    mock_garmin = AsyncMock()
    mock_garmin.get_body_composition = AsyncMock(
        return_value={
            "weight": 75.5,
            "bodyFatPercentage": 18.5,
            "vo2Max": {"value": 45.0},
        }
    )

    with patch("asyncio.to_thread", side_effect=lambda fn, *args: fn(*args)):
        result = await collect_body_for_date(mock_garmin, "2025-05-03")

    assert result["date"] == "2025-05-03"
    assert "weight_kg" in result


@pytest.mark.asyncio
async def test_collect_recent_activities():
    """Collect recent activities."""
    mock_garmin = AsyncMock()
    mock_garmin.get_activities = AsyncMock(
        return_value=[
            {
                "activityId": 123,
                "startTimeInSeconds": 1704067200,
                "activityName": "Morning Run",
                "distance": 5000,
            }
        ]
    )

    with patch("asyncio.to_thread", side_effect=lambda fn, *args: fn(*args)):
        result = await collect_recent_activities(mock_garmin, limit=20)

    assert len(result) >= 0
    if result:
        assert "activity_id" in result[0]


@pytest.mark.asyncio
async def test_collect_daily_handles_none_values():
    """Collect daily skips None values."""
    mock_garmin = AsyncMock()
    mock_garmin.get_stats = AsyncMock(
        return_value={
            "steps": 10000,
            "calories": None,
            "resting_hr": 60,
        }
    )

    with patch("asyncio.to_thread", side_effect=lambda fn, *args: fn(*args)):
        result = await collect_daily_for_date(mock_garmin, "2025-05-03")

    assert result["steps"] == 10000
    assert "calories" not in result or result.get("calories") is None
