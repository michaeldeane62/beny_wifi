"""Handle integration services."""

import logging
from typing import cast

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_DEVICE_ID
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN
from .coordinator import BenyWifiUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_services(hass: HomeAssistant) -> bool:
    """Set up Beny Wifi services."""

    async def async_handle_start_charging(call: ServiceCall):
        """Start charging car."""

        coordinator: BenyWifiUpdateCoordinator = _get_coordinator_from_device(hass, call)["coordinator"]
        if coordinator:
            device_name = _get_device_name(hass, call.data[ATTR_DEVICE_ID])
            await coordinator.async_toggle_charging(device_name, "start")
        else:
            _LOGGER.error(f"Device id {call.data[ATTR_DEVICE_ID]} not found")  # noqa: G004

    async def async_handle_stop_charging(call: ServiceCall):
        """Stop charging car."""

        coordinator: BenyWifiUpdateCoordinator = _get_coordinator_from_device(hass, call)["coordinator"]
        if coordinator:
            device_name = _get_device_name(hass, call.data[ATTR_DEVICE_ID])
            await coordinator.async_toggle_charging(device_name, "stop")
        else:
            _LOGGER.error(f"Device id {call.data[ATTR_DEVICE_ID]} not found")  # noqa: G004

    async def async_handle_set_timer(call: ServiceCall):
        """Set charging timer."""

        coordinator: BenyWifiUpdateCoordinator = _get_coordinator_from_device(hass, call)["coordinator"]
        if coordinator:
            device_name = _get_device_name(hass, call.data[ATTR_DEVICE_ID])
            await coordinator.async_set_timer(device_name, call.data["start_time"], call.data["end_time"])
        else:
            _LOGGER.error(f"Device id {call.data[ATTR_DEVICE_ID]} not found")  # noqa: G004

    async def async_handle_reset_timer(call: ServiceCall):
        """Reset charging timer."""

        coordinator: BenyWifiUpdateCoordinator = _get_coordinator_from_device(hass, call)["coordinator"]
        if coordinator:
            device_name = _get_device_name(hass, call.data[ATTR_DEVICE_ID])
            await coordinator.async_reset_timer(device_name)
        else:
            _LOGGER.error(f"Device id {call.data[ATTR_DEVICE_ID]} not found")  # noqa: G004


    services = {
        "start_charging": async_handle_start_charging,
        "stop_charging": async_handle_stop_charging,
        "set_timer": async_handle_set_timer,
        "reset_timer": async_handle_reset_timer
    }

    for _name, _service in services.items():
        hass.services.async_register(DOMAIN, _name, _service)

def _get_device_name(hass: HomeAssistant, device_id: str):
    device_entry = dr.async_get(hass).async_get(device_id)
    return device_entry.name if device_entry else None

def _get_coordinator_from_device(hass: HomeAssistant, call: ServiceCall) -> BenyWifiUpdateCoordinator:
    coordinators = list(hass.data[DOMAIN].keys())
    if len(coordinators) == 1:
        return hass.data[DOMAIN][coordinators[0]]

    device_entry = dr.async_get(hass).async_get(
        call.data[ATTR_DEVICE_ID]
    )
    config_entry_ids = device_entry.config_entries
    config_entry_id = next(
        (
            config_entry_id
            for config_entry_id in config_entry_ids
            if cast(
                ConfigEntry,
                hass.config_entries.async_get_entry(config_entry_id),
            ).domain
            == DOMAIN
        ),
        None,
    )
    config_entry_unique_id = hass.config_entries.async_get_entry(config_entry_id).unique_id
    return hass.data[DOMAIN][config_entry_unique_id]
