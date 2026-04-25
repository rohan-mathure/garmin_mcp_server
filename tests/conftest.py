from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def mock_garmin():
    client = MagicMock()
    client.ActivityDownloadFormat = MagicMock()
    client.ActivityDownloadFormat.GPX = "gpx"
    return client


@pytest.fixture
def mock_ctx():
    ctx = AsyncMock()
    ctx.elicit = AsyncMock()
    return ctx


@pytest.fixture(autouse=True)
def reset_garmin_client():
    """Reset the global Garmin client singleton before and after every test."""
    from garmin_mcp import client as client_mod

    client_mod._client = None
    yield
    client_mod._client = None


@pytest.fixture
def patch_to_thread(mocker):
    """Patch asyncio.to_thread to call the function directly (no thread pool)."""

    async def _passthrough(fn, *args, **kwargs):
        return fn(*args, **kwargs)

    return mocker.patch("asyncio.to_thread", new=AsyncMock(side_effect=_passthrough))
