"""Tests for trends MCP tools."""

import os
from unittest.mock import MagicMock, patch

import psycopg2
import pytest

from garmin_mcp.tools.trends import (
    get_health_summary,
    get_metric_trend,
    query_health_db,
)


@pytest.fixture
def mock_cursor():
    """Mock database cursor."""
    return MagicMock()


@pytest.fixture
def mock_conn(mock_cursor):
    """Mock database connection."""
    conn = MagicMock()
    conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
    conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    conn.__enter__ = MagicMock(return_value=conn)
    conn.__exit__ = MagicMock(return_value=False)
    return conn


def test_get_metric_trend_steps(monkeypatch, mock_conn, mock_cursor):
    """Get time-series for steps metric."""
    monkeypatch.setenv("TIMESCALE_URL", "postgresql://test:test@localhost/test")
    mock_cursor.fetchall.return_value = [
        ("2025-05-01", 10000),
        ("2025-05-02", 8500),
        ("2025-05-03", 12000),
    ]

    with patch("psycopg2.connect", return_value=mock_conn):
        result = get_metric_trend("steps", days=30)

    assert len(result) == 3
    assert result[0]["date"] == "2025-05-01"
    assert result[0]["value"] == 10000


def test_get_metric_trend_invalid_metric(monkeypatch):
    """Get metric trend rejects invalid metric name."""
    monkeypatch.setenv("TIMESCALE_URL", "postgresql://test:test@localhost/test")

    result = get_metric_trend("invalid_metric", days=30)

    assert len(result) == 1
    assert "error" in result[0]


def test_get_metric_trend_no_timescale_url():
    """Get metric trend raises when TIMESCALE_URL not set."""
    with patch.dict(os.environ, {}, clear=True):
        result = get_metric_trend("steps")
        assert "error" in result[0]


def test_query_health_db_select(monkeypatch, mock_conn, mock_cursor):
    """Query health DB with SELECT statement."""
    monkeypatch.setenv("TIMESCALE_URL", "postgresql://test:test@localhost/test")
    mock_cursor.description = [("date",), ("steps",)]
    mock_cursor.fetchall.return_value = [("2025-05-03", 10000)]

    with patch("psycopg2.connect", return_value=mock_conn):
        result = query_health_db("SELECT date, steps FROM daily_metrics LIMIT 1")

    assert len(result) == 1
    assert result[0]["date"] == "2025-05-03"
    assert result[0]["steps"] == 10000


def test_query_health_db_with_cte(monkeypatch, mock_conn, mock_cursor):
    """Query health DB with CTE (WITH clause)."""
    monkeypatch.setenv("TIMESCALE_URL", "postgresql://test:test@localhost/test")
    mock_cursor.description = [("total",)]
    mock_cursor.fetchall.return_value = [(42,)]

    with patch("psycopg2.connect", return_value=mock_conn):
        result = query_health_db(
            "WITH data AS (SELECT COUNT(*) as total FROM daily_metrics) SELECT * FROM data"
        )

    assert len(result) == 1
    assert result[0]["total"] == 42


def test_query_health_db_rejects_insert(monkeypatch):
    """Query health DB rejects INSERT statements."""
    monkeypatch.setenv("TIMESCALE_URL", "postgresql://test:test@localhost/test")

    result = query_health_db("INSERT INTO daily_metrics VALUES (...)")

    assert len(result) == 1
    assert "error" in result[0]
    assert "Only SELECT/WITH" in result[0]["error"]


def test_query_health_db_rejects_update(monkeypatch):
    """Query health DB rejects UPDATE statements."""
    monkeypatch.setenv("TIMESCALE_URL", "postgresql://test:test@localhost/test")

    result = query_health_db("UPDATE daily_metrics SET steps = 0")

    assert len(result) == 1
    assert "error" in result[0]


def test_query_health_db_handles_error(monkeypatch, mock_conn, mock_cursor):
    """Query health DB returns error dict on exception."""
    monkeypatch.setenv("TIMESCALE_URL", "postgresql://test:test@localhost/test")
    mock_cursor.execute.side_effect = psycopg2.OperationalError("Connection failed")

    with patch("psycopg2.connect", return_value=mock_conn):
        result = query_health_db("SELECT * FROM daily_metrics")

    assert len(result) == 1
    assert "error" in result[0]


def test_get_health_summary(monkeypatch, mock_conn, mock_cursor):
    """Get aggregated health summary."""
    monkeypatch.setenv("TIMESCALE_URL", "postgresql://test:test@localhost/test")
    mock_cursor.fetchone.side_effect = [
        (10000, 12000, 60, 8.5, 30, 98.5, 30),  # daily
        (75.5, 45.0, 35.0, 85),  # body
        (15, 75.2, 120, 5),  # activities
    ]
    mock_cursor.description = [
        ("avg_steps",),
        ("max_steps",),
        ("avg_resting_hr",),
        ("avg_sleep_hours",),
        ("avg_stress",),
        ("avg_spo2",),
        ("days_with_data",),
    ]

    with patch("psycopg2.connect", return_value=mock_conn):
        result = get_health_summary(days=30)

    assert result["period_days"] == 30
    assert "daily" in result
    assert "body" in result
    assert "activities" in result
    assert result["daily"]["avg_steps"] == 10000


def test_get_health_summary_handles_missing_data(monkeypatch, mock_conn, mock_cursor):
    """Get health summary handles missing data gracefully."""
    monkeypatch.setenv("TIMESCALE_URL", "postgresql://test:test@localhost/test")
    mock_cursor.fetchone.side_effect = [None, None, None]

    with patch("psycopg2.connect", return_value=mock_conn):
        result = get_health_summary(days=30)

    assert result["daily"] == {}
    assert result["body"] == {}
    assert result["activities"] == {}


def test_get_health_summary_error_handling(monkeypatch, mock_conn, mock_cursor):
    """Get health summary returns error dict on exception."""
    monkeypatch.setenv("TIMESCALE_URL", "postgresql://test:test@localhost/test")
    mock_cursor.execute.side_effect = psycopg2.DatabaseError("Query failed")

    with patch("psycopg2.connect", return_value=mock_conn):
        result = get_health_summary(days=30)

    assert "error" in result
