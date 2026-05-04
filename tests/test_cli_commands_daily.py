"""Tests for CLI daily commands."""

from unittest.mock import AsyncMock

import pytest
import typer

from garmin_mcp.cli.commands.daily import (
    calories,
    heart_rate,
    sleep,
    spo2,
    steps,
    stress,
    summary,
)


@pytest.fixture
def mock_garmin():
    """Mock Garmin client."""
    return AsyncMock()


def test_daily_summary_command(mocker, mock_garmin):
    """Daily summary command fetches and prints data."""
    mocker.patch(
        "garmin_mcp.cli.commands.daily.get_garmin_client",
        new=AsyncMock(return_value=mock_garmin),
    )
    mock_garmin.get_stats = AsyncMock(return_value={"steps": 10000})
    mocker.patch("garmin_mcp.cli.commands.daily.print_json")

    summary()

    # Command should succeed without error


def test_steps_command_with_date(mocker, mock_garmin):
    """Steps command accepts date parameter."""
    mocker.patch(
        "garmin_mcp.cli.commands.daily.get_garmin_client",
        new=AsyncMock(return_value=mock_garmin),
    )
    mock_garmin.get_steps_data = AsyncMock(return_value={"steps": 8500})
    mocker.patch("garmin_mcp.cli.commands.daily.print_json")

    steps(date="2025-05-03")

    # Command should succeed without error


def test_heart_rate_command(mocker, mock_garmin):
    """Heart rate command fetches HR data."""
    mocker.patch(
        "garmin_mcp.cli.commands.daily.get_garmin_client",
        new=AsyncMock(return_value=mock_garmin),
    )
    mock_garmin.get_heart_rate_data = AsyncMock(return_value={"resting_heart_rate": 60})
    mocker.patch("garmin_mcp.cli.commands.daily.print_json")

    heart_rate()

    # Command should succeed


def test_stress_command(mocker, mock_garmin):
    """Stress command fetches stress data."""
    mocker.patch(
        "garmin_mcp.cli.commands.daily.get_garmin_client",
        new=AsyncMock(return_value=mock_garmin),
    )
    mock_garmin.get_stress_data = AsyncMock(return_value={"stress": 30})
    mocker.patch("garmin_mcp.cli.commands.daily.print_json")

    stress()

    # Command should succeed


def test_spo2_command(mocker, mock_garmin):
    """SpO2 command fetches oxygen saturation data."""
    mocker.patch(
        "garmin_mcp.cli.commands.daily.get_garmin_client",
        new=AsyncMock(return_value=mock_garmin),
    )
    mock_garmin.get_spo2_data = AsyncMock(return_value={"spo2": 98})
    mocker.patch("garmin_mcp.cli.commands.daily.print_json")

    spo2()

    # Command should succeed


def test_sleep_command(mocker, mock_garmin):
    """Sleep command fetches sleep data."""
    mocker.patch(
        "garmin_mcp.cli.commands.daily.get_garmin_client",
        new=AsyncMock(return_value=mock_garmin),
    )
    mock_garmin.get_sleep_data = AsyncMock(return_value={"duration": 28800})
    mocker.patch("garmin_mcp.cli.commands.daily.print_json")

    sleep()

    # Command should succeed


def test_calories_command(mocker, mock_garmin):
    """Calories command fetches calorie data."""
    mocker.patch(
        "garmin_mcp.cli.commands.daily.get_garmin_client",
        new=AsyncMock(return_value=mock_garmin),
    )
    mock_garmin.get_calories_data = AsyncMock(return_value={"active_calories": 500})
    mocker.patch("garmin_mcp.cli.commands.daily.print_json")

    calories()

    # Command should succeed


def test_command_error_handling(mocker, mock_garmin):
    """Commands handle errors gracefully."""
    mocker.patch(
        "garmin_mcp.cli.commands.daily.get_garmin_client",
        new=AsyncMock(side_effect=RuntimeError("API error")),
    )
    mocker.patch("garmin_mcp.cli.commands.daily.print_error")

    with pytest.raises(typer.Exit) as exc_info:
        steps()

    assert exc_info.value.exit_code == 1
