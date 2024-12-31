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

                if not await self._device_exists(dev_data["serial"]):
                    user_input[MODEL] = dev_data["model"]
                    user_input[SERIAL] = dev_data["serial"]
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

    async def _device_exists(self, device_id: str) -> bool:
        """Check if a device with the given ID already exists."""
        device_registry = async_get_device_registry(self.hass)
        return any(device.name == device_id for device in device_registry.devices.values())

    async def _test_device(self, ip, port) -> dict | None:
        """Check is model can be retrieved from device."""
        def sync_socket_communication():
            try:
                dev_data = {}
                request = build_message(CLIENT_MESSAGE.REQUEST_DATA, {"request_type": get_hex(REQUEST_TYPE.MODEL.value)}).encode('ascii')
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(5)
                sock.sendto(request, (ip, port))
            except Exception:  # noqa: BLE001
                self._errors["base"] = "cannot_connect"
                return None

            try:
                response, addr = sock.recvfrom(1024)
                sock.close()
                response = response.decode('ascii')
                data = read_message(response)
                dev_data['model'] = data['model']
            except Exception:  # noqa: BLE001
                self._errors["base"] = "cannot_communicate"
                return None

            try:
                request = build_message(CLIENT_MESSAGE.POLL_DEVICES).encode('ascii')
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(5)
                sock.sendto(request, (ip, port))
            except Exception:  # noqa: BLE001
                self._errors["base"] = "cannot_connect"

            try:
                response, addr = sock.recvfrom(1024)
                sock.close()
                response = response.decode('ascii')
                data = read_message(response)
                dev_data['serial'] = data['serial']
            except Exception:  # noqa: BLE001
                self._errors["base"] = "cannot_communicate"
                return None

            return dev_data  # noqa: TRY300

        return await asyncio.to_thread(sync_socket_communication)
