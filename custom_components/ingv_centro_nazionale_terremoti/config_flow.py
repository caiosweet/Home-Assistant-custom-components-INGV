"""Config flow for INGV Earthquakes integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import (
    CONF_LATITUDE,
    CONF_LOCATION,
    CONF_LONGITUDE,
    CONF_RADIUS,
    CONF_SCAN_INTERVAL,
)
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_MINIMUM_MAGNITUDE,
    CONF_START_TIME,
    DEFAULT_MINIMUM_MAGNITUDE,
    DEFAULT_RADIUS,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_START_TIME,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class IngvConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for INGV Earthquakes integration."""

    VERSION = 1

    async def _show_form(self, errors: dict[str, Any] | None = None) -> FlowResult:
        """Show the form to the user."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_LOCATION, default=self.hass.config.location_name
                    ): str,
                    vol.Optional(
                        CONF_LATITUDE, default=self.hass.config.latitude
                    ): cv.latitude,
                    vol.Optional(
                        CONF_LONGITUDE, default=self.hass.config.longitude
                    ): cv.longitude,
                }
            ),
            errors=errors or {},
        )

    async def async_step_import(self, import_config: dict[str, Any]) -> FlowResult:
        """Import a config entry from configuration.yaml."""
        _LOGGER.debug("Import config from: %s", import_config.get("platform", DOMAIN))
        return await self.async_step_user(import_config)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the start of the config flow."""
        _LOGGER.debug("User input: %s", user_input)

        if not user_input:
            return await self._show_form()

        location = user_input.get(CONF_LOCATION, self.hass.config.location_name)
        await self.async_set_unique_id(location)
        self._abort_if_unique_id_configured()

        latitude = user_input.get(CONF_LATITUDE, self.hass.config.latitude)
        longitude = user_input.get(CONF_LONGITUDE, self.hass.config.longitude)

        data = {
            CONF_LOCATION: location,
            CONF_LATITUDE: latitude,
            CONF_LONGITUDE: longitude,
        }

        magnitude = user_input.get(CONF_MINIMUM_MAGNITUDE, DEFAULT_MINIMUM_MAGNITUDE)
        radius = user_input.get(CONF_RADIUS, DEFAULT_RADIUS)
        scan_interval = user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        start_time = user_input.get(CONF_START_TIME, DEFAULT_START_TIME)

        options = {
            CONF_MINIMUM_MAGNITUDE: magnitude,
            CONF_RADIUS: radius,
            CONF_SCAN_INTERVAL: scan_interval,
            CONF_START_TIME: start_time,
        }

        return self.async_create_entry(title=location, data=data, options=options)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> IngvOptionsFlow:
        """Get the options flow for this handler."""
        return IngvOptionsFlow(config_entry)


class IngvOptionsFlow(OptionsFlow):
    """Handle a option flow for INGV Earthquakes integration."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.options = config_entry.options

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle options flow."""
        if not user_input:
            return self.async_show_form(
                step_id="init",
                data_schema=vol.Schema(
                    {
                        vol.Optional(
                            CONF_MINIMUM_MAGNITUDE,
                            default=self.options.get(
                                CONF_MINIMUM_MAGNITUDE, DEFAULT_MINIMUM_MAGNITUDE
                            ),
                        ): cv.positive_float,
                        vol.Optional(
                            CONF_RADIUS,
                            default=self.options.get(CONF_RADIUS, DEFAULT_RADIUS),
                        ): vol.Coerce(float),
                        vol.Optional(
                            CONF_SCAN_INTERVAL,
                            default=self.options.get(
                                CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                            ),
                        ): cv.positive_int,
                        vol.Optional(
                            CONF_START_TIME,
                            default=self.options.get(
                                CONF_START_TIME, DEFAULT_START_TIME
                            ),
                        ): cv.positive_int,
                    }
                ),
            )

        return self.async_create_entry(title="", data=user_input)
