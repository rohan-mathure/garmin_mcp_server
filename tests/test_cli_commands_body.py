"""Tests for CLI body commands."""

from unittest.mock import AsyncMock

import pytest
import typer

from garmin_mcp.cli.commands.body import (
    composition,
    hrv,
    intensity_minutes,
    race_predictions,
    training_readiness,
    vo2max,
    weight,
)


def test_weight_command(mocker):
    """Weight command fetches weight data."""
    mock_garmin = AsyncMock()
    mock_garmin.get_weight_data = AsyncMock(return_value={"weight": 75.5})
    mocker.patch(
        "garmin_mcp.cli.commands.body.get_garmin_client",
        new=AsyncMock(return_value=mock_garmin),
    )
    mocker.patch("garmin_mcp.cli.commands.body.print_json")

    weight()


def test_composition_command(mocker):
    """Composition command fetches body composition."""
    mock_garmin = AsyncMock()
    mock_garmin.get_body_composition = AsyncMock(return_value={})
    mocker.patch(
        "garmin_mcp.cli.commands.body.get_garmin_client",
        new=AsyncMock(return_value=mock_garmin),
    )
    mocker.patch("garmin_mcp.cli.commands.body.print_json")

    composition()


def test_hrv_command(mocker):
    """HRV command fetches heart rate variability."""
    mock_garmin = AsyncMock()
    mock_garmin.get_hrv_data = AsyncMock(return_value={})
    mocker.patch(
        "garmin_mcp.cli.commands.body.get_garmin_client",
        new=AsyncMock(return_value=mock_garmin),
    )
    mocker.patch("garmin_mcp.cli.commands.body.print_json")

    hrv()


def test_vo2max_command(mocker):
    """VO2Max command fetches aerobic capacity."""
    mock_garmin = AsyncMock()
    mock_garmin.get_vo2max_data = AsyncMock(return_value={})
    mocker.patch(
        "garmin_mcp.cli.commands.body.get_garmin_client",
        new=AsyncMock(return_value=mock_garmin),
    )
    mocker.patch("garmin_mcp.cli.commands.body.print_json")

    vo2max()


def test_training_readiness_command(mocker):
    """Training readiness command fetches readiness score."""
    mock_garmin = AsyncMock()
    mock_garmin.get_training_readiness_data = AsyncMock(return_value={})
    mocker.patch(
        "garmin_mcp.cli.commands.body.get_garmin_client",
        new=AsyncMock(return_value=mock_garmin),
    )
    mocker.patch("garmin_mcp.cli.commands.body.print_json")

    training_readiness()


def test_intensity_minutes_command(mocker):
    """Intensity minutes command fetches intensity stats."""
    mock_garmin = AsyncMock()
    mock_garmin.get_intensity_minutes = AsyncMock(return_value={})
    mocker.patch(
        "garmin_mcp.cli.commands.body.get_garmin_client",
        new=AsyncMock(return_value=mock_garmin),
    )
    mocker.patch("garmin_mcp.cli.commands.body.print_json")

    intensity_minutes()


def test_race_predictions_command(mocker):
    """Race predictions command fetches predictions."""
    mock_garmin = AsyncMock()
    mock_garmin.get_race_predictions = AsyncMock(return_value={})
    mocker.patch(
        "garmin_mcp.cli.commands.body.get_garmin_client",
        new=AsyncMock(return_value=mock_garmin),
    )
    mocker.patch("garmin_mcp.cli.commands.body.print_json")

    race_predictions()


def test_body_error_handling(mocker):
    """Body commands handle errors."""
    mocker.patch(
        "garmin_mcp.cli.commands.body.get_garmin_client",
        new=AsyncMock(side_effect=RuntimeError("API error")),
    )
    mocker.patch("garmin_mcp.cli.commands.body.print_error")

    with pytest.raises(typer.Exit):
        weight()
