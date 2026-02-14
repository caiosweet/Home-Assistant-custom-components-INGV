"""The INGV Earthquakes integration.

All credit goes to Malte Franken [@exxamalte].
"""
import inspect
import logging
import re
from collections.abc import Callable
from datetime import timedelta
from importlib import import_module, util
from urllib.parse import parse_qs, urlsplit

from aio_quakeml_client.consts import UPDATE_ERROR, UPDATE_OK
from aio_quakeml_ingv_centro_nazionale_terremoti_client import (
    IngvCentroNazionaleTerremotiQuakeMLFeedManager,
)
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import (
    CONF_LATITUDE,
    CONF_LOCATION,
    CONF_LONGITUDE,
    CONF_RADIUS,
    CONF_SCAN_INTERVAL,
    UnitOfLength,
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


def _extract_event_id(external_id: str) -> str:
    """Extract stable event id from a feed external id."""
    query = urlsplit(external_id).query
    if query:
        parsed_query = parse_qs(query)
        if parsed_event_id := parsed_query.get("eventId"):
            if event_id := parsed_event_id[0]:
                return event_id

    fallback_event_id = external_id.rsplit("/", maxsplit=1)[-1]
    return fallback_event_id or external_id


@callback
def _normalize_geo_entity_ids(
    hass: HomeAssistant,
    entry: ConfigEntry,
    *,
    remove_without_unique_id: bool = False,
) -> None:
    """Normalize legacy geo_location entity IDs for this config entry."""
    if not entry.unique_id:
        return

    entity_registry = er.async_get(hass)
    unique_id_prefix = f"{entry.unique_id}_"
    entity_id_prefix = f"geo_location.{DOMAIN}_{entry.unique_id.lower()}_"
    duplicate_suffix_pattern = re.compile(rf"^({re.escape(entity_id_prefix)}\d+)_\d+$")

    for registry_entry in er.async_entries_for_config_entry(entity_registry, entry.entry_id):
        if registry_entry.platform != DOMAIN:
            continue
        if not registry_entry.entity_id.startswith("geo_location."):
            continue

        if remove_without_unique_id and not registry_entry.unique_id:
            _LOGGER.debug(
                "Removing legacy geolocation entity without unique_id: %s",
                registry_entry.entity_id,
            )
            entity_registry.async_remove(registry_entry.entity_id)
            continue

        unique_id = registry_entry.unique_id or ""
        if not unique_id.startswith(unique_id_prefix):
            continue

        if not (match := duplicate_suffix_pattern.match(registry_entry.entity_id)):
            continue

        expected_entity_id = match.group(1)
        existing = entity_registry.async_get(expected_entity_id)
        if existing and existing.entity_id != registry_entry.entity_id:
            # Prefer entity mapped to this config entry and unique_id.
            if (
                existing.unique_id == registry_entry.unique_id
                and existing.config_entry_id == entry.entry_id
            ):
                _LOGGER.debug(
                    "Removing duplicate geolocation %s (keeping %s)",
                    registry_entry.entity_id,
                    expected_entity_id,
                )
                entity_registry.async_remove(registry_entry.entity_id)
                continue

            # Remove stale conflicting entry mapped to another/old config entry.
            if (
                existing.unique_id == registry_entry.unique_id
                and existing.platform == DOMAIN
                and existing.config_entry_id != entry.entry_id
            ):
                _LOGGER.debug(
                    "Removing legacy conflicting geolocation %s",
                    existing.entity_id,
                )
                entity_registry.async_remove(existing.entity_id)
            else:
                _LOGGER.debug(
                    "Skipping normalization of %s because %s already exists",
                    registry_entry.entity_id,
                    expected_entity_id,
                )
                continue

        try:
            entity_registry.async_update_entity(
                registry_entry.entity_id, new_entity_id=expected_entity_id
            )
            _LOGGER.debug(
                "Normalized geolocation entity_id %s -> %s",
                registry_entry.entity_id,
                expected_entity_id,
            )
        except ValueError:
            _LOGGER.debug(
                "Unable to normalize geolocation entity_id %s -> %s",
                registry_entry.entity_id,
                expected_entity_id,
            )


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
    radius = entry.options.get(CONF_RADIUS, DEFAULT_RADIUS)
    if hass.config.units is IMPERIAL_SYSTEM:
        radius = METRIC_SYSTEM.length(radius, UnitOfLength.MILES)
    await _async_preload_dateparser(hass)
    # Create feed entity coordinator for all platforms.
    coordinator = IngvDataUpdateCoordinator(hass=hass, entry=entry, radius_in_km=radius)
    feeds[entry.entry_id] = coordinator
    _LOGGER.debug("Feed entity coordinator added for %s", entry.entry_id)
    _normalize_geo_entity_ids(hass, entry)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate config entry."""
    _LOGGER.debug("Migrating %s from version %s", entry.entry_id, entry.version)

    if entry.version > 2:
        _LOGGER.error(
            "Cannot migrate %s from unsupported version %s",
            entry.entry_id,
            entry.version,
        )
        return False

    migrated_version = entry.version

    if entry.version < 2:
        _normalize_geo_entity_ids(hass, entry, remove_without_unique_id=True)
        hass.config_entries.async_update_entry(entry, version=2)
        migrated_version = 2

    _LOGGER.info("Migration to version %s successful", migrated_version)
    return True


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

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, radius_in_km: float
    ) -> None:
        """Initialize the Feed Entity Coordinator."""
        self.entry = entry
        self.hass = hass
        minimum_magnitude = entry.options.get(
            CONF_MINIMUM_MAGNITUDE, DEFAULT_MINIMUM_MAGNITUDE
        )
        start_time = entry.options.get(CONF_START_TIME, DEFAULT_START_TIME)
        scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        coordinates = (
            entry.data[CONF_LATITUDE],
            entry.data[CONF_LONGITUDE],
        )
        websession = async_get_clientsession(hass)
        self._feed_manager = IngvCentroNazionaleTerremotiQuakeMLFeedManager(
            websession=websession,
            coordinates=coordinates,
            filter_radius=radius_in_km,
            filter_minimum_magnitude=minimum_magnitude,
            starttime_delta=timedelta(hours=start_time),
            generate_async_callback=self._generate_entity,
            update_async_callback=self._update_entity,
            remove_async_callback=self._remove_entity,
            status_async_callback=self._status_update,
        )
        self._entry_id = entry.entry_id
        self._status_info = None
        self._active_event_ids: set[str] = set()
        self._pending_removed_event_ids: set[str] = set()
        self._event_id_to_external_id: dict[str, str] = {}
        self._is_unloading = False
        self._entity_ids_normalized = False
        self.listeners: list[Callable[[], None]] = []
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=f"{DOMAIN}-{entry.data[CONF_LOCATION]}",
            update_method=self.async_update,
            update_interval=timedelta(seconds=scan_interval),
        )

    async def async_update(self) -> None:
        """Refresh data."""
        self._pending_removed_event_ids.clear()
        if inspect.iscoroutinefunction(self._feed_manager.update):
            await self._feed_manager.update()
        else:
            await self.hass.async_add_executor_job(self._feed_manager.update)

        status = self._status_info.status if self._status_info else None
        if status == UPDATE_OK:
            if not self._entity_ids_normalized:
                _normalize_geo_entity_ids(self.hass, self.entry)
                self._entity_ids_normalized = True

            current_feed_event_ids = {
                _extract_event_id(external_id)
                for external_id in self._feed_manager.feed_entries
            }
            stale_event_ids = self._active_event_ids.difference(
                current_feed_event_ids
            )
            remove_event_ids = self._pending_removed_event_ids.union(stale_event_ids)
            for event_id in remove_event_ids:
                # Ignore transient remove/create transitions of the same event.
                if event_id in current_feed_event_ids:
                    continue
                if event_id in self._active_event_ids:
                    async_dispatcher_send(self.hass, f"{DOMAIN}_delete_{event_id}")
                    self._active_event_ids.discard(event_id)
                    self._event_id_to_external_id.pop(event_id, None)
            for external_id in self._feed_manager.feed_entries:
                event_id = _extract_event_id(external_id)
                self._event_id_to_external_id[event_id] = external_id
            self._cleanup_stale_geo_entities(current_feed_event_ids)
        elif status == UPDATE_ERROR:
            _LOGGER.debug(
                "Feed update failed; keeping %s active entities",
                len(self._active_event_ids),
            )

        self._pending_removed_event_ids.clear()
        _LOGGER.debug("Feed entity coordinator updated")
        return self._feed_manager.feed_entries

    async def async_stop(self) -> None:
        """Stop this feed entity coordinator from refreshing."""
        self._is_unloading = True
        for unsub_dispatcher in self.listeners:
            unsub_dispatcher()
        self.listeners = []
        self._pending_removed_event_ids.clear()
        self._active_event_ids.clear()
        self._event_id_to_external_id.clear()
        _LOGGER.debug("Feed entity coordinator stopped")

    @property
    def is_unloading(self) -> bool:
        """Return whether the config entry is unloading/reloading."""
        return self._is_unloading

    @callback
    def async_event_new_entity(self) -> str:
        """Return coordinator specific event to signal new entity."""
        return f"{DOMAIN}_new_geolocation_{self._entry_id}"

    def get_entry(self, external_id):
        """Get feed entry by external id."""
        resolved_external_id = self._event_id_to_external_id.get(
            external_id, external_id
        )
        return self._feed_manager.feed_entries.get(resolved_external_id)

    def entry_available(self, external_id) -> bool:
        """Get feed entry by external id."""
        resolved_external_id = self._event_id_to_external_id.get(
            external_id, external_id
        )
        return self._feed_manager.feed_entries.get(resolved_external_id) is not None

    def status_info(self):
        """Return latest status update info received."""
        return self._status_info

    async def _generate_entity(self, external_id: str) -> None:
        """Generate new entity."""
        event_id = _extract_event_id(external_id)
        self._event_id_to_external_id[event_id] = external_id
        if event_id in self._active_event_ids:
            _LOGGER.debug(
                "Skipping duplicate geolocation creation for event: %s", event_id
            )
            return

        self._active_event_ids.add(event_id)
        _LOGGER.debug("New entry received for event: %s", event_id)
        async_dispatcher_send(
            self.hass,
            self.async_event_new_entity(),
            self,
            self.entry.unique_id,
            event_id,
        )

    async def _update_entity(self, external_id: str) -> None:
        """Ignore update call; this is handled by the coordinator."""

    async def _remove_entity(self, external_id: str) -> None:
        """Queue entity removal and process it after update status is known."""
        event_id = _extract_event_id(external_id)
        _LOGGER.debug("Remove received for event: %s", event_id)
        self._pending_removed_event_ids.add(event_id)

    async def _status_update(self, status_info) -> None:
        """Store status update."""
        _LOGGER.debug("Status update received: %s", status_info)
        self._status_info = status_info

    @callback
    def _cleanup_stale_geo_entities(self, current_feed_event_ids: set[str]) -> None:
        """Remove stale geo_location registry entities not present in current feed."""
        if not self.entry.unique_id:
            return

        entity_registry = er.async_get(self.hass)
        unique_id_prefix = f"{self.entry.unique_id}_"
        for registry_entry in er.async_entries_for_config_entry(
            entity_registry, self.entry.entry_id
        ):
            if registry_entry.platform != DOMAIN:
                continue
            if not registry_entry.entity_id.startswith("geo_location."):
                continue
            unique_id = registry_entry.unique_id or ""
            if not unique_id.startswith(unique_id_prefix):
                continue

            event_id = unique_id[len(unique_id_prefix) :]
            if not event_id or event_id in current_feed_event_ids:
                continue

            _LOGGER.debug(
                "Removing stale geolocation registry entity %s (event %s not in feed)",
                registry_entry.entity_id,
                event_id,
            )
            entity_registry.async_remove(registry_entry.entity_id)
