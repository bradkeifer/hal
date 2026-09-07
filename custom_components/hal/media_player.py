"""The HAL CA1006 multi-zone amplifier integration."""

from datetime import timedelta
from typing import Optional
import logging
import sys

import async_timeout

from homeassistant.helpers.entity import Entity
import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    EVENT_HOMEASSISTANT_STOP,
    STATE_OFF,
    STATE_ON,
)
from homeassistant.core import callback

from .const import (
    DOMAIN,
    PLATFORM,
    PLATFORM_NAME,
    MANUFACTURER,
    MODEL,
    CONF_ZONES,
    CONF_SOURCES,
    CONF_HAL_NAME,
    HAL_ZONES,
    HAL_SOURCES,
    HAL_ON,
    HAL_OFF,
    HAL_MUTED,
    HAL_NOT_MUTED,
    HAL_SCAN_INTERVAL,
    HAL_MODULE,
)

# CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

from homeassistant.components.media_player import (
    PLATFORM_SCHEMA,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
)

PLATFORMS = ["media_player"]

SUPPORT_HAL = (
    MediaPlayerEntityFeature.VOLUME_MUTE
    | MediaPlayerEntityFeature.VOLUME_SET
    | MediaPlayerEntityFeature.TURN_ON
    | MediaPlayerEntityFeature.TURN_OFF
    | MediaPlayerEntityFeature.SELECT_SOURCE
)

# from hal import HALProtocol

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the HAL CA1006 multi-zone amplifier component."""
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    _LOGGER.debug(f"async_unload_entry: media_player entry {entry}")
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_setup_entry(hass, config, async_add_entities):
    """Set up the HAL CA1006 platform."""

    _LOGGER.debug(f"async_setup_platform: config {config}")
    _LOGGER.debug(f"async_setup_platform: config data {config.data}")

    hal = hass.data[DOMAIN][config.entry_id]

    # Determine sources and zones
    valid_zones = {}
    for i in range(1, HAL_ZONES + 1):
        _LOGGER.debug(f"async_setup_platform: Checking if zone {i} should de defined.")
        if config.data[f"zone_{i}_valid"]:
            _LOGGER.debug("Yes it is!")
            valid_zones[f"{i}"] = config.data[f"zone_{i}"]
        else:
            _LOGGER.debug("No it isn't!")
    _LOGGER.debug(f"async_setup_platform: valid_zones {valid_zones}.")

    valid_sources = {}
    source_list = []
    for i in range(1, HAL_SOURCES + 1):
        _LOGGER.debug(
            f"async_setup_platform: Checking if source {i} should de defined."
        )
        if config.data[f"source_{i}_valid"]:
            _LOGGER.debug("Yes it is!")
            valid_sources[i] = config.data[f"source_{i}"]
            source_list.append(config.data[f"source_{i}"])
        else:
            _LOGGER.debug("No it isn't!")
    _LOGGER.debug(f"async_setup_platform: valid_sources {valid_sources}.")
    _LOGGER.debug(f"async_setup_platform: source_list {source_list}.")

    devices = []
    for zone_id, name in valid_zones.items():
        _LOGGER.debug(
            f"async_setup_platform: "
            f"{config.data[CONF_HAL_NAME]} zone id {zone_id} has name {name}."
        )
        dev = HALZoneDevice(
            hass,
            hal,
            config.data[CONF_HAL_NAME],
            zone_id,
            name,
            valid_sources,
            source_list,
        )
        devices.append(dev)

    # @callback
    # async def async_on_stop(event):
    #     """Shutdown cleanly when hass stops."""
    #     await hass.async_add_executor_job(hal.disconnect)

    # hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, async_on_stop)

    async_add_entities(devices, True)


# class HALDevice(Entity):
#     """Representation of a HAL CA1006 multi-zone amplifier.

#     The HALDevice provides services that are zone-independent"""

#     def __init__(self, hass, hal, hal_name, scan_interval):
#         """Initialize the HAL CA1006 device."""
#         self._hass = hass
#         self._hal = hal
#         self._hal_name = hal_name
#         self._scan_interval = scan_interval
#         _LOGGER.debug(
#             f"HALDevice: Instantianating HALDevice {self._hal_name} "
#             f"with scan interval {self._scan_interval}"
#         )

