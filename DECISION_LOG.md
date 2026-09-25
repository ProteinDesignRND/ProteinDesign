# DECISION LOG

This document chronologically logs all major architectural, methodological, and scientific decisions made during the lifecycle of the project. Every entry includes context, alternatives considered, rationale, and consequences.

---

## [DEC-001] Git Version Control & Branch Isolation Strategy
- **Date:** 2026-09-24
- **Decision:** Initialize a clean git repository in `d:/Projects/Protein Design` and check out dedicated branch `research/ai-research-bootstrap`.
- **Context:** The workspace directory was initialized empty without existing version control or legacy files.
- **Alternatives Considered:** Working on `main`/`master` directly.
- **Rationale:** Strict safety protocol requires isolating all exploratory scaffolding, literature matrices, and initial audits on a dedicated feature branch before merging into `main`.
- **Consequences:** All subsequent commits are tracked under `research/ai-research-bootstrap`.

---

## [DEC-002] Hypothesis Classified as Strictly Provisional
- **Date:** 2026-09-24
- **Decision:** Formalize the candidate hypothesis (*ProteinSolver complementing modern inverse-folding models via diversity-aware multi-objective selection*) as PROVISIONAL (`[HYPOTHESIS]`), prohibiting any assumption of novelty or effectiveness.
- **Context:** Literature review reveals that modern models (ProteinMPNN, PiFold) achieve substantially higher sequence recovery (~51% vs ~33%) than ProteinSolver.
- **Alternatives Considered:** Accepting the hypothesis as the definitive project foundation.
- **Rationale:** An AI executor must never assume that an older, lower-performing model automatically complements a modern state-of-the-art model without rigorous empirical evidence. Naive combinations frequently cause performance degradation.
- **Consequences:** The evaluation protocol must explicitly measure whether ProteinSolver adds orthogonal signal or acts as destructive noise.

---

## [DEC-003] Deconstruction of Pipeline Novelty
- **Date:** 2026-09-24
- **Decision:** Explicitly mark the pipeline `Inverse Folding + AlphaFold Validation` as prior art (`[REJECTED]` from novelty claims).
- **Context:** Watson et al. (*Nature* 2023, RFdiffusion) and hundreds of subsequent studies have established ProteinMPNN + AlphaFold2 self-consistency filtering (scRMSD < 2.0 Å, pLDDT > 80) as the canonical community baseline.
- **Alternatives Considered:** Claiming the structural validation pipeline itself as part of our novelty.
- **Rationale:** Claiming novelty on standard pipelines destroys scientific credibility. The candidate novelty must be strictly confined to:
  1. The specific interaction / ensembling between distance-graph constraint models (ProteinSolver) and coordinate-invariant MPNNs (ProteinMPNN), and
  2. The algorithmic formulation of diversity-aware, multi-objective candidate selection (Pareto ranking across confidence, stability proxy, and pairwise diversity).
- **Consequences:** Benchmarks must use the canonical Baker Lab RFdiffusion/ProteinMPNN + AF2 pipeline as a baseline control, not as our claimed invention.

---

## [DEC-004] Compute & Data Constraint: No Full Model Retraining
- **Date:** 2026-09-24
- **Decision:** Forbid retraining ProteinSolver from scratch on the 72M Gene3D corpus; utilize official pretrained weights (`ostrokach/proteinsolver` model checkpoints) and focus on inference-time ensembling, rescoring, and candidate selection.
- **Context:** Retraining ProteinSolver on 72M sequence-structure pairs requires hundreds of GPU-hours and extensive cluster storage, offering negligible scientific insight compared to evaluating inference-time complementarity.
- **Alternatives Considered:** Retraining on a miniature toy subset.
- **Rationale:** The scientific question is about the *information content* and *scoring properties* of the trained model, which is best evaluated using the authors' published, canonical weights.
- **Consequences:** Massive reduction in compute overhead; enables focused execution of controlled inference experiments.

---

## [DEC-005] Resolution of PyG 2.x and Python 3.11 Compatibility without Modifying Historical Source
- **Date:** 2026-09-24
- **Decision:** Preserve the original historical source in `external/proteinsolver-original` 100% untouched; resolve all modern PyG 2.x, PyTorch 2.6, and Python 3.11 incompatibilities via external caller-side wrappers and minimal runtime shims.
- **Context:** Modern environments lack legacy `kmbio` (Python 3.5/3.6 only), Windows lacks `fcntl`, PyG 2.x sets `Data.batch = None` causing `batch.max()` crashes in `design_sequence`, and PyG 2.x removed `torch_geometric.utils.scatter_`.
- **Alternatives Considered:** Permanently editing/patching historical repository source files.
- **Rationale:** Modifying historical source risks introducing undocumented divergence from original publication benchmarks. Wrapping input graphs with `Batch.from_data_list([data])` and providing an external scatter shim cleanly satisfies all runtime contracts.
- **Consequences:** Verifiable execution of original `ProteinNet` and original `design_sequence` with clean provenance.

