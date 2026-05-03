"""Body metrics commands."""

import asyncio
from datetime import date

import typer

from garmin_mcp.cli.auth_adapter import get_garmin_client
from garmin_mcp.cli.output import print_error, print_json

app = typer.Typer(help="Body metrics")


@app.command("weight")
def weight(date_str: str = typer.Option("", "--date", "-d", help="YYYY-MM-DD")):
    """Weight and body fat."""
    async def _run():
        try:
            garmin = await get_garmin_client()
            d = date_str or date.today().isoformat()
            return await asyncio.to_thread(garmin.get_body_composition, d)
        except Exception as e:
            print_error(str(e))
            raise typer.Exit(1)

    print_json(asyncio.run(_run()))


@app.command("composition")
def composition(
    start: str = typer.Option("", "--start", "-s", help="Start date YYYY-MM-DD"),
    end: str = typer.Option("", "--end", "-e", help="End date YYYY-MM-DD"),
):
    """Body composition history."""
    async def _run():
        try:
            garmin = await get_garmin_client()
            return await asyncio.to_thread(garmin.get_body_composition, start, end)
        except Exception as e:
            print_error(str(e))
            raise typer.Exit(1)

    print_json(asyncio.run(_run()))


@app.command("hrv")
def hrv(date_str: str = typer.Option("", "--date", "-d", help="YYYY-MM-DD")):
    """Heart rate variability."""
    async def _run():
        try:
            garmin = await get_garmin_client()
            d = date_str or date.today().isoformat()
            return await asyncio.to_thread(garmin.get_hrv_data, d)
        except Exception as e:
            print_error(str(e))
            raise typer.Exit(1)

    print_json(asyncio.run(_run()))


@app.command("vo2max")
def vo2max(date_str: str = typer.Option("", "--date", "-d", help="YYYY-MM-DD")):
    """VO2 max estimate."""
    async def _run():
        try:
            garmin = await get_garmin_client()
            d = date_str or date.today().isoformat()
            return await asyncio.to_thread(garmin.get_vo2max_summary_by_date, d)
        except Exception as e:
            print_error(str(e))
            raise typer.Exit(1)

    print_json(asyncio.run(_run()))


@app.command("training-readiness")
def training_readiness(date_str: str = typer.Option("", "--date", "-d", help="YYYY-MM-DD")):
    """Training readiness score."""
    async def _run():
        try:
            garmin = await get_garmin_client()
            d = date_str or date.today().isoformat()
            return await asyncio.to_thread(garmin.get_training_readiness, d)
        except Exception as e:
            print_error(str(e))
            raise typer.Exit(1)

    print_json(asyncio.run(_run()))


@app.command("intensity-minutes")
def intensity_minutes(date_str: str = typer.Option("", "--date", "-d", help="YYYY-MM-DD")):
    """Weekly intensity minutes."""
    async def _run():
        try:
            garmin = await get_garmin_client()
            d = date_str or date.today().isoformat()
            return await asyncio.to_thread(garmin.get_weekly_intensity_minutes, d)
        except Exception as e:
            print_error(str(e))
            raise typer.Exit(1)

    print_json(asyncio.run(_run()))


@app.command("race-predictions")
def race_predictions():
    """Race finish time predictions."""
    async def _run():
        try:
            garmin = await get_garmin_client()
            return await asyncio.to_thread(garmin.get_race_predictions)
        except Exception as e:
            print_error(str(e))
            raise typer.Exit(1)

    print_json(asyncio.run(_run()))
