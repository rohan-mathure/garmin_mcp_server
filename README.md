# Garmin Connect MCP Server

MCP server exposing Garmin Connect data to Claude. Supports MFA authentication and covers daily health, activities, body metrics, training, devices, and goals.

## Tools (28)

### Auth
| Tool | Description |
|------|-------------|
| `garmin_login` | Login with email/password. Handles MFA if required. |
| `garmin_logout` | Clear session and saved tokens. |
| `garmin_auth_status` | Check authentication state and token file. |

### Daily Health
| Tool | Description |
|------|-------------|
| `get_daily_summary` | Full daily snapshot: steps, calories, HR, distance. |
| `get_steps` | Step count and daily goal. |
| `get_heart_rate` | Resting HR, min/max, hourly timeline. |
| `get_stress` | Stress score and timeline. |
| `get_spo2` | Blood oxygen readings. |
| `get_sleep` | Sleep stages, score, and duration. |
| `get_calories` | Active, BMR, and total calorie breakdown. |

### Activities
| Tool | Description |
|------|-------------|
| `list_activities` | Paginated activity list, most recent first. |
| `get_activity` | Full activity detail by ID. |
| `get_activity_splits` | Lap/split data for an activity. |
| `get_activity_weather` | Weather recorded during an activity. |
| `download_activity_gpx` | GPX file content as string. |
| `get_activity_hr_zones` | Time spent in each HR zone. |

### Body & Training
| Tool | Description |
|------|-------------|
| `get_weight` | Weight and body fat % for a day. |
| `get_body_composition` | Body composition history over a date range. |
| `get_hrv` | Heart Rate Variability status and readings. |
| `get_vo2max` | VO2 max estimate. |
| `get_training_readiness` | Readiness score and contributing factors. |
| `get_intensity_minutes` | Weekly moderate and vigorous intensity minutes. |
| `get_race_predictions` | Predicted 5K/10K/half/marathon finish times. |

### Devices, Gear & Goals
| Tool | Description |
|------|-------------|
| `list_devices` | All connected Garmin devices. |
| `get_device_info` | Device settings by ID. |
| `list_gear` | Equipment (shoes, bikes, etc.) with mileage. |
| `list_personal_records` | All-time bests across activity types. |
| `list_badges` | Earned badges and completed challenges. |

## Setup

**1. Install dependencies**
```bash
uv sync
```

**2. Configure credentials**
```bash
cp .env.example .env
# Edit .env with your Garmin email and password
```

**3. Add to Claude Code**

Add `.mcp.json` (already in repo root) to Claude Code via `/mcp add` or restart Claude Code. The `garmin` server will appear automatically.

Alternatively, add to `~/.claude.json` for global access:
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

## Authentication

On first tool call, the server:
1. Reads `GARMIN_EMAIL` / `GARMIN_PASSWORD` from environment
2. If not set, prompts via Claude's elicitation UI
3. If Garmin requires MFA, Claude prompts for the OTP code

Tokens are cached at `~/.garminconnect/garmin_tokens.json` and auto-refreshed. Re-authentication is only needed if the refresh token expires (typically after months).

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)
- A Garmin Connect account
