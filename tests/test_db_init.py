"""Tests for database initialization module."""

from __future__ import annotations

from unittest.mock import MagicMock

import psycopg2
import pytest

from garmin_mcp.db.init import get_db_url, init_db, wait_for_db


def test_get_db_url_from_env(monkeypatch):
    """get_db_url returns env var when set."""
    monkeypatch.setenv("TIMESCALE_URL", "postgresql://user:pass@localhost:5432/garmin")
    assert get_db_url() == "postgresql://user:pass@localhost:5432/garmin"


def test_get_db_url_raises_when_not_set(monkeypatch):
    """get_db_url raises if env var not set."""
    monkeypatch.delenv("TIMESCALE_URL", raising=False)
    with pytest.raises(RuntimeError, match="TIMESCALE_URL env var not set"):
        get_db_url()


def test_wait_for_db_success(monkeypatch, mocker):
    """wait_for_db succeeds when DB is ready."""
    monkeypatch.setenv("TIMESCALE_URL", "postgresql://user:pass@localhost:5432/garmin")

    mock_conn = MagicMock()
    mocker.patch("psycopg2.connect", return_value=mock_conn)

    wait_for_db()  # Should not raise
    # Verify close was called
    mock_conn.close.assert_called_once()


def test_wait_for_db_retries_then_succeeds(monkeypatch, mocker):
    """wait_for_db retries on connection failure then succeeds."""
    monkeypatch.setenv("TIMESCALE_URL", "postgresql://user:pass@localhost:5432/garmin")

    mock_conn = MagicMock()
    # First call raises, second succeeds
    mocker.patch(
        "psycopg2.connect",
        side_effect=[
            psycopg2.OperationalError("Connection refused"),
            mock_conn,
        ],
    )

    wait_for_db(timeout=10)  # Should succeed after retry
    mock_conn.close.assert_called_once()


def test_wait_for_db_timeout(monkeypatch, mocker):
    """wait_for_db raises after timeout."""
    monkeypatch.setenv("TIMESCALE_URL", "postgresql://user:pass@localhost:5432/garmin")

    mocker.patch(
        "psycopg2.connect",
        side_effect=psycopg2.OperationalError("Connection refused"),
    )

    with pytest.raises(RuntimeError, match="TimescaleDB not ready after"):
        wait_for_db(timeout=1)


def test_init_db_creates_tables(monkeypatch, mocker):
    """init_db reads schema.sql and executes it."""
    monkeypatch.setenv("TIMESCALE_URL", "postgresql://user:pass@localhost:5432/garmin")

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=None)
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=None)

    mocker.patch("psycopg2.connect", return_value=mock_conn)

    # Mock the schema.sql file read
    schema_content = "CREATE TABLE test (id INT);"
    mocker.patch(
        "pathlib.Path.read_text",
        return_value=schema_content,
    )

    init_db()

    # Verify execute was called with schema SQL
    mock_cursor.execute.assert_called_once_with(schema_content)
    # Verify commit was called
    mock_conn.commit.assert_called_once()
