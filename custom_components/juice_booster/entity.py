"""Base entity for Juice Booster."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_NAME, DOMAIN, MANUFACTURER
from .coordinator import JuiceBoosterCoordinator


def nested_value(data: dict[str, Any], path: str) -> Any:
    """Return a nested value from a dot-separated path."""
    value: Any = data
    for part in path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


class JuiceBoosterEntity(CoordinatorEntity[JuiceBoosterCoordinator]):
    """Base coordinator entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: JuiceBoosterCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.device_id)},
            manufacturer=MANUFACTURER,
            name=DEFAULT_NAME,
            model=_first(coordinator.data.device, "model", "productName", "type") or DEFAULT_NAME,
            serial_number=_first(
                coordinator.data.device, "serialNumber", "serial-number", "serial"
            ),
            sw_version=_first(
                coordinator.data.device, "firmwareVersion", "firmware-version", "softwareVersion"
            ),
        )


def _first(data: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = data.get(key)
        if value is not None:
            return str(value)
    return None
