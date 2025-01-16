# tests/test_communication.py
from custom_components.beny_wifi.communication import read_message, build_message, get_message_type
from custom_components.beny_wifi.const import SERVER_MESSAGE, CLIENT_MESSAGE, CHARGER_STATE, TIMER_STATE, REQUEST_TYPE, CHARGER_COMMAND

def test_read_message_valid():
    data = "55aa10001103075BCD15c0a801220d0504"
    msg_type = SERVER_MESSAGE.HANDSHAKE
    result = read_message(data, msg_type)
    assert result["message_type"] == str(msg_type)
    assert result["serial"] == 123456789  # Replace with actual expected value
    assert result["ip"] == "192.168.1.34"  # Replace with actual expected IP
    assert result["port"] == 3333

def test_read_message_invalid_checksum():
    # Invalid checksum (last byte is altered)
    data = "55aa10000f0000cb34030e5a7938"  # Tampered checksum
    msg_type = SERVER_MESSAGE.HANDSHAKE
    result = read_message(data, msg_type)
    assert result is None  # Expect None when checksum validation fails

def test_read_message_no_msg_type():
    data = "55aa10001103075BCD15c0a801220d0504"
    # Do not pass `msg_type`, so it should attempt to determine it automatically
    expected_msg_type = SERVER_MESSAGE.HANDSHAKE
    # Mock `get_message_type` if needed
    result = read_message(data)
    assert result["message_type"] == str(expected_msg_type)
    assert result["serial"] == 123456789  # Replace with actual expected value
    assert result["ip"] == "192.168.1.34"  # Replace with actual expected IP
    assert result["port"] == 3333

def test_build_message():
    message = CLIENT_MESSAGE.SET_TIMER
    params = {
        "start_h": "08",
        "start_min": "00",
        "end_h": "10",
        "end_min": "30",
        "end_timer_set": "11111"
    }
    expected_hex = "55aa10001c0000cb3469000160080001111108000010300017153bce"
    assert build_message(message, params) == expected_hex

def test_build_message_no_end_time():
    message = CLIENT_MESSAGE.SET_TIMER
    params = {
        "start_h": "08",
        "start_min": "00",
        "end_h": "10",
        "end_min": "30",
        "end_timer_set": "00000"
    }
    expected_hex = "55aa10001c0000cb3469000160080000000008000010300017153bab"
    assert build_message(message, params) == expected_hex

def test_read_message_state_parsing():
    # Simulated data with 'state' field at a specific position
    data = "55aa1000237000000000e600e800e6000000005e05000000000000000f0000000003cb"  # (state: waiting)
    msg_type = SERVER_MESSAGE.SEND_VALUES
    result = read_message(data, msg_type)
    assert result["state"] == CHARGER_STATE.WAITING.name

def test_read_message_timer_state_parsing():
    # Simulated data with 'timer_state' field
    data = "55aa1000237000000000e500e600e6000000006702030102000304000f0000000003db"  # 'timer_state' = 3e04
    msg_type = SERVER_MESSAGE.SEND_VALUES
    result = read_message(data, msg_type)
    assert result["timer_state"] == TIMER_STATE.START_END_TIME.name

def test_read_message_total_kwh_parsing():
    # Simulated data with 'total_kwh' field
    data = "55aa100023700d0d0d00e500e500e2005b00af5f06000000000000000f0000000003f6"  # 'total_kwh' = 0a (10 in decimal)
    msg_type = SERVER_MESSAGE.SEND_VALUES
    result = read_message(data, msg_type)
    assert result["total_kwh"] == 17.5

def test_read_message_request_type_parsing():
    # Simulated data with 'request_type' field
    data = "55aa100023700d0d0d00e500e500e2005b00af5f06000000000000000f0000000003f6"  # 'request_type' = 12
    msg_type = SERVER_MESSAGE.SEND_VALUES  # Example message type
    result = read_message(data, msg_type)
    assert result["request_type"] == REQUEST_TYPE.VALUES.name  # Adjust based on actual REQUEST_TYPE mapping

def test_read_message_model_parsing(monkeypatch):
    # Mock the get_model function
    def mock_get_model(data):
        return "BCP-AT1N-L"

    monkeypatch.setattr("custom_components.beny_wifi.communication.get_model", mock_get_model)

    # Simulated data where 'model' is a part of the message
    data = "55aa1000200400014243502d4154314e2d4c00000000000000000000011a01df"
    msg_type = SERVER_MESSAGE.SEND_MODEL  # Example message type with 'model' parameter
    result = read_message(data, msg_type)
    assert result["model"] == "BCP-AT1N-L"


def test_read_message_weekdays_schedule_enabled(monkeypatch):
    # Mock the convert_weekdays_to_dict function
    def mock_convert_weekdays_to_dict(value):
        return {"monday": True, "tuesday": True, "wednesday": False, "thursday": True, "friday": False, "saturday": False, "sunday": True}

    monkeypatch.setattr("custom_components.beny_wifi.communication.convert_weekdays_to_dict", mock_convert_weekdays_to_dict)

    # Simulated data where 'weekdays' indicates an enabled schedule
    data = "55aa100020710201000155000f00197f0c22173b00000101000114060000023f"  # 'weekdays' at index 7 with value != 0
    msg_type = SERVER_MESSAGE.SEND_SETTINGS  # Example message type with 'weekdays' parameter
    result = read_message(data, msg_type)
    assert result["schedule"] == "enabled"
    assert result["weekdays"] == {"sunday": True, "monday": True, "tuesday": True, "wednesday": False, "thursday": True, "friday": False, "saturday": False}

def test_read_message_weekdays_schedule_disabled():
    # Simulated data where 'weekdays' indicates a disabled schedule
    data = "55aa100020710201000155000f00190001000200000001010001140600000243"  # 'weekdays' at index 7 with value = 0
    msg_type = SERVER_MESSAGE.SEND_SETTINGS  # Example message type with 'weekdays' parameter
    result = read_message(data, msg_type)
    assert result["schedule"] == "disabled"
    assert result["weekdays"] == {"sunday": False, "monday": False, "tuesday": False, "wednesday": False, "thursday": False, "friday": False, "saturday": False}

def test_send_charger_command():
    # Simulated data where the command corresponds to a charger action
    data = "55aa10000c0000cb34060121"  # Example: 'command' at index 3 with value 3 (example ID)
    msg_type = CLIENT_MESSAGE.SEND_CHARGER_COMMAND

    result = read_message(data, msg_type)
    assert result["charger_command"] == CHARGER_COMMAND.START.name  # Verifies correct mapping

def test_request_data():
    # Simulated data request
    data = "55aa10000b0000cb347089"
    msg_type = CLIENT_MESSAGE.REQUEST_DATA

    result = read_message(data, msg_type)
    assert result["request_type"] == REQUEST_TYPE.VALUES.name  # Verifies correct mapping

def test_set_timer():
    # Simulated data where timer settings are provided
    data = "55aa10001c0000cb3469000028140001c200000000080000150921d9"
    msg_type = CLIENT_MESSAGE.SET_TIMER

    result = read_message(data, msg_type)
    assert result["start_h"] == 0
    assert result["start_min"] == 0
    assert result["end_h"] == 8
    assert result["end_min"] == 0