"""Data coordinator for Juice Booster."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import JuiceBoosterApi, JuiceBoosterApiError, JuiceBoosterAuthError
from .const import (
    CONF_ACCESS_TOKEN,
    CONF_DEVICE_ID,
    CONF_REFRESH_TOKEN,
    CONF_USER_ID,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class JuiceBoosterData:
    """Data returned by the cloud."""

    charging: dict[str, Any]
    device: dict[str, Any]


class JuiceBoosterCoordinator(DataUpdateCoordinator[JuiceBoosterData]):
    """Coordinate cloud updates and commands."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, api: JuiceBoosterApi) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self.api = api
        self.device_id = str(entry.data[CONF_DEVICE_ID])
        self.user_id = str(entry.data[CONF_USER_ID])

    async def _async_update_data(self) -> JuiceBoosterData:
        try:
            charging = await self.api.async_get_charging(self.device_id)
            try:
                device = await self.api.async_get_device(self.device_id)
            except JuiceBoosterApiError as err:
                _LOGGER.debug("Device metadata unavailable: %s", err)
                device = {}
            self._save_tokens()
            return JuiceBoosterData(charging=charging, device=device)
        except JuiceBoosterAuthError as err:
            raise ConfigEntryAuthFailed from err
        except JuiceBoosterApiError as err:
            raise UpdateFailed(str(err)) from err

    async def async_set_current(self, amperes: int) -> None:
        """Set maximum supply current and refresh state."""
        try:
            await self.api.async_set_current(self.device_id, amperes)
            self._save_tokens()
        except JuiceBoosterAuthError as err:
            raise ConfigEntryAuthFailed from err
        await self.async_request_refresh()

    def _save_tokens(self) -> None:
        data = dict(self.config_entry.data)
        changed = False
        if self.api.access_token and data.get(CONF_ACCESS_TOKEN) != self.api.access_token:
            data[CONF_ACCESS_TOKEN] = self.api.access_token
            changed = True
        if self.api.refresh_token and data.get(CONF_REFRESH_TOKEN) != self.api.refresh_token:
            data[CONF_REFRESH_TOKEN] = self.api.refresh_token
            changed = True
        if changed:
            self.hass.config_entries.async_update_entry(self.config_entry, data=data)
