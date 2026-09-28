# Report Index

## 1. Current Truth
| Document | Path | Purpose |
| :--- | :--- | :--- |
| **Project Truth** | `docs/PROJECT_TRUTH.md` | Single source of truth for verified facts, limitations, and hypotheses |

## 2. Transition & Evaluation Authorities
| Document | Path | Purpose | Authority Scope |
| :--- | :--- | :--- | :--- |
| **Final Pre-E1 Scientific Readiness Reconciliation Report (V2)** | `reports/FINAL_PRE_E1_SCIENTIFIC_READINESS_RECONCILIATION_V2.md` | Final pre-E1 surgical reconciliation pass: manifest verification, LF hash canonicalization, scTM boundary, hydrophobic core formalization, and AI authorization clarification | **Current Pre-E1 Protocol & Readiness Authority** |
| **Final Pre-E1 Scientific Readiness Closure Report** | `reports/FINAL_PRE_E1_SCIENTIFIC_READINESS_CLOSURE_REPORT.md` | Pre-E1 scientific readiness, manifest freeze, infeasibility rule, and consistency closure report | **Pre-E1 Closure Baseline Authority** |
| **Development Hyperparameter Selection Freeze Report** | `reports/DEVELOPMENT_HYPERPARAMETER_SELECTION_FREEZE_REPORT.md` | Freeze of development objective $J$, Cartesian grids, freezing order, and tie breaking | **Development Hyperparameter Selection Authority** |
| **ProteinMPNN Counterfactual Leakage Audit Report** | `reports/PROTEINMPNN_COUNTERFACTUAL_LEAKAGE_AUDIT_REPORT.md` | Verification of 100% native-sequence invariance under counterfactual inputs | **Cleanroom Integration Leakage Authority** |
| **Transition Gate Report** | `reports/FINAL_FOUNDATION_INTEGRITY_AND_TRANSITION_GATE_REPORT.md` | Final foundation integrity and transition-gate report | **Historical Foundation Transition Authority** |
| **Protocol Freeze & Readiness Gate Report** | `reports/FINAL_SCIENTIFIC_PROTOCOL_FREEZE_AND_READINESS_GATE_REPORT.md` | Authoritative protocol freeze, Claude 2.0 audit disposition, and final readiness gate report | **Historical Protocol Freeze Authority** |
| **Study Pre-Registration** | `science/PREREGISTRATION.md` | Pre-registered freeze of all 24 study parameters prior to experimentation | **Study Pre-Registration Authority** |
| **Scientific Metrics & Evaluation Integrity Report** | `reports/FINAL_SCIENTIFIC_METRICS_AND_EVALUATION_INTEGRITY_REPORT.md` | Audit of mathematical definitions, non-tautological viability, and oracle separation | **Scientific Protocol & Metrics Authority** |
| **Governance Release Gate** | `reports/GOVERNANCE_RELEASE_GATE_REPORT.md` | Foundation freeze audit and red-team closure | **Foundation Freeze Authority** |

## 3. Active Scientific Evidence
| Document | Path | Purpose |
| :--- | :--- | :--- |
| **ProteinMPNN Provenance Manifest** | `reports/PROTEINMPNN_PROVENANCE_MANIFEST.md` | Official ProteinMPNN commit, weights hashes, cleanroom architecture, and interface verification |
| **Phase 1 Reproduction** | `reports/PHASE1_PROTEINSOLVER_REPRODUCTION.md` | Complete E0 verification and hardening report |
| **Provenance Manifest** | `reports/PROTEINSOLVER_PROVENANCE_MANIFEST.md` | Exact commit, hashes, environment, and compatibility layer documentation |
| **Paper vs. Implementation** | `reports/paper_vs_implementation.md` | Systematic audit of paper claims vs. code reality |

## 4. Experimental Evidence
| Experiment | Path | Status | Key Result |
| :--- | :--- | :--- | :--- |
| **EXP000** | `experiments/EXP000_PROTEINSOLVER_SMOKETEST/` | COMPLETE | Initial checkpoint loading and forward pass verification |
| **EXP001** | `experiments/EXP001_PROTEINSOLVER_INFERENCE/` | COMPLETE | 1n5uA03 all-masked design: 41.30% recovery (38/92) |
| **EXP004** | `experiments/EXP004_MASK_INVARIANCE/` | COMPLETE | In tested all-masked setup, max logit diff = 0.0; information leak documented |

## 5. Governance Architecture & Tools
| Document | Path | Purpose |
| :--- | :--- | :--- |
| **Architecture** | `governance/ARCHITECTURE.md` | Governance system design: Lesson/Rule/Event schemas, preflight, constraints |
| **Lessons** | `governance/data/lessons.json` | Project lessons (seeded from Phase 1 failures) |
| **Rules** | `governance/data/rules.json` | Governance rules (8 core rules) |
| **Events** | `governance/data/events.jsonl` | Append-only audit trail |
| **Preflight CLI** | `governance/preflight_cli.py` | Command-line preflight check tool |
| **Tests** | `tests/test_governance.py` | Comprehensive test suite (109 assertions across 25 pytest test suites) |

## 6. Historical / Superseded Documents (Supporting Evidence Only)
*The following documents are preserved for historical provenance and auditability. They are superseded by the authorities above and must not be used as primary truth sources.*

| Document | Path | Superseded By | Historical Context |
| :--- | :--- | :--- | :--- |
| `research/paper_vs_implementation.md` | `research/` | `reports/paper_vs_implementation.md` | Early pre-hardening audit draft. Preserved for code-level notes; superseded by the reports/ version. |
| `reports/FOUNDATION_HANDOFF_REPORT.md` | `reports/` | `reports/GOVERNANCE_RELEASE_GATE_REPORT.md` | Earlier team handoff report (v0.1) from branch `foundation/team-handoff-v0.1`. |
| `reports/GOVERNANCE_FOUNDATION_CLOSURE_REPORT.md` | `reports/` | `reports/GOVERNANCE_RELEASE_GATE_REPORT.md` | Initial governance closure report; superseded by Release Gate Report. |
| `reports/GOVERNANCE_FINAL_ACCEPTANCE_REPORT.md` | `reports/` | `reports/GOVERNANCE_RELEASE_GATE_REPORT.md` | Red-team acceptance report; superseded by Release Gate Report. |

## 7. Live Progress Tracking
| Document | Path | Purpose |
| :--- | :--- | :--- |
| **Live Progress** | `reports/AG_LIVE_PROGRESS.md` | Human-readable progress tracker |
| **Run State JSON** | `reports/AG_RUN_STATE.json` | Machine-readable progress state |


