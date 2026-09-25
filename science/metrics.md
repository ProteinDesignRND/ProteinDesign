# Evaluation Metrics & Scientific Justification

This document establishes the mathematical definitions, operational implementations, failure modes, and scientific justifications for all metrics used in the Protein Design project.

---

## 1. Primary Metrics Matrix

| Metric Name | Mathematical Definition | Property Measured | Gaming / Failure Mode | Threshold Classification |
|---|---|---|---|:---:|
| **Native Sequence Recovery (AAR)** | $\text{AAR} = \frac{1}{L} \sum_{i=1}^L \mathbb{I}(s_i = s_i^{\text{native}})$ (Macro-averaged per target) | Agreement with natural evolutionary sequence | Penalizes valid alternative sequences (neutral drift); favors memorization over de novo foldability. | Reference agreement proxy (No universal threshold; single-target result $\ne$ benchmark) |
| **Primary Hybrid Score ($H$)** | $H(u) = \lambda p_{\text{MPNN}}(u) + (1-\lambda) p_{\text{PS}}(u)$ via scale-free within-pool percentile rank | Balanced score integrating modern autoregressive and constraint-satisfaction signals | Sensitive to pool candidate composition; requires pre-frozen $\lambda$ tuned on dev set. | **Primary Generation Scoring Method** |
| **Fixed-Correspondence TM-Score (scTM)** | $\text{scTM} = \frac{1}{L_{\text{target}}} \sum_{i=1}^{L_{\text{target}}} \frac{1}{1 + (d_i / d_0)^2}$ under Kabsch C$\alpha$ superposition | Global fold topology similarity on matched residue mapping (length-scaled, scale-invariant) | Insensitive to local steric clashes or side-chain packing errors. | **PRIMARY STUDY ENDPOINT** (Target-level mean on selected library evaluated by primary validation oracle AlphaFold2) |
| **Self-Consistency RMSD (scRMSD)** | $\text{scRMSD} = \sqrt{\frac{1}{L} \sum_{i=1}^L \|\hat{\mathbf{x}}_i^{\text{CA}} - \mathbf{x}_i^{\text{CA}}\|^2}$ after optimal Kabsch superposition | Structural fidelity: Does predicted structure match design target backbone? | Hallucination on repeat motifs; sensitive to flexible loop ends. | Literature-supported project screening threshold: $\le 2.0\text{ \AA}$ |
| **Predicted lDDT (pLDDT)** | $\text{Mean per-residue predicted lDDT} \in [0, 100]$ from folding oracle | Folding oracle's confidence in local structural prediction | High confidence on non-protein repeating sequences; confidence is not free energy ($\Delta G$). | Literature-supported project screening threshold: $\ge 80.0$ (Oracle-specific) |
| **Structural Viability Rate (SVR)** | $\text{SVR} = \frac{|\{s \in S_{\text{raw}} : \text{scRMSD}_{\text{screen}}(s) \le 2.0\text{ \AA} \land \text{pLDDT}_{\text{screen}}(s) \ge 80\}|}{|S_{\text{raw}}|}$ | Raw generative structural yield under screening oracle (ESMFold) | Sensitive to choice of screening oracle and stringency of cutoffs. | Secondary generative yield metric (Non-tautological) |
| **Independent Validation Yield (IVY)** | $\text{IVY} = \frac{|\{s \in S_{\text{selected}} : \text{scRMSD}_{\text{val}}(s) \le 2.0\text{ \AA} \land \text{pLDDT}_{\text{val}}(s) \ge 80\}|}{|S_{\text{selected}}|}$ | Post-selection library yield under primary validation oracle (AlphaFold2) | Verifies that selected library is not an artifact of screening oracle bias. | Secondary validation yield metric (Cross-oracle firewall) |
| **Pairwise Sequence Diversity (Div)** | $\text{Div}(S) = \frac{2}{M(M-1)} \sum_{j < k} \left(1 - \frac{\text{ID}(s_j, s_k)}{L}\right)$ | Order-independent mean pairwise normalized Hamming distance | Trivial to maximize via random sequences; must be evaluated on structurally viable subset. | Secondary diversity metric (Reported as mean, std, median) |
| **Pareto Hypervolume (HV)** | Volume of objective space dominated by candidate set relative to fixed external reference point $\mathbf{r} = (0, 0, 0)$ | Multi-objective trade-off between structural fidelity, confidence, and score | Sensitive to objective scaling; non-trivial to normalize without outcome leakage. | **Exploratory Descriptive Analysis** (Demoted; fixed external bounds) |
| **Net Charge at pH 7.4 ($Q_{\text{pH7.4}}$)** | Net charge titration via Henderson-Hasselbalch equation at pH 7.4 | Theoretical net electrostatic charge at physiological pH | Sequence heuristic ignoring 3D tertiary electrostatic microenvironments. | Secondary biophysical heuristic (Explicitly NOT pI) |
| **Isoelectric Point (pI)** | Theoretical pH where net charge $Q(\text{pH}) = 0.0$ | Theoretical solubility and precipitation tendency | Sequence heuristic; does not reflect local pKa shifts in folded state. | Secondary biophysical heuristic |
| **Hydrophobic Core Fraction ($f_{\text{core}}$)** | Fraction of $\{\text{V, L, I, F, M, W}\}$ buried in predicted core ($\text{RSA} < 0.20$) | Core packing integrity vs. surface aggregation risk | Heuristics do not model sidechain rotamer packing strain. | Secondary structural proxy (Evaluated on predicted structure) |
| **Inference Compute Latency** | Wall-clock seconds per candidate sequence | Practical computational efficiency and scalability | Hardware-dependent; depends heavily on batching regime and iterative vs. single-pass decoding. | Operational metric (Must report hardware, precision, batch size) |

