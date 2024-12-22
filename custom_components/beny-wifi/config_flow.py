from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN

class BenyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the Beny WiFI integration"""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            # Validate the input if necessary
            return self.async_create_entry(title="Beny WiFi", data=user_input)

        # Show the form to the user
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("ip_address"): str,
                vol.Required("port", default=3333): int,
            }),
        )
