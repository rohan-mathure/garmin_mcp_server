# Developer Guide

## Project Layout

```
garmin_mcp_server/
├── pyproject.toml               # deps, entry point (garmin-mcp script)
├── .env.example                 # credential template
├── .mcp.json                    # Claude Code server registration
└── src/garmin_mcp/
    ├── __main__.py              # entry point; imports tools to trigger registration
    ├── server.py                # FastMCP("garmin") singleton
    ├── client.py                # Garmin client singleton + MFA bridge
    ├── models.py                # Pydantic models for ctx.elicit() schemas
    └── tools/
        ├── auth.py              # login, logout, status
        ├── daily.py             # daily health stats
        ├── activities.py        # activity list/detail/download
        ├── body.py              # body metrics + training metrics
        └── devices.py           # devices, gear, goals, badges
```

## Dependency Graph

```
models.py         ← no internal deps
server.py         ← no internal deps
client.py         ← models.py
tools/*.py        ← server.py, client.py
__main__.py       ← server.py + all tools/  (triggers @mcp.tool() registration)
```

No circular imports. `server.py` never imports from `tools/`.

## Adding a New Tool

1. Pick or create a file in `tools/` that matches the category.
2. Add the tool function:

```python
from garmin_mcp.client import ensure_authenticated
from garmin_mcp.server import mcp
from mcp.server.fastmcp import Context
import asyncio

@mcp.tool()
async def my_new_tool(ctx: Context, cdate: str = "") -> dict:
    """One-line description shown to Claude."""
    garmin = await ensure_authenticated(ctx)
    return await asyncio.to_thread(garmin.some_method, cdate)
```

3. If the tool is in a new file, import it in `__main__.py`:

```python
import garmin_mcp.tools.my_new_file  # noqa: F401
```

Rules:
- Always call `await ensure_authenticated(ctx)` first — never access `_client` directly.
- Always wrap blocking `garminconnect` calls with `asyncio.to_thread()`.
- Never `print()` to stdout — breaks the JSON-RPC stdio protocol. Use `logging` (goes to stderr).

## Auth & MFA Bridge

`garminconnect.login()` is **synchronous** and calls a `prompt_mfa()` callback if Garmin requires MFA. `ctx.elicit()` is **async**. The bridge in `client.py`:

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
                                       │
                                   returns OTP to login()
```

`code_ready.wait(timeout=120)` blocks the executor thread, not the event loop, so both sides run concurrently.

## Running Locally

```bash
# Start server (stdio mode — used by Claude)
uv run garmin-mcp

# Inspect tools interactively
npx @modelcontextprotocol/inspector uv run garmin-mcp

# Quick smoke test (check tools/list)
printf '{"jsonrpc":"2.0","method":"initialize","id":1,"params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"0"}}}\n{"jsonrpc":"2.0","method":"tools/list","id":2,"params":{}}\n' \
  | timeout 3 uv run garmin-mcp
```

## Key Libraries

| Library | Purpose |
|---------|---------|
| `garminconnect` | Garmin Connect API wrapper (131+ endpoints) |
| `curl_cffi` | TLS fingerprint impersonation — required to bypass Garmin's Cloudflare WAF |
| `mcp[cli]` | FastMCP framework (Anthropic) |
| `python-dotenv` | `.env` file loading |

## Garmin API Notes

- No official API keys — all access goes through the same SSO as the mobile app.
- Tokens stored at `~/.garminconnect/garmin_tokens.json`. Auto-refreshed before each request.
- Cloudflare WAF causes occasional rate limiting (`GarminConnectTooManyRequestsError`). The library adds randomized delays internally.
- Method names follow `snake_case` matching the `garminconnect` library. If a method fails, check the [library source](https://github.com/cyberjunky/python-garminconnect) for the current name — Garmin changes their API periodically.

## Error Handling

Tools surface errors as return strings rather than exceptions so Claude receives the message instead of an MCP error. Re-authentication is handled automatically in `ensure_authenticated()` by catching `GarminConnectAuthenticationError`, resetting the client, and retrying login.
