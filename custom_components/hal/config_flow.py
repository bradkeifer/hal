"""Config flow for HAL CA1006 multi-zone amplifier integration."""

import logging
from typing import Any

import voluptuous as vol
from halca1006 import HALProtocol  # type: ignore[import-not-found]

from homeassistant import config_entries, core, exceptions
from homeassistant.const import CONF_HOST, CONF_PORT

from .const import (
    DOMAIN,
    CONF_HAL_NAME,
    DEFAULT_HAL_NAME,
    CONF_HAL_SELECT_INTERVAL,
    DEFAULT_SELECT_INTERVAL,
    CONF_ZONE_1,
    CONF_ZONE_2,
    CONF_ZONE_3,
    CONF_ZONE_4,
    CONF_ZONE_5,
    CONF_ZONE_6,
    CONF_SOURCE_1,
    CONF_SOURCE_2,
    CONF_SOURCE_3,
    CONF_SOURCE_4,
    CONF_SOURCE_5,
    CONF_SOURCE_6,
    CONF_SOURCE_7,
    CONF_SOURCE_8,
    HAL_ZONE_1_VALID,
    HAL_ZONE_2_VALID,
    HAL_ZONE_3_VALID,
    HAL_ZONE_4_VALID,
    HAL_ZONE_5_VALID,
    HAL_ZONE_6_VALID,
    HAL_SOURCE_1_VALID,
    HAL_SOURCE_2_VALID,
    HAL_SOURCE_3_VALID,
    HAL_SOURCE_4_VALID,
    HAL_SOURCE_5_VALID,
    HAL_SOURCE_6_VALID,
    HAL_SOURCE_7_VALID,
    HAL_SOURCE_8_VALID,
)

HAL_TESTS_PASSED = 1
HAL_CANNOT_CONNECT = 2
HAL_NOT_HAL = 3
HAL_VERSION_UNKNOWN = "version unknown"

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default="localhost"): str,
        vol.Required(CONF_PORT, default=7000): int,
        vol.Optional(CONF_HAL_NAME, default=DEFAULT_HAL_NAME): str,
        # vol.Optional(CONF_SCAN_INTERVAL, default=10): int,
        vol.Optional(CONF_HAL_SELECT_INTERVAL, default=DEFAULT_SELECT_INTERVAL): float,
        vol.Optional(
            HAL_ZONE_1_VALID,
            default=True,
        ): bool,
        vol.Optional(
            CONF_ZONE_1,
            default="Zone 1",
        ): str,
        vol.Optional(
            HAL_ZONE_2_VALID,
            default=True,
        ): bool,
        vol.Optional(
            CONF_ZONE_2,
            default="Zone 2",
        ): str,
        vol.Optional(
            HAL_ZONE_3_VALID,
            default=True,
        ): bool,
        vol.Optional(
            CONF_ZONE_3,
            default="Zone 3",
        ): str,
        vol.Optional(
            HAL_ZONE_4_VALID,
            default=True,
        ): bool,
        vol.Optional(
            CONF_ZONE_4,
            default="Zone 4",
        ): str,
        vol.Optional(
            HAL_ZONE_5_VALID,
            default=True,
        ): bool,
        vol.Optional(
            CONF_ZONE_5,
            default="Zone 5",
        ): str,
        vol.Optional(
            HAL_ZONE_6_VALID,
            default=True,
        ): bool,
        vol.Optional(
            CONF_ZONE_6,
            default="Zone 6",
        ): str,
        vol.Required(
            HAL_SOURCE_1_VALID,
            default=True,
        ): bool,
        vol.Optional(
            CONF_SOURCE_1,
            default="Source 1",
        ): str,
        vol.Required(
            HAL_SOURCE_2_VALID,
            default=True,
        ): bool,
        vol.Optional(
            CONF_SOURCE_2,
            default="Source 2",
        ): str,
        vol.Required(
            HAL_SOURCE_3_VALID,
            default=True,
        ): bool,
        vol.Optional(
            CONF_SOURCE_3,
            default="Source 3",
        ): str,
        vol.Required(
            HAL_SOURCE_4_VALID,
            default=True,
        ): bool,
        vol.Optional(
            CONF_SOURCE_4,
            default="Source 4",
        ): str,
        vol.Required(
            HAL_SOURCE_5_VALID,
            default=True,
        ): bool,
        vol.Optional(
            CONF_SOURCE_5,
            default="Source 5",
        ): str,
        vol.Required(
            HAL_SOURCE_6_VALID,
            default=True,
        ): bool,
        vol.Optional(
            CONF_SOURCE_6,
            default="Source 6",
        ): str,
        vol.Required(
            HAL_SOURCE_7_VALID,
            default=True,
        ): bool,
        vol.Optional(
            CONF_SOURCE_7,
            default="Source 7",
        ): str,
        vol.Required(
            HAL_SOURCE_8_VALID,
            default=True,
        ): bool,
        vol.Optional(
            CONF_SOURCE_8,
            default="Source 8",
        ): str,
    }
)


