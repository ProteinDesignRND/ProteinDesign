# PRE-REGISTRATION SPECIFICATION: PROTEIN HYBRID EVALUATION STUDY
**Document ID:** `SCIENCE-PREREGISTRATION-V1`  
**Registration History:**
- **Original Registration:** Frozen 2026-09-25 (Pre-Phase 2, prior to ProteinMPNN cleanroom integration and prior to any benchmark execution)
- **Amendment A1 (Pre-E1 Closure & Surgical Reconciliation):** Frozen 2026-09-28 (Prior to any benchmark candidate generation; manifest, oracle, and protocol clarifications only; zero test-set outcomes used)
**Status:** **MERGED ON MAIN — PROTOCOL FROZEN (E1 BENCHMARK EXECUTION PENDING HUMAN AUTHORIZATION)**
**Study Phase:** Pre-Phase 2 / Milestone 3A Closure  
**Lead Repository:** `Protein Design`  

---

## 1. Primary Research Question
> *"Does ProteinSolver's distance-graph constraint-satisfaction scoring provide orthogonal structural signal that improves modern inverse-folding candidate selection, or does modern inverse folding combined with structural validation dominate hybrid selection?"*

This is a **strictly two-sided scientific question**. No superiority or complementarity of ProteinSolver over standalone ProteinMPNN is assumed in advance.

---

## 2. Primary Study Endpoint
The **single, pre-registered primary endpoint** is:
$$\overline{\text{scTM}}_{\text{val}}(t) = \frac{1}{M} \sum_{m=1}^M \text{scTM}_{\text{val}}(s^{(m)}_t)$$
The **target-level mean fixed-correspondence Self-Consistency TM-score** across the final selected candidate library ($M = 10$) evaluated by the **Primary Final Structural Validation Oracle (AlphaFold2 v2.3.2)**.
- **Direction:** Higher is better ($\in (0, 1]$).
- **Normalization:** Normalized strictly by target backbone length $L_{\text{target}}$.
- **Score Formulation:** Zhang & Skolnick (2004) formula under optimal rigid-body Kabsch superposition on matched C$\alpha$ positions.
- **Methodological Boundary:** Fixed-correspondence scTM uses the Zhang–Skolnick TM-score functional form and length normalization, but fixes residue correspondence ($i \mapsto i$) and performs rigid-body Kabsch superposition; it is not standard TM-align/TM-score dynamic-programming alignment optimization. The classical literature threshold of 0.5 for "same fold" or "identical global fold topology" was established for dynamic-programming alignment optimization and MUST NOT be inherited as an interpretive threshold for this fixed-correspondence metric. The project makes zero claims of "identical fold" or "universal threshold" based on fixed-correspondence scTM; it is utilized strictly as a continuous, length-normalized structural similarity endpoint.

---

## 3. Primary Statistical Comparison
The primary comparison is the target-level paired difference:
$$d_t = \overline{\text{scTM}}_{\text{hybrid}}(t) - \overline{\text{scTM}}_{\text{MPNN-only}}(t) \quad \text{for } t = 1, \dots, N$$
evaluated target-by-target across the primary test set ($N = 50$ TS50 targets).

---

## 4. Statistical Unit of Analysis
The unit of statistical analysis is the **TARGET / BACKBONE** ($N = 50$).
Individual generated candidates ($K = 500$) and selected library members ($M = 10$) within a target are nested observations and are treated as internal replicates, not independent statistical units.

---

## 5. Statistical Hypothesis Test
- **Test:** Two-sided paired Wilcoxon signed-rank test on target-level paired differences $\{d_t\}_{t=1}^N$:
  $$d_t = \overline{\text{scTM}}_{\text{hybrid}}(t) - \overline{\text{scTM}}_{\text{MPNN-only}}(t)$$
- **Significance Level:** $\alpha = 0.01$ (two-tailed, pre-registered confirmatory threshold).
- **Exact Implementation Details:**
  - Software & Library: Python 3.11 with SciPy v1.17.1 reference (`scipy.stats.wilcoxon`).
  - Function call: `scipy.stats.wilcoxon(d_t, zero_method='wilcox', correction=True, alternative='two-sided', method='asymptotic')`.
  - Approximation method: The confirmatory p-value is computed with the pre-registered asymptotic/normal approximation and continuity correction (`method='asymptotic'`, `correction=True`).
  - Zero-difference policy: zero differences ($d_t = 0$) are handled using the Wilcox convention (discards zeros from ranking).
  - Tie handling in $|d_t|$: average rank assignment (`method='average'`).
  - Continuity correction: enabled (`correction=True`).
- **Effect Sizes:**
  - Hodges-Lehmann paired median difference estimator (median of all pairwise Walsh averages $(d_i + d_j)/2$).
  - Paired Cohen's $d_z = \bar{d} / s_d$.
- **Edge Cases & Input Validation:**
  - Finite Numeric Validation: All input paired differences must be finite real numbers. Inputs containing NaN or infinite values raise an explicit validation error and are rejected rather than silently omitted.
  - Sample Size Requirement: Requires at least $N \ge 2$ paired observations.
  - If all $d_t = 0$: $p = 1.0$, Hodges-Lehmann effect size = $0.0$, Cohen's $d_z = 0.0$.
  - Zero standard deviation ($s_d = 0$): $d_z = 0.0$.
  - Insufficient valid target pairs: exclusions reported explicitly with reasons.
- **Confidence Intervals & Bootstrap Estimands:**
  - 95% and 99% nonparametric bootstrap confidence intervals derived strictly from **10,000 resamples of TARGET-LEVEL paired differences $d_t$** ($N = 50$).
  - Resampling RNG Seed: Fixed integer seed = 42 (`np.random.default_rng(42)`).
  - Interval Type: Percentile bootstrap ($2.5^{\text{th}}$ and $97.5^{\text{th}}$ percentiles for 95% CI; $0.5^{\text{th}}$ and $99.5^{\text{th}}$ percentiles for 99% CI).
  - Primary Estimand: Mean target-level paired difference $\Delta \overline{\text{scTM}} = \frac{1}{N_{\text{valid}}} \sum_{t=1}^{N_{\text{valid}}} d_t$.
  - Secondary Estimand: Hodges-Lehmann median paired difference.
  - Prohibition: Individual candidate sequences are nested replicates within targets and are STRICTLY NEVER bootstrapped.
