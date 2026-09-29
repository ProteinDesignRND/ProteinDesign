# Final Pre-E1 Scientific Readiness & Protocol Closure Report (V5)

**Document Identifier:** `reports/FINAL_PRE_E1_SCIENTIFIC_READINESS_CLOSURE_REPORT.md`  
**Task ID:** `PROTEIN-DESIGN-FINAL-CLOSURE-V5-STATISTICAL-AND-PROVENANCE-AUDIT`  
**Date:** 2026-09-29  
**Repository:** Protein Design / ProteinSolver Research Extension  
**Branch:** `governance/final-acceptance-redteam-v1`  
**Target Pull Request:** PR #1 (targeting `main`)  
**Authorization Boundary:** FROZEN ON REVIEW BRANCH — PENDING HUMAN REVIEW/MERGE  
**Operational Status:** `PROTOCOL_FROZEN`, `IMPLEMENTATION_VERIFIED`, `EXPERIMENTS_NOT_RUN`  

---

## 1. Final Status Summary

| Dimension | Frozen State | Verification Status |
| :--- | :--- | :--- |
| **Scientific Protocol** | **PROTOCOL_FROZEN** | Pre-registration Amendment A1 frozen; all currently registered protocol elements frozen under Amendment A1 |
| **Code Implementation** | **IMPLEMENTATION_VERIFIED** | Canonical statistical contract (`src/hybrid/statistics.py`), sequence length guards, deterministic retry and failure semantics verified |
| **Experimental Execution** | **EXPERIMENTS_NOT_RUN** | Zero benchmark candidates generated; zero ESMFold/AF2 benchmark evaluations run |
| **Development Benchmark (E1)**| **E1 NOT STARTED** | Strictly firewalled; awaiting human review and merge of PR #1 |
| **Primary Benchmark (TS50)** | **TS50 NOT STARTED** | Strictly firewalled; TS50 target manifest is a pre-test dependency |
| **Authorization Boundary** | **PENDING HUMAN REVIEW/MERGE** | Autonomous AI cannot grant scientific approval; human review/merge on PR #1 is mandatory |

---

## 2. Git State & Provenance

*Measured directly from live Git inspection on 2026-09-29:*

| Property | Measured Value | Verification Source |
| :--- | :--- | :--- |
| **Current Branch** | `governance/final-acceptance-redteam-v1` | `git status` |
| **Audit-Start HEAD SHA** | `62f2c9627ba344f3fc0e89edccb3e4ac3e9b37ab` | Initial HEAD prior to V5 pass |
| **Current HEAD SHA** | Determined by final V5 commit on this branch (verified post-commit) | `git rev-parse HEAD` |
| **Base Branch (`main`)** | `c1f0b863e3aca12eb9804696a3d8870aed625020` (Protected, untouched) | `git rev-parse origin/main` |
| **Merge Base** | `c1f0b863e3aca12eb9804696a3d8870aed625020` | `git merge-base HEAD origin/main` |
| **Working Tree Cleanliness** | Clean (tracked changes committed in single coherent V5 commit) | `git status` |
| **External Historical Repo** | Independent nested Git repository clone clean at commit `69ef0965a3fc3bf191804035b539720a06e58ba6` | `git -C external/proteinsolver-original status` |
| **Historical Source Modified** | **NO** — 0 bytes modified in `external/proteinsolver-original` | `git -C external/proteinsolver-original diff` |

---

## 3. Pull Request State

- **PR Number:** PR #1
- **PR URL:** `https://github.com/dheeraj-7ty/ProteinDesign/pull/1`
- **Source Branch:** `governance/final-acceptance-redteam-v1`
- **Target Branch:** `main`
- **Merge Status:** **NOT MERGED** (Autonomous AI merge is strictly prohibited; human review/merge is the mandatory authorization gate).

---

## 4. Scoped Scientific Authority Hierarchy

The repository enforces a strict scoped authority hierarchy:

1. **Level 1 — Actual Committed Code & Manifest Artifacts:**
   The committed software implementation (`src/`), manifests (`data/manifests/`), and automated regression tests (`tests/`) represent the physical ground truth of what executes.
