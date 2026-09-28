# PRE-REGISTRATION SPECIFICATION: PROTEIN HYBRID EVALUATION STUDY
**Document ID:** `SCIENCE-PREREGISTRATION-V1`  
**Status:** **FROZEN PRIOR TO EXPERIMENTATION**  
**Effective Date:** 2026-09-25  
**Study Phase:** Pre-Phase 2 (Frozen Before ProteinMPNN Integration and Benchmark Execution)  
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
- Direction: Higher is better ($\in (0, 1]$).
- Normalization: Normalized strictly by target backbone length $L_{\text{target}}$.
- Score formulation: Zhang & Skolnick (2004) formula under optimal rigid-body Kabsch superposition on matched C$\alpha$ positions.

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
  - Python / SciPy reference: `scipy.stats.wilcoxon(x, y, zero_method='wilcox', correction=True, alternative='two-sided')`.
  - Zero-difference policy: zero differences ($d_t = 0$) are handled using the Wilcox convention (discards zeros from ranking).
  - Tie handling in $|d_t|$: average rank assignment (`method='average'`).
  - Continuity correction: enabled (`correction=True`).
- **Effect Sizes:**
  - Hodges-Lehmann paired median difference estimator (median of all pairwise Walsh averages $(d_i + d_j)/2$).
  - Paired Cohen's $d_z = \bar{d} / s_d$.
- **Edge Cases:**
  - If all $d_t = 0$: $p = 1.0$, effect size = $0.0$.
  - Zero standard deviation ($s_d = 0$): $d_z = 0.0$.
  - Insufficient valid target pairs: exclusions reported explicitly with reasons.
- **Confidence Intervals:** 95% and 99% bootstrap confidence intervals derived strictly from **10,000 resamples of TARGET-LEVEL paired differences $d_t$** ($N = 50$). Individual candidate sequences are nested replicates and are NEVER bootstrapped.
- **Multiple Comparisons Policy:** Exactly **ONE primary confirmatory hypothesis comparison** is evaluated. All secondary analyses (alternative temperatures, seeds, ablations, PiFold/ESM-IF1 baselines, raw-logit interpolation, oracle sensitivity) are explicitly designated as exploratory and unadjusted.
- **Three-State Target Outcome Taxonomy:**
  1. **Missing Primary Endpoint (`SELECTION_INFEASIBLE_LT_M`):** Arm produces fewer than $M = 10$ unique viable candidates during screening. Primary endpoint for that target/arm is missing/undefined; no numeric scTM is manufactured. Evaluated via complete-case paired analysis; additionally reported under conservative zero-quality sensitivity analysis ($\overline{\text{scTM}} = 0.0$).
  2. **Scientific / Model Folding Failure:** Validation oracle completes inference normally, but the predicted structure is biologically non-physical (steric clash collapse, NaN/inf coordinates, disjoint C$\alpha$ trace) or confidence is below structural definition ($\text{pLDDT} < 10.0$). Assigned $\text{scTM} = 0.0$, included in $\{d_t\}$.
  3. **Infrastructure / Runtime Failure:** Oracle fails due to hardware or runtime exceptions (GPU OOM, process timeout > 600s/target, driver/CUDA crash, environment failure, missing/corrupted file).
     - Infrastructure failures are **NEVER assigned $\text{scTM} = 0.0$**.
     - Failed jobs are retried exactly once under clean execution parameters.
     - If unresolvable on target $t$, target $t$ is marked as `INFRASTRUCTURE_FAILURE_UNVALIDATED` and excluded from complete-case paired comparison $\{d_t\}$.
     - Target-level infrastructure failure rate $F_{\text{infra}} = N_{\text{infra}} / N_{\text{total}}$ is strictly tracked.
     - If $F_{\text{infra}} > 10\%$ (e.g. $> 5$ of 50 TS50 targets), the benchmark run is automatically declared **INVALID / INCONCLUSIVE** (Criterion 5 of Section 24), halting evaluation.
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
    1. *Development Temperature Selection:* Multi-temperature grid search evaluated on the 20 development backbones under the balanced integer allocation matrices.
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

## 8. Hyperparameter ($\lambda$) Tuning Procedure
- **Tuning Set:** Hyperparameter search for the hybrid mixing coefficient $\lambda$ is conducted **exclusively on the Development / Tuning Set** (CATH 4.2 validation split, 20 backbones).
- **Search Grid:** $\lambda \in \{0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0\}$.
- **Objective:** Maximize mean validation-set $\overline{\text{scTM}}$.
- **Freezing Rule:** Once the optimal $\lambda^*$ is selected on the tuning set, it is **strictly frozen** before running inference or evaluation on the primary test set. Zero tuning against test outcomes is permitted.

---

