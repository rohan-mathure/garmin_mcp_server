import asyncio

from mcp.server.fastmcp import Context

from garmin_mcp.client import ensure_authenticated
from garmin_mcp.server import mcp


@mcp.tool()
async def list_devices(ctx: Context) -> list:
    """List all Garmin devices connected to the account."""
    garmin = await ensure_authenticated(ctx)
    return await asyncio.to_thread(garmin.get_devices)


@mcp.tool()
async def get_device_info(ctx: Context, device_id: int) -> dict:
    """Get settings and information for a specific Garmin device by its ID."""
    garmin = await ensure_authenticated(ctx)
    return await asyncio.to_thread(garmin.get_device_settings, device_id)


@mcp.tool()
async def list_gear(ctx: Context) -> list:
    """List all gear and equipment (shoes, bikes, etc.) tracked in Garmin Connect."""
    garmin = await ensure_authenticated(ctx)
    user_info = await asyncio.to_thread(garmin.get_user_summary, __import__("datetime").date.today().isoformat())
    user_hash = user_info.get("userProfileId") or user_info.get("userId", "")
    return await asyncio.to_thread(garmin.get_gear, user_hash)


@mcp.tool()
async def list_personal_records(ctx: Context) -> dict:
    """List personal records and all-time bests (fastest pace, longest run, etc.)."""
    garmin = await ensure_authenticated(ctx)
    return await asyncio.to_thread(garmin.get_personal_record)


@mcp.tool()
async def list_badges(ctx: Context) -> list:
    """List earned badges and completed challenges on Garmin Connect."""
    garmin = await ensure_authenticated(ctx)
    return await asyncio.to_thread(garmin.get_badges)