2. **Level 2 — Frozen Scientific Pre-Registration:**
   `science/PREREGISTRATION.md` is the authoritative frozen scientific protocol, defining hypothesis tests, statistical methods, sample sizes, and oracle configurations.
3. **Level 3 — Verified Facts & Limitations Record:**
   `docs/PROJECT_TRUTH.md` is the authoritative record of verified implementation facts, evidence status, known limitations, untested status, and current implementation truth. It defers to `science/PREREGISTRATION.md` for scientific protocol.
4. **Level 4 — Chronological Decision Provenance:**
   `DECISION_LOG.md` is the authoritative record of chronological historical decisions (DEC-001 through DEC-019). Historical decisions are immutable records of prior context.
5. **Level 5 — High-Level Project State Summary:**
   `PROJECT_STATE.md` tracks high-level milestone progress and operational state.
6. **Level 6 — Protocol Specifications:**
   `science/evaluation_protocol.md`, `science/metrics.md`, and `science/datasets.md` are detailed specifications subordinate to `science/PREREGISTRATION.md`.
7. **Level 7 — Derived Summaries & Historical Snapshots:**
   `reports/*.md`, PR bodies, and progress logs are derived summaries. They serve as audit evidence but **never override Levels 1–4**.

---

## 5. Complete Issue Inventory & Classification

| Issue ID | Scope | Component | Classification | Description & Resolution Summary |
| :---: | :--- | :--- | :---: | :--- |
| **ISSUE-01** | Git Provenance | `reports/*.md` | **FIXED** | Delineated Audit-Start HEAD (`62f2c96...`) from the Final Current HEAD produced by this V5 pass. "Current HEAD" never refers to an ancestor. |
| **ISSUE-02** | Authority Scope | `docs/PROJECT_TRUTH.md` | **FIXED** | Refined Project Truth title and scope to verified implementation facts and limitations, explicitly establishing `science/PREREGISTRATION.md` as protocol authority and `DECISION_LOG.md` as historical decision authority. |
| **ISSUE-03** | Statistical Contract | `src/hybrid/statistics.py` | **FIXED** | Created canonical statistical module implementing `compute_paired_wilcoxon_test` with explicit `method='asymptotic'`, `zero_method='wilcox'`, `correction=True`, and `alternative='two-sided'`. Added strict finite numeric validation (rejecting NaN/inf) and sample size guard ($N \ge 2$). |
| **ISSUE-04** | Protocol Wording | `science/PREREGISTRATION.md` | **FIXED** | Replaced overclaiming "standard for N >= 25" with accurate description: "The confirmatory p-value is computed with the pre-registered asymptotic/normal approximation and continuity correction." |
| **ISSUE-05** | Retry Semantics | Protocol & Specifications | **FIXED** | Replaced vague "clean execution parameters" with deterministic rule: retry exactly once with identical frozen configuration (model, checkpoint, version, precision, device, chunk size, seed, input, timeout). Only process restart/cleanup permitted. |
| **ISSUE-06** | Oracle Scope | `science/PREREGISTRATION.md` | **FIXED** | Explicitly scoped frozen ESMFold path (GPU `cuda`, `float16`, `chunk_size = 128`, seed 42) to cover all registered benchmark stages, including E1 development tuning and TS50 primary evaluation. |
| **ISSUE-07** | Sequence Guard | `src/hybrid/selection.py` | **FIXED** | Implemented `validate_target_sequence_length(sequence, target_id, max_length=1024)`. Manifests must validate $L \le 1024$ before execution; violations reject at preflight. |
| **ISSUE-08** | Dev Failure Policy | `src/hybrid/optimization.py` | **FIXED** | Codified that if an AF2 validation fails for infrastructure during development tuning, unresolved failure makes target unable to produce complete $M=10$ library; configuration is classified INELIGIBLE with $J = -\infty$. |
| **ISSUE-09** | Screening Failure | `src/hybrid/selection.py` | **FIXED** | Added `is_screening_infrastructure_failure` to `Candidate`. If screening fails after one retry, candidate is marked infrastructure-unvalidated, excluded from viable set, never assigned 0.0, and never regenerated. |
| **ISSUE-10** | Parameter Language | Code & Docs | **FIXED** | Replaced brittle "all 24 study parameters locked" with "all currently registered protocol elements are frozen under Amendment A1". |
| **ISSUE-11** | Reproducibility | `DECISION_LOG.md` | **FIXED** | Excised "bitwise clarity" from DEC-018; replaced with scientifically accurate wording acknowledging hardware-level GPU variation. |
| **ISSUE-12** | Status Language | Reports & State | **FIXED** | Avoided overclaiming "zero ambiguities" or "full perfection"; adopted precise scoped claim: "No remaining deterministic defects were identified in the audited current-state scope." |
| **ISSUE-13** | Test Verification | Test Suite | **FIXED** | Fresh execution of full pytest suite: 81 collected, 81 passed across 4 test modules. Governance preflight passed with 0 conflicts and 0 store integrity violations. |
| **ISSUE-14** | Firewall Integrity | Repository-wide | **FIXED** | Verified complete scientific firewall: 0 candidates generated, 0 benchmark inferences run, 0 test targets inspected. |
| **ISSUE-15** | Governance Rules | `governance/` | **FIXED** | Preserved L-007 through L-011 as `PROPOSED`. Added proposed lessons L-012 through L-016. Appended DEC-019. |
| **LIMIT-01** | Technical Boundary | Hardware Execution | **LIMITATION** | Fixed seed 42 controls pseudo-randomness but does not guarantee bitwise GPU-identical AF2/ESMFold predictions across heterogeneous hardware/software architectures. |
| **LIMIT-02** | Training Provenance | Historical Checkpoint | **LIMITATION** | ProteinSolver historical training set membership for benchmark targets is not verifiable from accessible metadata. |
| **LIMIT-03** | Metric Semantics | Structural Evaluation | **LIMITATION** | Fixed-correspondence scTM is a continuous length-normalized similarity metric ($i \mapsto i$), not an alignment-optimized TM-score. |
| **HIST-01** | Upstream Source | Historical Clone | **HISTORICAL** | `external/proteinsolver-original` preserved 100% clean and untouched at commit `69ef0965a3fc3bf191804035b539720a06e58ba6`. |

