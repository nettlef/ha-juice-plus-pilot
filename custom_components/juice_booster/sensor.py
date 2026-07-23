"""Sensors for Juice Booster."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.const import UnitOfElectricCurrent, UnitOfElectricPotential, UnitOfEnergy, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import JuiceBoosterConfigEntry
from .entity import JuiceBoosterEntity, nested_value


def _as_datetime(value: Any) -> datetime | None:
    """Convert a J+ Pilot timestamp to a timezone-aware datetime."""
    if value in (None, "", 0, "0"):
        return None

    try:
        if isinstance(value, str):
            stripped = value.strip()

            # Numeric strings are handled as Unix timestamps.
            try:
                value = float(stripped)
            except ValueError:
                parsed = datetime.fromisoformat(stripped.replace("Z", "+00:00"))
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=UTC)
                return parsed

        if isinstance(value, (int, float)):
            timestamp = float(value)

            # J+ Pilot may return milliseconds instead of seconds.
            if timestamp > 10_000_000_000:
                timestamp /= 1000

            return datetime.fromtimestamp(timestamp, tz=UTC)

    except (TypeError, ValueError, OSError):
        return None

    return None


@dataclass(frozen=True, kw_only=True)
class JuiceSensorDescription(SensorEntityDescription):
    path: str
    multiplier: float = 1.0


SENSORS = (
    JuiceSensorDescription(key="charge_state", translation_key="charge_state", path="charge-state"),
    JuiceSensorDescription(key="charge_control", translation_key="charge_control", path="charge-control"),
    JuiceSensorDescription(key="charge_start_time", translation_key="charge_start_time", path="charge-start-time", device_class=SensorDeviceClass.TIMESTAMP),
    JuiceSensorDescription(key="energy_total", translation_key="energy_total", path="measured-energy.value-total", native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING),
    JuiceSensorDescription(key="power_total", translation_key="power_total", path="measured-power.value", native_unit_of_measurement=UnitOfPower.KILO_WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT),
    JuiceSensorDescription(key="voltage_l1", translation_key="voltage_l1", path="measured-details.voltage.valueL1", native_unit_of_measurement=UnitOfElectricPotential.VOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT),
    JuiceSensorDescription(key="voltage_l2", translation_key="voltage_l2", path="measured-details.voltage.valueL2", native_unit_of_measurement=UnitOfElectricPotential.VOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT),
    JuiceSensorDescription(key="voltage_l3", translation_key="voltage_l3", path="measured-details.voltage.valueL3", native_unit_of_measurement=UnitOfElectricPotential.VOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT),
    JuiceSensorDescription(key="current_l1", translation_key="current_l1", path="measured-details.ampere.valueL1", native_unit_of_measurement=UnitOfElectricCurrent.AMPERE, device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT),
    JuiceSensorDescription(key="current_l2", translation_key="current_l2", path="measured-details.ampere.valueL2", native_unit_of_measurement=UnitOfElectricCurrent.AMPERE, device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT),
    JuiceSensorDescription(key="current_l3", translation_key="current_l3", path="measured-details.ampere.valueL3", native_unit_of_measurement=UnitOfElectricCurrent.AMPERE, device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT),
    JuiceSensorDescription(key="power_l1", translation_key="power_l1", path="measured-details.power.valueL1", native_unit_of_measurement=UnitOfPower.KILO_WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT),
    JuiceSensorDescription(key="power_l2", translation_key="power_l2", path="measured-details.power.valueL2", native_unit_of_measurement=UnitOfPower.KILO_WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT),
    JuiceSensorDescription(key="power_l3", translation_key="power_l3", path="measured-details.power.valueL3", native_unit_of_measurement=UnitOfPower.KILO_WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT),
)


async def async_setup_entry(hass: HomeAssistant, entry: JuiceBoosterConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    async_add_entities(JuiceBoosterSensor(entry.runtime_data, description) for description in SENSORS)


class JuiceBoosterSensor(JuiceBoosterEntity, SensorEntity):
    entity_description: JuiceSensorDescription

    def __init__(self, coordinator, description: JuiceSensorDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.device_id}_{description.key}"

    @property
    def native_value(self) -> Any:
        value = nested_value(self.coordinator.data.charging, self.entity_description.path)
        if value is None:
            return None
        if self.entity_description.device_class == SensorDeviceClass.TIMESTAMP:
            return _as_datetime(value)
        if isinstance(value, (int, float)):
            return value * self.entity_description.multiplier
        return value
