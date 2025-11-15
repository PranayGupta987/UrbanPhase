# backend/gnn_pipeline/image_features.py
import os
from PIL import Image
import numpy as np
import torch
from torchvision import transforms, models
import logging

logger = logging.getLogger("image_features")
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except Exception:
    YOLO_AVAILABLE = False

# Preprocess
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
])

# Feature extractor: MobileNet backbone returning embedding
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
_mobilenet = models.mobilenet_v2(pretrained=True).to(device)
_mobilenet.eval()

# Regression head optional (simple linear) for vehicle count estimate
_reg_head = torch.nn.Sequential(
    torch.nn.AdaptiveAvgPool2d(1),
    torch.nn.Flatten(),
    torch.nn.Linear(1280, 256),
    torch.nn.ReLU(),
    torch.nn.Linear(256, 1)
).to(device)
# NOTE: reg head needs training if you use fallback; we will use heuristics initially.

if YOLO_AVAILABLE:
    logger.info("YOLO available, loading tiny model")
    # use yolov8n or yolov8s (lean)
    yolo = YOLO("yolov8n.pt")  # local model will be auto-downloaded if needed

def extract_with_yolo(image_path):
    # returns vehicle_count, embedding (avg pooled from mobilenet)
    try:
        res = yolo.predict(source=image_path, imgsz=640, conf=0.25, classes=None, max_det=200)
        # classes for vehicle-like: car(2), motorcycle(3), bus(5), truck(7) depending on COCO indexing
        preds = res[0]
        boxes = preds.boxes
        # filter by class indices: 2 car, 3 motorbike, 5 bus, 7 truck (COCO) - but confirm YOLO variant
        cls = boxes.cls.cpu().numpy().astype(int) if hasattr(boxes, "cls") else np.array([])
        vehicle_mask = np.isin(cls, [2,3,5,7])
        vehicle_count = int(vehicle_mask.sum())
    except Exception as e:
        logger.exception("YOLO failed: %s", e)
        vehicle_count = 0
    # embedding:
    img = Image.open(image_path).convert("RGB")
    x = transform(img).unsqueeze(0).to(device)
    with torch.no_grad():
        features = _mobilenet.features(x)
        pooled = torch.nn.functional.adaptive_avg_pool2d(features, 1).flatten(1).cpu().numpy()[0]
    return vehicle_count, pooled

def fallback_extract(image_path):
    # simple feature + heuristic vehicle count: count bright blobs on road area - quick heuristic
    img = Image.open(image_path).convert("RGB").resize((224,224))
    arr = np.array(img).astype(np.float32) / 255.0
    gray = arr.mean(axis=2)
    # threshold bright spots (cars headlights) - not robust but fallback
    bright = (gray > 0.7).astype(np.uint8)
    vehicle_count = int(np.clip(bright.sum() / 30, 0, 200))
    # embedding via mobilenet backbone
    x = transform(img).unsqueeze(0).to(device)
    with torch.no_grad():
        features = _mobilenet.features(x)
        pooled = torch.nn.functional.adaptive_avg_pool2d(features, 1).flatten(1).cpu().numpy()[0]
    return vehicle_count, pooled

def extract_features(image_path):
    if YOLO_AVAILABLE:
        return extract_with_yolo(image_path)
    else:
        return fallback_extract(image_path)
