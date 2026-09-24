# BASELINE MODELS SPECIFICATION & BENCHMARK AUDIT

This document evaluates potential baseline models for the inverse folding and sequence design benchmark. The final benchmark set is subject to human decision and empirical validation in Phase 1.

---

## 1. Summary Comparison Table

| Model | Model Family | Input Representation | Decoding Method | Reported CATH 4.2 Recovery | Parameter Count | Include in Benchmark? |
|---|---|---|---|:---:|:---:|:---:|
| **ProteinSolver** | Residual EdgeConv GNN | Sparse distance matrix (<12 Å) | Iterative CSP Masked Sampling | ~32–35% | ~1.5M | **YES (Foundational Baseline)** |
| **ProteinMPNN** | Message Passing GNN | Backbone coords (N, CA, C, O) | Autoregressive (Random Order) | 51.6% | ~1.8M | **YES (Primary SOTA Baseline)** |
| **PiFold** | Dual-track PiGNN | Multi-scale residue featurization | Non-autoregressive (One-shot) | 51.7% | ~2.5M | **RECOMMENDED (Fast Non-AR Baseline)** |
| **ESM-IF1** | GVP-GNN + Transformer | Backbone coordinates | Autoregressive Transformer | 51.3% | ~142M | **OPTIONAL (Resource Dependent)** |
| **LigandMPNN** | Message Passing GNN | Backbone coords + Ligand atoms | Autoregressive | N/A (ligand-aware) | ~2.0M | **NO (Specialized for Small Molecules)** |
| **Rosetta (FixBB)** | Physics-based Energy Min. | All-atom / Backbone coords | Monte Carlo / Simulated Annealing | ~28–30% | N/A (physics) | **OPTIONAL (Reference Physics Baseline)** |

---

## 2. In-Depth Baseline Profiles

### A. Original ProteinSolver
- **Paper:** Strokach et al. (*Cell Systems* 2020).
- **Model Family:** Residual Graph Neural Network with edge convolutions.
- **Input:** Shortest Cartesian heavy-atom distance matrix ($d_{ij} < 12\text{ \AA}$) and sequence offset $|i - j|$.
- **Output:** Categorical distribution over 20 amino acids per position.
- **Strengths:** Lightweight, simple graph formulation; treats sequence design as constraint satisfaction; supports partial sequence inpainting naturally.
- **Limitations:** Substantially lower sequence recovery than modern baselines; lacks explicit 3D coordinate frame orientation features; slow iterative CSP decoding.
- **Compute Requirements:** Very low (<50 MB GPU RAM; runs effortlessly on CPU).
- **Benchmark Verdict:** **MANDATORY.** Essential parent baseline to evaluate any proposed extension or ensembling.

---

### B. ProteinMPNN
- **Paper:** Dauparas et al. (*Science* 2022).
- **Model Family:** Autoregressive Message Passing Neural Network.
- **Input:** 3D coordinates of N, CA, C, O backbone atoms; local coordinate frames and geometric invariant features (distances, angles).
- **Output:** Conditional amino acid probabilities conditioned on backbone geometry and previously decoded positions.
- **Strengths:** Gold-standard accuracy, high recovery (51.6%), robust to experimental backbone noise, extremely fast inference (<0.1s per sequence on GPU).
- **Limitations:** Suffers from low sequence diversity at low temperatures ($T=0.1$); does not optimize multi-objective criteria.
- **Compute Requirements:** Low (~200 MB GPU RAM).
- **Benchmark Verdict:** **MANDATORY.** Universally acknowledged primary state-of-the-art benchmark.

---

### C. PiFold
- **Paper:** Gao et al. (*ICLR* 2023).
- **Model Family:** PiGNN with 1D, 2D, and 3D residue featurizer.
- **Input:** 3D backbone coordinates.
- **Output:** Categorical amino acid probabilities predicted in parallel across all residues.
- **Strengths:** Matches ProteinMPNN sequence recovery (51.66%) while achieving 10–70x faster inference via non-autoregressive decoding; independent code in `ProteinInvBench`.
- **Limitations:** May miss higher-order epistatic co-occurrence constraints because all residues are predicted simultaneously.
- **Compute Requirements:** Low (~300 MB GPU RAM).
- **Benchmark Verdict:** **RECOMMENDED.** Provides a modern non-autoregressive counterpoint to ProteinMPNN's autoregressive mechanism.

---

### D. ESM-IF1
- **Paper:** Hsu et al. (*ICML* 2022).
- **Model Family:** Geometric Vector Perceptron (GVP) encoder + Transformer decoder.
- **Input:** Backbone coordinates.
- **Output:** Autoregressive sequence probabilities.
- **Strengths:** Pretrained on 12M AlphaFold structures; excellent zero-shot variant effect predictions.
- **Limitations:** Large model footprint (142M parameters); slow inference compared to ProteinMPNN; high memory usage.
- **Compute Requirements:** High (>4 GB GPU RAM).
- **Benchmark Verdict:** **OPTIONAL.** If local GPU resources allow, include as a high-capacity baseline; otherwise omit to prioritize turnaround speed.

---

### E. Rosetta FixBB (Fixed-Backbone Design)
- **Paper:** Kuhlman & Baker (*PNAS* 2000).
- **Model Family:** Physics-based Monte Carlo side-chain packing with Rosetta energy function (`ref2015`).
- **Input:** All-atom or backbone PDB coordinates.
- **Output:** Designed sequence and packed rotamer structure.
- **Strengths:** Grounded in physical chemistry; evaluates explicit steric clashes and hydrogen-bonding networks.
- **Limitations:** Very slow (several minutes per sequence); lower sequence recovery (~28–30%); requires proprietary/academic Rosetta installation.
- **Benchmark Verdict:** **EXCLUDE FROM CORE LOOP.** Can be used as a secondary scoring proxy on top selected candidates, but impractical for large candidate generation pools.
