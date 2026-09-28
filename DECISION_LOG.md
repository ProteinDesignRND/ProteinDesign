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

---

## [DEC-012] Scientific Protocol Pre-Registration, Scale-Free Hybrid Scoring, and Single Primary Endpoint
- **Date:** 2026-09-25
- **Decision:** Formalize and freeze the study pre-registration (`science/PREREGISTRATION.md`):
  1. Primary hybrid method defined as scale-free within-pool percentile rank normalization ($H(u) = \lambda p_{\text{MPNN}}(u) + (1-\lambda) p_{\text{PS}}(u)$), demoting raw logit interpolation to an exploratory ablation.
  2. AlphaFold2 (v2.3.2, monomodel weights `model_1_ptm`, 3 recycles, no templates) frozen as the single Primary Final Structural Validation Oracle; Boltz-1 designated strictly for sensitivity analysis.
  3. Single primary study endpoint established as the target-level mean fixed-correspondence Self-Consistency TM-score ($\overline{\text{scTM}}_{\text{val}}$) across the $M=10$ selected library, evaluated by AlphaFold2.
  4. Unit of statistical analysis established as the TARGET / BACKBONE ($N=50$ TS50 targets) evaluated via two-sided paired Wilcoxon signed-rank test ($\alpha = 0.01$).
  5. E0 split into E0-A (historical deterministic MAP integration control on 1n5uA03, 41.30%) and E0-B (stochastic ProteinSolver candidate generation baseline).
  6. Two-stage candidate selection enforced (Stage 1 hard viability gate $\to$ Stage 2 greedy diversity selection heuristic).
  7. Hypervolume demoted to exploratory descriptive analysis with fixed external normalization bounds.
  8. Mixing weight $\lambda$ mandated to be tuned strictly on the development split (CATH 4.2 validation) and frozen before test evaluation.
  9. Explicit rule that all secondary baselines and exploratory analyses are reported regardless of outcome.
- **Context:** An independent red-team audit by Claude Standalone 2.0 identified methodological vulnerabilities: raw logit addition across different scales, lack of a single pre-registered primary endpoint, ambiguity between AlphaFold2 and Boltz-1, candidate-level pseudoreplication in statistical testing, and potential evaluation leakage in candidate selection and hypervolume.
- **Alternatives Considered:** Retaining raw logit interpolation as primary; evaluating both AF2 and Boltz-1 as co-primary oracles; using candidate-level pooling in statistical testing; post-hoc hyperparameter selection.
- **Rationale:** Rigorous, publication-grade science requires pre-registration, unambiguous single primary endpoints, scale-free score normalization, paired target-level statistics to avoid pseudoreplication, and pre-frozen hyperparameters.
- **Consequences:** All 24 protocol items are frozen in `science/PREREGISTRATION.md`, `src/hybrid/` provides cleanroom implementations, and tests verify mathematical behavior before ProteinMPNN integration.

---

## [DEC-013] Micro-Freeze Audit: Definitive Candidate Budget Accounting, Common Candidate Universe, AF2 Configuration, Folding Failure Taxonomy, and Provenance Language
- **Date:** 2026-09-25
- **Decision:** Resolve the final five protocol ambiguities identified in the Claude Standalone 2.0 red-team audit:
  1. **Candidate Budget ($K$):** Formally freeze **Interpretation A**: $K$ is the **TOTAL candidate sequences generated PER TARGET PER METHOD/ARM across all temperatures and random seeds** ($K=100$ tuning, $K=500$ primary test). For the TS50 benchmark ($K=500$): Standalone ProteinMPNN generates exactly 500 sequences per target (partitioned as 167 for seed 42, 167 for seed 1337, and 166 for seed 2026 at $T^*_{\text{MPNN}}$); Stochastic ProteinSolver (E0-B) generates exactly 500 sequences per target; Primary Hybrid evaluates the common candidate universe of 500 sequences scored by both models.
  2. **Common Candidate Universe:** Primary hybrid scoring operates strictly on the identical candidate sequences ($U_t$), computing both $S_{\text{MPNN}}$ and $S_{\text{PS}}$ on each $u \in U_t$ and ranking percentiles within that shared pool, completely eliminating cross-pool or asymmetric rank leakage.
  3. **AlphaFold2 Configuration Freeze:** Authoritative primary oracle parameters frozen as: AlphaFold2 v2.3.2, monomodel weights `model_1_ptm`, precision `float16` (`fp16`) on GPU (CUDA), 3 recycles, single-sequence mode (`msa_mode="single_sequence"`), no homologous templates, no Amber relaxation, deterministic seed 42 (`random_seed=42`).
  4. **Folding Failure Taxonomy:** Explicitly decoupled scientific vs. infrastructure folding failures. Biological/generative folding failures (steric clash, NaN coordinates, pLDDT < 10) are assigned $\text{scTM} = 0.0$ and included in paired differences $\{d_t\}$. Infrastructure crashes (OOM, timeout >600s, software/driver crashes) are NEVER assigned $\text{scTM} = 0.0$, are excluded from $\{d_t\}$, and trigger automatic experiment invalidation if $>10\%$ of targets fail.
  5. **Model-Specific Provenance Language:** Blanket claims that TS50 has "<30% sequence identity to training sets" replaced with model-specific provenance: <30% identity to CATH 4.2 / ProteinMPNN training sets, while ProteinSolver Gene3D 72M training membership is documented per model (superfamily absence verified where accessible, otherwise NOT VERIFIABLE FROM ACCESSIBLE METADATA).
  6. **Fixed-Correspondence scTM Terminology:** Fixed-correspondence Self-Consistency TM-score (scTM) is strictly defined under 1-to-1 residue index correspondence without dynamic programming alignment or gap insertion, disclaiming standard TM-align alignment.
