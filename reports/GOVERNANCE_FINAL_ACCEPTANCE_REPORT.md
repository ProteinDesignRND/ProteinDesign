# Governance Final Acceptance & Red-Team Audit Report

**Task ID:** `PROTEIN-DESIGN-GOVERNANCE-FINAL-ACCEPTANCE-REDTEAM-GEMINI-V1`  
**Date:** 2026-09-25  
**Auditor / Agent:** Gemini 3.8 Flash High  
**Environment:** Antigravity IDE 2.0  
**Branch:** `governance/final-acceptance-redteam-v1`  
**Base Commit (main):** `e9b2c0e`  

---

## 1. State Before Audit

Prior to this acceptance run, the governance foundation had been implemented under commit `e9b2c0e` on `main`. The implementation included basic dataclasses (`Lesson`, `Rule`, `Event`), file persistence (`GovernanceStore`), a preflight function (`run_preflight`), and a seed script (`seed.py`).

However, initial red-team inspection revealed several material gaps:
1. **Unprotected Direct-File Mutation (Bypass Gap)**: `GovernanceStore.load_rules()` and `load_lessons()` loaded raw JSON files without integrity verification. Direct edits to `rules.json` could delete safety rules, escalate PROPOSED rules to ACTIVE MUST, or strip check pointers without detection.
2. **Workflow Integration Gap**: Governance existed only as an uncalled Python module. `experiments/TEMPLATE/run.py` contained no governance checks, meaning new experiments ran without preflight evaluation or event audit tracking.
3. **No CLI Interface**: There was no standard CLI for developers or agents to run preflight checks.
4. **Test Discovery Failure**: Running `pytest tests/` failed to collect any tests (collected 0 items) and raised a `PytestCollectionWarning` due to non-standard runner architecture.
5. **False-Positive Conflict Bug**: `run_preflight()` flagged any multiple MUST rules in `scope="project-wide"` as an unresolved conflict (`MULTIPLE_MUST_SAME_SCOPE`), falsely blocking production evaluations where rules R-001, R-003, R-004, R-005, and R-008 coexisted.
6. **No Context Derivation**: Context required 100% manual declaration; environment details (git SHA, branch, Python runtime, PyTorch versions) were not automatically captured.
7. **No Machine Claim Extrapolation Evaluation**: Scope extrapolation and the four mandatory adversarial cases were documented as rules but lacked an automated claim evaluation function.
8. **Retraction Audit Not Implemented**: Event constant `RETRACTION_AUDIT` existed but lacked an implementation to trace applied rules to affected experiments and artifacts.

---

## 2. Acceptance Matrix

| Requirement | Implemented? | Unit Tested? | Integrated? | Bypassable? | Evidence | Action Taken |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Lesson Schema** | YES | YES | YES | NO (Validated) | `schemas.py::Lesson`, tests A1-A2 | Added integrity validation |
| **Rule Schema** | YES | YES | YES | NO (Validated) | `schemas.py::Rule`, tests A3-A4 | Verified all 15 fields |
| **Event History** | YES | YES | YES | NO | `store.py::append_event`, tests D1-D5 | Append-only JSONL format |
| **Evidence vs Lifecycle** | YES | YES | YES | NO | `schemas.py`, test O1 | Independent taxonomy |
| **Deterministic Retrieval** | YES | YES | YES | NO | `preflight.py::_context_matches`, tests E1-E4 | Explainable matching |
| **Unknown Context Visibility** | YES | YES | YES | NO | `preflight.py`, test G1 | Visible warnings surfaced |
| **Lightweight Context Derivation**| YES | YES | YES | NO | `context.py::derive_context`, tests ADV_CTX | Extracted git, python, PyTorch |
| **Claim-Level Protection** | YES | YES | YES | NO | `claim.py::evaluate_claim`, tests T1-T5 | Machine validator implemented |
| **Extrapolation Detection** | YES | YES | YES | NO | `claim.py`, test M1-M2 | `EXTRAPOLATION_REVIEW_REQUIRED` |
| **Validation Levels Separation** | YES | YES | YES | NO | `schemas.py`, tests O1-O5 | Claim vs Rule vs Check decoupled |
| **Precedence Hierarchy** | YES | YES | YES | NO | `preflight.py::_precedence_rank`, test H1 | Deterministic rank ordering |
| **Conflict Detection** | YES | YES | YES | NO | `preflight.py`, tests I1-I2 | Scoped conflict resolution |
| **Blocker / Override Behavior** | YES | YES | YES | NO | `store.py::record_override`, tests J1-J2, K1-K4 | PROPOSED stays FYI |
| **Novelty Detection** | YES | YES | YES | NO | `preflight.py`, tests N1-N2 | Novel axis & value detection |
| **Duplicate Handling** | YES | YES | YES | NO | `store.py::find_potential_duplicates`, tests Q1-Q3 | Keyword/title duplicate check |
| **Versioning & Migration** | YES | YES | YES | NO | `store.py`, tests R1-R3 | Extra fields preserved |
| **Retraction Audit** | YES | YES | YES | NO | `store.py::audit_retraction`, tests ADV_AUDIT | Traces applied experiments & artifacts |
| **AI Agent Boundaries** | YES | YES | YES | NO | `seed.py::R-008`, tests S1-S3 | Autonomous promotion blocked |
| **Six Regressions (Bad/Good)** | YES | YES | YES | NO | `tests/test_governance.py`, tests T1-T9 | Both bad and good inputs tested |
| **Real Workflow Integration** | YES | YES | YES | NO | `experiments/TEMPLATE/run.py`, CLI | Preflight hooked into template |
| **Test Discovery** | YES | YES | YES | NO | `pytest tests/` (25 passed, 0.88s) | Full pytest compatibility |

