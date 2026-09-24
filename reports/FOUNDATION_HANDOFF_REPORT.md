# Foundation Handoff Report

**Version:** v0.1  
**Date:** 2026-09-24  
**Branch:** `foundation/team-handoff-v0.1`  
**Agent:** Claude Opus 4.6 (via Antigravity IDE)  

---

## 1. Project Purpose

This is a computational biology research project investigating whether ProteinSolver (a 2020 GNN-based protein sequence design model) can complement modern inverse-folding models (e.g., ProteinMPNN) through multi-objective candidate selection.

The project is a controlled scientific investigation, not a software product.

## 2. What Has Been Established

### Verified Baseline: ProteinSolver

| Property | Value | Status |
| :--- | :--- | :--- |
| Historical repository | Commit `69ef0965`, working tree clean | `VERIFIED` |
| Published checkpoint | `e53-s1952148-d93703104.state`, SHA-256: `1E8272F0...` | `VERIFIED` |
| Model architecture | 4-block residual EdgeConv GNN, 567,060 parameters | `VERIFIED` |
| Checkpoint loading | `strict=True`, 0 missing, 0 unexpected keys (after documented key mapping) | `VERIFIED` |
| All-masked design on 1n5uA03 | 41.30% native identity (38/92 residues), 1.77s CPU | `VERIFIED` |
| Mask invariance | max logit diff = 0.0 on all-masked input | `VERIFIED` |
| Feature pipeline (1n5uA03) | Cleanroom extractor matches original repo (max diff: 0.0) | `VERIFIED` |
| Information leak mechanism | `data.y` triggers reference copying, not real recovery | `VERIFIED` |
| Historical source files | Zero modifications in `external/proteinsolver-original/` | `VERIFIED` |

### Equivalence Classification

**FUNCTIONALLY REPRODUCED WITH MODERN COMPATIBILITY ADAPTATION**

This means:
- The original model architecture, checkpoint, and design algorithm execute correctly.
- Six compatibility issues were resolved via external adapters (no historical source changes).
- Historical runtime numerical equivalence (Python 3.6 / PyG 1.3 / Linux) has NOT been tested.

## 3. Errors and Inconsistencies Discovered

| Issue | Resolution | Status |
| :--- | :--- | :--- |
| Initial "100% recovery" was information leak via `data.y` | Correctly classified as diagnostic scoring; documented in EXP004 | `CORRECTED` |
| Overclaim: "Mathematical fidelity is 100% preserved" | Scoped to tested target; general kmbio/Biopython equivalence marked NOT VERIFIED | `CORRECTED` |
| Unscoped "numerically identical" claims in CLAIMS_REGISTRY, PROJECT_STATE, PHASE1 report, and provenance manifest | Added target-specific qualifiers (1n5uA03) to all occurrences | `CORRECTED` |
| `research/paper_vs_implementation.md` duplicates `reports/paper_vs_implementation.md` | Research version marked SUPERSEDED; reports version is authoritative | `CORRECTED` |

## 4. Corrections Made During This Phase

1. Fixed `research/paper_vs_implementation.md` line 78: removed "Mathematical fidelity is 100% preserved"
2. Fixed `reports/paper_vs_implementation.md` line 37: scoped kmbio/Biopython claim to 1n5uA03
3. Fixed `reports/PROTEINSOLVER_PROVENANCE_MANIFEST.md` line 120: scoped cleanroom extractor claim
4. Fixed `PROJECT_STATE.md` line 59: added target qualifier
5. Fixed `CLAIMS_REGISTRY.md` V-15: scoped feature pipeline claim
6. Fixed `reports/PHASE1_PROTEINSOLVER_REPRODUCTION.md` line 24: scoped feature pipeline equivalence claim
7. Added SUPERSEDED notice to `research/paper_vs_implementation.md`

## 5. Remaining Scientific Limitations

| Limitation | Classification |
| :--- | :--- |
| Historical runtime numerical equivalence not tested | `NOT VERIFIABLE` (without historical environment) |
| kmbio/Biopython general parser equivalence | `NOT VERIFIED` |
| 1n5uA03 training set membership | `NOT VERIFIABLE FROM ACCESSIBLE METADATA` |
| 41.30% is single-target, not benchmark | `EXPLICIT LIMITATION` |
| CUDA iterative design under PyTorch 2.6 | `BLOCKED` (cross-device indexing) |
| Commit 69ef0965 may differ from exact 2020 paper state | `NOT VERIFIABLE` |

## 6. What Is Intentionally Deferred

- ProteinMPNN integration and baseline — Workstream B
- Multi-target benchmark evaluation — depends on Workstreams A+B
- Structural validation pipeline (ESMFold/AlphaFold) — Workstream C
- Candidate selection / multi-objective analysis — Workstream D
- Statistical analysis and visualization — Workstream E
- Training / fine-tuning
- UI / cloud infrastructure / Docker

## 7. Repository Structure

