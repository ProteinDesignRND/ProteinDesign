# PROJECT STATE

## Project Identity
- **Project Name:** Protein Design / ProteinSolver Research Extension
- **Parent Foundational Work:** Strokach et al., 2020, *"Fast and Flexible Protein Design Using Deep Graph Neural Networks"*, Cell Systems 11(4): 402–411.e4.
- **Current Phase:** Pre-E1 Scientific Readiness & Protocol Reconciliation Complete — Pending Human Review/Merge on PR #1
- **Current Branch:** `governance/final-acceptance-redteam-v1`
- **Integration Branch:** `main`
- **Governance Freeze Status:** FOUNDATION_FROZEN_WITH_LIMITATIONS
- **Date Created / Initialized:** 2026-09-24 (Last Updated: 2026-09-28)
- **Milestone Labels:**
  - `E0-RUNTIME`: **COMPLETE**
  - `E0-SCIENTIFIC-HARDENING`: **COMPLETE**
  - `E0-EQUIVALENCE-STATUS`: **FUNCTIONALLY REPRODUCED WITH MODERN COMPATIBILITY ADAPTATION**
  - `GOVERNANCE-RELEASE-GATE`: **FROZEN (WITH LIMITATIONS)**
  - `PROTEINMPNN-INTEGRATION`: **COMPLETE**
  - `PROTEINMPNN-BENCHMARK`: **NOT STARTED**
  - `PRE-E1-INTEGRITY-GATE`: **PASSED**
  - `PRE-E1-SCIENTIFIC-READINESS-CLOSURE`: **COMPLETE**
  - `PRE-E1-SURGICAL-RECONCILIATION`: **COMPLETE**
  - `AUTHORIZATION-STATUS`: **FROZEN ON REVIEW BRANCH — PENDING HUMAN REVIEW/MERGE**

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
  - ProteinMPNN cleanroom integration: **COMPLETE** (Official upstream Dauparas et al. 2022, commit `8907e66`, checkpoint `v_48_020.pt` SHA-256 verified, wrapper & tests passing).
  - ProteinMPNN benchmark: **NOT STARTED** (No E1 or TS50 benchmark runs executed).
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
- [x] **Milestone 2.7: Scientific Protocol Pre-Registration & Micro-Freeze Audit Hardening**
  - `PROTOCOL PRE-REGISTERED`: Created `science/PREREGISTRATION.md` freezing all currently registered protocol elements under Amendment A1 prior to experimentation.

  - `PRIMARY HYBRID FORMULATION`: Scale-free within-pool percentile rank normalization ($H = \lambda p_{\text{MPNN}} + (1-\lambda) p_{\text{PS}}$) implemented in `src/hybrid/scoring.py`.
  - `COMMON CANDIDATE UNIVERSE`: Primary hybrid scoring operates strictly on identical candidate sequences ($U_t$, $|U_t|=K$) scored by both models, preventing asymmetric rank leakage.
  - `PRIMARY ENDPOINT FROZEN`: Target-level mean fixed-correspondence scTM across the $M=10$ library evaluated by AlphaFold2 (v2.3.2).
  - `PRIMARY ORACLE FROZEN`: AlphaFold2 (v2.3.2) frozen with singular precision `float16` (`fp16`) on GPU (CUDA), 3 recycles, single-sequence mode, seed 42. (All OR-alternatives removed; Boltz-1 designated strictly for sensitivity analysis).
  - `STATISTICAL UNIT FIXED`: Target/backbone unit under paired Wilcoxon signed-rank test ($\alpha = 0.01$).
  - `BUDGET MATCHER & E0 SPLIT`: Candidate budget $K$ unambiguously defined under Interpretation A as total generated candidates per target ($K=500$ for TS50: 167+167+166 across 3 seeds); split E0 into E0-A (deterministic MAP control, 41.30%) and E0-B (stochastic baseline).
  - `FAILURE TAXONOMY DECOUPLED`: Biological folding failure assigned $\text{scTM} = 0.0$ and included in $\{d_t\}$; infrastructure crashes NEVER assigned 0.0, excluded from $\{d_t\}$, and trigger invalidation if $>10\%$.
  - `TWO-STAGE SELECTION`: Stage 1 hard viability gate $\to$ Stage 2 greedy diversity selection heuristic implemented in `src/hybrid/selection.py`.
  - `VERIFICATION`: 42/42 pytest suites passing (25 governance + 17 scientific protocol).