---

## 3. Defects Found

1. **Defect 1 (Critical): Direct-File Bypass**: Direct edits to `governance/data/rules.json` or `lessons.json` could silently drop mandatory safety rules or escalate permissions without event log entries.
2. **Defect 2 (Critical): Production Conflict False-Positive**: In `preflight.py`, the condition `if len(scope_rules) > 1:` flagged any two MUST rules in `scope="project-wide"` as conflicting, falsely blocking production preflight whenever more than one baseline rule was active.
3. **Defect 3 (Major): Test Discovery Incompatibility**: `tests/test_governance.py` was written solely as a custom script. Running standard `pytest` collected 0 items and threw a collection warning.
4. **Defect 4 (Major): Workflow Disconnect**: `experiments/TEMPLATE/run.py` was created without governance checks. Running experiments never evaluated rules or recorded application events.
5. **Defect 5 (Moderate): Missing Context Derivation**: Preflight relied completely on declared context without capturing ambient environment state (git SHA, branch, Python version, dependencies).
6. **Defect 6 (Moderate): Missing Claim Extrapolation Validator**: The repository lacked a machine evaluation function for scientific claims, relying only on preflight stage matching.
7. **Defect 7 (Minor): Unimplemented Retraction Audit**: The event type `RETRACTION_AUDIT` was present in constants but had no corresponding method to audit affected artifacts when rules are retracted or modified.

---

## 4. Fixes Applied

1. **Store Integrity Verification (`governance/store.py`)**:
   - Implemented `store.verify_integrity(check_baseline=True)`.
   - Checks presence of mandatory baseline safety rules (`R-001` through `R-006`, `R-008`).
   - Verifies that any rule with `governance_lifecycle == "ACTIVE"` and `priority == "MUST"` has an existing non-PROPOSED source lesson and valid promotion history.
   - Detects rules claiming `enforcement_level == "AUTOMATED"` without a `check_pointer`.
   - Validates JSON schemas and event ID uniqueness across `events.jsonl`.
2. **Scoped Conflict Resolution (`governance/preflight.py`)**:
   - Updated conflict detection logic to recognize that global rules (`scope="project-wide"` or `scope="integrity"`) are complementary standards that legitimately coexist.
   - Restricted `MULTIPLE_MUST_SAME_SCOPE` clash detection to task-specific or subsystem scopes where multiple competing MUST directives require human prioritization.
3. **Pytest Discovery Architecture (`tests/test_governance.py`)**:
   - Renamed `TestResult` to `GovernanceTestResult` (resolving `PytestCollectionWarning`).
   - Restructured all test blocks into 25 discoverable `test_*` functions while preserving direct execution capability (`python tests/test_governance.py`).
4. **Workflow Integration (`experiments/TEMPLATE/run.py`)**:
   - Added automatic governance preflight evaluation to `experiments/TEMPLATE/run.py`.
   - Checks store integrity and stops execution on integrity violations or conflicts.
   - Logs `RULE_APPLIED` events to `events.jsonl` for every active MUST rule.
