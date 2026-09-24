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
