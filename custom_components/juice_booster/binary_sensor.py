"""Binary sensors for Juice Booster."""

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import JuiceBoosterConfigEntry
from .entity import JuiceBoosterEntity, nested_value


async def async_setup_entry(hass: HomeAssistant, entry: JuiceBoosterConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    async_add_entities([
        JuiceBoosterChargingBinarySensor(entry.runtime_data),
        JuiceBoosterSmartJuiceBinarySensor(entry.runtime_data),
    ])


class JuiceBoosterChargingBinarySensor(JuiceBoosterEntity, BinarySensorEntity):
    _attr_translation_key = "is_charging"
    _attr_device_class = BinarySensorDeviceClass.BATTERY_CHARGING

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device_id}_is_charging"

    @property
    def is_on(self) -> bool:
        state = str(nested_value(self.coordinator.data.charging, "charge-state") or "").lower()
        power = nested_value(self.coordinator.data.charging, "measured-power.value")
        return state in {"charging", "charge", "active"} or (isinstance(power, (int, float)) and power > 0)


class JuiceBoosterSmartJuiceBinarySensor(JuiceBoosterEntity, BinarySensorEntity):
    _attr_translation_key = "smart_juice"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device_id}_smart_juice"

    @property
    def is_on(self) -> bool | None:
        value = nested_value(self.coordinator.data.charging, "device-currents.smart-juice-enabled")
        return value if isinstance(value, bool) else None
