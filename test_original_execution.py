"""Verification of Original ProteinSolver Implementation.

This script executes the complete Phase 1 / E0 verification suite:
1. Historical source executed unchanged (direct import behavior).
2. Historical source executed with minimal runtime compatibility shim.
3. Official checkpoint loading into original ProteinNet (Milestone E0).
4. Real PDB (1n5uA03) inverse-folding using original repository pipeline
   and CSP design algorithm from all-masked input.
5. Strict separation between valid all-masked sequence recovery and
   native sequence diagnostic scoring / likelihood evaluation.
"""

import sys
import time
import types
from pathlib import Path
import numpy as np
import torch
from Bio.PDB import PDBParser
from Bio.PDB.Polypeptide import is_aa
from Bio.SeqUtils import seq1
from scipy.spatial.distance import cdist

repo_root = Path.cwd().resolve()
orig_repo = repo_root / "external" / "proteinsolver-original"
sys.path.insert(0, str(orig_repo))

print("=" * 75)
print("PHASE 1: RIGOROUS VERIFICATION OF ORIGINAL PROTEINSOLVER REPOSITORY")
print("=" * 75)

# =========================================================================
# STEP 1: HISTORICAL SOURCE EXECUTED UNCHANGED
# =========================================================================
print("\n" + "=" * 75)
print("STEP 1: HISTORICAL SOURCE EXECUTED UNCHANGED")
print("=" * 75)

print("\n[Test 1.1] Direct import of 'proteinsolver' package (unchanged)...")
try:
    import proteinsolver
    print("RESULT: SUCCESS - historical source executed unchanged.")
except Exception as e:
    print(f"RESULT: FAILED as expected.")
    print(f"  Exception Type : {type(e).__name__}")
    print(f"  Exception Msg  : {e}")
    print("  Root Cause     : proteinsolver/__init__.py performs 'from . import *',")
    print("                   which loads utils.protein_structure, importing kmtools.")
    print("                   kmtools requires 'kmbio' (last built for Python 3.5/3.6,")
    print("                   no Python 3.11 wheels) and 'fcntl' (POSIX-only, not on Windows).")

print("\n[Test 1.2] Direct import of 'proteinsolver.models.proteinnet' (unchanged)...")
try:
    from proteinsolver.models.proteinnet import ProteinNet
    print("RESULT: SUCCESS - ProteinNet imported unchanged.")
except Exception as e:
    print(f"RESULT: FAILED as expected.")
    print(f"  Exception Type : {type(e).__name__}")
    print(f"  Exception Msg  : {e}")
    print("  Root Cause     : Importing submodule executes parent package __init__.py,")
    print("                   triggering the same missing legacy C-extension dependencies.")

# Clean up partially initialized modules from sys.modules
for mod in list(sys.modules.keys()):
    if mod == "proteinsolver" or mod.startswith("proteinsolver."):
        del sys.modules[mod]

# =========================================================================
# STEP 2: HISTORICAL SOURCE WITH RUNTIME COMPATIBILITY SHIM
# =========================================================================
print("\n" + "=" * 75)
print("STEP 2: HISTORICAL SOURCE WITH RUNTIME COMPATIBILITY SHIM")
print("=" * 75)
print("Status: historical source executed with compatibility shim.")
print("Documented Shims Applied Outside Repository:")
print("  1. torch_geometric.utils.scatter_: Author's backward-compatibility")
print("     fallback from proteinsolver/utils/scatter.py via torch_scatter.scatter.")
print("  2. fcntl: Dummy module shim for Windows (POSIX file-locking unsupported).")
print("  3. kmtools: Stub module to isolate neural network / design pipelines from")
print("     unsupported 2017 monolithic C-extension utilities (kmbio).")

import torch_geometric
import torch_scatter

def scatter_(name, src, index, out=None, dim=0, dim_size=None):
    return torch_scatter.scatter(src, index, out=None, dim=dim, dim_size=dim_size, reduce=name)

torch_geometric.utils.scatter_ = scatter_

sys.modules.setdefault("fcntl", types.ModuleType("fcntl"))
sys.modules.setdefault("kmtools", types.ModuleType("kmtools"))
sys.modules.setdefault("kmtools.structure_tools", types.ModuleType("kmtools.structure_tools"))

