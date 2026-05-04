"""Tests for CLI devices commands."""

from unittest.mock import AsyncMock

import pytest
import typer

from garmin_mcp.cli.commands.devices import (
    badges,
    device_info,
    gear,
    list_devices,
    personal_records,
)


def test_list_devices_command(mocker):
    """List devices command fetches devices."""
    mock_garmin = AsyncMock()
    mock_garmin.get_devices = AsyncMock(return_value=[{"deviceId": 1}])
    mocker.patch(
        "garmin_mcp.cli.commands.devices.get_garmin_client",
        new=AsyncMock(return_value=mock_garmin),
    )
    mocker.patch("garmin_mcp.cli.commands.devices.print_json")

    list_devices()


def test_device_info_command(mocker):
    """Device info command fetches device details."""
    mock_garmin = AsyncMock()
    mock_garmin.get_device_info = AsyncMock(return_value={})
    mocker.patch(
        "garmin_mcp.cli.commands.devices.get_garmin_client",
        new=AsyncMock(return_value=mock_garmin),
    )
    mocker.patch("garmin_mcp.cli.commands.devices.print_json")

    device_info(device_id=1)


def test_gear_command(mocker):
    """Gear command fetches equipment list."""
    mock_garmin = AsyncMock()
    mock_garmin.get_gear = AsyncMock(return_value=[])
    mocker.patch(
        "garmin_mcp.cli.commands.devices.get_garmin_client",
        new=AsyncMock(return_value=mock_garmin),
    )
    mocker.patch("garmin_mcp.cli.commands.devices.print_json")

    gear()


def test_records_command(mocker):
    """Records command fetches personal records."""
    mock_garmin = AsyncMock()
    mock_garmin.get_personal_records = AsyncMock(return_value=[])
    mocker.patch(
        "garmin_mcp.cli.commands.devices.get_garmin_client",
        new=AsyncMock(return_value=mock_garmin),
    )
    mocker.patch("garmin_mcp.cli.commands.devices.print_json")

    personal_records()


def test_badges_command(mocker):
    """Badges command fetches earned badges."""
    mock_garmin = AsyncMock()
    mock_garmin.get_badges = AsyncMock(return_value=[])
    mocker.patch(
        "garmin_mcp.cli.commands.devices.get_garmin_client",
        new=AsyncMock(return_value=mock_garmin),
    )
    mocker.patch("garmin_mcp.cli.commands.devices.print_json")

    badges()


def test_devices_error_handling(mocker):
    """Devices commands handle errors."""
    mocker.patch(
        "garmin_mcp.cli.commands.devices.get_garmin_client",
        new=AsyncMock(side_effect=RuntimeError("API error")),
    )
    mocker.patch("garmin_mcp.cli.commands.devices.print_error")

    with pytest.raises(typer.Exit):
        list_devices()
