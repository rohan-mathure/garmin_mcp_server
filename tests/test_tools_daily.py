from __future__ import annotations

from unittest.mock import AsyncMock

from garmin_mcp.tools.daily import (
    get_calories,
    get_daily_summary,
    get_heart_rate,
    get_sleep,
    get_spo2,
    get_steps,
    get_stress,
)

FIXED_DATE = "2026-04-25"


def _setup(mocker, mock_garmin):
    mocker.patch(
        "garmin_mcp.tools.daily.ensure_authenticated",
        new=AsyncMock(return_value=mock_garmin),
    )
    mocker.patch("garmin_mcp.tools.daily._today", return_value=FIXED_DATE)


# --- get_daily_summary ---


async def test_get_daily_summary_explicit_date(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    mock_garmin.get_user_summary.return_value = {"steps": 5000}
    result = await get_daily_summary(mock_ctx, cdate="2026-04-20")
    mock_garmin.get_user_summary.assert_called_once_with("2026-04-20")
    assert result == {"steps": 5000}


async def test_get_daily_summary_default_date(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    mock_garmin.get_user_summary.return_value = {}
    await get_daily_summary(mock_ctx)
    mock_garmin.get_user_summary.assert_called_once_with(FIXED_DATE)


# --- get_steps ---


async def test_get_steps_explicit_date(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    mock_garmin.get_steps_data.return_value = {"totalSteps": 8000}
    result = await get_steps(mock_ctx, cdate="2026-04-20")
    mock_garmin.get_steps_data.assert_called_once_with("2026-04-20")
    assert result == {"totalSteps": 8000}


async def test_get_steps_default_date(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    mock_garmin.get_steps_data.return_value = {}
    await get_steps(mock_ctx)
    mock_garmin.get_steps_data.assert_called_once_with(FIXED_DATE)


# --- get_heart_rate ---


async def test_get_heart_rate_explicit_date(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    mock_garmin.get_heart_rates.return_value = {"restingHR": 55}
    result = await get_heart_rate(mock_ctx, cdate="2026-04-20")
    mock_garmin.get_heart_rates.assert_called_once_with("2026-04-20")
    assert result == {"restingHR": 55}


async def test_get_heart_rate_default_date(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    await get_heart_rate(mock_ctx)
    mock_garmin.get_heart_rates.assert_called_once_with(FIXED_DATE)


# --- get_stress ---


async def test_get_stress_explicit_date(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    mock_garmin.get_stress_data.return_value = {"avgStress": 30}
    result = await get_stress(mock_ctx, cdate="2026-04-20")
    mock_garmin.get_stress_data.assert_called_once_with("2026-04-20")
    assert result == {"avgStress": 30}


async def test_get_stress_default_date(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    await get_stress(mock_ctx)
    mock_garmin.get_stress_data.assert_called_once_with(FIXED_DATE)


# --- get_spo2 ---


async def test_get_spo2_explicit_date(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    mock_garmin.get_spo2_data.return_value = {"avgSpo2": 98}
    result = await get_spo2(mock_ctx, cdate="2026-04-20")
    mock_garmin.get_spo2_data.assert_called_once_with("2026-04-20")
    assert result == {"avgSpo2": 98}


async def test_get_spo2_default_date(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    await get_spo2(mock_ctx)
    mock_garmin.get_spo2_data.assert_called_once_with(FIXED_DATE)


# --- get_sleep ---


async def test_get_sleep_explicit_date(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    mock_garmin.get_sleep_data.return_value = {"sleepScore": 80}
    result = await get_sleep(mock_ctx, cdate="2026-04-20")
    mock_garmin.get_sleep_data.assert_called_once_with("2026-04-20")
    assert result == {"sleepScore": 80}


async def test_get_sleep_default_date(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    await get_sleep(mock_ctx)
    mock_garmin.get_sleep_data.assert_called_once_with(FIXED_DATE)


# --- get_calories ---


async def test_get_calories_full_data(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    mock_garmin.get_user_summary.return_value = {
        "activeKilocalories": 500,
        "bmrKilocalories": 1800,
        "totalKilocalories": 2300,
        "wellnessActiveKilocalories": 450,
        "consumedKilocalories": 2100,
        "remainingKilocalories": -200,
    }
    result = await get_calories(mock_ctx, cdate="2026-04-20")
    assert set(result.keys()) == {
        "date",
        "active_kilocalories",
        "bmr_kilocalories",
        "total_kilocalories",
        "wellness_active_kilocalories",
        "consumed_kilocalories",
        "remaining_kilocalories",
    }
    assert result["date"] == "2026-04-20"
    assert result["active_kilocalories"] == 500
    assert result["bmr_kilocalories"] == 1800


async def test_get_calories_empty_summary(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    mock_garmin.get_user_summary.return_value = {}
    result = await get_calories(mock_ctx, cdate="2026-04-20")
    assert result["date"] == "2026-04-20"
    assert result["active_kilocalories"] is None
    assert result["total_kilocalories"] is None


async def test_get_calories_default_date(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    mock_garmin.get_user_summary.return_value = {}
    result = await get_calories(mock_ctx)
    assert result["date"] == FIXED_DATE
    mock_garmin.get_user_summary.assert_called_once_with(FIXED_DATE)