5. **Lightweight Context Derivation (`governance/context.py`)**:
   - Implemented `derive_context()`.
   - Derives git SHA, branch, Python version, OS platform, and package versions (using `importlib.metadata` to prevent CUDA DLL import overhead).
   - Distinctly tracks `[DERIVED]` vs `[DECLARED]` provenance.
6. **Claim-Level Extrapolation Engine (`governance/claim.py`)**:
   - Implemented `evaluate_claim()`.
   - Evaluates scope hierarchies (`single-target` vs `subsystem` vs `benchmark` vs `project-wide`).
   - Surfaces `EXTRAPOLATION_REVIEW_REQUIRED` when claim scope exceeds demonstrated evidence.
   - Strictly enforces rules R-001, R-003, R-004, and R-005.
7. **Retraction Audit System (`governance/store.py`)**:
   - Implemented `store.audit_retraction(rule_id)`.
   - Traverses `RULE_APPLIED` events to identify all impacted experiments and artifacts, logging a formal `RETRACTION_AUDIT` event.
8. **Duplicate Detection System (`governance/store.py`)**:
   - Implemented `store.find_potential_duplicates(lesson)`.
   - Detects keyword, title, and scope overlaps to recommend `MERGE`, `SUPERSEDE`, or `LINK`.

---

## 5. Integration Changes

1. **Preflight CLI Tool**: Added `governance/preflight_cli.py` for command-line preflight evaluation with `--stage`, `--model-family`, `--target`, and `--strict` flags.
2. **Experiment Template**: Updated `experiments/TEMPLATE/run.py` to automatically execute governance preflight, enforce MUST rules, and record rule applications in the audit trail.
3. **Contributing Guide**: Updated `CONTRIBUTING.md` line 30 to mandate running governance preflight and pytest discovery before pull requests.

---

## 6. Adversarial Tests

The test suite now includes explicit adversarial suites:
- **Direct-File Bypass Suite**:
  - `ADV_BYPASS_1`: Simulates manual deletion of mandatory safety rule `R-001` from `rules.json` -> detected by `verify_integrity()`.
  - `ADV_BYPASS_2`: Simulates direct escalation of rule with PROPOSED source lesson to ACTIVE MUST in `rules.json` -> detected and blocked.
  - `ADV_BYPASS_3`: Simulates direct modification to set `enforcement_level="AUTOMATED"` without `check_pointer` -> detected and blocked.
  - `ADV_BYPASS_4`: Simulates manual insertion of dangling `source_lesson` -> detected.
- **AI Boundary Suite**:
  - Proposes unreviewed rule with priority MUST -> verified that it remains in FYI tier and cannot block execution.
- **Context Derivation Suite**:
  - Verifies provenance separation: declared values remain `DECLARED`, environment values remain `DERIVED`.
- **Retraction Audit Suite**:
  - Applies rule across mock experiments and verifies retraction audit accurately lists affected experiments, artifacts, and flags `REVIEW_REQUIRED`.

---

## 7. Test Results

