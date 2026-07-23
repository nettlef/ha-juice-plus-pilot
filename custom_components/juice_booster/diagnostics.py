"""Diagnostics for Juice Booster."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from . import JuiceBoosterConfigEntry

TO_REDACT = {"access_token", "refresh_token", "password", "username", "email", "address"}


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: JuiceBoosterConfigEntry) -> dict[str, Any]:
    """Return redacted diagnostics."""
    coordinator = entry.runtime_data
    return {
        "config_entry": async_redact_data(dict(entry.data), TO_REDACT),
        "device_id": coordinator.device_id,
        "last_update_success": coordinator.last_update_success,
        "data": async_redact_data(
            {
                "charging": coordinator.data.charging,
                "device": coordinator.data.device,
            },
            TO_REDACT,
        ),
    }
