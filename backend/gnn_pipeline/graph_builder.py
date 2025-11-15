# backend/gnn_pipeline/graph_builder.py
import math
import numpy as np
from sklearn.neighbors import NearestNeighbors
from typing import List, Dict, Any
import torch

def haversine(lat1, lon1, lat2, lon2):
    # returns meters
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2*R*math.asin(math.sqrt(a))

def build_graph(cameras: List[Dict[str,Any]], k=4):
    # cameras: list of dict each with keys 'camera_id','lat','lon','vehicle_count','embedding'(ndarray), 'timestamp'
    coords = np.array([[c["Latitude"], c["Longitude"]] for c in cameras])
    # use nearest neighbors by haversine -> convert degrees to radians approx; here using Euclidean on lat/lon is fine for small areas
    nbrs = NearestNeighbors(n_neighbors=min(k+1, len(cameras))).fit(coords)
    distances, indices = nbrs.kneighbors(coords)
    edge_index = []
    for i, inds in enumerate(indices):
        for j in inds[1:]:  # skip self
            edge_index.append([i, j])
    # Build node features
    node_features = []
    for c in cameras:
        vc = float(c.get("vehicle_count", 0))
        ts = c.get("Timestamp")
        # hour features
        try:
            from dateutil import parser
            dt = parser.parse(ts)
            h = dt.hour
        except Exception:
            h = 0
        hour_sin = math.sin(2*math.pi*h/24)
        hour_cos = math.cos(2*math.pi*h/24)
        lat = float(c["Latitude"])
        lon = float(c["Longitude"])
        embedding = c.get("embedding")
        if embedding is None:
            embedding = np.zeros(1280, dtype=np.float32)
        # numeric features vector
        base = np.array([vc, hour_sin, hour_cos, lat, lon], dtype=np.float32)
        feat = np.concatenate([base, embedding.astype(np.float32)])
        node_features.append(feat)
    x = torch.tensor(np.vstack(node_features), dtype=torch.float)
    # edges to edge_index tensor
    edge_index = torch.tensor(np.array(edge_index).T, dtype=torch.long) if edge_index else torch.empty((2,0), dtype=torch.long)
    return x, edge_index
