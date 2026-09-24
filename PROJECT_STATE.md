# PROJECT STATE

## Project Identity
- **Project Name:** Protein Design / ProteinSolver Research Extension
- **Parent Foundational Work:** Strokach et al., 2020, *"Fast and Flexible Protein Design Using Deep Graph Neural Networks"*, Cell Systems 11(4): 402–411.e4.
- **Current Phase:** Phase 0 — Research Bootstrap, Infrastructure Setup & Literature/Novelty Audit
- **Current Branch:** `research/ai-research-bootstrap`
- **Date Created / Initialized:** 2026-09-24

---

## Current Scientific Posture
- **Research Hypothesis:** PROVISIONAL.
  > *"Can information from ProteinSolver complement modern structure-conditioned sequence-design models (e.g., ProteinMPNN), and can a diversity-aware, multi-objective candidate selection framework exploit that complementarity to improve the quality-diversity trade-off of designed protein sequences?"*
- **Hypothesis Status:** UNTESTED HYPOTHESIS.
  - Literature evidence confirms that modern models (ProteinMPNN, PiFold, ESM-IF1) significantly outperform ProteinSolver on native sequence recovery on standard benchmarks (CATH 4.2).
  - Whether ProteinSolver provides genuine complementary signal or merely degrades ProteinMPNN performance is an open empirical question that must be rigorously tested against null hypotheses.
- **Model Implementation Status:** FINAL MODEL NOT IMPLEMENTED.
  - No speculative or premature model training has begun.
  - Repositories and prior art are under formal audit.
- **Literature Audit Status:** INITIAL PASS COMPLETE / CONTINUOUS MONITORING ACTIVE.

---

## Known Risks & Scientific Vulnerabilities
1. **Lack of Novelty / Premature Novelty Claims:** Multi-objective optimization (MOME), quality-diversity algorithms (ME-GIDE), and inverse-folding ensembles (e.g., IgLM + ProteinMPNN) have already been explored in various configurations. Any claimed gap must be strictly delineated.
2. **Asymmetric Baseline Performance:** ProteinSolver achieves ~32–35% recovery on CATH 4.2, compared to ~51% for ProteinMPNN. Combining them naively may act as a corrupting noise source rather than a synergistic prior.
3. **Data Leakage:** Gene3D (ProteinSolver training corpus) vs. CATH 4.2 / 4.3 (ProteinMPNN training corpus) vs. validation sets (e.g. CASP15, TS50, TS500, de novo backbones) must be audited to prevent test set overlap.
4. **Metric Mismatch:** Native sequence recovery does not equal biophysical viability. Diversity without foldability is trivial.
5. **Over-reliance on Structural Proxies:** Using ESMFold / AlphaFold2 / Boltz-1 as oracles for self-consistency (scRMSD / scTM) introduces proxy bias (AlphaFold hallucination).
6. **Hallucination of Prior Art:** All papers, citations, DOIs, and empirical claims must be verified against primary sources.

---

## Milestones & Roadmap
- [x] **Milestone 0: Repository & Infrastructure Bootstrap**
  - Git initialization and dedicated branch creation (`research/ai-research-bootstrap`).
  - Project governance and role specifications (`AI_TEAM.md`).
  - Evidence standard and protocol specification (`RESEARCH_PROTOCOL.md`).
  - Claims registry establishing evidentiary boundaries (`CLAIMS_REGISTRY.md`).
  - Architecture and baseline documentation.
- [x] **Milestone 1: Comprehensive Literature & Prior-Art Audit**
  - Initial 6-stream literature scan (Streams A through F).
  - Population of `research/literature_matrix.csv` and `research/novelty_matrix.csv`.
  - Identification of closest prior art and provisional research gap analysis (`research/research_gap.md`).
- [ ] **Milestone 2: Empirical Feasibility & Baseline Audit (Dry-Run)**
  - Validate local environment for running ProteinSolver inference and ProteinMPNN inference on sample structures.
  - Inspect ProteinSolver model weights, schema, and I/O format.
  - Define exact benchmark dataset and filtering rules.
- [ ] **Milestone 3: Research Question Freezing & Human Review**
  - Present literature audit findings to Human Principal Investigator.
  - Decide whether to retain, refine, or pivot the provisional hypothesis based on audit evidence.
- [ ] **Milestone 4: Controlled Experimentation (E0–E5)**
  - Execute evaluation protocol (`science/evaluation_protocol.md`).
