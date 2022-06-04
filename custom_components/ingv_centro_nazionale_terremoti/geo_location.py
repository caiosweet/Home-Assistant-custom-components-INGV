"""Support for INGV Earthquakes integration geo location events."""
from __future__ import annotations

import functools
import logging

import voluptuous as vol

from homeassistant.components.geo_location import PLATFORM_SCHEMA, GeolocationEvent
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import (
    ATTR_TIME,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_RADIUS,
    CONF_UNIT_SYSTEM_IMPERIAL,
    LENGTH_KILOMETERS,
    LENGTH_MILES,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util.unit_system import IMPERIAL_SYSTEM

from . import IngvDataUpdateCoordinator
from .const import (
    CONF_MINIMUM_MAGNITUDE,
    DEFAULT_FORCE_UPDATE,
    DEFAULT_MINIMUM_MAGNITUDE,
    DEFAULT_RADIUS,
    DOMAIN,
    FEED,
    IMAGE_URL_PATTERN,
    SOURCE,
)

_LOGGER = logging.getLogger(__name__)

ATTR_DEPTH = "depth"
ATTR_EVENT_ID = "event_id"
ATTR_EXTERNAL_ID = "external_id"
ATTR_IMAGE_URL = "image_url"
ATTR_MAGNITUDE = "magnitude"
ATTR_MODE = "mode"
ATTR_PUBLICATION_DATE = "publication_date"
ATTR_REGION = "region"
ATTR_STATUS = "status"

# Deprecated.
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_LATITUDE): cv.latitude,
        vol.Optional(CONF_LONGITUDE): cv.longitude,
        vol.Optional(CONF_RADIUS, default=DEFAULT_RADIUS): vol.Coerce(float),
        vol.Optional(CONF_MINIMUM_MAGNITUDE, default=DEFAULT_MINIMUM_MAGNITUDE): cv.positive_float,
    }
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the INGV Earthquakes integration platform."""
    coordinator = hass.data[DOMAIN][FEED][entry.entry_id]

    @callback
    def async_add_geolocation(coordinator, config_entry_unique_id, external_id):
        """Add geolocation entity from feed."""
        new_entity = IngvGeolocationEvent(coordinator, config_entry_unique_id, external_id)
        _LOGGER.debug("Adding geolocation %s", new_entity)
        async_add_entities([new_entity], False)

    coordinator.listeners.append(
        async_dispatcher_connect(hass, coordinator.async_event_new_entity(), async_add_geolocation)
    )
    _LOGGER.debug("Geolocation setup done")


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the INGV Earthquakes integration platform."""
    _LOGGER.warning(
        "Configuration of the INGV platform in YAML is deprecated and will be "
        "removed in the next release;"
        "Your existing configuration for %s "
        "has been imported into the UI automatically and can be safely removed "
        "from your configuration.yaml file",
        config.get("platform", DOMAIN),
    )
    hass.async_create_task(
        hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_IMPORT}, data=config)
    )


class IngvGeolocationEvent(CoordinatorEntity, GeolocationEvent):
    """This represents an external event with INGV Earthquakes integration data."""

    coordinator: IngvDataUpdateCoordinator
    _attr_force_update = DEFAULT_FORCE_UPDATE
    _attr_icon = "mdi:pulse"
    _attr_unit_of_measurement = LENGTH_KILOMETERS

    def __init__(
        self,
        coordinator: IngvDataUpdateCoordinator,
        config_entry_unique_id: str | None,
        external_id: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._external_id = external_id
        self._event_id = external_id.split("eventId=")[1]
        self._attr_unique_id = f"{config_entry_unique_id}_{self._event_id}"
        # I think I will rename the domain in the future. (INGV Earthquake?)
        self.entity_id = f"geo_location.ingv_earthquakes_{self._attr_unique_id}"
        self._description = None
        self._distance: float | None = None
        self._latitude: float | None = None
        self._longitude: float | None = None
        self._depth = None
        self._region = None
        self._magnitude = None
        self._status = None
        self._mode = None
        self._time = None
        self._image_url = None
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.entry.entry_id)},
            entry_type=DeviceEntryType.SERVICE,
        )

    async def async_added_to_hass(self) -> None:
        """Call when entity is added to hass."""
        await super().async_added_to_hass()
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"{DOMAIN}_delete_{self._external_id}",
                functools.partial(self.async_remove, force_remove=True),
            )
        )
        self._update_internal_state()

    async def async_will_remove_from_hass(self) -> None:
        """Call when entity will be removed from hass."""
        entity_registry = er.async_get(self.hass)
        # Remove from entity registry.
        if self.entity_id in entity_registry.entities:
            entity_registry.async_remove(self.entity_id)
            _LOGGER.debug("Removed geolocation %s from entity registry", self.entity_id)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return super().available and self.coordinator.entry_available(self._external_id)

    @property
    def distance(self) -> float | None:
        """Return distance value of this external event."""
        return self._distance

    def _update_internal_state(self) -> None:
        """Update state and attributes from coordinator data."""
        _LOGGER.debug("Updating %s from coordinator data", self._external_id)
        if feed_entry := self.coordinator.get_entry(self._external_id):
            self._depth = round((feed_entry.origin.depth / 1000), 1)
            self._distance = feed_entry.distance_to_home
            # Convert distance and depth if not metric system.
            if self.hass.config.units.name == CONF_UNIT_SYSTEM_IMPERIAL:
                self._depth = IMPERIAL_SYSTEM.length(self._depth, LENGTH_KILOMETERS)
                self._distance = IMPERIAL_SYSTEM.length(self._distance, LENGTH_KILOMETERS)
                self._attr_unit_of_measurement = LENGTH_MILES

            self._description = feed_entry.description
            self._latitude = feed_entry.coordinates[0]
            self._longitude = feed_entry.coordinates[1]
            self._magnitude = feed_entry.magnitude.mag
            # extra attribute image url not in feed_entry
            if self._magnitude >= 3:
                self._image_url = IMAGE_URL_PATTERN.format(self._event_id)
            self._region = feed_entry._quakeml_event.description.text
            self._time = feed_entry.origin.time
            self._status = feed_entry.origin.evaluation_status
            self._mode = feed_entry.origin.evaluation_mode

            self._attr_attribution = feed_entry.attribution
            self._attr_name = f"M {self._magnitude:.1f} - {self._region}"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._update_internal_state()
        super()._handle_coordinator_update()

    @property
    def latitude(self) -> float | None:
        """Return latitude value of this external event."""
        return self._latitude

    @property
    def longitude(self) -> float | None:
        """Return longitude value of this external event."""
        return self._longitude

    @property
    def source(self) -> str:
        """Return source value of this external event."""
        return SOURCE

    @property
    def extra_state_attributes(self):
        """Return the device state attributes."""
        attributes = {}
        for key, value in (
            (ATTR_EVENT_ID, self._event_id),
            (ATTR_DEPTH, self._depth),
            (ATTR_REGION, self._region),
            (ATTR_MAGNITUDE, self._magnitude),
            (ATTR_STATUS, self._status),
            (ATTR_MODE, self._mode),
            (ATTR_PUBLICATION_DATE, self._time),
            (ATTR_IMAGE_URL, self._image_url),
        ):
            if value or isinstance(value, bool):
                attributes[key] = value
        return attributes
