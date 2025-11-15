# backend/gnn_pipeline/inference.py
import os
import torch
from .model import GraphSageNet
from .image_features import extract_features
from .graph_builder import build_graph
import joblib
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent  # this gets backend/
MODEL_PATH = os.getenv("GNN_MODEL_PATH", str(ROOT / "gnn_model.pt"))


def load_model(in_channels):
    model = GraphSageNet(in_channels, hidden_channels=128)
    model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    model.eval()
    return model

def predict_for_snapshot(camera_dicts):
    # camera_dicts: list of camera dicts (same structure used in graph_builder)
    x, edge_index = build_graph(camera_dicts, k=4)
    in_ch = x.shape[1]
    model = load_model(in_ch)
    with torch.no_grad():
        out = model(x, edge_index)
    # out is graph-level scalar or vector: if multiple graphs? here single graph -> scalar
    if hasattr(out, "item"):
        return float(out.item())
    return float(out[0])
