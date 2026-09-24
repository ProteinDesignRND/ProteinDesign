# ProteinSolver Provenance & Environment Manifest

**Date:** 2026-09-24  
**Project:** Protein Design  
**Milestone:** E0-SCIENTIFIC-HARDENING  
**Status:** COMPLETE  

---

## 1. Executive Summary

This manifest documents the exact software, hardware, source code commit, file checksums, compatibility shims, and invocation entrypoints used to execute and verify the historical ProteinSolver codebase (`external/proteinsolver-original`).

All historical source files inside `external/proteinsolver-original` remain **100% untouched and unmodified** from the upstream Git repository. All adaptations required to run the codebase on a modern Windows / PyTorch 2.6 / PyG 2.8 environment reside strictly in an external compatibility layer outside the historical repository.

---

## 2. Historical Repository Provenance

| Property | Value / Status |
| :--- | :--- |
| **Repository Path** | `external/proteinsolver-original` |
| **Upstream URL** | `https://github.com/ostrokach/proteinsolver.git` |
| **Commit SHA** | `69ef0965a3fc3bf191804035b539720a06e58ba6` |
| **Active Branch** | `master` |
| **Git Working Tree Status** | `clean` (`nothing to commit, working tree clean`) |
| **Modifications to Historical Code** | **NONE (0 modified files, 0 untracked files)** |

---

## 3. Cryptographic Artifact Hashes (SHA-256)

| Artifact Description | Local File Path | SHA-256 Checksum |
| :--- | :--- | :--- |
| **Pretrained Model Checkpoint** | `external/proteinsolver-original/data/e53-s1952148-d93703104.state` | `1E8272F05EC19041394568C949BBDBF012EE72C1595BE7157C4BB0324D0B5727` |
| **Verification Structure PDB** | `experiments/EXP000_PROTEINSOLVER_SMOKETEST/input/1n5uA03.pdb` | `19D1FCAA81C209B96C0B0559BC1C775EF393744094CCF2FB928FFEC528B65416` |

---

## 4. Execution Environment & Dependencies

| Component | Specification / Version |
| :--- | :--- |
| **Operating System** | Windows 11 (build 10.0.26100) x86_64 |
| **Python Virtualenv** | `environment/proteinsolver-original` |
| **Python Runtime** | `3.11.9` (`tags/v3.11.9:de54cf5, Apr 2 2024, 10:12:12 [MSC v.1938 64 bit]`) |
| **PyTorch (`torch`)** | `2.6.0+cu124` |
| **PyTorch Geometric (`torch_geometric`)** | `2.8.0.post1` |
| **PyG Scatter (`torch_scatter`)** | `2.1.2+pt26cu124` |
| **BioPython (`Bio`)** | `1.88` |
| **NumPy (`numpy`)** | `2.2.3` |
| **SciPy (`scipy`)** | `1.15.2` |
| **GPU Hardware** | NVIDIA GeForce RTX 3050 6GB Laptop GPU |
| **CUDA Driver / Runtime** | CUDA 12.4 |

---

## 5. Architectural Boundary: Historical Repo vs. External Compatibility Layer

```
+---------------------------------------------------------------------------------------+
| EXTERNAL COMPATIBILITY LAYER (Project-Side: test_original_execution.py & EXP004)     |
|                                                                                       |
|  1. POSIX Shim: sys.modules['fcntl'] = types.ModuleType('fcntl')                     |
|  2. Legacy C-Ext Shim: sys.modules['kmtools'] = types.ModuleType('kmtools')          |
|  3. PyG 2.x Scatter API: torch_geometric.utils.scatter_ -> torch_scatter.scatter     |
|  4. Batch Caller Wrapper: Batch.from_data_list([data]) sets batch tensor ([0...0])    |
|  5. State Dict Key Adapter: maps 'graph_conv_0.' -> 'graph_conv_1.', etc.             |
|  6. Execution Device: CPU inference for iterative CSP design (avoids PyTorch 2.6 bug) |
+---------------------------------------------------------------------------------------+
                                           |
                                  Invokes directly
                                           v
+---------------------------------------------------------------------------------------+
| HISTORICAL REPOSITORY (external/proteinsolver-original - 100% UNMODIFIED)             |
|                                                                                       |
|  - proteinsolver.models.proteinnet.ProteinNet                                         |
|  - proteinsolver.datasets.protein.row_to_data                                         |
|  - proteinsolver.datasets.protein.transform_edge_attr                                 |
|  - proteinsolver.utils.protein_design.design_sequence                                 |
|  - proteinsolver.utils.protein_structure.ProteinData                                  |
|  - data/e53-s1952148-d93703104.state (Official 567,060 parameter checkpoint)          |
+---------------------------------------------------------------------------------------+
```

### Detailed Breakdown of Compatibility Shims

1. **`fcntl` module stubbing:**
   - **Reason:** `proteinsolver/__init__.py` invokes submodules that import `fcntl`, a POSIX-only C-module for file locking. On Windows, Python does not provide `fcntl`.
   - **Shim:** `sys.modules.setdefault("fcntl", types.ModuleType("fcntl"))` injected at script entry before importing `proteinsolver`.
