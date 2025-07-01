"""Sensors for Beny Wifi."""

from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import CHARGER_TYPE, DLB, DOMAIN, MODEL, SERIAL


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    device_id = config_entry.data[SERIAL]
    device_model = config_entry.data[MODEL]
    device_type = config_entry.data[CHARGER_TYPE]
    dlb = config_entry.data[DLB]

    sensors = []

    if device_type == '1P':
        sensors = [
            BenyWifiChargerStateSensor(coordinator, "charger_state", device_id, device_model),
            BenyWifiPowerSensor(coordinator, "power", device_id, device_model),
            BenyWifiVoltageSensor(coordinator, "voltage1", device_id, device_model),
            BenyWifiCurrentSensor(coordinator, "current1", device_id, device_model),
            BenyWifiCurrentSensor(coordinator, "max_current", device_id, device_model),
            BenyWifiEnergySensor(coordinator, "total_kwh", device_id, device_model),
            BenyWifiTemperatureSensor(coordinator, "temperature", device_id, device_model),
            BenyWifiEnergySensor(coordinator, "maximum_session_consumption", device_id, device_model, icon="mdi:meter-electric"),
            BenyWifiTimerSensor(coordinator, "timer_start", device_id, device_model, icon="mdi:timer-sand-full"),
            BenyWifiTimerSensor(coordinator, "timer_end", device_id, device_model, icon="mdi:timer-sand-empty"),
        ]
    elif device_type == '3P':
        sensors = [
            BenyWifiChargerStateSensor(coordinator, "charger_state", device_id, device_model),
            BenyWifiPowerSensor(coordinator, "power", device_id, device_model),
            BenyWifiVoltageSensor(coordinator, "voltage1", device_id, device_model),
            BenyWifiVoltageSensor(coordinator, "voltage2", device_id, device_model),
            BenyWifiVoltageSensor(coordinator, "voltage3", device_id, device_model),
            BenyWifiCurrentSensor(coordinator, "current1", device_id, device_model),
            BenyWifiCurrentSensor(coordinator, "current2", device_id, device_model),
            BenyWifiCurrentSensor(coordinator, "current3", device_id, device_model),
            BenyWifiCurrentSensor(coordinator, "max_current", device_id, device_model),
            BenyWifiEnergySensor(coordinator, "total_kwh", device_id, device_model),
            BenyWifiTemperatureSensor(coordinator, "temperature", device_id, device_model),
            BenyWifiEnergySensor(coordinator, "maximum_session_consumption", device_id, device_model, icon="mdi:meter-electric"),
            BenyWifiTimerSensor(coordinator, "timer_start", device_id, device_model, icon="mdi:timer-sand-full"),
            BenyWifiTimerSensor(coordinator, "timer_end", device_id, device_model, icon="mdi:timer-sand-empty"),
        ]

    if dlb:
        sensors.extend([
            BenyWifiPowerSensor(coordinator, "grid_import", device_id, device_model, icon="mdi:transmission-tower-import"),
            BenyWifiPowerSensor(coordinator, "grid_export", device_id, device_model, icon="mdi:transmission-tower-export"),
            BenyWifiPowerSensor(coordinator, "solar_power", device_id, device_model, icon="mdi:solar-power-variant"),
            BenyWifiPowerSensor(coordinator, "ev_power", device_id, device_model, icon="mdi:car-electric"),
            BenyWifiPowerSensor(coordinator, "house_power", device_id, device_model, icon="mdi:home-lightning-bolt"),
        ])

    async_add_entities(sensors)


class BenyWifiSensor(CoordinatorEntity):
    def __init__(self, coordinator, key, device_id, device_model, icon=None):
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.key = key
        self._device_id = device_id
        self._device_model = device_model
        self._attr_icon = icon
        self._attr_name = key.replace("_", " ").title()
        self._attr_unique_id = f"{device_id}_{key}"
        self._attr_has_entity_name = True

    @property
    def state(self):
        return self.coordinator.data.get(self.key)

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=f"Beny Charger {self._device_id}",
            manufacturer="ZJ Beny",
            model=self._device_model,
        )


class BenyWifiChargerStateSensor(BenyWifiSensor):
    def __init__(self, coordinator, key, device_id, device_model, icon="mdi:ev-station"):
        super().__init__(coordinator, key, device_id, device_model, icon)


class BenyWifiCurrentSensor(BenyWifiSensor):
    def __init__(self, coordinator, key, device_id, device_model, icon="mdi:sine-wave"):
        super().__init__(coordinator, key, device_id, device_model, icon)

    @property
    def unit_of_measurement(self):
        return UnitOfElectricCurrent.AMPERE


class BenyWifiVoltageSensor(BenyWifiSensor):
    def __init__(self, coordinator, key, device_id, device_model, icon="mdi:flash-triangle"):
        super().__init__(coordinator, key, device_id, device_model, icon)

    @property
    def unit_of_measurement(self):
        return UnitOfElectricPotential.VOLT


class BenyWifiPowerSensor(BenyWifiSensor):
    def __init__(self, coordinator, key, device_id, device_model, icon="mdi:ev-plug-type2"):
        super().__init__(coordinator, key, device_id, device_model, icon)

    @property
    def unit_of_measurement(self):
        return UnitOfPower.KILO_WATT


class BenyWifiTemperatureSensor(BenyWifiSensor):
    def __init__(self, coordinator, key, device_id, device_model, icon="mdi:thermometer"):
        super().__init__(coordinator, key, device_id, device_model, icon)

    @property
    def unit_of_measurement(self):
        return self.hass.config.units.temperature_unit


class BenyWifiEnergySensor(BenyWifiSensor):
    def __init__(self, coordinator, key, device_id, device_model, icon="mdi:power-plug-battery"):
        super().__init__(coordinator, key, device_id, device_model, icon)

    @property
    def unit_of_measurement(self):
        return UnitOfEnergy.KILO_WATT_HOUR


class BenyWifiTimerSensor(BenyWifiSensor):
    def __init__(self, coordinator, key, device_id, device_model, icon="mdi:timer-sand-empty"):
        super().__init__(coordinator, key, device_id, device_model, icon)
