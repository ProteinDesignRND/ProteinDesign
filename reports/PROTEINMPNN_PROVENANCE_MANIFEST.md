# PROTEINMPNN PROVENANCE AND CLEANROOM INTEGRATION MANIFEST

**Document Version:** 1.0.0  
**Date:** 2026-09-28  
**Task ID:** `PROTEIN-DESIGN-PHASE2-PROTEINMPNN-CLEANROOM-INTEGRATION-V1`  
**Classification:** TECHNICAL INTEGRATION / SMOKE TESTS ONLY (NOT A SCIENTIFIC BENCHMARK RUN)  
**Status:** COMPLETE  

---

## 1. Executive Summary

This manifest documents the cleanroom integration and technical verification of the official ProteinMPNN model implementation into the Protein Design / ProteinSolver Research Extension repository.

- **Upstream Source:** Official repository by Dauparas et al. (Science 2022).
- **Integration Boundary:** Managed external clone in `external/proteinmpnn/` pinned to commit `8907e6671bfbfc92303b5f79c4b5e6ce47cdef57`.
- **Cleanroom Wrapper:** Implemented in `src/proteinmpnn/` (`wrapper.py`, `coords.py`, `provenance.py`, `__init__.py`).
- **Cryptographic Verification:** SHA-256 verification passed for all official vanilla model checkpoints.
- **Historical Repository Integrity:** `external/proteinsolver-original` remains 100% clean and untouched (commit `69ef0965a3fc3bf191804035b539720a06e58ba6`).
- **Scientific Firewall:** ZERO scientific benchmark experiments were executed (No E1, No TS50, No K=100 development sweeps, No parameter tuning).

---

## 2. Upstream Source & Provenance

| Parameter | Value |
| :--- | :--- |
| **Upstream Repository URL** | `https://github.com/dauparas/ProteinMPNN` |
| **Canonical Citation** | Dauparas et al., *Robust deep learning based protein sequence design using ProteinMPNN*, Science 378(6615): 49–56 (2022). DOI: `10.1126/science.add2187` |
| **Upstream Commit SHA** | `8907e6671bfbfc92303b5f79c4b5e6ce47cdef57` |
| **Upstream Commit Date** | `2023-06-27` |
| **Clone / Integration Date**| `2026-09-28` |
| **License** | MIT License (Copyright (c) 2022 Justas Dauparas) |
| **Local Path** | `external/proteinmpnn/` |

---

## 3. Model Weights & Cryptographic Verification

All official vanilla model checkpoints in `external/proteinmpnn/vanilla_model_weights/` have been cryptographically verified against their SHA-256 hashes:

| Checkpoint Name | Relative Path | Parameters / Edges | Noise Level | SHA-256 Hash | Integrity Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **v_48_020 (Default)** | `external/proteinmpnn/vanilla_model_weights/v_48_020.pt` | $K=48$ edges, 3 layers | 0.20 Å | `C9CB4A671D79604111231F8DBFC7C590E06F1197453B7A6854AC6661A642F5BD` | **VERIFIED MATCH** |
| **v_48_010** | `external/proteinmpnn/vanilla_model_weights/v_48_010.pt` | $K=48$ edges, 3 layers | 0.10 Å | `DB866FAE956A28661F926053D630610C55E9FC4BC03922F2AEEB98A37435CCCE` | **VERIFIED MATCH** |
| **v_48_002** | `external/proteinmpnn/vanilla_model_weights/v_48_002.pt` | $K=48$ edges, 3 layers | 0.02 Å | `925F2CA1007BF9B02E0E7F420FF00EB91F50FCC2722F64B42E644AE95ADAA131` | **VERIFIED MATCH** |
| **v_48_030** | `external/proteinmpnn/vanilla_model_weights/v_48_030.pt` | $K=48$ edges, 3 layers | 0.30 Å | `C34B7BFB38418EA30989FDA3314F4781AC4E3920F9825731CF555F1FED44AC66` | **VERIFIED MATCH** |

### Checkpoint Selection Decision Record
- **Default Baseline Model:** `v_48_020` is the default model of the official ProteinMPNN repository and the standard baseline in Dauparas et al. 2022 for de novo backbone sequence generation.
- **Configurability:** The cleanroom wrapper (`ProteinMPNNWrapper`) explicitly supports loading any official vanilla checkpoint via the `model_name` parameter without silent substitution.

---

## 4. Cleanroom Architecture & Integration Components

The integration is encapsulated in `src/proteinmpnn/` with zero modifications to the historical `external/proteinsolver-original` codebase:

1. **`src/proteinmpnn/wrapper.py` (`ProteinMPNNWrapper`):**
   - Explicit model loading with SHA-256 verification and device management (`cpu` / `cuda`).
   - Zero-leakage conditioning: passes `S_blank = torch.zeros((1, L))` to `model.sample` so native target sequence is NEVER supplied as conditioning input.
   - Deterministic candidate generation under seeded PyTorch RNG:
     - Sets `torch.manual_seed(seed)` and `np.random.seed(seed)`.
     - Draws residue permutation tensor `randn = torch.randn(chain_M.shape, device=device)`.
     - Samples sequences at specified `temperature`.
     - Computes sequence-level mean autoregressive log-probability ($S_{\text{MPNN}}(u)$).
     - Computes diagnostic autoregressive perplexity ($\text{PPL}_{\text{MPNN}}(u) = \exp(-S_{\text{MPNN}}(u))$).
     - Formats reproducible candidate ID using `src.hybrid.budget.generate_candidate_id`.
     - Returns `src.hybrid.selection.Candidate` records directly compatible with downstream hybrid scoring and selection.

