# FINAL SCIENTIFIC PROTOCOL FREEZE & READINESS GATE REPORT
**Task ID:** `PROTEIN-DESIGN-SCIENTIFIC-PROTOCOL-FINALIZATION-V1`  
**Execution Agent:** Gemini 3.8 Flash High (Pair Programming via Antigravity IDE 2.0)  
**Date:** 2026-09-25  
**Working Branch:** `governance/final-acceptance-redteam-v1`  
**Governance Foundation Status:** `FOUNDATION_FROZEN_WITH_LIMITATIONS`  
**Study Pre-Registration:** [`science/PREREGISTRATION.md`](file:///d:/Projects/Protein%20Design/science/PREREGISTRATION.md)  
**Readiness Classification:** **`READY_FOR_PROTEINMPNN_INTEGRATION`**

---

## 1. Executive Summary & Git State

This report establishes the final, authoritative scientific-protocol freeze following the independent red-team audit by Claude Standalone 2.0. The audit identified methodological vulnerabilities across hybrid score formulation, selection leakage, validation oracle ambiguity, multiple testing endpoints, candidate budget accounting, and statistical pseudoreplication.

All identified vulnerabilities have been formally resolved, codified in cleanroom code (`src/hybrid/`), verified via 36 unit and integration tests, pre-registered in [`science/PREREGISTRATION.md`](file:///d:/Projects/Protein%20Design/science/PREREGISTRATION.md), and reconciled across project truth and decision documentation.

### Git State Verification
- **Current Branch:** `governance/final-acceptance-redteam-v1`
- **Current HEAD Commit:** `4d891f7093ae862a0451c09faba20f98282c9906` (prior to this freeze commit)
- **Base Integration Branch (`main`):** `e9b2c0e1e221a5ad7cbe3ab7017824befebc22cd` (100% untouched)
- **Merge Base (`main..HEAD`):** `e9b2c0e1e221a5ad7cbe3ab7017824befebc22cd`
- **Historical Clone (`external/proteinsolver-original`):** Clean on `master` at commit `69ef0965a3fc3bf191804035b539720a06e58ba6` (100% untouched, 0 untracked files).
- **Confirmation:** NO new test-set scientific experiments were run; NO parameters were tuned against test outcomes; NO historical sources were modified.

---

## 2. Claude Standalone 2.0 Red-Team Findings & Issue Disposition

| Issue # | Claude Red-Team Finding | Prior Repository State | Resolution & Frozen Disposition | Verification |
|---|---|---|---|:---:|
| **ISSUE-01** | Raw logit interpolation $z_{\text{hybrid}} = \lambda z_{\text{MPNN}} + (1-\lambda) z_{\text{PS}}$ is scientifically indefensible as a primary method due to scale/objective mismatch. | Listed as formulation #1 in E2 without scale normalization. | **RESOLVED:** Primary hybrid method defined and implemented as **scale-free within-pool percentile rank normalization** in `src/hybrid/scoring.py`. Raw logit interpolation demoted strictly to an exploratory ablation. | `test_percentile_rank_normalization_and_scale_invariance`, `test_primary_hybrid_score_calculation` |
| **ISSUE-02** | Selection objective $f_4(u)$ depended on evolving candidate subset $S'$, conflating a greedy construction heuristic with an order-independent candidate metric. | $f_4$ in Pareto HV was defined as distance to current evolving library. | **RESOLVED:** Separated into two stages: Stage 1 (Hard viability gate $\text{scRMSD} \le 2.0\text{ \AA} \land \text{pLDDT} \ge 80$) $\to$ Stage 2 (Greedy diversity selection heuristic). Evolving greedy score is explicitly labeled as a construction heuristic; reported diversity is strictly order-independent pairwise Hamming distance. | `test_two_stage_candidate_selection`, `test_order_independent_pairwise_diversity` |
| **ISSUE-03** | Structural validation oracle was ambiguously specified as "AlphaFold2 OR Boltz-1", allowing post-hoc oracle switching. | Stated as "AlphaFold2 or Boltz-1" in evaluation documents. | **RESOLVED:** Formally froze **AlphaFold2 (v2.3.2, monomodel weights `model_1_ptm`, 3 recycles, no templates, single sequence mode, fp16/bf16 on GPU)** as the single Primary Final Validation Oracle. Boltz-1 designated strictly for sensitivity analysis. | [`science/PREREGISTRATION.md`](file:///d:/Projects/Protein%20Design/science/PREREGISTRATION.md#L102-L115) |
| **ISSUE-04** | Operational screening thresholds ($\text{scRMSD} \le 2.0\text{ \AA}, \text{pLDDT} \ge 80$) risked being mislabeled as "canonical" without explicit provenance. | Labeled as "canonical" in older drafts, partially reclassified in V2. | **RESOLVED:** Formally classified and frozen as **project-chosen operational screening thresholds** informed by standard literature conventions (Watson et al. 2023, Dauparas et al. 2022). | [`science/PREREGISTRATION.md`](file:///d:/Projects/Protein%20Design/science/PREREGISTRATION.md#L94-L100) |
| **ISSUE-05** | Lack of a single pre-registered primary endpoint created p-hacking risk across multiple evaluation metrics. | Multiple metrics listed in E0–E4 without declaring a primary success criterion. | **RESOLVED:** Established **EXACTLY ONE PRIMARY ENDPOINT**: Target-level mean fixed-correspondence Self-Consistency TM-score ($\overline{\text{scTM}}_{\text{val}}$) across the $M=10$ selected library, evaluated by AlphaFold2. All other metrics designated as secondary, exploratory, or diagnostic. | [`science/PREREGISTRATION.md`](file:///d:/Projects/Protein%20Design/science/PREREGISTRATION.md#L15-L27) |
| **ISSUE-06** | Unit of statistical analysis was ambiguous, risking candidate-level pseudoreplication ($N=500$ vs $N=50$). | Aggregation was partially described at the candidate level. | **RESOLVED:** Unit of statistical analysis is strictly the **TARGET / BACKBONE** ($N=50$ TS50 targets). Paired difference $d_t = \overline{\text{scTM}}_{\text{hybrid}}(t) - \overline{\text{scTM}}_{\text{MPNN}}(t)$ evaluated via two-sided paired Wilcoxon signed-rank test ($\alpha = 0.01$). | `test_target_level_paired_difference`, [`science/PREREGISTRATION.md`](file:///d:/Projects/Protein%20Design/science/PREREGISTRATION.md#L30-L45) |
| **ISSUE-07** | Candidate budget $K$ was ambiguous across sweeps and models; historical E0 integration result was conflated with stochastic baseline. | Single $K=100$ pool mentioned alongside historical 1n5uA03 MAP run. | **RESOLVED:** $K$ defined strictly as total candidates generated **per target per method**. Matched budget rule enforced ($K=100$ tuning, $K=500$ primary test). Split E0 into E0-A (deterministic control, 41.30%) and E0-B (stochastic baseline). | `test_matched_budget_bookkeeping`, `test_e0_split_separation` |
| **ISSUE-08** | Net charge at pH 7.4 was conflated with isoelectric point (pI); standard TM-score name was used for fixed-correspondence scTM. | Metrics table had "Isoelectric Point (pI)" calculated at pH 7.4. | **RESOLVED:** Renamed and decoupled: Net Charge at pH 7.4 ($Q_{\text{pH7.4}}$) is distinct from pI ($Q=0$). TM-score explicitly designated as Fixed-Correspondence Self-Consistency TM-score (scTM). | `test_net_charge_at_ph74_vs_pi_naming`, `test_fixed_correspondence_sctm` |
| **ISSUE-09** | Targets risked being labeled as generic "held-out" without model-specific training provenance; RFdiffusion backbones risked being called "homology-free". | High-level leakage prevention rules lacked model-specific provenance fields. | **RESOLVED:** Model-specific training status mandated (Gene3D for ProteinSolver, CATH 4.2 for ProteinMPNN). RFdiffusion scaffolds described neutrally as "RFdiffusion-generated de novo backbones" (not homology-free without explicit search). | [`science/PREREGISTRATION.md`](file:///d:/Projects/Protein%20Design/science/PREREGISTRATION.md#L140-L155) |
| **ISSUE-10** | Risk of selective reporting of secondary baselines (PiFold, ESM-IF1) if they outperformed or underperformed the hybrid. | Baseline inclusion was listed as optional/resource-dependent. | **RESOLVED:** Mandated protocol rule: *"Secondary baselines and exploratory analyses are reported regardless of outcome. No baseline or model variant may be omitted based on negative or unfavorable results."* | [`science/PREREGISTRATION.md`](file:///d:/Projects/Protein%20Design/science/PREREGISTRATION.md#L165-L172) |
| **ISSUE-11** | Latency comparisons lacked standardization across hardware, warmup, and batching regimes. | General timing described without batching caveats. | **RESOLVED:** Codified standardized latency protocol: fixed GPU/CPU, FP16/FP32, batch size 1 vs 32, 5 warmup sequences, CUDA sync, model loading excluded as initialization overhead. | [`science/PREREGISTRATION.md`](file:///d:/Projects/Protein%20Design/science/PREREGISTRATION.md#L174-L185) |
| **ISSUE-12** | Hypervolume normalization bounds derived from test pools created outcome leakage. | HV formulation mentioned min-max scaling across candidate pools. | **RESOLVED:** Demoted HV to an exploratory descriptive analysis; mandated pre-declared external normalization bounds and an a priori fixed reference point $\mathbf{r} = (0.0, 0.0, 0.0)$. | [`science/PREREGISTRATION.md`](file:///d:/Projects/Protein%20Design/science/PREREGISTRATION.md#L130-L138) |

---

## 3. Files Created and Modified

1. **`src/hybrid/__init__.py`** (New): Exposes hybrid scoring and selection APIs.
2. **`src/hybrid/scoring.py`** (New): Implements scale-free within-pool percentile ranking, primary hybrid score $H = \lambda p_{\text{MPNN}} + (1-\lambda) p_{\text{PS}}$, and exploratory logit ablation.
3. **`src/hybrid/selection.py`** (New): Implements Stage 1 hard viability gate, Stage 2 greedy selection heuristic, order-independent Hamming diversity, fixed-correspondence scTM, Net Charge at pH 7.4, and hydrophobic core fraction.
4. **`tests/test_scientific_protocol.py`** (New): 11 comprehensive unit test suites (covering all protocol components).
5. **`science/PREREGISTRATION.md`** (New): Formal pre-registration specification freezing all 24 study parameters.
6. **`science/metrics.md`** (Updated): Aligned all mathematical equations, primary endpoint definition, decoupled perplexities, and biophysical proxy naming.
7. **`science/evaluation_protocol.md`** (Updated): Updated matrix diagram, E0-A/E0-B split, primary hybrid formulation, primary validation oracle, and target-level statistics.
8. **`DECISION_LOG.md`** (Updated): Appended `[DEC-012]` logging the scientific protocol pre-registration and design freeze.
9. **`PROJECT_STATE.md`** (Updated): Logged completion of Milestone 2.7.
10. **`reports/REPORT_INDEX.md`** (Updated): Registered the pre-registration specification and this readiness gate report.
11. **`reports/AG_LIVE_PROGRESS.md`** & **`reports/AG_RUN_STATE.json`** (Updated): Live execution tracking updated to COMPLETE.

---

## 4. Verification Test Results

### Test Execution Summary
- **Pytest Discovery Suite:**
  - Command: `uv run --python environment/proteinsolver-original/Scripts/python.exe pytest tests/ -v`
  - Output: **36 passed in 2.65s** (25 governance test suites + 11 scientific protocol test suites).
- **Direct Governance Test Runner:**
  - Command: `environment/proteinsolver-original/Scripts/python.exe tests/test_governance.py`
  - Output: **109/109 assertions passed, 0 failed**.
- **Historical Baseline Verification Suite:**
  - Command: `environment/proteinsolver-original/Scripts/python.exe test_original_execution.py`
  - Output: **All 6 steps passed**. Clean historical execution, 0 missing/unexpected keys, 1n5uA03 41.30% recovery in 1.73s.
- **Mask Invariance & Information Leak Audit:**
  - Command: `environment/proteinsolver-original/Scripts/python.exe experiments/EXP004_MASK_INVARIANCE/run_mask_invariance.py`
  - Output: **Passed**. Max absolute logit difference = `0.00000000e+00`.
- **Governance Preflight CLI:**
  - Command: `environment/proteinsolver-original/Scripts/python.exe governance/preflight_cli.py --model-family proteinsolver --stage evaluation`
  - Output: **`PREFLIGHT PASSED`**. 8 rules evaluated, 0 unreviewed matches, 0 conflicts.
- **Historical Clone Integrity:**
  - Command: `git -C external/proteinsolver-original status`
  - Output: **Clean on `master` at commit `69ef0965a3fc3bf191804035b539720a06e58ba6`**.

---

## 5. Frozen Scientific Protocol Decisions

1. **Research Question:** Strictly two-sided. No superiority assumed.
2. **Primary Hybrid Method:** Scale-free within-pool percentile rank normalization ($H(u) = \lambda p_{\text{MPNN}}(u) + (1-\lambda) p_{\text{PS}}(u)$).
3. **Exploratory Ablation:** Raw logit interpolation is categorized strictly as an exploratory ablation.
4. **Primary Validation Oracle:** **AlphaFold2 (v2.3.2)**, single sequence mode, 3 recycles, FP16/BF16.
5. **Sensitivity Oracle:** **Boltz-1 (v0.4.1)**.
6. **Primary Study Endpoint:** Target-level mean fixed-correspondence Self-Consistency TM-score ($\overline{\text{scTM}}_{\text{val}}$) across the $M=10$ selected library, evaluated by AlphaFold2.
7. **Unit of Statistical Analysis:** **TARGET / BACKBONE** ($N = 50$ TS50 targets) evaluated via two-sided paired Wilcoxon signed-rank test ($\alpha = 0.01$).
8. **Candidate Budgets:** Matched generation budget $K$ ($K=100$ tuning, $K=500$ primary test) per target per method.
9. **Two-Stage Selection:** Stage 1 Hard Viability Gate ($\text{scRMSD} \le 2.0\text{ \AA} \land \text{pLDDT} \ge 80$) $\to$ Stage 2 Greedy Diversity-Aware Selection Heuristic ($M=10$).
10. **Hyperparameter Freezing:** Mixing weight $\lambda$ is tuned strictly on the development split (CATH 4.2 validation) and frozen before test evaluation.
11. **Secondary Baseline Policy:** All secondary baselines (PiFold, ESM-IF1) and exploratory analyses are reported regardless of outcome.

---

## 6. Known Intentional Limitations

1. **In Silico Proxy Nature:** Structural folding oracles (ESMFold, AlphaFold2, Boltz-1) provide in silico self-consistency models, not direct in vitro measurements of free energy of folding ($\Delta G$), thermodynamic stability, or experimental solubility.
2. **Single-Target Integration Scope:** Current empirical recovery data is strictly limited to the 1n5uA03 integration control (41.30% recovery, 38/92 residues). Multi-target evaluation will begin only in Phase 2.
3. **Corpus Unverifiability:** Training set membership of 1n5uA03 in the 72M Gene3D corpus remains *not verifiable from accessible metadata* without downloading the full external multi-terabyte dataset.
4. **Perplexity Asymmetry:** ProteinSolver masked pseudo-perplexity and ProteinMPNN autoregressive perplexity cannot be numerically compared across models and remain separate internal diagnostics.

---

## 7. Final Readiness Classification & Authorization

### Classification: **`READY_FOR_PROTEINMPNN_INTEGRATION`**

All 12 issues identified by the Claude Standalone 2.0 red-team review have been resolved, codified, tested, and pre-registered. No scientific-protocol defects, tautological metrics, circular oracle evaluations, or statistical pseudoreplications remain.

### Exact Next Phase:
**Phase 2 / Milestone 3: ProteinMPNN Integration & Baseline Verification**  
- **Track:** `Workstream B` (Modern Inverse-Folding Baselines)  
- **Action:** Integrate official ProteinMPNN repository into cleanroom environment, verify forward pass and autoregressive decoding on shared benchmark structures (including the 1n5uA03 control), and establish the standard baseline sequence recovery before initiating hybrid ensembling (E2).
