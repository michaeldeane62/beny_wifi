DOMAIN = "beny-wifi"
COMMANDS = {
    "START": bytes.fromhex("353561613130303030633030303063623334303630313231"), 
    "STOP": bytes.fromhex("353561613130303030633030303063623334303630303230"),  
    "UPDATE": bytes.fromhex("35356161313030303062303030306362333437303839"),
}

STATES = {
    "6102": "standby",
    "5d05": "waiting",
    "5e05": "charging",
    "6103": "stopping",
    "6105": "abnormal",
    "6100": "abnormal",
}

POS = {
    "state": (38, 42),
    "voltage_1": (20, 22),
    "voltage_2": (24, 26),
    "voltage_3": (28, 30),
    "current_1": (13, 14),
    "current_2": (15, 16),
    "current_3": (17, 18),
    "power": (30, 34)
}