import pytest
import socket
from unittest.mock import patch, MagicMock, AsyncMock, call
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import UpdateFailed
from custom_components.beny_wifi.coordinator import BenyWifiUpdateCoordinator
from custom_components.beny_wifi.const import CLIENT_MESSAGE, REQUEST_TYPE, CHARGER_STATE, CHARGER_COMMAND
from custom_components.beny_wifi.conversions import get_hex
from datetime import datetime, timedelta

@pytest.fixture
def mock_send_udp_request():
    """Mock the '_send_udp_request' method."""
    return AsyncMock()

@pytest.fixture
def mock_hass():
    """Fixture to mock HomeAssistant."""
    hass = MagicMock(HomeAssistant)
    # Mock the states object
    hass.states = MagicMock()
    return hass

@pytest.fixture
def coordinator(mock_hass):
    """Fixture to create a BenyWifiUpdateCoordinator instance."""
    # Mock the config_entry data
    config_entry = MagicMock()
    config_entry.data = {
        "serial": "1234567890"  # Mock the serial number
    }
    coordinator = BenyWifiUpdateCoordinator(
        hass=mock_hass,
        ip_address="192.168.1.100",
        port=502,
        scan_interval=10,
    )
    coordinator.config_entry = config_entry  # Mock config_entry to avoid 'NoneType' error
    return coordinator


@patch("custom_components.beny_wifi.coordinator.BenyWifiUpdateCoordinator._send_udp_request")
@patch("custom_components.beny_wifi.coordinator.read_message")
async def test_successful_data_fetch(mock_read_message, mock_send_udp_request, coordinator):
    """Test successful data fetch from the coordinator."""
    
    # Prepare mock response from UDP request (simulated)
    mock_send_udp_request.return_value = b"some_udp_response"
    
    # Simulate a valid read_message response
    mock_read_message.return_value = {
        "state": "standby",
        "power": 0.0,
        "total_kwh": 0.0,
        "timer_start_h": 8,
        "timer_start_min": 0,
        "timer_end_h": 7,
        "timer_end_min": 30,
    }

    # Call the update function
    data = await coordinator._async_update_data()

    # Check if the data was correctly transformed and returned
    assert data["state"] == "standby"
    assert data["power"] == 0.0
    assert data["total_kwh"] == 0.0
    assert isinstance(data["timer_start"], datetime)
    assert isinstance(data["timer_end"], datetime)


@patch("custom_components.beny_wifi.coordinator.BenyWifiUpdateCoordinator._send_udp_request")
async def test_udp_request_failure(mock_send_udp_request, coordinator):
    """Test that the coordinator raises an error when the UDP request fails."""

    # Simulate a failure in sending the UDP request
    mock_send_udp_request.side_effect = Exception("UDP request failed")

    # Call the update function and check if it raises UpdateFailed
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()  # Ensure this is awaited


@patch("custom_components.beny_wifi.coordinator.BenyWifiUpdateCoordinator._send_udp_request")
@patch("custom_components.beny_wifi.coordinator.read_message")
async def test_async_toggle_charging_start(mock_read_message, mock_send_udp_request, coordinator):
    """Test toggling charging start."""

    # Mock the response from the UDP request as raw bytes
    mock_send_udp_request.return_value = b"55aa10001103499602D2c0a801640d05d8"

    # Mock the parsed response returned by read_message
    mock_read_message.return_value = {
        "state": "standby",  # Expected parsed state
        "power": 0.0,        # Parsed power value
        "total_kwh": 0.0,    # Parsed energy value
        "timer_start_h": 8,  # Parsed timer start hour
        "timer_start_min": 0,  # Parsed timer start minute
        "timer_end_h": 10,   # Parsed timer end hour
        "timer_end_min": 30, # Parsed timer end minute
    }

    # Call the coordinator's update method
    data = await coordinator._async_update_data()

    # Assertions
    assert data["state"] == "standby"
    assert data["power"] == 0.0
    assert data["total_kwh"] == 0.0
    assert isinstance(data["timer_start"], datetime)
    assert isinstance(data["timer_end"], datetime)


