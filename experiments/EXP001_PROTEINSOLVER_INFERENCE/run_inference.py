import csv
import json
import os
import sys
import time
import types
from pathlib import Path
from typing import Tuple
import numpy as np
import torch
from Bio.PDB import PDBParser
from Bio.PDB.Polypeptide import is_aa
from Bio.SeqUtils import seq1
from scipy.spatial.distance import cdist

repo_root = Path(__file__).resolve().parents[2]
orig_repo = repo_root / "external" / "proteinsolver-original"
sys.path.insert(0, str(orig_repo))

# Apply documented runtime shims
import torch_geometric
import torch_scatter

def scatter_(name, src, index, out=None, dim=0, dim_size=None):
    return torch_scatter.scatter(src, index, out=None, dim=dim, dim_size=dim_size, reduce=name)

torch_geometric.utils.scatter_ = scatter_

sys.modules.setdefault("fcntl", types.ModuleType("fcntl"))
sys.modules.setdefault("kmtools", types.ModuleType("kmtools"))
sys.modules.setdefault("kmtools.structure_tools", types.ModuleType("kmtools.structure_tools"))

from proteinsolver.models.proteinnet import ProteinNet
import proteinsolver.datasets.protein as ps_protein
import proteinsolver.utils.protein_design as ps_design
from proteinsolver.utils.protein_structure import ProteinData
from torch_geometric.data import Batch

AMINO_ACIDS = [
    "G", "V", "A", "L", "I", "C", "M", "F", "W", "P",
    "D", "E", "S", "T", "Y", "Q", "N", "K", "R", "H"
]

def calculate_sequence_recovery(native_seq: str, designed_seq: str) -> Tuple[float, int, int]:
    matches = sum(1 for a, b in zip(native_seq, designed_seq) if a == b)
    total = len(native_seq)
    recovery_pct = (matches / total) * 100.0
    return recovery_pct, matches, total

def extract_target_pdata(pdb_path: Path, chain_id: str = "A") -> Tuple[ProteinData, str, int]:
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("target", str(pdb_path))
    chain = next(iter(structure))[chain_id]
    residues = [r for r in chain if is_aa(r, standard=True)]
    native_seq = "".join(seq1(r.get_resname()) for r in residues)
    num_residues = len(residues)

    heavy_coords = [np.array([a.get_coord() for a in r if a.element != "H"]) for r in residues]
    row_idx, col_idx, dists = [], [], []
    for i in range(num_residues):
        for j in range(i + 1, num_residues):
            d = cdist(heavy_coords[i], heavy_coords[j]).min()
            if d < 12.0:
                row_idx.append(i)
                col_idx.append(j)
                dists.append(d)

    pdata = ProteinData(
        sequence=native_seq,
        row_index=torch.tensor(row_idx, dtype=torch.long),
        col_index=torch.tensor(col_idx, dtype=torch.long),
        distances=torch.tensor(dists, dtype=torch.float),
    )
    return pdata, native_seq, num_residues

