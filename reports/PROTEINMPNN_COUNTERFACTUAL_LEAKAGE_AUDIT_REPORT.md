# PROTEINMPNN COUNTERFACTUAL LEAKAGE & INTEGRITY AUDIT REPORT

**Task ID:** `PROTEIN-DESIGN-PRE-E1-PROTEINMPNN-LEAKAGE-INTEGRITY-GATE-V1`  
**Date:** 2026-09-28  
**Classification:** TECHNICAL INTEGRATION / FORENSIC LEAKAGE AUDIT (NOT A SCIENTIFIC BENCHMARK RUN)  
**Status:** **PASSED**  

---

## 1. Executive Summary

This report documents the forensic conditioning-leakage audit of the cleanroom ProteinMPNN integration before authorizing the first E1 development benchmark.

The audit verified that the cleanroom ProteinMPNN integration exhibits **100% counterfactual native-sequence invariance**: altering or mutating the residue identity labels of the input structure (Native sequence vs. Poly-Alanine vs. Poly-Glycine) while maintaining identical backbone Cartesian 3D coordinates yields **100% identical sequence candidates** and **0.00e+00 numerical score difference**.

No label leakage exists. The integration is verified mathematically and empirically clean.

---

## 2. Official ProteinMPNN Conditioning Semantics

