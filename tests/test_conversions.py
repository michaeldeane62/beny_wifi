# tests/test_conversions.py
from custom_components.beny_wifi.conversions import (
    convert_timer,
    convert_schedule,
    convert_weekdays_to_dict,
    convert_weekdays_to_hex,
    get_hex,
    get_message_type,
    get_model
)

from custom_components.beny_wifi.const import CLIENT_MESSAGE, SERVER_MESSAGE

def test_convert_timer():
    start_time = "08:00"
    end_time = "10:30"
    expected = {
        "start_h": "08",
        "start_min": "00",
        "end_timer_set": "11111",
        "end_h": "0a",
        "end_min": "1e"
    }
    assert convert_timer(start_time, end_time) == expected

def test_convert_schedule():
    weekdays = [True, False, True, False, True, False, True]
    start_time = "09:00"
    end_time = "11:00"
    expected = {
        "weekdays": "55",
        "start_h": "09",
        "start_min": "00",
        "end_h": "0b",
        "end_min": "00"
    }
    assert convert_schedule(weekdays, start_time, end_time) == expected

def test_convert_weekdays_to_dict():
    weekdays_hex = 0b1010101  # Binary representation
    expected = {
        "sunday": True,
        "monday": False,
        "tuesday": True,
        "wednesday": False,
        "thursday": True,
        "friday": False,
        "saturday": True,
    }
    assert convert_weekdays_to_dict(weekdays_hex) == expected

def test_convert_weekdays_to_hex():
    weekdays = [True, False, True, False, True, False, True]
    expected = "55"  # Hex representation
    assert convert_weekdays_to_hex(weekdays) == expected

def test_convert_timer_defaults():
    # Input with no end timer set
    start_time = "9:30"
    end_time = None

    # Call the function with input missing end timer values
    result = convert_timer(start_time, end_time)

    # Assertions for default values
    assert result["end_timer_set"] == "00000", "Default end_timer_set not set correctly"
    assert result["end_h"] == get_hex(0), "Default end_h not set to '0' in hex format"
    assert result["end_min"] == get_hex(0), "Default end_min not set to '0' in hex format"

def test_get_message_type():
    # Test CLIENT_MESSAGE
    assert get_message_type("55aa10000b0000cb347089") == CLIENT_MESSAGE.REQUEST_DATA, "CLIENT_MESSAGE.REQUEST_DATA not returned for msg_int 11"
    assert get_message_type("55aa10001c0000cb3469000028140001c200000000080000150921d9") == CLIENT_MESSAGE.SET_TIMER, "CLIENT_MESSAGE.SET_TIMER not returned for msg_int 28"
    assert get_message_type("55aa10000c0000cb34060121") == CLIENT_MESSAGE.SEND_CHARGER_COMMAND, "CLIENT_MESSAGE.SEND_CHARGER_COMMAND not returned for msg_int 12"
    
    # Test SERVER_MESSAGE
    assert get_message_type("55aa100008690181") == SERVER_MESSAGE.SEND_ACK, "SERVER_MESSAGE.SEND_ACK not returned for msg_int 8"
    assert get_message_type("55aa1000237000000000e600e800e6000000006102000000000000000f0000000003cb") == SERVER_MESSAGE.SEND_VALUES, "SERVER_MESSAGE.SEND_VALUES not returned for msg_int 35"
    assert get_message_type("55aa100011030e5a7937c0a801220d05d8") == SERVER_MESSAGE.HANDSHAKE, "SERVER_MESSAGE.HANDSHAKE not returned for msg_int 17"
    assert get_message_type("55aa1000200400014243502d4154314e2d4c00000000000000000000011a01df") == SERVER_MESSAGE.SEND_MODEL, "SERVER_MESSAGE.SEND_MODEL not returned for msg_int 32"
    
    # Test for invalid msg_int
    assert get_message_type("55aafff0fff000000000e600e800e6000000006102000000000000000f0000000003cb") is None, "get_message_type should return None for unknown msg_int"

def test_get_model():
    # Test data with model value 'BCP-AT1N-L'
    data = "0000000000000000000000000000000000000000000000004243502d4154314e2d4c0000000000000000000000000000000000000000"
    expected_model = "BCP-AT1N-L"
    assert get_model(data) == expected_model, f"Expected model 'BCP-AT1N-L' but got {get_model(data)}"

    # Test data with model value 'EV-CHARGER-001'
    data = "00000000000000000000000000000000000000000000000045562d434841524745522d303031000000000000000000000000000000000000"
    expected_model = "EV-CHARGER-001"
    assert get_model(data) == expected_model, f"Expected model 'EV-CHARGER-001' but got {get_model(data)}"
    
    # Test data where model field is empty
    data = "000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    expected_model = ""
    assert get_model(data) == expected_model, f"Expected empty model but got {get_model(data)}"

    # Test data where model field has non-ASCII characters (to see how it's handled)
    data = "0000000000000000000000000000000000000000000000004e6f6e2d4153434949204348504552"
    expected_model = "Non-ASCII CHPE"  # This would depend on the actual data and its ASCII conversion
    assert get_model(data) == expected_model, f"Expected model 'Non-ASCII CHPE' but got {get_model(data)}"