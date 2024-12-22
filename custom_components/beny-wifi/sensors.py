from homeassistant.helpers.entity import Entity
import logging
from .const import COMMANDS, POS, STATES

_LOGGER = logging.getLogger(__name__)

class BenyStateSensor(Entity):
    """Representation of the charger state sensor."""

    def __init__(self, name, fetch_state):
        """Initialize the sensor."""
        self._name = name
        self._state = None
        self._fetch_state = fetch_state

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the current state of the sensor."""
        return self._state

    async def async_update(self):
        """Fetch the latest state from the charger."""
        _LOGGER.debug("Updating charger state...")
        response = await self._fetch_state()

        if response:
            state_code = response[POS["STATE"][0]:POS["STATE"][1]] 
            self._state = STATES.get(state_code, "unknown")
            _LOGGER.debug(f"Updated state: {self._state}")
        else:
            _LOGGER.warning("Failed to update EV Charger state.")


class BenyMeasurementSensor(Entity):
    """Representation of an charger measurement sensor."""

    def __init__(self, name, fetch_state, measurement_type):
        """Initialize the sensor."""
        self._name = name
        self._state = None
        self._fetch_state = fetch_state
        self._measurement_type = measurement_type

    def get_ascii(data):
        # Convert hex to ASCII
        ascii_data = binascii.unhexlify(data).decode('utf-8', errors='replace')  # Replace errors if any
        return ascii_data

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the current measurement value."""
        return self._state

    async def async_update(self):
        """Fetch the latest measurement from the charger."""
        _LOGGER.debug(f"Updating {self._name}...")
        response = await self._fetch_state()
        response = get_ascii(response)

        if response:
            try:
                start, end = POS[self._measurement_type]
                raw_value = response[start:end]
                self._state = int(raw_value, 16) / 100.0  # Convert hex to float
                _LOGGER.debug(f"Updated {self._name}: {self._state}")
            except KeyError:
                _LOGGER.error(f"Unknown measurement type: {self._measurement_type}")
            except Exception as e:
                _LOGGER.error(f"Failed to parse measurement: {e}")
        else:
            _LOGGER.warning(f"Failed to update {self._name}.")