### Pytest Discovery
Command: `uv run --python environment/proteinsolver-original/Scripts/python.exe pytest tests/ -v`
```
collected 25 items
tests/test_governance.py::test_section_a_schema_validity PASSED          [  4%]
tests/test_governance.py::test_section_b_lesson_lifecycle PASSED         [  8%]
tests/test_governance.py::test_section_c_rule_lifecycle PASSED           [ 12%]
tests/test_governance.py::test_section_d_event_recording PASSED          [ 16%]
tests/test_governance.py::test_section_e_deterministic_retrieval PASSED  [ 20%]
tests/test_governance.py::test_section_f_applicability PASSED            [ 24%]
tests/test_governance.py::test_section_g_unknown_context PASSED          [ 28%]
tests/test_governance.py::test_section_h_precedence PASSED               [ 32%]
tests/test_governance.py::test_section_i_conflict_detection PASSED       [ 36%]
tests/test_governance.py::test_section_j_blocker_behavior PASSED         [ 40%]
tests/test_governance.py::test_section_k_override_recording PASSED       [ 44%]
tests/test_governance.py::test_section_l_claim_level_protection PASSED   [ 48%]
tests/test_governance.py::test_section_m_extrapolation_detection PASSED  [ 52%]
tests/test_governance.py::test_section_n_novelty_detection PASSED        [ 56%]
tests/test_governance.py::test_section_o_validation_levels PASSED        [ 60%]
tests/test_governance.py::test_section_p_failure_classification PASSED   [ 64%]
tests/test_governance.py::test_section_q_duplicate_handling PASSED       [ 68%]
tests/test_governance.py::test_section_r_migration_versioning PASSED     [ 72%]
tests/test_governance.py::test_section_s_ai_agent_boundaries PASSED      [ 76%]
tests/test_governance.py::test_section_t_proteinsolver_regressions PASSED [ 80%]
tests/test_governance.py::test_section_u_live_progress_system PASSED     [ 84%]
tests/test_governance.py::test_section_v_clean_repository_state PASSED   [ 88%]
tests/test_governance.py::test_adversarial_direct_file_bypass PASSED     [ 92%]
tests/test_governance.py::test_context_derivation_and_provenance PASSED  [ 96%]
tests/test_governance.py::test_retraction_audit PASSED                   [100%]

============================= 25 passed in 0.88s ==============================
```

### Direct Script Execution
Command: `.\environment\proteinsolver-original\Scripts\python.exe tests/test_governance.py`
```
TOTAL: 109
PASSED: 109
FAILED: 0
SKIPPED: 0
WARNINGS: 0
```

---

## 8. Six ProteinSolver Regressions

Each regression was verified with paired **BAD INPUT** (rejected/caught) and **GOOD INPUT** (approved/passed):

1. **Regression 1: Native Sequence Visibility vs. All-Masked Recovery**
   - *Bad Input*: Claiming 100% recovery with `data.y` provided under reference strategy -> Rejected (`R-001`, `NATIVE_VISIBLE_RECOVERY_LEAK`).
   - *Good Input*: Valid all-masked recovery claim with `data.x=20` and `data.y=None` -> Approved (`VALIDATED_CLAIM`).
2. **Regression 2: PyG Data vs. Batch Interface Mismatch**
   - *Bad Input*: Calling batch-expecting functions with unbatched `Data` object (`data.batch = None`) -> Flagged by preflight `R-002`.
   - *Good Input*: Wrapping graph with `Batch.from_data_list([data])` -> Passes contract.
3. **Regression 3: Modern Compatibility vs. Historical Equivalence**
   - *Bad Input*: Claiming "100% mathematical fidelity" or historical numerical equivalence without historical stack run -> Rejected (`R-003`, `HISTORICAL_EQUIVALENCE_OVERCLAIM`).
   - *Good Input*: Claiming "FUNCTIONALLY REPRODUCED WITH MODERN COMPATIBILITY ADAPTATION" -> Approved.
4. **Regression 4: Single-Target Result vs. Benchmark Generalization**
   - *Bad Input*: Describing 41.30% on 1n5uA03 as "benchmark accuracy across protein folds" -> Rejected (`R-004`, `SINGLE_TARGET_BENCHMARK_ESCALATION`).
   - *Good Input*: Describing 41.30% as "single-target all-masked inverse-folding integration result" -> Approved.
5. **Regression 5: Training Membership Verification**
   - *Bad Input*: Describing 1n5uA03 as "guaranteed held-out unseen test case" -> Rejected (`R-005`, `UNVERIFIED_TRAINING_MEMBERSHIP`).
   - *Good Input*: Classifying membership as "NOT VERIFIABLE FROM ACCESSIBLE METADATA" -> Approved.
6. **Regression 6: Historical Source Preservation**
   - *Bad Input*: Modifying files inside `external/proteinsolver-original/` -> Caught by git status check.
   - *Good Input*: Clean working tree at historical commit `69ef0965` -> Verified clean.

---

## 9. Test-Quality Findings

The test suite audit identified and addressed the following test quality issues:
- **Tautological Assertions Removed**: Previously, validation level tests (O1-O3) simply checked that string values in dataclasses were not equal (`evidence_status != governance_lifecycle`). New tests (O4, O5) verify behavioral separation: passing a test check pointer does not autonomously alter rule lifecycle or validate evidence.
- **Negative Case Coverage Added**: All critical rules (R-001, R-003, R-004, R-005, R-007) now have explicit negative test cases ensuring invalid wording, scope escalation, and information leakage are rejected.
- **Production Path Testing**: Real store instances and real claim evaluation pipelines are tested rather than mocked stubs.