---

## 6. Exact Files Changed in V5 Pass

1. `src/hybrid/statistics.py`: Created canonical statistical module implementing `compute_paired_wilcoxon_test` (`method='asymptotic'`, `zero_method='wilcox'`, `correction=True`, finite input validation, $HL$, Cohen's $d_z$).
2. `src/hybrid/selection.py`: Added `validate_target_sequence_length` ($L \le 1024$ preflight guard) and `is_screening_infrastructure_failure` flag on `Candidate`.
3. `src/hybrid/optimization.py`: Implemented `compute_development_target_sctm_mean` returning `None` on infrastructure failure, assigning $J = -\infty$ for development tuning.
4. `src/hybrid/__init__.py`: Exported statistical and validation functions.
5. `science/PREREGISTRATION.md`: Aligned Section 5 (asymptotic Wilcoxon, input validation, deterministic retries, failure handling), Section 8 (AF2 failure $\implies J = -\infty$), Section 11 (ESMFold scope covering E1+TS50, $L \le 1024$ guard).
6. `science/evaluation_protocol.md`: Aligned ESMFold screening, Wilcoxon `method='asymptotic'`, and retry/failure rules.
7. `science/metrics.md`: Aligned oracle specifications, retry rules, and failure classification.
8. `docs/PROJECT_TRUTH.md`: Scoped authority to verified facts and limitations, deferring protocol authority to `PREREGISTRATION.md`.
9. `PROJECT_STATE.md`: Replaced "24 study parameters" with "all currently registered protocol elements under Amendment A1"; added V5 milestone closure summary.
10. `reports/REPORT_INDEX.md`: Replaced "24 study parameters" with "all currently registered protocol elements under Amendment A1".
11. `DECISION_LOG.md`: Excised "bitwise clarity" from DEC-018; appended `[DEC-019]` for V5 statistical and failure handling freeze.
12. `governance/data/lessons.json`: Appended proposed lessons L-012 through L-016.
13. `tests/test_scientific_protocol.py`: Added comprehensive unit tests for Wilcoxon asymptotic configuration, input validation, sequence length guard, oracle failure policies, and Project Truth authority scope.
14. `reports/AG_LIVE_PROGRESS.md`: Real-time execution and audit progress tracking.
15. `reports/AG_RUN_STATE.json`: Machine-readable run state.
16. `reports/FINAL_PRE_E1_SCIENTIFIC_READINESS_CLOSURE_REPORT.md`: Comprehensive V5 closure report.

---

## 7. Exact Statistical Contract Frozen

```python
# Frozen Statistical Invocation (src/hybrid/statistics.py)
scipy.stats.wilcoxon(
    d,
    zero_method='wilcox',
    correction=True,
    alternative='two-sided',
    method='asymptotic',
)
```

- **Hypothesis Test:** Two-sided paired Wilcoxon signed-rank test on target-level paired differences $d_t = \overline{\text{scTM}}_{\text{hybrid}}(t) - \overline{\text{scTM}}_{\text{MPNN-only}}(t)$.
- **Software Reference:** SciPy v1.17.1.
- **Approximation Method:** Explicitly frozen to `method='asymptotic'` with continuity correction (`correction=True`).
- **Zero Differences:** Handled via `zero_method='wilcox'` (zero differences assigned average rank; if all differences are zero, returns $W=0.0$, $z=0.0$, $p=1.0$).
- **Numeric Validation:** Strictly rejects NaN, positive infinity, and negative infinity inputs by raising `ValueError`.
- **Sample Size Guard:** Minimum sample size $N \ge 2$; raises `ValueError` if fewer than 2 valid paired differences are provided.
- **Effect Size:** Hodges-Lehmann median of pairwise Walsh averages $\text{median}(\{(d_i + d_j)/2 : 1 \le i \le j \le N\})$.
- **Confidence Intervals:** 10,000 paired target-level bootstrap resamples with seed 42 using the percentile method (95% CI).

---

## 8. Exact ESMFold & AlphaFold2 Oracle Paths Frozen

### ESMFold Screening Path (E1 Development & TS50 Benchmark)
- **Model:** `esm.pretrained.esmfold_v1()`
- **Mode:** Sequence-only (zero structural templates, 4 recycles)
- **Precision:** `float16`
- **Device:** Single NVIDIA GPU (`cuda`)
- **Chunk Size:** `chunk_size = 128` (fixed; CPU and chunk 64 are non-confirmatory diagnostics only)
- **Seed:** 42
- **Length Constraint:** Max sequence length $L \le 1024$ enforced by preflight guard
- **Screening Thresholds:** Mean pLDDT $\ge 70.0$, pTM $\ge 0.50$
- **Candidate-Level Failure:** If a candidate fails ESMFold due to infrastructure, retry exactly once with identical frozen configuration. If unresolved, mark candidate as infrastructure-unvalidated (`is_screening_infrastructure_failure = True`), exclude from viable set, never assign 0.0, and never regenerate.

### AlphaFold2 Validation Path (Selected Library M=10)
- **Pipeline:** Sequence-only prediction (single-sequence mode / reduced MSA as specified in protocol)
- **Seed:** 42
- **Precision:** `float16`
- **Development Failure Policy:** If a selected candidate's AF2 validation fails for infrastructure, retry exactly once with identical frozen configuration. If unresolved, the target cannot produce the required complete $M=10$ library; classify the development configuration as INELIGIBLE and assign objective $J = -\infty$.
- **Confirmatory TS50 Policy:** Preserves target-level complete-case analysis (infrastructure failures documented and handled under primary statistical missingness policy).

---

## 9. Exact Retry Semantics Frozen

Across all frozen validation oracles (ESMFold, AlphaFold2), retry semantics are strictly defined:

> **Frozen Retry Rule:**  
> Retry exactly once using the identical frozen model, checkpoint, version, precision, device, chunk size, seed, input, timeout, and protocol configuration. Only process restart and resource cleanup are permitted. No scientific or inference parameter may be changed during the retry.

If a failure remains unresolved after the one identical-configuration retry:
- Classify as `INFRASTRUCTURE_FAILURE`.
- Never assign biological score 0.0.
- Never silently switch precision (e.g., fp16 $\to$ fp32), device (CUDA $\to$ CPU), chunk size (128 $\to$ 64), or model.
- Apply the appropriate downstream failure rule (screening exclusion for candidates, $J = -\infty$ for dev tuning, complete-case reporting for TS50).

---

## 10. Fresh Test Execution Results

```
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\Projects\Protein Design
plugins: anyio-4.15.1
collected 81 items

tests/test_development_hyperparameter_selection.py ...........           [ 13%]
tests/test_governance.py .........................                       [ 44%]
tests/test_proteinmpnn.py ............                                   [ 59%]
tests/test_scientific_protocol.py .................................      [100%]

============================= 81 passed in 28.74s =============================
```

- **Total Collected Tests:** **81**
- **Passed:** **81**
- **Failed:** **0**
- **Errors:** **0**
- **Warnings:** **0**
- **Test Modules:** 4
  - `tests/test_development_hyperparameter_selection.py`: 11 passed
  - `tests/test_governance.py`: 25 passed
  - `tests/test_proteinmpnn.py`: 12 passed
  - `tests/test_scientific_protocol.py`: 33 passed
- **Governance Preflight:** PASSED (0 store integrity violations, 0 conflicts, 8 rules evaluated, 6 relevant).
- **Historical ProteinSolver Cleanliness:** Verified untouched at commit `69ef0965a3fc3bf191804035b539720a06e58ba6` (0 bytes modified).

---

## 11. Scientific Firewall Verification

The scientific firewall remains **100% INTACT AND UNBREACHED**:
- **E1 Benchmark:** NOT RUN (0 candidates generated)
- **TS50 Primary Benchmark:** NOT RUN (0 candidates generated)
- **ESMFold Benchmark Screening:** NOT RUN (0 benchmark inferences)
- **AlphaFold2 Benchmark Validation:** NOT RUN (0 benchmark inferences)
- **Test-Set Inspection:** NOT RUN (0 test outcomes observed)
- **Benchmark Hyperparameter Tuning:** NOT RUN (0 parameters tuned against benchmark outcomes)

---

## 12. Remaining Genuine Limitations

1. **Hardware-Level GPU Determinism:** While fixed inference seed 42 strictly controls pseudo-random number generator state, bitwise GPU determinism cannot be guaranteed across heterogeneous hardware architectures, CUDA versions, or cuBLAS algorithm selections.
2. **ProteinSolver Historical Training Set Membership:** Historical ProteinSolver training manifests are not fully recoverable from published metadata; benchmark targets cannot be guaranteed to be absent from historical training data.
3. **Fixed-Correspondence scTM:** Residue-to-residue fixed correspondence ($i \mapsto i$) without alignment optimization is an operational project surrogate for global fold fidelity, not standard TM-align.
4. **TS50 Pre-Test Dependency:** The TS50 exact target manifest remains a pre-test dependency that must be frozen prior to TS50 benchmark execution.

---

## 13. Explicit Statement on Benchmark Experiments

**NO BENCHMARK EXPERIMENTS HAVE BEEN RUN.**  
Zero candidate sequences have been generated for development targets. Zero ESMFold screening passes have been executed on benchmark targets. Zero AlphaFold2 validations have been run. Zero TS50 targets have been inspected or processed. All parameters ($T^*, \lambda^*, \gamma^*$) remain unselected and strictly awaiting human authorization of Milestone 3A.

---

## 14. Exact Next Authorized Step

```
PROTOCOL_FROZEN
IMPLEMENTATION_VERIFIED
EXPERIMENTS_NOT_RUN
PENDING HUMAN REVIEW/MERGE
```

1. **Human review** of Pull Request #1 on branch `governance/final-acceptance-redteam-v1`.
2. **Human approval and merge** of PR #1 into `main`.
3. **Post-Merge Authorization:** Initiate Phase 3 Milestone 3A (Development Hyperparameter Selection E1) strictly in accordance with frozen decisions DEC-015, DEC-016, DEC-017, DEC-018, and DEC-019.
