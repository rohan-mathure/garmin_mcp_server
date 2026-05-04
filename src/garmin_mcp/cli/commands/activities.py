"""Activities commands."""

import asyncio

import typer

from garmin_mcp.cli.auth_adapter import get_garmin_client
from garmin_mcp.cli.output import print_error, print_json

app = typer.Typer(help="Activities")


@app.command("list")
def list_activities(
    start: int = typer.Option(0, "--start", help="Start index"),
    limit: int = typer.Option(20, "--limit", help="Max results"),
):
    """List recent activities."""

    async def _run():
        try:
            garmin = await get_garmin_client()
            return await asyncio.to_thread(garmin.get_activities, start, limit)
        except Exception as e:
            print_error(str(e))
            raise typer.Exit(1) from None

    print_json(asyncio.run(_run()))


@app.command("get")
def get_activity(activity_id: int = typer.Argument(..., help="Activity ID")):
    """Get activity details."""

    async def _run():
        try:
            garmin = await get_garmin_client()
            return await asyncio.to_thread(garmin.get_activity_details, activity_id)
        except Exception as e:
            print_error(str(e))
            raise typer.Exit(1) from None

    print_json(asyncio.run(_run()))


@app.command("splits")
def activity_splits(activity_id: int = typer.Argument(..., help="Activity ID")):
    """Get activity splits/laps."""

    async def _run():
        try:
            garmin = await get_garmin_client()
            return await asyncio.to_thread(garmin.get_activity_splits, activity_id)
        except Exception as e:
            print_error(str(e))
            raise typer.Exit(1) from None

    print_json(asyncio.run(_run()))


@app.command("weather")
def activity_weather(activity_id: int = typer.Argument(..., help="Activity ID")):
    """Get activity weather."""

    async def _run():
        try:
            garmin = await get_garmin_client()
            return await asyncio.to_thread(garmin.get_activity_weather, activity_id)
        except Exception as e:
            print_error(str(e))
            raise typer.Exit(1) from None

    print_json(asyncio.run(_run()))


@app.command("gpx")
def activity_gpx(activity_id: int = typer.Argument(..., help="Activity ID")):
    """Download activity GPX."""

    async def _run():
        try:
            garmin = await get_garmin_client()
            from garminconnect import ActivityDownloadFormat

            return await asyncio.to_thread(
                garmin.download_activity, activity_id, dl_fmt=ActivityDownloadFormat.GPX
            )
        except Exception as e:
            print_error(str(e))
            raise typer.Exit(1) from None

    result = asyncio.run(_run())
    if isinstance(result, bytes):
        result = result.decode("utf-8")
    typer.echo(result)


@app.command("hr-zones")
def activity_hr_zones(activity_id: int = typer.Argument(..., help="Activity ID")):
    """Get activity heart rate zones."""

    async def _run():
        try:
            garmin = await get_garmin_client()
            return await asyncio.to_thread(garmin.get_activity_hr_timeinzone, activity_id)
        except Exception as e:
            print_error(str(e))
            raise typer.Exit(1) from None

    print_json(asyncio.run(_run()))
