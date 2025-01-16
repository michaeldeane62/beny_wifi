import pytest
from unittest.mock import MagicMock, AsyncMock
from custom_components.beny_wifi.sensor import (
    BenyWifiVoltageSensor,
    BenyWifiChargerStateSensor,
    BenyWifiCurrentSensor,
    BenyWifiEnergySensor,
    BenyWifiPowerSensor,
    BenyWifiSensor,
    BenyWifiTimerSensor

)
from custom_components.beny_wifi.const import DOMAIN
from custom_components.beny_wifi.sensor import async_setup_entry
from homeassistant.config_entries import ConfigEntry

@pytest.fixture
def mock_coordinator():
    """Fixture to mock the coordinator."""
    coordinator = MagicMock()
    coordinator.data = {
        "state": "charging",
        "power": 1.5,
        "voltage1": 230,
        "voltage2": 230,
        "voltage3": 230,
        "current1": 10,
        "current2": 10,
        "current3": 10,
        "max_current": 16,
        "total_kwh": 120,
        "timer_start": "08:00",
        "timer_end": "10:00",
    }
    coordinator.async_request_refresh = AsyncMock()
    return coordinator


@pytest.fixture
def voltage_sensor(mock_coordinator):
    """Fixture to create a BenyWifiSensor instance."""
    return BenyWifiVoltageSensor(
        coordinator=mock_coordinator,
        key="state",
        icon="mdi:chuck_norris",
        device_id="1234567890",
        device_model="BenyModel123",
    )

def test_sensor_initialization(voltage_sensor, mock_coordinator):
    """Test the initialization of the sensor."""

    # Ensure the sensor has the correct entity_id
    assert voltage_sensor.entity_id == "sensor.1234567890_state"

    # Verify the sensor name and unique_id
    #assert voltage_sensor.name == "Charger State"
    assert voltage_sensor.unique_id == "1234567890_state"

    # Check that the sensor state matches the coordinator's data
    assert voltage_sensor.state == "charging"

    # Test the unit of measurement (None for this sensor)
    assert voltage_sensor.unit_of_measurement == 'V'

    # Test the device info
    device_info = voltage_sensor.device_info
    assert device_info["identifiers"] == {(DOMAIN, "1234567890")}
    assert device_info["name"] == "Beny Charger 1234567890"
    assert device_info["manufacturer"] == "ZJ Beny"
    assert device_info["model"] == "BenyModel123"
    assert device_info["serial_number"] == "1234567890"

@pytest.mark.asyncio
async def test_async_update(voltage_sensor, mock_coordinator):
    """Test that the async_update method updates the sensor state."""

    # Call async_update
    await voltage_sensor.async_update()

    # Ensure that async_request_refresh was called
    mock_coordinator.async_request_refresh.assert_called_once()

    # Simulate a state change in the coordinator
    mock_coordinator.data["state"] = "charging"
    await voltage_sensor.async_update()

    # Check that the state has updated correctly
    assert voltage_sensor.state == "charging"


def test_sensor_properties(voltage_sensor, mock_coordinator):
    """Test the sensor's properties."""
    
    # Test the state property
    assert voltage_sensor.state == "charging"
    
    # Test the name property
    #assert voltage_sensor.name == "Charger State"
    
    # Test the unique_id property
    assert voltage_sensor.unique_id == "1234567890_state"
    
    # Test the unit_of_measurement property
    assert voltage_sensor.unit_of_measurement == 'V'

    # Test the device_info property
    device_info = voltage_sensor.device_info
    assert device_info["name"] == "Beny Charger 1234567890"
    assert device_info["manufacturer"] == "ZJ Beny"
    assert device_info["model"] == "BenyModel123"
    assert device_info["serial_number"] == "1234567890"

@pytest.fixture
def mock_hass():
    """Mock the Home Assistant instance."""
    return MagicMock()


@pytest.fixture
def mock_config_entry():
    """Mock the config entry."""
    config_entry = MagicMock(spec=ConfigEntry)
    config_entry.entry_id = "test_entry_id"
    config_entry.data = {
        "serial": "1234567890",
        "model": "BenyModel123",
    }
    return config_entry

@pytest.mark.asyncio
async def test_async_setup_entry(mock_hass, mock_config_entry, mock_coordinator):
    """Test the async_setup_entry function."""

    # Mock the hass.data structure to simulate Home Assistant data
    mock_hass.data = {DOMAIN: {mock_config_entry.entry_id: {"coordinator": mock_coordinator}}}

    # Mock async_add_entities to track the entities being added
    async_add_entities = AsyncMock()

    # Call async_setup_entry to simulate the setup
    await async_setup_entry(mock_hass, mock_config_entry, async_add_entities)

    # Check that async_add_entities was called with the correct sensors
    assert async_add_entities.call_count == 1  # We expect 12 sensors to be added

    # Verify the sensors were correctly initialized and added
    args, _ = async_add_entities.call_args
    sensors = args[0]

    assert len(sensors) == 13  # We expect 12 sensors to be created

    # Check the attributes of one of the sensors
    sensor = sensors[0]
    assert sensor.entity_id == "sensor.1234567890_charger_state"
    assert sensor.unique_id == "1234567890_charger_state"
    assert sensor.state is None
