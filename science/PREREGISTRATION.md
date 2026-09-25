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
- **Missing Data Handling:** If structural folding fails on a target under the validation oracle, the target is recorded as a failure and assigned $\text{scTM} = 0.0$.
- **Stratification:** Primary hypothesis testing is evaluated on natural targets ($N = 50$, TS50). The de novo test set ($N = 15$, RFdiffusion) is evaluated and reported as a separate stratified analysis.

---

## 6. Candidate Budgets
- **$K$ (Generation Budget):** Defined strictly as total candidates generated **PER TARGET PER METHOD PER CONDITION**.
  - Development / Tuning Set: $K = 100$ sequences per target per method.
  - Primary Test Set: $K = 500$ sequences per target per method.
- **Matched Budget Rule:** All comparisons between standalone ProteinMPNN and hybrid methods MUST evaluate identical total generation budgets $K$.
- **Selection Library Size ($M$):** Exactly $M = 10$ candidates selected per target.
- **Validation Pool:** Exactly the $M = 10$ selected candidates are evaluated by the primary final validation oracle.

---

## 7. Sampling Temperatures & Random Seeds
- **ProteinMPNN Sampling:** Autoregressive sampling across pre-registered temperature grid $T \in \{0.1, 0.2, 0.5, 0.8, 1.0\}$ with random residue permutation decoding orders.
- **ProteinSolver Sampling (E0-B):** Stochastic CSP sampling across temperature grid $T \in \{0.1, 0.5, 1.0\}$.
- **Random Seeds:** 3 fixed integer random seeds (`seed=42`, `seed=1337`, `seed=2026`) pre-registered for candidate generation.

---

## 8. Hyperparameter ($\lambda$) Tuning Procedure
- **Tuning Set:** Hyperparameter search for the hybrid mixing coefficient $\lambda$ is conducted **exclusively on the Development / Tuning Set** (CATH 4.2 validation split, 20 backbones).
- **Search Grid:** $\lambda \in \{0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0\}$.
- **Objective:** Maximize mean validation-set $\overline{\text{scTM}}$.
- **Freezing Rule:** Once the optimal $\lambda^*$ is selected on the tuning set, it is **strictly frozen** before running inference or evaluation on the primary test set. Zero tuning against test outcomes is permitted.

---

## 9. Primary Hybrid Method Definition
- **Method:** Scale-free within-pool percentile rank normalization:
  1. For each candidate $u$ in target pool $S$ of size $K$:
     $$p_{\text{MPNN}}(u) = \frac{\text{rank}(S_{\text{MPNN}}(u))}{K} \in (0, 1]$$
     $$p_{\text{PS}}(u) = \frac{\text{rank}(S_{\text{PS}}(u))}{K} \in (0, 1]$$
  2. $S_{\text{MPNN}}(u)$ is sequence-level mean autoregressive log-probability.
  3. $S_{\text{PS}}(u)$ is sequence-level mean single-site masked pseudo-log-likelihood (PLL scan; NOT autoregressive log-likelihood).
  4. Ties are broken deterministically using standard average ranking (`scipy.stats.rankdata(..., method='average')`).
  5. Higher percentile always indicates higher confidence.
  6. Hybrid score: $H(u) = \lambda^* \cdot p_{\text{MPNN}}(u) + (1 - \lambda^*) \cdot p_{\text{PS}}(u)$.

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
- **Oracle:** **AlphaFold2 (v2.3.2)**
- **Model Checkpoint:** Monomodel weights `model_1_ptm`
- **Configuration:** Single sequence mode (no MSA search, no templates), 3 recycles, Amber relaxation disabled, precision FP16/BF16 on GPU.
- **Firewall Rule:** AlphaFold2 is strictly reserved for validating the final selected candidate library ($M=10$). It is NEVER used during initial candidate generation, screening, or selection.

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
2. **Primary Test Set ($N = 50$):** TS50 non-redundant PDB crystal structures ($<30\%$ sequence identity to training sets). Evaluated once with frozen parameters.
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
5. More than 10% of test targets fail structural folding due to hardware or runtime crashes.
