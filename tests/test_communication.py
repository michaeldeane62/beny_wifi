import pytest
from unittest.mock import patch
from custom_components.beny_wifi.communication import read_message, build_message
from custom_components.beny_wifi.const import SERVER_MESSAGE, CLIENT_MESSAGE
from .const import TEST_MODEL, TEST_IP_ADDRESS, TEST_PORT, TEST_SERIAL

"""Read message."""
@pytest.mark.parametrize(
    "data, message_type, expected",
    [
        # Test for valid SERVER_MESSAGE.SEND_VALUES
        (
            "55aa1000237000000000e600e800e6000000006102000000000000000f0000000003cb",
            SERVER_MESSAGE.SEND_VALUES,
            {
                "message_type": "SERVER_MESSAGE.SEND_VALUES",
                "header": 21930,
                "version": 16,
                "message_id": 35,
                "request_type": "VALUES",
                "current1": 0,
                "current2": 0,
                "current3": 0,
                "voltage1": 230,
                "voltage2": 232,
                "voltage3": 230,
                "power": 0.0,
                "total_kwh": 0.0,
                "state": "STANDBY",
                "max_current": 15,
                "timer_start_h": 0,
                "timer_start_min": 0,
                "timer_end_h": 0,
                "timer_end_min": 0,
            },
        ),
        # Test for valid SERVER_MESSAGE.SEND_MODEL
        (
            "55aa1000200400014243502d4154314e2d4c00000000000000000000011a01df",
            SERVER_MESSAGE.SEND_MODEL,
            {
                "message_type": "SERVER_MESSAGE.SEND_MODEL", 
                "header": 21930, 
                "version": 16, 
                "message_id": 32, 
                "request_type": "MODEL", 
                "model": TEST_MODEL
            },
        ),
        # Test for valid SERVER_MESSAGE.HANDSHAKE
        (
            "55aa10001103499602D2c0a801640d05b5",
            SERVER_MESSAGE.HANDSHAKE,
            {
                "message_type": "SERVER_MESSAGE.HANDSHAKE", 
                "header": 21930, 
                "version": 16, 
                "message_id": 17, 
                "serial": TEST_SERIAL, 
                "ip": TEST_IP_ADDRESS, 
                "port": TEST_PORT
            },
        ),
        # Test for valid CLIENT_MESSAGE.SEND_CHARGER_COMMAND
        (
            "55aa10000c0000cb34060121",
            CLIENT_MESSAGE.SEND_CHARGER_COMMAND,
            {
                "message_type": "CLIENT_MESSAGE.SEND_CHARGER_COMMAND", 
                "header": 21930, 
                "version": 16, 
                "message_id": 12, 
                "charger_command": "START", 
            },
        ),
        # Test for valid CLIENT_MESSAGE.REQUEST_DATA
        (
            "55aa10000b0000cb347089",
            CLIENT_MESSAGE.REQUEST_DATA,
            {
                "message_type": "CLIENT_MESSAGE.REQUEST_DATA", 
                "header": 21930, 
                "version": 16, 
                "message_id": 11, 
                "request_type": "VALUES"
            },
        ),
        # Test for valid CLIENT_MESSAGE.SET_TIMER
        (
            "55aa10001c0000cb34690001600800017ca0000000173b0017153bd2",
            CLIENT_MESSAGE.SET_TIMER,
            {
                "message_type": "CLIENT_MESSAGE.SET_TIMER", 
                "header": 21930, 
                "version": 16, 
                "message_id": 28, 
                "start_h": 0, 
                "start_min": 0, 
                "end_h": 23, 
                "end_min": 59
            },
        ),
        # Test for invalid checksum
        (
            "55aa10001c0000cb34690001600800017ca0000000173b0017153bd1",
            CLIENT_MESSAGE.SET_TIMER,
            None
        )
    ],
)
@patch("custom_components.beny_wifi.communication.get_message_type")

def test_read_message(mock_get_message_type, data, message_type, expected):
    mock_get_message_type.return_value = message_type

    result = read_message(data)
    assert result == expected

"""Build message."""
@pytest.mark.parametrize(
    "message, params, expected",
    [
        # Test building data request
        (
            CLIENT_MESSAGE.REQUEST_DATA,
            {"checksum": "89", "request_type": "70"},
            "55aa10000b0000cb347089",
        ),
        # Test building charger command
        (
            CLIENT_MESSAGE.SEND_CHARGER_COMMAND,
            {"checksum": "21", "charger_command": "01"},
            "55aa10000c0000cb34060121",  # Replace with expected hex string
        ),
    ],
)
@patch("custom_components.beny_wifi.communication.calculate_checksum")
def test_build_message(mock_calculate_checksum, message, params, expected):
    mock_calculate_checksum.return_value = 42
    result = build_message(message, params)
    assert result == expected
