from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from pathlib import Path
import os
import requests
import logging

from backend.gnn_pipeline.inference import predict_for_snapshot
from backend.gnn_pipeline.image_features import extract_features

router = APIRouter()
logger = logging.getLogger(__name__)

TMP_DIR = Path("tmp")
TMP_DIR.mkdir(exist_ok=True)


# ----------- Request Models -----------
class CameraMeta(BaseModel):
    CameraID: str
    Latitude: float
    Longitude: float
    ImageLink: str
    Timestamp: str


class PredictRequest(BaseModel):
    cameras: List[CameraMeta]


# ---------- Prediction Endpoint ----------
@router.post("/cameras")
async def predict_cameras(req: PredictRequest):
    if not req.cameras:
        raise HTTPException(status_code=400, detail="No cameras provided")

    temp_files = []
    camera_dicts = []

    try:
        # Download + extract features
        for cam in req.cameras:
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                r = requests.get(cam.ImageLink, timeout=20, headers=headers)
                r.raise_for_status()
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to download {cam.CameraID}: {e}")

            filename = f"{cam.CameraID}_{cam.Timestamp.replace(':','-')}.jpg"
            fp = TMP_DIR / filename
            with open(fp, "wb") as f:
                f.write(r.content)
            temp_files.append(fp)

            vehicle_count, embedding = extract_features(str(fp))

            camera_dicts.append({
                "CameraID": cam.CameraID,
                "Latitude": cam.Latitude,
                "Longitude": cam.Longitude,
                "vehicle_count": vehicle_count,
                "embedding": embedding,
                "Timestamp": cam.Timestamp
            })

        # Run GNN
        congestion = predict_for_snapshot(camera_dicts)

        return {
            "congestion": float(congestion)
        }

    except Exception as e:
        logger.exception("Prediction failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        for tf in temp_files:
            try: os.remove(tf)
            except: pass
