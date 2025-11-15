# backend/gnn_pipeline/model.py
import torch
import torch.nn.functional as F
from torch_geometric.nn import SAGEConv, global_mean_pool
import os

class GraphSageNet(torch.nn.Module):
    def __init__(self, in_channels, hidden_channels=128, num_layers=2, out_dim=1):
        super().__init__()
        self.convs = torch.nn.ModuleList()
        self.convs.append(SAGEConv(in_channels, hidden_channels))
        for _ in range(num_layers-1):
            self.convs.append(SAGEConv(hidden_channels, hidden_channels))
        self.pool = global_mean_pool
        self.fc = torch.nn.Sequential(
            torch.nn.Linear(hidden_channels, hidden_channels//2),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_channels//2, out_dim)
        )
    def forward(self, x, edge_index, batch=None):
        # x: node features
        for conv in self.convs:
            x = conv(x, edge_index)
            x = F.relu(x)
        if batch is None:
            # single graph -> batch zeros
            batch = torch.zeros(x.size(0), dtype=torch.long, device=x.device)
        g = self.pool(x, batch)
        out = self.fc(g)
        return torch.sigmoid(out).squeeze(-1)

# ------------------------------
# Model Loading Helper Function
# ------------------------------


def load_gnn_model(
    model_path="gnn_pipeline/model_weights.pth",
    in_channels=128,
    hidden_channels=128,
    num_layers=2
):
    """
    Loads a trained GraphSageNet model safely.
    Returns a ready-to-use PyTorch model.
    """

    model = GraphSageNet(
        in_channels=in_channels,
        hidden_channels=hidden_channels,
        num_layers=num_layers,
        out_dim=1,
    )

    if not os.path.exists(model_path):
        print(f"[WARN] GNN model not found at {model_path}. Using randomly initialized model.")
        return model

    try:
        state = torch.load(model_path, map_location="cpu")
        model.load_state_dict(state)
        print(f"[INFO] Loaded GNN model from: {model_path}")
    except Exception as e:
        print(f"[ERROR] Failed loading GNN model: {e}")
        print("[WARN] Proceeding with randomly initialized model instead.")

    return model
