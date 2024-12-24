from homeassistant.helpers.entity import ButtonEntity
from homeassistant.core import HomeAssistant
from .sensor import get_historical_data, predict_future_load_and_solar

class SunsynkForecastButton(ButtonEntity):
    """Representation of a button that triggers the Sunsynk forecast prediction."""

    def __init__(self, hass: HomeAssistant, name: str, solar_entity: str, load_entity: str, battery_entity: str, grid_entity: str, weather_entity: str):
        self._hass = hass
        self._name = name
        self._solar_entity = solar_entity
        self._load_entity = load_entity
        self._battery_entity = battery_entity
        self._grid_entity = grid_entity
        self._weather_entity = weather_entity

    @property
    def name(self):
        """Return the name of the button."""
        return self._name

    def press(self):
        """Handle the button press."""
        # Get historical data
        solar_data, weather_data, load_data, battery_data, grid_data = get_historical_data(
            self._solar_entity, self._load_entity, self._battery_entity, self._grid_entity, self._weather_entity
        )

        if solar_data and weather_data and load_data and battery_data and grid_data:
            prediction = predict_future_load_and_solar(solar_data, weather_data, load_data, battery_data, grid_data)
            if prediction:
                # Here you can trigger any action with the prediction
                # For example, update a sensor with the prediction result or log it
                self._hass.states.set("sensor.sunsynk_forecast", prediction)