@patch("custom_components.beny_wifi.coordinator.BenyWifiUpdateCoordinator._send_udp_request")
async def test_async_set_timer_unplugged(mock_send_udp_request, coordinator, mock_hass):
    """Test that timer setting fails if the charger is unplugged."""

    # Simulate the charger being unplugged (mocking as None state)
    mock_hass.states.get.return_value = None  # Ensure no state is returned

    # Check that HomeAssistantError is raised when trying to set the timer
    with pytest.raises(HomeAssistantError):
        await coordinator.async_set_timer(device_name="Charger1", start_time="08:00", end_time="10:00")

@patch("custom_components.beny_wifi.coordinator.read_message")
@patch("socket.socket")
async def test_async_toggle_charging_start_with_socket(mock_socket, mock_read_message, coordinator):
    """Test toggling charging start with simulated socket."""

    # Create a mock socket instance
    mock_socket_instance = MagicMock()
    mock_socket.return_value = mock_socket_instance

    # Simulate sending data with `sendto`
    def mock_sendto(data, addr):
        assert data == b"55aa10000b0000cb347089"  # Verify the correct request data is sent
        assert addr == ("192.168.1.100", 502)  # Verify correct IP and port
    mock_socket_instance.sendto.side_effect = mock_sendto

    # Simulate receiving data with `recvfrom`
    mock_socket_instance.recvfrom.return_value = (b"55aa10001103499602D2c0a801640d05d8", ("192.168.1.100", 502))

    # Mock the parsed message structure returned by `read_message`
    mock_read_message.return_value = {
        "state": "standby",
        "power": 0.0,
        "total_kwh": 0.0,
        "timer_start_h": 8,
        "timer_start_min": 0,
        "timer_end_h": 10,
        "timer_end_min": 30,
    }

    # Mock the built message
    with patch("custom_components.beny_wifi.communication.build_message") as mock_build_message:
        mock_build_message.return_value = b"mocked_request"

        # Call the coordinator's update method
        data = await coordinator._async_update_data()

        # Assertions
        assert data["state"] == "standby"
        assert data["power"] == 0.0
        assert data["total_kwh"] == 0.0
        assert isinstance(data["timer_start"], datetime)
        assert isinstance(data["timer_end"], datetime)

        # Verify socket operations
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_DGRAM)
        mock_socket_instance.settimeout.assert_called_once_with(5)
        mock_socket_instance.close.assert_called_once()

@patch("socket.socket")
async def test_socket_exception(mock_socket, coordinator):
    """Test that a socket exception is correctly handled and raises UpdateFailed."""

    # Create a mock socket instance
    mock_socket_instance = MagicMock()
    mock_socket.return_value = mock_socket_instance

    # Simulate a socket exception when sending data
    mock_socket_instance.sendto.side_effect = socket.error("Mocked socket error")

    # Mock the built message
    with patch("custom_components.beny_wifi.communication.build_message") as mock_build_message:
        mock_build_message.return_value = b"55aa10000b0000cb347089"

        # Call the coordinator's update method and ensure it raises UpdateFailed
        with pytest.raises(UpdateFailed, match="Error sending UDP request: Mocked socket error"):
            await coordinator._async_update_data()

    # Print the mock calls for debugging (optional)
    print(mock_socket_instance.mock_calls)

    # Verify socket operations
    mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_DGRAM)
    mock_socket_instance.settimeout.assert_called_once_with(5)
    mock_socket_instance.sendto.assert_called_once_with(b"55aa10000b0000cb347089", ("192.168.1.100", 502))
    mock_socket_instance.close.assert_called_once()

@patch("custom_components.beny_wifi.coordinator.BenyWifiUpdateCoordinator._send_udp_request")
async def test_toggle_charging_unplugged(mock_send_udp_request, coordinator, mock_hass):
    """Test that HomeAssistantError is raised when the charger is unplugged."""

    # Simulate charger state as unplugged
    mock_hass.states.get.return_value = CHARGER_STATE.UNPLUGGED.name.lower()

    # Call the method and expect HomeAssistantError
    with pytest.raises(HomeAssistantError, match="Cannot start charging - charger unplugged"):
        await coordinator.async_toggle_charging(device_name="Charger1", command="start")

    # Ensure no UDP request was sent
    mock_send_udp_request.assert_not_called()
