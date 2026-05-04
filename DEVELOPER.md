# Developer Guide

## Project Layout

```
garmin_mcp_server/
├── pyproject.toml                 # deps, entry points (garmin-mcp, garmin-cli)
├── docker-compose.yml             # TimescaleDB + scraper stack
├── docker/scraper/Dockerfile      # scraper container
├── .env.example                   # credential template
├── .mcp.json                      # Claude Code server registration
├── src/garmin_mcp/
│   ├── __main__.py                # MCP entry; imports all tools
│   ├── server.py                  # FastMCP("garmin") singleton
│   ├── service.py                 # GarminService + auth protocols
│   ├── client.py                  # MCP adapter (ctx.elicit + threading bridge)
│   ├── models.py                  # Pydantic models for elicit schemas
│   ├── tools/
│   │   ├── auth.py
│   │   ├── daily.py
│   │   ├── activities.py
│   │   ├── body.py
│   │   ├── devices.py
│   │   └── trends.py              # NEW: TimescaleDB time-series tools
│   ├── cli/                       # NEW: typer CLI
│   │   ├── __main__.py
│   │   ├── auth_adapter.py        # env + typer.prompt()
│   │   ├── output.py              # rich console helpers
│   │   └── commands/
│   │       ├── auth.py, daily.py, activities.py, body.py, devices.py
│   ├── db/                        # NEW: TimescaleDB schema + init
│   │   ├── init.py
│   │   └── schema.sql
│   └── scraper/                   # NEW: APScheduler data pipeline
│       ├── __main__.py
│       ├── auth_adapter.py
│       ├── writer.py              # upsert functions
│       ├── scheduler.py           # APScheduler jobs
│       └── collectors/
│           ├── daily.py, body.py, activities.py
└── tests/
    ├── conftest.py
    ├── test_client.py
    ├── test_service.py            # NEW
    ├── test_db_init.py            # NEW
    ├── test_tools_*.py
```

## Architecture: Shared Backend (NEW)

All three interfaces use the same **`GarminService`** class via callback-based auth:

```
GarminService (service.py)
    ├─ CredentialProvider protocol (async callback for email/password)
    └─ MFAProvider protocol (sync callback for OTP code)

Adapters:
    ├─ client.py → MCP adapter: ctx.elicit() + threading bridge
    ├─ cli/auth_adapter.py → CLI adapter: env + typer.prompt()
    └─ scraper/auth_adapter.py → env-only (raises if missing)

All 28 tools untouched
+ 3 new trends tools (query TimescaleDB via psycopg2)
```

**Why:** Removes MCP `ctx` dependency from auth logic. MCP, CLI, and scraper all share the same business logic but inject different credential/MFA providers.

## Dependency Graph

```
service.py        ← no internal deps (pure auth logic)
models.py         ← no internal deps
server.py         ← no internal deps
client.py         ← service.py, models.py
tools/*.py        ← server.py, client.py
db/init.py        ← no internal deps
scraper/*         ← service.py, db/init.py, tools via garminconnect
cli/*             ← service.py
__main__.py       ← server.py + all tools/ (triggers @mcp.tool() registration)
```

No circular imports. `server.py` never imports from `tools/`, `cli/`, or `scraper/`.

## Adding a New Tool (unchanged pattern)

1. Add to `tools/<category>.py`:

```python
from garmin_mcp.client import ensure_authenticated
from garmin_mcp.server import mcp
from mcp.server.fastmcp import Context
import asyncio

@mcp.tool()
async def my_new_tool(ctx: Context, cdate: str = "") -> dict:
    """One-line description."""
    garmin = await ensure_authenticated(ctx)
    return await asyncio.to_thread(garmin.some_method, cdate)
```

2. Import in `__main__.py`:

```python
import garmin_mcp.tools.my_new_file  # noqa: F401
```

Rules:
- Always call `await ensure_authenticated(ctx)` — never access `_client` directly
- Wrap blocking `garminconnect` calls with `asyncio.to_thread()`
- No `print()` to stdout (breaks JSON-RPC). Use `logging` (goes to stderr)

## Adding a New CLI Command

1. Add to `cli/commands/<group>.py`:

```python
import typer
from garmin_mcp.cli.auth_adapter import get_garmin_client
from garmin_mcp.cli.output import print_json, print_error

app = typer.Typer(help="Command group")

@app.command()
def my_command(date: str = typer.Option("", "--date", "-d")):
    """Command description."""
    async def _run():
        try:
            garmin = await get_garmin_client()
            return await asyncio.to_thread(garmin.some_method, date or date.today().isoformat())
        except Exception as e:
            print_error(str(e))
            raise typer.Exit(1)
    print_json(asyncio.run(_run()))
```

2. Register in `cli/__main__.py`:

```python
from garmin_mcp.cli.commands import my_group
app.add_typer(my_group.app, name="my-group")
```

## Adding a Scraper Collector

1. Create `scraper/collectors/<type>.py`:

```python
import asyncio
from garminconnect import Garmin

async def collect_<type>_for_date(garmin: Garmin, d: str) -> dict:
    """Fetch and normalize <type> data for a single date."""
    raw = await asyncio.to_thread(garmin.get_<method>, d)
    return {
        "date": d,
        "field1": raw.get("key1"),
        "field2": raw.get("key2"),
    }
```

