import asyncio

from mcp.server.fastmcp import Context

from garmin_mcp.client import ensure_authenticated
from garmin_mcp.server import mcp


@mcp.tool()
async def list_activities(ctx: Context, start: int = 0, limit: int = 20) -> list:
    """List Garmin Connect activities, most recent first. Use start/limit for pagination."""
    garmin = await ensure_authenticated(ctx)
    return await asyncio.to_thread(garmin.get_activities, start, limit)


@mcp.tool()
async def get_activity(ctx: Context, activity_id: int) -> dict:
    """Get full details for a specific activity by its ID."""
    garmin = await ensure_authenticated(ctx)
    return await asyncio.to_thread(garmin.get_activity_details, activity_id)


@mcp.tool()
async def get_activity_splits(ctx: Context, activity_id: int) -> dict:
    """Get lap/split data for a specific activity."""
    garmin = await ensure_authenticated(ctx)
    return await asyncio.to_thread(garmin.get_activity_splits, activity_id)


@mcp.tool()
async def get_activity_weather(ctx: Context, activity_id: int) -> dict:
    """Get weather conditions recorded during a specific activity."""
    garmin = await ensure_authenticated(ctx)
    return await asyncio.to_thread(garmin.get_activity_weather, activity_id)


@mcp.tool()
async def download_activity_gpx(ctx: Context, activity_id: int) -> str:
    """Download GPX file content for a specific activity. Returns raw GPX XML string."""
    garmin = await ensure_authenticated(ctx)
    data = await asyncio.to_thread(
        garmin.download_activity, activity_id, dl_fmt=garmin.ActivityDownloadFormat.GPX
    )
    return data.decode("utf-8") if isinstance(data, bytes) else data


@mcp.tool()
async def get_activity_hr_zones(ctx: Context, activity_id: int) -> dict:
    """Get time spent in each heart rate zone for a specific activity."""
    garmin = await ensure_authenticated(ctx)
    return await asyncio.to_thread(garmin.get_activity_hr_timeinzone, activity_id)