Inspection of the pinned upstream implementation ([`external/proteinmpnn/protein_mpnn_utils.py`](file:///d:/Projects/Protein%20Design/external/proteinmpnn/protein_mpnn_utils.py)) reveals how sequence conditioning is executed within `ProteinMPNN.sample`:

### A. Role of Key Tensors
1. **`X` (`[B, L, 4, 3]`):** Cartesian backbone coordinates for atoms $N, C\alpha, C, O$. Invariant geometric features (distances, orientations) are extracted via `ProteinFeatures`.
2. **`randn` (`[B, L]`):** Random Gaussian noise tensor drawn under PyTorch RNG. Dictates the residue decoding permutation order $\pi$ via:
   ```python
   decoding_order = torch.argsort((chain_mask + 0.0001) * (torch.abs(randn)))
   ```
3. **`chain_mask` (`[B, L]`):** Binary design mask (1.0 for residues to design/predict, 0.0 for fixed residues). In full de novo design, `chain_mask = 1.0` everywhere.
4. **`chain_M_pos` (`[B, L]`):** Per-residue designability mask (1.0 for designable positions).
5. **`S_true` (`[B, L]`):** Sequence tokens passed into `model.sample`.

### B. Official Control Flow and Potential Leak Mechanism
In the official implementation autoregressive decoding loop (lines 1143–1186 of `protein_mpnn_utils.py`), each position $t = \pi[t\_]$ is sampled:
```python
S_t = torch.multinomial(probs, 1)
S_true_gathered = torch.gather(S_true, 1, t[:, None])
S_t = (S_t * chain_mask_gathered + S_true_gathered * (1.0 - chain_mask_gathered)).long()
```
- **If `chain_mask_gathered == 0.0` (Fixed Position):** $S_t$ takes the label from `S_true_gathered` ($1.0 - 0.0 = 1.0$), and embeds it via `self.W_s(S_t)` into sequence context $h_S$, which conditions all subsequent autoregressive decoding steps.
- **If `chain_mask_gathered == 1.0` (Designed Position):** $S_t$ takes the newly sampled token ($S_t \times 1.0 + S_{\text{true}} \times 0.0 = S_t$).

### C. Cleanroom Isolation Guarantee
To guarantee absolute protection against label leakage regardless of mask configuration:
1. **In `src/proteinmpnn/coords.py` (`coords_to_proteinmpnn_batch`):** Native sequence strings from PDB metadata are discarded; only backbone coordinates are retained. The batch dictionary is populated with a dummy sequence (`"A" * L`) purely for dimensional padding.
2. **In `src/proteinmpnn/wrapper.py` (`ProteinMPNNWrapper.sample_candidates`):** The tensor supplied as `S_true` is explicitly initialized as all zeros:
   ```python
   S_blank = torch.zeros((1, seq_len), dtype=torch.long, device=self.device)
   ```
   Native sequence tokens NEVER enter `S`, NEVER enter `model.sample`, and NEVER condition generation.

---

## 3. Counterfactual Invariance Empirical Test

### A. Experimental Setup
- **Target Backbone:** `1n5uA03.pdb` (92 residues, CATH crystal structure, Chain A).
- **Backbone Coordinates:** Identical 3D atomic coordinates ($N, C\alpha, C, O$) across all runs.
- **Counterfactual Variants:**
  1. **Variant A (Native):** Original PDB containing native sequence labels (`KFGERAFKAWAVARLSQRFPKAEFA...`).
  2. **Variant B (Poly-Ala):** Every residue name in the PDB ATOM records mutated to `ALA` (`AAAAAAAAAAAAAAAAAAAAAAAAA...`).
  3. **Variant C (Poly-Gly):** Every residue name in the PDB ATOM records mutated to `GLY` (`GGGGGGGGGGGGGGGGGGGGGGGGG...`).
- **Inference Configuration:** Checkpoint `v_48_020` (0.20 Å noise, 48 edges), temperature $T = 0.2$, seed $S = 42$, device CPU, 3 candidates per condition.
- **Repetition:** Complete test repeated across multiple execution passes.

### B. Results & Numerical Differences

| Candidate Index | Native Label Sequence | Poly-Ala Label Sequence | Poly-Gly Label Sequence | String Match | Max Score Difference |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **0** | `HMGSEALRKALRKRLSKRFPSAS...` | `HMGSEALRKALRKRLSKRFPSAS...` | `HMGSEALRKALRKRLSKRFPSAS...` | **100% IDENTICAL** | **`0.00e+00`** |
| **1** | `ARGRAARRAELRRRLSARYPSAT...` | `ARGRAARRAELRRRLSARYPSAT...` | `ARGRAARRAELRRRLSARYPSAT...` | **100% IDENTICAL** | **`0.00e+00`** |
| **2** | `GSGPEALRARLREELTRRYPSAS...` | `GSGPEALRARLREELTRRYPSAS...` | `GSGPEALRARLREELTRRYPSAS...` | **100% IDENTICAL** | **`0.00e+00`** |

- **Candidate 0 Score:** `Native = -1.01528072`, `Poly-Ala = -1.01528072`, `Poly-Gly = -1.01528072` (Difference = `0.00000000e+00`).
- **Candidate 1 Score:** `Native = -1.00484860`, `Poly-Ala = -1.00484860`, `Poly-Gly = -1.00484860` (Difference = `0.00000000e+00`).
- **Candidate 2 Score:** `Native = -1.03126991`, `Poly-Ala = -1.03126991`, `Poly-Gly = -1.03126991` (Difference = `0.00000000e+00`).

### C. Direct Coordinate Array Verification
Supplying raw numpy coordinate arrays directly to `sample_candidates(coords, ...)` produces sequences and scores 100% identical to the PDB file inputs (`score difference: 0.00e+00`).

---

## 4. Scoring Semantics & Metric Decoupling

1. **Autoregressive Scoring:**
   $S_{\text{MPNN}}(u)$ evaluates the exact mean autoregressive log-probability over candidate $u$ along the designated permutation decoding order $\pi$:
   $$S_{\text{MPNN}}(u) = \frac{1}{L} \sum_{i=1}^L \log p(u_{\pi_i} \mid u_{\pi_{<i}}, \text{backbone})$$
   - Higher is better ($S_{\text{MPNN}}(u) \le 0.0$).
   - Perplexity is computed as $\text{PPL}_{\text{MPNN}}(u) = \exp(-S_{\text{MPNN}}(u)) \ge 1.0$.
2. **Separation from Generation:**
   Candidate generation samples $u$ from the generative model; sequence scoring subsequently evaluates $u$ conditionally. Native labels are never supplied as targets during candidate evaluation.
3. **Decoupling from ProteinSolver:**
   ProteinMPNN autoregressive perplexity is mathematically distinct from ProteinSolver single-site pseudo-perplexity. Both are retained strictly as model-specific internal diagnostics.

---

## 5. Automated Regression Verification

The complete repository regression suite was executed:
- **PyTest Suite:** **63 / 63 passed** in 17.27s (including new test [`test_counterfactual_native_sequence_invariance`](file:///d:/Projects/Protein%20Design/tests/test_proteinmpnn.py#L203-L241)).
- **Historical ProteinSolver Execution:** **All 6 steps passed** (567,060 parameters, MAP sequence recovery 41.30% [38/92] on 1n5uA03).
- **EXP004 Mask Invariance:** **Passed** (max logit diff = `0.00000000e+00`).
- **Governance Preflight CLI:** **Passed** (8 rules evaluated, 6 relevant, 0 conflicts).
- **Historical Repository Status:** `external/proteinsolver-original` is on branch `master`, **100% clean and untouched**.

---

## 6. Limitations & Scientific Firewall

- **Non-Benchmark Nature:** This audit is an integration verification test. It does NOT evaluate sequence recovery across benchmarks, scTM foldability, or design quality.
- **Scientific Firewall Compliance:**
  - **NO E1 benchmark was executed.**
  - **NO TS50 benchmark was executed.**
  - **NO $K=100$ development candidate pool was generated.**
  - **NO optimal temperature ($T^*$) was selected.**
  - **NO hyperparameter tuning was conducted.**
