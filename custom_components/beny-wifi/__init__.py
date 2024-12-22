from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import async_add_entities
from .const import DOMAIN, COMMANDS
from .sensor import BenyStateSensor, BenyMeasurementSensor
import socket
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the charger integration using YAML (not supported yet)"""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the EV Charger integration from a config entry"""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    ip_address = entry.data["ip_address"]
    port = entry.data["port"]

    _LOGGER.info(f"Setting up charger with IP {ip_address}:{port}")

    async def fetch_state():
        """Fetch the current state and measurements from the charger"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.settimeout(5)

                if "UPDATE" not in COMMANDS:
                    raise ValueError(f"Unknown command: UPDATE")

                update_command = bytes.fromhex(COMMANDS["UPDATE"]) 
                s.sendto(update_command, (ip_address, port))

                response, _ = s.recvfrom(1024)
                _LOGGER.debug(f"Received state update: {response.hex()}")
                return response.hex()
        except socket.timeout:
            _LOGGER.warning("No response received for state update")
            return None
        except Exception as e:
            _LOGGER.error(f"Failed to fetch state update: {e}")
            return None

    async def send_command(command):
        """Send a command to the charger"""
        try:
            if command not in COMMANDS:
                raise ValueError(f"Unknown command: {command}")

            message = COMMANDS[command]

            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.settimeout(5)
                s.sendto(message, (ip_address, port))
                _LOGGER.debug(f"Sent {command} command to {ip_address}:{port}")

                response, _ = s.recvfrom(1024)
                _LOGGER.debug(f"Received response: {response.hex()}")
                return response
        except Exception as e:
            _LOGGER.error(f"Failed to send {command} command: {e}")

    async def start_charge_service(call):
        """Service to start charging"""
        response = await send_command("START")
        if response:
            _LOGGER.debug("Start command executed successfully")
        else:
            _LOGGER.warning("Failed to confirm start command")

    async def stop_charge_service(call):
        """Service to stop charging."""
        response = await send_command("STOP")
        if response:
            _LOGGER.debug("Stop command executed successfully")
        else:
            _LOGGER.warning("Failed to confirm stop command")

    # Register sensors
    async_add_entities([
        BenyStateSensor("Charger State", fetch_state),
        BenyMeasurementSensor("Voltage Phase 1", fetch_state, "voltage_1"),
        BenyMeasurementSensor("Voltage Phase 2", fetch_state, "voltage_2"),
        BenyMeasurementSensor("Voltage Phase 3", fetch_state, "voltage_3"),
        BenyMeasurementSensor("Current Phase 1", fetch_state, "current_1"),
        BenyMeasurementSensor("Current Phase 2", fetch_state, "current_2"),
        BenyMeasurementSensor("Current Phase 3", fetch_state, "current_3"),
        BenyMeasurementSensor("Power", fetch_state, "power"),
    ])

    # Register services
    hass.services.async_register(DOMAIN, "start_charge", start_charge_service)
    hass.services.async_register(DOMAIN, "stop_charge", stop_charge_service)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry"""
    hass.services.async_remove(DOMAIN, "start_charge")
    hass.services.async_remove(DOMAIN, "stop_charge")
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
