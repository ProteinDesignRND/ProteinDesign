# Report Index

## Active Reports (Current Truth)

| Document | Path | Purpose |
| :--- | :--- | :--- |
| **Project Truth** | `docs/PROJECT_TRUTH.md` | Single source of truth for verified facts, limitations, and hypotheses |
| **Phase 1 Reproduction** | `reports/PHASE1_PROTEINSOLVER_REPRODUCTION.md` | Complete E0 verification and hardening report |
| **Provenance Manifest** | `reports/PROTEINSOLVER_PROVENANCE_MANIFEST.md` | Exact commit, hashes, environment, and compatibility layer documentation |
| **Paper vs. Implementation** | `reports/paper_vs_implementation.md` | Systematic audit of paper claims vs. code reality |
| **Foundation Handoff** | `reports/FOUNDATION_HANDOFF_REPORT.md` | Team handoff summary and remaining actions |

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

## Live Progress

| Document | Path | Purpose |
| :--- | :--- | :--- |
| **Live Progress** | `reports/AG_LIVE_PROGRESS.md` | Human-readable progress tracker |
| **Run State JSON** | `reports/AG_RUN_STATE.json` | Machine-readable progress state |
