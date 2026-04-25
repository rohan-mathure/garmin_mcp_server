import asyncio
import os
from pathlib import Path

from mcp.server.fastmcp import Context

from garmin_mcp.client import ensure_authenticated, reset_client
from garmin_mcp.server import mcp


@mcp.tool()
async def garmin_login(ctx: Context) -> str:
    """Login to Garmin Connect. Reads GARMIN_EMAIL/GARMIN_PASSWORD from env or prompts for credentials. Handles MFA if required."""
    try:
        await ensure_authenticated(ctx)
        return "Successfully authenticated with Garmin Connect"
    except Exception as e:
        return f"Authentication failed: {e}"


@mcp.tool()
async def garmin_logout(ctx: Context) -> str:
    """Logout from Garmin Connect and clear the saved session tokens."""
    import garmin_mcp.client as client_module
    garmin = client_module._client
    if garmin is None:
        return "Not currently authenticated"
    try:
        await asyncio.get_event_loop().run_in_executor(None, garmin.logout)
        reset_client()
        return "Logged out successfully"
    except Exception as e:
        reset_client()
        return f"Logout completed (with error: {e})"


@mcp.tool()
async def garmin_auth_status() -> dict:
    """Check current authentication status and token file location."""
    import garmin_mcp.client as client_module
    token_path = Path.home() / ".garminconnect" / "garmin_tokens.json"
    return {
        "authenticated": client_module._client is not None,
        "token_file": str(token_path),
        "token_file_exists": token_path.exists(),
        "email_configured": bool(os.getenv("GARMIN_EMAIL")),
    }
