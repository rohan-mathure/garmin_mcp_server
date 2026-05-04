"""Device and gear commands."""

import asyncio

import typer

from garmin_mcp.cli.auth_adapter import get_garmin_client
from garmin_mcp.cli.output import print_error, print_json

app = typer.Typer(help="Devices & gear")


@app.command("list")
def list_devices():
    """List connected devices."""

    async def _run():
        try:
            garmin = await get_garmin_client()
            return await asyncio.to_thread(garmin.get_devices)
        except Exception as e:
            print_error(str(e))
            raise typer.Exit(1) from None

    print_json(asyncio.run(_run()))


@app.command("info")
def device_info(device_id: int = typer.Argument(..., help="Device ID")):
    """Device settings and info."""

    async def _run():
        try:
            garmin = await get_garmin_client()
            return await asyncio.to_thread(garmin.get_device_settings, device_id)
        except Exception as e:
            print_error(str(e))
            raise typer.Exit(1) from None

    print_json(asyncio.run(_run()))


@app.command("gear")
def gear():
    """List gear and equipment."""

    async def _run():
        try:
            garmin = await get_garmin_client()
            return await asyncio.to_thread(garmin.get_gear)
        except Exception as e:
            print_error(str(e))
            raise typer.Exit(1) from None

    print_json(asyncio.run(_run()))


@app.command("records")
def personal_records():
    """Personal records and all-time bests."""

    async def _run():
        try:
            garmin = await get_garmin_client()
            return await asyncio.to_thread(garmin.get_personal_record)
        except Exception as e:
            print_error(str(e))
            raise typer.Exit(1) from None

    print_json(asyncio.run(_run()))


@app.command("badges")
def badges():
    """Earned badges and achievements."""

    async def _run():
        try:
            garmin = await get_garmin_client()
            return await asyncio.to_thread(garmin.get_badges)
        except Exception as e:
            print_error(str(e))
            raise typer.Exit(1) from None

    print_json(asyncio.run(_run()))
