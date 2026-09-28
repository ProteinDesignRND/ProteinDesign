# Project Truth — Single Source of Truth

**Last Updated:** 2026-09-28  
**Maintained By:** Project Lead  

This document is the single authoritative reference for what has been verified, what is assumed, what remains untested, and what is known to be limited. All other project documents defer to this one when there is a conflict.

---

## Verified Facts

These claims are supported by direct inspection, execution, or primary literature.

### ProteinSolver Architecture
- ProteinSolver is a 4-block residual EdgeConv GNN with 567,060 parameters. `[VERIFIED]`
- Node vocabulary: 20 amino acids + 1 mask token (index 20). Embedding: `nn.Embedding(21, 128)`. `[VERIFIED]`
- Edge features: 2-channel normalized float vector `[(d - 6.0)/12.0, (|j-i| - 0.0)/68.1319]`. `[VERIFIED]`
- Edge connectivity: all residue pairs with minimum heavy-atom distance < 12.0 Å. `[VERIFIED]`

### Checkpoint & Repository
- Historical repository: `external/proteinsolver-original`, commit `69ef0965a3fc3bf191804035b539720a06e58ba6`, branch `master`, working tree clean (zero modifications). `[VERIFIED]`
- This commit is **the upstream repository revision tested in this study**. It is NOT confirmed to be the exact source state at the time of the 2020 Cell Systems publication. `[VERIFIED — with limitation]`
- Published checkpoint: `e53-s1952148-d93703104.state` (SHA-256: `1E8272F05EC19041394568C949BBDBF012EE72C1595BE7157C4BB0324D0B5727`). `[VERIFIED]`
- Checkpoint loads under `strict=True` with 0 missing keys, 0 unexpected keys, 45/45 tensor shapes matching, 567,060 parameters. `[VERIFIED]`
- Layer naming divergence between checkpoint (`graph_conv_0`, `graph_conv.0..2`) and packaged class (`graph_conv_1..4`) is explained by training-time use of `nn.ModuleList`. Resolved by 1-to-1 prefix mapping outside the historical repo. `[VERIFIED]`

### Execution
- Original `ProteinNet` class instantiates and executes forward passes on both CPU and CUDA. `[VERIFIED]`
- Original `design_sequence` function executes through the repository data pipeline (`ProteinData → row_to_data → transform_edge_attr → Batch`). `[VERIFIED]`
- Iterative CSP design must run on CPU under PyTorch 2.6 due to cross-device indexing in `protein_design.py:224`. `[VERIFIED]`

### 1n5uA03 Result
- On target structure 1n5uA03 (92 AA), valid all-masked inverse-folding (MAP, seed-deterministic) achieves **41.30% native sequence identity** (38/92 residues) in **1.77 seconds**. `[VERIFIED]`
- This is classified as a **single-target all-masked inverse-folding integration result**. `[VERIFIED]`
- It is NOT benchmark accuracy, generalization accuracy, or full ProteinSolver benchmark reproduction. `[EXPLICIT LIMITATION]`

### Mask Invariance (EXP004)
- In the tested all-masked mask-invariance experiment (EXP004, `x = 20`, `y = None`), changing hidden/native labels produced a maximum absolute logit difference of 0.00000000e+00. `[VERIFIED]`
- Designed sequences under identical seeds are bitwise identical regardless of hidden labels. `[VERIFIED]`
- When `data.y` is supplied, `protein_design.py` copies reference labels via `strategy="ref"`, producing an information leak. This is NOT valid sequence recovery. `[VERIFIED]`

### Feature Pipeline
- On the tested target 1n5uA03, the original repo pipeline and the cleanroom Biopython extractor produce numerically identical tensors: `x equal: True`, `edge_index equal: True`, `edge_attr max diff: 0.0`. `[VERIFIED]`

---

## Current Baseline

| Property | Value |
| :--- | :--- |
| **Model** | ProteinSolver (historical `ProteinNet`, published checkpoint) |
| **Status** | FUNCTIONALLY REPRODUCED WITH MODERN COMPATIBILITY ADAPTATION |
| **Target Tested** | 1n5uA03 (CATH domain, 92 AA) |
| **Valid Recovery** | 41.30% (38/92, MAP, all-masked, deterministic) |
| **Environment** | Python 3.11.9, PyTorch 2.6.0+cu124, PyG 2.8.0.post1 |
| **Hardware** | NVIDIA GeForce RTX 3050 6GB Laptop GPU |
| **Compatibility Layer** | External (fcntl stub, kmtools stub, scatter_ shim, Batch wrapper, key mapping, CPU placement) |
| **Historical Source Modified** | NO — zero bytes changed in `external/proteinsolver-original/` |

---

## Known Limitations

1. **Historical runtime numerical equivalence: NOT TESTED.** We have not compared outputs against the original Python 3.6 / PyG 1.3 / Linux environment. Modern PyTorch 2.6 may produce numerically different floating-point results due to different kernel implementations.

2. **kmbio/Biopython parser equivalence: NOT GENERALLY VERIFIED.** The Biopython-based cleanroom extractor matches the original repo pipeline on the tested target 1n5uA03. Equivalence across all PDB structures (edge cases in alternate conformations, non-standard residues, multi-model PDBs) has not been tested.

3. **Training set membership for 1n5uA03: NOT VERIFIABLE FROM ACCESSIBLE METADATA.** The author's notebook checked `"1.10.246.10" in cath_ids` → `False`, but the full 72M training Parquet corpus is on an external cluster and not in git. We cannot independently confirm membership.

4. **Single target, not a benchmark.** 41.30% on one 92-residue CATH domain does not establish generalization performance. Published paper reports ~33-35% average across CATH 4.2 test superfamilies.

