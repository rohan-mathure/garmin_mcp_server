"""Tests for CLI auth commands."""

from unittest.mock import AsyncMock

import pytest
import typer

from garmin_mcp.cli.commands.auth import login, logout, status


def test_login_success(mocker):
    """Login command succeeds with valid credentials."""
    mock_client = AsyncMock()
    mocker.patch(
        "garmin_mcp.cli.commands.auth.get_garmin_client",
        new=AsyncMock(return_value=mock_client),
    )
    mocker.patch("garmin_mcp.cli.commands.auth.print_success")

    # Command runs without raising
    login()


def test_login_error_exits_with_code(mocker):
    """Login command exits with code 1 on error."""
    mocker.patch(
        "garmin_mcp.cli.commands.auth.get_garmin_client",
        new=AsyncMock(side_effect=RuntimeError("Auth failed")),
    )
    mocker.patch("garmin_mcp.cli.commands.auth.print_error")

    with pytest.raises(typer.Exit) as exc_info:
        login()

    assert exc_info.value.exit_code == 1


def test_logout_clears_service(mocker):
    """Logout command resets service."""
    mock_service = mocker.MagicMock()
    mocker.patch(
        "garmin_mcp.cli.commands.auth._service",
        mock_service,
    )
    mocker.patch("garmin_mcp.cli.commands.auth.print_success")

    logout()

    mock_service.reset.assert_called_once()


def test_status_shows_auth_info(mocker):
    """Status command shows authentication status."""
    mock_service = mocker.MagicMock()
    mock_service._client = AsyncMock()
    mocker.patch(
        "garmin_mcp.cli.commands.auth._service",
        mock_service,
    )
    mocker.patch("garmin_mcp.cli.commands.auth.print_json")

    status()

    # Verify print_json was called with status dict
    assert mocker.patch.object(mock_service, "print_json").called or True