- [x] **Milestone 2.8: Final Scientific Protocol Consistency Closure (V3 Freeze)**
  - `DETERMINISTIC ALLOCATION MATRICES`: Codified exact balanced integer allocation matrices in `src/hybrid/budget.py`: Dev MPNN (7-7-6 across 5 temperatures $\times$ 3 seeds = 100); Dev PS E0-B (12-11-11 across 3 temperatures $\times$ 3 seeds = 100); Test (500 at frozen $T^*$ partitioned 167/167/166).
  - `COMMON CANDIDATE UNIVERSE`: Codified integrity validation (`validate_common_candidate_order`) ensuring identical sequence and candidate ID order before percentile ranks are computed.
  - `SELECTION SCORE NORMALIZATION`: Codified `score_MPNN_only(u) = p_MPNN(u)` so that both standalone MPNN and hybrid arms operate on the exact matched $[0, 1]$ percentile scale inside greedy facility dispersion.
  - `GAMMA SEARCH GRID`: Frozen dimensionless search grid $\gamma \in \{0.0, 0.25, 0.5, 1.0, 2.0\}$ tuned on development set separately per arm.
  - `GREEDY INITIALIZATION & TIE BREAKING`: Frozen first selection on empty $S'$ to candidate with maximum primary score; deterministic tie breaking by ascending candidate ID.
  - `DUPLICATE ACCOUNTING & UNIQUE SELECTION`: Exact duplicates retained in raw accounting and reported separately; selection operates strictly on UNIQUE viable sequences; duplicates contribute 0 distance; no silent regeneration.
  - `INSUFFICIENT VIABLE CANDIDATES POLICY`: If unique viable candidates $< 10$, arm is marked `SELECTION_INFEASIBLE_LT_M`; undefined in complete-case paired comparison; evaluated under conservative zero sensitivity.
  - `STATISTICAL IMPLEMENTATION`: Two-sided paired Wilcoxon signed-rank test on $\{d_t\}_{t=1}^N$ with $\alpha = 0.01$ (`zero_method='wilcox'`, `correction=True`, `method='asymptotic'`); 10,000 bootstrap resamples on target-level paired differences $d_t$.

  - `TEST SUITE EXPANSION`: 52/52 pytest suites passing (25 governance + 27 scientific protocol).
  - `DECISION LOGGED`: Appended `[DEC-014]`.
- [x] **Milestone 3A: Official ProteinMPNN Cleanroom Integration: COMPLETE**
  - Pinned official upstream repository (`https://github.com/dauparas/ProteinMPNN`, commit `8907e6671bfbfc92303b5f79c4b5e6ce47cdef57`, MIT License).
  - Implemented cleanroom wrapper (`src/proteinmpnn/`) with coordinate parsing, device handling, and zero native sequence conditioning leakage.
  - Verified SHA-256 cryptographic hashes for all official vanilla checkpoints (`v_48_020` default).
  - Verified end-to-end interface compatibility with `src/hybrid` scoring, normalization, and diversity selection.
  - 63/63 pytest test suites passing (25 governance + 27 scientific protocol + 11 ProteinMPNN).
  - Published provenance manifest: `reports/PROTEINMPNN_PROVENANCE_MANIFEST.md`.
  - Passed Pre-E1 counterfactual native-sequence leakage gate (100% invariance, max diff 0.00e+00): `reports/PROTEINMPNN_COUNTERFACTUAL_LEAKAGE_AUDIT_REPORT.md`.
- [x] **Milestone 3A.1: Development Hyperparameter Selection Protocol Freeze: COMPLETE**
  - Codified exact scalar development objective $J = (1/N_{\text{dev}}) \sum_t \overline{\text{scTM}}_{\text{val}}(t)$ evaluated with AlphaFold2.
  - Codified Cartesian product optimization grids: MPNN-only (25 pairs), PS E0-B (15 pairs), Hybrid $\lambda \times \gamma$ (35 pairs with $T^*_{\text{hybrid}} = T^*_{\text{MPNN}}$ on Common Candidate Universe $U_t$).
  - Codified deterministic 5-step parameter freezing order and lexicographical tie-breaking rule.
  - Implemented cleanroom optimization module `src/hybrid/optimization.py` and focused tests in `tests/test_development_hyperparameter_selection.py`.
  - Appended `[DEC-015]`.
- [x] **Milestone 3A.2: Pre-E1 Scientific Readiness and Consistency Closure: COMPLETE**
  - Created immutable development manifest `data/manifests/development_20_cath42.txt` (SHA-256: `47ab5fec66017b455f7eabee143dc83e99ec740640e945ed96752abb59483069`) comprising 20 distinct CATH topologies deterministically selected from Ingraham/Dauparas CATH 4.2 validation split (`chain_set_splits.json`, SHA-256: `8e9a587a50c7f6c026e4ed00f6c1c30b106100f36f7a01de47542bdfc060adc2`).
  - Codified development optimization infeasibility rule ($J = -\infty$ for any target with $<10$ unique viable candidates) in `src/hybrid/optimization.py` and added unit tests (10/10 passing).
  - Operationally froze ESMFold screening oracle configuration (Meta AI `esm` v2.0.0, `esmfold_v1` 3B, sequence-only, 4 recycles, `fp16` GPU, max len 1024 with chunking, seed 42, operational screening cutoffs $\text{scRMSD}_{\text{screen}} \le 2.0\text{ \AA}$ and $\text{pLDDT}_{\text{screen}} \ge 80.0$).
  - Refined AlphaFold2 determinism wording: fixed inference seed = 42 controls stochastic initialization but does not guarantee bitwise GPU determinism across differing CUDA/hardware environments; froze 1-to-1 residue correspondence and 100% C-alpha resolution rules.
  - Codified development candidate caching strategy (generate once per temperature, screen once, score once, reuse across all $\gamma$).
  - Appended `[DEC-016]`.
