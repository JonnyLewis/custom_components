import logging
from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.selector import selector
from homeassistant.const import CONF_NAME, CONF_ENTITY_ID

_LOGGER = logging.getLogger(__name__)

class SunsynkForecastConfigFlow(config_entries.ConfigFlow, domain="sunsynk_forecast"):
    """Handle a config flow for Sunsynk Forecast."""
    
    VERSION = 1

    def __init__(self):
        """Initialize the flow."""
        self._solar_entity = None
        self._load_entity = None
        self._battery_entity = None
        self._grid_entity = None
        self._weather_entity = None

    async def async_step_user(self, user_input=None):
        """Handle the user input."""
        if user_input is not None:
            self._solar_entity = user_input.get("solar_entity")
            self._load_entity = user_input.get("load_entity")
            self._battery_entity = user_input.get("battery_entity")
            self._grid_entity = user_input.get("grid_entity")
            self._weather_entity = user_input.get("weather_entity")

            # Store the configuration and finish setup
            return self.async_create_entry(
                title="Sunsynk Forecast",
                data={
                    "solar_entity": self._solar_entity,
                    "load_entity": self._load_entity,
                    "battery_entity": self._battery_entity,
                    "grid_entity": self._grid_entity,
                    "weather_entity": self._weather_entity,
                },
            )

        # Show the user the config flow
        return self.async_show_form(
            step_id="user",
            data_schema=cv.Schema({
                "solar_entity": selector({"entity": "sensor"}),
                "load_entity": selector({"entity": "sensor"}),
                "battery_entity": selector({"entity": "sensor"}),
                "grid_entity": selector({"entity": "sensor"}),
                "weather_entity": selector({"entity": "sensor"}),
            }),
        )
