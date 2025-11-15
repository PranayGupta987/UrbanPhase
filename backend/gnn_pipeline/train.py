# backend/gnn_pipeline/train.py
import os
import glob
import numpy as np
import torch
from torch_geometric.loader import DataLoader
from image_features import extract_features
from graph_builder import build_graph
from dataset import TrafficGraphDataset
from model import GraphSageNet
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("train")

DATA_DIR = os.getenv("DOWNLOAD_DIR", "./data/images")

def collect_camera_snapshots(pattern="*.jpg"):
    # we assume filenames like CameraID_timestamp.jpg
    files = glob.glob(os.path.join(DATA_DIR, "*.jpg"))
    cam_map = {}
    for f in files:
        base = os.path.basename(f)
        try:
            cam_id, ts = base.split("_", 1)
        except:
            continue
        cam_map.setdefault(cam_id, []).append((f, ts))
    return cam_map

def build_graphs_from_data(max_graphs=100):
    cam_snapshots = collect_camera_snapshots()
    # For simplicity, create graph per timestamp across cameras that have similar timestamps.
    # Here we just take latest snapshot per camera.
    cameras = []
    for cam_id, snaps in cam_snapshots.items():
        snaps_sorted = sorted(snaps, key=lambda x: x[1], reverse=True)
        path, ts = snaps_sorted[0]
        vc, emb = extract_features(path)
        # produce camera dict
        # NOTE: You should map/from LTA feed metadata to lat/lon; for demo we set zeros
        cameras.append({
            "CameraID": cam_id,
            "Latitude": 0.0,
            "Longitude": 0.0,
            "vehicle_count": vc,
            "embedding": emb,
            "Timestamp": ts
        })
    # If insufficient cameras, fail
    if len(cameras) < 2:
        raise RuntimeError("Not enough cameras for training graph")
    # Build one graph from all cameras
    x, edge_index = build_graph(cameras, k=4)
    # label: heuristic average vehicle_count normalized to 0-1
    avg_vc = np.mean([c["vehicle_count"] for c in cameras])
    y = torch.tensor([float(min(1.0, avg_vc / 200.0))], dtype=torch.float)  # example scaling
    return [(x, edge_index, y)]

def train_main(epochs=50):
    graphs = build_graphs_from_data()
    dataset = TrafficGraphDataset(graphs)
    loader = DataLoader(dataset, batch_size=1, shuffle=True)
    in_channels = dataset[0].x.shape[1]
    model = GraphSageNet(in_channels, hidden_channels=128)
    optim = torch.optim.Adam(model.parameters(), lr=1e-3)
    for epoch in range(1, epochs+1):
        model.train()
        total_loss = 0.0
        for data in loader:
            optim.zero_grad()
            out = model(data.x, data.edge_index, batch=batch_from_data(data))
            loss = torch.nn.functional.mse_loss(out, data.y)
            loss.backward()
            optim.step()
            total_loss += loss.item()
        logger.info("Epoch %d loss=%.6f", epoch, total_loss)
    torch.save(model.state_dict(), "gnn_model.pt")
    logger.info("Model saved to gnn_model.pt")

def batch_from_data(data):
    # data is a single Data, create batch vector of zeros
    return torch.zeros(data.x.size(0), dtype=torch.long)

if __name__ == "__main__":
    train_main(epochs=25)
