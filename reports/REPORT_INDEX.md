# Report Index

## 1. Current Truth & Model Specifications
| Document | Path | Purpose | Authority Scope |
| :--- | :--- | :--- | :--- |
| **Project Truth** | `docs/PROJECT_TRUTH.md` | Single source of truth for verified facts, limitations, and hypotheses | **Global Project Authority** |
| **Original ProteinSolver Specification** | `science/original_proteinsolver.md` | Authoritative, source-grounded model architecture, featurization, and dataset specifications | **Original Model Specification Authority** |
| **ProteinSolver R1 Final Evidence Closure Report** | `reports/PROTEINSOLVER_R1_2_2_FINAL_EVIDENCE_CLOSURE.md` | Final authoritative reconciliation closing Phase R1 (evidence graph, figure crosswalk, experiment classifications, R2 gate) | **Phase R1 Authoritative Closure Gate** |
| **ProteinSolver R2 Figure 2B & 2C Computational Reproduction Report** | `reports/PROTEINSOLVER_R2_FIG2BC_REPRODUCTION_REPORT.md` | Authoritative computational reproduction of Figure 2B & 2C decoding, legacy data-route verification, and auxiliary evaluation (Phase R2 Closure Status: `R2_PARTIAL`) | **Phase R2 Authoritative Closure Gate** |

## 2. Transition & Evaluation Authorities
| Document | Path | Purpose | Authority Scope |
| :--- | :--- | :--- | :--- |
| **Final Pre-E1 Scientific Readiness Reconciliation Report (V2)** | `reports/FINAL_PRE_E1_SCIENTIFIC_READINESS_RECONCILIATION_V2.md` | Final pre-E1 surgical reconciliation pass: manifest verification, LF hash canonicalization, scTM boundary, hydrophobic core formalization, and AI authorization clarification | **Current Pre-E1 Protocol & Readiness Authority** |
| **Final Pre-E1 Scientific Readiness Closure Report** | `reports/FINAL_PRE_E1_SCIENTIFIC_READINESS_CLOSURE_REPORT.md` | Pre-E1 scientific readiness, manifest freeze, infeasibility rule, and consistency closure report | **Pre-E1 Closure Baseline Authority** |
| **Development Hyperparameter Selection Freeze Report** | `reports/DEVELOPMENT_HYPERPARAMETER_SELECTION_FREEZE_REPORT.md` | Freeze of development objective $J$, Cartesian grids, freezing order, and tie breaking | **Development Hyperparameter Selection Authority** |
| **ProteinMPNN Counterfactual Leakage Audit Report** | `reports/PROTEINMPNN_COUNTERFACTUAL_LEAKAGE_AUDIT_REPORT.md` | Verification of native-sequence invariance under counterfactual inputs in tested fully-designed mask configuration | **Cleanroom Integration Leakage Authority** |
| **Transition Gate Report** | `reports/FINAL_FOUNDATION_INTEGRITY_AND_TRANSITION_GATE_REPORT.md` | Final foundation integrity and transition-gate report | **Historical Foundation Transition Authority** |
| **Protocol Freeze & Readiness Gate Report** | `reports/FINAL_SCIENTIFIC_PROTOCOL_FREEZE_AND_READINESS_GATE_REPORT.md` | Authoritative protocol freeze, Claude 2.0 audit disposition, and final readiness gate report | **Historical Protocol Freeze Authority** |
| **Study Pre-Registration** | `science/PREREGISTRATION.md` | Pre-registered freeze of all currently registered protocol elements under Amendment A1 prior to experimentation | **Study Pre-Registration Authority** |
| **Scientific Metrics & Evaluation Integrity Report** | `reports/FINAL_SCIENTIFIC_METRICS_AND_EVALUATION_INTEGRITY_REPORT.md` | Audit of mathematical definitions, non-tautological viability, and oracle separation | **Scientific Protocol & Metrics Authority** |
| **Governance Release Gate** | `reports/GOVERNANCE_RELEASE_GATE_REPORT.md` | Foundation freeze audit and red-team closure | **Foundation Freeze Authority** |

## 3. Active Scientific Evidence
| Document | Path | Purpose | Role |
| :--- | :--- | :--- | :--- |
| **Master Reproduction Audit (Phase R1)** | `reports/PROTEINSOLVER_MASTER_REPRODUCTION_AUDIT_R1.md` | Comprehensive paper-to-code-to-data reconciliation, master matrix, and execution history | **Supporting Reproduction Matrix** |
| **ProteinMPNN Provenance Manifest** | `reports/PROTEINMPNN_PROVENANCE_MANIFEST.md` | Official ProteinMPNN commit, weights hashes, cleanroom architecture, and interface verification | Supporting Evidence |
| **Phase 1 Reproduction** | `reports/PHASE1_PROTEINSOLVER_REPRODUCTION.md` | Complete E0 verification and hardening report | Supporting Evidence |
| **Provenance Manifest** | `reports/PROTEINSOLVER_PROVENANCE_MANIFEST.md` | Exact commit, hashes, environment, and compatibility layer documentation | Supporting Evidence |
| **Paper vs. Implementation** | `reports/paper_vs_implementation.md` | Systematic audit of paper claims vs. code reality | Supporting Evidence |

