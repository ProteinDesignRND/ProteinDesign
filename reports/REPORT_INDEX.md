# Report Index

## Active Reports (Current Truth)

| Document | Path | Purpose |
| :--- | :--- | :--- |
| **Project Truth** | `docs/PROJECT_TRUTH.md` | Single source of truth for verified facts, limitations, and hypotheses |
| **Phase 1 Reproduction** | `reports/PHASE1_PROTEINSOLVER_REPRODUCTION.md` | Complete E0 verification and hardening report |
| **Provenance Manifest** | `reports/PROTEINSOLVER_PROVENANCE_MANIFEST.md` | Exact commit, hashes, environment, and compatibility layer documentation |
| **Paper vs. Implementation** | `reports/paper_vs_implementation.md` | Systematic audit of paper claims vs. code reality |
| **Transition Gate Report** | `reports/FINAL_FOUNDATION_INTEGRITY_AND_TRANSITION_GATE_REPORT.md` | Authoritative final foundation integrity and transition-gate report (**Sole Current Transition Authority**) |
| **Governance Release Gate** | `reports/GOVERNANCE_RELEASE_GATE_REPORT.md` | Foundation freeze audit report (**Foundation Freeze Authority**) |

## Reference Documents (Supporting Evidence)

| Document | Path | Purpose |
| :--- | :--- | :--- |
| **Research Paper Audit** | `research/paper_vs_implementation.md` | Earlier version of paper/code audit (pre-hardening). Kept as reference. |
| **Code Audit** | `research/proteinsolver_code_audit.md` | Detailed source code walkthrough |
| **Data Schema** | `research/proteinsolver_data_schema.md` | Dataset format and schema documentation |
| **Literature Matrix** | `research/literature_matrix.csv` | Structured literature review data |
| **Novelty Matrix** | `research/novelty_matrix.csv` | Prior art and novelty gap analysis |
| **Research Gap** | `research/research_gap.md` | Identified research gaps and opportunities |
| **Research Questions** | `research/research_questions.md` | Formulated research questions |
| **Rejected Directions** | `research/rejected_directions.md` | Directions explicitly ruled out with reasons |

## Experimental Evidence

| Experiment | Path | Status | Key Result |
| :--- | :--- | :--- | :--- |
| **EXP000** | `experiments/EXP000_PROTEINSOLVER_SMOKETEST/` | COMPLETE | Initial checkpoint loading and forward pass verification |
| **EXP001** | `experiments/EXP001_PROTEINSOLVER_INFERENCE/` | COMPLETE | 1n5uA03 all-masked design: 41.30% recovery (38/92) |
| **EXP004** | `experiments/EXP004_MASK_INVARIANCE/` | COMPLETE | Mask invariance verified (logit diff = 0.0), information leak demonstrated |

## Superseded Documents

| Document | Path | Superseded By | Notes |
| :--- | :--- | :--- | :--- |
| `research/paper_vs_implementation.md` | `research/` | `reports/paper_vs_implementation.md` | Earlier version of the audit. Contains useful code-level detail but uses some overclaiming language that was corrected in the reports/ version. Preserved as historical reference. |
| `reports/FOUNDATION_HANDOFF_REPORT.md` | `reports/` | `reports/GOVERNANCE_RELEASE_GATE_REPORT.md` | Earlier team handoff report (v0.1) from branch `foundation/team-handoff-v0.1`. Preserved as historical evidence of pre-governance handoff. Superseded by the Governance Release Gate Report as freeze authority. |
| `reports/GOVERNANCE_FOUNDATION_CLOSURE_REPORT.md` | `reports/` | `reports/GOVERNANCE_RELEASE_GATE_REPORT.md` | Initial governance closure report. Preserved as historical evidence. Superseded by the Governance Release Gate Report. |
| `reports/GOVERNANCE_FINAL_ACCEPTANCE_REPORT.md` | `reports/` | `reports/GOVERNANCE_RELEASE_GATE_REPORT.md` | Final red-team acceptance report. Preserved as historical evidence. Superseded by the Governance Release Gate Report. |

## Governance

| Document | Path | Purpose |
| :--- | :--- | :--- |
| **Architecture** | `governance/ARCHITECTURE.md` | Governance system design: Lesson/Rule/Event schemas, preflight, constraints |
| **Lessons** | `governance/data/lessons.json` | All project lessons (6 seeded from Phase 1 failures) |
| **Rules** | `governance/data/rules.json` | All governance rules (8 core rules) |
| **Events** | `governance/data/events.jsonl` | Append-only audit trail |
| **Preflight CLI** | `governance/preflight_cli.py` | Command-line preflight check tool |
| **Tests** | `tests/test_governance.py` | Comprehensive test suite (109 assertions across 25 pytest test suites) |
| **Transition Gate Report** | `reports/FINAL_FOUNDATION_INTEGRITY_AND_TRANSITION_GATE_REPORT.md` | Authoritative final foundation integrity and transition-gate report (**Sole Current Transition Authority**) |
| **Release Gate Report** | `reports/GOVERNANCE_RELEASE_GATE_REPORT.md` | Final release-gate audit and foundation freeze report (**Foundation Freeze Authority**) |
| **Final Acceptance Report** | `reports/GOVERNANCE_FINAL_ACCEPTANCE_REPORT.md` | Final red-team acceptance report (Historical; superseded by Release Gate Report) |
| **Foundation Closure** | `reports/GOVERNANCE_FOUNDATION_CLOSURE_REPORT.md` | Foundation closure report (Historical; superseded by Release Gate Report) |

## Live Progress

| Document | Path | Purpose |
| :--- | :--- | :--- |
| **Live Progress** | `reports/AG_LIVE_PROGRESS.md` | Human-readable progress tracker |
| **Run State JSON** | `reports/AG_RUN_STATE.json` | Machine-readable progress state |