```
Protein Design/
├── docs/                              # Team documentation
│   ├── PROJECT_TRUTH.md              # Single source of truth
│   ├── AI_AGENT_RULES_AND_LESSONS.md # AI agent rules and lessons
│   ├── TEAM_ONBOARDING.md           # New teammate onboarding
│   └── TEAM_WORKSTREAMS.md          # Work division
├── external/
│   └── proteinsolver-original/       # Historical repo (DO NOT MODIFY)
├── environment/
│   └── proteinsolver-original/       # Python virtualenv (gitignored)
├── src/
│   └── proteinsolver_baseline/       # Cleanroom wrapper
├── experiments/
│   ├── TEMPLATE/                     # Template for new experiments
│   ├── EXP000_PROTEINSOLVER_SMOKETEST/
│   ├── EXP001_PROTEINSOLVER_INFERENCE/
│   └── EXP004_MASK_INVARIANCE/
├── reports/                          # Analysis reports
│   ├── REPORT_INDEX.md              # Index of all reports
│   ├── PHASE1_PROTEINSOLVER_REPRODUCTION.md
│   ├── PROTEINSOLVER_PROVENANCE_MANIFEST.md
│   ├── paper_vs_implementation.md
│   ├── FOUNDATION_HANDOFF_REPORT.md  # This file
│   ├── AG_LIVE_PROGRESS.md          # Live progress tracker
│   └── AG_RUN_STATE.json            # Machine-readable state
├── research/                         # Literature and analysis
├── science/                          # Evaluation protocol
├── architecture/                     # Architecture documentation
├── scripts/
│   └── show_progress.ps1            # Progress display script
├── CLAIMS_REGISTRY.md
├── DECISION_LOG.md
├── PROJECT_STATE.md
├── CONTRIBUTING.md
├── AI_TEAM.md
├── RESEARCH_PROTOCOL.md
├── .gitignore
└── test_original_execution.py        # Phase 1 verification suite
```

## 8. Team Onboarding

New teammates should read, in order:
1. `docs/TEAM_ONBOARDING.md` — project context, setup, pitfalls
2. `docs/PROJECT_TRUTH.md` — verified facts vs. hypotheses
3. `docs/TEAM_WORKSTREAMS.md` — work division
4. `docs/AI_AGENT_RULES_AND_LESSONS.md` — rules for AI agents
5. `CONTRIBUTING.md` — git workflow and experiment standards

## 9. Team Workstreams

| Workstream | Focus | Status |
| :--- | :--- | :--- |
| A | Research Lead / Integration | ACTIVE (foundation complete) |
| B | Modern Inverse-Folding Baselines | NOT STARTED |
| C | Structural Validation | NOT STARTED |
| D | Candidate Selection / Multi-Objective | NOT STARTED |
| E | Evaluation / Statistics / Visualization | NOT STARTED |

## 10. Experiment Conventions

Copy `experiments/TEMPLATE/` for every new experiment. Required files: `README.md`, `config.json`, `run.py`, `input/`, `output/`, `metrics.json`, `run_log.txt`, `environment.txt`.

## 11. AI Team Model

| System | Role |
| :--- | :--- |
| Antigravity (Gemini) | Local execution, repository, coding |
| Perplexity | Literature search, source verification |
| Claude | Independent scientific red-team |
| ChatGPT | Research strategy, hypothesis design |
| OpenRouter | Optional second opinion |

One system modifies the repository at a time. Independent systems challenge conclusions.

## 12. Live Progress

- `reports/AG_LIVE_PROGRESS.md` — human-readable
- `reports/AG_RUN_STATE.json` — machine-readable
- `scripts/show_progress.ps1` — CLI display

## 13. Git Workflow

- Branch: `research/ai-research-bootstrap` (current working branch)
- Feature branches: `feature/<name>`, experiment branches: `experiment/<id>`
- No force-pushing, no direct pushes without review
- See `CONTRIBUTING.md` for details

## 14. Current Research Question

> *"Does ProteinSolver's distance-graph constraint-satisfaction scoring provide orthogonal structural signal that improves modern inverse-folding candidate selection, or does modern inverse folding combined with structural validation dominate hybrid selection?"*

This is a two-sided question. ProteinSolver complementarity is a HYPOTHESIS, not an established fact.

## 15. Next Scientific Phase

The next phase is: **Comparative evaluation framework + ProteinMPNN baseline** (Workstreams A+B).

This phase was intentionally NOT started during foundation hardening.

## 16. Git State at Handoff

- **Branch:** `foundation/team-handoff-v0.1`
- **Parent branch:** `research/ai-research-bootstrap` (commit `4af496f`)
- **Remote:** No remote configured
- **Push status:** DEFERRED (no remote to push to)
- **Historical repo:** CLEAN (zero modifications)

## 17. Human Action Required

1. Review this handoff report.
2. Configure a git remote if team collaboration is needed.
3. Push `foundation/team-handoff-v0.1` to the remote when ready.
4. Assign workstream owners.
5. Begin Workstream B (ProteinMPNN baseline).

## 18. Confirmation

- [x] ProteinMPNN was NOT implemented
- [x] No new research experiments were started
- [x] No training was performed
- [x] No unnecessary infrastructure was created
- [x] Historical ProteinSolver source was NOT modified
- [x] All existing baseline artifacts were preserved
