"""Charging switch for Juice Booster."""

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import JuiceBoosterConfigEntry
from .entity import JuiceBoosterEntity, nested_value


async def async_setup_entry(hass: HomeAssistant, entry: JuiceBoosterConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    async_add_entities([JuiceBoosterChargingSwitch(entry.runtime_data)])


class JuiceBoosterChargingSwitch(JuiceBoosterEntity, SwitchEntity):
    _attr_translation_key = "charging"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device_id}_charging"

    @property
    def is_on(self) -> bool:
        value = nested_value(self.coordinator.data.charging, "device-currents.max-supply-current")
        return isinstance(value, (int, float)) and value > 0

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_set_current(10)

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_set_current(0)
