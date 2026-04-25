import asyncio
from datetime import date

from mcp.server.fastmcp import Context

from garmin_mcp.client import ensure_authenticated
from garmin_mcp.server import mcp


def _today() -> str:
    return date.today().isoformat()


@mcp.tool()
async def get_daily_summary(ctx: Context, cdate: str = "") -> dict:
    """Get full daily activity summary (steps, calories, HR, distance). Date format: YYYY-MM-DD. Defaults to today."""
    garmin = await ensure_authenticated(ctx)
    d = cdate or _today()
    return await asyncio.to_thread(garmin.get_user_summary, d)


@mcp.tool()
async def get_steps(ctx: Context, cdate: str = "") -> dict:
    """Get step count and goal for a given day. Date format: YYYY-MM-DD. Defaults to today."""
    garmin = await ensure_authenticated(ctx)
    d = cdate or _today()
    return await asyncio.to_thread(garmin.get_steps_data, d)


@mcp.tool()
async def get_heart_rate(ctx: Context, cdate: str = "") -> dict:
    """Get heart rate data (resting HR, min/max, hourly timeline). Date format: YYYY-MM-DD. Defaults to today."""
    garmin = await ensure_authenticated(ctx)
    d = cdate or _today()
    return await asyncio.to_thread(garmin.get_heart_rates, d)


@mcp.tool()
async def get_stress(ctx: Context, cdate: str = "") -> dict:
    """Get stress score and timeline for a given day. Date format: YYYY-MM-DD. Defaults to today."""
    garmin = await ensure_authenticated(ctx)
    d = cdate or _today()
    return await asyncio.to_thread(garmin.get_stress_data, d)


@mcp.tool()
async def get_spo2(ctx: Context, cdate: str = "") -> dict:
    """Get blood oxygen (SpO2) readings for a given day. Date format: YYYY-MM-DD. Defaults to today."""
    garmin = await ensure_authenticated(ctx)
    d = cdate or _today()
    return await asyncio.to_thread(garmin.get_spo2_data, d)


@mcp.tool()
async def get_sleep(ctx: Context, cdate: str = "") -> dict:
    """Get sleep analysis: stages, score, total duration, and restlessness. Date format: YYYY-MM-DD. Defaults to today."""
    garmin = await ensure_authenticated(ctx)
    d = cdate or _today()
    return await asyncio.to_thread(garmin.get_sleep_data, d)


@mcp.tool()
async def get_calories(ctx: Context, cdate: str = "") -> dict:
    """Get active and resting calorie burn for a given day. Date format: YYYY-MM-DD. Defaults to today."""
    garmin = await ensure_authenticated(ctx)
    d = cdate or _today()
    summary = await asyncio.to_thread(garmin.get_user_summary, d)
    return {
        "date": d,
        "active_kilocalories": summary.get("activeKilocalories"),
        "bmr_kilocalories": summary.get("bmrKilocalories"),
        "total_kilocalories": summary.get("totalKilocalories"),
        "wellness_active_kilocalories": summary.get("wellnessActiveKilocalories"),
        "consumed_kilocalories": summary.get("consumedKilocalories"),
        "remaining_kilocalories": summary.get("remainingKilocalories"),
    }
