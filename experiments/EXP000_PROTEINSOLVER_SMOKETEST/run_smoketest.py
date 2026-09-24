import json
import sys
import time
import types
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
from Bio.PDB import PDBParser
from Bio.PDB.Polypeptide import is_aa
from Bio.SeqUtils import seq1
from scipy.spatial.distance import cdist

repo_root = Path(__file__).resolve().parents[2]
orig_repo = repo_root / "external" / "proteinsolver-original"
sys.path.insert(0, str(orig_repo))

def main():
    exp_dir = Path(__file__).resolve().parent
    config_path = exp_dir / "config.json"
    with open(config_path, "r") as f:
        config = json.load(f)

    log_lines = []
    def log(msg=""):
        print(msg)
        log_lines.append(str(msg))

    log("=" * 70)
    log("EXP000: ORIGINAL PROTEINSOLVER IMPLEMENTATION SMOKE TEST")
    log("=" * 70)

    start_time = time.time()
    cuda_available = torch.cuda.is_available()
    device = "cuda" if cuda_available else "cpu"
    device_name = torch.cuda.get_device_name(0) if cuda_available else "CPU"
    log(f"Execution Device : {device} ({device_name})")

    # Step 1: Historical source direct execution check
    log("\n[Step 1] Checking direct import of original proteinsolver without shims...")
    direct_import_success = False
    try:
        import proteinsolver
        direct_import_success = True
        log("  Direct import succeeded.")
    except Exception as e:
        log(f"  Direct import failed as expected ({type(e).__name__}: {e}).")
        log("  Reason: proteinsolver/__init__.py imports kmtools, requiring legacy kmbio and fcntl.")

    # Clean up sys.modules
    for mod in list(sys.modules.keys()):
        if mod == "proteinsolver" or mod.startswith("proteinsolver."):
            del sys.modules[mod]

    # Step 2: Apply documented runtime compatibility shims
    log("\n[Step 2] Applying documented runtime compatibility shims...")
    import torch_geometric
    import torch_scatter
    def scatter_(name, src, index, out=None, dim=0, dim_size=None):
        return torch_scatter.scatter(src, index, out=None, dim=dim, dim_size=dim_size, reduce=name)
    torch_geometric.utils.scatter_ = scatter_

    sys.modules.setdefault("fcntl", types.ModuleType("fcntl"))
    sys.modules.setdefault("kmtools", types.ModuleType("kmtools"))
    sys.modules.setdefault("kmtools.structure_tools", types.ModuleType("kmtools.structure_tools"))
    shim_applied = True
    log("  Applied shims: torch_geometric.utils.scatter_, fcntl, kmtools isolation.")

    # Step 3: Instantiate original ProteinNet
    log("\n[Step 3] Instantiating original ProteinNet architecture...")
    try:
        from proteinsolver.models.proteinnet import ProteinNet
        net = ProteinNet(
            x_input_size=config["model_architecture"]["x_input_size"],
            adj_input_size=config["model_architecture"]["adj_input_size"],
            hidden_size=config["model_architecture"]["hidden_size"],
            output_size=config["model_architecture"]["output_size"],
        )
        param_count = sum(p.numel() for p in net.parameters())
        original_impl_pass = True
        log(f"  Model instantiated successfully. Parameters: {param_count:,}")
    except Exception as e:
        log(f"  Failed to instantiate ProteinNet: {e}")
        original_impl_pass = False
        sys.exit(1)

    # Step 4: Checkpoint Loading
    log(f"\n[Step 4] Loading checkpoint from: {config['checkpoint_path']}...")
    checkpoint_file = repo_root / config["checkpoint_path"]
    assert checkpoint_file.exists(), f"Checkpoint file missing: {checkpoint_file}"
    raw_state_dict = torch.load(checkpoint_file, map_location="cpu", weights_only=True)

    # Key remapping from training notebook names to refactored package names
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
    checkpoint_loading_pass = (len(load_res.missing_keys) == 0 and len(load_res.unexpected_keys) == 0)
    log(f"  Missing keys: {len(load_res.missing_keys)}, Unexpected keys: {len(load_res.unexpected_keys)}")
    log(f"  Checkpoint loading pass: {checkpoint_loading_pass}")

    # Step 5: Forward pass test (CPU & CUDA)
    log("\n[Step 5] Running forward pass on tiny graph...")
    x_test = torch.randint(0, 20, (10,))
    edge_index_test = torch.tensor([[0, 1, 2, 3, 4, 5, 6, 7, 8], [1, 2, 3, 4, 5, 6, 7, 8, 9]], dtype=torch.long)
    edge_attr_test = torch.randn(9, 2)

    net.eval()
    with torch.no_grad():
        out_cpu = net(x_test, edge_index_test, edge_attr_test)
    forward_pass_pass = (out_cpu.shape == (10, 20))
    log(f"  CPU Forward pass output shape: {list(out_cpu.shape)} (Expected: [10, 20])")

    cuda_execution_pass = False
    if cuda_available:
        try:
            net_cuda = net.to("cuda")
            with torch.no_grad():
                out_cuda = net_cuda(x_test.cuda(), edge_index_test.cuda(), edge_attr_test.cuda())
            cuda_execution_pass = (out_cuda.shape == (10, 20))
            log(f"  CUDA Forward pass output shape: {list(out_cuda.shape)} - SUCCESS")
            net = net.to("cpu")
        except Exception as e:
            log(f"  CUDA Forward pass FAILED: {e}")

    # Step 6: Test original design_sequence
    log("\n[Step 6] Testing original design_sequence on synthetic graph...")
    import proteinsolver.utils.protein_design as ps_design
    from torch_geometric.data import Data, Batch

    d_test = Data(
        x=torch.full((5,), 20, dtype=torch.long),
        edge_index=torch.tensor([[0, 1, 2, 3], [1, 2, 3, 4]], dtype=torch.long),
        edge_attr=torch.randn(4, 2),
    )
    b_test = Batch.from_data_list([d_test])
    try:
        x_des, p_des = ps_design.design_sequence(net, b_test, value_selection_strategy="map")
        design_sequence_pass = (x_des.size(0) == 5)
        log(f"  Synthetic design_sequence result: tokens={x_des.tolist()} - SUCCESS")
    except Exception as e:
        log(f"  Synthetic design_sequence FAILED: {e}")
        design_sequence_pass = False

    # Step 7: Real Target Test (1n5uA03)
    log("\n[Step 7] Testing real PDB graph pipeline on 1n5uA03.pdb...")
    pdb_path = repo_root / config["target_pdb"]
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("1n5uA03", str(pdb_path))
    chain = next(iter(structure))["A"]
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

    from proteinsolver.utils.protein_structure import ProteinData
    import proteinsolver.datasets.protein as ps_protein

    pdata = ProteinData(
        sequence=native_seq,
        row_index=torch.tensor(row_idx, dtype=torch.long),
        col_index=torch.tensor(col_idx, dtype=torch.long),
        distances=torch.tensor(dists, dtype=torch.float),
    )
    data = ps_protein.row_to_data(pdata)
    data = ps_protein.transform_edge_attr(data)
    b_real = Batch.from_data_list([data])
    b_real.x = torch.full_like(b_real.x, 20)
    if hasattr(b_real, "y"):
        delattr(b_real, "y")

    t_start = time.perf_counter()
    x_gen, p_gen = ps_design.design_sequence(net, b_real, value_selection_strategy="map")
    gen_time = time.perf_counter() - t_start

    aa = ["G","V","A","L","I","C","M","F","W","P","D","E","S","T","Y","Q","N","K","R","H"]
    gen_seq = "".join(aa[i.item()] for i in x_gen)
    recovery = sum(a == b for a, b in zip(gen_seq, native_seq)) / num_residues * 100.0

    log(f"  Target 1n5uA03 length         : {num_residues} residues")
    log(f"  Graph directed edges (<12A)   : {data.edge_index.size(1)}")
    log(f"  Valid all-masked recovery     : {recovery:.2f}% ({sum(a == b for a, b in zip(gen_seq, native_seq))}/{num_residues})")
    log(f"  Inference runtime (CPU)       : {gen_time:.4f} s")
    log(f"  Designed sequence (MAP)       : {gen_seq}")

    total_duration = time.time() - start_time
    log("\n" + "=" * 70)
    log("EXPLICIT SMOKE TEST VERIFICATION RESULTS:")
    log(f"  Original implementation: {'PASS' if original_impl_pass else 'FAIL'}")
    log(f"  Checkpoint loading: {'PASS' if checkpoint_loading_pass else 'FAIL'}")
    log(f"  Forward pass: {'PASS' if forward_pass_pass else 'FAIL'}")
    log(f"  design_sequence: {'PASS' if design_sequence_pass else 'FAIL'}")
    log(f"  Compatibility shim: {'YES' if shim_applied else 'NO'}")
    log(f"  CUDA: {'PASS' if cuda_execution_pass else 'FAIL'}")
    log("=" * 70)
    log(f"EXP000 completed in {total_duration:.3f} seconds.")

    # Write log
    with open(exp_dir / "run_log.txt", "w") as f:
        f.write("\n".join(log_lines) + "\n")

    # Write metrics
    metrics = {
        "experiment_id": config["experiment_id"],
        "date": config["date"],
        "original_implementation": "PASS" if original_impl_pass else "FAIL",
        "checkpoint_loading": "PASS" if checkpoint_loading_pass else "FAIL",
        "forward_pass": "PASS" if forward_pass_pass else "FAIL",
        "design_sequence": "PASS" if design_sequence_pass else "FAIL",
        "compatibility_shim": "YES" if shim_applied else "NO",
        "cuda_execution": "PASS" if cuda_execution_pass else "FAIL",
        "model_parameters": param_count,
        "test_target": "1n5uA03",
        "sequence_length": num_residues,
        "num_edges": data.edge_index.size(1),
        "valid_all_masked_recovery": round(recovery, 2),
        "designed_sequence": gen_seq,
        "inference_runtime_seconds": round(gen_time, 4),
        "total_test_duration_seconds": round(total_duration, 4),
    }
    with open(exp_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

if __name__ == "__main__":
    main()