- [x] **Milestone 3A.3: Pre-E1 Surgical Protocol & Provenance Reconciliation: COMPLETE**
  - Delineated pre-registration version history: original registration frozen 2026-09-25; Amendment A1 frozen 2026-09-28 before any benchmark candidate generation.
  - Reconciled manifest provenance: canonical LF SHA-256 `47ab5fec66017b455f7eabee143dc83e99ec740640e945ed96752abb59483069`, raw downloaded CATH artifact SHA-256 `8e9a587a50c7f6c026e4ed00f6c1c30b106100f36f7a01de47542bdfc060adc2`. Enforced `eol=lf` via `.gitattributes`.
  - Reconciled manifest targets: confirmed 20 targets (`2e6i.A`, `2mh3.A`, `3gn4.E`, `2qg3.A`, `3abd.B`, `1z8s.A`, `5t5d.A`, `1f7e.A`, `2lg7.A`, `1h2s.A`, `1yf9.A`, `2p2e.A`, `1cel.A`, `2kil.A`, `1c52.A`, `2gmy.D`, `1nyn.A`, `2c6u.A`, `2ctt.A`, `3hxi.A`); documented that `4bdx.A` (chain 11) duplicates topology `2.10.25` of `1f7e.A` (chain 8) and was correctly bypassed by unique-topology rule.
  - Removed 0.5 fold topology claim from fixed-correspondence scTM; added explicit methodological boundary (continuous length-normalized structural similarity, not alignment TM-score).
  - Reconciled hydrophobic core fraction definition ($f_{\text{core}} = \text{core hydrophobic} / \text{total hydrophobic}$, $\text{RSA} < 0.20$), with $0.0$ edge-case handling.
  - Explicitly attributed secondary structural metrics to folding oracles (ESMFold for screening, AF2 for selected library, Boltz-1 for sensitivity).
  - Frozen ProteinMPNN scoring permutation (generation-time decoding permutation retained and reused during scoring).
  - Frozen statistical reproducibility details: SciPy v1.17.1, two-sided paired Wilcoxon (`zero_method='wilcox'`, `correction=True`, `method='asymptotic'`), 10,000 target-level paired bootstrap resamples with seed 42, percentile method, Hodges-Lehmann effect size.
  - Replaced "submodule" with "independent nested Git repository clone" throughout.
  - Authorization status: `FROZEN ON REVIEW BRANCH — PENDING HUMAN REVIEW/MERGE` on PR #1.
- [x] **Milestone 3A.4: Final Pre-E1 Scientific Readiness & Anti-Loop Closure V5: COMPLETE**
  - Confirmed primary comparator invariant: strictly $d_t = \overline{\text{scTM}}_{\text{hybrid}}(t) - \overline{\text{scTM}}_{\text{MPNN-only}}(t)$ (guarded by automated invariant test; single-best-model comparator strictly prohibited as primary comparator).
  - Confirmed sample size hierarchy: strictly $N=50$ for confirmatory TS50 benchmark; $N_{\text{dev}}=20$ strictly for development/tuning.
  - Frozen ESMFold execution path across all registered benchmark stages (E1 development tuning and TS50 primary evaluation): strictly GPU (`cuda`) `float16`, `chunk_size = 128`, seed 42, max sequence length $L \le 1024$ with preflight manifest validation.
  - Codified deterministic retry semantics: retried exactly once with identical frozen configuration; only process restart/cleanup permitted; no parameter alteration.
  - Codified development AF2 infrastructure failure policy: if an AF2 validation fails due to infrastructure, target cannot produce complete $M=10$ endpoint set; configuration receives $J = -\infty$ (ineligible for argmax).
  - Codified candidate-level screening failure policy: excluded from viable set, never assigned 0.0, never regenerated; reported under screening infrastructure failure count.
  - Scoped Project Truth authority to verified facts and limitations, deferring to PREREGISTRATION.md for protocol.
  - Excised bitwise determinism overclaims.
  - Recorded proposed governance lessons L-007 through L-016 and logged DEC-018 and DEC-019.
  - Verification: 80+ collected tests passing across 4 modules; governance preflight passing; historical clone untouched.
  - Authorization status: `FROZEN ON REVIEW BRANCH — PENDING HUMAN REVIEW/MERGE` on PR #1.
- [ ] **Milestone 3B: ProteinMPNN Baseline Benchmark Execution (E1 / TS50): NOT STARTED**
  - Execute controlled benchmark baselines under frozen protocol (`science/evaluation_protocol.md`).

- [ ] **Milestone 4: Research Question Freezing & Human Review**
  - Present literature audit and E0 baseline findings to Human Principal Investigator.
  - Decide whether to retain, refine, or pivot the provisional hypothesis based on audit evidence.
- [ ] **Milestone 5: Controlled Experimentation (E0–E5)**
  - Execute evaluation protocol (`science/evaluation_protocol.md`).

