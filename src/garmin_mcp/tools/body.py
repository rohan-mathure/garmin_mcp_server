import asyncio
from datetime import date, timedelta

from mcp.server.fastmcp import Context

from garmin_mcp.client import ensure_authenticated
from garmin_mcp.server import mcp


def _today() -> str:
    return date.today().isoformat()


def _week_ago() -> str:
    return (date.today() - timedelta(days=7)).isoformat()


@mcp.tool()
async def get_weight(ctx: Context, cdate: str = "") -> dict:
    """Get weight and body fat % for a given day. Date format: YYYY-MM-DD. Defaults to today."""
    garmin = await ensure_authenticated(ctx)
    d = cdate or _today()
    return await asyncio.to_thread(garmin.get_body_composition, d)


@mcp.tool()
async def get_body_composition(ctx: Context, start_date: str = "", end_date: str = "") -> dict:
    """Get body composition history over a date range. Defaults to last 7 days. Date format: YYYY-MM-DD."""
    garmin = await ensure_authenticated(ctx)
    start = start_date or _week_ago()
    end = end_date or _today()
    return await asyncio.to_thread(garmin.get_body_composition, start, end)


@mcp.tool()
async def get_hrv(ctx: Context, cdate: str = "") -> dict:
    """Get Heart Rate Variability (HRV) status and readings. Date format: YYYY-MM-DD. Defaults to today."""
    garmin = await ensure_authenticated(ctx)
    d = cdate or _today()
    return await asyncio.to_thread(garmin.get_hrv_data, d)


@mcp.tool()
async def get_vo2max(ctx: Context, cdate: str = "") -> dict:
    """Get VO2 max estimate. Date format: YYYY-MM-DD. Defaults to today."""
    garmin = await ensure_authenticated(ctx)
    d = cdate or _today()
    return await asyncio.to_thread(garmin.get_vo2max_summary_by_date, d)


@mcp.tool()
async def get_training_readiness(ctx: Context, cdate: str = "") -> dict:
    """Get training readiness score and contributing factors. Date format: YYYY-MM-DD. Defaults to today."""
    garmin = await ensure_authenticated(ctx)
    d = cdate or _today()
    return await asyncio.to_thread(garmin.get_training_readiness, d)


@mcp.tool()
async def get_intensity_minutes(ctx: Context, cdate: str = "") -> dict:
    """Get weekly moderate and vigorous intensity minutes. Date format: YYYY-MM-DD. Defaults to today."""
    garmin = await ensure_authenticated(ctx)
    d = cdate or _today()
    return await asyncio.to_thread(garmin.get_weekly_intensity_minutes, d)


@mcp.tool()
async def get_race_predictions(ctx: Context) -> dict:
    """Get predicted race finish times (5K, 10K, half marathon, marathon) based on recent training."""
    garmin = await ensure_authenticated(ctx)
    return await asyncio.to_thread(garmin.get_race_predictions)