try:
    from proteinsolver.models.proteinnet import ProteinNet
    print("\n[Test 2.1] Instantiating original ProteinNet class...")
    net = ProteinNet(x_input_size=21, adj_input_size=2, hidden_size=128, output_size=20)
    param_count = sum(p.numel() for p in net.parameters())
    print(f"  Original ProteinNet instantiated: True")
    print(f"  Total trainable parameter count : {param_count:,}")

    # Synthetic forward pass test on GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"  Target Device                   : {device}")
    if torch.cuda.is_available():
        print(f"  GPU Name                        : {torch.cuda.get_device_name(0)}")
    net = net.to(device)

    x_dummy = torch.randint(0, 20, (10,), device=device)
    edge_index_dummy = torch.tensor(
        [[0, 1, 2, 3, 4, 5, 6, 7, 8], [1, 2, 3, 4, 5, 6, 7, 8, 9]],
        dtype=torch.long,
        device=device,
    )
    edge_attr_dummy = torch.randn(9, 2, device=device)

    print(f"  Input Tensor Shapes:")
    print(f"    x          : {list(x_dummy.shape)}")
    print(f"    edge_index : {list(edge_index_dummy.shape)}")
    print(f"    edge_attr  : {list(edge_attr_dummy.shape)}")

    out_dummy = net(x_dummy, edge_index_dummy, edge_attr_dummy)
    print(f"  Forward pass success            : True")
    print(f"  Output Tensor Shape             : {list(out_dummy.shape)} (Expected: [10, 20])")

