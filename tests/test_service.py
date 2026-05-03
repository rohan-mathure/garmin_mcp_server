"""Tests for GarminService — shared auth layer without MCP dependency."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from garminconnect import GarminConnectAuthenticationError

from garmin_mcp.service import CredentialProvider, GarminService, MFAProvider


@pytest.fixture
def service():
    """Fresh GarminService instance."""
    return GarminService()


@pytest.fixture
def mock_garmin_class(mocker):
    """Mock the Garmin class itself so we can control login behavior."""
    garmin_mock = MagicMock()
    garmin_mock.login = MagicMock()
    mocker.patch("garmin_mcp.service.Garmin", return_value=garmin_mock)
    return garmin_mock


@pytest.mark.asyncio
async def test_authenticate_success(service, mock_garmin_class, mocker):
    """Authenticate succeeds with valid credentials."""
    async def cred_provider() -> tuple[str, str]:
        return ("user@example.com", "password123")

    # Mock asyncio.to_thread to run login synchronously
    async def passthrough_to_thread(fn, *args, **kwargs):
        return fn(*args, **kwargs)

    mocker.patch("asyncio.to_thread", side_effect=passthrough_to_thread)

    client = await service.authenticate(cred_provider)

    assert client is not None
    # Verify Garmin was instantiated with credentials
    from garmin_mcp.service import Garmin

    Garmin.assert_called_once()
    call_kwargs = Garmin.call_args.kwargs
    assert call_kwargs["email"] == "user@example.com"
    assert call_kwargs["password"] == "password123"
    assert "prompt_mfa" in call_kwargs


@pytest.mark.asyncio
async def test_authenticate_with_mfa(service, mock_garmin_class, mocker):
    """Authentication calls MFA provider when MFA is needed."""
    async def cred_provider() -> tuple[str, str]:
        return ("user@example.com", "password123")

    def mfa_provider() -> str:
        return "123456"

    async def passthrough_to_thread(fn, *args, **kwargs):
        return fn(*args, **kwargs)

    mocker.patch("asyncio.to_thread", side_effect=passthrough_to_thread)

    # Simulate MFA being triggered during login
    def mock_login_with_mfa():
        # Extract the prompt_mfa callback and call it
        from garmin_mcp.service import Garmin

        prompt_mfa = Garmin.call_args.kwargs["prompt_mfa"]
        code = prompt_mfa()
        assert code == "123456"

    mock_garmin_class.login.side_effect = mock_login_with_mfa

    client = await service.authenticate(cred_provider, mfa_provider)
    assert client is not None


@pytest.mark.asyncio
async def test_authenticate_no_mfa_provider_raises(service, mock_garmin_class, mocker):
    """Authentication fails if MFA is needed but no provider given."""
    async def cred_provider() -> tuple[str, str]:
        return ("user@example.com", "password123")

    async def passthrough_to_thread(fn, *args, **kwargs):
        return fn(*args, **kwargs)

    mocker.patch("asyncio.to_thread", side_effect=passthrough_to_thread)

    # Simulate MFA being triggered
    def mock_login_needs_mfa():
        from garmin_mcp.service import Garmin

        prompt_mfa = Garmin.call_args.kwargs["prompt_mfa"]
        prompt_mfa()  # This will raise since no MFA provider

    mock_garmin_class.login.side_effect = mock_login_needs_mfa

    with pytest.raises(RuntimeError, match="MFA required but no MFA provider"):
        await service.authenticate(cred_provider, mfa_provider=None)


@pytest.mark.asyncio
async def test_ensure_authenticated_caches_client(service, mock_garmin_class, mocker):
    """ensure_authenticated caches the client on first call."""
    async def cred_provider() -> tuple[str, str]:
        return ("user@example.com", "password123")

    async def passthrough_to_thread(fn, *args, **kwargs):
        return fn(*args, **kwargs)

    mocker.patch("asyncio.to_thread", side_effect=passthrough_to_thread)

    client1 = await service.ensure_authenticated(cred_provider)
    client2 = await service.ensure_authenticated(cred_provider)

    assert client1 is client2  # Same instance
    # Garmin constructor should only be called once
    from garmin_mcp.service import Garmin

    assert Garmin.call_count == 1


@pytest.mark.asyncio
async def test_ensure_authenticated_retries_on_auth_error(
    service, mock_garmin_class, mocker
):
    """ensure_authenticated retries once on GarminConnectAuthenticationError."""
    async def cred_provider() -> tuple[str, str]:
        return ("user@example.com", "password123")

    async def passthrough_to_thread(fn, *args, **kwargs):
        return fn(*args, **kwargs)

    mocker.patch("asyncio.to_thread", side_effect=passthrough_to_thread)

    call_count = 0

    def mock_login_fails_first():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise GarminConnectAuthenticationError(401, "Invalid credentials")
        # Second call succeeds

    mock_garmin_class.login.side_effect = mock_login_fails_first

    client = await service.ensure_authenticated(cred_provider)
    assert client is not None
    # Should have tried twice
    assert mock_garmin_class.login.call_count == 2


@pytest.mark.asyncio
async def test_reset_clears_client(service, mocker):
    """reset() clears the cached client."""
    async def cred_provider() -> tuple[str, str]:
        return ("user@example.com", "password123")

    async def passthrough_to_thread(fn, *args, **kwargs):
        return fn(*args, **kwargs)

    mocker.patch("asyncio.to_thread", side_effect=passthrough_to_thread)

    # Mock Garmin to return different instances each time
    garmin_instance_1 = MagicMock()
    garmin_instance_2 = MagicMock()
    garmin_instance_1.login = MagicMock()
    garmin_instance_2.login = MagicMock()

    mocker.patch(
        "garmin_mcp.service.Garmin",
        side_effect=[garmin_instance_1, garmin_instance_2],
    )

    client1 = await service.ensure_authenticated(cred_provider)
    service.reset()
    client2 = await service.ensure_authenticated(cred_provider)

    assert client1 is not client2  # Different instances after reset
