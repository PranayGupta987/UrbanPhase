from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import requests
import tempfile
import os

from backend.gnn_pipeline.inference import predict_for_snapshot
from backend.gnn_pipeline.image_features import extract_features

router = APIRouter()

# ---------- SCHEMA ----------
class CameraMeta(BaseModel):
    CameraID: str
    Latitude: float
    Longitude: float
    ImageLink: str
    Timestamp: str

class SimulationRequest(BaseModel):
    vehicle_reduction: float
    cameras: List[CameraMeta]


# ---------- SIMULATION ROUTE ----------
@router.post("/simulate")
async def simulate(req: SimulationRequest):

    try:
        # --------------------------------------
        # 1) PROCESS IMAGES (baseline prediction)
        # --------------------------------------
        camera_dicts = []

        for cam in req.cameras:
            # Download image
            img_data = requests.get(cam.ImageLink).content

            # Save to temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            temp_file.write(img_data)
            temp_file.close()

            # Extract AI features
            vehicle_count, embedding = extract_features(temp_file.name)

            camera_dicts.append({
                "CameraID": cam.CameraID,
                "Latitude": cam.Latitude,
                "Longitude": cam.Longitude,
                "vehicle_count": vehicle_count,
                "embedding": embedding,
                "Timestamp": cam.Timestamp
            })

            os.remove(temp_file.name)

        # Compute baseline congestion via GNN
        baseline_congestion = predict_for_snapshot(camera_dicts)
        total_vehicles = sum(c["vehicle_count"] for c in camera_dicts)

        baseline = {
            "congestion": baseline_congestion,
            "total_vehicle_count": total_vehicles,
            "pm25": round(total_vehicles * 0.05, 2),
            "aqi": int(total_vehicles * 0.21),
            "aqi_category": "Good" if total_vehicles < 300 else "Moderate"
        }

        # --------------------------------------
        # 2) APPLY VEHICLE REDUCTION SIMULATION
        # --------------------------------------
        reduction_factor = (100 - req.vehicle_reduction) / 100.0
        new_vehicles = total_vehicles * reduction_factor

        simulated = {
            "reduce_vehicles_pct": req.vehicle_reduction,
            "congestion": round(baseline_congestion * reduction_factor, 4),
            "total_vehicle_count": round(new_vehicles, 2),
            "pm25": round(new_vehicles * 0.05, 2),
            "aqi": int(new_vehicles * 0.21),
            "aqi_category": "Good" if new_vehicles < 300 else "Moderate"
        }

        return {
            "baseline": baseline,
            "simulated": simulated
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