- **Multiple Comparisons Policy:** Exactly **ONE primary confirmatory hypothesis comparison** is evaluated. All secondary analyses (alternative temperatures, seeds, ablations, PiFold/ESM-IF1 baselines, raw-logit interpolation, oracle sensitivity) are explicitly designated as exploratory and unadjusted.
- **Three-State Target Outcome Taxonomy:**
  1. **Missing Primary Endpoint (`SELECTION_INFEASIBLE_LT_M`):** Arm produces fewer than $M = 10$ unique viable candidates during screening. Primary endpoint for that target/arm is missing/undefined; no numeric scTM is manufactured. Evaluated via complete-case paired analysis; additionally reported under conservative zero-quality sensitivity analysis ($\overline{\text{scTM}} = 0.0$).
  2. **Scientific / Model Folding Failure:** Validation oracle completes inference normally, but the predicted structure is biologically non-physical (steric clash collapse, NaN/inf coordinates, disjoint C$\alpha$ trace) or confidence is below structural definition ($\text{pLDDT} < 10.0$). Assigned $\text{scTM} = 0.0$, included in $\{d_t\}$.
  3. **Infrastructure / Runtime Failure:** Oracle fails due to hardware or runtime exceptions (GPU OOM, process timeout > 600s/target, driver/CUDA crash, environment failure, missing/corrupted file).
     - Infrastructure failures are **NEVER assigned $\text{scTM} = 0.0$**.
     - **Deterministic Retry Policy:** Retry exactly once using the identical frozen model, checkpoint, version, precision, device, chunk size, seed, input, timeout, and protocol configuration. Only process restart/resource cleanup is permitted. No scientific or inference parameter may be changed during the retry.
     - If unresolvable on target $t$, target $t$ is marked as `INFRASTRUCTURE_FAILURE_UNVALIDATED` and excluded from complete-case paired comparison $\{d_t\}$.
     - Target-level infrastructure failure rate $F_{\text{infra}} = N_{\text{infra}} / N_{\text{total}}$ is strictly tracked.
     - If $F_{\text{infra}} > 10\%$ (e.g. $> 5$ of 50 TS50 targets), the benchmark run is automatically declared **INVALID / INCONCLUSIVE** (Criterion 5 of Section 24), halting evaluation.
     - **Candidate-Level Screening Infrastructure Failure (ESMFold):** If an individual candidate fails ESMFold screening for infrastructure reasons, retry exactly once with the identical frozen configuration. If it still fails, mark candidate as infrastructure-unvalidated (never assign viability 0.0, never regenerate). Exclude it from the viable candidate set because screening status is unknown. Continue processing remaining fixed $K$ candidates; the existing $M=10$ viability/infeasibility rule determines whether the target remains eligible. Report the count of screening-infrastructure failures.
     - **Development-Time AF2 Infrastructure Failure:** For development hyperparameter optimization, the objective $J$ requires all 20 development targets to produce complete $M=10$ validated endpoints. If a selected candidate fails AF2 validation for infrastructure reasons, retry once with the identical frozen configuration. If still failing, never assign $\text{scTM} = 0.0$, do not regenerate or substitute another sequence. The configuration cannot produce the required complete $M=10$ endpoint set; classify the configuration as INELIGIBLE and assign $J = -\infty$ for argmax selection.
- **Stratification:** Primary hypothesis testing is evaluated on natural targets ($N = 50$, TS50). The de novo test set ($N = 15$, RFdiffusion) is evaluated and reported as a separate stratified analysis.


---