---

## 2. Rigorous Mathematical & Operational Definitions

### A. Native Sequence Recovery (Amino Acid Recovery, AAR)
- **Mathematical Definition:**
  For a designed sequence $s = (s_1, \dots, s_L)$ and wild-type target reference sequence $s^{\text{native}} = (s_1^{\text{native}}, \dots, s_L^{\text{native}})$ of length $L$:
  $$\text{AAR}(s, s^{\text{native}}) = \frac{1}{|I_{\text{eval}}|} \sum_{i \in I_{\text{eval}}} \mathbb{I}(s_i = s_i^{\text{native}})$$
  where $I_{\text{eval}}$ is the set of evaluated residue indices with experimentally resolved coordinates in the reference PDB structure. Missing residues in the experimental structure are strictly excluded from $I_{\text{eval}}$ across all candidates identically.
- **Candidate Pool Aggregation:**
  For a candidate pool $S = \{s^{(1)}, \dots, s^{(K)}\}$ generated for target $t$:
  $$\overline{\text{AAR}}_t = \frac{1}{K} \sum_{k=1}^K \text{AAR}(s^{(k)}, s^{\text{native}})$$
- **Benchmark Aggregation Convention (Standardized):**
  Across a benchmark set of $N$ targets, the primary reporting convention is the **Macro-Average AAR**:
  $$\text{AAR}_{\text{macro}} = \frac{1}{N} \sum_{t=1}^N \overline{\text{AAR}}_t$$
  Pooled length-weighted AAR is reported only as an auxiliary secondary statistic to prevent long proteins from dominating benchmark conclusions.
- **Scientific Caveat:**
  AAR measures similarity to one historical evolutionary sequence. In natural biology, multiple distinct sequence families fold into the same topology. AAR rewards sequence memorization and can penalize valid, novel de novo sequences that fold into the target geometry. Comparative AAR must be measured experimentally on identical evaluation targets; no cross-model outcome is assumed in advance.

---

### B. Sequence Likelihoods & Primary Hybrid Scoring

#### 1. Decoupled Model Perplexities (Model-Specific Diagnostics)
The conditional probability mechanisms of the baseline models differ fundamentally:
- **ProteinMPNN:** Evaluates exact normalized autoregressive conditional probabilities along a designated residue decoding permutation order $\pi$:
  $$\text{PPL}_{\text{MPNN}}(s \mid \mathbf{X}, \pi) = \exp\left( -\frac{1}{L} \sum_{i=1}^L \log p_{\text{MPNN}}(s_{\pi_i} \mid \mathbf{X}, s_{\pi_{<i}}) \right)$$
- **ProteinSolver:** Evaluates single-site masked marginal conditional probabilities via pseudo-log-likelihood (PLL) scan:
  $$\text{PPL}_{\text{PS}}(s \mid \mathcal{G}) = \exp\left( -\frac{1}{L} \sum_{i=1}^L \log p_{\text{PS}}(s_i \mid \mathcal{G}, s_{\setminus i}) \right)$$
- **Operational Separation Rule:**
  ProteinSolver pseudo-perplexity and ProteinMPNN autoregressive perplexity are **NOT directly comparable numerical quantities**. They serve strictly as **model-specific internal diagnostics**.

