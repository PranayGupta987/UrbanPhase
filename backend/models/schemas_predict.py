"""
Pydantic Schemas for Prediction and Simulation Endpoints
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional


class PredictRequest(BaseModel):
    """Request schema for congestion prediction"""
    avg_speed: float = Field(..., ge=0, le=200, description="Average speed in km/h")
    vehicle_count: int = Field(..., ge=0, description="Number of vehicles")
    pm25: float = Field(..., ge=0, description="PM2.5 concentration in µg/m³")
    temperature: float = Field(..., ge=-50, le=50, description="Temperature in Celsius")
    humidity: float = Field(..., ge=0, le=100, description="Humidity percentage")
    wind_speed: float = Field(..., ge=0, le=100, description="Wind speed in km/h")
    rainfall: float = Field(..., ge=0, le=100, description="Rainfall in mm")
    segment_id: Optional[int] = Field(None, description="Road segment ID (optional)")
    timestamp: Optional[str] = Field(None, description="Timestamp (optional)")


class PredictResponse(BaseModel):
    """Response schema for congestion prediction"""
    prediction: float = Field(..., ge=0, le=1, description="Predicted congestion level (0-1)")
    error: Optional[str] = Field(None, description="Error message if prediction failed")


class SimulationRequest(BaseModel):
    """Request schema for traffic simulation"""
    vehicle_reduction: float = Field(
        ...,
        ge=0,
        le=100,
        description="Vehicle reduction percentage (0 to 100, e.g., 20 = 20% reduction)"
    )
    segment_ids: Optional[List[int]] = Field(
        None,
        description="List of segment IDs to apply simulation to. If None, applies to all segments."
    )


class Metrics(BaseModel):
    """Metrics for simulation results"""
    avg_congestion_before: float
    avg_congestion_after: float
    avg_speed_before: float
    avg_speed_after: float
    aqi_before: float
    aqi_after: float


class SimulationResponse(BaseModel):
    """Response schema for traffic simulation"""
    before: Dict[str, Any] = Field(..., description="GeoJSON FeatureCollection before simulation")
    after: Dict[str, Any] = Field(..., description="GeoJSON FeatureCollection after simulation")
    metrics: Metrics = Field(..., description="Simulation metrics")
    error: Optional[str] = Field(None, description="Error message if simulation failed")

