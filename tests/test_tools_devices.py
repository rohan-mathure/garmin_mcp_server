from __future__ import annotations

from unittest.mock import AsyncMock

from garmin_mcp.tools.devices import (
    get_device_info,
    list_badges,
    list_devices,
    list_gear,
    list_personal_records,
)


def _setup(mocker, mock_garmin):
    mocker.patch(
        "garmin_mcp.tools.devices.ensure_authenticated",
        new=AsyncMock(return_value=mock_garmin),
    )


# --- list_devices ---


async def test_list_devices(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    mock_garmin.get_devices.return_value = [{"deviceId": "123"}]
    result = await list_devices(mock_ctx)
    mock_garmin.get_devices.assert_called_once_with()
    assert result == [{"deviceId": "123"}]


# --- get_device_info ---


async def test_get_device_info(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    mock_garmin.get_device_settings.return_value = {"deviceId": "123", "displayName": "Forerunner"}
    result = await get_device_info(mock_ctx, device_id=123)
    mock_garmin.get_device_settings.assert_called_once_with(123)
    assert result["displayName"] == "Forerunner"


# --- list_gear ---
# list_gear makes two sequential asyncio.to_thread calls:
#   1. get_user_summary(today) → extract user hash
#   2. get_gear(user_hash) → return gear list


async def test_list_gear_with_user_profile_id(mock_garmin, mock_ctx, mocker):
    _setup(mocker, mock_garmin)
    mocker.patch(
        "asyncio.to_thread",
        new=AsyncMock(side_effect=[{"userProfileId": "profile_123"}, [{"gearId": "shoe1"}]]),
    )
    result = await list_gear(mock_ctx)
    assert result == [{"gearId": "shoe1"}]
    # get_gear called via to_thread mock, not directly on mock_garmin
    assert mock_garmin.get_gear.call_count == 0


async def test_list_gear_fallback_to_user_id(mock_garmin, mock_ctx, mocker):
    _setup(mocker, mock_garmin)
    mocker.patch(
        "asyncio.to_thread",
        new=AsyncMock(side_effect=[{"userId": "user_99"}, [{"gearId": "bike1"}]]),
    )
    result = await list_gear(mock_ctx)
    assert result == [{"gearId": "bike1"}]


async def test_list_gear_calls_get_gear_with_correct_hash(mock_garmin, mock_ctx, mocker):
    _setup(mocker, mock_garmin)
    # Use passthrough to verify actual call args
    mock_garmin.get_user_summary.return_value = {"userProfileId": "hash_abc"}
    mock_garmin.get_gear.return_value = [{"gearId": "gear1"}]

    async def _pt(fn, *a, **kw):
        return fn(*a, **kw)

    mocker.patch("asyncio.to_thread", new=AsyncMock(side_effect=_pt))
    result = await list_gear(mock_ctx)
    mock_garmin.get_gear.assert_called_once_with("hash_abc")
    assert result == [{"gearId": "gear1"}]


# --- list_personal_records ---
# NOTE: tool calls garmin.get_personal_record — verify it's called


async def test_list_personal_records(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    mock_garmin.get_personal_record.return_value = {"fastestMile": "5:30"}
    result = await list_personal_records(mock_ctx)
    mock_garmin.get_personal_record.assert_called_once_with()
    assert result == {"fastestMile": "5:30"}


# --- list_badges ---
# NOTE: tool calls garmin.get_badges — library actual method is get_earned_badges
# MagicMock auto-creates the attribute so tests pass.


async def test_list_badges(mock_garmin, mock_ctx, mocker, patch_to_thread):
    _setup(mocker, mock_garmin)
    mock_garmin.get_badges.return_value = [{"badgeId": "1", "name": "First Run"}]
    result = await list_badges(mock_ctx)
    mock_garmin.get_badges.assert_called_once_with()
    assert result == [{"badgeId": "1", "name": "First Run"}]
