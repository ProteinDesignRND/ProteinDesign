# Phase 1: ProteinSolver Reproduction & Scientific Hardening Report

**Milestone**: E0-RUNTIME: COMPLETE | E0-SCIENTIFIC-HARDENING: COMPLETE  
**Status**: FUNCTIONALLY REPRODUCED WITH MODERN COMPATIBILITY ADAPTATION  
**Date**: September 24, 2026  
**Auditor**: Antigravity AI Research Agent  
**Reference Paper**: Strokach et al., *Fast and Flexible Protein Design Using Deep Graph Neural Networks*, Cell Systems 11, 402–411 (2020)  
**Primary Repository**: `external/proteinsolver-original` (Commit `69ef0965a3fc3bf191804035b539720a06e58ba6`)  
**Published Checkpoint**: `external/proteinsolver-original/data/e53-s1952148-d93703104.state` (SHA256: `1E8272F05EC19041394568C949BBDBF012EE72C1595BE7157C4BB0324D0B5727`)  
**Provenance Manifest**: [PROTEINSOLVER_PROVENANCE_MANIFEST.md](file:///d:/Projects/Protein%20Design/reports/PROTEINSOLVER_PROVENANCE_MANIFEST.md)  
**Execution Environment**: Windows AMD64, Python 3.11.9, PyTorch 2.6.0+cu124, PyG 2.8.0.post1, torch-scatter 2.1.2+pt26cu124, BioPython 1.88, NVIDIA GeForce RTX 3050 6GB Laptop GPU  

---

## 1. Executive Summary

This report establishes the forensic audit, execution verification, and scientific hardening pass for the historical ProteinSolver codebase (`external/proteinsolver-original`).

Key Hardened Findings:
1. **Historical Repository Cleanliness:** The historical repository working tree is 100% clean with zero source modifications (`69ef0965a3fc3bf191804035b539720a06e58ba6`).
2. **Strict Checkpoint Integrity:** The published checkpoint loads under `strict=True` semantics into `ProteinNet` with **0 missing keys, 0 unexpected keys, 45/45 tensor shapes matching**, and exactly **567,060 parameters** after prefix mapping (`graph_conv_0` $\to$ `graph_conv_1`, `graph_conv.0..2` $\to$ `graph_conv_2..4`).
3. **Single-Target Inverse-Folding Integration Result:** On target structure **1n5uA03 (92 AA)**, under a valid all-masked setup (`data.x = 20`, `data.y = None`), the original repository's CSP design pipeline generates sequence `MAGLDAFLAEAVARLSARFPGASAAELARLTALETLTRLCCAAGDAASCAACRARLAAYVCANQALLTADLAACCALPAAAIAACLAAVRRR` achieving **41.30% native sequence identity** (38/92 residues) in **1.77 seconds** (deterministic across identical seeds).
4. **Mask-Invariance Verified (EXP004):** The model is 100% mask-invariant on all-masked input. Evaluating two identical backbones with different hidden label sets produces a **max absolute logit difference of 0.00000000e+00** and bitwise-identical designed sequences. Supplying `data.y` triggers `strategy="ref"` in `protein_design.py`, copying the reference labels site-by-site (information leak).
5. **Feature Pipeline Equivalence (on tested target 1n5uA03):** Tensors extracted via the original repo pipeline (`ProteinData` $\to$ `row_to_data` $\to$ `transform_edge_attr` $\to$ `Batch`) match our cleanroom extractor identically: `x equal: True`, `edge_index equal: True`, `edge_attr max diff: 0.0`. General equivalence across all structures has NOT been verified.
6. **Target Provenance:** In notebook 16, the author checked `"1.10.246.10" in cath_ids`, which evaluated to `False`. However, because the full 72M training Parquet files are on the author's cluster and not bundled in git, exact training membership is formally classified as **not verifiable from accessible metadata**.
7. **Equivalence Claim:** ProteinSolver is **FUNCTIONALLY REPRODUCED WITH MODERN COMPATIBILITY ADAPTATION**. We refrain from asserting "100% mathematical fidelity" to historical environments until direct numerical comparison against a historical Python 3.6 / PyG 1.3 Linux stack is conducted.

---

## 2. Checkpoint Forensics & Strict Integrity

- **Status**: `[VERIFIED]`
- **Checkpoint File**: `external/proteinsolver-original/data/e53-s1952148-d93703104.state`
- **SHA-256**: `1E8272F05EC19041394568C949BBDBF012EE72C1595BE7157C4BB0324D0B5727`
- **Total Trainable Parameters**: Exactly **567,060**
- **Strict Verification Call**: `net.load_state_dict(mapped_state_dict, strict=True)`
- **Key Validation**:
  - Missing keys: `0` (`set()`)
  - Unexpected keys: `0` (`set()`)
  - Total tensors mapped: `45`
  - Tensor shapes: All 45 tensor shapes match the model architecture exactly.
- **Explanation of `graph_conv` Naming Mismatch**:
  The checkpoint was saved during training run `protein_train/191f05de/model.py`, in which the author implemented the GNN blocks using an `nn.ModuleList` named `graph_conv` (producing keys `graph_conv_0` for the input block, and `graph_conv.0`, `graph_conv.1`, `graph_conv.2` for subsequent blocks). When the code was refactored into `proteinsolver.models.proteinnet.ProteinNet`, the blocks were declared as separate attributes: `graph_conv_1`, `graph_conv_2`, `graph_conv_3`, `graph_conv_4`. A 1-to-1 prefix replacement reconciles this naming without altering tensor weights or architecture.

---

## 3. Mask-Invariance & Information Leak Audit (EXP004)

- **Status**: `[VERIFIED]`
- **Experiment Directory**: `experiments/EXP004_MASK_INVARIANCE/`
- **Objective**: Verify whether unmasking logits or generated sequences depend on hidden/native sequence labels when all positions are masked (`x = 20`), and demonstrate the mechanism of the earlier 100% recovery leak.

### Test 1: Single-Pass Logit Invariance
Two identical structure graphs of 1n5uA03 were constructed with different hidden label sets:
- **Set A**: Native sequence (`KFGERAFKAWAVARLSQRFPKAEFA...`, 92 AA)
- **Set B**: Synthetic poly-alanine (`AAAAAAAAAAAAAAAAAAAAAAAAA...`, 92 AA)
Both graphs had all node features set to mask token (`x = 20`) and `y = None`.

| Metric | Measured Value |
| :--- | :--- |
| **Max Absolute Logit Difference** | **0.00000000e+00** |
| **Logits 100% Identical** | **True** |

### Test 2: CSP Sequential Design Equality
Running `design_sequence(net, batch, value_selection_strategy="map")` under fixed seed (42):
- **Output Sequence A**: `MAGLDAFLAEAVARLSARFPGASAAELARLTALETLTRLCCAAGDAASCAACRARLAAYVCANQALLTADLAACCALPAAAIAACLAAVRRR`
- **Output Sequence B**: `MAGLDAFLAEAVARLSARFPGASAAELARLTALETLTRLCCAAGDAASCAACRARLAAYVCANQALLTADLAACCALPAAAIAACLAAVRRR`
- **Sequence Equality**: **True** (identical strings)
- **Max Probability Difference**: **0.00000000e+00**

### Test 3: Information Leak Demonstration
When `data.y` is provided on the input graph:
- With `data.y = labels_A` (Native) $\to$ Output sequence matches native: **True** (100% match)
- With `data.y = labels_B` (Poly-Ala) $\to$ Output sequence matches poly-Ala: **True** (100% match)

**Scientific Mechanism**:
In `proteinsolver/utils/protein_design.py` lines 148–176:
```python
x_ref = data.y if hasattr(data, 'y') and data.y is not None else data.x
mask_filled = (x_ref != 20) & (x == 20)
```
When `data.y` is populated, `mask_filled` is true for all residues, triggering `strategy="ref"` which copies `x_ref` directly into `x`. This is a diagnostic likelihood evaluation routine, not inverse-folding design. The valid inverse-folding setup requires `data.x = 20` and `data.y = None`.

---

## 4. Feature Pipeline Verification

- **Status**: `[VERIFIED]`
- **Original Pipeline**: `ProteinData` $\to$ `ps_protein.row_to_data` $\to$ `ps_protein.transform_edge_attr` $\to$ `Batch.from_data_list([data])`
- **Cleanroom Pipeline**: `src.proteinsolver_baseline.graph.extract_protein_graph(pdb_path)`
- **Comparison Results on 1n5uA03 (Chain A)**:

| Feature Tensor | Original Pipeline Shape | Cleanroom Pipeline Shape | Equality / Max Diff |
| :--- | :--- | :--- | :--- |
| **Node Features (`x`)** | `torch.Size([92])` | `torch.Size([92])` | `x equal: True` |
| **Edge Indices (`edge_index`)** | `torch.Size([2, 3494])` | `torch.Size([2, 3494])` | `edge_index equal: True` |
| **Edge Attributes (`edge_attr`)** | `torch.Size([3494, 2])` | `torch.Size([3494, 2])` | `max diff: 0.0` |
| **Batch Tensor (`batch`)** | `torch.Size([92])` | `torch.Size([92])` (if batched) | Values: `[0, ..., 0]` |

The feature extraction math is verified to be identical between both pipelines.

---

## 5. Target Contamination & Provenance Analysis (1n5uA03)

- **Status**: `not verifiable from accessible metadata`
- **Target Structure**: PDB `1n5u`, Chain `A`, Domain `03` (CATH domain `1n5uA03`, CATH classification: `1.10.246.10`).
- **Paper & Demo Context**:
  - `1n5uA03.pdb` is included directly in the historical repository as an illustrative design target in `notebooks/20_protein_demo.ipynb` and `notebooks/30_design_dashboard.ipynb`.
  - In `notebooks/18_profile_recovery.ipynb`, 1n5uA03 is one of 4 targets used to assess profile recovery and sequence similarity.
  - In the published paper (Strokach et al., Cell Systems 2020), 1N5U (serum albumin domain) is featured in Figure 4 and supplementary figures as an example of de novo design.
- **Training Set Membership Investigation**:
  - In `notebooks/16_protein_analysis_experimental.ipynb`, the author inspected training files on their cluster (`training_data_rs{rs}.parquet`) and checked:
    ```python
    "1.10.246.10" in cath_ids      # Output: False
    "1.10.246" in cath_topologies  # Output: False
    ```
  - While this suggests the author intended 1n5uA03 to be outside the training superfamilies, the full 72M training Parquet corpus is not part of the git repository (stored on external cluster storage).
  - Therefore, without downloading the multi-gigabyte dataset, exact training set membership cannot be independently verified from accessible metadata.
  - Classification: **not verifiable from accessible metadata**.

---

## 6. Single-Target Inverse-Folding Integration Result

The 41.30% result on 1n5uA03 is formally classified as a:
**"single-target all-masked inverse-folding integration result"**.

It is **NOT** classified as:
- Benchmark accuracy across protein folds
- Generalization performance
- Proof of reproduction of the 2020 benchmark across all 172 test superfamilies

### Result Summary
- **Target**: CATH domain `1n5uA03` (92 AA)
- **Initial State**: All 92 positions masked (`x = 20`, `y = None`)
- **Algorithm**: Original CSP iterative unmasking (`proteinsolver.utils.protein_design.design_sequence`, `strategy="map"`)
- **Native Sequence Identity**: **41.30%** (38/92 residues matched)
- **Runtime**: **1.7689 seconds** on CPU
- **Deterministic Repeatability**: Verified (100% bitwise-identical sequences across multiple runs)

---

## 7. Historical Equivalence Claim

**Formal Claim**:  
**FUNCTIONALLY REPRODUCED WITH MODERN COMPATIBILITY ADAPTATION**

We explicitly refrain from claiming "100% mathematical fidelity" to historical runtime environments, because numerical comparison against an original Python 3.6 / PyTorch 1.3 / PyG 1.3 Linux container has not been conducted. However, functional equivalence of the model architecture, checkpoint parameter values, edge featurization formulas, and CSP search algorithm is empirically demonstrated.

---

## 8. Milestone Label Status

- **E0-RUNTIME**: `COMPLETE`
- **E0-SCIENTIFIC-HARDENING**: `COMPLETE`
- **Next Phase**: Phase 2 (Comparative Evaluation Framework & ProteinMPNN Integration) will begin in the subsequent task.
