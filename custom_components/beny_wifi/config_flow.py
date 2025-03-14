"""Home Assistant config flow ."""
import asyncio
import logging
import socket

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.device_registry import async_get as async_get_device_registry

from .communication import build_message, read_message
from .const import (
    CLIENT_MESSAGE,
    CONF_IP,
    CONF_PORT,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MODEL,
    REQUEST_TYPE,
    SCAN_INTERVAL,
    SERIAL,
)
from .conversions import get_hex

_LOGGER = logging.getLogger(__name__)

class BenyWifiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for beny-wifi."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Handle user initialized config flow."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""

        self._errors = {}

        if user_input is not None:
            dev_data = await self._test_device(user_input[CONF_IP], user_input[CONF_PORT])
            if dev_data is not None:

                if not await self._device_exists(dev_data["serial_number"]):
                    user_input[MODEL] = dev_data.get("model", "Charger")
                    user_input[SERIAL] = dev_data["serial_number"]
                    return self.async_create_entry(title="Beny Wifi", data=user_input)

                self._errors["base"] = "device_already_configured"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_IP): str,
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                    vol.Optional(SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
                }
            ),
            errors=self._errors
        )

    async def _device_exists(self, serial_number: str) -> bool:
        """Check if a device with the given serial number already exists."""
        device_registry = async_get_device_registry(self.hass)
        return any(device.serial_number == serial_number for device in device_registry.devices.values())

    async def _test_device(self, ip, port) -> dict | None:
        """Check is model can be retrieved from device."""
        def sync_socket_communication():
            try:
                dev_data = {}
                request = build_message(CLIENT_MESSAGE.REQUEST_DATA, {"request_type": get_hex(REQUEST_TYPE.MODEL.value)}).encode('ascii')
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(5)
                sock.sendto(request, (ip, port))
                _LOGGER.debug(f"Sent model request to {ip}:{port}")  # noqa: G004
            except Exception as ex:  # noqa: BLE001
                self._errors["base"] = "cannot_connect"
                _LOGGER.exception(f"Exception sending model request to {ip}:{port}. Cause: {ex}. Request: {request}")  # noqa: G004, TRY401
                return None

            try:
                response, addr = sock.recvfrom(1024)
                _LOGGER.debug(f"Model message received from {ip}:{port}")  # noqa: G004
                sock.close()
                response = response.decode('ascii')
                data = read_message(response)
                _LOGGER.debug(f"Model message data: {data}")  # noqa: G004
                dev_data['model'] = data.get("model", "Charger")
            except Exception as ex:  # noqa: BLE001
                self._errors["base"] = "cannot_communicate"
                _LOGGER.exception(f"Exception receiving model data from {ip}:{port}. Cause: {ex}. Request hex: {request}. Response hex: {response}. Translated response: {data}")  # noqa: G004, TRY401
                return None

            try:
                request = build_message(CLIENT_MESSAGE.POLL_DEVICES).encode('ascii')
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(5)
                sock.sendto(request, (ip, port))
                _LOGGER.debug(f"Sent serial number request to {ip}:{port}")  # noqa: G004
            except Exception as ex:  # noqa: BLE001
                self._errors["base"] = "cannot_connect"
                _LOGGER.exception(f"Exception sending serial number request to {ip}:{port}. Cause: {ex}. Request: {request}")  # noqa: G004, TRY401


            try:
                response, addr = sock.recvfrom(1024)
                sock.close()
                response = response.decode('ascii')
                data = read_message(response)
                dev_data['serial_number'] = data.get('serial', '12345678')
                _LOGGER.debug(f"Serial number message data: {data}")  # noqa: G004
            except Exception as ex:  # noqa: BLE001
                self._errors["base"] = "cannot_communicate"
                _LOGGER.exception(f"Exception receiving serial number data from {ip}:{port}. Cause: {ex}. Request hex: {request}. Response hex: {response}. Translated response: {data}")  # noqa: G004, TRY401
                return None

            return dev_data  # noqa: TRY300

        return await asyncio.to_thread(sync_socket_communication)
