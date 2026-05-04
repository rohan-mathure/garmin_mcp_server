"""Tests for CLI auth adapter."""

import os
from unittest.mock import AsyncMock, patch

import pytest

from garmin_mcp.cli.auth_adapter import (
    _get_credentials,
    _get_mfa_code,
    get_garmin_client,
)


@pytest.mark.asyncio
async def test_get_credentials_from_env():
    """Get credentials from environment variables."""
    with patch.dict(
        os.environ,
        {"GARMIN_EMAIL": "test@example.com", "GARMIN_PASSWORD": "password123"},
    ):
        email, password = await _get_credentials()
        assert email == "test@example.com"
        assert password == "password123"


@pytest.mark.asyncio
async def test_get_credentials_from_prompt(monkeypatch):
    """Get credentials from typer.prompt when env vars missing."""
    monkeypatch.delenv("GARMIN_EMAIL", raising=False)
    monkeypatch.delenv("GARMIN_PASSWORD", raising=False)

    with patch("typer.prompt") as mock_prompt:
        mock_prompt.side_effect = ["user@test.com", "pass456"]
        email, password = await _get_credentials()
        assert email == "user@test.com"
        assert password == "pass456"
        assert mock_prompt.call_count == 2


def test_get_mfa_code():
    """Get MFA code from typer.prompt."""
    with patch("typer.prompt", return_value="123456"):
        code = _get_mfa_code()
        assert code == "123456"


@pytest.mark.asyncio
async def test_get_garmin_client_success(monkeypatch, mocker):
    """Get authenticated Garmin client."""
    monkeypatch.setenv("GARMIN_EMAIL", "test@example.com")
    monkeypatch.setenv("GARMIN_PASSWORD", "password123")

    mock_garmin = AsyncMock()
    mocker.patch(
        "garmin_mcp.cli.auth_adapter._service.ensure_authenticated",
        return_value=mock_garmin,
    )

    client = await get_garmin_client()
    assert client is mock_garmin


@pytest.mark.asyncio
async def test_get_garmin_client_with_mfa(monkeypatch, mocker):
    """Get Garmin client with MFA required."""
    monkeypatch.setenv("GARMIN_EMAIL", "test@example.com")
    monkeypatch.setenv("GARMIN_PASSWORD", "password123")

    mock_garmin = AsyncMock()
    mocker.patch(
        "garmin_mcp.cli.auth_adapter._service.ensure_authenticated",
        return_value=mock_garmin,
    )
    mocker.patch("garmin_mcp.cli.auth_adapter._get_mfa_code", return_value="123456")

    client = await get_garmin_client()
    assert client is mock_garmin
