"""
Status Router for UrbanPulse API
Provides health check and API status endpoints
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def get_status():
    """Get API status and health information"""
    model = get_model()
    return {
        "status": "healthy",
        "version": "1.0.0",
        "ml_model_loaded": model is not None,
        "message": "UrbanPulse API is running"
    }

