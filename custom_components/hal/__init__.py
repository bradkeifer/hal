"""The HAL CA1006 multi-zone amplifier integration."""

import asyncio
from datetime import timedelta

import voluptuous as vol

# from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from homeassistant.config_entries import ConfigEntry, SOURCE_IMPORT
from homeassistant.core import HomeAssistant

from homeassistant.helpers import device_registry as dr

from .const import (
    DOMAIN,
    MANUFACTURER,
    MODEL,
    CONF_HAL_NAME,
    DEFAULT_HAL_NAME,
    CONF_HAL_SELECT_INTERVAL,
    DEFAULT_SELECT_INTERVAL,
    HAL_OBJECT,
    HAL_COORDINATOR,
    HAL_VERSION,
    HAL_SCAN_INTERVAL,
    HAL_CONNECT_RETRY_INTERVAL,
    SERVICE_TURN_OFF,
    SERVICE_SET_SELECT_INTERVAL,
)

SERVICE_TURN_OFF_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HAL_NAME, default=DEFAULT_HAL_NAME): str,
    }
)

SERVICE_SET_SELECT_INTERVAL_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HAL_NAME, default=DEFAULT_HAL_NAME): str,
        vol.Required(CONF_HAL_SELECT_INTERVAL, default=DEFAULT_SELECT_INTERVAL): float,
    }
)

PLATFORMS = ["media_player"]

from homeassistant.components.media_player import PLATFORM_SCHEMA, MediaPlayerEntity
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
    EVENT_HOMEASSISTANT_STOP,
)
from homeassistant.core import callback

from halca1006 import HALProtocol
import logging

_LOGGER = logging.getLogger(__name__)
hal_collect = {}


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the HAL CA1006 multi-zone amplifier component."""
    _LOGGER.debug(f"hal.__init__.async_setup():hass ={hass}, config = {config}")
    hass.data.setdefault(DOMAIN, {})
    conf = config.get(DOMAIN)
    _LOGGER.debug(f"hal.__init__.async_setup():config.get({DOMAIN}) = {conf}")

    # Setup services
    _LOGGER.debug(f"async_setp: Setting up services.")

    _LOGGER.debug(f"Defining turn_off service")

    async def turn_off(service):
        """Turn off all zones."""
        hal_name = service.data[CONF_HAL_NAME]
        _LOGGER.debug(f"turn_off: Turning off HAL unit {hal_name} from {hal_collect}.")
        await hass.async_add_executor_job(hal_collect[hal_name].turn_off)

    _LOGGER.debug(
        f"async_setp: Registering service {SERVICE_TURN_OFF} for domain {DOMAIN} "
        f"with schema {SERVICE_TURN_OFF_SCHEMA}."
    )
    hass.services.async_register(
        DOMAIN, SERVICE_TURN_OFF, turn_off, schema=SERVICE_TURN_OFF_SCHEMA
    )

    _LOGGER.debug(f"Defining set_select_interval service")

    async def set_select_interval(service):
        """Turn off all zones."""
        hal_name = service.data[CONF_HAL_NAME]
        select_interval = service.data[CONF_HAL_SELECT_INTERVAL]
        _LOGGER.debug(
            f"turn_off: Setting select interval on HAL unit {hal_name} to {select_interval}."
        )
        await hass.async_add_executor_job(
            hal_collect[hal_name].set_select_interval, select_interval
        )

    _LOGGER.debug(
        f"async_setp: Registering service {SERVICE_SET_SELECT_INTERVAL} for domain {DOMAIN} "
        f"with schema {SERVICE_SET_SELECT_INTERVAL_SCHEMA}."
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_SELECT_INTERVAL,
        set_select_interval,
        schema=SERVICE_SET_SELECT_INTERVAL_SCHEMA,
    )

    if not conf:
        return True

    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_IMPORT},
            data=conf,
        )
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up HAL CA1006 multi-zone amplifier from a config entry."""
    _LOGGER.debug(f"hal.__init__.async_setup_entry():hass ={hass}, entry = {entry}")
    _LOGGER.debug(
        f"entry.domain {entry.domain}, "
        f"entry.title {entry.title}, "
        f"entry.version {entry.version}, "
        f"entry.data {entry.data}, "
        f"entry.source {entry.source}, "
        f"entry.options {entry.options}, "
        f"entry.unique_id {entry.unique_id}, "
        f"entry.entry_id {entry.entry_id}, "
        f"entry.state {entry.state}."
    )

    _LOGGER.debug(
        f"async_setup_entry:Adding HALProtocol API to hass.data[{DOMAIN}][{entry.entry_id}]"
    )
    hal = hal_collect[entry.data[CONF_HAL_NAME]] = HALProtocol(
        entry.data[CONF_HOST],
        entry.data[CONF_PORT],
        name=entry.data[CONF_HAL_NAME],
    )
    hass.data[DOMAIN][entry.entry_id] = hal
    _LOGGER.debug(
        f"async_setup_entry:hass.data[{DOMAIN}][entry.entry_id] = {hass.data[DOMAIN][entry.entry_id]}"
    )

    # Manually register a device for the overall HAL unit
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.data[CONF_HAL_NAME])},
        manufacturer=MANUFACTURER,
        name=entry.data[CONF_HAL_NAME],
        model=MODEL,
        sw_version=entry.data["sw_version"],
    )
    # We need to centralize connection/disconnection logic since we have more than one platform
    while not await hass.async_add_executor_job(hal.connect):
        _LOGGER.warning(
            f"Unable to connect to HAL at {entry.data[CONF_PORT]}:{entry.data[CONF_PORT]}. "
            f"Retry in {HAL_CONNECT_RETRY_INTERVAL} seconds"
        )
        asyncio.sleep(HAL_CONNECT_RETRY_INTERVAL)

    await hass.async_add_executor_job(hal.enable_logger)
    await hass.async_add_executor_job(
        hal.set_select_interval, entry.data[CONF_HAL_SELECT_INTERVAL]
    )

    _LOGGER.debug(
        f"hal.__init__.async_setup_entry: Setting up entry {entry} for platforms {PLATFORMS}."
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""

    # Disconnect from HAL gracefully before unloading
    hal = hass.data[DOMAIN][entry.entry_id]
    _LOGGER.debug(
        f"async_unload_entry: Disconnecting from HAL {entry.data[CONF_HAL_NAME]}"
        f" with handle {hal}."
    )
    await hass.async_add_executor_job(hal.disconnect)

    _LOGGER.debug(f"async_unload_entry: hass {hass}, entry {entry}.")
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    _LOGGER.debug(f"async_unload_entry: unload_ok {unload_ok}.")
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
