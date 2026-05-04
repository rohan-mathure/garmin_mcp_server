"""Daily metrics commands."""

import asyncio
from datetime import date

import typer

from garmin_mcp.cli.auth_adapter import get_garmin_client
from garmin_mcp.cli.output import print_error, print_json

app = typer.Typer(help="Daily metrics")


@app.command("summary")
def summary(date_str: str = typer.Option("", "--date", "-d", help="YYYY-MM-DD")):
    """Daily summary."""

    async def _run():
        try:
            garmin = await get_garmin_client()
            d = date_str or date.today().isoformat()
            return await asyncio.to_thread(garmin.get_user_summary, d)
        except Exception as e:
            print_error(str(e))
            raise typer.Exit(1) from None

    print_json(asyncio.run(_run()))


@app.command("steps")
def steps(date_str: str = typer.Option("", "--date", "-d", help="YYYY-MM-DD")):
    """Step count and goal."""

    async def _run():
        try:
            garmin = await get_garmin_client()
            d = date_str or date.today().isoformat()
            return await asyncio.to_thread(garmin.get_steps_data, d)
        except Exception as e:
            print_error(str(e))
            raise typer.Exit(1) from None

    print_json(asyncio.run(_run()))


@app.command("heart-rate")
def heart_rate(date_str: str = typer.Option("", "--date", "-d", help="YYYY-MM-DD")):
    """Heart rate data."""

    async def _run():
        try:
            garmin = await get_garmin_client()
            d = date_str or date.today().isoformat()
            return await asyncio.to_thread(garmin.get_heart_rates, d)
        except Exception as e:
            print_error(str(e))
            raise typer.Exit(1) from None

    print_json(asyncio.run(_run()))


@app.command("stress")
def stress(date_str: str = typer.Option("", "--date", "-d", help="YYYY-MM-DD")):
    """Stress data."""

    async def _run():
        try:
            garmin = await get_garmin_client()
            d = date_str or date.today().isoformat()
            return await asyncio.to_thread(garmin.get_stress_data, d)
        except Exception as e:
            print_error(str(e))
            raise typer.Exit(1) from None

    print_json(asyncio.run(_run()))


@app.command("spo2")
def spo2(date_str: str = typer.Option("", "--date", "-d", help="YYYY-MM-DD")):
    """Blood oxygen."""

    async def _run():
        try:
            garmin = await get_garmin_client()
            d = date_str or date.today().isoformat()
            return await asyncio.to_thread(garmin.get_spo2_data, d)
        except Exception as e:
            print_error(str(e))
            raise typer.Exit(1) from None

    print_json(asyncio.run(_run()))


@app.command("sleep")
def sleep(date_str: str = typer.Option("", "--date", "-d", help="YYYY-MM-DD")):
    """Sleep data."""

    async def _run():
        try:
            garmin = await get_garmin_client()
            d = date_str or date.today().isoformat()
            return await asyncio.to_thread(garmin.get_sleep_data, d)
        except Exception as e:
            print_error(str(e))
            raise typer.Exit(1) from None

    print_json(asyncio.run(_run()))


@app.command("calories")
def calories(date_str: str = typer.Option("", "--date", "-d", help="YYYY-MM-DD")):
    """Calorie data."""

    async def _run():
        try:
            garmin = await get_garmin_client()
            d = date_str or date.today().isoformat()
            summary = await asyncio.to_thread(garmin.get_user_summary, d)
            return {
                "activeKilocalories": summary.get("activeKilocalories"),
                "bmrKilocalories": summary.get("bmrKilocalories"),
                "totalKilocalories": summary.get("totalKilocalories"),
                "wellnessActiveKilocalories": summary.get("wellnessActiveKilocalories"),
                "consumedKilocalories": summary.get("consumedKilocalories"),
                "remainingKilocalories": summary.get("remainingKilocalories"),
            }
        except Exception as e:
            print_error(str(e))
            raise typer.Exit(1) from None

    print_json(asyncio.run(_run()))
