"""Button entities for Juice Booster."""

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import JuiceBoosterConfigEntry
from .entity import JuiceBoosterEntity


async def async_setup_entry(hass: HomeAssistant, entry: JuiceBoosterConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    async_add_entities([JuiceBoosterRefreshButton(entry.runtime_data)])


class JuiceBoosterRefreshButton(JuiceBoosterEntity, ButtonEntity):
    _attr_translation_key = "refresh"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device_id}_refresh"

    async def async_press(self) -> None:
        await self.coordinator.async_request_refresh()
