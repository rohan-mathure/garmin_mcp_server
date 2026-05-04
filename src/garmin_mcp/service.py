"""Shared Garmin authentication and client service — no MCP dependency."""

from __future__ import annotations

import asyncio
import logging
import threading
from collections.abc import Awaitable, Callable

from garminconnect import Garmin, GarminConnectAuthenticationError

logger = logging.getLogger(__name__)

# Protocols for dependency injection of credential and MFA providers
CredentialProvider = Callable[[], Awaitable[tuple[str, str]]]
MFAProvider = Callable[[], str]


class GarminService:
    """Singleton service managing Garmin client auth and lifecycle."""

    def __init__(self) -> None:
        self._client: Garmin | None = None

    async def authenticate(
        self,
        credential_provider: CredentialProvider,
        mfa_provider: MFAProvider | None = None,
    ) -> Garmin:
        """Authenticate and return a Garmin client.

        Args:
            credential_provider: async callable returning (email, password)
            mfa_provider: optional sync callable returning MFA code from executor thread

        Returns:
            Authenticated Garmin instance
        """
        email, password = await credential_provider()

        loop = asyncio.get_event_loop()
        mfa_code: list[str] = []
        code_ready = threading.Event()

        def prompt_mfa() -> str:
            if mfa_provider is None:
                raise RuntimeError("MFA required but no MFA provider given")

            # Synchronously call the provider from the executor thread
            code = mfa_provider()
            mfa_code.append(code)
            code_ready.set()
            return code

        garmin = Garmin(email=email, password=password, prompt_mfa=prompt_mfa)
        await loop.run_in_executor(None, garmin.login)
        logger.info("Garmin client authenticated successfully")
        return garmin

    async def ensure_authenticated(
        self,
        credential_provider: CredentialProvider,
        mfa_provider: MFAProvider | None = None,
    ) -> Garmin:
        """Ensure client is authenticated. Retries once on auth failure.

        Args:
            credential_provider: async callable returning (email, password)
            mfa_provider: optional sync callable returning MFA code

        Returns:
            Authenticated Garmin instance
        """
        if self._client is not None:
            return self._client

        try:
            self._client = await self.authenticate(credential_provider, mfa_provider)
        except GarminConnectAuthenticationError:
            self._client = None
            self._client = await self.authenticate(credential_provider, mfa_provider)

        return self._client

    def reset(self) -> None:
        """Clear the cached client, forcing re-authentication on next call."""
        self._client = None
