import pytest
from unittest.mock import AsyncMock, patch
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from custom_components.beny_wifi import async_setup_entry, async_unload_entry
from custom_components.beny_wifi.const import DOMAIN, CONF_IP, CONF_PORT, SCAN_INTERVAL, PLATFORMS

@pytest.mark.asyncio
async def test_async_setup_entry(hass: HomeAssistant):
    """Test the async_setup_entry function."""
    entry = ConfigEntry(
        version=1,
        domain=DOMAIN,
        title="Beny WiFi",
        data={
            CONF_IP: "192.168.1.100",
            CONF_PORT: 8080,
            SCAN_INTERVAL: 10,
        },
        source="user",
        entry_id="test",
        unique_id="unique_test_id",
        options={},
        minor_version=0,
        discovery_keys=None,
    )

    coordinator_mock = AsyncMock()
    
    with patch("custom_components.beny_wifi.BenyWifiUpdateCoordinator", return_value=coordinator_mock) as mock_coordinator, \
         patch("custom_components.beny_wifi.async_setup_services", new_callable=AsyncMock) as mock_setup_services, \
         patch("homeassistant.config_entries.ConfigEntries.async_forward_entry_setups", new_callable=AsyncMock) as mock_forward_setups:

        # Test successful setup
        coordinator_mock.async_config_entry_first_refresh.return_value = None
        assert await async_setup_entry(hass, entry) is True
        mock_coordinator.assert_called_once_with(hass, "192.168.1.100", 8080, 10)
        mock_setup_services.assert_awaited_once()
        mock_forward_setups.assert_awaited_once_with(entry, PLATFORMS)
        assert DOMAIN in hass.data
        assert entry.entry_id in hass.data[DOMAIN]

        # Test setup failure due to ConfigEntryNotReady
        coordinator_mock.async_config_entry_first_refresh.side_effect = Exception("Connection error")
        with pytest.raises(ConfigEntryNotReady):
            await async_setup_entry(hass, entry)


@pytest.mark.asyncio
async def test_async_unload_entry(hass: HomeAssistant):
    """Test the async_unload_entry function."""
    entry = ConfigEntry(
        version=1,
        domain=DOMAIN,
        title="Beny WiFi",
        data={
            CONF_IP: "192.168.1.100",
            CONF_PORT: 8080,
            SCAN_INTERVAL: 10,
        },
        source="user",
        entry_id="test",
        unique_id="unique_test_id",
        options={},
        minor_version=0,
        discovery_keys=None,
    )

    # Mock data in hass
    hass.data[DOMAIN] = {
        entry.entry_id: {
            "coordinator": AsyncMock()
        }
    }

    with patch("homeassistant.config_entries.ConfigEntries.async_unload_platforms", return_value=True) as mock_unload_platforms:
        assert await async_unload_entry(hass, entry) is True
        mock_unload_platforms.assert_awaited_once_with(entry, PLATFORMS)
        assert entry.entry_id not in hass.data[DOMAIN]
