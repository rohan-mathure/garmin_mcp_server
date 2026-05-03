"""Auth commands: login, logout, status."""

import asyncio
import os

import typer

from garmin_mcp.cli.auth_adapter import _service, get_garmin_client
from garmin_mcp.cli.output import print_error, print_json, print_success

app = typer.Typer(help="Authentication")


@app.command()
def login():
    """Login to Garmin Connect."""
    async def _run():
        try:
            client = await get_garmin_client()
            print_success("Logged in")
        except Exception as e:
            print_error(str(e))
            raise typer.Exit(1)

    asyncio.run(_run())


@app.command()
def logout():
    """Logout and clear cached credentials."""
    _service.reset()
    print_success("Logged out")


@app.command()
def status():
    """Show auth status."""
    token_file = os.path.expanduser("~/.garminconnect/garmin_tokens.json")
    token_exists = os.path.exists(token_file)
    email_set = bool(os.getenv("GARMIN_EMAIL"))

    print_json(
        {
            "authenticated": _service._client is not None,
            "token_file": token_file,
            "token_file_exists": token_exists,
            "email_configured": email_set,
        }
    )