## 9. Primary Hybrid Method & Common Candidate Universe
- **Common Candidate Universe Architecture:**
  The primary hybrid is **NOT a joint generator**. Its definitive operational pipeline is:
  $$\text{ProteinMPNN generates } U_t \longrightarrow \text{Scored by ProteinMPNN } [S_{\text{MPNN}}] \longrightarrow \text{Scored by ProteinSolver } [S_{\text{PS}}] \longrightarrow \text{Percentile Normalization } [p_{\text{MPNN}}, p_{\text{PS}}] \longrightarrow \text{Hybrid Score } H(u)$$
- **Integrity Rule:** For every target $t$, the candidate universe $U_t$ contains exactly $K = 500$ sequences generated by ProteinMPNN at frozen $T^*_{\text{MPNN}}$. ProteinSolver performs scoring only. Sequences scored by both models MUST be identical and in identical candidate identity order (`validate_common_candidate_order`) before percentile ranks are computed.
- **Step-by-Step Pipeline:**
  1. **Candidate Universe Generation:** Generate candidate pool $U_t = \{u_1, \dots, u_K\}$ of size $K$ ($K=100$ tuning, $K=500$ primary test).
  2. **ProteinMPNN Scoring:** Compute sequence-level mean autoregressive log-probability $S_{\text{MPNN}}(u)$ for each $u \in U_t$.
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

## 11. Screening Thresholds
- **Thresholds:**
  $$\text{scRMSD}_{\text{screen}} \le 2.0\text{ \AA} \quad \text{AND} \quad \text{pLDDT}_{\text{screen}} \ge 80.0$$
- Evaluated locally using the screening oracle (ESMFold). Candidates satisfying both criteria enter $S_{\text{viable}}$.

---

## 12. Threshold Provenance
- **Provenance Classification:** **Project-Chosen Operational Screening Thresholds**.
- Informed by established literature standards (Watson et al. 2023 RFdiffusion, Dauparas et al. 2022 ProteinMPNN, Baker Lab de novo design).
- They were NOT calibrated on our project's test data and are NOT universal physical constants.

---

## 13. Primary Final Structural Validation Oracle
- **Exact Oracle Implementation:** **AlphaFold2 (v2.3.2)** / ColabFold single-sequence inference pipeline.
- **Model Checkpoint:** Monomodel weights `model_1_ptm` (384-dim evoformer, fine-tuned with pTM head).
- **Exact Numerical Precision:** `float16` (`fp16`) on GPU (CUDA). (FP16/BF16 alternatives removed; float16 is strictly frozen).
- **Recycle Count:** Exactly 3 recycles (`num_recycle = 3`).
- **Template Policy:** Homologous structural templates disabled (`use_templates = False`).
- **MSA Policy:** Single sequence mode (`msa_mode = "single_sequence"`, no MSA search; sequence query replicated as single-sequence MSA).
- **Amber Relaxation:** Disabled (`use_amber = False`).
- **Determinism & Random Seed:** Deterministic execution with fixed integer seed 42 (`random_seed = 42`).
- **Hardware Platform:** NVIDIA RTX 3050 6GB Laptop GPU (CUDA).
- **Output Extraction:** Unrelaxed C$\alpha$ 3D coordinates and per-residue pLDDT array extracted directly from the unrelaxed PDB output.
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
  - Tuned exclusively on the development set separately for MPNN-only ($\gamma^*_{\text{MPNN}}$) and primary hybrid ($\gamma^*_{\text{hybrid}}$).
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
1. **Development / Tuning Set ($N = 20$):** CATH 4.2 validation split. Used for tuning $\lambda, T, \gamma$.
2. **Primary Test Set ($N = 50$):** TS50 non-redundant PDB crystal structures ($<30\%$ sequence identity to CATH 4.2 / ProteinMPNN training sets; ProteinSolver Gene3D 72M training membership documented per model according to Section 19: superfamily absence verified where accessible, otherwise NOT VERIFIABLE FROM ACCESSIBLE METADATA). Evaluated once with frozen parameters.
3. **De Novo Test Set ($N = 15$):** RFdiffusion generated scaffolds. Evaluated once as a separate stratified benchmark.

---

## 19. Model-Specific Training Membership Language
- **ProteinSolver:** Training membership in the 72M Gene3D corpus is classified as:
  - *"Not present in accessible training superfamily list"* (if superfamily code is absent from the 1,029 training superfamilies).
  - *"NOT VERIFIABLE FROM ACCESSIBLE METADATA"* (if raw domain membership cannot be resolved without downloading the external 72M dataset).
- **ProteinMPNN:** Documented based on CATH 4.2 training vs. test topology splits.
- **Rule:** Targets must NEVER be described as "guaranteed held-out" or "unseen".

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
  - Mean Self-Consistency RMSD (scRMSD)
  - Net Charge at pH 7.4 ($Q_{\text{pH7.4}}$)
  - Hydrophobic core fraction ($f_{\text{core}}$, $\text{RSA} < 0.20$ on predicted structure)
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
