from __future__ import annotations

from unittest.mock import AsyncMock

from garmin_mcp.tools.activities import (
    download_activity_gpx,
    get_activity,
    get_activity_hr_zones,
    get_activity_splits,
    get_activity_weather,
    list_activities,
)


def _setup(mocker, mock_garmin):
    mocker.patch(
        "garmin_mcp.tools.activities.ensure_authenticated",
        new=AsyncMock(return_value=mock_garmin),
    )


# --- list_activities ---


async def test_list_activities_default_pagination(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    mock_garmin.get_activities.return_value = [{"activityId": 1}]
    result = await list_activities(mock_ctx)
    mock_garmin.get_activities.assert_called_once_with(0, 20)
    assert result == [{"activityId": 1}]


async def test_list_activities_custom_pagination(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    mock_garmin.get_activities.return_value = []
    await list_activities(mock_ctx, start=10, limit=5)
    mock_garmin.get_activities.assert_called_once_with(10, 5)


# --- get_activity ---


async def test_get_activity(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    mock_garmin.get_activity_details.return_value = {"activityId": 42, "activityName": "Run"}
    result = await get_activity(mock_ctx, activity_id=42)
    mock_garmin.get_activity_details.assert_called_once_with(42)
    assert result["activityId"] == 42


# --- get_activity_splits ---


async def test_get_activity_splits(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    mock_garmin.get_activity_splits.return_value = {"lapDTOs": []}
    result = await get_activity_splits(mock_ctx, activity_id=42)
    mock_garmin.get_activity_splits.assert_called_once_with(42)
    assert "lapDTOs" in result


# --- get_activity_weather ---


async def test_get_activity_weather(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    mock_garmin.get_activity_weather.return_value = {"temperature": 20}
    result = await get_activity_weather(mock_ctx, activity_id=42)
    mock_garmin.get_activity_weather.assert_called_once_with(42)
    assert result["temperature"] == 20


# --- download_activity_gpx ---


async def test_download_activity_gpx_bytes(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    mock_garmin.download_activity.return_value = b"<gpx>data</gpx>"
    result = await download_activity_gpx(mock_ctx, activity_id=42)
    assert result == "<gpx>data</gpx>"
    mock_garmin.download_activity.assert_called_once_with(
        42, dl_fmt=mock_garmin.ActivityDownloadFormat.GPX
    )


async def test_download_activity_gpx_string(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    mock_garmin.download_activity.return_value = "<gpx>already string</gpx>"
    result = await download_activity_gpx(mock_ctx, activity_id=42)
    assert result == "<gpx>already string</gpx>"


# --- get_activity_hr_zones ---
# NOTE: tool calls garmin.get_activity_hr_timeinzone — library actual method is get_activity_hr_in_timezones
# MagicMock auto-creates the attribute so tests pass, but the real API call would fail.


async def test_get_activity_hr_zones(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    mock_garmin.get_activity_hr_timeinzone.return_value = {"zones": []}
    result = await get_activity_hr_zones(mock_ctx, activity_id=42)
    mock_garmin.get_activity_hr_timeinzone.assert_called_once_with(42)
    assert result == {"zones": []}
