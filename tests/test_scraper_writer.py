"""Tests for scraper writer (upsert functions)."""

import os
from unittest.mock import MagicMock, patch

import pytest

from garmin_mcp.scraper.writer import (
    upsert_activity,
    upsert_body,
    upsert_daily,
)


@pytest.fixture
def mock_conn():
    """Mock database connection."""
    cursor = MagicMock()
    conn = MagicMock()
    conn.cursor.return_value.__enter__ = MagicMock(return_value=cursor)
    conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    return conn, cursor


def test_upsert_daily(monkeypatch, mock_conn):
    """Upsert daily metrics row."""
    monkeypatch.setenv("TIMESCALE_URL", "postgresql://test:test@localhost/test")
    conn, cursor = mock_conn

    with patch("psycopg2.connect", return_value=conn):
        row = {
            "date": "2025-05-03",
            "steps": 10000,
            "calories_active": 500,
            "resting_hr": 60,
        }
        upsert_daily(row)

    assert cursor.execute.called
    # Verify INSERT was called
    call_args = cursor.execute.call_args
    assert "INSERT INTO daily_metrics" in call_args[0][0]
    assert call_args[0][1] == row


def test_upsert_body(monkeypatch, mock_conn):
    """Upsert body metrics row."""
    monkeypatch.setenv("TIMESCALE_URL", "postgresql://test:test@localhost/test")
    conn, cursor = mock_conn

    with patch("psycopg2.connect", return_value=conn):
        row = {
            "date": "2025-05-03",
            "weight_kg": 75.5,
            "vo2max": 45.0,
        }
        upsert_body(row)

    assert cursor.execute.called
    call_args = cursor.execute.call_args
    assert "INSERT INTO body_metrics" in call_args[0][0]


def test_upsert_activity(monkeypatch, mock_conn):
    """Upsert activity row."""
    monkeypatch.setenv("TIMESCALE_URL", "postgresql://test:test@localhost/test")
    conn, cursor = mock_conn

    with patch("psycopg2.connect", return_value=conn):
        row = {
            "activity_id": 123456,
            "start_time": "2025-05-03T10:00:00+00:00",
            "activity_type": "running",
            "distance_meters": 5000,
        }
        upsert_activity(row)

    assert cursor.execute.called
    call_args = cursor.execute.call_args
    assert "INSERT INTO activities" in call_args[0][0]


def test_upsert_without_timescale_url():
    """Upsert raises RuntimeError when TIMESCALE_URL not set."""
    with patch.dict(os.environ, {}, clear=True), pytest.raises(RuntimeError, match="TIMESCALE_URL"):
        upsert_daily({"date": "2025-05-03"})