def main():
    exp_dir = Path(__file__).resolve().parent
    config_path = exp_dir / "config.json"
    with open(config_path, "r") as f:
        config = json.load(f)

    log_lines = []
    def log(msg: str):
        print(msg)
        log_lines.append(str(msg))

    log("=" * 75)
    log("EXP001: ORIGINAL PROTEINSOLVER INFERENCE & REPRODUCIBILITY TEST")
    log("=" * 75)

    start_total_time = time.time()
    cuda_available = torch.cuda.is_available()
    device = "cuda" if cuda_available else "cpu"
    gpu_name = torch.cuda.get_device_name(0) if cuda_available else "CPU"
    log(f"Execution Device : {device} ({gpu_name})")
    log(f"PyTorch Version  : {torch.__version__}")
    log(f"PyG Version      : {torch_geometric.__version__}")
    log(f"CUDA Available   : {cuda_available}")

    # Load original ProteinNet
    checkpoint_file = repo_root / config["checkpoint_path"]
    log(f"\n[Phase 1] Loading official pretrained ProteinSolver checkpoint from:")
    log(f"  {checkpoint_file}")
    net = ProteinNet(x_input_size=21, adj_input_size=2, hidden_size=128, output_size=20)
    raw_state_dict = torch.load(checkpoint_file, map_location="cpu", weights_only=True)
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
    assert len(load_res.missing_keys) == 0 and len(load_res.unexpected_keys) == 0
    net.eval()
    param_count = sum(p.numel() for p in net.parameters())
    log(f"  Model loaded successfully. Total parameters: {param_count:,}")

    all_metrics = {}
    csv_rows = []

    # Filter targets: Focus strictly on 1n5uA03 (the paper demo CATH domain)
    targets = [t for t in config["targets"] if t["name"] == "1n5uA03"]
    if not targets:
        targets = config["targets"]

    for target in targets:
        target_name = target["name"]
        pdb_path = repo_root / target["pdb_path"]
        log("\n" + "-" * 75)
        log(f"Processing Target: {target_name} ({target['description']})")
        log(f"PDB Path: {pdb_path}")

        pdata, native_seq, num_residues = extract_target_pdata(pdb_path, target.get("chain", "A"))
        raw_graph_data = ps_protein.row_to_data(pdata)
        graph_data = ps_protein.transform_edge_attr(raw_graph_data)
        num_edges = graph_data.edge_index.size(1)

        log(f"  Residue Count (Nodes) : {num_residues}")
        log(f"  Directed Edges (<12A) : {num_edges}")
        log(f"  Average Degree        : {num_edges / num_residues:.2f}")
        log(f"  Native Sequence       : {native_seq}")

        # Native sequence diagnostic scoring
        native_x = torch.tensor([AMINO_ACIDS.index(aa) for aa in native_seq], dtype=torch.long)
        log_probs = ps_design.get_node_outputs(
            net, native_x, graph_data.edge_index, graph_data.edge_attr, num_categories=20, output_transform="logproba", oneshot=True
        )
        native_score = log_probs.mean().item()
        native_ppl = np.exp(-native_score)
        log(f"  Native Log-Prob Score : {native_score:.4f} (Diagnostic)")
        log(f"  Native Perplexity     : {native_ppl:.4f} (Diagnostic)")

        target_metrics = {
            "num_residues": num_residues,
            "num_edges": num_edges,
            "native_sequence": native_seq,
            "native_log_prob_score": round(native_score, 4),
            "native_perplexity": round(native_ppl, 4),
            "sampling_results": {},
        }

        for samp_cfg in config["sampling_configurations"]:
            cfg_name = samp_cfg["name"]
            strategy = samp_cfg["strategy"]
            temp = samp_cfg["temperature"]
            rand_pos = samp_cfg["random_position"]

            log(f"\n  [Sampling Config: {cfg_name}] Strategy={strategy}, Temp={temp}, RandPos={rand_pos}")

            torch.manual_seed(42)
            np.random.seed(42)

            batch_data = Batch.from_data_list([graph_data])
            batch_data.x = torch.full_like(batch_data.x, 20)
            if hasattr(batch_data, "y"):
                delattr(batch_data, "y")

            t0 = time.perf_counter()
            des_tokens, des_probas = ps_design.design_sequence(
                net, batch_data,
                random_position=rand_pos,
                value_selection_strategy=strategy,
                temperature=temp,
                num_categories=20,
            )
            inf_time = time.perf_counter() - t0

            des_seq = "".join(AMINO_ACIDS[idx.item()] for idx in des_tokens)
            rec_pct, matches, total = calculate_sequence_recovery(native_seq, des_seq)
            mean_conf = des_probas.mean().item()

            log(f"    Designed Sequence : {des_seq}")
            log(f"    Sequence Recovery : {rec_pct:.2f}% ({matches}/{total})")
            log(f"    Mean Confidence   : {mean_conf:.4f}")
            log(f"    Inference Time    : {inf_time:.3f} s")

            target_metrics["sampling_results"][cfg_name] = {
                "designed_sequence": des_seq,
                "recovery_pct": round(rec_pct, 2),
                "matches": matches,
                "total_residues": total,
                "mean_confidence": round(mean_conf, 4),
                "inference_time_seconds": round(inf_time, 4),
            }

            csv_rows.append({
                "target": target_name,
                "config": cfg_name,
                "strategy": strategy,
                "temperature": temp,
                "random_position": rand_pos,
                "recovery_pct": round(rec_pct, 2),
                "matches": matches,
                "total_residues": total,
                "mean_confidence": round(mean_conf, 4),
                "inference_time_s": round(inf_time, 4),
                "designed_sequence": des_seq,
            })

        # Determinism test
        log(f"\n  [Determinism Test] Running identical configurations twice with seed=42...")
        batch1 = Batch.from_data_list([graph_data])
        batch1.x = torch.full_like(batch1.x, 20)
        if hasattr(batch1, "y"): delattr(batch1, "y")
        torch.manual_seed(42)
        r1, _ = ps_design.design_sequence(net, batch1, value_selection_strategy="map", num_categories=20)

        batch2 = Batch.from_data_list([graph_data])
        batch2.x = torch.full_like(batch2.x, 20)
        if hasattr(batch2, "y"): delattr(batch2, "y")
        torch.manual_seed(42)
        r2, _ = ps_design.design_sequence(net, batch2, value_selection_strategy="map", num_categories=20)

        is_det = bool((r1 == r2).all().item())
        log(f"    Mode 'map_greedy': Run 1 == Run 2 -> {is_det}")
        target_metrics["determinism_map_greedy"] = is_det

        all_metrics[target_name] = target_metrics

    total_exp_time = time.time() - start_total_time
    log("\n" + "=" * 75)
    log(f"EXP001 INFERENCE COMPLETED IN {total_exp_time:.2f} SECONDS")
    log("=" * 75)

    # Write log
    with open(exp_dir / "run_log.txt", "w") as f:
        f.write("\n".join(log_lines) + "\n")

    # Write metrics JSON
    with open(exp_dir / "metrics.json", "w") as f:
        json.dump(all_metrics, f, indent=2)

    # Write output CSV
    output_dir = exp_dir / "output"
    output_dir.mkdir(exist_ok=True)
    csv_path = output_dir / "inference_summary.csv"
    if csv_rows:
        fieldnames = list(csv_rows[0].keys())
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)
        log(f"Saved inference summary table to: {csv_path}")

if __name__ == "__main__":
    main()
