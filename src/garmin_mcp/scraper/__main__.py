"""Scraper entry point — initialize DB, backfill, start scheduler."""

import asyncio
import logging
import sys

from garmin_mcp.db.init import init_db, wait_for_db
from garmin_mcp.scraper.auth_adapter import make_env_credential_provider
from garmin_mcp.scraper.collectors.activities import collect_recent_activities
from garmin_mcp.scraper.collectors.body import collect_body_for_date
from garmin_mcp.scraper.collectors.daily import collect_daily_range
from garmin_mcp.scraper.scheduler import backup_job, register_jobs, scheduler
from garmin_mcp.scraper.writer import upsert_activity, upsert_body, upsert_daily
from garmin_mcp.service import GarminService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def initial_backfill(service: GarminService) -> None:
    """Backfill last 7 days of metrics and last 50 activities on startup."""
    logger.info("Starting initial backfill...")

    try:
        cred_provider = make_env_credential_provider()
        garmin = await service.ensure_authenticated(cred_provider)

        # Daily metrics (last 7 days)
        logger.info("Backfilling daily metrics...")
        daily_rows = await collect_daily_range(garmin, days=7)
        for row in daily_rows:
            upsert_daily(row)
        logger.info(f"Backfilled {len(daily_rows)} days of daily metrics")

        # Body metrics (last 7 days)
        logger.info("Backfilling body metrics...")
        from datetime import date, timedelta

        for i in range(7):
            d = (date.today() - timedelta(days=i)).isoformat()
            try:
                row = await collect_body_for_date(garmin, d)
                upsert_body(row)
            except Exception:
                pass  # Body data may be sparse, don't fail
        logger.info("Backfilled body metrics")

        # Activities (last 50)
        logger.info("Backfilling activities...")
        activity_rows = await collect_recent_activities(garmin, limit=50)
        for row in activity_rows:
            upsert_activity(row)
        logger.info(f"Backfilled {len(activity_rows)} activities")

    except Exception as e:
        logger.error(f"Initial backfill failed: {e}")
        raise


async def main() -> None:
    """Main scraper loop."""
    try:
        # Wait for DB to be ready
        logger.info("Waiting for TimescaleDB...")
        wait_for_db(timeout=60)

        # Initialize DB (idempotent)
        logger.info("Initializing database...")
        init_db()

        # Authenticate and set up service
        service = GarminService()
        logger.info("Authenticating with Garmin...")
        cred_provider = make_env_credential_provider()
        garmin = await service.ensure_authenticated(cred_provider)

        # Backfill on startup
        await initial_backfill(service)

        # Register and start scheduler
        register_jobs(garmin)
        scheduler.start()

        logger.info("Scraper ready. Scheduler running.")

        # Keep running
        try:
            while True:
                await asyncio.sleep(3600)
        except (KeyboardInterrupt, SystemExit):
            logger.info("Shutting down...")
            scheduler.shutdown()

    except Exception as e:
        logger.error(f"Scraper startup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
