"""Tests for scraper scheduler."""

from unittest.mock import AsyncMock, patch

import pytest

from garmin_mcp.scraper.scheduler import register_jobs


@pytest.mark.asyncio
async def test_register_jobs_adds_four_jobs():
    """Register jobs adds 4 scheduled tasks."""
    mock_garmin = AsyncMock()

    with patch("garmin_mcp.scraper.scheduler.scheduler") as mock_scheduler:
        register_jobs(mock_garmin)

    # Verify add_job called 4 times (daily, body, activities, backup)
    assert mock_scheduler.add_job.call_count == 4

    # Verify job IDs
    job_ids = [call[1]["id"] for call in mock_scheduler.add_job.call_args_list]
    assert "daily_scrape" in job_ids
    assert "body_scrape" in job_ids
    assert "activities_scrape" in job_ids
    assert "backup_job" in job_ids


@pytest.mark.asyncio
async def test_register_jobs_replace_existing():
    """Register jobs replaces existing jobs with same ID."""
    mock_garmin = AsyncMock()

    with patch("garmin_mcp.scraper.scheduler.scheduler") as mock_scheduler:
        register_jobs(mock_garmin)

        # Check replace_existing=True flag
        for call in mock_scheduler.add_job.call_args_list:
            assert call[1]["replace_existing"] is True


@pytest.mark.asyncio
async def test_jobs_receive_garmin_client():
    """Scheduled jobs receive garmin client as argument."""
    mock_garmin = AsyncMock()

    with patch("garmin_mcp.scraper.scheduler.scheduler") as mock_scheduler:
        register_jobs(mock_garmin)

        # Verify args contains garmin client
        for call in mock_scheduler.add_job.call_args_list:
            assert call[1]["args"] == (mock_garmin,)


@pytest.mark.asyncio
async def test_cron_triggers_configured():
    """Jobs have correct cron triggers."""
    mock_garmin = AsyncMock()

    with patch("garmin_mcp.scraper.scheduler.scheduler") as mock_scheduler:
        register_jobs(mock_garmin)

        calls = mock_scheduler.add_job.call_args_list
        # First call: daily_scrape @06:00
        assert "06" in str(calls[0][0][1]) or "hour=6" in str(calls[0][0][1])
        # Second call: body_scrape @07:00
        assert "07" in str(calls[1][0][1]) or "hour=7" in str(calls[1][0][1])
