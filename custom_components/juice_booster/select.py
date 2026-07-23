"""Charging current selector."""

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import JuiceBoosterConfigEntry
from .const import AVAILABLE_AMPERES
from .entity import JuiceBoosterEntity, nested_value


async def async_setup_entry(
    hass: HomeAssistant,
    entry: JuiceBoosterConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([JuiceBoosterCurrentSelect(entry.runtime_data)])


class JuiceBoosterCurrentSelect(JuiceBoosterEntity, SelectEntity):
    _attr_translation_key = "maximum_current"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device_id}_maximum_current"
        self._attr_options = [str(v) for v in AVAILABLE_AMPERES]

    @property
    def current_option(self) -> str | None:
        value = nested_value(
            self.coordinator.data.charging,
            "device-currents.max-supply-current",
        )
        if isinstance(value, (int, float)):
            return str(int(value))
        return None

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_set_current(int(option))