## 6. Candidate Budgets (Unambiguous Accounting)
- **$K$ (Generation Budget — Definitive Interpretation):**
  - $K$ is defined strictly as the **TOTAL candidate sequences generated PER TARGET PER METHOD/ARM across all temperatures and random seeds (Interpretation A)**.
  - It is **NEVER interpreted as per-condition or per-temperature $\times$ seed**.
  - **Budget Allocation:**
    - Development / Tuning Set: $K = 100$ total candidates per target.
    - Primary Test Set: $K = 500$ total candidates per target.
  - **Development / Tuning Allocation Matrices ($K = 100$ per target):**
    - **ProteinMPNN Development Allocation:**
      | Temperature | Seed 42 | Seed 1337 | Seed 2026 | Subtotal |
      | :--- | :---: | :---: | :---: | :---: |
      | $T=0.1$ | 7 | 7 | 6 | 20 |
      | $T=0.2$ | 7 | 6 | 7 | 20 |
      | $T=0.5$ | 6 | 7 | 7 | 20 |
      | $T=0.8$ | 7 | 7 | 6 | 20 |
      | $T=1.0$ | 7 | 6 | 7 | 20 |
      | **Per-Seed Total** | **34** | **33** | **33** | **100** |
    - **ProteinSolver E0-B Development Allocation:**
      | Temperature | Seed 42 | Seed 1337 | Seed 2026 | Subtotal |
      | :--- | :---: | :---: | :---: | :---: |
      | $T=0.1$ | 12 | 11 | 11 | 34 |
      | $T=0.5$ | 11 | 11 | 11 | 33 |
      | $T=1.0$ | 11 | 11 | 11 | 33 |
      | **Per-Seed Total** | **34** | **33** | **33** | **100** |
  - **Primary Test Set Allocation on TS50 ($K = 500$ per target at frozen $T^*$):**
    - **Standalone ProteinMPNN:** Exactly 500 total generated sequences per target at frozen optimal temperature $T^*_{\text{MPNN}}$ (selected on tuning set). Distributed across 3 pre-registered seeds: Seed 42 ($N = 167$), Seed 1337 ($N = 167$), Seed 2026 ($N = 166$). Resulting total sequences = 500. Zero test-time temperature sweep.
    - **Stochastic ProteinSolver (E0-B Baseline):** Exactly 500 total generated sequences per target at frozen optimal temperature $T^*_{\text{PS}}$ (selected on tuning set). Distributed across 3 pre-registered seeds: Seed 42 ($N = 167$), Seed 1337 ($N = 167$), Seed 2026 ($N = 166$). Resulting total sequences = 500. Zero test-time temperature sweep.
    - **Primary Hybrid Method:** Evaluates the Common Candidate Universe $U_t$ of size $K = 500$ generated by ProteinMPNN at frozen $T^*_{\text{MPNN}}$ (with the 167/167/166 seed allocation). Both ProteinMPNN and ProteinSolver score the exact same 500 sequences. ProteinSolver performs scoring only and does NOT generate an independent candidate pool for the primary hybrid. Resulting total newly generated sequences = 0.
    - **Historical Deterministic ProteinSolver (E0-A Control):** Exactly 1 sequence on target 1n5uA03 (MAP decoding, 41.30% recovery; single target integration control, NOT part of TS50 benchmark).
  - **Explicit Distinction of Three Generation Modes:**
    1. *Development Parameter Selection:* Cartesian grid search ($T \times \gamma$) evaluated on the 20 development backbones under objective $J$ (Section 8).
    2. *Frozen Test-Time Generation:* Monolithic generation of 500 candidates strictly at frozen $T^*$ across the 167/167/166 seed partition on TS50.
    3. *E0-A Historical Control:* Single-target deterministic MAP verification.

  - **Matched Budget Rule:** Standalone ProteinMPNN and Primary Hybrid methods evaluate exactly matched candidate pools of size $K = 500$ per target.
  - **Selection Library Size ($M$):** Exactly $M = 10$ candidates selected per target from the viable candidate subset $S_{\text{viable}} \subseteq S_{\text{raw}}$.
  - **Validation Pool:** Exactly the $M = 10$ selected candidates are evaluated by the primary final validation oracle (AlphaFold2).

---

## 7. Randomness & Reproducibility
- **Reproducible Candidate Identity:** Every generated sequence has a globally unique, reproducible identifier:
  $$\text{ID} = \texttt{\{target\_id\}\_\{method\_arm\}\_T\{temperature\}\_s\{seed\}\_idx\{seq\_idx:04d\}}$$
- **RNG Stream Separation:** Independent random number generator states are maintained for Python (`random`), NumPy (`np.random`), PyTorch (`torch.manual_seed`), and CUDA (`torch.cuda.manual_seed_all`). Accidental reuse or interleaving of RNG streams between arms is strictly forbidden.
- **Residue Permutation Decoding Order:** In the official ProteinMPNN implementation, random residue permutation decoding orders are drawn deterministically per sequence sample under the PyTorch RNG initialized with the specified integer seed. This official model behavior is preserved and documented.
- **ProteinSolver Sampling:** Stochastic CSP sampling uses PyTorch multinomial sampling on masked logits governed by the specified integer seed.

---

## 8. Development Hyperparameter Selection & Freezing Protocol ($T^*, \lambda^*, \gamma^*$)
- **Development / Tuning Set ($N_{\text{dev}} = 20$):** Hyperparameter selection for temperatures $T^*$, mixing coefficient $\lambda^*$, and diversity weights $\gamma^*$ is conducted **exclusively on the 20 CATH 4.2 validation backbones** frozen in the immutable manifest:
  - **Manifest File:** `data/manifests/development_20_cath42.txt` (canonical LF SHA-256: `47ab5fec66017b455f7eabee143dc83e99ec740640e945ed96752abb59483069`).
  - **Canonical Provenance:** Ingraham et al. (NeurIPS 2019) / Dauparas et al. (Science 2022) CATH 4.2 validation split (`chain_set_splits.json`, raw downloaded artifact SHA-256: `8e9a587a50c7f6c026e4ed00f6c1c30b106100f36f7a01de47542bdfc060adc2`).
  - **Deterministic Selection Rule:** Deterministic first encounter of unique primary CATH topology (Class.Arch.Topology) in canonical validation split order across 20 distinct CATH topologies covering classes 1, 2, 3, and 4:
    `2e6i.A` (4.10.1130), `2mh3.A` (4.10.280), `3gn4.E` (1.10.3060), `2qg3.A` (3.30.1960), `3abd.B` (3.30.900), `1z8s.A` (1.10.860), `5t5d.A` (3.40.35), `1f7e.A` (2.10.25), `2lg7.A` (2.60.60), `1h2s.A` (1.20.1070), `1yf9.A` (3.10.110), `2p2e.A` (2.60.300), `1cel.A` (2.70.100), `2kil.A` (3.90.1520), `1c52.A` (1.10.760), `2gmy.D` (1.20.1290), `1nyn.A` (3.30.1250), `2c6u.A` (3.10.100), `2ctt.A` (2.10.230), `3hxi.A` (3.30.760).
  - *Topology Deduplication Note:* Target `4bdx.A` (chain 11 in validation split) has primary topology `2.10.25`, which duplicates chain 8 (`1f7e.A`), and is therefore correctly bypassed by the unique-topology selection rule, leading to the selection of `3hxi.A` (3.30.760).
  - Zero tuning or parameter selection against primary test outcomes (TS50) is permitted.
