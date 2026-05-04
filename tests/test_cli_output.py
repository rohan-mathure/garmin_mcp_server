"""Tests for CLI output formatting."""

import json
from io import StringIO
from unittest.mock import patch

from garmin_mcp.cli.output import print_error, print_json, print_success


def test_print_json_dict():
    """Print dict as formatted JSON."""
    data = {"key": "value", "number": 42}
    with patch("sys.stdout", new_callable=StringIO) as mock_out:
        print_json(data)
        output = mock_out.getvalue()
        assert json.loads(output) == data


def test_print_json_list():
    """Print list as formatted JSON."""
    data = [1, 2, 3]
    with patch("sys.stdout", new_callable=StringIO) as mock_out:
        print_json(data)
        output = mock_out.getvalue()
        assert json.loads(output) == data


def test_print_json_none():
    """Print None as null JSON."""
    with patch("sys.stdout", new_callable=StringIO) as mock_out:
        print_json(None)
        output = mock_out.getvalue()
        assert json.loads(output) is None


def test_print_success():
    """Print success message."""
    with patch("sys.stderr", new_callable=StringIO) as mock_err:
        print_success("All good")
        output = mock_err.getvalue()
        assert "All good" in output


def test_print_error():
    """Print error message."""
    with patch("sys.stderr", new_callable=StringIO) as mock_err:
        print_error("Something failed")
        output = mock_err.getvalue()
        assert "Something failed" in output
