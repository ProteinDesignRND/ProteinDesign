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
- **Test:** Two-sided paired Wilcoxon signed-rank test on $\{d_t\}_{t=1}^N$.
- **Significance Level:** $\alpha = 0.01$ (two-tailed, pre-registered).
- **Effect Size:** Hodges-Lehmann median paired difference estimator and paired Cohen's $d_z$.
- **Confidence Intervals:** 95% and 99% bootstrap confidence intervals (10,000 resamples).
- **Folding Failure Handling (Scientific vs. Infrastructure Distinction):**
  - **Scientific / Model Folding Failure:** Oracle finishes execution without system error, but outputs unphysical coordinates (e.g. steric clash collapse, NaN/inf coordinates, disjoint C$\alpha$ trace) or confidence below structural definition ($\text{pLDDT} < 10.0$). This reflects a biological/generative failure to design a foldable sequence; it is a valid scientific observation, assigned $\text{scTM} = 0.0$, and included in target-level differences $\{d_t\}$.
  - **Infrastructure / Runtime Failure:** Oracle fails due to system or hardware exceptions independent of sequence biology (GPU Out-Of-Memory [OOM], process timeout exceeding 600s/target, driver/CUDA crash, unhandled environment error, corrupted/missing output file).
    - Infrastructure failures are **NEVER assigned $\text{scTM} = 0.0$** (doing so conflates system bugs with biological design quality).
    - Failed jobs are retried once under clean execution parameters.
    - If unresolvable on target $t$, target $t$ is marked as `INFRASTRUCTURE_FAILURE_UNVALIDATED` and excluded from the primary paired comparison $\{d_t\}$.
    - The target-level infrastructure failure rate $F_{\text{infra}} = N_{\text{infra}} / N_{\text{total}}$ is strictly tracked.
    - If $F_{\text{infra}} > 10\%$ (e.g. $> 5$ of 50 TS50 targets), the entire benchmark run is automatically declared **INVALID / INCONCLUSIVE** (Criterion 5 of Section 24), halting evaluation until the runtime/hardware defect is remediated.
    - If $F_{\text{infra}} \le 10\%$, primary evaluation proceeds on the remaining valid targets, and complete-case analysis is reported alongside worst-case sensitivity bounds.
- **Stratification:** Primary hypothesis testing is evaluated on natural targets ($N = 50$, TS50). The de novo test set ($N = 15$, RFdiffusion) is evaluated and reported as a separate stratified analysis.

---

## 6. Candidate Budgets (Unambiguous Accounting)
- **$K$ (Generation Budget — Definitive Interpretation):**
  - $K$ is defined strictly as the **TOTAL candidate sequences generated PER TARGET PER METHOD/ARM across all temperatures and random seeds (Interpretation A)**.
  - It is **NEVER interpreted as per-condition or per-temperature $\times$ seed**.
  - **Budget Allocation:**
    - Development / Tuning Set: $K = 100$ total candidates per target.
    - Primary Test Set: $K = 500$ total candidates per target.
  - **Explicit Breakdown of Generated Sequences per Target for TS50 ($K = 500$):**
    - **Standalone ProteinMPNN:** Exactly 500 total generated sequences per target. Generated at the pre-frozen optimal sampling temperature $T^*_{\text{MPNN}}$ (selected from $\{0.1, 0.2, 0.5, 0.8, 1.0\}$ on the tuning set), distributed across the 3 pre-registered seeds: Seed 42 ($N = 167$), Seed 1337 ($N = 167$), Seed 2026 ($N = 166$). Resulting total sequences = 500.
    - **Stochastic ProteinSolver (E0-B Baseline):** Exactly 500 total generated sequences per target. Generated via stochastic CSP sampling at the pre-frozen optimal sampling temperature $T^*_{\text{PS}}$ (selected from $\{0.1, 0.5, 1.0\}$ on the tuning set), distributed across the 3 pre-registered seeds: Seed 42 ($N = 167$), Seed 1337 ($N = 167$), Seed 2026 ($N = 166$). Resulting total sequences = 500.
    - **Primary Hybrid Method:** Evaluates the Common Candidate Universe of size $K = 500$ generated per target (the sequences generated by ProteinMPNN at $T^*_{\text{MPNN}}$ with the 167/167/166 seed allocation). Both ProteinMPNN and ProteinSolver score all 500 sequences in this common pool. Resulting total newly generated sequences = 0 (or 500 if evaluated on an independent matched pool).
    - **Historical Deterministic ProteinSolver (E0-A Control):** Exactly 1 sequence (1n5uA03 only, MAP decoding, 41.30% recovery; single target integration control, NOT part of TS50 benchmark).
