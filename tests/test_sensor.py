import pytest
from unittest.mock import MagicMock, AsyncMock
from homeassistant.helpers.entity import DeviceInfo
from custom_components.beny_wifi.sensor import BenyWifiSensor
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
def sensor(mock_coordinator):
    """Fixture to create a BenyWifiSensor instance."""
    return BenyWifiSensor(
        coordinator=mock_coordinator,
        key="state",
        name="Charger State",
        unit=None,
        device_id="1234567890",
        device_model="BenyModel123",
    )


def test_sensor_initialization(sensor, mock_coordinator):
    """Test the initialization of the sensor."""

    # Ensure the sensor has the correct entity_id
    assert sensor.entity_id == "sensor.1234567890_state"

    # Verify the sensor name and unique_id
    assert sensor.name == "Charger State"
    assert sensor.unique_id == "1234567890_state"

    # Check that the sensor state matches the coordinator's data
    assert sensor.state == "charging"

    # Test the unit of measurement (None for this sensor)
    assert sensor.unit_of_measurement is None

    # Test the device info
    device_info = sensor.device_info
    assert device_info["identifiers"] == {(DOMAIN, "1234567890")}
    assert device_info["name"] == "Beny Charger 1234567890"
    assert device_info["manufacturer"] == "ZJ Beny"
    assert device_info["model"] == "BenyModel123"
    assert device_info["serial_number"] == "1234567890"

@pytest.mark.asyncio
async def test_async_update(sensor, mock_coordinator):
    """Test that the async_update method updates the sensor state."""

    # Call async_update
    await sensor.async_update()

    # Ensure that async_request_refresh was called
    mock_coordinator.async_request_refresh.assert_called_once()

    # Simulate a state change in the coordinator
    mock_coordinator.data["state"] = "charging"
    await sensor.async_update()

    # Check that the state has updated correctly
    assert sensor.state == "charging"


def test_sensor_properties(sensor, mock_coordinator):
    """Test the sensor's properties."""
    
    # Test the state property
    assert sensor.state == "charging"
    
    # Test the name property
    assert sensor.name == "Charger State"
    
    # Test the unique_id property
    assert sensor.unique_id == "1234567890_state"
    
    # Test the unit_of_measurement property
    assert sensor.unit_of_measurement is None

    # Test the device_info property
    device_info = sensor.device_info
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

    assert len(sensors) == 12  # We expect 12 sensors to be created

    # Check the attributes of one of the sensors
    sensor = sensors[0]
    assert sensor.entity_id == "sensor.1234567890_state"
    assert sensor.name == "Charger State"
    assert sensor.unique_id == "1234567890_state"
    assert sensor.state == "charging"



@pytest.mark.parametrize("key, unit, expected_icon", [
    ("state", None, "mdi:ev-station"),  # The "state" key should give mdi:ev-station
    ("power", "kW", "mdi:ev-plug-type2"),  # The "power" key with unit "kW" should give mdi:ev-plug-type2
    ("timer_start", None, "mdi:timer-sand-empty"),  # The "timer_start" key should give mdi:timer-sand-empty
    ("timer_end", None, "mdi:timer-sand-full"),  # The "timer_end" key should give mdi:timer-sand-full
    ("voltage1", "V", "mdi:flash-triangle"),  # "voltage" keys with unit "V" should give mdi:flash-triangle
    ("current1", "A", "mdi:sine-wave"),  # "current" keys with unit "A" should give mdi:sine-wave
    ("unknown_key", "unknown_unit", None),  # An unknown key with unknown unit should return None
    ("total_kwh", None, "mdi:power-plug-battery"),  # The "total_kwh" key should give mdi:power-plug-battery
])
def test_icon_logic(key, unit, expected_icon):
    """Test the icon logic in BenyWifiSensor."""

    # Mock a coordinator, assuming `key` and `unit` affect the icon
    mock_coordinator = None  # Use None or mock as needed, no effect on icon logic for this test
    sensor = BenyWifiSensor(mock_coordinator, key, "Sensor Name", unit=unit)

    # Check the icon
    assert sensor.icon == expected_icon