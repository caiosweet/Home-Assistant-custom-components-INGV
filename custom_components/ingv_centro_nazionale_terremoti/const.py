"""Define constants for the INGV Earthquakes integration."""

from typing import Final

from homeassistant.const import Platform

from .version import __version__

DOMAIN: Final = "ingv_centro_nazionale_terremoti"
DEFAULT_NAME: Final = "INGV Earthquakes"

ATTR_CREATED: Final = "created"
ATTR_LAST_UPDATE: Final = "last_update"
ATTR_LAST_UPDATE_SUCCESSFUL: Final = "last_update_successful"
ATTR_LAST_TIMESTAMP: Final = "last_timestamp"
ATTR_REMOVED: Final = "removed"
ATTR_STATUS: Final = "status"
ATTR_UPDATED: Final = "updated"

CONF_MINIMUM_MAGNITUDE: Final = "minimum_magnitude"
CONF_START_TIME: Final = "start_time"

DEFAULT_FORCE_UPDATE: Final = True
DEFAULT_MINIMUM_MAGNITUDE: Final = 3.0
DEFAULT_RADIUS: Final = 50.0
DEFAULT_SCAN_INTERVAL: Final = 300
DEFAULT_START_TIME: Final = 24
DEFAULT_UNIT_OF_MEASUREMENT: Final = "quakes"

FEED: Final = "feed"

IMAGE_URL_PATTERN: Final = (
    "https://shakemap.ingv.it/data/{}/current/products/intensity.jpg"
)

PLATFORMS: Final = [Platform.SENSOR, Platform.GEO_LOCATION]

SOURCE: Final = "ingv_centro_nazionale_terremoti"

VERSION: Final = __version__
