"""Tests for CLI output formatting."""

import json

from garmin_mcp.cli.output import print_json, print_success, print_table


def test_print_json_dict(capsys):
    """Print dict as formatted JSON."""
    data = {"key": "value", "number": 42}
    print_json(data)
    captured = capsys.readouterr()
    assert captured.out  # Rich formats JSON output


def test_print_json_list(capsys):
    """Print list as formatted JSON."""
    data = [1, 2, 3]
    print_json(data)
    captured = capsys.readouterr()
    assert captured.out


def test_print_json_none(capsys):
    """Print None as null JSON."""
    print_json(None)
    captured = capsys.readouterr()
    assert captured.out


def test_print_success(capsys):
    """Print success message."""
    print_success("All good")
    captured = capsys.readouterr()
    assert "All good" in captured.out


def test_print_table_with_data(capsys):
    """Print table with data."""
    data = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
    ]
    print_table(data, title="People")
    captured = capsys.readouterr()
    assert "Alice" in captured.out or "name" in captured.out
