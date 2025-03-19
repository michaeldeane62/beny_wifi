"""Constants for custom component."""
from enum import Enum  # noqa: D100
from typing import Final
from homeassistant.const import Platform
import logging

PLATFORMS: Final = [Platform.SENSOR]

NAME: Final = "Beny Wifi"
DOMAIN: Final = "beny_wifi"
MODEL = "model"
SERIAL = "serial"

SCAN_INTERVAL: Final = "update_interval"

DEFAULT_SCAN_INTERVAL: Final = 30
DEFAULT_PORT = 3333 # default listening port (at least for BCP-AT1N-L)

IP_ADDRESS = "ip_address"
PORT = "port"
CONF_SERIAL = "serial"
CONF_PIN = "pin"

_LOGGER = logging.getLogger(__name__)

def calculate_checksum(data: str) -> int:
    """Calculate checksum of the message.

    Args:
        data (str): message as ascii hex string

    Returns:
        int: checksum

    """

    # if there is a placeholder in command message, skip that one
    if "[checksum]" in data:
        data = data[:-len("[checksum]")]
    else:
        data = data[:-2]

    return sum([int(data[i:i+2], 16) for i in range(0, len(data), 2)]) % 256

def get_checksum(data: str) -> int:
    """Get last digits containing checksum.

    Args:
        data (str): message as ascii hex string

    Returns:
        int: checksum

    """
    return int(data[-2:], 16)

def validate_checksum(data: str) -> bool:
    """Validate checksum message vs calculated.

    Args:
        data (str): message as ascii hex string

    Returns:
        bool: checksums match

    """
    msg_checksum = get_checksum(data)
    calc_checksum = calculate_checksum(data)

    if msg_checksum != calc_checksum:
        _LOGGER.debug(f"Calculated checksum does not match: msg={msg_checksum} calc={calc_checksum} data={data}")  # noqa: G004

    return msg_checksum == calc_checksum

class CHARGER_STATE(Enum):
    """Charger states."""

    ABNORMAL = 0
    UNPLUGGED = 1
    STANDBY = 2
    STARTING = 3
    UNKNOWN = 4
    WAITING = 5
    CHARGING = 6

class TIMER_STATE(Enum):
    """Timer states."""

    UNSET = 0
    START_TIME = 1
    END_TIME = 2
    START_END_TIME = 3

class CHARGER_COMMAND(Enum):
    """Charger commands."""

    STOP = 0
    START = 1

class REQUEST_TYPE(Enum):
    """Request type to retrieve data from charger."""

    VALUES = 112
    SETTINGS = 113
    MODEL = 4

class COMMON(Enum):
    """Common mapping for fixed message contents."""

    FIXED_PART = {
        "description": "Header of message",
        "structure": {
            "header": slice(0, 4),
            "version": slice(4, 6),
            "message_id": slice(6, 10)
        },
    }

class CLIENT_MESSAGE(Enum):
    """Client message definitions. Defines structures of the messages sent to charger."""

    POLL_DEVICES = {
        "description": "Send broadcast to 255.255.255.255 and wait for answers",
        "hex": "55aa03000f000[pin]03[serial][checksum]",
        "structure": {
            "pin": slice(13,18),
            "serial": slice(20,28)
        }
    }
    REQUEST_DATA = {
        "description": "Update request 1",
        "hex": "55aa10000b000[pin][request_type][checksum]",
        "structure": {
            "pin": slice(13,18),
            "request_type": slice(18, 20)
        }
    }
    SEND_CHARGER_COMMAND = {
        "description": "Start or stop charging",
        "hex": "55aa10000c000[pin]06[charger_command][checksum]",
        "structure": {
            "pin": slice(13,18),
            "charger_command": slice(21, 22)
        }
    }
    SET_TIMER = {
        "description": "Set timer",
        "hex": "55aa10001c000[pin]6900016008000[end_timer_set][start_h][start_min]00[end_h][end_min]0017153b[checksum]",
        "structure": {
            "pin": slice(13,18),
            "start_h": slice(35, 38),
            "start_min": slice(38, 40),
            "end_h": slice(42, 44),
            "end_min": slice(44, 46),
            "end_timer_set": slice(31, 35)
        }
    }
    RESET_TIMER = {
        "description": "Reset timer",
        "hex": "55aa10001c000[pin]690000000000000000000000000000171035[checksum]",
        "structure": {
            "pin": slice(13,18)
        }
    }
    REQUEST_SETTINGS = {
        "description": "Request settings",
        "hex": "55aa10000b000[pin]71[checksum]",
        "structure": {
            "pin": slice(13,18)
        }
    }
    SET_SCHEDULE = {
        "description": "Set schedule",
        "hex": "55aa100016000[pin]7519010e0f2725[weekdays][start_h][start_min][end_h][end_min][checksum]",
        "structure": {
            "pin": slice(13,18),
            "weekdays": slice(32, 34),
            "start_h": slice(34, 36),
            "start_min": slice(36, 38),
            "end_h": slice(38, 40),
            "end_min": slice(40, 42)
        }
    }
    SET_MAX_MONTHLY_CONSUMPTION = {
        "description": "Set maximum monthly consumption",
        "hex": "55aa10000d000[pin]78[maximum_consumption][checksum]",
        "structure": {
            "pin": slice(13,18),
            "maximum_consumption": slice(20, 24)
        }
    }
    SET_MAX_SESSION_CONSUMPTION = {
        "description": "Set maximum session consumption",
        "hex": "55aa10000c000[pin]74[maximum_consumption][checksum]",
        "structure": {
            "pin": slice(13,18),
            "maximum_consumption": slice(20, 22)
        }
    }

    # DO NOT USE, UNCONFIRMED PARAMETERS
    SET_VALUES = {
        "description": "Send setting values to charger",
        "hex": "55aa10000d000[pin]6d00[max_amps][checksum]",
        "structure": {
            "pin": slice(13,18)
        }
    }

class SERVER_MESSAGE(Enum):
    """Server message definitions. Defines structures translated from the charger messages."""

    HANDSHAKE = {
        "description": "Receive charger handshake",
        "structure": {
            "serial": slice(12, 20),
            "ip": slice(20, 28, 2),
            "port": slice(28, 32)

        }
    }
    SEND_MODEL = {
        "description": "Receive model from charger",
        "structure": {
            "request_type": slice(10, 12),
            "model": slice(12, -2)
        }
    }
    SEND_VALUES = {
        "description": "Receive values from charger",
        "structure": {
            "request_type": slice(10, 12),
            "current1": slice(13, 14),
            "current2": slice(15, 16),
            "current3": slice(17, 18),
            "voltage1": slice(20, 22),
            "voltage2": slice(24, 26),
            "voltage3": slice(28, 30),
            "power": slice(30, 34),
            "total_kwh": slice(34, 38),
            "state": slice(40, 42),
            "timer_state": slice(42, 44),
            "max_current": slice(56, 58),
            "timer_start_h": slice(44, 46),
            "timer_start_min": slice(46, 48),
            "timer_end_h": slice(50, 52),
            "timer_end_min": slice(52, 54),
            "maximum_session_consumption": slice(58, 60)
        }
    }
    ACCESS_DENIED = {
        "description": "Access denied message",
        "structure": {}
    }

    SEND_SETTINGS = {
        "description": "Receive settings from charger",
        "structure": {
            "weekdays": slice(30, 32),
            "timer_start_h": slice(32, 34),
            "timer_start_min": slice(34, 36),
            "timer_end_h": slice(36, 38),
            "timer_end_min": slice(38, 40),

        }
    }
