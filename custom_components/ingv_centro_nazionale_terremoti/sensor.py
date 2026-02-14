"""INGV Earthquakes integration status sensor."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt

from . import IngvDataUpdateCoordinator
from .const import (
    ATTR_CREATED,
    ATTR_LAST_TIMESTAMP,
    ATTR_LAST_UPDATE,
    ATTR_LAST_UPDATE_SUCCESSFUL,
    ATTR_REMOVED,
    ATTR_STATUS,
    ATTR_UPDATED,
    DEFAULT_FORCE_UPDATE,
    DEFAULT_UNIT_OF_MEASUREMENT,
    DOMAIN,
    FEED,
    VERSION,
)

_LOGGER = logging.getLogger(__name__)


# An update of this entity is not making a web request, but uses internal data only.
PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the INGV Earthquakes integration sensor platform."""
    coordinator = hass.data[DOMAIN][FEED][entry.entry_id]
    config_entry_unique_id = entry.unique_id

    async_add_entities(
        [IngvSensorEntity(coordinator, config_entry_unique_id, entry.title)],
        True,
    )
    _LOGGER.debug("Sensor setup done")


class IngvSensorEntity(CoordinatorEntity, SensorEntity):
    """Implementation of the sensor."""

    coordinator: IngvDataUpdateCoordinator
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_force_update = DEFAULT_FORCE_UPDATE
    _attr_native_unit_of_measurement = DEFAULT_UNIT_OF_MEASUREMENT
    _attr_icon = "mdi:pulse"

    def __init__(
        self,
        coordinator: IngvDataUpdateCoordinator,
        config_entry_unique_id: str | None,
        config_title: str | None,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._config_title = config_title
        self._attr_unique_id = f"{config_entry_unique_id}_status"
        self._attr_name = f"Ingv Earthquakes {config_title} status"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry.entry_id)},
            entry_type=DeviceEntryType.SERVICE,
            manufacturer="Istituto Nazionale di Geofisica e Vulcanologia",
            name="INGV Earthquakes",
            sw_version=VERSION,
        )

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        self._update_internal_state()

    def _update_internal_state(self) -> None:
        """Update state and attributes from coordinator data."""

        if status_info := self.coordinator.status_info():
            _LOGGER.debug("Updating state from %s", status_info)
            self._attr_native_value = status_info.total
            self._attr_extra_state_attributes = {}
            for key, value in (
                (ATTR_STATUS, status_info.status),
                (
                    ATTR_LAST_UPDATE,
                    (
                        dt.as_utc(status_info.last_update)
                        if status_info.last_update
                        else None
                    ),
                ),
                (
                    ATTR_LAST_UPDATE_SUCCESSFUL,
                    (
                        dt.as_utc(status_info.last_update_successful)
                        if status_info.last_update_successful
                        else None
                    ),
                ),
                (ATTR_LAST_TIMESTAMP, status_info.last_timestamp),
                (ATTR_CREATED, status_info.created),
                (ATTR_UPDATED, status_info.updated),
                (ATTR_REMOVED, status_info.removed),
            ):
                if value or isinstance(value, bool):
                    self._attr_extra_state_attributes[key] = value

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._update_internal_state()
        super()._handle_coordinator_update()
