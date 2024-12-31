"""Initialize integration."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.device_registry import async_get as async_get_device_registry

from .const import (
    CONF_IP,
    CONF_PORT,
    COORDINATOR,
    DOMAIN,
    MODEL,
    PLATFORMS,
    SCAN_INTERVAL,
    SERIAL,
)
from .coordinator import BenyWifiUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Beny Wifi from a config entry."""
    _LOGGER.info("Setting up Beny WiFi integration")

    ip_address = entry.data[CONF_IP]
    port = entry.data[CONF_PORT]
    scan_interval = entry.data[SCAN_INTERVAL]

    """
    device_registry = async_get_device_registry(hass)

    # Ensure a device is registered
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.data[SERIAL])},  # Unique identifier for the device
        name=f"Beny Charger {entry.data[SERIAL]}",
        manufacturer="ZJ Beny",
        model=entry.data[MODEL]
    )
    """

    # Create the DataUpdateCoordinator
    coordinator = BenyWifiUpdateCoordinator(hass, ip_address, port, scan_interval)

    # Perform the first update to ensure connection works
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as ex:
        _LOGGER.error(f"Error setting up coordinator: {ex}")  # noqa: G004
        raise ConfigEntryNotReady from ex

    # Store the coordinator for use by platforms
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        COORDINATOR: coordinator,
    }

    # Forward entry setup to supported platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unloading Beny WiFi integration")

    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    # Clean up resources
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
