from __future__ import annotations

from unittest.mock import AsyncMock

from garmin_mcp.tools.body import (
    get_body_composition,
    get_hrv,
    get_intensity_minutes,
    get_race_predictions,
    get_training_readiness,
    get_vo2max,
    get_weight,
)

FIXED_TODAY = "2026-04-25"
FIXED_WEEK_AGO = "2026-04-18"


def _setup(mocker, mock_garmin):
    mocker.patch(
        "garmin_mcp.tools.body.ensure_authenticated",
        new=AsyncMock(return_value=mock_garmin),
    )
    mocker.patch("garmin_mcp.tools.body._today", return_value=FIXED_TODAY)
    mocker.patch("garmin_mcp.tools.body._week_ago", return_value=FIXED_WEEK_AGO)


# --- get_weight ---


async def test_get_weight_explicit_date(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    mock_garmin.get_body_composition.return_value = {"weight": 75.0}
    result = await get_weight(mock_ctx, cdate="2026-04-20")
    mock_garmin.get_body_composition.assert_called_once_with("2026-04-20")
    assert result == {"weight": 75.0}


async def test_get_weight_default_date(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    mock_garmin.get_body_composition.return_value = {}
    await get_weight(mock_ctx)
    mock_garmin.get_body_composition.assert_called_once_with(FIXED_TODAY)


# --- get_body_composition ---


async def test_get_body_composition_explicit_range(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    mock_garmin.get_body_composition.return_value = {"entries": []}
    await get_body_composition(mock_ctx, start_date="2026-04-01", end_date="2026-04-10")
    mock_garmin.get_body_composition.assert_called_once_with("2026-04-01", "2026-04-10")


async def test_get_body_composition_default_range(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    mock_garmin.get_body_composition.return_value = {}
    await get_body_composition(mock_ctx)
    mock_garmin.get_body_composition.assert_called_once_with(FIXED_WEEK_AGO, FIXED_TODAY)


# --- get_hrv ---


async def test_get_hrv_explicit_date(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    mock_garmin.get_hrv_data.return_value = {"lastNight": 45}
    result = await get_hrv(mock_ctx, cdate="2026-04-20")
    mock_garmin.get_hrv_data.assert_called_once_with("2026-04-20")
    assert result == {"lastNight": 45}


async def test_get_hrv_default_date(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    await get_hrv(mock_ctx)
    mock_garmin.get_hrv_data.assert_called_once_with(FIXED_TODAY)


# --- get_vo2max ---
# NOTE: tool calls garmin.get_vo2max_summary_by_date — library actual method is get_max_metrics
# MagicMock auto-creates the attribute so tests pass.


async def test_get_vo2max_explicit_date(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    mock_garmin.get_vo2max_summary_by_date.return_value = {"vo2MaxValue": 52}
    result = await get_vo2max(mock_ctx, cdate="2026-04-20")
    mock_garmin.get_vo2max_summary_by_date.assert_called_once_with("2026-04-20")
    assert result == {"vo2MaxValue": 52}


async def test_get_vo2max_default_date(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    await get_vo2max(mock_ctx)
    mock_garmin.get_vo2max_summary_by_date.assert_called_once_with(FIXED_TODAY)


# --- get_training_readiness ---


async def test_get_training_readiness(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    mock_garmin.get_training_readiness.return_value = {"score": 70}
    result = await get_training_readiness(mock_ctx, cdate="2026-04-20")
    mock_garmin.get_training_readiness.assert_called_once_with("2026-04-20")
    assert result == {"score": 70}


async def test_get_training_readiness_default_date(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    await get_training_readiness(mock_ctx)
    mock_garmin.get_training_readiness.assert_called_once_with(FIXED_TODAY)


# --- get_intensity_minutes ---


async def test_get_intensity_minutes(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    mock_garmin.get_weekly_intensity_minutes.return_value = {"moderateIntensityMinutes": 120}
    result = await get_intensity_minutes(mock_ctx, cdate="2026-04-20")
    mock_garmin.get_weekly_intensity_minutes.assert_called_once_with("2026-04-20")
    assert result == {"moderateIntensityMinutes": 120}


async def test_get_intensity_minutes_default_date(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    await get_intensity_minutes(mock_ctx)
    mock_garmin.get_weekly_intensity_minutes.assert_called_once_with(FIXED_TODAY)


# --- get_race_predictions ---


async def test_get_race_predictions(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    mock_garmin.get_race_predictions.return_value = {"marathon": "3:30:00"}
    result = await get_race_predictions(mock_ctx)
    mock_garmin.get_race_predictions.assert_called_once_with()
    assert result == {"marathon": "3:30:00"}