- **Matched Budget Rule:** Standalone ProteinMPNN and Primary Hybrid methods evaluate exactly matched candidate pools of size $K = 500$ per target.
- **Selection Library Size ($M$):** Exactly $M = 10$ candidates selected per target from the viable candidate subset $S_{\text{viable}} \subseteq S_{\text{raw}}$.
- **Validation Pool:** Exactly the $M = 10$ selected candidates are evaluated by the primary final validation oracle (AlphaFold2).

---

## 7. Sampling Temperatures & Random Seeds
- **ProteinMPNN Sampling:** Autoregressive sampling across pre-registered temperature grid $T \in \{0.1, 0.2, 0.5, 0.8, 1.0\}$ with random residue permutation decoding orders.
- **ProteinSolver Sampling (E0-B):** Stochastic CSP sampling across temperature grid $T \in \{0.1, 0.5, 1.0\}$.
- **Random Seeds:** 3 fixed integer random seeds (`seed=42`, `seed=1337`, `seed=2026`) pre-registered for candidate generation. Partitioned across the 500-sequence generation budget as: 167 (seed 42), 167 (seed 1337), and 166 (seed 2026).

---

## 8. Hyperparameter ($\lambda$) Tuning Procedure
- **Tuning Set:** Hyperparameter search for the hybrid mixing coefficient $\lambda$ is conducted **exclusively on the Development / Tuning Set** (CATH 4.2 validation split, 20 backbones).
- **Search Grid:** $\lambda \in \{0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0\}$.
- **Objective:** Maximize mean validation-set $\overline{\text{scTM}}$.
- **Freezing Rule:** Once the optimal $\lambda^*$ is selected on the tuning set, it is **strictly frozen** before running inference or evaluation on the primary test set. Zero tuning against test outcomes is permitted.

---

## 9. Primary Hybrid Method & Common Candidate Universe
- **Common Candidate Universe Rule:**
  For each target backbone $t$, ProteinMPNN and ProteinSolver scores are evaluated on the **EXACT SAME candidate sequences** (the Common Candidate Universe $U_t$ of size $K$). Percentiles are NEVER computed over different or independently drawn candidate populations.
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
  6. **Screening & Diversity Selection:** Hard viability gate ($\text{scRMSD}_{\text{screen}} \le 2.0\text{ \AA} \land \text{pLDDT}_{\text{screen}} \ge 80.0$) $\to$ Stage 2 diversity-aware selection heuristic $\to$ final library $S_{\text{selected}}$ ($M = 10$).

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
  Candidates failing $\text{scRMSD}_{\text{screen}} \le 2.0\text{ \AA}$ or $\text{pLDDT}_{\text{screen}} \ge 80.0$ are discarded, forming $S_{\text{viable}}$.
- **Stage 2 (Greedy Diversity-Aware Selection Heuristic):**
  From $S_{\text{viable}}$, greedily select $M = 10$ candidates maximizing:
  $$u^* = \arg\max_{u \in S_{\text{viable}} \setminus S'} \left[ \text{score}(u) + \gamma^* \cdot \min_{v \in S'} d(u, v) \right]$$
  where $d(u, v)$ is normalized Hamming distance, and $\gamma^*$ is tuned on the development set and frozen.
- **Reporting Rule:** The greedy selection objective is a construction heuristic; final diversity is evaluated independently.

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