---

## [DEC-006] Strict Separation of Native Sequence Diagnostic Likelihood from Valid Inverse-Folding Recovery
- **Date:** 2026-09-24
- **Decision:** Formally classify any experiment supplying the native sequence to `design_sequence` as *diagnostic scoring / likelihood evaluation*, strictly reserving the term *native sequence recovery* for experiments where all residues are masked (`data.x = 20`, `data.y = None`).
- **Context:** In `protein_design.py`, supplying `data.y` triggers a reference-guided mode (`strategy="ref"`) that copies native residues site-by-site, creating an apparent 100% recovery that is actually an information leak artifact.
- **Alternatives Considered:** Reporting both numbers as "recovery" under different modes.
- **Rationale:** Scientific integrity requires completely rejecting leaked metrics. True inverse-folding recovery for 1n5uA03 is 41.30% (38/92).
- **Consequences:** Prevents false claims of near-perfect recovery and establishes a credible, reproducible E0 baseline.

---

## [DEC-007] E0 Scientific Hardening & Equivalence Claim Calibration
- **Date:** 2026-09-24
- **Decision:** Adopt the formal equivalence claim "FUNCTIONALLY REPRODUCED WITH MODERN COMPATIBILITY ADAPTATION", classify the 41.30% result as a "single-target all-masked inverse-folding integration result", mark target 1n5uA03 training set membership as "not verifiable from accessible metadata", and record milestone status as `E0-RUNTIME: COMPLETE` and `E0-SCIENTIFIC-HARDENING: COMPLETE`.
- **Context:** Following the runtime verification of ProteinSolver, a scientific hardening pass verified:
  1. Strict checkpoint loading under `strict=True` with 0 missing and 0 unexpected keys (567,060 params).
  2. Mask-invariance (EXP004) showing max absolute logit difference of 0.00000000e+00.
  3. Feature pipeline numerical identity (`max diff: 0.0`) between original repo and cleanroom extractor.
  4. Investigation of target provenance in author notebooks, which evaluated `"1.10.246.10" in cath_ids` as False, but cannot be independently verified without the full 72M training corpus.
- **Alternatives Considered:** Asserting "100% mathematical fidelity" or claiming 41.30% as benchmark generalization.
- **Rationale:** Demarcating exact empirical boundaries avoids overclaiming and ensures strict fidelity to the scientific method.
- **Consequences:** Robust, audited foundation for subsequent Phase 2 comparison with ProteinMPNN.

---

## [DEC-008] Lightweight Governance Architecture (Lesson/Rule/Event)
- **Date:** 2026-09-24
- **Decision:** Implement a three-entity governance architecture (Lesson, Rule, Event) using repository-native JSON storage with deterministic preflight retrieval. Seed with 6 lessons and 8 rules encoding the real ProteinSolver failure cases from Phase 1.
- **Context:** The project experienced multiple wasted cycles rediscovering the same failures: information leak misreporting, Data/Batch interface mismatch, overclaimed reproduction fidelity, single-target benchmark escalation. These needed durable, machine-readable regression protection.
- **Alternatives Considered:** Ocean Sentinel's full governance architecture (too complex); ad-hoc markdown rules only (no machine-readable retrieval); embedding-based RAG system (unnecessary infrastructure).
- **Rationale:** The architecture must remain lightweight enough for a 5-person student team while preventing the specific catastrophic mistakes that already occurred. Three entities (Lesson, Rule, Event) cover all governance needs without taxonomy explosion. Deterministic context-based retrieval is sufficient and explainable.
- **Constraints Enforced:** No embeddings, no vector databases, no autonomous lesson promotion, no numeric trust scores, no cross-project federation. PROPOSED lessons cannot block execution. Only human review promotes lessons to rules.
- **Consequences:** 83/83 governance tests pass. All 6 ProteinSolver regression cases are encoded as durable lessons with corresponding rules. Preflight system produces MUST/SHOULD/FYI output with coverage summary.

---

