from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv
import logging
import os
import requests

# Use your gnn pipeline (absolute imports)
from backend.gnn_pipeline.inference import predict_for_snapshot
from backend.gnn_pipeline.image_features import extract_features

load_dotenv()
logger = logging.getLogger(__name__)
router = APIRouter()

TMP_DIR = Path("tmp")
TMP_DIR.mkdir(exist_ok=True)

# ---------- Request models ----------
class CameraMeta(BaseModel):
    CameraID: str
    Latitude: float
    Longitude: float
    ImageLink: str
    Timestamp: str

class SimulateRequest(BaseModel):
    cameras: List[CameraMeta]
    reduce_vehicles_pct: Optional[float] = 0.0  # percentage [0-100], default 0 (no reduction)


# ---------- Helper: PM2.5 <-> AQI (approximate, US EPA) ----------
# Returns integer AQI for a given pm2_5 concentration (µg/m3)
def pm25_to_aqi(pm25: float) -> int:
    # EPA breakpoints: (From-low, To-high, AQI-low, AQI-high)
    breakpoints = [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 350.4, 301, 400),
        (350.5, 500.4, 401, 500),
    ]
    for (clow, chigh, ilow, ihigh) in breakpoints:
        if clow <= pm25 <= chigh:
            aqi = ((ihigh - ilow) / (chigh - clow)) * (pm25 - clow) + ilow
            return int(round(aqi))
    # If beyond table, cap at 500
    return 500

def pm25_category(aqi: int) -> str:
    if aqi <= 50: return "Good"
    if aqi <= 100: return "Moderate"
    if aqi <= 150: return "Unhealthy for Sensitive Groups"
    if aqi <= 200: return "Unhealthy"
    if aqi <= 300: return "Very Unhealthy"
    return "Hazardous"


# ---------- Simple emission model ----------
# This is a placeholder linear model:
#   total_pm25 = EMISSION_FACTOR * total_vehicle_count
# Choose a default emission factor (µg/m3 per vehicle). You can tune this later.
EMISSION_FACTOR = float(os.getenv("EMISSION_FACTOR", "0.05"))  # µg/m3 per vehicle (example)


# ---------- Core endpoint: predict + simulate ----------
@router.post("/simulate", summary="Predict congestion and simulate AQI change when vehicles reduced")
async def predict_and_simulate(req: SimulateRequest):
    """
    Accepts a list of cameras (with ImageLink). Downloads images,
    extracts features (vehicle_count, embedding), runs GNN for baseline congestion,
    then simulates reducing vehicle counts by reduce_vehicles_pct and re-runs the GNN.
    Returns baseline & simulated congestion, PM2.5, AQI and categories.
    """
    if not req.cameras:
        raise HTTPException(status_code=400, detail="No cameras provided")

    temp_files = []
    camera_dicts = []

    try:
        # 1) Download images and extract features
        for cam in req.cameras:
            try:
                response = requests.get(cam.ImageLink, timeout=15)
                response.raise_for_status()
            except Exception as e:
                logger.error("Failed to download image for %s: %s", cam.CameraID, e)
                raise HTTPException(status_code=400, detail=f"Failed to download image for {cam.CameraID}: {e}")

            filename = f"{cam.CameraID}_{cam.Timestamp.replace(':','-')}.jpg"
            file_path = TMP_DIR / filename
            with open(file_path, "wb") as f:
                f.write(response.content)
            temp_files.append(file_path)

            # Use your image_features.extract_features(image_path) -> (vehicle_count, embedding)
            vehicle_count, embedding = extract_features(str(file_path))

            camera_dicts.append({
                "CameraID": cam.CameraID,
                "Latitude": cam.Latitude,
                "Longitude": cam.Longitude,
                "vehicle_count": vehicle_count,
                "embedding": embedding,
                "Timestamp": cam.Timestamp
            })

        # 2) Baseline congestion (GNN)
        baseline_congestion = predict_for_snapshot(camera_dicts)

        # 3) Baseline PM2.5 estimate from raw vehicle counts
        total_vehicles = sum([c["vehicle_count"] for c in camera_dicts])
        baseline_pm25 = EMISSION_FACTOR * total_vehicles
        baseline_aqi = pm25_to_aqi(baseline_pm25)
        baseline_aqi_category = pm25_category(baseline_aqi)

        # 4) Simulate reduction
        pct = float(req.reduce_vehicles_pct or 0.0)
        if pct < 0 or pct > 100:
            raise HTTPException(status_code=400, detail="reduce_vehicles_pct must be between 0 and 100")

        if pct == 0.0:
            # no change: return baseline only
            simulated_congestion = baseline_congestion
            simulated_pm25 = baseline_pm25
            simulated_aqi = baseline_aqi
            simulated_aqi_category = baseline_aqi_category
        else:
            # Create modified camera dicts with scaled vehicle_count.
            # We keep embeddings the same (approximation) and scale vehicle_count.
            scale = max(0.0, 1.0 - pct / 100.0)
            sim_camera_dicts = []
            for c in camera_dicts:
                sim_camera_dicts.append({
                    "CameraID": c["CameraID"],
                    "Latitude": c["Latitude"],
                    "Longitude": c["Longitude"],
                    # scale the vehicle counts:
                    "vehicle_count": c["vehicle_count"] * scale,
                    "embedding": c["embedding"],
                    "Timestamp": c["Timestamp"]
                })

            # Simulated congestion via GNN (approximation: embeddings unchanged)
            simulated_congestion = predict_for_snapshot(sim_camera_dicts)

            # Simulated PM2.5 & AQI
            simulated_total_vehicles = sum([c["vehicle_count"] for c in sim_camera_dicts])
            simulated_pm25 = EMISSION_FACTOR * simulated_total_vehicles
            simulated_aqi = pm25_to_aqi(simulated_pm25)
            simulated_aqi_category = pm25_category(simulated_aqi)

        # 5) Build response
        response = {
            "baseline": {
                "congestion": float(baseline_congestion),
                "total_vehicle_count": float(total_vehicles),
                "pm25_estimate": float(baseline_pm25),
                "aqi": int(baseline_aqi),
                "aqi_category": baseline_aqi_category
            },
            "simulated": {
                "reduce_vehicles_pct": float(pct),
                "congestion": float(simulated_congestion),
                "total_vehicle_count": float(simulated_total_vehicles if pct>0 else total_vehicles),
                "pm25_estimate": float(simulated_pm25),
                "aqi": int(simulated_aqi),
                "aqi_category": simulated_aqi_category
            }
        }

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Simulation failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # cleanup
        for tmp in temp_files:
            try:
                os.remove(tmp)
            except Exception:
                pass


from fastapi import APIRouter

router = APIRouter()

@router.get("/traffic")
async def get_traffic():
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [103.84, 1.29],
                        [103.85, 1.30],
                        [103.86, 1.31]
                    ]
                }
            }
        ]
    }

