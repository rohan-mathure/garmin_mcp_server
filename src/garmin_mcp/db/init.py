"""Database initialization — create tables and indexes."""

import logging
import os
import time
from pathlib import Path

import psycopg2

logger = logging.getLogger(__name__)


def get_db_url() -> str:
    """Get TimescaleDB connection URL from env or raise."""
    url = os.environ.get("TIMESCALE_URL")
    if not url:
        raise RuntimeError(
            "TIMESCALE_URL env var not set. "
            "Expected: postgresql://user:pass@host:port/dbname"
        )
    return url


def wait_for_db(timeout: int = 60) -> None:
    """Wait for TimescaleDB to be ready with retry loop."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            conn = psycopg2.connect(get_db_url())
            conn.close()
            logger.info("TimescaleDB is ready")
            return
        except psycopg2.OperationalError as e:
            wait_time = 2
            remaining = timeout - (time.time() - start)
            if remaining > 0:
                logger.debug(
                    f"DB not ready yet ({e}), retrying in {wait_time}s... "
                    f"({remaining:.0f}s remaining)"
                )
                time.sleep(wait_time)
            else:
                raise

    raise RuntimeError(f"TimescaleDB not ready after {timeout}s")


def init_db() -> None:
    """Create tables and indexes from schema.sql. Idempotent."""
    logger.info("Initializing TimescaleDB...")

    schema_sql = (Path(__file__).parent / "schema.sql").read_text()

    with psycopg2.connect(get_db_url()) as conn:
        with conn.cursor() as cur:
            cur.execute(schema_sql)
        conn.commit()

    logger.info("Database initialization complete")
