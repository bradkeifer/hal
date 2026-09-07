"""Constants for the HAL CA1006 multi-zone amplifier integration."""

DOMAIN = "hal"
PLATFORM = "hal"
PLATFORM_NAME = "hal"
MODEL = "CA1006"
MANUFACTURER = "HAL"
HAL_MODULE = "hal"
HAL_OBJECT = "hal"
HAL_COORDINATOR = "coordinator"
HAL_VERSION = "version"

CONF_HAL_NAME = "hal_name"
DEFAULT_HAL_NAME = "HAL"
CONF_HAL_SELECT_INTERVAL = "hal_select_interval"
DEFAULT_SELECT_INTERVAL = 0.5
CONF_ZONES = "zones"
CONF_SOURCES = "sources"
CONF_ZONE_1 = "zone_1"
CONF_ZONE_2 = "zone_2"
CONF_ZONE_3 = "zone_3"
CONF_ZONE_4 = "zone_4"
CONF_ZONE_5 = "zone_5"
CONF_ZONE_6 = "zone_6"
CONF_SOURCE_1 = "source_1"
CONF_SOURCE_2 = "source_2"
CONF_SOURCE_3 = "source_3"
CONF_SOURCE_4 = "source_4"
CONF_SOURCE_5 = "source_5"
CONF_SOURCE_6 = "source_6"
CONF_SOURCE_7 = "source_7"
CONF_SOURCE_8 = "source_8"

HAL_ZONE_1_VALID = "zone_1_valid"
HAL_ZONE_2_VALID = "zone_2_valid"
HAL_ZONE_3_VALID = "zone_3_valid"
HAL_ZONE_4_VALID = "zone_4_valid"
HAL_ZONE_5_VALID = "zone_5_valid"
HAL_ZONE_6_VALID = "zone_6_valid"

HAL_SOURCE_1_VALID = "source_1_valid"
HAL_SOURCE_2_VALID = "source_2_valid"
HAL_SOURCE_3_VALID = "source_3_valid"
HAL_SOURCE_4_VALID = "source_4_valid"
HAL_SOURCE_5_VALID = "source_5_valid"
HAL_SOURCE_6_VALID = "source_6_valid"
HAL_SOURCE_7_VALID = "source_7_valid"
HAL_SOURCE_8_VALID = "source_8_valid"

HAL_ZONES = 6
HAL_SOURCES = 8

HAL_ON = "01"
HAL_OFF = "00"
HAL_MUTED = "01"
HAL_NOT_MUTED = "00"

HAL_SCAN_INTERVAL = 10  # Seconds
HAL_CONNECT_RETRY_INTERVAL = 10  # Seconds

SERVICE_TURN_OFF = "turn_off"
SERVICE_SET_SELECT_INTERVAL = "set_select_interval"
