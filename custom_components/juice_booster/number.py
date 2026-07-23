"""Charging current control."""

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.const import UnitOfElectricCurrent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import JuiceBoosterConfigEntry
from .const import AVAILABLE_AMPERES
from .entity import JuiceBoosterEntity, nested_value


async def async_setup_entry(hass: HomeAssistant, entry: JuiceBoosterConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    async_add_entities([JuiceBoosterCurrentNumber(entry.runtime_data)])


class JuiceBoosterCurrentNumber(JuiceBoosterEntity, NumberEntity):
    _attr_translation_key = "maximum_current"
    _attr_device_class = NumberDeviceClass.CURRENT
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_native_min_value = 0
    _attr_native_max_value = 16
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device_id}_maximum_current"

    @property
    def native_value(self) -> float | None:
        value = nested_value(self.coordinator.data.charging, "device-currents.max-supply-current")
        return float(value) if isinstance(value, (int, float)) else None

    async def async_set_native_value(self, value: float) -> None:
        requested = int(round(value))
        nearest = min(AVAILABLE_AMPERES, key=lambda allowed: abs(allowed - requested))
        await self.coordinator.async_set_current(nearest)