- **Scalar Development Optimization Objective ($J$):**
  The scalar development optimization objective for all hyperparameter selection is the mean over the 20 development targets of the target-level mean fixed-correspondence scTM of the final selected $M=10$ library after the complete prescribed development pipeline:
  $$J = \frac{1}{N_{\text{dev}}} \sum_{t=1}^{N_{\text{dev}}} \overline{\text{scTM}}_{\text{val}}(t) = \frac{1}{N_{\text{dev}}} \sum_{t=1}^{N_{\text{dev}}} \left( \frac{1}{M} \sum_{m=1}^M \text{scTM}_{\text{val}}(s_{t,m}) \right)$$
  where:
  - $N_{\text{dev}} = 20$ CATH 4.2 validation backbones from the frozen manifest.
  - $M = 10$ selected library size.
  - $\text{scTM}_{\text{val}}$ is produced by the frozen Primary Final Structural Validation Oracle: AlphaFold2 v2.3.2, monomodel weights `model_1_ptm`, single-sequence mode (no MSA, no templates), 3 recycles, precision `float16` (`fp16`) on GPU (CUDA), fixed inference seed = 42 (seed controls stochastic initialization but does not guarantee bitwise GPU determinism across heterogeneous hardware/CUDA drivers), standard Amber relaxation disabled. No surrogate objective is permitted.
- **Development Infeasibility Rule ($J = -\infty$):**
  For development hyperparameter optimization only:
  - Every candidate hyperparameter configuration must successfully produce an $M=10$ unique viable library on ALL 20 development targets to be eligible for the primary $J$ argmax.
  - If ANY single target is `SELECTION_INFEASIBLE_LT_M` ($<10$ unique viable candidates) for that configuration, the configuration is INELIGIBLE and receives objective $J = -\infty$ for argmax purposes.
  - Do NOT replace missing/infeasible development target scTM with 0.0.
  - Do NOT exclude the infeasible target and average over the remaining targets.
  - Do NOT reduce $M$.
  - Do NOT regenerate beyond $K=100$.
  - Do NOT alter screening thresholds.
  - Do NOT silently substitute another temperature or seed.
  - Report the configuration's target infeasibility rate separately: $\text{infeasibility\_rate} = \frac{N_{\text{infeasible}}}{N_{\text{dev}}}$.
  - If every configuration for an arm is infeasible, STOP THAT TUNING ARM and classify the development tuning stage as `DEVELOPMENT_TUNING_STAGE_INFEASIBLE` rather than inventing a fallback.
- **MPNN-Only Parameter Selection ($T^*_{\text{MPNN}}, \gamma^*_{\text{MPNN}}$):**
  - Search Space: Complete Cartesian product $T_{\text{MPNN}} \times \gamma$ (25 combinations):
    $$T_{\text{MPNN}} \in \{0.1, 0.2, 0.5, 0.8, 1.0\}, \quad \gamma \in \{0.0, 0.25, 0.5, 1.0, 2.0\}$$
  - Pipeline for every combination: Candidate generation ($K=100$) $\to$ ESMFold viability screening $\to$ duplicate handling $\to$ $M=10$ greedy selection $\to$ AlphaFold2 validation $\to$ objective $J$.
  - Selection Rule: $(T^*_{\text{MPNN}}, \gamma^*_{\text{MPNN}}) = \arg\max J$.
- **ProteinSolver E0-B Parameter Selection ($T^*_{\text{PS}}, \gamma^*_{\text{PS}}$):**
  - Search Space: Complete Cartesian product $T_{\text{PS}} \times \gamma$ (15 combinations):
    $$T_{\text{PS}} \in \{0.1, 0.5, 1.0\}, \quad \gamma \in \{0.0, 0.25, 0.5, 1.0, 2.0\}$$
  - Complete development pipeline evaluated under identical objective $J$.
  - Selection Rule: $(T^*_{\text{PS}}, \gamma^*_{\text{PS}}) = \arg\max J$.
- **Primary Hybrid Parameter Selection ($\lambda^*, \gamma^*_{\text{hybrid}}$):**
  - Candidate Universe Constraint: The primary hybrid MUST evaluate the identical Common Candidate Universe $U_t$ generated by ProteinMPNN at $T^*_{\text{MPNN}}$. Therefore:
    $$T^*_{\text{hybrid}} = T^*_{\text{MPNN}}$$
    Zero independent temperature sweep is conducted for the hybrid method.
  - Search Space: Complete Cartesian product $\lambda \times \gamma$ (35 combinations):
    $$\lambda \in \{0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0\}, \quad \gamma \in \{0.0, 0.25, 0.5, 1.0, 2.0\}$$
  - Pipeline for every combination: Score candidate universe $U_t$ with both models $\to$ within-pool percentile rank normalization $\to$ compute $H(u)$ $\to$ ESMFold viability screening $\to$ unique viable deduplication $\to$ $M=10$ greedy selection $\to$ AlphaFold2 validation $\to$ objective $J$.
  - Selection Rule: $(\lambda^*, \gamma^*_{\text{hybrid}}) = \arg\max J$.
- **Development Generation Reuse & Efficiency (Caching):**
  - To avoid redundant re-generation without altering protocol semantics:
    - MPNN Development: Generate candidate pools once for each target $\times$ temperature $\times$ seed allocation, screen once with ESMFold, score once, and reuse across all $\gamma$ values at that temperature.
    - ProteinSolver Development: Generate candidate pools once for each target $\times$ temperature $\times$ seed allocation, screen once, score once, and reuse across all $\gamma$ values at that temperature.
    - Hybrid Development: Generate Common Candidate Universe $U_t$ once at $T^*_{\text{MPNN}}$, score all candidates with both models once, compute within-pool percentiles once, and reuse across all 35 $(\lambda, \gamma)$ combinations.
  - Caching MUST NOT alter candidate identities, ordering, counts, RNG states, scores, screening outcomes, or selection behavior.