#### 2. Primary Hybrid Method: Scale-Free Within-Pool Percentile Rank Normalization
To combine scores from fundamentally different objectives without scale mismatch, the primary hybrid method uses within-pool percentile ranking:
1. For each candidate sequence $u$ in target pool $S$ of size $K$:
   - Compute sequence-level MPNN score: $S_{\text{MPNN}}(u) = \frac{1}{L} \sum_{i=1}^L \log p_{\text{MPNN}}(u_{\pi_i} \mid \mathbf{X}, u_{\pi_{<i}})$ (mean autoregressive log-probability, higher is better).
   - Compute sequence-level ProteinSolver score: $S_{\text{PS}}(u) = \frac{1}{L} \sum_{i=1}^L \log p_{\text{PS}}(u_i \mid \mathcal{G}, u_{\setminus i})$ (mean single-site masked pseudo-log-likelihood, higher is better; explicitly NOT called autoregressive log-likelihood).
2. Compute scale-free within-pool percentile ranks:
   $$p_{\text{MPNN}}(u) = \frac{\text{rank}(S_{\text{MPNN}}(u))}{K} \in (0, 1]$$
   $$p_{\text{PS}}(u) = \frac{\text{rank}(S_{\text{PS}}(u))}{K} \in (0, 1]$$
   Ties are broken deterministically using standard average ranking. Higher percentile always indicates better sequence confidence.
3. Compute the primary hybrid score:
   $$H(u) = \lambda \cdot p_{\text{MPNN}}(u) + (1 - \lambda) \cdot p_{\text{PS}}(u), \quad \lambda \in [0.0, 1.0]$$
4. **Hyperparameter Freezing Rule:**
   The mixing parameter $\lambda$ is tuned **strictly on the development/tuning set** (CATH 4.2 validation split, 20 backbones) across a pre-registered grid $\lambda \in \{0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0\}$, and **frozen prior to unblinding the primary test set**.

#### 3. Exploratory Logit Hybrid (Ablation Only)
Raw logit interpolation:
$$z_{\text{hybrid}}(a_i) = \lambda \cdot z_{\text{MPNN}}(a_i) + (1 - \lambda) \cdot z_{\text{PS}}(a_i)$$
is retained **strictly as an exploratory ablation** and is explicitly NOT the primary hybrid method.

---

### C. Self-Consistency RMSD (scRMSD)
- **Mathematical Definition:**
  $$\text{scRMSD} = \sqrt{\frac{1}{L} \sum_{i=1}^L \|\mathbf{R} \mathbf{x}_{\text{pred}, i}^{\text{CA}} + \mathbf{t} - \mathbf{x}_{\text{target}, i}^{\text{CA}}\|^2}$$
- **Operational Ingredients:**
  - Evaluated strictly over backbone $\text{C}\alpha$ atoms on matched sequence-to-structure residue correspondence ($N = L$).
  - Missing electron density positions in target PDB must be excluded identically across all candidates, ensuring unresolved residues cannot silently shrink the evaluation set.
  - Optimal rotation matrix $\mathbf{R} \in \text{SO}(3)$ and translation vector $\mathbf{t} \in \mathbb{R}^3$ are computed via the Kabsch algorithm.
  - Direction: Lower is better ($0.0\text{ \AA}$ indicates identical $\text{C}\alpha$ trace).
  - Threshold Context: $\text{scRMSD} \le 2.0\text{ \AA}$ is adopted as a **project screening threshold** based on standard literature practices (e.g. Baker Lab de novo design pipelines). It is not an absolute physical constant.

---

### D. Fixed-Correspondence Self-Consistency TM-Score (scTM) — PRIMARY STUDY ENDPOINT
- **Mathematical Definition (Zhang & Skolnick 2004):**
  $$\text{scTM} = \frac{1}{L_{\text{target}}} \sum_{i=1}^{L_{\text{target}}} \frac{1}{1 + \left(\frac{d_i(\mathbf{R}^*, \mathbf{t}^*)}{d_0(L_{\text{target}})}\right)^2}$$
- **Operational Ingredients:**
  - Evaluated under fixed sequence-to-structure residue correspondence (residue index $i$ in prediction mapped to residue index $i$ in target).
  - Superposition $(\mathbf{R}^*, \mathbf{t}^*)$ computed via Kabsch / TM-score maximizing rotation and translation.
  - Normalized strictly by $L_{\text{target}}$ to ensure length-scale invariance.
  - $d_0(L_{\text{target}}) = 1.24 \sqrt[3]{L_{\text{target}} - 15} - 1.8$ for $L_{\text{target}} > 15$ residues (minimum cutoff $0.5\text{ \AA}$).
  - Direction: Higher is better ($\in (0, 1]$). $\text{scTM} > 0.5$ indicates identical global fold topology.
