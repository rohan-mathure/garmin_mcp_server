"""CLI auth adapters — env + typer.prompt fallback."""

import os

import typer

from garmin_mcp.service import GarminService

_service = GarminService()  # Separate singleton for CLI


async def _get_credentials() -> tuple[str, str]:
    """Env vars or typer.prompt fallback."""
    email = os.getenv("GARMIN_EMAIL", "").strip()
    password = os.getenv("GARMIN_PASSWORD", "").strip()

    if not email:
        email = typer.prompt("Garmin email")
    if not password:
        password = typer.prompt("Garmin password", hide_input=True)

    return email, password


def _get_mfa_code() -> str:
    """Prompt for MFA code via typer."""
    return typer.prompt("Garmin MFA code (OTP)")


async def get_garmin_client():
    """Get authenticated Garmin client for CLI."""
    return await _service.ensure_authenticated(_get_credentials, _get_mfa_code)