except Exception as e:
    print(f"  Forward pass FAILED: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# =========================================================================
# STEP 3: CHECKPOINT LOADING INTO ORIGINAL ProteinNet (MILESTONE E0)
# =========================================================================
print("\n" + "=" * 75)
print("STEP 3: CHECKPOINT LOADING INTO ORIGINAL ProteinNet (MILESTONE E0)")
print("=" * 75)

ckpt_path = orig_repo / "data" / "e53-s1952148-d93703104.state"
print(f"Checkpoint path: {ckpt_path.resolve()}")
raw_state_dict = torch.load(ckpt_path, map_location=device, weights_only=True)

# State dict key forensics:
# The published state dict was saved from training run `protein_train/191f05de/model.py`,
# which named the layers `graph_conv_0` and `graph_conv.0..2` (using ModuleList).
# When packaged into `proteinsolver.models.proteinnet`, the author flattened these to:
# `graph_conv_1`, `graph_conv_2`, `graph_conv_3`, `graph_conv_4`.
# All weight and bias tensor shapes are 100% mathematically and structurally identical.
key_mapping = {
    "graph_conv_0.": "graph_conv_1.",
    "graph_conv.0.": "graph_conv_2.",
    "graph_conv.1.": "graph_conv_3.",
    "graph_conv.2.": "graph_conv_4.",
}

mapped_state_dict = {}
for k, v in raw_state_dict.items():
    new_k = k
    for src, dst in key_mapping.items():
        if k.startswith(src):
            new_k = k.replace(src, dst, 1)
            break
    mapped_state_dict[new_k] = v

load_res = net.load_state_dict(mapped_state_dict)
print(f"Load state_dict result:")
print(f"  Missing keys    : {len(load_res.missing_keys)} {load_res.missing_keys}")
print(f"  Unexpected keys : {len(load_res.unexpected_keys)} {load_res.unexpected_keys}")
assert len(load_res.missing_keys) == 0 and len(load_res.unexpected_keys) == 0, "Key mismatch!"

net.eval()
with torch.no_grad():
    out_ckpt = net(x_dummy, edge_index_dummy, edge_attr_dummy)
print(f"Checkpoint forward pass on {device} SUCCESS.")
print(f"Output shape: {list(out_ckpt.shape)}")
print("MILESTONE E0 STATUS: Original ProteinNet executes published checkpoint.")

# =========================================================================
# STEP 4: ORIGINAL design_sequence() SMOKE TEST ON SYNTHETIC GRAPH
# =========================================================================
print("\n" + "=" * 75)
print("STEP 4: ORIGINAL design_sequence() SMOKE TEST ON SYNTHETIC GRAPH")
print("=" * 75)

import proteinsolver.utils.protein_design as ps_design
from torch_geometric.data import Data, Batch

d_tiny = Data(
    x=torch.full((5,), 20, dtype=torch.long),
    edge_index=torch.tensor([[0, 1, 2, 3], [1, 2, 3, 4]], dtype=torch.long),
    edge_attr=torch.randn(4, 2),
)
b_tiny = Batch.from_data_list([d_tiny])

t0 = time.perf_counter()
net_cpu = ProteinNet(21, 2, 128, 20)
net_cpu.load_state_dict(mapped_state_dict)
net_cpu.eval()
x_tiny, proba_tiny = ps_design.design_sequence(net_cpu, b_tiny, value_selection_strategy="map")
t_tiny = time.perf_counter() - t0

print(f"Synthetic design_sequence execution: SUCCESS")
print(f"  Returned types   : x={type(x_tiny)}, proba={type(proba_tiny)}")
print(f"  Generated tokens : {x_tiny.tolist()}")
print(f"  Mean probability : {proba_tiny.mean().item():.4f}")
print(f"  Runtime          : {t_tiny:.4f} s")

# =========================================================================
# STEP 5: REAL PDB WITH ORIGINAL CODE PIPELINE (1n5uA03)
# =========================================================================
print("\n" + "=" * 75)
print("STEP 5: REAL PDB INFERENCE (1n5uA03)")
print("=" * 75)

pdb_path = repo_root / "experiments" / "EXP000_PROTEINSOLVER_SMOKETEST" / "input" / "1n5uA03.pdb"
if not pdb_path.exists():
    pdb_path = repo_root / "experiments" / "EXP001_PROTEINSOLVER_INFERENCE" / "input" / "1n5uA03.pdb"

print(f"Loading target structure: {pdb_path.resolve()}")
parser = PDBParser(QUIET=True)
structure = parser.get_structure("1n5uA03", str(pdb_path))
first_model = next(iter(structure))
chain = first_model["A"] if "A" in first_model else next(iter(first_model))
residues = [r for r in chain if is_aa(r, standard=True)]
native_sequence = "".join(seq1(r.get_resname()) for r in residues)
seq_len = len(residues)

print(f"  Target ID              : 1n5uA03")
print(f"  Chain                  : A")
print(f"  Sequence Length        : {seq_len} residues")
print(f"  Native Sequence        : {native_sequence}")

# Compute heavy atom contacts (< 12A) in the exact format of the repository
heavy_coords = [
    np.array([atom.get_coord() for atom in r if atom.element != "H"])
    for r in residues
]

row_indices = []
col_indices = []
distances = []
r_cutoff = 12.0

for i in range(seq_len):
    for j in range(i + 1, seq_len):
        d = cdist(heavy_coords[i], heavy_coords[j]).min()
        if d < r_cutoff:
            row_indices.append(i)
            col_indices.append(j)
            distances.append(d)

# Construct ProteinData NamedTuple matching proteinsolver.utils.protein_structure
from proteinsolver.utils.protein_structure import ProteinData
pdata = ProteinData(
    sequence=native_sequence,
    row_index=torch.tensor(row_indices, dtype=torch.long),
    col_index=torch.tensor(col_indices, dtype=torch.long),
    distances=torch.tensor(distances, dtype=torch.float),
)

import proteinsolver.datasets.protein as ps_protein

# Pipeline: row_to_data -> transform_edge_attr -> Batch.from_data_list
data = ps_protein.row_to_data(pdata)
data = ps_protein.transform_edge_attr(data)

num_nodes = data.x.size(0)
num_edges = data.edge_index.size(1)
print(f"  Number of nodes (residues) : {num_nodes}")
print(f"  Number of directed edges   : {num_edges}")
print(f"  Edge feature tensor shape  : {list(data.edge_attr.shape)}")

# Wrap in PyG Batch
batch_data = Batch.from_data_list([data])

# =========================================================================
# STEP 5A: VALID ALL-MASKED INVERSE-FOLDING TEST (MAP / GREEDY)
# =========================================================================
print("\n--- [Test 5A] VALID ALL-MASKED CSP DESIGN (Argmax / MAP) ---")
# To design entirely from scratch without data leakage:
# Both data.x must be initialized entirely to mask token (20) and data.y must be omitted/None
batch_data.x = torch.full_like(batch_data.x, 20)
if hasattr(batch_data, "y"):
    delattr(batch_data, "y")

t0 = time.perf_counter()
designed_seq_tensor, designed_proba = ps_design.design_sequence(
    net_cpu, batch_data, value_selection_strategy="map", num_categories=20
)
runtime_map = time.perf_counter() - t0

AMINO_ACIDS = [
    "G", "V", "A", "L", "I", "C", "M", "F", "W", "P",
    "D", "E", "S", "T", "Y", "Q", "N", "K", "R", "H"
]
designed_sequence_map = "".join(AMINO_ACIDS[idx.item()] for idx in designed_seq_tensor)
matches_map = sum(1 for a, b in zip(designed_sequence_map, native_sequence) if a == b)
recovery_map = (matches_map / seq_len) * 100.0

print(f"  Execution Device           : cpu")
print(f"  Inference Runtime          : {runtime_map:.4f} seconds")
print(f"  Generated Sequence (MAP)   : {designed_sequence_map}")
print(f"  Native Sequence            : {native_sequence}")
print(f"  Native Sequence Recovery   : {recovery_map:.2f}% ({matches_map}/{seq_len})")
print(f"  Mean Confidence per Site   : {designed_proba.mean().item():.4f}")

# =========================================================================
# STEP 5B: VALID ALL-MASKED CSP DESIGN (Multinomial T=0.1)
# =========================================================================
print("\n--- [Test 5B] VALID ALL-MASKED CSP DESIGN (Multinomial T=0.1) ---")
batch_data.x = torch.full_like(batch_data.x, 20)
torch.manual_seed(42)

t0 = time.perf_counter()
designed_seq_tensor_multi, designed_proba_multi = ps_design.design_sequence(
    net_cpu, batch_data, value_selection_strategy="multinomial", temperature=0.1, num_categories=20
)
runtime_multi = time.perf_counter() - t0
designed_sequence_multi = "".join(AMINO_ACIDS[idx.item()] for idx in designed_seq_tensor_multi)
matches_multi = sum(1 for a, b in zip(designed_sequence_multi, native_sequence) if a == b)
recovery_multi = (matches_multi / seq_len) * 100.0

print(f"  Inference Runtime          : {runtime_multi:.4f} seconds")
print(f"  Generated Sequence (T=0.1) : {designed_sequence_multi}")
print(f"  Native Sequence Recovery   : {recovery_multi:.2f}% ({matches_multi}/{seq_len})")
print(f"  Mean Confidence per Site   : {designed_proba_multi.mean().item():.4f}")

# =========================================================================
# STEP 6: STRICT SEPARATION OF NATIVE SEQUENCE DIAGNOSTIC SCORING
# =========================================================================
print("\n" + "=" * 75)
print("STEP 6: SEPARATION OF NATIVE SEQUENCE DIAGNOSTIC SCORING")
print("=" * 75)
print("EXPLANATION OF EARLIER '100% RECOVERY' ARTIFACT:")
print("  In the author's original design_sequence function (lines 148-176):")
print("    x_ref = data.y if hasattr(data, 'y') and data.y is not None else data.x")
print("    mask_filled = (x_ref != 20) & (x == 20)")
print("  If data.y contains the native sequence, design_sequence identifies all")
print("  positions as 'pre-assigned' and copies x_ref site-by-site using strategy='ref',")
print("  gathering per-site probabilities. This is a DIAGNOSTIC scoring mode.")
print("  Reporting this as 'sequence recovery' is a methodological error (label leak).")
print("  The VALID inverse-folding recovery must mask all residues (data.x = 20, data.y = None).\n")

# Run diagnostic scoring via get_node_outputs
native_x = torch.tensor([AMINO_ACIDS.index(aa) for aa in native_sequence], dtype=torch.long)
log_probs = ps_design.get_node_outputs(
    net_cpu, native_x, data.edge_index, data.edge_attr, num_categories=20, output_transform="logproba", oneshot=True
)
mean_log_prob = log_probs.mean().item()
perplexity = np.exp(-mean_log_prob)

print(f"  Diagnostic Native Mean Log-Prob : {mean_log_prob:.4f}")
print(f"  Diagnostic Native Perplexity   : {perplexity:.4f}")
print("  Classification: DIAGNOSTIC SCORING / LIKELIHOOD ONLY (not sequence recovery).")

print("\n" + "=" * 75)
print("ALL VERIFICATION SUITE TESTS COMPLETED SUCCESSFULLY.")
print("=" * 75)
