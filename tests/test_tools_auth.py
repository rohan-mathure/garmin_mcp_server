from __future__ import annotations

from unittest.mock import AsyncMock, patch

import garmin_mcp.client as client_mod
from garmin_mcp.tools.auth import garmin_auth_status, garmin_login, garmin_logout


async def test_login_success(mock_garmin, mock_ctx, mocker):
    mocker.patch(
        "garmin_mcp.tools.auth.ensure_authenticated",
        new=AsyncMock(return_value=mock_garmin),
    )
    result = await garmin_login(mock_ctx)
    assert result == "Successfully authenticated with Garmin Connect"


async def test_login_failure(mock_ctx, mocker):
    mocker.patch(
        "garmin_mcp.tools.auth.ensure_authenticated",
        new=AsyncMock(side_effect=Exception("bad credentials")),
    )
    result = await garmin_login(mock_ctx)
    assert "Authentication failed" in result
    assert "bad credentials" in result


async def test_logout_success(mock_garmin, mock_ctx, mocker):
    client_mod._client = mock_garmin
    mock_reset = mocker.patch("garmin_mcp.tools.auth.reset_client")
    result = await garmin_logout(mock_ctx)
    assert result == "Logged out successfully"
    mock_reset.assert_called_once()


async def test_logout_not_authenticated(mock_ctx, mocker):
    client_mod._client = None
    mock_reset = mocker.patch("garmin_mcp.tools.auth.reset_client")
    result = await garmin_logout(mock_ctx)
    assert result == "Not currently authenticated"
    mock_reset.assert_not_called()


async def test_logout_with_error(mock_garmin, mock_ctx, mocker):
    client_mod._client = mock_garmin
    mock_garmin.logout.side_effect = Exception("network error")
    mock_reset = mocker.patch("garmin_mcp.tools.auth.reset_client")
    result = await garmin_logout(mock_ctx)
    assert "Logout completed (with error:" in result
    assert "network error" in result
    mock_reset.assert_called_once()


async def test_auth_status_not_authenticated(monkeypatch):
    client_mod._client = None
    monkeypatch.delenv("GARMIN_EMAIL", raising=False)
    with patch("pathlib.Path.exists", return_value=False):
        result = await garmin_auth_status()
    assert result["authenticated"] is False
    assert result["email_configured"] is False
    assert result["token_file_exists"] is False


async def test_auth_status_authenticated(mock_garmin, monkeypatch):
    client_mod._client = mock_garmin
    monkeypatch.setenv("GARMIN_EMAIL", "test@test.com")
    with patch("pathlib.Path.exists", return_value=True):
        result = await garmin_auth_status()
    assert result["authenticated"] is True
    assert result["email_configured"] is True
    assert result["token_file_exists"] is True
    assert "token_file" in result
