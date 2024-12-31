<div align="left">
    <img alt="beny-wifi" height="256px" src="https://github.com/Jarauvi/beny-wifi/blob/main/images/logo.png?raw=true">
</div>

# beny-wifi

![Home Assistant](https://img.shields.io/badge/home%20assistant-%2341BDF5.svg?style=for-the-badge&logo=home-assistant&logoColor=white)


:warning: *DISCLAIMER: I DO NOT TAKE ANY RESPONSIBILITY OF DAMAGED OR DESTROYED PROPERTY, INJURIES OR HUMAN CASUALTIES. USE WITH YOUR OWN RISK*

This repository contains Home Assistant addon for controlling and retrieving information from ZJ Beny EV chargers. 

Integration mimics ZBox phone app's communication with charger. I have not mapped all parameters and commands yet. I think that any charger communicating with ZBox app should work.

### Supported chargers

I have tested integration with 3-phase, non-OCPP model. 1-phase chargers and OCPP equipped devices may work, but I have no possibility to confirm that. If you have one and you're willing to test the compatibility, please share your results and we'll add the model to supported devices :pray: 

### Confirmed to work with models

| Model              | Firmware version |       Status      |
| ------------------ | ---------------- | ----------------- |
| BCP-AT1N-L         | 1.26             |:white_check_mark: |

### Sensors

Currently, integration contains sensor for charger with following parameters

Value: 
- Charger state (standby | waiting | starting charging | charging | abnormal)

Attributes:
- Current A [A]
- Current B [A]
- Current C [A]
- Voltage A [V]
- Voltage B [V]
- Voltage C [V]
- Power [kW]
- Total energy [kWh]
- Timer start time [UTC timestamp]
- Timer end time [UTC timestamp]

### Actions

Currently integration supports following actions:
- start charging
- stop charging
- set timer (start time > end time)

### Roadmap

I am pretty busy with the most adorable baby boy right now, but I'll be adding some bells and whistles when I have a moment:
- action to set max amps
- map missing parameters as sensors (like outdoor temperature)
