from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

import garmin_mcp.client as client_mod
from garmin_mcp.client import ensure_authenticated, reset_client


def test_reset_client_clears_singleton(mock_garmin):
    client_mod._client = mock_garmin
    client_mod._service._client = mock_garmin
    reset_client()
    assert client_mod._client is None
    assert client_mod._service._client is None


def test_reset_client_when_already_none():
    client_mod._client = None
    client_mod._service._client = None
    reset_client()  # should not raise
    assert client_mod._client is None
    assert client_mod._service._client is None


async def test_ensure_authenticated_happy_path(mock_garmin, mock_ctx, mocker, monkeypatch):
    """ensure_authenticated succeeds with valid credentials from env."""
    mock_garmin.login = MagicMock()

    async def passthrough_to_thread(fn, *args, **kwargs):
        return fn(*args, **kwargs)

    mocker.patch("asyncio.to_thread", side_effect=passthrough_to_thread)
    mocker.patch("garmin_mcp.service.Garmin", return_value=mock_garmin)
    monkeypatch.setenv("GARMIN_EMAIL", "user@test.com")
    monkeypatch.setenv("GARMIN_PASSWORD", "pass")

    result = await ensure_authenticated(mock_ctx)
    assert result is mock_garmin
    assert client_mod._client is mock_garmin


async def test_ensure_authenticated_via_ctx_elicit(mock_ctx, mocker, monkeypatch):
    """ensure_authenticated uses ctx.elicit when env vars missing."""
    # Reset service for clean state
    client_mod._service.reset()
    client_mod._client = None

    mock_garmin2 = MagicMock()
    mock_garmin2.login = MagicMock()

    async def passthrough_to_thread(fn, *args, **kwargs):
        return fn(*args, **kwargs)

    mocker.patch("asyncio.to_thread", side_effect=passthrough_to_thread)
    mocker.patch("garmin_mcp.service.Garmin", return_value=mock_garmin2)
    monkeypatch.delenv("GARMIN_EMAIL", raising=False)
    monkeypatch.delenv("GARMIN_PASSWORD", raising=False)

    mock_result = MagicMock()
    mock_result.action = "accept"
    mock_result.data.email = "prompted@test.com"
    mock_result.data.password = "prompted_pass"
    mock_ctx.elicit.return_value = mock_result

    result = await ensure_authenticated(mock_ctx)
    assert result is mock_garmin2
    mock_ctx.elicit.assert_called_once()


async def test_ensure_authenticated_elicit_cancelled(mock_ctx, mocker, monkeypatch):
    """ensure_authenticated raises if ctx.elicit is cancelled."""
    # Reset service for clean state
    client_mod._service.reset()
    client_mod._client = None

    async def passthrough_to_thread(fn, *args, **kwargs):
        return fn(*args, **kwargs)

    mocker.patch("asyncio.to_thread", side_effect=passthrough_to_thread)
    monkeypatch.delenv("GARMIN_EMAIL", raising=False)
    monkeypatch.delenv("GARMIN_PASSWORD", raising=False)

    mock_result = MagicMock()
    mock_result.action = "cancel"
    mock_ctx.elicit.return_value = mock_result

    with pytest.raises(RuntimeError, match="Credentials not provided"):
        await ensure_authenticated(mock_ctx)
