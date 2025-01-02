from .const import CLIENT_MESSAGE, COMMON, SERVER_MESSAGE  # noqa: D100


def get_hex(data: int) -> str:
    """Convert int to hex string.

    Args:
        data (int): integer value converted

    Returns:
        str: hex string

    """
    return f"{data:02x}"

def convert_timer(start_time_str: str, end_time_str: str) -> dict:
    """Convert start and end times to timer parameters.

    Args:
        start_time_str (str): charging start time "08:00"
        end_time_str (str): charging end time "10:30"

    Returns:
        dict: timer values

    """
    times = {}
    time_params = start_time_str.split(':')
    times["start_h"] = get_hex(int(time_params[0]))
    times["start_min"] = get_hex(int(time_params[1]))
    time_params = end_time_str.split(':')
    times["end_h"] = get_hex(int(time_params[0]))
    times["end_min"] = get_hex(int(time_params[1]))
    return times

def get_message_type(data: str) -> CLIENT_MESSAGE | SERVER_MESSAGE:
    """Get message structure by id.

    Args:
        data (str): message as ascii hex string

    Returns:
        _type_: _description_

    """
    msg_int = int(data[COMMON.FIXED_PART.value["structure"]["message_id"]], 16)

    if msg_int == 11:
        return CLIENT_MESSAGE.REQUEST_DATA
    if msg_int == 28:
        return CLIENT_MESSAGE.SET_TIMER
    if msg_int == 12:
        return CLIENT_MESSAGE.SEND_CHARGER_COMMAND

    if msg_int == 8:
        return SERVER_MESSAGE.SEND_ACK
    if msg_int == 35:
        return SERVER_MESSAGE.SEND_VALUES
    if msg_int == 17:
        return SERVER_MESSAGE.HANDSHAKE
    if msg_int == 32:
        return SERVER_MESSAGE.SEND_MODEL

    return None

def get_ip(data: str) -> str:
    """Read ip from message.

    Args:
        data (str): message as ascii hex string

    Returns:
        str: ip address

    """

    ip_pos = SERVER_MESSAGE.HANDSHAKE.value["structure"]["ip"]

    # Assuming the IP address starts from index 20 and ends at 28 (adjustable)
    return '.'.join(str(int(data[i:i+2], 16)) for i in range(ip_pos.start, ip_pos.stop, ip_pos.step))

def get_model(data: str) -> str:
    """Read model from message.

    Args:
        data (str): message as ascii hex string

    Returns:
        _type_: _description_

    """

    model_hex = data[SERVER_MESSAGE.SEND_MODEL.value["structure"]["model"]]  # This part seems to be the actual values

    # Convert field values into more readable format (as ASCII if applicable)
    return ''.join(
        chr(int(model_hex[i:i+2], 16))
        for i in range(0, len(model_hex), 2)
        if 32 <= int(model_hex[i:i+2], 16) <= 126
    ).strip()
