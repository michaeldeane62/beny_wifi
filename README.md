<div align="left">
    <img alt="beny-wifi" height="256px" src="https://github.com/Jarauvi/beny-wifi/blob/main/images/logo.png?raw=true">
</div>

# Beny Wifi

<div align="left">
    <img alt="Home Assistant" src="https://img.shields.io/badge/home%20assistant-%2341BDF5.svg"/>
    <img alt="Local polling" src="https://img.shields.io/badge/IOT_class-Local_polling-blue">
    <img alt="Static Badge" src="https://img.shields.io/badge/License-GPL_3.0-green">
</div>

[![Tests](https://github.com/Jarauvi/beny_wifi/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Jarauvi/beny_wifi/actions/workflows/ci.yml)

:warning: *DISCLAIMER: I DO NOT TAKE ANY RESPONSIBILITY OF DAMAGED OR DESTROYED PROPERTY, INJURIES OR HUMAN CASUALTIES. USE WITH YOUR OWN RISK*

This repository contains Home Assistant custom component for controlling and retrieving information from ZJ Beny EV chargers via Wifi. 

Integration mimics ZBox phone app's communication with charger. All parameters and commands are not mapped yet, but assumption is that any charger communicating using ZBox app should work with integration.

### Supported chargers

I have tested integration with 3-phase, non-OCPP model. 1-phase chargers and OCPP equipped devices may work, but I have no possibility to confirm that. If you have one and you're willing to test the compatibility, please share your results and we'll add the model to supported devices :pray: 

### Confirmed to work with models

| Model              | Firmware version |       Status      |
| ------------------ | ---------------- | ----------------- |
| BCP-AT1N-L         | 1.26             |:white_check_mark: |

### Installation

**Using HACS**
- Click three dots in the upper right corner of HACS.
- From the menu, select Custom Repositories
- Paste link to this repository to Repository field
- Select "integration" to Type field
- Find Beny Wifi from the list of integrations
- Restart Home Assistant

**Manually**
- Copy custom_components/beny_wifi folder of this repository as config/custom_components/beny_wifi folder in Home Assistant

**Configuration**
- Find Beny Wifi integration under Settings > Devices & services
- Insert charger IP address. Related on model, port may have to be changed. Also scan interval of the sensors can be configured

### Sensors

Currently, integration contains creates charger devices with following sensors:

| Sensor             | Unit            | Description                                                                   |
| ------------------ | --------------- | ----------------------------------------------------------------------------- |
| state              | [charger state] | Charger state *(abnormal unplugged standby starting unknown waiting charging)*|
| current1           | [A]             | Current L1                                                                    |
| current2           | [A]             | Current L2                                                                    |
| current3           | [A]             | Current L3                                                                    |
| voltage1           | [V]             | Voltage L1                                                                    |
| voltage2           | [V]             | Voltage L2                                                                    |
| voltage3           | [V]             | Voltage L3                                                                    |
| power              | [kW]            | Current power consumption                                                     |
| total_energy       | [kWh]           | Session based charged capacity                                                |
| timer_start        | [timestamp]     | Currently set timer start time                                                |
| timer_end          | [timestamp]     | Currently set timer end time                                                  |

### Actions

Currently integration supports following actions:
- beny_wifi.start_charging (*device_id*)
- beny_wifi.stop_charging (*device_id*)
- beny_wifi.set_timer (*device_id | start time | end time*)
- beny_wifi.reset_timer (*device_id*)

### Roadmap

I am pretty busy with the most adorable baby boy right now, but I'll be adding some bells and whistles when I have a moment:
- action to set max amps
- map missing parameters as sensors (like outdoor temperature)
- add integration to hacs