#     @property
#     def device_info(self):
#         return {
#             "identifiers": {(self._hal_name)},
#             "name": self._hal_name,
#         }

#     @property
#     def name(self):
#         """Return the name of the zone."""
#         return self._hal_name

#     @property
#     def unique_id(self) -> Optional[str]:
#         """Return a unique ID."""
#         return self._hal_name


class HALZoneDevice(MediaPlayerEntity):
    """Representation of a HAL Zone."""

    def __init__(self, hass, hal, hal_name, zone_id, name, sources, source_list):
        """Initialize the zone device."""
        super().__init__()
        self._hass = hass
        self._hal_name = hal_name
        self._name = name
        self._hal = hal
        self._zone_id = zone_id
        self._unique_id = hal_name + "." + str(zone_id)
        self._sources = sources
        self._source_list = source_list
        _LOGGER.debug(
            f"HALZoneDevice: Instantianating HALZoneDevice {self._hal_name}, "
            f"zone {self._zone_id} ({self._name})."
        )

    @property
    def device_info(self):
        return {
            "name": self._name,
            "identifiers": {(DOMAIN, self._unique_id)},
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }

    @property
    def name(self):
        """Return the name of the zone."""
        _LOGGER.debug(f"name: {self._name}")
        return self._name

    @property
    def unique_id(self):
        """Return a unique ID."""
        _LOGGER.debug(f"unique_id: {self._unique_id}")
        return self._unique_id

    @property
    def device_id(self):
        """Return a device ID."""
        _LOGGER.debug(f"device_id: {self._unique_id}")
        return self._unique_id

    @property
    def state(self):
        """Return the state of the device."""
        _LOGGER.debug("HALZoneDevice.state")
        power = self._hal.get_power(self._zone_id)
        _LOGGER.debug(f"HALZoneDevice.state: power = {power}")
        if power == HAL_ON:
            _LOGGER.debug("HALZoneDevice.state is on")
            return STATE_ON
        else:
            _LOGGER.debug("HALZoneDevice.state is off")
            return STATE_OFF

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_HAL

    @property
    def source(self):
        """Get the currently selected source."""
        source = self._hal.get_source(self._zone_id)
        _LOGGER.debug(f"HALZoneDevice.source: source = {source}")
        return self._sources[int(source)]

    @property
    def source_list(self):
        """Return a list of available input sources."""
        _LOGGER.debug(f"HALZoneDevice.source_list: source_list = {self._source_list}")
        return self._source_list

    @property
    def volume_level(self):
        """Volume level of the media player (0..1).

        Value is returned based on a range (0..100).
        Therefore float divide by 100 to get to the required range.
        """
        return float(self._hal.get_volume(self._zone_id)) / 100.0

    @property
    def device_class(self):
        return "speaker"

    @property
    def is_volume_muted(self):
        if self._hal.get_mute(self._zone_id) == HAL_MUTED:
            return True
        return False

    async def async_turn_off(self):
        """Turn off the zone."""
        await self._hass.async_add_executor_job(
            self._hal.set_power, self._zone_id, HAL_OFF
        )

    async def async_turn_on(self):
        """Turn on the zone."""
        await self._hass.async_add_executor_job(
            self._hal.set_power, self._zone_id, HAL_ON
        )

    async def async_set_volume_level(self, volume):
        """Set the volume level."""
        rvol = int(volume * 100.0)
        await self._hass.async_add_executor_job(
            self._hal.set_volume, self._zone_id, rvol
        )

    async def async_select_source(self, source):
        """Select the source input for this zone."""
        _LOGGER.debug(
            f"HALZoneDevice.async_select_source: "
            f"source = {source}, self._sources = {self._sources}"
        )
        for source_id, name in self._sources.items():
            if name.lower() != source.lower():
                continue
            _LOGGER.debug(f"Found source_id:{source_id}, for source:{source}")
            await self._hass.async_add_executor_job(
                self._hal.set_source, self._zone_id, source_id
            )
            break

    async def async_update(self):
        await self._hass.async_add_executor_job(self._hal.get_zone_info, self._zone_id)

    async def async_mute_volume(self, mute):
        """Mute the volume."""
        if mute:
            hal_mute = HAL_MUTED
        else:
            hal_mute = HAL_NOT_MUTED
        await self.hass.async_add_executor_job(
            self._hal.set_mute, self._zone_id, hal_mute
        )