class HALTests:
    """Basic tests to validate configuration."""

    def __init__(self, host: str, port: int) -> None:
        """Initialize."""
        _LOGGER.debug("HALTests.__init__(): host = %s, port = %d", host, port)
        self.host = host
        self.port = port

    async def validate(self, hass) -> dict:
        """Test if we can authenticate with the host."""
        _LOGGER.debug("HALTests.validate()")
        validate_results = {
            "connect": HAL_TESTS_PASSED,
            "is_hal": HAL_TESTS_PASSED,
            "fw_version": HAL_VERSION_UNKNOWN,
        }
        hal = HALProtocol(self.host, self.port)
        _LOGGER.debug("Enabling HALProtocol logger")
        hal.enable_logger()
        _LOGGER.debug("Checking we can connect to HAL at %s, %d", self.host, self.port)
        if not await hass.async_add_executor_job(hal.connect):
            _LOGGER.error(
                "HALTests.validate: Unable to connect. Returning HAL_CANNOT_CONNECT."
            )
            validate_results["connect"] = HAL_CANNOT_CONNECT
        else:
            # TODO(@bradkeifer): add an is_hal() method to HALProtocol to validate
            #      we are connecting to a HAL unit. Throw InvalidAuth if it's not a HAL.
            validate_results["fw_version"] = await hass.async_add_executor_job(
                hal.get_version
            )
            await hass.async_add_executor_job(hal.disconnect)
        _LOGGER.debug("HALTests.validate() complete. Results are %s.", validate_results)

        return validate_results


async def validate_input(
    hass: core.HomeAssistant, data: dict[str, Any]
) -> dict[str, str]:
    """
    Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    _LOGGER.debug("Instantiate HALTests")
    hal_tests = HALTests(data["host"], data["port"])
    test_results = await hal_tests.validate(hass)
    if test_results["connect"] == HAL_CANNOT_CONNECT:
        raise CannotConnect
    if test_results["is_hal"] == HAL_NOT_HAL:
        raise InvalidAuth

    # Obtain firmware version of the HAL
    fw_version = HAL_VERSION_UNKNOWN
    fw_version = test_results["fw_version"]
    _LOGGER.debug("HAL firmware version is %s.", fw_version)

    _LOGGER.debug("HALTests Completed")

    # Return info that you want to store in the config entry.
    return {
        "title": data[CONF_HAL_NAME],
        "sw_version": fw_version,
    }


class HALConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HAL CA1006 multi-zone amplifier."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize."""
        self.hal = None
        self.host = None
        self.port = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            _LOGGER.debug("Set unique identifier to %s", user_input[CONF_HAL_NAME])
            await self.async_set_unique_id(user_input[CONF_HAL_NAME])
            self._abort_if_unique_id_configured()
            user_input["sw_version"] = info["sw_version"]
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """
        Handle the reconfiguration step.

        TODO<@bradkeifer>: Populate form with existing config values
        """
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_HAL_NAME])
            self._abort_if_unique_id_mismatch()
            return self.async_update_reload_and_abort(
                self._get_reconfigure_entry(),
                data_updates=user_input,
            )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=STEP_USER_DATA_SCHEMA,
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""
