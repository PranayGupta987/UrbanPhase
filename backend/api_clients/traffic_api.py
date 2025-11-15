"""
LTA DataMall Traffic API Client for Singapore
Fetches live traffic data with fallback to mock data
"""
import os
import json
import requests
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# LTA DataMall API endpoints (corrected)
LTA_TRAFFIC_SPEED_URL = "http://datamall2.mytransport.sg/ltaodataservice/TrafficSpeedBandsv2"
LTA_TRAFFIC_INCIDENTS_URL = "http://datamall2.mytransport.sg/ltaodataservice/TrafficIncidents"

def _create_default_traffic_geojson() -> Dict[str, Any]:
    """Create default valid GeoJSON for Singapore"""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[103.85, 1.29], [103.851, 1.291], [103.852, 1.292]]
                },
                "properties": {
                    "segment_id": 1,
                    "speed": 45.0,
                    "avg_speed": 45.0,
                    "congestion": "moderate",
                    "congestion_level": 0.5,
                    "vehicle_count": 150,
                    "volume": 150
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[103.86, 1.30], [103.861, 1.301], [103.862, 1.302]]
                },
                "properties": {
                    "segment_id": 2,
                    "speed": 25.0,
                    "avg_speed": 25.0,
                    "congestion": "high",
                    "congestion_level": 0.8,
                    "vehicle_count": 200,
                    "volume": 200
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[103.84, 1.28], [103.841, 1.281], [103.842, 1.282]]
                },
                "properties": {
                    "segment_id": 3,
                    "speed": 60.0,
                    "avg_speed": 60.0,
                    "congestion": "low",
                    "congestion_level": 0.2,
                    "vehicle_count": 80,
                    "volume": 80
                }
            }
        ]
    }

def _load_mock_data() -> Dict[str, Any]:
    """Load mock traffic data - guaranteed valid GeoJSON"""
    mock_path = os.path.join(
        os.path.dirname(__file__), "..", "mock_data", "traffic.geojson"
    )
    
    if not os.path.exists(mock_path):
        mock_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "traffic.geojson"
        )
    
    if os.path.exists(mock_path):
        try:
            with open(mock_path, 'r') as f:
                data = json.load(f)
                if "type" not in data or data["type"] != "FeatureCollection":
                    return _create_default_traffic_geojson()
                if "features" not in data:
                    data["features"] = []
                for feature in data.get("features", []):
                    props = feature.get("properties", {})
                    if "congestion_level" not in props:
                        if "congestion" in props:
                            congestion = props["congestion"]
                            if isinstance(congestion, str):
                                congestion_map = {"low": 0.2, "moderate": 0.5, "high": 0.8}
                                props["congestion_level"] = congestion_map.get(congestion.lower(), 0.5)
                            else:
                                props["congestion_level"] = float(congestion)
                        else:
                            props["congestion_level"] = 0.5
                    if "avg_speed" not in props:
                        props["avg_speed"] = props.get("speed", 30.0)
                    if "vehicle_count" not in props:
                        props["vehicle_count"] = props.get("volume", 100)
                return data
        except Exception as e:
            logger.error(f"Error loading mock data: {e}")
    
    return _create_default_traffic_geojson()

def _convert_lta_to_geojson(lta_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert LTA DataMall response to GeoJSON"""
    features = []
    
    if "value" in lta_data:
        for idx, item in enumerate(lta_data["value"][:20]):
            link_id = item.get("LinkID", "")
            speed_band = item.get("SpeedBand", 0)
            
            speed = max(10, min(80, speed_band * 10 if speed_band > 0 else 30))
            
            if speed < 20:
                congestion = "high"
                congestion_level = 0.8
            elif speed < 40:
                congestion = "moderate"
                congestion_level = 0.5
            else:
                congestion = "low"
                congestion_level = 0.2
            
            vehicle_count = max(50, min(300, int(200 - (speed * 2))))
            
            base_lon = 103.85 + (hash(link_id) % 100) / 1000
            base_lat = 1.29 + (hash(link_id) % 50) / 1000
            
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [base_lon, base_lat],
                        [base_lon + 0.001, base_lat + 0.001],
                        [base_lon + 0.002, base_lat + 0.002]
                    ]
                },
                "properties": {
                    "segment_id": idx + 1,
                    "link_id": link_id,
                    "speed": float(speed),
                    "avg_speed": float(speed),
                    "congestion": congestion,
                    "congestion_level": float(congestion_level),
                    "vehicle_count": int(vehicle_count),
                    "volume": int(vehicle_count)
                }
            })
    
    if not features:
        return _create_default_traffic_geojson()
    
    return {
        "type": "FeatureCollection",
        "features": features
    }

def fetch_live_traffic() -> Dict[str, Any]:
    """Fetch live traffic data from LTA DataMall API"""
    api_key = os.getenv("LTA_API_KEY")
    
    if not api_key:
        logger.warning("LTA_API_KEY not found, using mock data")
        return _load_mock_data()
    
    try:
        headers = {
            "AccountKey": api_key,
            "accept": "application/json"
        }
        
        response = requests.get(
            LTA_TRAFFIC_SPEED_URL,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        
        lta_data = response.json()
        geojson_data = _convert_lta_to_geojson(lta_data)
        
        if not geojson_data.get("features"):
            logger.warning("No features in LTA response, using mock data")
            return _load_mock_data()
        
        return geojson_data
        
    except Exception as e:
        logger.error(f"Error fetching LTA traffic data: {e}", exc_info=True)
        return _load_mock_data()
