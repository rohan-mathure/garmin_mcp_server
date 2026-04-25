from __future__ import annotations

import asyncio
import logging
import os
import threading

from dotenv import load_dotenv
from garminconnect import Garmin, GarminConnectAuthenticationError
from mcp.server.fastmcp import Context

from garmin_mcp.models import CredentialsInput, MFAInput

load_dotenv()
logger = logging.getLogger(__name__)

_client: Garmin | None = None


async def _resolve_credentials(ctx: Context) -> tuple[str, str]:
    email = os.getenv("GARMIN_EMAIL", "")
    password = os.getenv("GARMIN_PASSWORD", "")

    if not email or not password:
        result = await ctx.elicit(
            "Garmin credentials not found in environment. Enter your email and password:",
            schema=CredentialsInput,
        )
        if result.action != "accept":
            raise RuntimeError("Credentials not provided — authentication cancelled")
        email = result.data.email
        password = result.data.password

    return email, password


async def _do_login(email: str, password: str, ctx: Context) -> Garmin:
    loop = asyncio.get_event_loop()
    mfa_code: list[str] = []
    code_ready = threading.Event()

    def prompt_mfa() -> str:
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

    garmin = Garmin(email=email, password=password, prompt_mfa=prompt_mfa)
    await loop.run_in_executor(None, garmin.login)
    return garmin


async def get_client(ctx: Context) -> Garmin:
    global _client
    if _client is None:
        email, password = await _resolve_credentials(ctx)
        _client = await _do_login(email, password, ctx)
        logger.info("Garmin client authenticated successfully")
    return _client


async def ensure_authenticated(ctx: Context) -> Garmin:
    global _client
    try:
        return await get_client(ctx)
    except GarminConnectAuthenticationError:
        _client = None
        return await get_client(ctx)


def reset_client() -> None:
    global _client
    _client = None
