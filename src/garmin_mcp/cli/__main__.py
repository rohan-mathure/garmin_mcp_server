"""CLI app — all 28 Garmin tools as subcommands."""

import typer

from garmin_mcp.cli.commands import activities, auth, body, daily, devices

app = typer.Typer(name="garmin-cli", help="Garmin Connect CLI")

app.add_typer(auth.app, name="auth")
app.add_typer(daily.app, name="daily")
app.add_typer(activities.app, name="activities")
app.add_typer(body.app, name="body")
app.add_typer(devices.app, name="devices")


if __name__ == "__main__":
    app()
