"""Sensors for Beny Wifi."""

from homeassistant.helpers.entity import DeviceInfo, Entity

from .const import DOMAIN, MODEL, SERIAL


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    device_id = config_entry.data[SERIAL]
    device_model = config_entry.data[MODEL]
    sensors = [
        BenyWifiSensor(coordinator, "state", "Charger State", device_id=device_id, device_model=device_model),
        BenyWifiSensor(coordinator, "power", "Power", "kW", device_id=device_id, device_model=device_model),
        BenyWifiSensor(coordinator, "voltage1", "Voltage L1", "V", device_id=device_id, device_model=device_model),
        BenyWifiSensor(coordinator, "voltage2", "Voltage L2", "V", device_id=device_id, device_model=device_model),
        BenyWifiSensor(coordinator, "voltage3", "Voltage L3", "V", device_id=device_id, device_model=device_model),
        BenyWifiSensor(coordinator, "current1", "Current L1", "A", device_id=device_id, device_model=device_model),
        BenyWifiSensor(coordinator, "current2", "Current L2", "A", device_id=device_id, device_model=device_model),
        BenyWifiSensor(coordinator, "current3", "Current L3", "A", device_id=device_id, device_model=device_model),
        BenyWifiSensor(coordinator, "max_current", "Max Current", "A", device_id=device_id, device_model=device_model),
        BenyWifiSensor(coordinator, "total_kwh", "Total Energy", "kWh", device_id=device_id, device_model=device_model),
        BenyWifiSensor(coordinator, "timer_start", "Timer Start", device_id=device_id, device_model=device_model),
        BenyWifiSensor(coordinator, "timer_end", "Timer End", device_id=device_id, device_model=device_model),
    ]

    async_add_entities(sensors)

class BenyWifiSensor(Entity):
    """Charger sensor model."""

    def __init__(self, coordinator, key, name, unit=None, device_id=None, device_model=None):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self.key = key
        self._name = name
        self._unit = unit
        self._device_id = device_id
        self._device_model = device_model
        self.entity_id = f"sensor.{device_id}_{key}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return a unique ID for this sensor."""
        return f"{self._device_id}_{self.key}"

    @property
    def state(self):
        """Return the current state of the sensor."""
        return self.coordinator.data.get(self.key)

    @property
    def unit_of_measurement(self):
        """Sensor unit."""
        return self._unit

    async def async_update(self):
        """Update the sensor."""
        await self.coordinator.async_request_refresh()

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers = {(DOMAIN, self._device_id)},
            name=f"Beny Charger {self._device_id}",
            manufacturer = "ZJ Beny",
            model = self._device_model,
        )