- **Deterministic 5-Step Freezing Order:**
  1. Select $(T^*_{\text{MPNN}}, \gamma^*_{\text{MPNN}})$ via Cartesian grid search on development set.
  2. Select $(T^*_{\text{PS}}, \gamma^*_{\text{PS}})$ via Cartesian grid search on development set.
  3. Using $T^*_{\text{MPNN}}$, generate Common Candidate Universe $U_t$ and select $(\lambda^*, \gamma^*_{\text{hybrid}})$.
  4. Freeze ALL resulting parameters: $(T^*_{\text{MPNN}}, \gamma^*_{\text{MPNN}}, T^*_{\text{PS}}, \gamma^*_{\text{PS}}, T^*_{\text{hybrid}}, \lambda^*, \gamma^*_{\text{hybrid}})$.
  5. Only then permit TS50 primary benchmark execution. TS50 targets are NEVER inspected prior to complete parameter freeze.
- **Deterministic Tie-Breaking Rule:**
  If two or more parameter combinations achieve exactly equal development objective $J$:
  - For $(T, \gamma)$: Select the combination that is first in ascending lexicographical order (sort key: $T$ ascending, then $\gamma$ ascending).
  - For $(\lambda, \gamma)$: Select the combination that is first in ascending lexicographical order (sort key: $\lambda$ ascending, then $\gamma$ ascending).
  - Prohibited Criteria: No tie-breaking may use amino acid recovery (AAR), computational latency, sequence diversity, model perplexity/pseudo-perplexity, visual inspection, implementation convenience, or anticipated test behavior.
- **Development Failure & Missing Data Handling:**
  Reuses the existing frozen failure taxonomy:
  - Generative biological folding failure: Assigned $\text{scTM} = 0.0$ and included in target mean.
  - Infrastructure failure (AF2 validation): Retried exactly once using the identical frozen configuration. If unresolvable on any selected candidate, never assign $\text{scTM} = 0.0$, do not regenerate or substitute sequences. The target cannot produce the required complete $M=10$ endpoint set; classify the configuration as INELIGIBLE and assign $J = -\infty$ for argmax selection.
  - Insufficient unique viable candidates ($< 10$): Target classified as `SELECTION_INFEASIBLE_LT_M`. For development hyperparameter optimization, the configuration receives $J = -\infty$ (ineligible for argmax). For confirmatory test-set analysis, missing in complete-case analysis, and assigned 0.0 under conservative sensitivity analysis.


---


## 9. Primary Hybrid Method & Common Candidate Universe
- **Common Candidate Universe Architecture:**
  The primary hybrid is **NOT a joint generator**. Its definitive operational pipeline is:
  $$\text{ProteinMPNN generates } U_t \longrightarrow \text{Scored by ProteinMPNN } [S_{\text{MPNN}}] \longrightarrow \text{Scored by ProteinSolver } [S_{\text{PS}}] \longrightarrow \text{Percentile Normalization } [p_{\text{MPNN}}, p_{\text{PS}}] \longrightarrow \text{Hybrid Score } H(u)$$
- **Integrity Rule:** For every target $t$, the candidate universe $U_t$ contains exactly $K = 500$ sequences generated by ProteinMPNN at frozen $T^*_{\text{MPNN}}$. ProteinSolver performs scoring only. Sequences scored by both models MUST be identical and in identical candidate identity order (`validate_common_candidate_order`) before percentile ranks are computed.
- **Step-by-Step Pipeline:**
  1. **Candidate Universe Generation:** Generate candidate pool $U_t = \{u_1, \dots, u_K\}$ of size $K$ ($K=100$ tuning, $K=500$ primary test).
  2. **ProteinMPNN Scoring:** Compute sequence-level mean autoregressive log-probability $S_{\text{MPNN}}(u)$ for each $u \in U_t$. In the official cleanroom wrapper, candidates are scored along their exact generation-time decoding permutation (`use_input_decoding_order=True, decoding_order=decoding_order`), ensuring that candidate scoring is strictly reproducible and that zero hidden re-sampling of permutations occurs.
  3. **ProteinSolver Scoring:** Compute sequence-level mean single-site masked pseudo-log-likelihood $S_{\text{PS}}(u)$ for each $u \in U_t$ (PLL scan; explicitly NOT called autoregressive log-likelihood).
  4. **Within-Universe Percentile Normalization:**
     $$p_{\text{MPNN}}(u) = \frac{\text{rank}(S_{\text{MPNN}}(u))}{K} \in (0, 1]$$
     $$p_{\text{PS}}(u) = \frac{\text{rank}(S_{\text{PS}}(u))}{K} \in (0, 1]$$
     where ranks are computed strictly within $U_t$ with average tie-breaking (`scipy.stats.rankdata(..., method='average')`). Higher percentile always indicates higher confidence.
  5. **Hybrid Score Calculation:**
     $$H(u) = \lambda^* \cdot p_{\text{MPNN}}(u) + (1 - \lambda^*) \cdot p_{\text{PS}}(u)$$
     where $\lambda^*$ is pre-frozen on the development set.
  6. **Screening & Diversity Selection:** Hard viability gate ($\text{scRMSD}_{\text{screen}} \le 2.0\text{ \AA} \land \text{pLDDT}_{\text{screen}} \ge 80.0$) $\to$ deduplication to unique viable candidates $\to$ Stage 2 diversity-aware selection heuristic $\to$ final library $S_{\text{selected}}$ ($M = 10$).

---

## 10. Exploratory Raw-Logit Ablation
- Raw logit interpolation:
  $$z_{\text{hybrid}}(a_i) = \lambda \cdot z_{\text{MPNN}}(a_i) + (1 - \lambda) \cdot z_{\text{PS}}(a_i)$$
  is categorized strictly as an **exploratory ablation**. It must NEVER be presented as the primary hybrid method.

---

