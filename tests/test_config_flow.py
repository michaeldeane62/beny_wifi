import pytest
from unittest.mock import patch
from custom_components.beny_wifi.config_flow import BenyWifiConfigFlow
from custom_components.beny_wifi.const import CONF_IP, CONF_PORT, SCAN_INTERVAL, MODEL, SERIAL
from .const import (
    TEST_PORT, 
    TEST_SCAN_INTERVAL, 
    TEST_IP_ADDRESS,
    TEST_MODEL,
    TEST_SERIAL
)

@pytest.mark.asyncio
async def test_async_step_user_valid_input(hass):
    """Test the user step with valid input."""
    
    flow = BenyWifiConfigFlow()
    flow.hass = hass

    user_input = {
        CONF_IP: TEST_IP_ADDRESS,
        CONF_PORT: TEST_PORT,
        SCAN_INTERVAL: TEST_SCAN_INTERVAL,
    }

    dev_data = {
        "model": TEST_MODEL,
        "serial_number": TEST_SERIAL,
    }

    with patch.object(flow, "_test_device", return_value=dev_data) as mock_test_device, \
         patch.object(flow, "_device_exists", return_value=False) as mock_device_exists:

        result = await flow.async_step_user(user_input)

        assert result["type"] == "create_entry"
        assert result["title"] == "Beny Wifi"
        assert result["data"] == {
            CONF_IP: TEST_IP_ADDRESS,
            CONF_PORT: TEST_PORT,
            SCAN_INTERVAL: TEST_SCAN_INTERVAL,
            MODEL: TEST_MODEL,
            SERIAL: TEST_SERIAL,
        }
        mock_test_device.assert_called_once_with(TEST_IP_ADDRESS, TEST_PORT)
        mock_device_exists.assert_awaited_once_with(TEST_SERIAL)

@pytest.mark.asyncio
async def test_async_step_user_device_already_configured(hass):
    """Test the user step when the device is already configured."""
    
    flow = BenyWifiConfigFlow()
    flow.hass = hass

    user_input = {
        CONF_IP: TEST_IP_ADDRESS,
        CONF_PORT: TEST_PORT,
        SCAN_INTERVAL: TEST_SCAN_INTERVAL,
    }

    dev_data = {
        "model": TEST_MODEL,
        "serial_number": TEST_SERIAL,
    }

    with patch.object(flow, "_test_device", return_value=dev_data) as mock_test_device, \
         patch.object(flow, "_device_exists", return_value=True) as mock_device_exists:

        result = await flow.async_step_user(user_input)

        assert result["type"] == "form"
        assert result["errors"] == {"base": "device_already_configured"}
        mock_test_device.assert_called_once_with(TEST_IP_ADDRESS, TEST_PORT)
        mock_device_exists.assert_awaited_once_with(TEST_SERIAL)

@pytest.mark.asyncio
async def test_test_device_cannot_connect(mocker):
    """Test _test_device handles connection error."""

    mock_socket = mocker.patch("socket.socket")
    mock_instance = mock_socket.return_value
    mock_instance.sendto.side_effect = OSError("Cannot connect")

    flow = BenyWifiConfigFlow()

    result = await flow._test_device(TEST_IP_ADDRESS, TEST_PORT)
    assert result is None
    assert flow._errors["base"] == "cannot_connect"

@pytest.mark.asyncio
async def test_test_device_cannot_communicate(mocker):
    """Test _test_device handles communication error."""
    
    mock_socket = mocker.patch("socket.socket")
    mock_instance = mock_socket.return_value
    mock_instance.recvfrom.return_value = (b"invalid_response", (TEST_IP_ADDRESS, TEST_PORT))

    mocker.patch("custom_components.beny_wifi.communication.read_message", side_effect=ValueError("Invalid message format"))

    flow = BenyWifiConfigFlow()

    result = await flow._test_device(TEST_IP_ADDRESS, TEST_PORT)
    assert result is None
    assert flow._errors["base"] == "cannot_communicate"