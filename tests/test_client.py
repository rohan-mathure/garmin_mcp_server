from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from garminconnect import GarminConnectAuthenticationError

import garmin_mcp.client as client_mod
from garmin_mcp.client import _resolve_credentials, ensure_authenticated, get_client, reset_client


def test_reset_client_clears_singleton(mock_garmin):
    client_mod._client = mock_garmin
    reset_client()
    assert client_mod._client is None


def test_reset_client_when_already_none():
    client_mod._client = None
    reset_client()  # should not raise
    assert client_mod._client is None


async def test_get_client_returns_existing_singleton(mock_garmin, mock_ctx):
    client_mod._client = mock_garmin
    result = await get_client(mock_ctx)
    assert result is mock_garmin


async def test_get_client_creates_new_when_none(mock_garmin, mock_ctx, mocker):
    mock_resolve = mocker.patch(
        "garmin_mcp.client._resolve_credentials",
        new=AsyncMock(return_value=("user@test.com", "pass")),
    )
    mock_login = mocker.patch(
        "garmin_mcp.client._do_login",
        new=AsyncMock(return_value=mock_garmin),
    )
    result = await get_client(mock_ctx)
    assert result is mock_garmin
    assert client_mod._client is mock_garmin
    mock_resolve.assert_called_once_with(mock_ctx)
    mock_login.assert_called_once_with("user@test.com", "pass", mock_ctx)


async def test_get_client_singleton_skips_login_on_second_call(mock_garmin, mock_ctx, mocker):
    mocker.patch(
        "garmin_mcp.client._resolve_credentials",
        new=AsyncMock(return_value=("user@test.com", "pass")),
    )
    mocker.patch(
        "garmin_mcp.client._do_login",
        new=AsyncMock(return_value=mock_garmin),
    )
    await get_client(mock_ctx)
    mock_resolve2 = mocker.patch("garmin_mcp.client._resolve_credentials", new=AsyncMock())
    await get_client(mock_ctx)
    mock_resolve2.assert_not_called()


async def test_ensure_authenticated_happy_path(mock_garmin, mock_ctx, mocker):
    mocker.patch("garmin_mcp.client.get_client", new=AsyncMock(return_value=mock_garmin))
    result = await ensure_authenticated(mock_ctx)
    assert result is mock_garmin


async def test_ensure_authenticated_retries_on_auth_error(mock_garmin, mock_ctx, mocker):
    mock_get = mocker.patch(
        "garmin_mcp.client.get_client",
        new=AsyncMock(side_effect=[GarminConnectAuthenticationError("expired"), mock_garmin]),
    )
    result = await ensure_authenticated(mock_ctx)
    assert result is mock_garmin
    assert mock_get.call_count == 2
    assert client_mod._client is None  # was reset between the two calls


async def test_resolve_credentials_from_env(mock_ctx, monkeypatch):
    monkeypatch.setenv("GARMIN_EMAIL", "env@test.com")
    monkeypatch.setenv("GARMIN_PASSWORD", "envpass")
    email, password = await _resolve_credentials(mock_ctx)
    assert email == "env@test.com"
    assert password == "envpass"
    mock_ctx.elicit.assert_not_called()


async def test_resolve_credentials_via_elicit(mock_ctx, monkeypatch):
    monkeypatch.delenv("GARMIN_EMAIL", raising=False)
    monkeypatch.delenv("GARMIN_PASSWORD", raising=False)
    mock_result = MagicMock()
    mock_result.action = "accept"
    mock_result.data.email = "prompted@test.com"
    mock_result.data.password = "prompted_pass"
    mock_ctx.elicit.return_value = mock_result
    email, password = await _resolve_credentials(mock_ctx)
    assert email == "prompted@test.com"
    assert password == "prompted_pass"


async def test_resolve_credentials_cancelled(mock_ctx, monkeypatch):
    monkeypatch.delenv("GARMIN_EMAIL", raising=False)
    monkeypatch.delenv("GARMIN_PASSWORD", raising=False)
    mock_result = MagicMock()
    mock_result.action = "cancel"
    mock_ctx.elicit.return_value = mock_result
    with pytest.raises(RuntimeError, match="Credentials not provided"):
        await _resolve_credentials(mock_ctx)
