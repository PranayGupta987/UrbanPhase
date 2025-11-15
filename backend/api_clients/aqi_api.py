"""
WAQI Air Quality API Client for Singapore
Fetches live AQI data with fallback to mock data
"""
import os
import json
import requests
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

WAQI_URL = "https://api.waqi.info/feed/@1666/"
WAQI_TOKEN = "c5c8204b44d6579b0def08c45059faca2430308f"
DATA_GOV_SG_POLLUTANT_URL = "https://api.data.gov.sg/v1/environment/pm25"

def _create_default_aqi_geojson() -> Dict[str, Any]:
    """Create default valid GeoJSON for Singapore AQI"""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [103.85, 1.29]
                },
                "properties": {
                    "aqi": 65,
                    "pm25": 25.0,
                    "pm10": 35.0,
                    "category": "Moderate",
                    "station": "Central Singapore"
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [103.88, 1.32]
                },
                "properties": {
                    "aqi": 55,
                    "pm25": 20.0,
                    "pm10": 28.0,
                    "category": "Moderate",
                    "station": "North Singapore"
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [103.82, 1.27]
                },
                "properties": {
                    "aqi": 75,
                    "pm25": 30.0,
                    "pm10": 42.0,
                    "category": "Moderate",
                    "station": "South Singapore"
                }
            }
        ]
    }

def _load_mock_data() -> Dict[str, Any]:
    """Load mock AQI data - guaranteed valid GeoJSON"""
    mock_path = os.path.join(
        os.path.dirname(__file__), "..", "mock_data", "aqi.geojson"
    )
    
    if not os.path.exists(mock_path):
        mock_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "aqi.geojson"
        )
    
    if os.path.exists(mock_path):
        try:
            with open(mock_path, 'r') as f:
                data = json.load(f)
                if "type" not in data or data["type"] != "FeatureCollection":
                    return _create_default_aqi_geojson()
                if "features" not in data:
                    data["features"] = []
                for feature in data.get("features", []):
                    props = feature.get("properties", {})
                    if "aqi" not in props:
                        props["aqi"] = 75
                    if "pm25" not in props:
                        props["pm25"] = 25.0
                    if "pm10" not in props:
                        props["pm10"] = props.get("pm25", 25.0) * 1.4
                    if "category" not in props:
                        props["category"] = "Moderate"
                    if "station" not in props:
                        props["station"] = "Unknown Station"
                return data
        except Exception as e:
            logger.error(f"Error loading mock AQI data: {e}")
    
    return _create_default_aqi_geojson()

def _get_aqi_category(pm25: float) -> str:
    """Convert PM2.5 value to AQI category"""
    if pm25 <= 12:
        return "Good"
    elif pm25 <= 35.4:
        return "Moderate"
    elif pm25 <= 55.4:
        return "Unhealthy for Sensitive Groups"
    elif pm25 <= 150.4:
        return "Unhealthy"
    elif pm25 <= 250.4:
        return "Very Unhealthy"
    else:
        return "Hazardous"

def _convert_waqi_to_geojson(waqi_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert WAQI API response to GeoJSON"""
    features = []
    
    if "data" in waqi_data and "iaqi" in waqi_data["data"]:
        data = waqi_data["data"]
        iaqi = data.get("iaqi", {})
        
        pm25_val = iaqi.get("pm25", {}).get("v", 25.0)
        pm10_val = iaqi.get("pm10", {}).get("v", 35.0)
        aqi_val = data.get("aqi", int((pm25_val / 35.4) * 100))
        
        city = data.get("city", {})
        coords = city.get("geo", [1.29, 103.85])
        
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [coords[1], coords[0]]
            },
            "properties": {
                "pm25": round(pm25_val, 2),
                "pm10": round(pm10_val, 2),
                "aqi": int(aqi_val),
                "category": _get_aqi_category(pm25_val),
                "station": city.get("name", "Singapore")
            }
        })
    
    if not features:
        return _create_default_aqi_geojson()
    
    return {
        "type": "FeatureCollection",
        "features": features
    }

def fetch_live_aqi() -> Dict[str, Any]:
    """Fetch live AQI data from WAQI API"""
    token = os.getenv("WAQI_TOKEN", WAQI_TOKEN)
    
    try:
        params = {"token": token}
        response = requests.get(WAQI_URL, params=params, timeout=10)
        response.raise_for_status()
        
        waqi_data = response.json()
        
        if waqi_data.get("status") == "ok":
            geojson_data = _convert_waqi_to_geojson(waqi_data)
            if geojson_data.get("features"):
                return geojson_data
        
        # Try data.gov.sg as fallback
        try:
            response = requests.get(DATA_GOV_SG_POLLUTANT_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "items" in data and len(data["items"]) > 0:
                item = data["items"][0]
                readings = item.get("readings", [])
                if readings:
                    pm25 = readings[0].get("value", 25.0)
                    aqi = int((pm25 / 35.4) * 100)
                    
                    return {
                        "type": "FeatureCollection",
                        "features": [{
                            "type": "Feature",
                            "geometry": {
                                "type": "Point",
                                "coordinates": [103.85, 1.29]
                            },
                            "properties": {
                                "pm25": round(pm25, 2),
                                "pm10": round(pm25 * 1.4, 2),
                                "aqi": aqi,
                                "category": _get_aqi_category(pm25),
                                "station": "Singapore"
                            }
                        }]
                    }
        except Exception as e:
            logger.warning(f"data.gov.sg fallback failed: {e}")
        
        logger.warning("WAQI API returned no data, using mock")
        return _load_mock_data()
        
    except Exception as e:
        logger.error(f"Error fetching AQI data: {e}", exc_info=True)
        return _load_mock_data()