2. **`kmtools` module stubbing:**
   - **Reason:** `proteinsolver.utils.protein_structure` historically imported `kmtools.structure_tools`, which depends on `kmbio` (a compiled C/Cython extension last built for Python 3.5/3.6). The core neural network (`ProteinNet`), edge featurization (`transform_edge_attr`), dataset classes (`row_to_data`), and design functions (`design_sequence`) do not require `kmtools`.
   - **Shim:** `sys.modules.setdefault("kmtools", types.ModuleType("kmtools"))` and `sys.modules.setdefault("kmtools.structure_tools", types.ModuleType("kmtools.structure_tools"))`.
3. **`torch_geometric.utils.scatter_` function binding:**
   - **Reason:** In PyTorch Geometric 1.3, `scatter_` was exposed in `torch_geometric.utils`. In PyG 2.x, the author's own fallback utility (`proteinsolver/utils/scatter.py`) directs users to `torch_scatter.scatter`.
   - **Shim:**
     ```python
     def scatter_(name, src, index, out=None, dim=0, dim_size=None):
         return torch_scatter.scatter(src, index, out=None, dim=dim, dim_size=dim_size, reduce=name)
     torch_geometric.utils.scatter_ = scatter_
     ```
4. **Caller-Side Batching Wrapper (`Batch.from_data_list([data])`):**
   - **Reason:** In PyG 1.3, unbatched `Data` objects had no `batch` attribute (`hasattr(data, 'batch') == False`). In PyG 2.x, `BaseData` declares `batch = None` by default (`hasattr(data, 'batch') == True`), causing `protein_design.py:144` (`data.batch.max().item() + 1`) to fail with `AttributeError: 'NoneType' object has no attribute 'max'`.
   - **Shim:** The caller wraps the single structure graph into `Batch.from_data_list([data])`, which assigns `data.batch = tensor([0, 0, ..., 0])`, matching the historical batch contract without modifying historical library code.
5. **Checkpoint State Dict Key Adapter:**
   - **Reason:** Checkpoint `e53-s1952148-d93703104.state` was saved from training script `protein_train/191f05de/model.py`, which used `nn.ModuleList` (`graph_conv_0` and `graph_conv.0..2`). When the author encapsulated `ProteinNet` in `proteinsolver.models.proteinnet`, the layers were assigned to flat attributes (`graph_conv_1`, `graph_conv_2`, `graph_conv_3`, `graph_conv_4`).
   - **Shim:** A 1-to-1 prefix translation (`graph_conv_0.` -> `graph_conv_1.`, `graph_conv.0.` -> `graph_conv_2.`, `graph_conv.1.` -> `graph_conv_3.`, `graph_conv.2.` -> `graph_conv_4.`). With this mapping, `net.load_state_dict(mapped_state_dict, strict=True)` loads with **0 missing keys, 0 unexpected keys, 45/45 tensor shapes matching, and exactly 567,060 parameters**.
6. **CPU Execution for Iterative Design Loop:**
   - **Reason:** `proteinsolver/utils/protein_design.py:224` creates index tensors using `torch.arange(x.size(0))` without passing `device=x.device` (defaulting to CPU). Under PyTorch 2.6, cross-device indexing (`cuda` tensor indexed by `cpu` mask) raises `RuntimeError: indices should be either on cpu or on same device`.
   - **Shim:** Running the CSP design loop on CPU resolves this completely. CPU execution time is 1.77s for 92 residues.

---

## 6. Project-Side Invocation Files

| File | Purpose | Key Operations |
| :--- | :--- | :--- |
| `test_original_execution.py` | Complete Phase 1 verification suite | Imports unpatched vs patched, loads checkpoint with `strict=True`, runs synthetic design, runs 1n5uA03 MAP design (41.30%), runs multinomial design, demonstrates native likelihood scoring. |
| `experiments/EXP004_MASK_INVARIANCE/run_mask_invariance.py` | Mask-invariance & information leakage audit | Proves logit diff = 0.0 on all-masked input; proves sequence output equality; exposes information leak mechanism when `data.y` is attached. |
| `src/proteinsolver_baseline/graph.py` | Cleanroom PyG graph extractor | On the tested target 1n5uA03, extracted features verified numerically identical to original repo's `row_to_data` and `transform_edge_attr` (`max diff: 0.0`). General equivalence across all structures: NOT VERIFIED. |

---

## 7. Compliance Attestation

1. **No Historical Code Altered:** Zero bytes in `external/proteinsolver-original/` were changed.
2. **Strict Semantics Verified:** Official weights loaded under `strict=True` with zero key or shape deviations.
3. **Information Leak Eliminated:** The valid all-masked test strictly omits `data.y`, completely preventing the reference-copying behavior of `proteinsolver/utils/protein_design.py`.
4. **Reproducibility:** Seeded runs are deterministic across multiple executions.
