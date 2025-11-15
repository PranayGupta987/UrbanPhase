# backend/routers/gnn_predict.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from pathlib import Path
from dotenv import load_dotenv
import requests
import logging
import os

# Load .env
load_dotenv()

# Correct imports (NO relative imports)
from backend.gnn_pipeline.inference import predict_for_snapshot
from backend.gnn_pipeline.image_features import extract_features



logger = logging.getLogger("gnn_router")
router = APIRouter()


# ---------------------------
# Request Models
# ---------------------------
class CameraMeta(BaseModel):
    CameraID: str
    Latitude: float
    Longitude: float
    ImageLink: str
    Timestamp: str


class PredictRequest(BaseModel):
    cameras: List[CameraMeta]


# ---------------------------
# Main Prediction Route
# ---------------------------
@router.post("/predict/cameras")
async def predict_cameras(req: PredictRequest):

    temp_files = []
    camera_dicts = []

    try:
        tmp_dir = Path("tmp")
        tmp_dir.mkdir(exist_ok=True)

        for cam in req.cameras:

            # Download image
            response = requests.get(cam.ImageLink, timeout=15)
            response.raise_for_status()

            filename = f"{cam.CameraID}_{cam.Timestamp.replace(':','-')}.jpg"
            file_path = tmp_dir / filename

            with open(file_path, "wb") as f:
                f.write(response.content)

            # Extract image features
            vehicle_count, embedding = extract_features(str(file_path))

            camera_dicts.append({
                "CameraID": cam.CameraID,
                "Latitude": cam.Latitude,
                "Longitude": cam.Longitude,
                "vehicle_count": vehicle_count,
                "embedding": embedding,
                "Timestamp": cam.Timestamp
            })

            temp_files.append(file_path)

        # Run congestion prediction
        congestion_score = predict_for_snapshot(camera_dicts)

        return {"congestion": float(congestion_score)}

    except Exception as e:
        logger.exception("Prediction failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Clean up temporary files
        for tmp in temp_files:
            try:
                os.remove(tmp)
            except:
                pass
