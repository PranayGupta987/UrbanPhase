"""
data.gov.sg Weather API Client for Singapore
Fetches live weather data
"""
import os
import json
import requests
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# data.gov.sg Current Weather API
DATA_GOV_SG_WEATHER_URL = "https://api.data.gov.sg/v1/environment/2-hour-weather-forecast"
DATA_GOV_SG_AIR_TEMP_URL = "https://api.data.gov.sg/v1/environment/air-temperature"
DATA_GOV_SG_RELATIVE_HUMIDITY_URL = "https://api.data.gov.sg/v1/environment/relative-humidity"
DATA_GOV_SG_WIND_SPEED_URL = "https://api.data.gov.sg/v1/environment/wind-speed"
DATA_GOV_SG_RAINFALL_URL = "https://api.data.gov.sg/v1/environment/rainfall"


def _load_mock_weather() -> Dict[str, Any]:
    """Load mock weather data"""
    return {
        "temp": 28.5,
        "temperature": 28.5,
        "humidity": 75.0,
        "wind_speed": 15.0,
        "rainfall": 0.0,
        "description": "Partly cloudy",
        "city": "Singapore",
        "source": "mock"
    }


def fetch_live_weather() -> Dict[str, Any]:
    """Fetch live weather data from data.gov.sg"""
    try:
        # Get air temperature
        temp = 28.0
        try:
            response = requests.get(DATA_GOV_SG_AIR_TEMP_URL, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if "items" in data and len(data["items"]) > 0:
                    readings = data["items"][0].get("readings", [])
                    if readings:
                        temp = readings[0].get("value", 28.0)
        except:
            pass
        
        # Get humidity
        humidity = 75.0
        try:
            response = requests.get(DATA_GOV_SG_RELATIVE_HUMIDITY_URL, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if "items" in data and len(data["items"]) > 0:
                    readings = data["items"][0].get("readings", [])
                    if readings:
                        humidity = readings[0].get("value", 75.0)
        except:
            pass
        
        # Get wind speed
        wind_speed = 15.0
        try:
            response = requests.get(DATA_GOV_SG_WIND_SPEED_URL, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if "items" in data and len(data["items"]) > 0:
                    readings = data["items"][0].get("readings", [])
                    if readings:
                        wind_speed = readings[0].get("value", 15.0)
        except:
            pass
        
        # Get rainfall
        rainfall = 0.0
        try:
            response = requests.get(DATA_GOV_SG_RAINFALL_URL, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if "items" in data and len(data["items"]) > 0:
                    readings = data["items"][0].get("readings", [])
                    if readings:
                        rainfall = readings[0].get("value", 0.0)
        except:
            pass
        
        return {
            "temp": round(temp, 1),
            "temperature": round(temp, 1),
            "humidity": round(humidity, 1),
            "wind_speed": round(wind_speed, 1),
            "rainfall": round(rainfall, 1),
            "description": "Current weather",
            "city": "Singapore",
            "source": "live"
        }
        
    except Exception as e:
        logger.error(f"Error fetching weather data: {e}", exc_info=True)
        return _load_mock_weather()