## 4. Experimental Evidence
| Experiment | Path | Status | Evidence Classification | Key Result |
| :--- | :--- | :--- | :--- | :--- |
| **EXP000** | `experiments/EXP000_PROTEINSOLVER_SMOKETEST/` | COMPLETE | `INTEGRATION_FIXTURE_VERIFIED` | Initial checkpoint loading and forward pass verification |
| **EXP001** | `experiments/EXP001_PROTEINSOLVER_INFERENCE/` | COMPLETE | `INTEGRATION_FIXTURE_VERIFIED` | 1n5uA03 all-masked design: 41.30% recovery (38/92) |
| **EXP004** | `experiments/EXP004_MASK_INVARIANCE/` | COMPLETE | `RAW_DATA_RECOMPUTED` | In tested all-masked setup, max logit diff = 0.0; information leak documented |
| **EXP005** | `experiments/EXP005_PROTHERM_REPRODUCTION/` | COMPLETE | `PARTIAL_RECOMPUTATION / RECONSTRUCTION_FROM_PRESERVED_NOTEBOOK_STATISTICS` | ProTherm mutation stability (Fig 2D): Rosetta recomputed ($N=3,471$, 10k bootstrap $\rho=-0.008$); PS preserved ($\rho=0.444$) |
| **EXP006** | `experiments/EXP006_ROCKLIN_STABILITY_REPRODUCTION/` | COMPLETE | `RECONSTRUCTION_FROM_PRESERVED_NOTEBOOK_STATISTICS` | De novo protein stability (Fig 2F) across 4 topologies & rounds 1-4; EEHEE Rd 4 exception documented ($\rho_{PS}=-0.14, \rho_{Rosetta}=-0.40$) |
| **EXP007** | `experiments/EXP007_BESTSEL_CD_REPRODUCTION/` | COMPLETE | `RECONSTRUCTION_FROM_PRESERVED_BESTSEL_OUTPUTS` | BeStSel CD secondary structure deconvolution (STAR Step 19); 1n5u $p > 0.05$ (no difference detected); 4beu $N=1$ descriptive only |
| **EXP008** | `experiments/EXP008_FOUR_TARGET_INTEGRATION_FIXTURE/` | COMPLETE | `INTEGRATION_FIXTURE_VERIFIED` | Multi-target inverse folding design fixture on 4 folds (92, 217, 109, 96 AA); full 2.4M generation cost unbenchmarked |
| **R2_FIG2BC_REPRODUCTION** | `experiments/R2_FIG2BC_REPRODUCTION/` | COMPLETE | `AUXILIARY_EVALUATION_WITH_HISTORICAL_EVIDENCE_RECONSTRUCTION` | Figure 2B single-pass (38.59%) vs iterative MAP (39.77%); Figure 2C conditioning (0% -> 39.77%, 50% -> 40.93%, 80% -> 41.67%); legacy host active with expired TLS cert; full 10k dataset resource-bounded across 172 superfamilies |

*Note on Status Terminology:* "COMPLETE" in the table above denotes that the local computational execution of the experimental run finished. It does NOT imply full paper reproduction. In particular, for `R2_FIG2BC_REPRODUCTION`, the scientific reproduction status is `R2_PARTIAL_VERIFIED_ON_AUXILIARY_POPULATION_WITH_HISTORICAL_EVIDENCE_RECONSTRUCTION` due to the historical 10,000-instance Gene3D test dataset being unavailable on current artifacts.

## 5. Governance Architecture & Tools
| Document | Path | Purpose |
| :--- | :--- | :--- |
| **Architecture** | `governance/ARCHITECTURE.md` | Governance system design: Lesson/Rule/Event schemas, preflight, constraints |
| **Lessons** | `governance/data/lessons.json` | Project lessons (seeded from Phase 1 failures and R1 audits) |
| **Rules** | `governance/data/rules.json` | Governance rules (8 core rules) |
| **Events** | `governance/data/events.jsonl` | Append-only audit trail |
| **Preflight CLI** | `governance/preflight_cli.py` | Command-line preflight check tool |
| **Tests** | `tests/test_governance.py` | Comprehensive test suite (81 pytest test cases passed) |

## 6. Historical / Superseded Documents (Supporting Evidence Only)
*The following documents are preserved for historical provenance and auditability. They are superseded by the authorities above and must not be used as primary truth sources.*

| Document | Path | Superseded By | Historical Context |
| :--- | :--- | :--- | :--- |
| `reports/PROTEINSOLVER_R1_2_1_FINAL_RECONCILIATION.md` | `reports/` | `reports/PROTEINSOLVER_R1_2_2_FINAL_EVIDENCE_CLOSURE.md` | Intermediate R1.2.1 pass; superseded by the authoritative R1.2.2 evidence closure report. |
| `research/paper_vs_implementation.md` | `research/` | `reports/paper_vs_implementation.md` | Early pre-hardening audit draft. Preserved for code-level notes; superseded by the reports/ version. |
| `reports/FOUNDATION_HANDOFF_REPORT.md` | `reports/` | `reports/GOVERNANCE_RELEASE_GATE_REPORT.md` | Earlier team handoff report (v0.1) from branch `foundation/team-handoff-v0.1`. |
| `reports/GOVERNANCE_FOUNDATION_CLOSURE_REPORT.md` | `reports/` | `reports/GOVERNANCE_RELEASE_GATE_REPORT.md` | Initial governance closure report; superseded by Release Gate Report. |
| `reports/GOVERNANCE_FINAL_ACCEPTANCE_REPORT.md` | `reports/` | `reports/GOVERNANCE_RELEASE_GATE_REPORT.md` | Red-team acceptance report; superseded by Release Gate Report. |

## 7. Live Progress Tracking
| Document | Path | Purpose |
| :--- | :--- | :--- |
| **Live Progress** | `reports/AG_LIVE_PROGRESS.md` | Human-readable progress tracker |
| **Run State JSON** | `reports/AG_RUN_STATE.json` | Machine-readable progress state |
