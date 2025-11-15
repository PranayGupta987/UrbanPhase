"""
Feature Engineering for UrbanPulse ML Models
Computes engineered features from raw input data
"""
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def compute_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute engineered features from raw input DataFrame
    
    Args:
        df: Input DataFrame with columns like avg_speed, vehicle_count, pm25, etc.
    
    Returns:
        DataFrame with additional engineered features
    """
    try:
        df = df.copy()
        
        # Ensure required columns exist with defaults
        if 'avg_speed' not in df.columns:
            df['avg_speed'] = 30.0
        if 'vehicle_count' not in df.columns:
            df['vehicle_count'] = 100
        if 'pm25' not in df.columns:
            df['pm25'] = 50.0
        if 'temperature' not in df.columns:
            df['temperature'] = 25.0
        if 'humidity' not in df.columns:
            df['humidity'] = 70.0
        if 'wind_speed' not in df.columns:
            df['wind_speed'] = 10.0
        if 'rainfall' not in df.columns:
            df['rainfall'] = 0.0
        
        # Fill NaN values
        df = df.fillna({
            'avg_speed': 30.0,
            'vehicle_count': 100,
            'pm25': 50.0,
            'temperature': 25.0,
            'humidity': 70.0,
            'wind_speed': 10.0,
            'rainfall': 0.0
        })
        
        # Traffic density: vehicles per unit speed
        df['traffic_density'] = df['vehicle_count'] / (df['avg_speed'] + 1.0)
        
        # PM2.5 dispersion factor (higher wind = lower concentration)
        df['pm25_dispersion'] = df['pm25'] / (df['wind_speed'] + 1.0)
        
        # Heat index approximation (simplified)
        df['heat_index'] = (
            0.5 * (df['temperature'] + 61.0 + ((df['temperature'] - 68.0) * 1.2) + (df['humidity'] * 0.094))
        )
        
        # Weather impact on speed (rain reduces effective speed)
        df['weather_speed_impact'] = df['avg_speed'] * (1.0 - df['rainfall'] * 0.01)
        
        # Normalize features to prevent extreme values
        df['traffic_density'] = df['traffic_density'].clip(0, 1000)
        df['pm25_dispersion'] = df['pm25_dispersion'].clip(0, 500)
        df['heat_index'] = df['heat_index'].clip(-50, 100)
        df['weather_speed_impact'] = df['weather_speed_impact'].clip(0, 200)
        
        return df
        
    except Exception as e:
        logger.error(f"Error computing features: {e}", exc_info=True)
        # Return original DataFrame if feature engineering fails
        return df.fillna(0)

