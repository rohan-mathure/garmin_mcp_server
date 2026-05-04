# Garmin Connect — MCP Server, CLI, and Trending Data Pipeline

Garmin Connect data exposed to Claude via MCP, plus self-contained CLI and local time-series scraper with TimescaleDB.

## What's Included

### 1. MCP Server (`garmin-mcp`)
28 tools for querying Garmin Connect live data:
- **Auth** (3): login, logout, status
- **Daily health** (7): summary, steps, heart-rate, stress, spo2, sleep, calories
- **Activities** (6): list, get, splits, weather, gpx, hr-zones
- **Body & training** (7): weight, composition, hrv, vo2max, training-readiness, intensity-minutes, race-predictions
- **Devices** (5): list, info, gear, records, badges

### 2. CLI (`garmin-cli`)
All 28 tools as typer subcommands. Same auth as MCP (env vars + interactive fallback).
```bash
garmin-cli daily steps --date 2025-04-15
garmin-cli activities list --limit 10
garmin-cli body vo2max
```

### 3. Local Trending Data Pipeline
**Architecture:**
- **Scraper** (Docker): APScheduler runs 4 periodic jobs
  - daily metrics @06:00 (last 2 days, idempotent)
  - body metrics @07:00 (yesterday + today)
  - activities every 4h (last 20)
  - backup @03:00 (pg_dump → gzip → rclone to Google Drive)
- **TimescaleDB** (Docker): 3 hypertables for persistent storage
  - daily_metrics (date-partitioned, 13 columns)
  - body_metrics (date-partitioned, 5 columns)
  - activities (start_time-partitioned, 12 columns)
- **MCP Trends Tools** (3): query local DB via Claude
  - `get_metric_trend(metric, days)` — time-series data
  - `query_health_db(sql)` — SELECT-only SQL passthrough
  - `get_health_summary(days)` — aggregated stats

**Backup:** pg_dump compressed to Google Drive via rclone (15GB free, one-time auth on host, then headless).

---

## Setup

### Option 1: MCP Server Only
```bash
uv sync
cp .env.example .env
# Edit .env with GARMIN_EMAIL and GARMIN_PASSWORD
```

Add to Claude Code via `/mcp add` or `~/.claude.json`:
```json
{
  "mcpServers": {
    "garmin": {
      "command": "uv",
      "args": ["--directory", "/path/to/garmin_mcp_server", "run", "garmin-mcp"]
    }
  }
}
```

### Option 2: CLI Only
```bash
uv sync
export GARMIN_EMAIL=your-email
export GARMIN_PASSWORD=your-password
uv run garmin-cli --help
```

### Option 3: Full Stack (Docker + Scraper + Trends)

**Prerequisites:**
- Docker Compose v2
- Garmin credentials in `.env`
- (Optional) Google Drive backup: one-time `rclone config` on host

**Start:**
```bash
docker compose up --build
```

Scraper will:
1. Wait for TimescaleDB to be ready
2. Create 3 hypertables
3. Backfill last 7 days of daily/body metrics, last 50 activities
4. Register APScheduler jobs
5. Keep running (logs via `docker compose logs scraper`)

**Query locally:**
```bash
export TIMESCALE_URL=postgresql://garmin:garmin@localhost:5432/garmin
uv run garmin-mcp  # MCP server queries local DB via trends tools
```

---

## Architecture: Shared Backend

All three interfaces (MCP, CLI, scraper) use the same `GarminService` class, which is auth-agnostic via callback protocols:
- **MCP adapter**: `ctx.elicit()` for credentials/MFA, threading bridge for MFA from executor thread
- **CLI adapter**: `typer.prompt()` for env-var fallback
- **Scraper adapter**: env-only (raises if missing, no interactive fallback)

All 28 Garmin tools unchanged. Trends tools (@mcp.tool) added to existing server without modifying tool modules.

---

## Authentication

### MCP / CLI
1. Read `GARMIN_EMAIL` / `GARMIN_PASSWORD` from env
2. If missing, prompt (MCP via ctx.elicit, CLI via typer.prompt)
3. If MFA required, prompt for OTP (120s timeout)

Tokens cached at `~/.garminconnect/garmin_tokens.json`, auto-refreshed.

### Scraper
Env vars only (no interactive prompt). Raises RuntimeError if missing.

---

## Docker Compose

**Services:**
- `timescaledb`: PostgreSQL 16 + TimescaleDB extension
  - Port: 5432
  - DB: garmin / User: garmin / Pass: garmin
  - Volume: ts_data (persists across restarts)
  - Healthcheck: pg_isready
- `scraper`: Python 3.12 scraper with uv
  - Env vars: GARMIN_EMAIL, GARMIN_PASSWORD, TIMESCALE_URL
  - Volumes: rclone config (read-only, for Google Drive backup)
  - Depends on timescaledb healthcheck

**Data Persistence:**
- Named volume `ts_data` mounted at `/var/lib/postgresql/data` in container
- On host: inspect with `docker volume ls` and `docker volume inspect garmin_mcp_server_ts_data`
- Survives `docker compose down` (preserves data)

**Backup:**
Set up once on host:
```bash
rclone config  # Add remote "gdrive-garmin" (type: drive, OAuth once)
rclone mkdir "gdrive-garmin:garmin-health-backup"
```

Mount rclone config into scraper:
```yaml
volumes:
  - ${HOME}/.config/rclone:/root/.config/rclone:ro
```

Scraper backup job runs daily @03:00, uploading `garmin_backup_YYYY-MM-DD.sql.gz` to Google Drive.

---

## Tools Reference

### Trends Tools (query local TimescaleDB)

**get_metric_trend**
```
metric: str (steps, calories_active, resting_hr, weight_kg, vo2max, etc.)
days: int (default 30)
→ list[dict] with date and value
```

**query_health_db**
```
sql: str (SELECT/WITH only, no INSERT/UPDATE/DELETE)
→ list[dict] rows from daily_metrics, body_metrics, or activities
```

**get_health_summary**
```
days: int (default 30)
→ dict with aggregated stats:
  daily: {avg_steps, max_steps, avg_resting_hr, avg_sleep_hours, avg_stress, avg_spo2, days_with_data}
  body: {avg_weight_kg, avg_vo2max, avg_hrv, avg_readiness}
  activities: {total_activities, total_km, avg_activity_hr, activity_types}
```

### Original 28 Tools
See above for full list or `garmin-cli --help` for CLI equivalents.

---

## Development

**Install & test:**
```bash
uv sync --all-extras
uv run pytest --cov=src/garmin_mcp --cov-fail-under=90
```

**Run MCP server locally:**
```bash
uv run garmin-mcp
```

**Run CLI:**
```bash
uv run garmin-cli auth login
uv run garmin-cli daily steps
```

**Start scraper (without Docker):**
```bash
export TIMESCALE_URL=postgresql://garmin:garmin@localhost:5432/garmin
uv run python -m garmin_mcp.scraper
```

---

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)
- Garmin Connect account
- Docker Compose v2 (for scraper stack)
- PostgreSQL/TimescaleDB (Docker or local, for scraper)

---

## License & Attribution

Builds on [`garminconnect`](https://github.com/cyberjunky/python-garminconnect) library.
