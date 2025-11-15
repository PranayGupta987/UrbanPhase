# backend/gnn_pipeline/dataset.py
import torch
from .torch_geometric.data import Data, InMemoryDataset

class TrafficGraphDataset(InMemoryDataset):
    def __init__(self, graphs_list, transform=None):
        # graphs_list: list of tuples (x, edge_index, y) where y is congestion label for nodes or graph-level
        super().__init__(None, transform)
        self.data_list = []
        for x, edge_index, y in graphs_list:
            data = Data(x=x, edge_index=edge_index, y=y)
            self.data_list.append(data)
        self.data, self.slices = self.collate(self.data_list)
    def __len__(self):
        return len(self.data_list)
    def get(self, idx):
        return self.data_list[idx]