- **Context:** A final micro-freeze audit by Claude Standalone 2.0 identified residual ambiguities in the interpretation of $K$ (total vs per condition), common candidate universe specification, precision alternatives (FP16 vs BF16), failure score assignment (scTM=0 for hardware crashes), and blanket TS50 training separation claims.
- **Alternatives Considered:** Allowing $K$ to scale with temperature $\times$ seed conditions (rejected: causes 15x candidate explosion and evaluation infeasibility); allowing separate candidate generation pools for hybrid scoring (rejected: creates asymmetric ranking bias); assigning scTM=0 to hardware crashes (rejected: conflates infrastructure faults with sequence design quality).
- **Rationale:** Absolute scientific integrity requires that candidate generation budgets are mathematically matched and bounded, hybrid percentiles are drawn from identical candidate universes, oracle configurations are deterministic and singular, failure modes are taxonomically accurate, and provenance statements never overclaim.
- **Consequences:** All ambiguities are completely eliminated from `science/PREREGISTRATION.md`, `science/evaluation_protocol.md`, `science/metrics.md`, and `src/hybrid/`. Implementation and test suites enforce these rules.

---

### [DEC-014] 2026-09-28: Final Scientific Protocol Consistency Closure and Parameter Freeze
- **Status:** APPROVED AND FROZEN
- **Decider:** Repository Consistency Audit Agent & Protocol Integrity Gate
- **Decision:**
  1. **Deterministic Development Allocation Matrices:** Codified exact balanced integer allocation matrices: ProteinMPNN (7-7-6 across 5 temperatures $\times$ 3 seeds = 100 sequences/target); ProteinSolver E0-B (12-11-11 across 3 temperatures $\times$ 3 seeds = 100 sequences/target).
  2. **Frozen Test-Time Seed Allocation:** Primary test generation ($K = 500$) is conducted strictly at optimal frozen temperature $T^*$ partitioned across seeds: seed 42 ($N=167$), seed 1337 ($N=167$), seed 2026 ($N=166$), with zero test-time temperature sweep.
  3. **Common Candidate Universe Enforcement:** Primary hybrid is NOT a joint generator; ProteinMPNN generates $U_t$ ($K=500$ at $T^*_{\text{MPNN}}$), both models score the identical sequences in identical candidate identity order (`validate_common_candidate_order`), and percentiles are derived strictly within that pool.
  4. **Selection Score Normalization Consistency:** Inside the greedy diversity selector ($\text{score}(u) + \gamma \cdot \text{diversity}$), the primary MPNN-only arm uses normalized percentile rank score ($\text{score}_{\text{MPNN-only}}(u) = p_{\text{MPNN}}(u) \in (0, 1]$), ensuring scale compatibility with hybrid score $H(u) \in (0, 1]$ and normalized Hamming distance in $[0, 1]$.
  5. **Dimensionless Diversity Weight ($\gamma$) Search Grid:** Frozen to $\gamma \in \{0.0, 0.25, 0.5, 1.0, 2.0\}$, tuned strictly on the development set separately for MPNN-only and hybrid selection, and frozen prior to TS50 evaluation.
  6. **Greedy Selection Initialization & Deterministic Tie Breaking:** First selection on empty $S'$ chooses candidate with maximum primary score; subsequent selections use the full greedy formula. All ties in score or objective are resolved deterministically by ascending candidate ID.
  7. **Duplicate Accounting & Unique Candidate Filtering:** Generation budget $K$ counts all generated sequences including duplicates; duplicate rate is reported separately; Stage 2 selection operates strictly on UNIQUE viable sequences; duplicates contribute 0 distance; duplicates are never silently regenerated.
  8. **Insufficient Viable Candidates Policy:** If $|S_{\text{viable, unique}}| < M=10$, mark arm/target as `SELECTION_INFEASIBLE_LT_M`. No silent regeneration, padding, or threshold alterations occur. Primary endpoint is undefined for complete-case paired comparison; conservative zero-quality sensitivity analysis is additionally reported.
  9. **Statistical Test Specification:** Two-sided paired Wilcoxon signed-rank test on $\{d_t\}_{t=1}^N$ with $\alpha = 0.01$ (`scipy.stats.wilcoxon(..., zero_method='wilcox', correction=True, alternative='two-sided')`); 10,000 bootstrap resamples derived strictly from target-level paired differences $d_t$.
  10. **Single Primary Confirmatory Hypothesis:** Exactly one primary comparison is evaluated; all secondary analyses are explicitly exploratory and unadjusted.
- **Context:** Comprehensive repository-wide audit resolved all remaining mathematical, statistical, reproducibility, and bookkeeping degrees of freedom before starting ProteinMPNN integration.
- **Alternatives Considered:** Using unnormalized raw log-probs in greedy selection (rejected: causes arbitrary scale incompatibility with [0, 1] diversity distance); unconstrained gamma search (rejected: introduces post-hoc tuning degrees of freedom); padding libraries with duplicates or failed sequences (rejected: invalidates experimental library size and statistical integrity).
- **Rationale:** Complete scientific closure requires that every parameter, search grid, tie-breaking rule, duplicate policy, and edge case is fully determinized and tested in automated software before any experimental benchmark data is collected.
- **Consequences:** Implementation in `src/hybrid/` and 27 scientific protocol tests (52 total pytest suites) fully verify all protocol rules. Repository is 100% frozen and ready for ProteinMPNN integration.




