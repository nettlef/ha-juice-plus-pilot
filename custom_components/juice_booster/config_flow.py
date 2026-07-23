"""Config flow for Juice Booster."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    JuiceBoosterApi,
    JuiceBoosterApiError,
    JuiceBoosterAuthError,
    JuiceBoosterConnectionError,
)
from .const import (
    CONF_ACCESS_TOKEN,
    CONF_DEVICE_ID,
    CONF_REFRESH_TOKEN,
    CONF_USER_ID,
    DEFAULT_NAME,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class JuiceBoosterConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            api = JuiceBoosterApi(
                async_get_clientsession(self.hass),
                username=user_input[CONF_USERNAME],
                password=user_input[CONF_PASSWORD],
            )
            try:
                tokens = await api.async_login()
                user_id = api.user_id_from_token(str(tokens[CONF_ACCESS_TOKEN]))
                user = await api.async_get_user(user_id)
                devices = user.get("devices") or []
                if not devices:
                    errors["base"] = "no_devices"
                else:
                    device_id = str(devices[0]["id"])
                    await self.async_set_unique_id(device_id)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=DEFAULT_NAME,
                        data={
                            CONF_USERNAME: user_input[CONF_USERNAME],
                            CONF_PASSWORD: user_input[CONF_PASSWORD],
                            CONF_ACCESS_TOKEN: api.access_token,
                            CONF_REFRESH_TOKEN: api.refresh_token,
                            CONF_USER_ID: user_id,
                            CONF_DEVICE_ID: device_id,
                        },
                    )
                
            except JuiceBoosterAuthError as err:
                _LOGGER.error("J+ Pilot authentication failed: %s", err)
                errors["base"] = "invalid_auth"
                
            except JuiceBoosterConnectionError as err:
                _LOGGER.exception("Unable to connect to J+ Pilot: %s", err)
                errors["base"] = "cannot_connect"
                
            except JuiceBoosterApiError as err:
                _LOGGER.exception("J+ Pilot API error during setup: %s", err)
                errors["base"] = "unknown"                
                
            except (KeyError, TypeError, ValueError):
                _LOGGER.exception("Unexpected J+ Pilot response during setup")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> ConfigFlowResult:
        """Start reauthentication."""
        self._reauth_entry = self._get_reauth_entry()
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm reauthentication."""
        errors: dict[str, str] = {}
        if user_input is not None:
            api = JuiceBoosterApi(
                async_get_clientsession(self.hass),
                username=self._reauth_entry.data[CONF_USERNAME],
                password=user_input[CONF_PASSWORD],
            )
            try:
                await api.async_login()
            except JuiceBoosterAuthError:
                errors["base"] = "invalid_auth"
            except JuiceBoosterConnectionError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_update_reload_and_abort(
                    self._reauth_entry,
                    data_updates={
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                        CONF_ACCESS_TOKEN: api.access_token,
                        CONF_REFRESH_TOKEN: api.refresh_token,
                    },
                )
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_PASSWORD): str}),
            errors=errors,
        )
