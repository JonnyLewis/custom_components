import logging
import openai
import requests
from datetime import datetime, timedelta
from homeassistant.helpers.entity import Entity
from homeassistant.components.button import ButtonEntity
from homeassistant.const import CONF_NAME

# Setup logging
_LOGGER = logging.getLogger(__name__)

# Configuration variables (from config entry)
openai.api_key = "your_openai_api_key"  # Replace with your OpenAI API key

# Function to fetch historical data of a sensor
def fetch_sensor_history(entity_id, start_time=None, end_time=None):
    """Fetch historical data of a sensor from Home Assistant."""
    url = f"http://<your-home-assistant-url>:8123/api/history/period"
    params = {"filter_entity_id": entity_id}
    if start_time:
        params["start_time"] = start_time
    if end_time:
        params["end_time"] = end_time

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data[0] if data else []
    except requests.exceptions.RequestException as e:
        _LOGGER.error(f"Error fetching history for {entity_id}: {e}")
        return []

def get_historical_data(solar_entity, load_entity, battery_entity, grid_entity, weather_entity):
    """Get historical solar, weather, load, battery, and grid data."""
    start_time = (datetime.now() - timedelta(days=30)).isoformat()  # Last 30 days
    end_time = datetime.now().isoformat()

    solar_data = fetch_sensor_history(solar_entity, start_time, end_time)
    weather_data = fetch_sensor_history(weather_entity, start_time, end_time)
    load_data = fetch_sensor_history(load_entity, start_time, end_time)
    battery_data = fetch_sensor_history(battery_entity, start_time, end_time)
    grid_data = fetch_sensor_history(grid_entity, start_time, end_time)

    return solar_data, weather_data, load_data, battery_data, grid_data

def predict_future_load_and_solar(solar_data, weather_data, load_data, battery_data, grid_data):
    """Predict future solar production and load based on given data."""
    battery_state = battery_data[-1]['state'] if battery_data else 0
    battery_capacity = 100  # Example value, adjust to match your system's capacity
    is_battery_full = battery_state >= battery_capacity

    adjusted_solar = []
    for i in range(len(solar_data)):
        if is_battery_full and load_data[i]['state'] < 50:
            adjusted_solar.append(solar_data[i]['state'] * 0.5)
        else:
            adjusted_solar.append(solar_data[i]['state'])

    prompt = f"""
    I have the following historical data for the last 30 days:
    Solar Production: {adjusted_solar}
    Weather (Temperature): {weather_data}
    Load Data: {load_data}
    Battery Data: {battery_data}
    Grid Data: {grid_data}
    
    Based on this data, please predict the solar production and load for the next day.
    """

    try:
        response = openai.Completion.create(
            engine="gpt-4",
            prompt=prompt,
            max_tokens=150,
            temperature=0.7,
        )

        prediction = response.choices[0].text.strip()
        return prediction
    except Exception as e:
        _LOGGER.error(f"Error predicting future data: {e}")
        return None

class SunsynkForecastButton(ButtonEntity):
    """Button to trigger Sunsynk Forecast prediction."""

    def __init__(self, name, solar_entity, load_entity, battery_entity, grid_entity, weather_entity):
        self._name = name
        self._solar_entity = solar_entity
        self._load_entity = load_entity
        self._battery_entity = battery_entity
        self._grid_entity = grid_entity
        self._weather_entity = weather_entity

    @property
    def name(self):
        return self._name

    async def async_press(self):
        """Fetch data and call prediction."""
        solar_data, weather_data, load_data, battery_data, grid_data = get_historical_data(
            self._solar_entity, self._load_entity, self._battery_entity, self._grid_entity, self._weather_entity
        )

        prediction = predict_future_load_and_solar(solar_data, weather_data, load_data, battery_data, grid_data)
        
        if prediction:
            _LOGGER.info(f"Predicted Solar and Load Data: {prediction}")
        else:
            _LOGGER.error("Prediction failed.")