## [DEC-009] Final Governance Hardening, Direct-Bypass Protection, and Workflow Integration
- **Date:** 2026-09-25
- **Decision:** Harden the governance foundation against direct-file bypass, integrate automatic preflight into experiment templates, provide a preflight CLI, implement claim-level extrapolation evaluation, support retraction audits, and enable standard pytest discovery.
- **Context:** The final acceptance red-team audit revealed that while schemas and preflight functions existed, governance was not invoked by `experiments/TEMPLATE/run.py`, direct edits to JSON files could silently mutate rules, pytest could not collect tests, and claims lacked a machine validator for extrapolation.
- **Alternatives Considered:** Relying only on manual Python script execution without CLI; ignoring direct JSON file mutations; adding complex cryptographic hashing (rejected in favor of event log consistency and mandatory rule validation).
- **Rationale:** A requirement is not integrated simply because a unit test exists. Integrating preflight into the experiment template guarantees that every new experiment runs safety checks and logs `RULE_APPLIED` events. Store integrity checks prevent accidental or adversarial mutation.
- **Consequences:** 109/109 assertions pass across 25 pytest-collected test functions. Preflight CLI (`governance/preflight_cli.py`) available. `experiments/TEMPLATE/run.py` automatically evaluates preflight and records audit trail. All 6 ProteinSolver regressions protected with bad and good case verification.

---

## [DEC-010] Governance Release Gate Acceptance and Foundation Freeze
- **Date:** 2026-09-25
- **Decision:** Formally declare the governance foundation FROZEN under classification FOUNDATION_FROZEN_WITH_LIMITATIONS. Halt all governance redesign and speculative infrastructure development. Establish `reports/GOVERNANCE_RELEASE_GATE_REPORT.md` as the sole current freeze authority and transition the project to Phase 2 / Milestone 3 (ProteinMPNN Integration & Baseline Verification).
- **Context:** The Lesson/Rule/Event governance architecture underwent full implementation, adversarial red-teaming, direct-file bypass detection hardening, and workflow integration. All 25 pytest test suites (109 assertions) pass, all 6 ProteinSolver regressions are protected with bad and good input pairs, the template experiment runner enforces preflight, and documentation consistency audits have reconciled branch and authority definitions.
- **Alternatives Considered:** Further cycles of speculative governance expansion; opening Phase 2 without a formal release-gate freeze.
- **Rationale:** The governance foundation is complete, verified, and integrated. Continued development without empirical research would violate the scientific mission. A formal freeze provides a solid, stable baseline for ProteinMPNN integration.
- **Consequences:** Governance is frozen. No further changes to `governance/` schemas or preflight logic are permitted. Next work is Workstream B (ProteinMPNN integration).

---

## [DEC-011] Scientific Metrics, Non-Tautological Viability, and Evaluation Protocol Integrity
- **Date:** 2026-09-25
- **Decision:** Codify the standard Zhang & Skolnick (2004) TM-score formulation with length-dependent $d_0(L_{\text{target}})$, resolve tautological Candidate Survival Rate into Generative Structural Viability Rate (SVR) and Independent Validation Yield (IVY), decouple within-model perplexity diagnostics between ProteinSolver (masked pseudo-perplexity) and ProteinMPNN (autoregressive perplexity), establish an anti-leakage structural oracle firewall (ESMFold screening vs. AlphaFold2/Boltz-1 independent validation), mandate an a priori fixed Pareto reference point $\mathbf{r}$, define explicit biophysical proxies (Henderson-Hasselbalch pI, hydrophobic core fraction with $\text{RSA} < 0.20$), and reclassify thresholds from "canonical" to "project screening thresholds".
- **Context:** A comprehensive audit of `science/metrics.md` and `science/evaluation_protocol.md` identified mathematical ambiguities (incomplete TM-score formula), metric tautology risk (evaluating candidate survival using the same criteria used to filter the set), invalid cross-model comparison of fundamentally different perplexity mechanisms, potential evaluation leakage across structural oracles, and overgeneralized phrasing ("canonical threshold", "100% mask-invariant").
- **Alternatives Considered:** Retaining approximate or informal metric descriptions; treating within-model perplexity as directly comparable; using the same oracle for screening and final evaluation.
- **Rationale:** Defensible scientific conclusions require mathematically precise definitions, strict separation between candidate selection and independent validation, explicit distinction between within-model diagnostics and cross-model metrics, and rigorously scoped empirical assertions.
- **Consequences:** All metric equations are mathematically sound, evaluation is protected against circular tautology, and the protocol is ready for Phase 2 / Milestone 3 (ProteinMPNN integration).


