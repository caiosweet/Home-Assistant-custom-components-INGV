"""The INGV Earthquakes integration."""
"""All credit goes to Malte Franken [@exxamalte]."""
from collections.abc import Callable
from datetime import timedelta
from importlib import import_module, util
import logging

from aio_quakeml_ingv_centro_nazionale_terremoti_client import (
    IngvCentroNazionaleTerremotiQuakeMLFeedManager,
)

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import UnitOfLength
from homeassistant.const import (
    CONF_LATITUDE,
    CONF_LOCATION,
    CONF_LONGITUDE,
    CONF_RADIUS,
    CONF_SCAN_INTERVAL,
    Platform,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util.unit_system import IMPERIAL_SYSTEM, METRIC_SYSTEM

from .const import (
    CONF_MINIMUM_MAGNITUDE,
    CONF_START_TIME,
    DEFAULT_MINIMUM_MAGNITUDE,
    DEFAULT_RADIUS,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_START_TIME,
    DOMAIN,
    FEED,
    PLATFORMS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the INGV Earthquakes integration."""
    if DOMAIN not in config:
        return True

    conf = config[DOMAIN]
    location = conf.get(CONF_LOCATION, hass.config.location_name)
    latitude = conf.get(CONF_LATITUDE, hass.config.latitude)
    longitude = conf.get(CONF_LONGITUDE, hass.config.longitude)
    radius = conf.get(CONF_RADIUS, DEFAULT_RADIUS)
    magnitude = conf.get(CONF_MINIMUM_MAGNITUDE, DEFAULT_MINIMUM_MAGNITUDE)
    start_time = conf.get(CONF_START_TIME, DEFAULT_START_TIME)
    scan_interval = conf.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_IMPORT},
            data={
                CONF_LOCATION: location,
                CONF_LATITUDE: latitude,
                CONF_LONGITUDE: longitude,
                CONF_RADIUS: radius,
                CONF_MINIMUM_MAGNITUDE: magnitude,
                CONF_SCAN_INTERVAL: scan_interval,
                CONF_START_TIME: start_time,
            },
        )
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the INGV Earthquakes integration from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    feeds = hass.data[DOMAIN].setdefault(FEED, {})
    radius = entry.options[CONF_RADIUS]
    if hass.config.units is IMPERIAL_SYSTEM:
        radius = METRIC_SYSTEM.length(radius, UnitOfLength.MILES)
    await _async_preload_dateparser(hass)
    # Create feed entity coordinator for all platforms.
    coordinator = IngvDataUpdateCoordinator(hass=hass, entry=entry, radius_in_km=radius)
    feeds[entry.entry_id] = coordinator
    _LOGGER.debug("Feed entity coordinator added for %s", entry.entry_id)

    async_cleanup_entity_registry(hass=hass, entry=entry)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


@callback
def async_cleanup_entity_registry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> None:
    """Remove orphaned geo_location entities."""
    entity_registry = er.async_get(hass)
    orphaned_entries = er.async_entries_for_config_entry(
        registry=entity_registry, config_entry_id=entry.entry_id
    )
    if orphaned_entries is not None:
        for orphan in orphaned_entries:
            if orphan.domain == Platform.GEO_LOCATION:
                _LOGGER.debug("Removing orphaned entry %s", orphan.entity_id)
                entity_registry.async_remove(orphan.entity_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    coordinator = hass.data[DOMAIN][FEED].pop(entry.entry_id)
    await coordinator.async_stop()
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle an options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def _async_preload_dateparser(hass: HomeAssistant) -> None:
    """Preload dateparser data to avoid blocking imports in the event loop."""
    language = hass.config.language or "en"
    module_names = [f"dateparser.data.date_translation_data.{language}"]
    if language != "en":
        module_names.append("dateparser.data.date_translation_data.en")
    for module_name in module_names:
        if util.find_spec(module_name) is None:
            continue
        await hass.async_add_executor_job(import_module, module_name)


class IngvDataUpdateCoordinator(DataUpdateCoordinator):
    """Data update coordinator for the INGV Earthquakes integration."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, radius_in_km: float) -> None:
        """Initialize the Feed Entity Coordinator."""
        self.entry = entry
        self.hass = hass
        coordinates = (
            entry.data[CONF_LATITUDE],
            entry.data[CONF_LONGITUDE],
        )
        websession = async_get_clientsession(hass)
        self._feed_manager = IngvCentroNazionaleTerremotiQuakeMLFeedManager(
            websession=websession,
            coordinates=coordinates,
            filter_radius=radius_in_km,
            filter_minimum_magnitude=entry.options[CONF_MINIMUM_MAGNITUDE],
            starttime_delta=timedelta(hours=entry.options[CONF_START_TIME]),
            generate_async_callback=self._generate_entity,
            update_async_callback=self._update_entity,
            remove_async_callback=self._remove_entity,
            status_async_callback=self._status_update,
        )
        self._entry_id = entry.entry_id
        self._status_info = None
        self.listeners: list[Callable[[], None]] = []
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=f"{DOMAIN}-{entry.data[CONF_LOCATION]}",
            update_method=self.async_update,
            update_interval=timedelta(seconds=entry.options[CONF_SCAN_INTERVAL]),
        )

    async def async_update(self) -> None:
        """Refresh data."""
        await self._feed_manager.update()
        _LOGGER.debug("Feed entity coordinator updated")
        return self._feed_manager.feed_entries

    async def async_stop(self) -> None:
        """Stop this feed entity coordinator from refreshing."""
        for unsub_dispatcher in self.listeners:
            unsub_dispatcher()
        self.listeners = []
        _LOGGER.debug("Feed entity coordinator stopped")

    @callback
    def async_event_new_entity(self) -> str:
        """Return coordinator specific event to signal new entity."""
        return f"{DOMAIN}_new_geolocation_{self._entry_id}"

    def get_entry(self, external_id):
        """Get feed entry by external id."""
        return self._feed_manager.feed_entries.get(external_id)

    def entry_available(self, external_id) -> bool:
        """Get feed entry by external id."""
        return self._feed_manager.feed_entries.get(external_id) is not None

    def status_info(self):
        """Return latest status update info received."""
        return self._status_info

    async def _generate_entity(self, external_id: str) -> None:
        """Generate new entity."""
        _LOGGER.debug("New entry received for: %s", external_id)
        async_dispatcher_send(
            self.hass,
            self.async_event_new_entity(),
            self,
            self.entry.unique_id,
            external_id,
        )

    async def _update_entity(self, external_id: str) -> None:
        """Ignore update call; this is handled by the coordinator."""

    async def _remove_entity(self, external_id: str) -> None:
        """Remove entity."""
        _LOGGER.debug("Remove received for: %s", external_id)
        async_dispatcher_send(self.hass, f"{DOMAIN}_delete_{external_id}")

    async def _status_update(self, status_info) -> None:
        """Store status update."""
        _LOGGER.debug("Status update received: %s", status_info)
        self._status_info = status_info
