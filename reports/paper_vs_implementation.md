# ProteinSolver: Paper vs. Implementation Audit & Forensics

**Document Status**: COMPLETED & VERIFIED  
**Audit Date**: September 24, 2026  
**Milestone**: E0-RUNTIME: COMPLETE | E0-SCIENTIFIC-HARDENING: COMPLETE  
**Historical Equivalence Claim**: FUNCTIONALLY REPRODUCED WITH MODERN COMPATIBILITY ADAPTATION  
**Reference Paper**: Strokach, Becerra, Corbi-Verge, Pérez-Riba, & Kim, *Fast and Flexible Protein Design Using Deep Graph Neural Networks*, Cell Systems 11, 402–411 (October 21, 2020). DOI: [10.1016/j.cels.2020.08.016](https://doi.org/10.1016/j.cels.2020.08.016)  
**Evaluated Repository**: `external/proteinsolver-original` (`https://github.com/ostrokach/proteinsolver`)  
**Evaluated Commit**: `69ef0965a3fc3bf191804035b539720a06e58ba6`  
**Execution Environment**: Python 3.11.9, PyTorch 2.6.0+cu124, PyG 2.8.0.post1, torch-scatter 2.1.2+pt26cu124, BioPython 1.88, NVIDIA GeForce RTX 3050 6GB Laptop GPU.  

---

## 1. Scope & Attribution Separation

To maintain strict scientific integrity, this audit explicitly distinguishes between:
1. **Original Historical Code**: The untouched code in `external/proteinsolver-original` at commit `69ef0965` (100% clean working tree).
2. **External Compatibility Layer**: The minimal external adapter / caller adjustments outside the historical repo required to execute the historical code on a modern Python 3.11 / PyTorch 2.6 / PyG 2.8 Windows platform.
3. **Cleanroom Reconstructed Code**: The independent implementation in `src/proteinsolver_baseline/` developed to isolate architectural math from legacy repository dependencies.

---

## 2. Component Forensic Matrix

| Component | Paper Claim (Strokach et al. 2020) | Implementation Reality in Code | Status | Exact Evidence |
| :--- | :--- | :--- | :---: | :--- |
| **GNN Architecture** | Deep GNN with EdgeConv blocks and residual aggregation | 4 EdgeConv residual blocks updating both edge and node features | **VERIFIED MATCH** | `proteinsolver/models/proteinnet.py` and `proteinsolver/nn/edge_conv_mod.py`. Total parameter count = 567,060. |
| **Node Vocabulary** | 20 standard amino acids + 1 mask token (21 tokens total) | Vocabulary indices $0 \dots 19$ for canonical amino acids, index 20 for mask/unknown (`-`). Dimension $x \in \{0, \dots, 20\}$ | **VERIFIED MATCH** | `AMINO_ACID_TO_IDX` in `proteinsolver/utils/protein_sequence.py`. Embedding layer: `nn.Embedding(21, 128)`. |
| **Edge Connectivity** | Heavy atom contact distance $< 12.0\text{ \AA}$ | Directed edges between all residue pairs with $\min_{a \in i, b \in j} \|r_{ia} - r_{jb}\|_2 < 12.0\text{ \AA}$ | **VERIFIED MATCH** | `proteinsolver/utils/protein_structure.py::get_interaction_dataset_wdistances`. Self-loops explicitly removed. |
| **Edge Featurization** | Continuous Cartesian distance and sequence separation | 2-channel normalized edge feature vector: $\left[\frac{d - 6.0}{12.0}, \frac{\|j - i\| - 0.0}{68.1319}\right]$ | **VERIFIED MATCH** | Normalization constants hardcoded in `proteinsolver/datasets/protein.py` lines 168–182 (`normalize_cart_distances`, `normalize_seq_distances`). |
| **Published Checkpoint** | Trained on Gene3D protein domains | Checkpoint file `e53-s1952148-d93703104.state` (53 epochs, 1.95M steps) | **VERIFIED MATCH** | Stored in `external/proteinsolver-original/data/`. Matches 567,060 parameters with 0 missing/unexpected keys after layer name normalization under `strict=True`. |
| **Checkpoint Layer Naming** | Checkpoint weights match packaged class | Raw state dict uses training notebook names (`graph_conv_0`, `graph_conv.0..2`); library class uses (`graph_conv_1..4`) | **IMPLEMENTATION DIFFERENCE** | Originates from training script `protein_train/191f05de/model.py` which used `nn.ModuleList`. All weight/bias shapes are identical. |
| **Inference Algorithm** | CSP sequential design via iterative unmasking | Iterative masked residue assignment: argmax MAP or multinomial sampling | **VERIFIED MATCH** | `proteinsolver/utils/protein_design.py::design_sequence`. |
| **Batching Contract in PyG** | Batched or unbatched graph inference | PyG 1.3 omitted `.batch` on `Data`; PyG 2.x sets `Data.batch = None`, causing `None.max()` crash | **IMPLEMENTATION DIFFERENCE** | Caller wraps input graph in `Batch.from_data_list([data])`, assigning `data.batch = tensor([0..0])`. Leaves original repo untouched. |
| **Cross-Device Indexing** | CPU / GPU agnostic design | `torch.arange(x.size(0))` in `protein_design.py` creates CPU tensor, triggering cross-device indexing error on CUDA in PyTorch 2.6 | **IMPLEMENTATION DIFFERENCE** | PyTorch 2.6 strictly enforces same-device tensor indexing. Running on CPU resolves this completely (1.77s runtime). |
| **PyG Scatter Function** | Uses PyG scatter aggregation | Historically used `torch_geometric.utils.scatter_`, removed in modern PyG 2.x | **IMPLEMENTATION DIFFERENCE** | Author already provided fallback in `proteinsolver/utils/scatter.py` using `torch_scatter.scatter`. Shim outside repo activates this fallback. |
| **Legacy Dependencies** | Assumed standard scientific Python stack | Hard dependencies on obsolete Cython PDB parser `kmbio` (Python 3.5/3.6 only) and UNIX `fcntl` | **IMPLEMENTATION DIFFERENCE** | Isolated via minimal runtime stubs outside historical repo; Biopython adapter produced numerically identical contact graphs on the tested target 1n5uA03 (`max diff: 0.0`). General kmbio/Biopython equivalence across all structures: NOT VERIFIED. |

---

## 3. Structural Comparison of Execution Pathways

### Pathway A: Original Historical Code (`external/proteinsolver-original`)
- **Execution File**: `proteinsolver/models/proteinnet.py`, `proteinsolver/datasets/protein.py`, `proteinsolver/utils/protein_design.py`
- **Model Class**: `from proteinsolver.models.proteinnet import ProteinNet`
- **Execution Status**: **FUNCTIONALLY REPRODUCED WITH MODERN COMPATIBILITY ADAPTATION**. Successfully instantiates, loads official checkpoint under `strict=True`, performs CUDA forward passes, and generates sequences using original `design_sequence`.
- **Requirements**:
  1. Runtime monkeypatch for `torch_geometric.utils.scatter_` (using author's own scatter implementation).
  2. Module stubs for `fcntl` (Windows POSIX) and `kmtools` (isolating obsolete `kmbio`).
  3. Caller graph wrapping via `Batch.from_data_list([data])`.
  4. Execution of iterative design loop on CPU to satisfy PyTorch 2.6 same-device tensor indexing.

### Pathway B: Reconstructed Cleanroom Code (`src/proteinsolver_baseline`)
- **Execution File**: `src/proteinsolver_baseline/model.py`, `graph.py`, `sampler.py`
- **Model Class**: `from src.proteinsolver_baseline import ProteinSolverNet`
- **Execution Status**: **VERIFIED**. Direct 100% key match with raw checkpoint naming without key mapping.
- **Role in Research**: Serves as an unencumbered, pure-PyTorch reference implementation free from legacy package baggage.

---

## 4. Methodological Distinction: Sequence Recovery vs. Diagnostic Likelihood

A critical finding from source inspection of `proteinsolver/utils/protein_design.py` (lines 148–176):
- If `data.y` is supplied with the reference sequence, `design_sequence` treats all non-mask residues as **pre-assigned**, iteratively gathers their marginal probabilities using strategy `"ref"`, and copies the reference sequence into the output.
- This produces an apparent **100% recovery** which is actually an informational leak / diagnostic scoring routine.
- The **valid inverse-folding sequence recovery** requires starting with **all residues masked** (`data.x = 20`, `data.y = None`).
- Under valid all-masked CSP generation on test structure 1n5uA03 (92 AA), the original implementation achieves **41.30% native sequence identity** (38/92 residues, 1.77s runtime).
- This metric is properly classified as a **single-target all-masked inverse-folding integration result**, rather than benchmark accuracy or general proof of reproduction across all CATH superfamilies.