## 11. Screening Oracle Configuration & Thresholds (ESMFold)
- **Applicability Scope:** The frozen ESMFold execution path applies to all registered benchmark pipeline stages that use ESMFold, including E1 development tuning and TS50 primary evaluation.
- **Exact Oracle Implementation:** Meta AI `esm` (v2.0.0) / Hugging Face `transformers` `facebook/esmfold_v1`.
- **Model Checkpoint:** `esmfold_v1` (3B parameters; pinned to canonical Meta AI / Hugging Face release artifact).
- **Inference Mode:** Sequence-only input mode (zero MSA search, zero homologous templates).
- **Recycle Count:** Exactly 4 recycles (`num_recycles = 4`, canonical default).
- **Precision & Device (Frozen Benchmark Path):** Strictly `float16` (`fp16`) on GPU (CUDA). If CUDA is unavailable or a GPU out-of-memory error occurs, it is classified as `INFRASTRUCTURE_FAILURE` (retried exactly once using the identical frozen configuration, then logged as unvalidated if unresolvable), NEVER silently falling back to CPU or alternative precisions. CPU `float32` execution is classified strictly as a non-confirmatory local diagnostic / smoke-test mode and is prohibited from producing confirmatory benchmark evidence.
- **Sequence Length Guard:** Maximum sequence length $L \le 1024$ residues. Target manifests must be validated for this constraint before E1 or TS50 execution; targets with $L > 1024$ are rejected at preflight time (silent truncation, chunking alteration, or oracle substitution is strictly prohibited).
- **Internal Tensor Chunking (Frozen Benchmark Path):** Attention/trunk chunking frozen to `model.set_chunk_size(128)`. If chunk size 128 fails due to memory exhaustion, it is treated as an infrastructure failure, not a silent parameter change. Alternative chunk sizes (such as 64) are classified strictly as non-confirmatory diagnostic modes. Internal chunk size is distinct from sequence length.
- **Screening Seed:** Fixed integer seed = 42 (`seed = 42`).
- **Output & Metric Extraction:**
  - 3D atomic coordinates extracted from predicted structure.
  - $C_\alpha$ mapping: 1-to-1 residue index correspondence to native target backbone without gap insertion.
  - $\text{scRMSD}_{\text{screen}}$: Kabsch-aligned root-mean-square deviation of $C_\alpha$ coordinates against native backbone.
  - $\text{pLDDT}_{\text{screen}}$: Arithmetic mean of per-residue predicted LDDT values across the sequence: $\text{pLDDT} = \frac{1}{L} \sum_{i=1}^L \text{pLDDT}_i \in [0, 100]$.
- **Operational Screening Thresholds:**
  $$\text{scRMSD}_{\text{screen}} \le 2.0\text{ \AA} \quad \text{AND} \quad \text{pLDDT}_{\text{screen}} \ge 80.0$$
  - Candidates satisfying both criteria enter $S_{\text{viable}}$.
  - Candidates failing either criterion are classified as structural folding failures and excluded from $S_{\text{viable}}$.
  - If a sequence cannot be evaluated due to memory error, library crash, or runtime exception, it is retried exactly once under the identical frozen configuration. If still failing, it is classified as `INFRASTRUCTURE_FAILURE`, excluded from the viable candidate set (never assigned viability 0.0, never regenerated), and reported in the screening infrastructure failure count.


---

## 12. Threshold Provenance
- **Provenance Classification:** **Project-Chosen Operational Screening Thresholds**.
- Informed by established literature standards (Watson et al. 2023 RFdiffusion, Dauparas et al. 2022 ProteinMPNN, Lin et al. 2023 ESMFold, Baker Lab de novo design).
- They were NOT calibrated on our project's test data and are NOT universal physical constants.

---

## 13. Primary Final Structural Validation Oracle (AlphaFold2)
- **Exact Oracle Implementation:** **AlphaFold2 (v2.3.2)** / ColabFold single-sequence inference pipeline.
- **Model Checkpoint:** Monomodel weights `model_1_ptm` (384-dim evoformer, fine-tuned with pTM head).
- **Exact Numerical Precision:** `float16` (`fp16`) on GPU (CUDA). (FP16/BF16 alternatives removed; float16 is strictly frozen).
- **Recycle Count:** Exactly 3 recycles (`num_recycle = 3`).
- **Template Policy:** Homologous structural templates disabled (`use_templates = False`).
- **MSA Policy:** Single sequence mode (`msa_mode = "single_sequence"`, no MSA search; sequence query replicated as single-sequence MSA).
- **Amber Relaxation:** Disabled (`use_amber = False`).
- **Fixed Inference Seed:** Fixed inference seed = 42 (`random_seed = 42`). Setting a fixed random seed controls stochastic initialization and sampling within the framework, but does not guarantee bitwise GPU determinism across heterogeneous hardware architectures, CUDA drivers, or cuBLAS algorithm selections.
- **Hardware Platform:** NVIDIA RTX 3050 6GB Laptop GPU (CUDA).
- **Residue & Structure Alignment Specifications:**
  - **Residue Correspondence:** 1-to-1 residue index correspondence ($i$-th residue of design corresponds strictly to $i$-th residue of target backbone without gap insertion or alignment shifting).
  - **$C_\alpha$ Coordinate Extraction:** Cartesian coordinates extracted strictly from canonical residue atoms (`ATOM ... CA ...`).
  - **Target Backbone Preprocessing:** Native target PDBs are cleaned of water molecules, heteroatoms (`HETATM`), and alternate conformations (retaining conformation 'A' or highest occupancy).
  - **Length Invariant:** Target and candidate sequence lengths must match exactly ($|s| = L$). Any length mismatch is classified as a fatal error (`INFRASTRUCTURE_FAILURE`).
  - **Unresolved Residue Rule:** Every target backbone in the frozen development manifest and test set must have 100% resolved $C_\alpha$ coordinates across all residues $1..L$. Missing internal backbone coordinates render the target invalid.
  - **Chain Selection:** For multi-chain native structures, target chain is explicitly specified by chain identifier (e.g. `chain A`). Single-chain inference is conducted on designed sequences.
  - **Output Coordinate Selection:** Model output $C_\alpha$ coordinates are extracted from the rank-1 prediction of model 1 (`model_1_ptm`, unrelaxed structure).
- **Firewall Rule:** AlphaFold2 is strictly reserved for validating the final selected candidate library ($M=10$). It is NEVER used during initial candidate generation, screening, or candidate selection.