2. Register job in `scraper/scheduler.py`:

```python
async def scrape_<type>_job(garmin: Garmin) -> None:
    """Scrape <type> data."""
    logger.info("Starting <type> scrape...")
    # ... collect and upsert
    logger.info("<type> scrape complete")

scheduler.add_job(
    scrape_<type>_job,
    CronTrigger(hour=<H>, minute=<M>),
    id="<type>_scrape",
    replace_existing=True,
    args=[garmin],
)
```

## Auth & MFA Bridge (unchanged)

`garminconnect.login()` is sync and calls `prompt_mfa()` if needed. `ctx.elicit()` is async. The bridge in `client.py`:

```
event loop thread                 executor thread
─────────────────                 ───────────────
run_in_executor(login) ──────────► garmin.login()
                                       │ (MFA needed)
                                       ▼
                         prompt_mfa() called
                              │
call_soon_threadsafe ◄────────┘
       │
       ▼
  elicit() runs on event loop
       │
       ▼
  user enters OTP
       │
  code_ready.set() ──────────────► code_ready.wait() unblocks
```

## Running Locally

### MCP Server
```bash
uv run garmin-mcp
```

### CLI
```bash
uv run garmin-cli daily steps
uv run garmin-cli activities list
```

### Scraper (without Docker)
Requires local TimescaleDB or Docker container running:
```bash
export TIMESCALE_URL=postgresql://garmin:garmin@localhost:5432/garmin
uv run python -m garmin_mcp.scraper
```

### Full Docker Stack
```bash
docker compose up --build
docker compose logs scraper  # Monitor scraper
docker compose exec timescaledb psql -U garmin -d garmin -c "\dt"  # Verify tables
```

## Testing & Linting

### Setup dev dependencies
```bash
uv sync --all-extras
```

### Linting
```bash
uv run ruff check src/ tests/
uv run ruff format src/ tests/
```

### Running Tests
```bash
uv run pytest                      # Full suite with coverage
uv run pytest --no-cov             # Faster iteration
uv run pytest -k "test_service" -v # Single test by keyword
```

Coverage enforced at 90% via CI. Tests for new modules (scraper, cli, db, trends) needed for full coverage.

### CI
GitHub Actions (`.github/workflows/ci.yml`) runs on every push to `main` and PRs:
1. **Lint** — `ruff check` + `ruff format --check`
2. **Test** — `pytest --cov=src/garmin_mcp --cov-fail-under=90`

## Mock Pattern for Tools (unchanged)

Test new tools:

```python
async def test_my_tool(mock_garmin, mock_ctx, mocker, patch_to_thread):
    mocker.patch(
        "garmin_mcp.tools.<module>.ensure_authenticated",
        new=AsyncMock(return_value=mock_garmin),
    )
    result = await my_tool(mock_ctx, ...)
    assert result == ...
```

## Key Libraries

| Library | Purpose |
|---------|---------|
| `garminconnect` | Garmin Connect API wrapper (131+ endpoints) |
| `curl_cffi` | TLS fingerprint impersonation (bypass Cloudflare WAF) |
| `mcp[cli]` | FastMCP framework (Anthropic) |
| `typer` | CLI framework (new) |
| `rich` | Rich console output (new) |
| `apscheduler` | Periodic job scheduling (new) |
| `psycopg2-binary` | PostgreSQL driver (new) |
| `python-dotenv` | `.env` file loading |

## TimescaleDB Schema (NEW)

Located in `src/garmin_mcp/db/schema.sql`. Three hypertables:

| Table | Dimensions | Columns | Purpose |
|-------|-----------|---------|---------|
| `daily_metrics` | date | 13 (steps, HR, stress, sleep, spo2, etc.) | Daily health rollups |
| `body_metrics` | date | 5 (weight, fat%, HRV, VO2, readiness) | Body composition |
| `activities` | start_time | 12 (type, distance, pace, HR, power, etc.) | Workout details |

Indexes on `date` (daily/body) and `activity_type, start_time DESC` (activities).

All timestamps use `TIMESTAMPTZ` for UTC normalization. `scraped_at` defaults to `NOW()`.

## Garmin API Notes (unchanged)

- No official API keys — mirrors mobile app auth
- Tokens stored at `~/.garminconnect/garmin_tokens.json`, auto-refreshed
- Cloudflare WAF causes rate limiting. Library adds randomized delays
- Method names in `garminconnect` change periodically — check [library source](https://github.com/cyberjunky/python-garminconnect) if a call fails

## Error Handling (updated)

### MCP Tools
Surface errors as return strings (Claude receives the message):
```python
try:
    return await asyncio.to_thread(garmin.some_method)
except Exception as e:
    return {"error": str(e)}
```

### CLI Commands
Catch exceptions, use `print_error()`, exit with code 1:
```python
except Exception as e:
    print_error(str(e))
    raise typer.Exit(1)
```

### Scraper
Log errors but don't fail the entire job. Continues to next item:
```python
for item in items:
    try:
        await collect_and_upsert(item)
    except Exception as e:
        logger.warning(f"Failed for {item}: {e}")
```

### Re-authentication
Handled automatically in `GarminService.ensure_authenticated()`: catches `GarminConnectAuthenticationError`, resets client, retries login once.
