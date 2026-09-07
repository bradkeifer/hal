"""Diagnostics support for HAL."""

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from .coordinator import HALConfigEntry

TO_REDACT = []


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: HALConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""

    return {
        "entry_data": async_redact_data(entry.data, TO_REDACT),
        "data": entry.runtime_data.data,
    }


async def async_get_device_diagnostics(
    hass: HomeAssistant, entry: HALConfigEntry, device: DeviceEntry
) -> dict[str, Any]:
    """Return diagnostics for a device."""
    appliance = _get_appliance_by_device_id(hass, device.id)
    return {
        "details": async_redact_data(appliance.raw_data, TO_REDACT),
        "data": appliance.data,
    }
