"""Env-only credential provider for scraper (no interactive fallback)."""

import os

from garmin_mcp.service import CredentialProvider


def make_env_credential_provider() -> CredentialProvider:
    """Env-only creds. Raises if missing — no interactive fallback."""

    async def credential_provider() -> tuple[str, str]:
        email = os.getenv("GARMIN_EMAIL", "").strip()
        password = os.getenv("GARMIN_PASSWORD", "").strip()

        if not email or not password:
            raise RuntimeError(
                "GARMIN_EMAIL or GARMIN_PASSWORD not set. "
                "Scraper runs headless — env vars required."
            )

        return email, password

    return credential_provider
