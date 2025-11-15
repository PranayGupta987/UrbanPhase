# backend/gnn_pipeline/download_images.py
import os
import time
import requests
from urllib.parse import urljoin
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import logging

load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")

LTA_KEY = os.getenv("LTA_ACCOUNT_KEY")
CAMERA_FEED_URL = os.getenv("CAMERA_LIST_URL") or "https://datamall2.mytransport.sg/ltaodataservice/Traffic-Imagesv2"
DOWNLOAD_DIR = Path(os.getenv("DOWNLOAD_DIR", "./data/images"))
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"AccountKey": LTA_KEY, "accept": "application/json"}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("downloader")

def fetch_camera_list():
    resp = requests.get(CAMERA_FEED_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.json().get("value") or resp.json()

def download_image(camera):
    img_url = camera.get("ImageLink") or camera.get("image")
    cam_id = camera.get("CameraID") or camera.get("camera_id") or camera.get("cameraId")
    timestamp = camera.get("Timestamp") or camera.get("timestamp") or datetime.utcnow().isoformat()
    if not img_url:
        logger.warning("no image link for camera %s", cam_id)
        return None
    # filename: camera_timestamp.jpg
    safe_ts = timestamp.replace(":", "-").replace(" ", "_")
    fn = DOWNLOAD_DIR / f"{cam_id}_{safe_ts}.jpg"
    try:
        r = requests.get(img_url, stream=True, timeout=20)
        r.raise_for_status()
        with open(fn, "wb") as f:
            for chunk in r.iter_content(1024*64):
                f.write(chunk)
        logger.info("Downloaded %s -> %s", cam_id, fn)
        return str(fn)
    except Exception as e:
        logger.exception("download failed for %s: %s", img_url, e)
        return None

def run_once(save_meta=True):
    cameras = fetch_camera_list()
    saved = []
    for cam in cameras:
        filepath = download_image(cam)
        if filepath:
            saved.append({"camera": cam, "path": filepath})
    return saved

if __name__ == "__main__":
    # simple scheduler: fetch every minute
    interval = 60
    while True:
        try:
            run_once()
        except Exception as e:
            logger.exception("error in downloader loop: %s", e)
        time.sleep(interval)
