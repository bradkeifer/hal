"""The HAL integration base entity."""

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL


class HALEntity(CoordinatorEntity):
    """Base class for HAL entities."""

    def __init__(self, coordinator, name, version="TBD"):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._name = name
        self.base_unique_id = "_".join(name)
        self._version = version

    @property
    def device_info(self):
        """Powerwall device info."""
        device_info = {
            "identifiers": {(DOMAIN, self.base_unique_id)},
            "name": self._name,
            "manufacturer": MANUFACTURER,
        }
        device_info["model"] = MODEL
        device_info["sw_version"] = self._version
        return device_info