5. **CUDA iterative design not possible under PyTorch 2.6.** The `torch.arange` on line 224 of `protein_design.py` creates CPU tensors without `device=` parameter. CPU execution is fast enough (< 2s for 92 AA) but limits throughput for large-scale design.

6. **Obsolete kmbio dependency.** The historical PDB parsing pipeline (`kmtools` → `kmbio`) is non-functional on Python 3.11 / Windows. The model and design algorithms have zero functional dependency on `kmbio`.

7. **Upstream commit dating.** Commit `69ef0965` dates to December 2021 (post-publication). The paper was published October 2020. Whether this commit introduces post-publication changes relative to the exact paper submission state is unknown.

---

## Current Hypotheses

> **These are untested conjectures. They are NOT facts.**

1. **H-01:** ProteinSolver's distance-graph constraint-satisfaction scoring provides orthogonal structural signal that improves modern inverse-folding candidate selection.
2. **H-02:** A diversity-aware, multi-objective candidate selection framework can exploit model complementarity to improve the quality-diversity trade-off.
3. **H-03:** Rescoring ProteinMPNN-generated candidates using ProteinSolver CSP metrics enriches for candidates with higher AlphaFold self-consistency.

**Research question (two-sided):**  
*"Does ProteinSolver's distance-graph constraint-satisfaction scoring provide orthogonal structural signal that improves modern inverse-folding candidate selection, or does modern inverse folding combined with structural validation dominate hybrid selection?"*

---

### Protocol & Hyperparameter Optimization Framework
- Development optimization objective $J$ is frozen as the mean over $N_{\text{dev}} = 20$ CATH 4.2 validation targets of target-level mean fixed-correspondence scTM across the selected $M = 10$ library evaluated by AlphaFold2 (v2.3.2, monomodel weights `model_1_ptm`, single-sequence mode, no templates, 3 recycles, fp16 GPU, fixed inference seed = 42, Amber disabled). `[VERIFIED SPECIFICATION]`
- Development targets are frozen in immutable manifest `data/manifests/development_20_cath42.txt` (SHA-256: `47ab5fec66017b455f7eabee143dc83e99ec740640e945ed96752abb59483069`), derived deterministically from the canonical Ingraham/Dauparas CATH 4.2 validation split across 20 distinct CATH topologies. `[VERIFIED SPECIFICATION]`
- Development Infeasibility Rule ($J = -\infty$): Every configuration must produce $M=10$ unique viable candidates on ALL 20 development targets. If any target is `SELECTION_INFEASIBLE_LT_M`, the configuration receives $J = -\infty$ and is ineligible for argmax. If all configurations in an arm are infeasible, stop that tuning arm and classify the stage as `DEVELOPMENT_TUNING_STAGE_INFEASIBLE`. `[VERIFIED SPECIFICATION]`
- Screening oracle ESMFold is frozen: Meta AI `esm` v2.0.0 / Hugging Face `facebook/esmfold_v1`, `esmfold_v1` (3B parameters), sequence-only, 4 recycles, `fp16` GPU, max len 1024 with chunking, seed 42, operational screening cutoffs $\text{scRMSD}_{\text{screen}} \le 2.0\text{ \AA}$ and $\text{pLDDT}_{\text{screen}} \ge 80.0$. `[VERIFIED SPECIFICATION]`
- Development generation reuse (caching) is permitted and enforced: Candidate pools at temperature $T$ are generated once, screened once with ESMFold, and scored once, then reused across all $\gamma$ values (and across all 35 $(\lambda, \gamma)$ combinations for hybrid on $U_t$). `[VERIFIED SPECIFICATION]`
- Parameter selection searches complete Cartesian grids:
  - MPNN-only: $T_{\text{MPNN}} \times \gamma$ ($5 \times 5 = 25$ combinations). `[VERIFIED SPECIFICATION]`
  - ProteinSolver E0-B: $T_{\text{PS}} \times \gamma$ ($3 \times 5 = 15$ combinations). `[VERIFIED SPECIFICATION]`
  - Primary Hybrid: $\lambda \times \gamma$ ($7 \times 5 = 35$ combinations), with $T^*_{\text{hybrid}} = T^*_{\text{MPNN}}$ strictly enforced via Common Candidate Universe $U_t$. `[VERIFIED SPECIFICATION]`
- Selection order: 1. $(T^*_{\text{MPNN}}, \gamma^*_{\text{MPNN}})$ $\to$ 2. $(T^*_{\text{PS}}, \gamma^*_{\text{PS}})$ $\to$ 3. $(\lambda^*, \gamma^*_{\text{hybrid}})$ $\to$ 4. Freeze ALL parameters $\to$ 5. TS50 execution authorized. Ties resolved deterministically via ascending lexicographical grid order. `[VERIFIED SPECIFICATION]`

---

## Not Yet Tested

- Development hyperparameter selection execution ($K=100$ candidate generation, ESMFold screening, and AlphaFold2 validation across 20 dev targets)
- ProteinMPNN baseline benchmark execution on TS50 ($K=500$ at $T^*_{\text{MPNN}}$)
- Multi-target benchmark evaluation (TS50 / RFdiffusion de novo)
- Head-to-head comparison: ProteinSolver vs. ProteinMPNN on shared targets
- Complementarity analysis: whether ProteinSolver logits correlate with orthogonal biophysical properties
- Primary hybrid benchmark execution and candidate selection on TS50
- Statistical significance of any observed differences
- Training set membership of any benchmark target beyond 1n5uA03
- Historical runtime numerical equivalence (Python 3.6 / PyG 1.3)
- General kmbio/Biopython parser equivalence across diverse structures

