"""
Model Loader for UrbanPulse ML Predictions
Loads and caches the trained LightGBM model for fast inference
Works with or without trained model (fallback to heuristic)
"""
import os
import json
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Import feature engineering
try:
    from ml.features import compute_feature_matrix
except ImportError:
    logger.warning("Could not import ml.features, using fallback")
    def compute_feature_matrix(df):
        return df

# Paths
BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
CONFIG_FILE = BASE_DIR / "model_config.json"

MODEL_FILE = MODELS_DIR / "model.pkl"

# Global model cache
_cached_model: Optional[Any] = None
_model_config: Optional[Dict[str, Any]] = None
_model_available = False


def get_model():
    """
    Get the cached model, loading it if necessary
    
    Returns:
        Trained LightGBM model or None if not available
    """
    global _cached_model, _model_available
    
    if _cached_model is not None:
        return _cached_model
    
    if not MODEL_FILE.exists():
        logger.warning(f"Model file not found: {MODEL_FILE}. Using heuristic fallback.")
        _model_available = False
        return None
    
    try:
        logger.info(f"Loading model from {MODEL_FILE}...")
        _cached_model = joblib.load(MODEL_FILE)
        _model_available = True
        logger.info("  ✓ Model loaded and cached")
        return _cached_model
    except Exception as e:
        logger.error(f"Error loading model: {e}", exc_info=True)
        _model_available = False
        return None


def get_config() -> Dict[str, Any]:
    """Load model configuration"""
    global _model_config
    
    if _model_config is not None:
        return _model_config
    
    if not CONFIG_FILE.exists():
        logger.warning(f"Config file not found: {CONFIG_FILE}, using defaults")
        return {
            "target_variable": "congestion_level",
            "feature_columns": ["avg_speed", "vehicle_count", "pm25", "temperature", "humidity", "wind_speed", "rainfall"]
        }
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            _model_config = json.load(f)
        return _model_config
    except Exception as e:
        logger.error(f"Error loading config: {e}", exc_info=True)
        return {
            "target_variable": "congestion_level",
            "feature_columns": ["avg_speed", "vehicle_count", "pm25", "temperature", "humidity", "wind_speed", "rainfall"]
        }


def _heuristic_prediction(input_dict: Dict[str, Any]) -> float:
    """Fallback heuristic prediction when model is not available"""
    avg_speed = input_dict.get("avg_speed", 30.0)
    vehicle_count = input_dict.get("vehicle_count", 100)
    
    # Simple heuristic: congestion increases with vehicle count and decreases with speed
    base_congestion = 1.0 - (avg_speed / 80.0)
    vehicle_factor = min(1.0, vehicle_count / 200.0)
    
    congestion = (base_congestion * 0.6 + vehicle_factor * 0.4)
    return max(0.0, min(1.0, congestion))


def preprocess_input(input_dict: Dict[str, Any]) -> pd.DataFrame:
    """Preprocess input dictionary to DataFrame with required features"""
    try:
        df = pd.DataFrame([input_dict])
        
        if 'timestamp' in df.columns:
            if isinstance(df['timestamp'].iloc[0], str):
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour_of_day'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['day_of_month'] = df['timestamp'].dt.day
        else:
            now = datetime.now()
            df['hour_of_day'] = now.hour
            df['day_of_week'] = now.weekday()
            df['day_of_month'] = now.day
        
        df = compute_feature_matrix(df)
        return df
    except Exception as e:
        logger.error(f"Error preprocessing input: {e}", exc_info=True)
        return pd.DataFrame([input_dict])


def predict_from_dict(input_dict: Dict[str, Any]) -> float:
    """
    Predict congestion_level from input dictionary
    Works with or without trained model
    """
    model = get_model()
    
    if model is None:
        logger.debug("Using heuristic prediction (model not available)")
        return _heuristic_prediction(input_dict)
    
    try:
        config = get_config()
        df = preprocess_input(input_dict)
        
        base_features = config.get('feature_columns', [])
        timestamp_features = ['hour_of_day', 'day_of_week', 'day_of_month']
        
        all_features = []
        for feat in base_features + timestamp_features:
            if feat in df.columns:
                all_features.append(feat)
        
        engineered_features = ['traffic_density', 'pm25_dispersion', 'heat_index', 'weather_speed_impact']
        for feat in engineered_features:
            if feat in df.columns and feat not in all_features:
                all_features.append(feat)
        
        required_base = ['avg_speed', 'vehicle_count', 'pm25', 'temperature', 'humidity', 'wind_speed', 'rainfall']
        missing = [f for f in required_base if f not in df.columns]
        if missing:
            logger.warning(f"Missing features: {missing}, using defaults")
            for f in missing:
                df[f] = 0.0
        
        X = df[all_features] if all_features else df[required_base]
        X = X.fillna(0)
        
        if hasattr(model, 'predict'):
            if hasattr(model, 'best_iteration'):
                prediction = model.predict(X, num_iteration=model.best_iteration)[0]
            else:
                prediction = model.predict(X)[0]
        else:
            prediction = _heuristic_prediction(input_dict)
        
        return max(0.0, min(1.0, float(prediction)))
        
    except Exception as e:
        logger.error(f"Error in ML prediction: {e}, using heuristic", exc_info=True)
        return _heuristic_prediction(input_dict)
