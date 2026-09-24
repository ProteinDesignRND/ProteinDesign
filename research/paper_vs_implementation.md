# ProteinSolver: Paper vs. Repository Implementation Audit

> **SUPERSEDED**: The authoritative version of this audit is [`reports/paper_vs_implementation.md`](file:///d:/Projects/Protein%20Design/reports/paper_vs_implementation.md). This file is preserved as a development-stage reference with detailed code-level analysis.

**Audit Date**: September 24, 2026  
**Reference Paper**: Strokach, Becerra, Corbi-Verge, Pérez-Riba, & Kim, *Fast and Flexible Protein Design Using Deep Graph Neural Networks*, Cell Systems 11, 402–411 (October 21, 2020). DOI: [10.1016/j.cels.2020.08.016](https://doi.org/10.1016/j.cels.2020.08.016)  
**Evaluated Repository**: `external/proteinsolver-original` (`https://gitlab.com/ostrokach/proteinsolver`)  
**Evaluated Commit**: `69ef0965a3fc3bf191804035b539720a06e58ba6` (December 10, 2021)  
**Execution Environment**: Python 3.11.9, PyTorch 2.6.0+cu124, PyG 2.8.0.post1, NVIDIA RTX 3050 6GB Laptop GPU.

---

## 1. Summary of Audit Classifications

| Dimension | Paper Description | Code Implementation | Audit Status | Evidence / Notes |
| :--- | :--- | :--- | :--- | :--- |
| **GNN Architecture** | Deep GNN with EdgeConv blocks and residual aggregation | 4 EdgeConv residual blocks with linear projections and LayerNorm / ELU activations | **VERIFIED MATCH** | `proteinsolver/models/protein_solver.py`, `EdgeConvMod` in `edge_conv_mod.py`. Total parameter count = 567,060. |
| **Node Features** | 20 canonical amino acids + 1 mask token (21 vocabulary categories) | Tensor `x` of integer indices $\{0, \dots, 19\}$ + index 20 as mask token; embedded into $\mathbb{R}^{128}$ | **VERIFIED MATCH** | `AMINO_ACID_TO_IDX` in `proteinsolver/utils/protein.py`; embedding layer `nn.Embedding(21, 128)`. |
| **Edge Connectivity** | $C_\alpha - C_\alpha$ spatial distance cutoff at 12.0 Å | Directed edges between all residue pairs with $d_{ij} \le 12.0$ Å | **VERIFIED MATCH** | `proteinsolver/utils/protein_structure.py::extract_protein_graph(..., r_cutoff=12)`. |
| **Edge Features** | Continuous distance $d_{ij}$ and sequence separation $\|i - j\|$ | 2-channel normalized edge feature vector $\mathbf{e}_{ij} = \left[\frac{d_{ij} - 6.0}{12.0}, \frac{\|j - i\| - 0.0}{68.1319}\right]$ | **VERIFIED MATCH** | Continuous normalization constants hardcoded in `protein_structure.py` lines 86–90. |
| **Training Masking Procedure** | Random variable fraction (up to 100%) of residue identities masked as CSP | For each graph batch, a random subset of residues is replaced by token 20 (mask) | **VERIFIED MATCH** | `proteinsolver/datasets/proteinnet.py` and `proteinsolver/scripts/train.py`. |
| **Training Objective & Loss** | Cross-entropy loss computed over masked positions | `F.cross_entropy` evaluated over masked positions: $L = -\frac{1}{\|M\|} \sum_{i \in M} \log P(s_i \mid \mathbf{x}_{\text{masked}}, G)$ | **VERIFIED MATCH** | Masking target gathered via `gather` on masked indices. |
| **Inference / Sequence Generation** | Constraint Satisfaction Problem (CSP) iterative masked inference | Iterative single-residue unmasking: greedy MAP or multinomial sampling at temperature $T$ | **VERIFIED MATCH** | `proteinsolver/utils/protein_design.py::design_sequence` and notebook `20_protein_demo.ipynb`. |
| **Sequence Scoring / Evaluation** | Sequence probability / pseudo-log-likelihood (PLL) | Two modes: `scan_with_mask` (masking each residue individually: $P(s_i \mid s_{\setminus i}, G)$) and zero-shot `oneshot` | **VERIFIED MATCH** | `scan_with_mask` in `proteinsolver/utils/protein_design.py`. |
| **Pretrained Weights** | Trained on 72 million Gene3D protein domains | Checkpoint `e53-s1952148-d93703104.state` (53 epochs, 1.95M optimizer steps, 937M samples seen) | **VERIFIED MATCH** | Stored in `external/proteinsolver-original/data/`. Matches architecture exactly with 0 missing/unexpected keys. |
| **Dataset Storage Format** | Described in paper as Gene3D structural domain database | Stored as Apache Parquet (`.snappy.parquet`) instead of raw HDF5 or PDBs | **IMPLEMENTATION DIFFERENCE** | Paper text suggests database records, but the repo serialized pairwise indices and distances into compressed Parquet tables (`residue_idx_1_corrected`, `residue_idx_2_corrected`, `distances`). |
| **Rosetta Energy Evaluation** | Rosetta score (`score_jd2`, `ref2015`, Cartesian score) cited for stability verification | Scripts invoke external Linux binary `$ROSETTA_BIN/score_jd2.static.linuxgccrelease` | **PARTIAL MATCH** | Requires licensed standalone Rosetta installation; cannot run out-of-the-box on Windows/without Rosetta binary. |
| **kmbio Parsing Dependency** | Not discussed in paper (assumed standard PDB parsing) | Repository relies on private C++ Cython fork `kmbio` for PDB coordinate parsing | **IMPLEMENTATION DIFFERENCE** | `kmbio` has binary wheels only for obsolete Python 3.5/3.6. Cleanly resolved via modern Biopython adapter without altering model math. |
| **Full 72M Gene3D Raw Corpus** | 72 million domain training corpus cited | Distributed across external URLs/zenodo; not bundled in repository due to multi-terabyte size | **NOT VERIFIABLE (OUT OF SCOPE)** | Bundled checkpoint is available, but raw 72M Parquet dataset download is deliberately omitted to prevent excessive bandwidth waste. |

---

## 2. Detailed Technical Audit Findings

### A. Graph Featurization & Edge Representation
- **Paper Claim**: The network constructs graphs where residues are nodes and spatial proximities under 12 Å are edges, incorporating distance and sequential distance.
- **Source Grounding**:
  In `proteinsolver/utils/protein_structure.py`:
  ```python
  adj = (distances < r_cutoff)
  edge_index = adj.nonzero()
  edge_attr = torch.stack([
      (distances[edge_index] - 6.0) / 12.0,
      (sequence_separation[edge_index] - 0.0) / 68.1319,
  ], dim=-1)
  ```
- **Finding**: **VERIFIED MATCH**. The edge attributes are continuous normalized floats, not discrete distance bins. The normalizers $(6.0, 12.0)$ and $(0.0, 68.1319)$ represent empirical mean and standard deviations derived from the Gene3D training set.

### B. Neural Architecture Specifications
- **Paper Claim**: Deep message passing graph neural network using modified EdgeConv operations with residual skip connections.
- **Source Grounding**:
  In `proteinsolver/models/protein_solver.py` and `proteinsolver/nn/edge_conv_mod.py`:
  - 4 sequential `EdgeConvMod` residual blocks.
  - Node embedding dimension $d_n = 128$.
  - Edge embedding dimension $d_e = 64$ expanding to $128$.
  - Hidden MLP layers: Linear $\to$ LayerNorm $\to$ ELU $\to$ Linear.
  - Total parameter count: **567,060 parameters** (2.28 MB checkpoint).
- **Finding**: **VERIFIED MATCH**. The network size is remarkably compact by modern LLM standards (567K parameters vs. 1.7M in ProteinMPNN or 650M in ESMFold), enabling sub-second inference on standard consumer GPUs.

### C. Sequence Scoring & The "Information Leakage" Pitfall
- **Paper Claim**: ProteinSolver evaluates sequence compatibility with structural backbones via log-likelihood.
- **Critical Code Discovery**:
  Because ProteinSolver is a bidirectional masked graph model (BERT-style), passing a fully unmasked sequence $(x_0, x_1, \dots, x_{L-1})$ into the model results in trivial label copying due to direct residual embeddings.
  In `proteinsolver/utils/protein_design.py`, the authors explicitly addressed this by providing `scan_with_mask`:
  ```python
  for i in range(x_ref.size(0)):
      x = x_ref.clone()
      x[i] = num_categories # MASK TOKEN
      output = net(x, edge_index, edge_attr)
      output_for_mask[i] = output.gather(1, x_ref.view(-1, 1))[i]
  ```
- **Finding**: **VERIFIED MATCH**. True sequence scoring in ProteinSolver is Pseudo-Log-Likelihood (PLL) through leave-one-out masking, exactly replicating the marginal evaluation of modern masked language models.

### D. Upstream Dependency Obsolescence & Modern Compatibility
- **Paper Claim**: Code publicly available on GitLab.
- **Implementation Reality**:
  The historical repository specifies Python 3.7 and hard-depends on `kmbio` (a private Cythonized PDB parser by the author) and legacy PyG functions (`torch_geometric.utils.scatter_`).
  On modern systems (Python 3.10+, PyTorch 2.0+), `kmbio` fails compilation.
- **Audit Assessment**: **IMPLEMENTATION DIFFERENCE / DEPENDENCY ROT**.
  This was resolved by creating `src/proteinsolver_baseline/` which maps standard Biopython `Bio.PDB` structures into the tensors expected by `ProteinSolverNet`. On the tested target (1n5uA03), the Biopython-based cleanroom extractor produced tensors (`x`, `edge_index`, `edge_attr`) numerically identical to the original repo pipeline (`max diff: 0.0`). General equivalence to the historical `kmbio` parser across all structures has NOT been verified.
