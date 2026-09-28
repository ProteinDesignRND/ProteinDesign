# FINAL SCIENTIFIC PROTOCOL FREEZE & READINESS GATE REPORT (V3 CLOSURE)
**Task ID:** `PROTEIN-DESIGN-FINAL-SCIENTIFIC-CONSISTENCY-CLOSURE-V3`  
**Execution Agent:** Gemini 3.8 Flash High (Pair Programming via Antigravity IDE 2.0)  
**Date:** 2026-09-28  
**Working Branch:** `governance/final-acceptance-redteam-v1`  
**Governance Foundation Status:** `FOUNDATION_FROZEN_WITH_LIMITATIONS`  
**Study Pre-Registration:** [`science/PREREGISTRATION.md`](file:///d:/Projects/Protein%20Design/science/PREREGISTRATION.md)  
**Decision Record:** [`DECISION_LOG.md#dec-014`](file:///d:/Projects/Protein%20Design/DECISION_LOG.md)  
**Readiness Classification:** **`READY_FOR_PROTEINMPNN_INTEGRATION`**

---

## 1. Executive Summary & Git State

This report establishes the final, authoritative protocol-consistency closure prior to the start of ProteinMPNN experimentation. Independent review evidence from Claude Standalone 2.0, prior Perplexity review, and ChatGPT synthesis identified residual researcher degrees of freedom across development temperature allocation, selection score normalization, diversity grid bounds, greedy heuristic initialization, tie breaking, duplicate accounting, candidate pool infeasibility, and statistical bootstrap semantics.

All remaining degrees of freedom have been rigorously resolved, codified in cleanroom code (`src/hybrid/`), verified via 52 automated tests (25 governance + 27 scientific protocol), pre-registered in [`science/PREREGISTRATION.md`](file:///d:/Projects/Protein%20Design/science/PREREGISTRATION.md), and cross-referenced in [`DECISION_LOG.md`](file:///d:/Projects/Protein%20Design/DECISION_LOG.md#dec-014) and [`PROJECT_STATE.md`](file:///d:/Projects/Protein%20Design/PROJECT_STATE.md).

### Git State Verification
- **Current Working Branch:** `governance/final-acceptance-redteam-v1`
- **Current HEAD Commit:** `efc8fc6623ae011f3a9450c14a8b48feb57d362b` (prior to this closure commit)
- **Base Integration Branch (`main`):** `e9b2c0e1e221a5ad7cbe3ab7017824befebc22cd` (100% untouched)
- **Merge Base (`main..HEAD`):** `e9b2c0e1e221a5ad7cbe3ab7017824befebc22cd`
- **Historical Clone (`external/proteinsolver-original`):** Clean on `master` at commit `69ef0965a3fc3bf191804035b539720a06e58ba6` (100% untouched, 0 untracked files).
- **Absolute Scope & Boundary Confirmation:**
  - This project is strictly **Protein Design / ProteinSolver Research Extension**.
  - Zero Ocean Sentinel artifacts, code, or terminology are present or imported.
  - **NO ProteinMPNN benchmark science was executed.**
  - **NO TS50 benchmark evaluations were performed.**
  - **NO E2–E5 benchmark experiments were run.**
  - **NO test outcomes were inspected to tune protocol parameters.**
  - **NO historical ProteinSolver source was modified.**

---

## 2. Issue Disposition Matrix (V1–V3 Closure)

| Issue # | Area / Finding | Prior Repository State | Resolution & Frozen Disposition | Verification Check |
|---|---|---|---|:---:|
| **ISSUE-01** | Raw logit interpolation scale mismatch | Listed as primary option in E2 without normalization. | **RESOLVED:** Primary hybrid method defined as **scale-free within-pool percentile rank normalization** ($H = \lambda p_{\text{MPNN}} + (1-\lambda) p_{\text{PS}}$) in `src/hybrid/scoring.py`. Raw logit interpolation demoted strictly to exploratory ablation. | `test_percentile_rank_normalization_and_scale_invariance`, `test_primary_hybrid_score_calculation` |
| **ISSUE-02** | Selection metric order dependence | Greedy score evaluated against evolving subset was described as candidate metric. | **RESOLVED:** Two-stage framework codified: Stage 1 Hard Viability Gate $\to$ Stage 2 Greedy Diversity Heuristic. Greedy score is explicitly labeled as a construction heuristic; reported diversity is strictly order-independent pairwise Hamming distance. | `test_two_stage_candidate_selection`, `test_order_independent_pairwise_diversity` |
| **ISSUE-03** | Structural oracle ambiguity | Specified as "AlphaFold2 OR Boltz-1"; precision as "FP16/BF16". | **RESOLVED:** Formally froze **AlphaFold2 (v2.3.2, monomodel weights `model_1_ptm`, 3 recycles, single-sequence mode, no templates, float16 / fp16 on GPU, seed 42)** as the singular Primary Final Validation Oracle. Boltz-1 designated strictly for sensitivity analysis. | `test_primary_alphafold2_exact_configuration` |
| **ISSUE-04** | Screening threshold provenance | Thresholds labeled as "canonical". | **RESOLVED:** Classified and frozen as **project-chosen operational screening thresholds** ($\text{scRMSD} \le 2.0\text{ \AA}, \text{pLDDT} \ge 80.0$) informed by standard literature conventions. | [`science/PREREGISTRATION.md#11`](file:///d:/Projects/Protein%20Design/science/PREREGISTRATION.md#11) |
| **ISSUE-05** | Multiple testing endpoints | Multiple metrics listed in E0–E4 without declared primary endpoint. | **RESOLVED:** Established **EXACTLY ONE PRIMARY ENDPOINT**: Target-level mean fixed-correspondence scTM ($\overline{\text{scTM}}_{\text{val}}$) across the $M=10$ selected library, evaluated by AlphaFold2. | [`science/PREREGISTRATION.md#2`](file:///d:/Projects/Protein%20Design/science/PREREGISTRATION.md#2) |
| **ISSUE-06** | Statistical pseudoreplication | Aggregation partially described at candidate level ($N=500$). | **RESOLVED:** Unit of statistical analysis is strictly the **TARGET / BACKBONE** ($N=50$). Paired difference $d_t = \overline{\text{scTM}}_{\text{hybrid}}(t) - \overline{\text{scTM}}_{\text{MPNN}}(t)$ evaluated via two-sided paired Wilcoxon signed-rank test ($\alpha = 0.01$). | `test_target_level_paired_difference` |
| **ISSUE-07** | Candidate budget ambiguity & Common Universe | Ambiguous "per condition" wording; unverified candidate universe. | **RESOLVED:** Formally froze **Interpretation A**: $K$ is the **TOTAL candidate sequences generated PER TARGET PER METHOD/ARM across all temperatures and seeds** ($K=500$ primary test). Primary Hybrid evaluates the **Common Candidate Universe** ($U_t$, $|U_t|=500$) scored by both models. E0 split into E0-A (deterministic control, 41.30%) and E0-B (stochastic baseline). | `test_candidate_budget_unambiguous_accounting`, `test_common_hybrid_candidate_universe`, `test_e0_split_separation` |
| **ISSUE-08** | Net charge vs pI & scTM terminology | Net charge at pH 7.4 labeled as pI; scTM labeled as standard TM-score. | **RESOLVED:** Renamed and decoupled: Net Charge at pH 7.4 ($Q_{\text{pH7.4}}$) is distinct from pI ($Q=0$). TM-score explicitly designated as Fixed-Correspondence Self-Consistency TM-score (scTM), disclaiming standard alignment-based TM-score (TM-align). | `test_net_charge_at_ph74_vs_pi_naming`, `test_fixed_correspondence_sctm`, `test_sctm_terminology_and_fixed_correspondence` |
| **ISSUE-09** | Blanket TS50 held-out overclaim | Blanket claim that TS50 has "<30% sequence identity to training sets". | **RESOLVED:** Model-specific training status mandated: <30% identity to CATH 4.2 / ProteinMPNN training sets, while ProteinSolver Gene3D 72M training membership is documented per model (superfamily absence verified where accessible, otherwise NOT VERIFIABLE FROM ACCESSIBLE METADATA). RFdiffusion scaffolds described neutrally as "RFdiffusion-generated de novo backbones". | `test_provenance_language_consistency` |
| **ISSUE-10** | Selective baseline reporting risk | Secondary baselines listed as optional/resource-dependent. | **RESOLVED:** Mandated protocol rule: *"Secondary baselines and exploratory analyses are reported regardless of outcome. No baseline or model variant may be omitted based on negative or unfavorable results."* | [`science/PREREGISTRATION.md#22`](file:///d:/Projects/Protein%20Design/science/PREREGISTRATION.md#22) |
| **ISSUE-11** | Latency comparison standardization | Latency timing lacked standardized hardware/batching rules. | **RESOLVED:** Codified standardized latency protocol: fixed GPU/CPU, FP16/FP32, batch size 1 vs 32, 5 warmup sequences, CUDA sync, model loading excluded as initialization overhead. | [`science/PREREGISTRATION.md#23`](file:///d:/Projects/Protein%20Design/science/PREREGISTRATION.md#23) |
| **ISSUE-12** | Hypervolume test-pool normalization | HV min-max normalization across candidate pools created outcome leakage. | **RESOLVED:** Demoted HV to exploratory descriptive analysis; mandated pre-declared external normalization bounds and an a priori fixed reference point $\mathbf{r} = (0.0, 0.0, 0.0)$. | [`science/PREREGISTRATION.md#17`](file:///d:/Projects/Protein%20Design/science/PREREGISTRATION.md#17) |
| **ISSUE-13** | Folding failure conflation | Hardware/software crashes risked receiving scTM=0. | **RESOLVED:** Decoupled folding failure modes: Scientific folding failure (steric clash, NaN coordinates, pLDDT < 10) is assigned $\text{scTM} = 0.0$ and included in $\{d_t\}$; Infrastructure crashes (OOM, timeout >600s, software crashes) are NEVER assigned 0.0, are excluded from $\{d_t\}$, and trigger benchmark invalidation if $>10\%$ of targets fail. | `test_folding_failure_taxonomy_handling` |
| **ISSUE-14** | Development temperature/seed allocation matrix | Integer partition across seeds and temperatures was not explicitly frozen. | **RESOLVED:** Codified exact deterministic balanced allocation matrices in `src/hybrid/budget.py`: Dev MPNN (7-7-6 across 5 temperatures $\times$ 3 seeds = 100); Dev PS E0-B (12-11-11 across 3 temperatures $\times$ 3 seeds = 100); Test ($K=500$ at frozen $T^*$ partitioned 167/167/166 across seeds 42, 1337, 2026). | `test_exact_development_temperature_allocation`, `test_frozen_test_seed_allocation` |
| **ISSUE-15** | Normalization consistency of baseline selection | Standalone MPNN greedy selector paired raw log-probs with normalized [0, 1] diversity distance. | **RESOLVED:** Codified `score_MPNN_only(u) = p_MPNN(u) \in (0, 1]` in `src/hybrid/scoring.py` so that both standalone MPNN and hybrid arms operate on the exact matched $[0, 1]$ percentile scale inside greedy facility dispersion. Autoregressive perplexity remains diagnostic. | `test_normalized_mpnn_only_selection_score` |
| **ISSUE-16** | Diversity weight $\gamma$ search grid bounds | $\gamma$ was described as tuned without a frozen search grid. | **RESOLVED:** Pre-registered dimensionless search grid $\gamma \in \{0.0, 0.25, 0.5, 1.0, 2.0\}$ in `src/hybrid/budget.py`. Tuned strictly on development set separately per arm; strictly frozen before TS50 evaluation. | `test_gamma_search_grid_freeze` |
| **ISSUE-17** | Greedy selection initialization & tie breaking | Greedy objective was undefined for empty library $S'=\emptyset$; tie breaking was unspecified. | **RESOLVED:** First selection ($S' = \emptyset$) chooses candidate with maximum primary score ($u_1 = \arg\max \text{score}(u)$); subsequent selections maximize facility dispersion objective. Ties are resolved deterministically by ascending candidate ID. | `test_first_greedy_selection_and_deterministic_tie_breaking` |
| **ISSUE-18** | Duplicate candidate accounting | Duplicate sequence handling was unspecified (risk of silent regeneration or distorted library size). | **RESOLVED:** Generation budget $K$ strictly counts all generated samples including duplicates; duplicate rate is reported separately; Stage 2 selection operates strictly on UNIQUE viable sequences; duplicates contribute 0 distance; duplicates are never silently regenerated. | `test_duplicate_candidate_accounting_and_deduplication` |
| **ISSUE-19** | Insufficient viable candidates policy ($<M$) | Behavior when viable candidates $< 10$ was undefined. | **RESOLVED:** Target arm is classified as **`SELECTION_INFEASIBLE_LT_M`**. No silent regeneration, padding with failed candidates, or post hoc threshold changes. Primary endpoint is undefined for complete-case paired comparison; conservative zero-quality sensitivity analysis is additionally reported. | `test_insufficient_viable_candidates_handling` |
| **ISSUE-20** | Statistical test implementation parameters & bootstrap | Wilcoxon zero handling, continuity correction, and bootstrap semantics were underspecified. | **RESOLVED:** Two-sided paired Wilcoxon signed-rank test on $\{d_t\}_{t=1}^N$ with $\alpha = 0.01$ (`zero_method='wilcox'`, `correction=True`); 10,000 bootstrap resamples derived strictly from target-level paired differences $d_t$ ($N=50$), never individual candidates. | `test_bootstrap_target_level_semantics` |

---

## 3. Files Created and Modified

1. **`src/hybrid/budget.py`** (Created): Codifies exact deterministic integer allocation matrices (`PROTEINMPNN_DEV_ALLOCATION`, `PROTEINSOLVER_DEV_ALLOCATION`), frozen test-time seed allocation (`PRIMARY_TEST_SEED_ALLOCATION_500`), search grids (`GAMMA_SEARCH_GRID`, `LAMBDA_SEARCH_GRID`), reproducible candidate ID generation, and budget matrix validation.
2. **`src/hybrid/scoring.py`** (Updated): Codifies scale-free percentile ranking, common candidate universe order verification (`validate_common_candidate_order`), and normalized MPNN-only selection scoring (`compute_mpnn_only_selection_score`).
3. **`src/hybrid/selection.py`** (Updated): Implements candidate deduplication (`deduplicate_candidates`), greedy selection initialization on empty $S'$ with deterministic ID tie breaking, library selection with infeasibility handling (`select_candidate_library`, `SELECTION_INFEASIBLE_LT_M`), and 3-state failure taxonomy evaluation (`evaluate_validation_outcome`).
4. **`src/hybrid/__init__.py`** (Updated): Exposes all budget, scoring, and selection functions and classes.
5. **`tests/test_scientific_protocol.py`** (Updated): Expanded from 17 to 27 comprehensive unit test suites covering all protocol rules, allocation matrices, normalized MPNN-only scoring, gamma grid, tie breaking, duplicates, infeasibility, and target-level bootstrap semantics.
6. **`science/PREREGISTRATION.md`** (Updated): Fully frozen study pre-registration incorporating all V3 parameter definitions, allocation matrices, failure taxonomies, and statistical specifications.
7. **`science/evaluation_protocol.md`** (Updated): Aligned experimental specifications E0–E5 with normalized MPNN-only selection score, balanced integer allocation tables, and 3-state failure handling.
8. **`science/metrics.md`** (Updated): Aligned candidate selection section with normalized score scale, gamma grid, deduplication, and infeasibility handling.
9. **`DECISION_LOG.md`** (Updated): Appended `[DEC-014]` recording final protocol consistency closure.
10. **`PROJECT_STATE.md`** (Updated): Logged Milestone 2.8 completion.
11. **`reports/AG_LIVE_PROGRESS.md`** & **`reports/AG_RUN_STATE.json`** (Updated): Updated live tracking to 100% complete.

---

## 4. Verification Test Results

### Full Pytest Discovery Suite
- **Command:** `uv run --python environment/proteinsolver-original/Scripts/python.exe pytest tests/ -v`
- **Output:** **52 passed in 3.14s** (25 governance test suites + 27 scientific protocol test suites).
- **Status:** **100% PASSED** (0 failures, 0 errors, 0 warnings).

### Direct Governance Test Runner
- **Command:** `environment/proteinsolver-original/Scripts/python.exe tests/test_governance.py`
- **Output:** **109/109 assertions passed, 0 failed**.
- **Coverage:** Schema validity, lesson/rule lifecycles, event log, deterministic retrieval, conflict resolution, store integrity against direct-file bypass, claim-level protections, extrapolation detection, retraction audit, and all 6 ProteinSolver regressions with bad and good case verification.

### Historical Baseline Verification Suite
- **Command:** `environment/proteinsolver-original/Scripts/python.exe test_original_execution.py`
- **Output:** **All 6 steps passed**. Clean historical execution, 0 missing/unexpected keys, 1n5uA03 41.30% recovery (38/92 matches) in 1.72s.

### Mask Invariance & Information Leak Audit
- **Command:** `environment/proteinsolver-original/Scripts/python.exe experiments/EXP004_MASK_INVARIANCE/run_mask_invariance.py`
- **Output:** **Passed**. Max absolute logit difference = `0.00000000e+00`.

### Governance Preflight CLI
- **Command:** `environment/proteinsolver-original/Scripts/python.exe -m governance.preflight_cli`
- **Output:** **`PREFLIGHT PASSED`**. 8 rules evaluated, 6 relevant, 0 unreviewed matches, 0 conflicts.

### Historical Clone Integrity
- **Command:** `git -C external/proteinsolver-original status`
- **Output:** **Clean on `master` at commit `69ef0965a3fc3bf191804035b539720a06e58ba6`** (100% untouched, 0 untracked files).

---

## 5. Distinction of Validation Levels

To maintain absolute intellectual honesty and comply with Rule `[R-007]` (Distinguish evidence scope from application scope):
1. **Implementation Verification (SOFTWARE CORRECTNESS):**
   - Verified that code in `src/hybrid/` correctly computes percentile ranks, evaluates common candidate universes, filters unique viable candidates, resolves ties deterministically, and assigns appropriate failure codes.
   - Verified that all 52 automated tests pass.
   - **This proves software correctness; it does NOT prove the biological hypothesis.**
2. **Scientific Validity (BIOLOGICAL TRUTH):**
   - Whether ProteinSolver's distance-graph constraint-satisfaction scoring provides complementary structural signal to ProteinMPNN remains an **UNTESTED HYPOTHESIS**.
   - No benchmark results on TS50 or CATH 4.2 have been generated in this pass.
   - Scientific validity will be established only through prospective evaluation under the frozen pre-registered protocol.
3. **External Evidence (LITERATURE & PEER REVIEW):**
   - The protocol design is grounded in independent red-team reviews (Claude Standalone 2.0, Perplexity, ChatGPT) and published literature (Strokach et al. 2020, Dauparas et al. 2022, Watson et al. 2023).
   - Literature evidence indicates that modern inverse-folding models substantially outperform ProteinSolver in native sequence recovery, establishing the necessity of our two-sided research question.

---

## 6. Known Intentional Limitations

1. **In Silico Proxy Nature:** Structural folding oracles (ESMFold, AlphaFold2, Boltz-1) provide in silico self-consistency models, not direct in vitro measurements of free energy of folding ($\Delta G$), thermodynamic stability, or experimental solubility.
2. **Single-Target Integration Scope:** Current empirical recovery data is strictly limited to the 1n5uA03 integration control (41.30% recovery, 38/92 residues). Multi-target evaluation will begin only in Phase 2.
3. **Corpus Unverifiability:** Training set membership of 1n5uA03 in the 72M Gene3D corpus remains *not verifiable from accessible metadata* without downloading the full external multi-terabyte dataset.
4. **Perplexity Asymmetry:** ProteinSolver masked pseudo-perplexity and ProteinMPNN autoregressive perplexity cannot be numerically compared across models and remain separate internal diagnostics.
5. **Complete-Case Paired Exclusions:** Targets encountering `SELECTION_INFEASIBLE_LT_M` (< 10 unique viable candidates) or `INFRASTRUCTURE_FAILURE_UNVALIDATED` (runtime crashes) are excluded from primary paired comparisons in complete-case analysis. Sensitivity bounds treating infeasible targets as zero-quality must be reported alongside complete-case findings.

---

## 7. Final Readiness Classification & Authorization

### Classification: **`READY_FOR_PROTEINMPNN_INTEGRATION`**

All researcher degrees of freedom are fully frozen. All authoritative documents (`docs/PROJECT_TRUTH.md`, `science/PREREGISTRATION.md`, `science/evaluation_protocol.md`, `science/metrics.md`, `DECISION_LOG.md`, `PROJECT_STATE.md`) are 100% internally consistent. All 52 automated tests pass. Zero substantive protocol ambiguities remain.

### Exact Next Phase:
**Phase 2 / Milestone 3: ProteinMPNN Integration & Baseline Verification**  
- **Track:** `Workstream B` (Modern Inverse-Folding Baselines)  
- **Action:** Integrate official ProteinMPNN repository into cleanroom environment, verify forward pass and autoregressive decoding on shared benchmark structures (including the 1n5uA03 control), and establish the standard baseline sequence recovery before initiating hybrid ensembling (E2).
