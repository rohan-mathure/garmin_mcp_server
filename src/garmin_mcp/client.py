from __future__ import annotations

import asyncio
import logging
import os
import threading

from dotenv import load_dotenv
from garminconnect import Garmin
from mcp.server.fastmcp import Context

from garmin_mcp.models import CredentialsInput, MFAInput
from garmin_mcp.service import GarminService, CredentialProvider, MFAProvider

load_dotenv()
logger = logging.getLogger(__name__)

_service = GarminService()
# Maintain backward compat with tests that access _client directly
_client: Garmin | None = None


def _make_ctx_credential_provider(ctx: Context) -> CredentialProvider:
    """Create a credential provider that uses MCP ctx.elicit() as fallback."""

    async def credential_provider() -> tuple[str, str]:
        email = os.getenv("GARMIN_EMAIL", "")
        password = os.getenv("GARMIN_PASSWORD", "")

        if not email or not password:
            result = await ctx.elicit(
                "Garmin credentials not found in environment. Enter your email and password:",
                schema=CredentialsInput,
            )
            if result.action != "accept":
                raise RuntimeError(
                    "Credentials not provided — authentication cancelled"
                )
            email = result.data.email
            password = result.data.password

        return email, password

    return credential_provider


def _make_ctx_mfa_provider(
    ctx: Context, loop: asyncio.AbstractEventLoop
) -> MFAProvider:
    """Create an MFA provider that uses MCP ctx.elicit() from executor thread."""

    mfa_code: list[str] = []
    code_ready = threading.Event()

    def mfa_provider() -> str:
        async def elicit() -> None:
            r = await ctx.elicit(
                "Garmin MFA required. Enter your one-time password:",
                schema=MFAInput,
            )
            mfa_code.append(r.data.code if r.action == "accept" else "")
            code_ready.set()

        # Schedule elicitation on the event loop from this executor thread.
        # code_ready.wait() blocks the thread (not the event loop) until done.
        loop.call_soon_threadsafe(lambda: asyncio.ensure_future(elicit()))
        if not code_ready.wait(timeout=120):
            raise RuntimeError("MFA timeout — no code provided within 120 seconds")
        return mfa_code[0] if mfa_code else ""

    return mfa_provider


async def ensure_authenticated(ctx: Context) -> Garmin:
    global _client
    loop = asyncio.get_event_loop()
    cred_provider = _make_ctx_credential_provider(ctx)
    mfa_provider = _make_ctx_mfa_provider(ctx, loop)
    _client = await _service.ensure_authenticated(cred_provider, mfa_provider)
    return _client


def reset_client() -> None:
    global _client
    _client = None
    _service.reset()
