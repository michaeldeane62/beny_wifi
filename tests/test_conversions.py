import pytest
from custom_components.beny_wifi.conversions import (
    get_hex,
    convert_timer,
    get_message_type,
    get_ip,
    get_model,
)
from custom_components.beny_wifi.const import CLIENT_MESSAGE, SERVER_MESSAGE

"""Test get_hex."""
@pytest.mark.parametrize(
    "data, expected",
    [
        (0, "00"),
        (15, "0f"),
        (255, "ff"),
    ],
)
def test_get_hex(data, expected):
    assert get_hex(data) == expected

"""Test convert_timer."""
@pytest.mark.parametrize(
    "start_time_str, end_time_str, expected",
    [
        (
            "08:00",
            "10:30",
            {"start_h": "08", "start_min": "00", "end_h": "0a", "end_min": "1e"},
        ),
        (
            "00:00",
            "23:59",
            {"start_h": "00", "start_min": "00", "end_h": "17", "end_min": "3b"},
        ),
    ],
)
def test_convert_timer(start_time_str, end_time_str, expected):
    assert convert_timer(start_time_str, end_time_str) == expected

"""Test get_message_type."""
@pytest.mark.parametrize(
    "data, expected",
    [
        ("55aa10000b0000", CLIENT_MESSAGE.REQUEST_DATA),
        ("55aa10001c0000", CLIENT_MESSAGE.SET_TIMER),
        ("55aa10000c0000", CLIENT_MESSAGE.SEND_CHARGER_COMMAND),
        ("55aa1000080000", SERVER_MESSAGE.SEND_ACK),
        ("55aa1000230000", SERVER_MESSAGE.SEND_VALUES),
        ("55aa1000110000", SERVER_MESSAGE.HANDSHAKE),
        ("55aa1000200000", SERVER_MESSAGE.SEND_MODEL),
        ("55aa1000ff0000", None),
    ],
)
def test_get_message_type(data, expected, mocker):
    # Mock the COMMON structure to ensure correct slicing for "message_id"
    mock_common = mocker.patch("custom_components.beny_wifi.conversions.COMMON")
    mock_common.FIXED_PART.value = {
        "structure": {"message_id": slice(8, 10)}  # Adjusted based on input hex
    }
    
    result = get_message_type(data)
    assert result == expected


"""Test get_ip."""
@pytest.mark.parametrize(
    "data, expected",
    [
        ("55aa10001103499602D2c0a80164", "192.168.1.100"),
        ("55aa10001103499602D2c0a80001", "192.168.0.1"),
    ],
)
def test_get_ip(data, expected, mocker):
    # Mock SERVER_MESSAGE.HANDSHAKE structure for IP slicing
    mock_server_message = mocker.patch("custom_components.beny_wifi.conversions.SERVER_MESSAGE")
    mock_server_message.HANDSHAKE.value = {
        "structure": {"ip": slice(20, 28, 2)}  # Adjust based on input data
    }

    result = get_ip(data)
    assert result == expected


"""Test get_model."""
@pytest.mark.parametrize(
    "data, expected",
    [
        ("4243502d4154314e2d4c", "BCP-AT1N-L"),
        ("414243", "ABC"),
        ("3132333435", "12345"),
    ],
)
def test_get_model(data, expected, mocker):
    mock_send_model = mocker.patch("custom_components.beny_wifi.conversions.SERVER_MESSAGE")
    mock_send_model.SEND_MODEL.value = {"structure": {"model": slice(0, len(data))}}
    assert get_model(data) == expected
