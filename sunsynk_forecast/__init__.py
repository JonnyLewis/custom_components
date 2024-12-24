from homeassistant.core import HomeAssistant
from homeassistant import config_entries

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Sunsynk Forecast integration."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: config_entries.ConfigEntry):
    """Set up Sunsynk Forecast from a config entry."""
    hass.data.setdefault("sunsynk_forecast", {})
    hass.data["sunsynk_forecast"][entry.entry_id] = entry.data
    return True