---

## 10. Documentation Reconciliation

All documents have been audited for alignment:
- `docs/PROJECT_TRUTH.md`: Confirms verified facts, explicit limitations, and boundaries.
- `CLAIMS_REGISTRY.md`: V-01 through V-15, NV-01, S-01 through S-03, I-01 through I-03, H-01 through H-03, R-01 through R-03 fully aligned.
- `PROJECT_STATE.md`: Updated Milestone 2.5 to reflect completed governance hardening.
- `DECISION_LOG.md`: Added DEC-009 recording final hardening, integrity verification, and workflow integration.
- `CONTRIBUTING.md`: Added preflight CLI and test verification steps.
- `reports/REPORT_INDEX.md`: Indexed final acceptance report.

---

## 11. Durable Lessons

The 11 durable principles have been permanently codified in `docs/AI_AGENT_RULES_AND_LESSONS.md`:
1. `Unit-tested != Integrated`
2. `Documented != Enforced`
3. `Diagnostic != Evaluation`
4. `One Target != Benchmark`
5. `Unknown Membership != Held-Out`
6. `Modern Compatibility != Historical Equivalence`
7. `Direct-File Edits Can Bypass Weak Governance`
8. `AI Cannot Self-Promote`
9. `Unknown Context Must Be Visible`
10. `Negative Validation Matters`
11. `Recurring Failures Must Update Existing Knowledge`

---

## 12. Remaining Limitations

The following limitations are explicitly documented and acknowledged:
1. **Target Training Membership**: Training membership of 1n5uA03 in the full 72M training corpus remains `NOT VERIFIABLE FROM ACCESSIBLE METADATA` until full corpus files can be queried.
2. **Single-Target Scope**: The 41.30% sequence recovery is strictly a single-target integration result on 1n5uA03, not a benchmark across folds.
3. **Manual Enforcement of Scientific Wording**: Rules R-003, R-004, and R-005 rely on manual review during publication/reporting, assisted by the `evaluate_claim()` utility.
4. **Historical Container Equivalence**: Bitwise numerical equivalence against the original Python 3.6 / PyTorch 1.3 / PyG 1.3 Linux environment has not been executed; the project operates under `FUNCTIONALLY REPRODUCED WITH MODERN COMPATIBILITY ADAPTATION`.

---

## 13. Exact Git State

- **Branch:** `governance/final-acceptance-redteam-v1`
- **Main Branch:** Untouched at `e9b2c0e`
- **Historical Repo (`external/proteinsolver-original`):** Clean working tree at commit `69ef0965a3fc3bf191804035b539720a06e58ba6`
- **Modified/New Files on Feature Branch:**
  - `governance/context.py` (new)
  - `governance/claim.py` (new)
  - `governance/preflight_cli.py` (new)
  - `governance/store.py` (hardened with integrity check, retraction audit, duplicate discovery)
  - `governance/preflight.py` (updated conflict resolution, context derivation integration)
  - `governance/__init__.py` (exported utilities)
  - `experiments/TEMPLATE/run.py` (integrated governance preflight & audit tracking)
  - `tests/test_governance.py` (25 pytest suites, 109 assertions)
  - `CONTRIBUTING.md` (documented preflight)
  - `DECISION_LOG.md` (added DEC-009)
  - `PROJECT_STATE.md` (updated Milestone 2.5)
  - `docs/AI_AGENT_RULES_AND_LESSONS.md` (added 11 durable principles)
  - `reports/REPORT_INDEX.md` (indexed final report)
  - `reports/GOVERNANCE_FINAL_ACCEPTANCE_REPORT.md` (this report)
  - `reports/AG_LIVE_PROGRESS.md` & `reports/AG_RUN_STATE.json` (milestone updates)

---

## 14. Final Readiness Classification

### **READY_WITH_EXPLICIT_LIMITATIONS**

**Rationale:**  
The Lesson/Rule/Event governance architecture is fully verified, hardened against bypass, integrated into the experiment workflow, and backed by a 109-assertion automated test suite with zero failures. It is ready to support the next research phase (ProteinMPNN baseline integration) subject to the four explicit limitations detailed in Section 12.
