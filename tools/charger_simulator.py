import socket
import json
import time
import os
import binascii
import re
from copy import deepcopy

from const import SERVER_MESSAGE
from communication import build_message
from conversions import get_hex
import socket
import struct

CONFIG_FILE = "messages.json"
UDP_IP = "0.0.0.0"
UDP_PORT = 3333

def ip_to_hex(ip: str) -> str:
    """Convert an IPv4 address string to a hex string."""
    packed_ip = socket.inet_aton(ip)  
    hex_str = packed_ip.hex()
    return hex_str

def check_message(received_message, pattern):
    regex_pattern = pattern.replace('*', '.*')
    
    if re.match(regex_pattern, received_message):
        return True
    
    return False

def hex_to_str(hex_str):
    try:
        bytes_data = binascii.unhexlify(hex_str)
        return bytes_data.decode('ascii', errors='ignore')
    except (binascii.Error, UnicodeDecodeError):
        return None

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

responses = load_config()
last_modified = None

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening for UDP packets on port {UDP_PORT}...")

while True:
    try:
        modified_time = time.ctime(os.path.getmtime(CONFIG_FILE))
        if modified_time != last_modified:
            conf = load_config()
            last_modified = modified_time
            print("Config reloaded.")
    except Exception as e:
        print(f"Error checking config file: {e}")

    data, addr = sock.recvfrom(1024)
    data = str(data.decode('ascii')).strip()
    print(f"Received from {addr}: {data}")

    response = deepcopy(conf['responses'])
    for request, response in response.items():
        if check_message(data, request):
            if type(response) == str:
                sock.sendto(response.encode('ascii'), addr)
            elif type(response) == dict:
                mtype = SERVER_MESSAGE[response['type']]
                for key, value in response['params'].items():
                    if key == "ip":
                        response['params'][key] = ip_to_hex(value)
                    elif key == "model":
                        response['params'][key] = value.encode().hex()
                        while len(response['params'][key]) < 41:
                            response['params'][key] += '0'
                        response['params'][key] += '11900'
                    else:
                        response['params'][key] = get_hex(value)
                response = build_message(mtype, params=response['params'])
                sock.sendto(response.encode('ascii'), addr)
            print(f"Sent to {addr}: {response}")
