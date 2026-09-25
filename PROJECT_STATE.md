# PROJECT STATE

## Project Identity
- **Project Name:** Protein Design / ProteinSolver Research Extension
- **Parent Foundational Work:** Strokach et al., 2020, *"Fast and Flexible Protein Design Using Deep Graph Neural Networks"*, Cell Systems 11(4): 402–411.e4.
- **Current Phase:** Foundation Frozen (Milestone 2.5 Complete) — Ready for Phase 2 / Milestone 3 (ProteinMPNN Integration & Baseline Verification)
- **Current Branch:** `governance/final-acceptance-redteam-v1`
- **Integration Branch:** `main`
- **Governance Freeze Status:** FOUNDATION_FROZEN_WITH_LIMITATIONS
- **Date Created / Initialized:** 2026-09-24
- **Milestone Labels:**
  - `E0-RUNTIME`: **COMPLETE**
  - `E0-SCIENTIFIC-HARDENING`: **COMPLETE**
  - `E0-EQUIVALENCE-STATUS`: **FUNCTIONALLY REPRODUCED WITH MODERN COMPATIBILITY ADAPTATION**
  - `GOVERNANCE-RELEASE-GATE`: **FROZEN (WITH LIMITATIONS)**

---

## Current Scientific Posture
- **Research Hypothesis:** PROVISIONAL.
  > *"Can information from ProteinSolver complement modern structure-conditioned sequence-design models (e.g., ProteinMPNN), and can a diversity-aware, multi-objective candidate selection framework exploit that complementarity to improve the quality-diversity trade-off of designed protein sequences?"*
- **Hypothesis Status:** UNTESTED HYPOTHESIS.
  - Literature evidence confirms that modern models (ProteinMPNN, PiFold, ESM-IF1) significantly outperform ProteinSolver on native sequence recovery on standard benchmarks (CATH 4.2).
  - Whether ProteinSolver provides genuine complementary signal or merely degrades ProteinMPNN performance is an open empirical question that must be rigorously tested against null hypotheses.
- **Model Implementation Status:** 
  - ProteinSolver baseline: **FUNCTIONALLY REPRODUCED WITH MODERN COMPATIBILITY ADAPTATION**.
  - Strict checkpoint integrity: Verified (`strict=True`, 0 missing, 0 unexpected, 567,060 params).
  - Mask-invariance: Verified (max logit diff = 0.00000000e+00).
  - Integration result: 41.30% on 1n5uA03 (single-target all-masked inverse-folding integration result).
  - ProteinMPNN: NOT STARTED (queued for Phase 2).
- **Literature Audit Status:** INITIAL PASS COMPLETE / CONTINUOUS MONITORING ACTIVE.

---

## Known Risks & Scientific Vulnerabilities
1. **Lack of Novelty / Premature Novelty Claims:** Multi-objective optimization (MOME), quality-diversity algorithms (ME-GIDE), and inverse-folding ensembles (e.g., IgLM + ProteinMPNN) have already been explored in various configurations. Any claimed gap must be strictly delineated.
2. **Asymmetric Baseline Performance:** ProteinSolver achieves ~32–35% recovery on CATH 4.2, compared to ~51% for ProteinMPNN. Combining them naively may act as a corrupting noise source rather than a synergistic prior.
3. **Data Leakage & Target Contamination:** 1n5uA03 was used in repository demos and profile recovery experiments; training set membership in the full 72M corpus is *not verifiable from accessible metadata*. Benchmark sets for Phase 2 must use strictly isolated test splits (e.g. CATH 4.2 / TS50).
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
- [x] **Milestone 2: Empirical Feasibility & Baseline Audit (Milestone E0)**
  - `E0-RUNTIME: COMPLETE`: Original `ProteinNet` loads published checkpoint and runs forward pass on CUDA; CSP `design_sequence` executes on CPU.
  - `E0-SCIENTIFIC-HARDENING: COMPLETE`:
    - Strict checkpoint verification under `strict=True` (0 missing, 0 unexpected, 567,060 params).
    - Provenance manifest published (`reports/PROTEINSOLVER_PROVENANCE_MANIFEST.md`).
    - EXP004 mask-invariance verified (max logit diff = 0.00000000e+00).
    - Feature pipeline verified numerically identical on tested target 1n5uA03 (`max diff: 0.0`).
    - 41.30% result reclassified as single-target all-masked inverse-folding integration result.
    - Historical equivalence claim formulated as: FUNCTIONALLY REPRODUCED WITH MODERN COMPATIBILITY ADAPTATION.