- **PRIMARY ENDPOINT STATUS:**
  The primary statistical endpoint of the entire research project is:
  $$\overline{\text{scTM}}_{\text{val}}(t) = \frac{1}{M} \sum_{m=1}^M \text{scTM}_{\text{val}}(s^{(m)}_t)$$
  evaluated across the final selected candidate library ($M = 10$) by the **Primary Final Structural Validation Oracle (AlphaFold2)**.
  The primary comparison is the target-level paired difference:
  $$\Delta \overline{\text{scTM}}(t) = \overline{\text{scTM}}_{\text{hybrid}}(t) - \overline{\text{scTM}}_{\text{MPNN-only}}(t)$$
  evaluated target-by-target across the primary test set ($N = 50$ TS50 targets).

---

### E. Predicted Local Distance Difference Test (pLDDT)
- **Definition:** Mean per-residue predicted lDDT confidence metric emitted by the structural folding oracle:
  $$\overline{\text{pLDDT}} = \frac{1}{L} \sum_{i=1}^L \text{pLDDT}_i \in [0, 100]$$
- **Scientific Caveat:**
  pLDDT is an oracle-specific local confidence score. It is NOT free energy of folding ($\Delta G$), NOT thermodynamic stability, and NOT wet-lab verification. Threshold $\ge 80.0$ is an **empirically supported screening cutoff**, not a universal physical law. Values from ESMFold, AlphaFold2, and Boltz-1 are oracle-specific and are never pooled or compared on an identical numerical axis.

---

### F. Candidate Viability vs. Independent Validation Yield
To eliminate circular evaluation where candidate selection and evaluation share the same oracle:
1. **Generative Structural Viability Rate (SVR):**
   $$\text{SVR} = \frac{|\{s \in S_{\text{raw}} : \text{scRMSD}_{\text{screen}}(s) \le 2.0\text{ \AA} \land \text{pLDDT}_{\text{screen}}(s) \ge 80\}|}{|S_{\text{raw}}|}$$
   Measures the raw generative yield of the model under the initial screening oracle (ESMFold).
2. **Independent Validation Yield (IVY):**
   $$\text{IVY} = \frac{|\{s \in S_{\text{selected}} : \text{scRMSD}_{\text{val}}(s) \le 2.0\text{ \AA} \land \text{pLDDT}_{\text{val}}(s) \ge 80\}|}{|S_{\text{selected}}|}$$
   Evaluates the final candidate library ($M=10$) using the **Primary Final Validation Oracle (AlphaFold2)**, which was NOT used during initial generation or screening.

---

### G. Order-Independent Pairwise Sequence Diversity
- **Mathematical Definition:**
  For any candidate sequence set $S = \{s^{(1)}, \dots, s^{(M)}\}$ of size $M \ge 2$, where each sequence has length $L$:
  $$\text{Div}(S) = \frac{2}{M(M - 1)} \sum_{1 \le j < k \le M} d(s^{(j)}, s^{(k)})$$
  where $d(u, v) = \frac{1}{L} \sum_{i=1}^L \mathbb{I}(u_i \ne v_i)$ is normalized Hamming distance.
- **Edge Cases & Duplicate Handling:**
  - If $M < 2$, $\text{Div}(S) = 0.0$ by definition.
  - Duplicates have distance $0.0$ and decrease mean diversity naturally.
  - Distribution reporting: Mean, standard deviation, and median of the pairwise distance distribution are reported.
- **Stage-Specific Diversity Reporting:**
  Diversity is evaluated and reported at three distinct stages:
  1. **Raw Generation Diversity ($\text{Div}_{\text{raw}}$):** Computed over all $K$ generated samples in $S_{\text{raw}}$.
  2. **Viable Candidate Diversity ($\text{Div}_{\text{viable}}$):** Computed over the subset $S_{\text{viable}}$ passing structural screening criteria ($\text{scRMSD}_{\text{screen}} \le 2.0\text{ \AA}, \text{pLDDT}_{\text{screen}} \ge 80$).
  3. **Selected Library Diversity ($\text{Div}_{\text{selected}}$):** Computed over the final top-$M$ candidate library $S_{\text{selected}}$.

---

### H. Candidate Selection & Pareto Hypervolume (HV)

#### 1. Two-Stage Candidate Selection Protocol
- **Stage 1 (Hard Viability Gate):**
  Filter all $K$ candidates through the screening oracle (ESMFold). Discard candidates failing $\text{scRMSD}_{\text{screen}} \le 2.0\text{ \AA}$ or $\text{pLDDT}_{\text{screen}} \ge 80.0$, yielding $S_{\text{viable}}$.
