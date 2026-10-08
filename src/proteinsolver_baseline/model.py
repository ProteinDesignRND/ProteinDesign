import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn.inits import reset

try:
    import torch_scatter

    def scatter_(name, src, index, out=None, dim=0, dim_size=None):
        """PyG-compatible scatter utility leveraging torch_scatter."""
        return torch_scatter.scatter(src, index, out=out, dim=dim, dim_size=dim_size, reduce=name)
except ImportError:
    from torch_geometric.utils import scatter

    def scatter_(name, src, index, out=None, dim=0, dim_size=None):
        """Pure-PyG fallback scatter utility when torch_scatter binary is absent."""
        return scatter(src, index, dim=dim, dim_size=dim_size, reduce=name)


class EdgeConvMod(nn.Module):
    """Residual Edge Convolution module from original ProteinSolver implementation."""

    def __init__(self, nn_module, aggr="max"):
        super().__init__()
        self.nn = nn_module
        self.aggr = aggr
        self.reset_parameters()

    def reset_parameters(self):
        reset(self.nn)

    def forward(self, x, edge_index, edge_attr=None):
        row, col = edge_index
        x = x.unsqueeze(-1) if x.dim() == 1 else x
        if edge_attr is None:
            out = torch.cat([x[row], x[col]], dim=-1)
        else:
            out = torch.cat([x[row], x[col], edge_attr], dim=-1)
        out = self.nn(out)
        x = scatter_(self.aggr, out, row, dim_size=x.size(0))
        return x, out


class EdgeConvBatch(nn.Module):
    """Post-processing normalization and dropout block wrapping EdgeConvMod."""

    def __init__(self, gnn, hidden_size, batch_norm=True, dropout=0.2):
        super().__init__()
        self.gnn = gnn

        x_post_modules = []
        edge_attr_post_modules = []

        if batch_norm is not None:
            x_post_modules.append(nn.LayerNorm(hidden_size))
            edge_attr_post_modules.append(nn.LayerNorm(hidden_size))

        if dropout:
            x_post_modules.append(nn.Dropout(dropout))
            edge_attr_post_modules.append(nn.Dropout(dropout))

        self.x_postprocess = nn.Sequential(*x_post_modules)
        self.edge_attr_postprocess = nn.Sequential(*edge_attr_post_modules)

    def forward(self, x, edge_index, edge_attr=None):
        x, edge_attr = self.gnn(x, edge_index, edge_attr)
        x = self.x_postprocess(x)
        edge_attr = self.edge_attr_postprocess(edge_attr)
        return x, edge_attr


def get_graph_conv_layer(input_size, hidden_size, output_size):
    mlp = nn.Sequential(
        nn.Linear(input_size, hidden_size),
        nn.ReLU(),
        nn.Linear(hidden_size, output_size),
    )
    gnn = EdgeConvMod(nn_module=mlp, aggr="add")
    graph_conv = EdgeConvBatch(gnn, output_size, batch_norm=True, dropout=0.2)
    return graph_conv


class ProteinSolverNet(nn.Module):
    """Original ProteinSolver 4-block Residual GNN matching published checkpoint."""

    def __init__(self, x_input_size=21, adj_input_size=2, hidden_size=128, output_size=20):
        super().__init__()
        self.embed_x = nn.Sequential(
            nn.Embedding(x_input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.LayerNorm(hidden_size),
        )
        self.embed_adj = nn.Sequential(
            nn.Linear(adj_input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.LayerNorm(hidden_size),
        )
        self.graph_conv_0 = get_graph_conv_layer(3 * hidden_size, 2 * hidden_size, hidden_size)
        self.graph_conv = nn.ModuleList([
            get_graph_conv_layer(3 * hidden_size, 2 * hidden_size, hidden_size)
            for _ in range(3)
        ])
        self.linear_out = nn.Linear(hidden_size, output_size)

    def forward(self, x, edge_index, edge_attr=None):
        x = self.embed_x(x)
        edge_attr = self.embed_adj(edge_attr) if edge_attr is not None else None

        x_out, edge_attr_out = self.graph_conv_0(x, edge_index, edge_attr)
        x = x + x_out
        edge_attr = (edge_attr + edge_attr_out) if edge_attr is not None else edge_attr_out

        for conv in self.graph_conv:
            x = F.relu(x)
            edge_attr = F.relu(edge_attr)
            x_out, edge_attr_out = conv(x, edge_index, edge_attr)
            x = x + x_out
            edge_attr = edge_attr + edge_attr_out

        x = self.linear_out(x)
        return x


def load_proteinsolver_checkpoint(checkpoint_path, device="cpu"):
    """Loads official ProteinSolver state dictionary and verifies 100% key match."""
    net = ProteinSolverNet(x_input_size=21, adj_input_size=2, hidden_size=128, output_size=20)
    state = torch.load(checkpoint_path, map_location=device)
    res = net.load_state_dict(state)
    assert len(res.missing_keys) == 0, f"Missing keys: {res.missing_keys}"
    assert len(res.unexpected_keys) == 0, f"Unexpected keys: {res.unexpected_keys}"
    net.to(device)
    net.eval()
    return net