2. **`src/proteinmpnn/coords.py`:**
   - `extract_backbone_coordinates`: BioPython PDB parser extracting 4 backbone atoms (N, CA, C, O) in standard order into `[L, 4, 3]` arrays.
   - `validate_backbone_coordinates`: Numerical integrity checks (shape, NaN, Inf, non-zero length).
   - `coords_to_proteinmpnn_batch`: Converts coordinates to official `tied_featurize` batch dictionaries.

3. **`src/proteinmpnn/provenance.py`:**
   - Manifest data structures and automated SHA-256 verification functions.

---

## 5. Technical Smoke Tests & Verification Results

All tests executed are strictly non-benchmark technical integration checks:

| Test ID | Test Description | Command / Assertion | Result |
| :--- | :--- | :--- | :--- |
| **SMOKE-01** | Model Import | `from src.proteinmpnn import ProteinMPNNWrapper` | **PASS** |
| **SMOKE-02** | Checkpoint Load & Integrity | `verify_checkpoint_integrity(model_name='v_48_020')` | **PASS** |
| **SMOKE-03** | Synthetic Coordinate Forward Pass | Forward pass with $L=25$ random coordinates | **PASS** |
| **SMOKE-04** | PDB Coordinate Extraction | Parse `1n5uA03.pdb` into shape `(92, 4, 3)` | **PASS** |
| **SMOKE-05** | Candidate Generation Smoke | Sample 2 candidates on `1n5uA03` ($T=0.1, \text{seed}=42$) | **PASS** |
| **SMOKE-06** | Expected Sequence Length | Length = 92 matching target backbone | **PASS** |
| **SMOKE-07** | Standard 20-AA Alphabet | Output sequence characters in `ACDEFGHIKLMNPQRSTVWY` | **PASS** |
| **SMOKE-08** | Candidate ID Determinism | ID matches `{target}_{arm}_T{T}_s{seed}_idx{idx:04d}` | **PASS** |
| **SMOKE-09** | Seed Reproducibility | Identical candidates for seed 1337 run twice | **PASS** |
| **SMOKE-10** | Stochastic Divergence | Different candidates for seed 42 vs seed 2026 | **PASS** |
| **SMOKE-11** | Zero Label Leakage | Conditioning uses blank sequence; recovery is 40–65%, not 100% | **PASS** |
| **SMOKE-12** | Score Direction | Higher mean log-prob = better ($\le 0$); perplexity $\ge 1.0$ | **PASS** |
| **SMOKE-13** | Hybrid Pipeline Interoperability | Candidates feed into `score_common_candidate_universe`, `compute_mpnn_only_selection_score`, and `select_diverse_library` | **PASS** |

---

## 6. Regression & Governance Test Results

- **Complete PyTest Suite:** **62 / 62 passed** in 10.57s.
  - `tests/test_governance.py`: 25 passed (109 assertions).
  - `tests/test_proteinmpnn.py`: 10 passed.
  - `tests/test_scientific_protocol.py`: 27 passed.
- **Historical ProteinSolver Execution:**
  - `python test_original_execution.py`: **ALL 6 STEPS PASSED** (567,060 params, MAP recovery 41.30% on 1n5uA03).
- **EXP004 Mask Invariance:**
  - `python experiments/EXP004_MASK_INVARIANCE/run_mask_invariance.py`: **PASSED** (max logit diff = 0.00000000e+00).
- **Governance Preflight:**
  - `python -m governance.preflight_cli`: **PASSED** (Coverage: 8 evaluated, 6 relevant, 0 conflicts).
- **Historical Repository Status:**
  - `git -C external/proteinsolver-original status`: **CLEAN & UNTOUCHED** on `master`.

---

## 7. Scientific Firewall Compliance

The following activities were **STRICTLY NOT EXECUTED** in this run:
- [x] No E1 benchmark experiment executed.
- [x] No TS50 benchmark experiment executed.
- [x] No K=100 development benchmark candidate pool generated.
- [x] No optimal temperature ($T^*$) selected.
- [x] No mixing parameter ($\lambda$) tuned.
- [x] No diversity weight ($\gamma$) tuned.
- [x] No primary endpoint evaluated.
- [x] No AlphaFold2 benchmark validation executed.
- [x] No test-set outcome inspected for protocol optimization.
- [x] No frozen protocol document scientifically altered.

---

## 8. Summary & Next Steps

The official ProteinMPNN model is technically integrated, verified, and ready for baseline execution under the frozen scientific protocol.

**Next Step:** Milestone 3 baseline execution (controlled non-benchmark calibration and readiness for E1 baseline runs per `science/evaluation_protocol.md`).
