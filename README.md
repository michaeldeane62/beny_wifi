# beny-wifi

This repository contains Home Assistant addon for controlling and retrieving information from ZJ Beny (non-ocpp) 3-phase chargers

Thanks to plain unencrypted udp packets, this integration mimics ZBox phone app's communication with charger.

*Sensors*
Currently, integration contains sensor for charger with following parameters

Value: Charger state (standby | waiting | starting charging | charging | abnormal)
Attributes:
- Current A
- Current B
- Current C
- Voltage A
- Voltage B
- Voltage C
- Power

*Services*
For now, integration supports only commands to start and stop charging
