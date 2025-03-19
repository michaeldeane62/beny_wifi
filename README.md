<div align="left">
    <img alt="beny-wifi" width="50%" src="https://github.com/Jarauvi/beny-wifi/blob/main/images/logo@2x.png?raw=true">
</div>

# ⚡ Beny Wifi ⚡

<div align="left">
    <img alt="Home Assistant" src="https://img.shields.io/badge/home%20assistant-%2341BDF5.svg"/>
    <img alt="Local polling" src="https://img.shields.io/badge/IOT_class-Local_polling-blue">
    <img alt="Static Badge" src="https://img.shields.io/badge/License-GPL_3.0-green">
    <img alt="Version" src="https://img.shields.io/github/manifest-json/v/Jarauvi/beny_wifi?filename=custom_components%2Fbeny_wifi%2Fmanifest.json&label=Version">
</div>

⚠️*DISCLAIMER: I DO NOT TAKE ANY RESPONSIBILITY OF DAMAGED OR DESTROYED PROPERTY, INJURIES OR HUMAN CASUALTIES. USE AT YOUR OWN RISK*

<div align="left">
    <img alt="Sensors" height="256px" src="https://github.com/Jarauvi/beny-wifi/blob/main/images/sensors.png?raw=true">
</div>

This repository contains Home Assistant custom component for controlling and retrieving information from ZJ Beny EV chargers via Wifi. 

Integration mimics ZBox phone app's communication with charger. All parameters and commands are not mapped yet, but assumption is that any charger communicating with ZBox app should work with integration.

### Supported chargers

I have tested integration with 3-phase, non-OCPP model. 1-phase chargers and OCPP equipped devices may work, but I have no possibility to confirm that. If you have one and you're willing to test the compatibility, please share your results and I will add the model to supported devices 🙏 

### Confirmed to work with models

| Model              | Firmware version |       Status      |
| ------------------ | ---------------- | ----------------- |
| BCP-AT1N-L         | 1.26             | ✅            |

### Installation

**Using HACS**
- Click three dots in the upper right corner of HACS.
- From the menu, select Custom Repositories
- Paste link of this repository to Repository field
- Select "integration" to Type field
- Find and install Beny Wifi from the list of integrations
- Restart Home Assistant

**Manually**
- Copy contents of custom_components/beny_wifi folder of this repository to config/custom_components/beny_wifi folder in Home Assistant

**Configuration**
- Find Beny Wifi integration under Settings > Devices & services
- Insert charger serial number and pin. Also scan interval of the sensors can be configured

### Sensors

Currently, integration creates charger device with following sensors:

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
| maximum_session_consumption       | [kWh]           | Session based maximum consumption                                                |
| timer_start        | [timestamp]     | Currently set timer start time                                                |
| timer_end          | [timestamp]     | Currently set timer end time                                                  |

### Actions

Currently integration supports following actions:

*Only when EV is plugged to charger:*
- beny_wifi.start_charging (*device_id*)
- beny_wifi.stop_charging (*device_id*)
- beny_wifi.set_timer (*device_id | start time | end time*)
- beny_wifi.reset_timer (*device_id*)
- beny_wifi.set_maximum_session_consumption (*device_id | maximum_consumption*)

*Any state:*
- beny_wifi.request_weekly_schedule (*device_id*)
- beny_wifi.set_weekly_schedule (*device_id | sunday | monday | tuesday | wednesday | thursday | friday | saturday | start time | end time)
- beny_wifi.set_maximum_monthly_consumption (*device_id | maximum_consumption*)

### Roadmap

I am pretty busy with the most adorable baby boy right now, but I'll be adding some bells and whistles when I have a moment:
- map missing parameters as sensors (like internal device temperature)
