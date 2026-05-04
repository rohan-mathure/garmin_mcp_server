"""Tests for CLI activities commands."""

from unittest.mock import AsyncMock

import pytest
import typer

from garmin_mcp.cli.commands.activities import (
    activity_gpx,
    activity_hr_zones,
    activity_splits,
    activity_weather,
    get_activity,
    list_activities,
)


def test_list_activities_command(mocker):
    """List activities command fetches activities."""
    mock_garmin = AsyncMock()
    mock_garmin.get_activities = AsyncMock(
        return_value=[{"activityId": 123, "activityName": "Run"}]
    )
    mocker.patch(
        "garmin_mcp.cli.commands.activities.get_garmin_client",
        new=AsyncMock(return_value=mock_garmin),
    )
    mocker.patch("garmin_mcp.cli.commands.activities.print_json")

    list_activities(limit=10)


def test_get_activity_command(mocker):
    """Get activity command fetches single activity."""
    mock_garmin = AsyncMock()
    mock_garmin.get_activity = AsyncMock(return_value={"activityId": 123, "distance": 5000})
    mocker.patch(
        "garmin_mcp.cli.commands.activities.get_garmin_client",
        new=AsyncMock(return_value=mock_garmin),
    )
    mocker.patch("garmin_mcp.cli.commands.activities.print_json")

    get_activity(activity_id=123)


def test_splits_command(mocker):
    """Splits command fetches activity splits."""
    mock_garmin = AsyncMock()
    mock_garmin.get_activity_splits = AsyncMock(return_value=[])
    mocker.patch(
        "garmin_mcp.cli.commands.activities.get_garmin_client",
        new=AsyncMock(return_value=mock_garmin),
    )
    mocker.patch("garmin_mcp.cli.commands.activities.print_json")

    activity_splits(activity_id=123)


def test_weather_command(mocker):
    """Weather command fetches activity weather."""
    mock_garmin = AsyncMock()
    mock_garmin.get_activity_weather = AsyncMock(return_value={})
    mocker.patch(
        "garmin_mcp.cli.commands.activities.get_garmin_client",
        new=AsyncMock(return_value=mock_garmin),
    )
    mocker.patch("garmin_mcp.cli.commands.activities.print_json")

    activity_weather(activity_id=123)


def test_gpx_command(mocker):
    """GPX command fetches activity GPX."""
    mock_garmin = AsyncMock()
    mock_garmin.download_activity_gpx = AsyncMock(return_value="<gpx>...</gpx>")
    mocker.patch(
        "garmin_mcp.cli.commands.activities.get_garmin_client",
        new=AsyncMock(return_value=mock_garmin),
    )
    mocker.patch("garmin_mcp.cli.commands.activities.print_json")

    activity_gpx(activity_id=123)


def test_hr_zones_command(mocker):
    """HR zones command fetches heart rate zones."""
    mock_garmin = AsyncMock()
    mock_garmin.get_activity_hr_zones = AsyncMock(return_value={})
    mocker.patch(
        "garmin_mcp.cli.commands.activities.get_garmin_client",
        new=AsyncMock(return_value=mock_garmin),
    )
    mocker.patch("garmin_mcp.cli.commands.activities.print_json")

    activity_hr_zones(activity_id=123)


def test_activities_error_handling(mocker):
    """Activities commands handle errors."""
    mocker.patch(
        "garmin_mcp.cli.commands.activities.get_garmin_client",
        new=AsyncMock(side_effect=RuntimeError("API error")),
    )
    mocker.patch("garmin_mcp.cli.commands.activities.print_error")

    with pytest.raises(typer.Exit):
        list_activities()
