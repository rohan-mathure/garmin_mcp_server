"""Additional tests for db.init module coverage."""

from unittest.mock import MagicMock, patch

import psycopg2
import pytest

from garmin_mcp.db.init import init_db, wait_for_db


def test_wait_for_db_success():
    """Wait for DB succeeds on first try."""
    with patch("psycopg2.connect") as mock_connect:
        mock_connect.return_value = MagicMock()
        result = wait_for_db(timeout=10)
        assert result is True
        mock_connect.assert_called_once()


def test_wait_for_db_retries_then_succeeds():
    """Wait for DB retries until connection succeeds."""
    mock_conn = MagicMock()
    with patch("psycopg2.connect") as mock_connect:
        mock_connect.side_effect = [
            psycopg2.OperationalError("Connection refused"),
            psycopg2.OperationalError("Connection refused"),
            mock_conn,
        ]
        with patch("time.sleep"):  # Skip sleep for speed
            result = wait_for_db(timeout=30)
        assert result is True
        assert mock_connect.call_count == 3


def test_wait_for_db_timeout():
    """Wait for DB raises RuntimeError on timeout."""
    with patch("psycopg2.connect") as mock_connect, patch("time.sleep"):
        mock_connect.side_effect = psycopg2.OperationalError("Connection refused")
        with pytest.raises(RuntimeError, match="Database not ready"):
            wait_for_db(timeout=0.1)


def test_init_db_creates_tables(monkeypatch):
    """Init DB creates hypertables idempotently."""
    monkeypatch.setenv("TIMESCALE_URL", "postgresql://test:test@localhost/test")

    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

    with patch("psycopg2.connect", return_value=mock_conn):
        init_db()

    # Verify schema.sql was executed
    assert mock_cursor.execute.called
    # Check that CREATE EXTENSION was called
    calls = [str(call) for call in mock_cursor.execute.call_args_list]
    schema_calls = [c for c in calls if "CREATE EXTENSION" in c or "CREATE TABLE" in c]
    assert len(schema_calls) > 0


def test_init_db_with_invalid_url():
    """Init DB raises when TIMESCALE_URL invalid."""
    with (
        patch.dict("os.environ", {}, clear=True),
        pytest.raises(RuntimeError, match="TIMESCALE_URL"),
    ):
        init_db()