---

## 14. Sensitivity Validation Oracle
- **Oracle:** **Boltz-1 (v0.4.1)**
- **Role:** Pre-registered secondary sensitivity analysis. Used to test whether conclusions are sensitive to folding oracle architecture.

---

## 15. Final Candidate Selection Procedure
- **Stage 1 (Hard Viability Gate):**
  Candidates failing $\text{scRMSD}_{\text{screen}} \le 2.0\text{ \AA}$ or $\text{pLDDT}_{\text{screen}} \ge 80.0$ are discarded, forming the viable pool $S_{\text{viable}}$.
- **Duplicate Accounting & Unique Candidate Filtering:**
  - The generation budget $K$ counts every generated sequence, including duplicates ($|S_{\text{raw}}| = K$).
  - Exact duplicate sequences are retained in raw-generation accounting and reported as:
    $$\text{Duplicate Rate} = \frac{|S_{\text{raw}}| - |S_{\text{raw, unique}}|}{|S_{\text{raw}}|}$$
  - For final diversity-aware selection, the pipeline operates strictly on **UNIQUE viable sequences** ($S_{\text{viable, unique}} \subseteq S_{\text{viable}}$).
  - For identical sequences passing screening, the candidate with the highest primary score is retained (ties broken deterministically by candidate ID).
  - Exact duplicates contribute zero pairwise Hamming distance ($d(u, u) = 0.0$).
  - Duplicate candidates are **NEVER silently regenerated**.
- **Insufficient Viable Candidates Policy ($|S_{\text{viable, unique}}| < M=10$):**
  - If an arm produces fewer than $M = 10$ unique viable candidates on a target backbone:
    - The target arm is classified as **`SELECTION_INFEASIBLE_LT_M`**.
    - The pipeline does **NOT** silently regenerate sequences.
    - The pipeline does **NOT** pad with screening-failed candidates or duplicates.
    - The pipeline does **NOT** alter screening thresholds post hoc or reduce $M$.
    - For the primary confirmatory paired comparison, the target is treated as missing/undefined and excluded in the complete-case analysis.
    - The selection infeasibility rate $F_{\text{infeasible}} = N_{\text{infeasible}} / N_{\text{total}}$ is reported for each arm.
    - A secondary sensitivity analysis is reported treating all selection-infeasible targets conservatively as zero-quality ($\overline{\text{scTM}} = 0.0$).
