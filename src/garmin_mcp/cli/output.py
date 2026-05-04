"""Rich console helpers for CLI output."""

import json
import sys

from rich.console import Console

console = Console()
error_console = Console(file=sys.stderr)


def print_json(data):
    """Print data as formatted JSON."""
    console.print_json(json.dumps(data, default=str))


def print_table(data: list[dict], title: str = None):
    """Print list of dicts as table."""
    if not data:
        print_error("No data")
        return
    from rich.table import Table

    table = Table(title=title)
    cols = data[0].keys()
    for col in cols:
        table.add_column(col)
    for row in data:
        table.add_row(*[str(row.get(col, "")) for col in cols])
    console.print(table)


def print_success(msg: str):
    """Print success message."""
    console.print(f"[green]✓ {msg}[/green]")


def print_error(msg: str):
    """Print error message."""
    error_console.print(f"[red]✗ {msg}[/red]")