- **Stage 2 (Greedy Diversity-Aware Selection Heuristic):**
  Select $M = 10$ candidates from $S_{\text{viable}}$ using greedy facility dispersion:
  $$u^* = \arg\max_{u \in S_{\text{viable}} \setminus S'} \left[ \text{score}(u) + \gamma \cdot \min_{v \in S'} d(u, v) \right]$$
  *Methodological Rule:* This greedy score is a **construction heuristic** and must NEVER be reported as an intrinsic static candidate quality metric.

#### 2. Pareto Hypervolume (Exploratory Descriptive Analysis)
Hypervolume is demoted to an **exploratory descriptive metric** to avoid normalization leakage.
When evaluated, it uses pre-declared external normalization bounds:
- $f_1(u) = \text{scTM}(u) \in [0, 1]$
- $f_2(u) = 1.0 - \min(1.0, \text{scRMSD}(u) / 10.0) \in [0, 1]$
- $f_3(u) = \text{pLDDT}(u) / 100.0 \in [0, 1]$
- Anti-ideal reference point: fixed externally a priori at $\mathbf{r} = (0.0, 0.0, 0.0)$. Normalization bounds are NEVER derived from test-set candidate min/max values.

---

### I. Biophysical Proxies
- **Net Charge at pH 7.4 ($Q_{\text{pH7.4}}$):**
  Calculated using the Henderson-Hasselbalch equation with standard EMBOSS pKa values at neutral pH 7.4.
  *Terminology Rule:* This is strictly labeled **Net Charge at pH 7.4** ($Q_{\text{pH7.4}}$), explicitly NOT "pI".
- **Isoelectric Point (pI):**
  The theoretical pH at which the net charge equals zero: $Q(\text{pI}) = 0.0$.
  *Limitation:* Sequence-based heuristic ignoring 3D electrostatic environments and tertiary salt bridges.
- **Hydrophobic Core Fraction ($f_{\text{core}}$):**
  Fraction of project-defined hydrophobic residues $\mathcal{H} = \{\text{Val, Leu, Ile, Phe, Met, Trp}\}$ occupying core positions (relative solvent accessibility $\text{RSA} < 0.20$).
  *Structural Reference Rule:* Evaluated on the **predicted 3D structure from the folding oracle** (since de novo candidates lack an experimental structure). Denominator is total sequence length $L$.

---

### J. Inference Latency & Computational Scaling
Computational speed must be reported with:
1. Exact hardware specifications (e.g. NVIDIA RTX 3050 6GB Laptop GPU vs. CPU).
2. Execution precision (FP32 on CPU, FP16/BF16 on GPU).
3. Batch size: Batch size 1 for iterative ProteinSolver; batch sizes 1 and 32 for ProteinMPNN.
4. Timing boundaries: Timing strictly measures inference forward passes (`torch.cuda.synchronize()` before and after); model loading and data extraction are measured and reported separately as initialization overhead.
5. Warmup & Repeatability: 5 warmup sequences followed by reporting median and interquartile range across 3 independent timing runs per target.
6. Scaling Note: ProteinSolver's iterative constraint satisfaction design loop executes $L$ sequential unmasking passes ($O(L \times \text{GNN inference})$), whereas ProteinMPNN evaluates autoregressive decoding in $O(L)$ message-passing steps with optimized GPU vectorization.

---

## 3. Structural Oracle Separation & Anti-Leakage Protocol

To ensure evaluation rigor and prevent circular selection biases:
1. **Screening vs. Validation Firewall:**
   - **Screening Oracle:** ESMFold (fast, local single-pass inference) is used to compute initial structural metrics for generation pools and candidate selection ($K = 100–500$ sequences/target).
   - **Primary Final Structural Validation Oracle:** **AlphaFold2 (v2.3.2, monomodel weights `model_1_ptm`, 3 recycles, no templates, single sequence mode, fp16/bf16 on GPU)** is the frozen primary validation oracle for the final selected library ($M = 10$ candidates/target).
   - **Sensitivity Validation Oracle:** **Boltz-1 (v0.4.1, default diffusion steps, no templates, single sequence mode)** is designated strictly for sensitivity analysis.
2. **Anti-Leakage Prohibition:**
   A metric or oracle score used as an objective criterion during candidate selection (ESMFold) must NEVER be cited as independent evidence of success without confirmation by the primary independent validation oracle (AlphaFold2).
3. **Hyperparameter Isolation:**
   All selection thresholds, mixing weight $\lambda$, diversity weight $\gamma$, and sampling temperatures must be determined strictly on the validation set (CATH 4.2 validation split, 20 backbones), NEVER on final benchmark test targets.