- **Stage 2 (Greedy Diversity-Aware Selection Heuristic):**
  From $S_{\text{viable, unique}}$, greedily select $M = 10$ candidates maximizing:
  - **First Selection ($S' = \emptyset$):**
    $$u_1 = \arg\max_{u \in S_{\text{viable, unique}}} \text{score}(u)$$
  - **Subsequent Selections ($1 \le |S'| < M$):**
    $$u^* = \arg\max_{u \in S_{\text{viable, unique}} \setminus S'} \left[ \text{score}(u) + \gamma^* \cdot \min_{v \in S'} d(u, v) \right]$$
    where $d(u, v)$ is normalized Hamming distance in $[0, 1]$.
- **Normalization Consistency of Baseline Selection:**
  - Because diversity distance $d(u, v) \in [0, 1]$ and hybrid score $H(u) \in (0, 1]$, the standalone MPNN-only arm must use scores on the exact same $[0, 1]$ scale:
    - Primary Hybrid Arm: $\text{score}_{\text{hybrid}}(u) = H(u) \in (0, 1]$
    - Primary MPNN-Only Arm: $\text{score}_{\text{MPNN-only}}(u) = p_{\text{MPNN}}(u) \in (0, 1]$
  - Both primary arms operate on the matched percentile rank scale inside the greedy selector, ensuring scale compatibility across arms. Autoregressive perplexity remains a diagnostic metric.
- **Diversity Weight ($\gamma$) Search Grid:**
  - Dimensionless pre-registered search grid:
    $$\gamma \in \{0.0, 0.25, 0.5, 1.0, 2.0\}$$
  - Tuned exclusively on the development set separately for MPNN-only ($\gamma^*_{\text{MPNN}}$) and primary hybrid ($\gamma^*_{\text{hybrid}}$) via the Cartesian grid optimization protocol specified in Section 8.
  - Strictly frozen prior to TS50 benchmark evaluation; zero test-time tuning permitted.
- **Deterministic Tie Breaking:**
  - All ties in primary score or greedy objective are broken deterministically by stable candidate identifier order (ascending lexicographical ID).
- **Reporting Rule:** The greedy selection objective is a construction heuristic; final library diversity is evaluated independently after selection.

---

## 16. Sequence Diversity Definition
- **Metric:** Order-independent mean pairwise normalized Hamming distance:
  $$\text{Div}(S) = \frac{2}{M(M - 1)} \sum_{1 \le j < k \le M} \frac{1}{L} \sum_{i=1}^L \mathbb{I}(s_j[i] \ne s_k[i])$$
- If $M < 2$, $\text{Div}(S) = 0.0$ by definition.
- Duplicates retain distance $0.0$.
- Reported statistics: Mean, standard deviation, and median.
- Evaluated at three distinct stages: $\text{Div}_{\text{raw}}$, $\text{Div}_{\text{viable}}$, $\text{Div}_{\text{selected}}$.

---

## 17. Pareto Hypervolume (HV) Treatment
- **Status:** **Exploratory Descriptive Analysis** (demoted from primary evaluation).
- When computed, uses pre-declared external normalization bounds:
  - $f_1 = \text{scTM} \in [0, 1]$
  - $f_2 = 1.0 - \min(1.0, \text{scRMSD} / 10.0) \in [0, 1]$
  - $f_3 = \text{pLDDT} / 100.0 \in [0, 1]$
  - Anti-ideal reference point: $\mathbf{r} = (0.0, 0.0, 0.0)$ fixed a priori.
- Normalization bounds are NEVER derived from test-set candidate min/max values.

---

## 18. Benchmark Dataset Partitions
1. **Development / Tuning Set ($N = 20$):** CATH 4.2 validation split frozen in immutable manifest `data/manifests/development_20_cath42.txt` (canonical LF SHA-256: `47ab5fec66017b455f7eabee143dc83e99ec740640e945ed96752abb59483069`), derived deterministically from the canonical Ingraham et al. (NeurIPS 2019) / Dauparas et al. (Science 2022) validation split across 20 distinct CATH topologies. Used exclusively for hyperparameter optimization ($T^*, \lambda^*, \gamma^*$) under the deterministic Section 8 optimization protocol.
2. **Primary Test Set ($N = 50$):** TS50 non-redundant PDB crystal structures ($<30\%$ sequence identity to CATH 4.2 / ProteinMPNN training sets; ProteinSolver Gene3D 72M training membership documented per model according to Section 19: superfamily absence verified where accessible, otherwise NOT VERIFIABLE FROM ACCESSIBLE METADATA). Evaluated once with frozen parameters.
   - *Pre-Test Dependency:* The TS50 exact target manifest remains a pre-test dependency and must be frozen before TS50 benchmark execution. Development tuning (E1) is not blocked by TS50 manifest preparation.
3. **De Novo Test Set ($N = 15$):** RFdiffusion generated scaffolds. Evaluated once as a separate stratified benchmark.

---

## 19. Model-Specific Training Membership Language & Leakage Boundaries
- **Native-Sequence Leakage Audit:** No native-sequence conditioning leakage was detected in the tested ProteinSolver and ProteinMPNN cleanroom integration paths or counterfactual audits. Native sequence tokens are strictly absent during candidate generation.
- **ProteinSolver Historical Training Set:** Training membership in the 72M Gene3D corpus is classified as:
  - *"Not present in accessible training superfamily list"* (if superfamily code is absent from the 1,029 training superfamilies).
  - *"NOT VERIFIABLE FROM ACCESSIBLE METADATA"* (if raw domain membership cannot be resolved without downloading the external 72M dataset).
- **ProteinMPNN:** Documented based on CATH 4.2 training vs. test topology splits.
- **Rule:** Targets must NEVER be described as "guaranteed held-out" or "unseen".
- **Scoped Leakage Language:** Targets and candidate pipelines must NEVER be described as "completely leak-free". No native-sequence conditioning leakage was detected in the tested ProteinSolver/ProteinMPNN cleanroom integration paths and counterfactual audits. ProteinSolver historical training-set membership for benchmark targets remains NOT VERIFIABLE FROM ACCESSIBLE METADATA.

---

## 20. RFdiffusion Homology Policy
- RFdiffusion backbones must NOT be called "homology-free" without explicit sequence (BLAST against UniRef50, E-value $< 10^{-3}$) and structural (Foldseek against PDB, TM-score $> 0.5$) searches.
- Described neutrally as *"RFdiffusion-generated de novo backbones"*.

---

## 21. Secondary & Diagnostic Metrics
- **Secondary Metrics:**
  - Macro-average Native Sequence Recovery (AAR)
  - Generative Structural Viability Rate (SVR)
  - Independent Validation Yield (IVY)
  - Mean Self-Consistency RMSD (scRMSD; evaluated on 100% resolved native $C_\alpha$ backbone coordinates)
  - Net Charge at pH 7.4 ($Q_{\text{pH7.4}}$, EMBOSS scale, explicitly NOT pI)
  - Isoelectric Point ($\text{pI}$, theoretical $Q(\text{pH})=0.0$)
  - Hydrophobic Core Fraction ($f_{\text{core}} = \text{core hydrophobic} / \text{total hydrophobic}$, $\text{RSA} < 0.20$; zero-hydrophobic sequence defined as $0.0$; evaluated on ESMFold for screening pool, AlphaFold2 for selected library, Boltz-1 for sensitivity)
  - Wall-clock inference latency (seconds per sequence)
- **Diagnostic Metrics:**
  - ProteinSolver pseudo-perplexity ($\text{PPL}_{\text{PS}}$)
  - ProteinMPNN autoregressive perplexity ($\text{PPL}_{\text{MPNN}}$)

---

## 22. Secondary Baseline Reporting Policy
- **Mandatory Reporting Rule:**
  *All secondary baselines (e.g. PiFold, ESM-IF1) and exploratory ablations (e.g. logit interpolation, rescoring) that are executed MUST be reported in final publications regardless of outcome. No baseline may be selectively omitted.*

---

## 23. Standardized Latency Benchmarking Protocol
- Hardware: Fixed CPU model and GPU model (NVIDIA RTX 3050 6GB Laptop GPU).
- Precision: FP32 on CPU, FP16 on GPU.
- Batching: Batch size 1 for iterative ProteinSolver; batch sizes 1 and 32 for ProteinMPNN.
- Warmup: 5 warmup sequences before timing.
- CUDA Synchronization: `torch.cuda.synchronize()` before and after timing blocks.
- Boundaries: Model loading and graph extraction are excluded and reported as separate initialization overhead.
- Repetitions: 3 independent timing runs per target; report median and IQR.

---

## 24. Criteria for Inconclusive / Invalid Experiment
The benchmark run is classified as **INVALID** or **INCONCLUSIVE** if:
1. Candidate generation budget $K$ differs between comparison models.
2. Mixing weight $\lambda$ or diversity weight $\gamma$ was altered after inspecting primary test set results.
3. Folding oracle screening outputs (ESMFold) are reported as the sole validation of candidate viability.
4. Any historical ProteinSolver source file in `external/proteinsolver-original` is modified.
5. More than 10% of test targets (e.g. > 5 of 50 TS50 targets) fail structural folding due to hardware or runtime infrastructure crashes (OOM, timeout, crash). In such case, evaluation is halted and the experiment is declared INVALID / INCONCLUSIVE.