- [x] **Milestone 2.5: Governance Foundation & Final Red-Team Acceptance**
  - `GOVERNANCE: IMPLEMENTED & HARDENED`: Lesson/Rule/Event architecture with 6 lessons, 8 rules, append-only event log, and deterministic preflight.
  - `GOVERNANCE: TESTED`: 109/109 assertions pass across 25 pytest test suites (0 failures, 0 warnings) covering schema, retrieval, conflict resolution, store integrity against direct-file bypass, and all 6 ProteinSolver regressions with bad and good case verification.
  - `GOVERNANCE: INTEGRATED`: Automatic preflight hooked into `experiments/TEMPLATE/run.py` (logging `RULE_APPLIED` events); CLI available at `governance/preflight_cli.py`.
  - `GOVERNANCE: CLAIM PROTECTION`: Machine evaluation of claim scope, extrapolation detection (`EXTRAPOLATION_REVIEW_REQUIRED`), and retraction audit (`audit_retraction`).
  - `GOVERNANCE: DOCUMENTED`: Complete reconciliation across DECISION_LOG, ARCHITECTURE, AI_AGENT_RULES_AND_LESSONS, and TEAM_ONBOARDING.
- [x] **Milestone 2.6: Scientific Metrics & Evaluation Protocol Integrity Gate**
  - `METRICS: MATHEMATICALLY CODIFIED`: Standard Zhang & Skolnick (2004) TM-score ($d_0(L_{\text{target}})$ normalized), Kabsch C$\alpha$ scRMSD, Henderson-Hasselbalch pI, and RSA-based hydrophobic core fraction.
  - `SELECTION/EVALUATION FIREWALL`: Candidate survival split into Generative Structural Viability Rate (SVR) and Independent Validation Yield (IVY) to prevent tautological evaluation.
  - `ORACLE SEPARATION`: Screening oracle (ESMFold) strictly separated from final independent validation oracle (AlphaFold2/Boltz-1).
  - `PERPLEXITY DECOUPLING`: ProteinSolver masked pseudo-perplexity documented as non-comparable to ProteinMPNN autoregressive perplexity; retained as within-model diagnostics.
  - `DIVERSITY SPECIFICATION`: Three distinct stages codified (Raw, Viable, Selected library) with exact pairwise Hamming distance formulations.
  - `SCIENTIFIC WORDING AUDITED`: Scoped mask-invariance to EXP004 tested evidence; removed uncalibrated SOTA claims; corrected ProteinMPNN permutation decoding order.
- [x] **Milestone 2.7: Scientific Protocol Pre-Registration & Independent Review Hardening**
  - `PROTOCOL PRE-REGISTERED`: Created `science/PREREGISTRATION.md` freezing all 24 study parameters prior to experimentation.
  - `PRIMARY HYBRID FORMULATION`: Scale-free within-pool percentile rank normalization ($H = \lambda p_{\text{MPNN}} + (1-\lambda) p_{\text{PS}}$) implemented in `src/hybrid/scoring.py`.
  - `PRIMARY ENDPOINT FROZEN`: Target-level mean fixed-correspondence scTM across the $M=10$ library evaluated by AlphaFold2 (v2.3.2).
  - `PRIMARY ORACLE FROZEN`: AlphaFold2 (v2.3.2) frozen as single primary final validation oracle; Boltz-1 designated strictly for sensitivity analysis.
  - `STATISTICAL UNIT FIXED`: Target/backbone unit under paired Wilcoxon signed-rank test ($\alpha = 0.01$).
  - `BUDGET MATCHER & E0 SPLIT`: Enforced matched generation budgets $K$; split E0 into E0-A (deterministic MAP control, 41.30%) and E0-B (stochastic baseline).
  - `TWO-STAGE SELECTION`: Stage 1 hard viability gate $\to$ Stage 2 greedy diversity selection heuristic implemented in `src/hybrid/selection.py`.
- [ ] **Milestone 3: ProteinMPNN Integration & Baseline Verification (Phase 2)**
  - Integrate official ProteinMPNN repository.
  - Execute sanity checks and baseline recovery on shared benchmark structures.
- [ ] **Milestone 4: Research Question Freezing & Human Review**
  - Present literature audit and E0 baseline findings to Human Principal Investigator.
  - Decide whether to retain, refine, or pivot the provisional hypothesis based on audit evidence.
- [ ] **Milestone 5: Controlled Experimentation (E0–E5)**
  - Execute evaluation protocol (`science/evaluation_protocol.md`).
