"""APScheduler setup for periodic scraping and backup jobs."""

import asyncio
import logging
import subprocess
from datetime import date
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from garminconnect import Garmin

from garmin_mcp.scraper.collectors.activities import collect_recent_activities
from garmin_mcp.scraper.collectors.body import collect_body_for_date
from garmin_mcp.scraper.collectors.daily import collect_daily_range
from garmin_mcp.scraper.writer import upsert_activity, upsert_body, upsert_daily

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def scrape_daily_job(garmin: Garmin) -> None:
    """Scrape last 2 days of daily metrics (covers yesterday if today runs early)."""
    try:
        logger.info("Starting daily metrics scrape...")
        rows = await collect_daily_range(garmin, days=2)
        for row in rows:
            upsert_daily(row)
        logger.info(f"Daily scrape complete: {len(rows)} days")
    except Exception as e:
        logger.error(f"Daily scrape failed: {e}")


async def scrape_body_job(garmin: Garmin) -> None:
    """Scrape body metrics for yesterday and today."""
    try:
        logger.info("Starting body metrics scrape...")
        yesterday = (date.today() - __import__("datetime").timedelta(days=1)).isoformat()
        today = date.today().isoformat()

        for d in [yesterday, today]:
            row = await collect_body_for_date(garmin, d)
            upsert_body(row)

        logger.info("Body scrape complete")
    except Exception as e:
        logger.error(f"Body scrape failed: {e}")


async def scrape_activities_job(garmin: Garmin) -> None:
    """Scrape last 20 activities."""
    try:
        logger.info("Starting activities scrape...")
        rows = await collect_recent_activities(garmin, limit=20)
        for row in rows:
            upsert_activity(row)
        logger.info(f"Activities scrape complete: {len(rows)} activities")
    except Exception as e:
        logger.error(f"Activities scrape failed: {e}")


async def backup_job() -> None:
    """Backup DB to Google Drive via rclone."""
    try:
        logger.info("Starting backup job...")
        dump_path = f"/tmp/garmin_backup_{date.today().isoformat()}.sql.gz"

        # pg_dump → gzip
        await asyncio.to_thread(
            subprocess.run,
            [
                "bash",
                "-c",
                f"pg_dump $TIMESCALE_URL | gzip > {dump_path}",
            ],
            check=True,
        )

        # rclone copy to Google Drive
        await asyncio.to_thread(
            subprocess.run,
            [
                "rclone",
                "copy",
                dump_path,
                "gdrive-garmin:garmin-health-backup/",
            ],
            check=True,
        )

        # Cleanup
        Path(dump_path).unlink(missing_ok=True)
        logger.info(f"Backup complete: {dump_path} → Google Drive")
    except Exception as e:
        logger.error(f"Backup failed: {e}")


def register_jobs(garmin: Garmin) -> None:
    """Register all scraper and backup jobs."""
    scheduler.add_job(
        scrape_daily_job,
        CronTrigger(hour=6, minute=0),
        id="daily_scrape",
        replace_existing=True,
        args=[garmin],
    )

    scheduler.add_job(
        scrape_body_job,
        CronTrigger(hour=7, minute=0),
        id="body_scrape",
        replace_existing=True,
        args=[garmin],
    )

    scheduler.add_job(
        scrape_activities_job,
        CronTrigger(minute=0, hour="*/4"),
        id="activities_scrape",
        replace_existing=True,
        args=[garmin],
    )

    scheduler.add_job(
        backup_job,
        CronTrigger(hour=3, minute=0),
        id="backup",
        replace_existing=True,
    )

    logger.info("Scraper jobs registered")
