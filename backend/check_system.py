import os
import sys
import logging
from typing import Any, Dict

import requests
from dotenv import load_dotenv


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("check_system")


def print_python_info() -> None:
    logger.info("Python executable: %s", sys.executable)
    logger.info("Python version: %s", sys.version.replace("\n", " "))


def print_env_info() -> None:
    waqi_token = os.getenv("WAQI_TOKEN")
    lta_key = os.getenv("LTA_ACCOUNT_KEY")

    logger.info("WAQI_TOKEN present: %s", bool(waqi_token))
    logger.info("LTA_ACCOUNT_KEY present: %s", bool(lta_key))


def check_waqi() -> None:
    token = os.getenv("WAQI_TOKEN")
    if not token:
        logger.warning("WAQI_TOKEN is not set; skipping WAQI connectivity check")
        return

    url = "https://api.waqi.info/feed/here/"
    try:
        logger.info("Checking WAQI connectivity: %s", url)
        resp = requests.get(url, params={"token": token}, timeout=10)
        logger.info("WAQI HTTP %s", resp.status_code)
        data: Dict[str, Any] = {}
        try:
            data = resp.json()
        except Exception:
            logger.warning("WAQI response is not JSON")
        logger.info("WAQI status field: %s", data.get("status"))
    except Exception as exc:
        logger.error("WAQI check failed: %s", exc, exc_info=True)


def check_lta() -> None:
    api_key = os.getenv("LTA_ACCOUNT_KEY")
    if not api_key:
        logger.warning("LTA_ACCOUNT_KEY is not set; skipping LTA connectivity check")
        return

    url = "https://datamall2.mytransport.sg/ltaodataservice/v4/TrafficSpeedBands"
    headers = {"AccountKey": api_key, "accept": "application/json"}
    try:
        logger.info("Checking LTA connectivity: %s", url)
        resp = requests.get(url, headers=headers, timeout=10)
        logger.info("LTA HTTP %s", resp.status_code)
        text = resp.text[:500].replace("\n", " ")
        logger.info("LTA response preview: %s", text)
    except Exception as exc:
        logger.error("LTA check failed: %s", exc, exc_info=True)


if __name__ == "__main__":
    # Ensure .env is loaded the same way as in main.py
    load_dotenv()

    print_python_info()
    print_env_info()
    check_waqi()
    check_lta()
