# Evaluation Metrics & Scientific Justification

This document establishes the mathematical definitions, operational implementations, failure modes, and scientific justifications for all metrics used in the Protein Design project.

---

## 1. Primary Metrics Matrix

| Metric Name | Mathematical Definition | Property Measured | Gaming / Failure Mode | Threshold Classification |
|---|---|---|---|:---:|
| **Native Sequence Recovery (AAR)** | $\text{AAR} = \frac{1}{L} \sum_{i=1}^L \mathbb{I}(s_i = s_i^{\text{native}})$ (Macro-averaged per target) | Agreement with natural evolutionary sequence | Penalizes valid alternative sequences (neutral drift); favors memorization over de novo foldability. | Reference agreement proxy (No universal threshold; single-target result $\ne$ benchmark) |
| **Primary Hybrid Score ($H$)** | $H(u) = \lambda p_{\text{MPNN}}(u) + (1-\lambda) p_{\text{PS}}(u)$ via scale-free within-pool percentile rank | Balanced score integrating modern autoregressive and constraint-satisfaction signals | Sensitive to pool candidate composition; requires pre-frozen $\lambda$ tuned on dev set. | **Primary Generation Scoring Method** |
| **Fixed-Correspondence TM-Score (scTM)** | $\text{scTM} = \frac{1}{L_{\text{target}}} \sum_{i=1}^{L_{\text{target}}} \frac{1}{1 + (d_i / d_0)^2}$ under Kabsch C$\alpha$ superposition | Continuous length-normalized backbone structural similarity under fixed residue correspondence (Kabsch superposition) | Insensitive to local steric clashes or side-chain packing errors. | **PRIMARY STUDY ENDPOINT** (Target-level mean on selected library evaluated by primary validation oracle AlphaFold2) |
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
4. **Development Hyperparameter Selection & Freezing Protocol ($T^*, \lambda^*, \gamma^*$):**
   The mixing parameter $\lambda$ and diversity weights $\gamma$ are selected **strictly on the development set** (frozen manifest `data/manifests/development_20_cath42.txt`, SHA-256: `47ab5fec66017b455f7eabee143dc83e99ec740640e945ed96752abb59483069`, 20 backbones from the Ingraham/Dauparas CATH 4.2 validation split) by maximizing the scalar development objective:
   $$J = \frac{1}{N_{\text{dev}}} \sum_{t=1}^{N_{\text{dev}}} \overline{\text{scTM}}_{\text{val}}(t) = \frac{1}{N_{\text{dev}}} \sum_{t=1}^{N_{\text{dev}}} \left( \frac{1}{M} \sum_{m=1}^M \text{scTM}_{\text{val}}(s_{t,m}) \right)$$
   using the frozen Primary Final Structural Validation Oracle (AlphaFold2 v2.3.2, monomodel weights `model_1_ptm`, single-sequence mode, 3 recycles, fp16 GPU, fixed inference seed = 42, Amber disabled).
   - **Development Infeasibility Rule ($J = -\infty$):** Any configuration producing `SELECTION_INFEASIBLE_LT_M` ($<10$ unique viable candidates) on ANY single development target receives $J = -\infty$ and is ineligible for argmax. If all configurations in an arm are infeasible, stop that tuning arm and classify the development tuning stage as `DEVELOPMENT_TUNING_STAGE_INFEASIBLE`.
   - **MPNN-only:** Cartesian product $T_{\text{MPNN}} \times \gamma$ (25 combinations) $\to (T^*_{\text{MPNN}}, \gamma^*_{\text{MPNN}}) = \arg\max J$.
   - **ProteinSolver E0-B:** Cartesian product $T_{\text{PS}} \times \gamma$ (15 combinations) $\to (T^*_{\text{PS}}, \gamma^*_{\text{PS}}) = \arg\max J$.
   - **Primary Hybrid:** $T^*_{\text{hybrid}} = T^*_{\text{MPNN}}$ (evaluates common candidate universe $U_t$; zero independent temperature sweep). Cartesian product $\lambda \times \gamma$ (35 combinations) $\to (\lambda^*, \gamma^*_{\text{hybrid}}) = \arg\max J$.
   - **Development Caching:** Candidate pools at temperature $T$ are generated once, screened once with ESMFold, and scored once, then reused across all $\gamma$ values (and across all 35 $(\lambda, \gamma)$ combinations for hybrid on $U_t$).
   - **Freezing Order:** 1. MPNN $\to$ 2. PS $\to$ 3. Hybrid $\to$ 4. Freeze ALL parameters $\to$ 5. TS50 execution permitted.
   - **Deterministic Tie-Breaking:** Ascending lexicographical grid order. All parameters are **strictly frozen prior to TS50 evaluation**. Zero test-set tuning permitted.


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
  - **Benchmark Target Invariant:** For the frozen development (E1) and confirmatory (TS50) benchmarks, all target structures strictly require 100% resolved backbone $C_\alpha$ coordinates ($1..L$) without gaps, ensuring an exact 1-to-1 residue mapping ($N = L$) with zero silent target-specific residue subset alterations.
  - *Generic Helper Boundary:* General-purpose metric utilities supporting missing experimental density masking exist solely for arbitrary exploratory PDB evaluation and are strictly NOT utilized in the frozen benchmark evaluation protocol.
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
  - Direction: Higher is better ($\in (0, 1]$).
  - Methodological Boundary: Fixed-correspondence scTM uses the Zhang–Skolnick TM-score functional form and length normalization, but fixes residue correspondence ($i \mapsto i$) and performs rigid-body Kabsch superposition; it is not standard TM-align/TM-score dynamic-programming alignment optimization. The classical literature threshold of 0.5 for "same fold" or "identical global fold topology" was established for dynamic-programming alignment optimization and MUST NOT be inherited as an interpretive threshold for this fixed-correspondence metric. The project makes zero claims of "identical fold" or "universal threshold" based on fixed-correspondence scTM; it is utilized strictly as a continuous, length-normalized structural similarity endpoint.
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
  Filter all $K$ candidates through the screening oracle (ESMFold). Discard candidates failing $\text{scRMSD}_{\text{screen}} \le 2.0\text{ \AA}$ or $\text{pLDDT}_{\text{screen}} \ge 80.0$, yielding viable pool $S_{\text{viable}}$.
- **Duplicate Accounting & Unique Candidate Filtering:**
  - $K$ counts all generated candidates, including duplicates.
  - Deduplicate to unique viable sequences ($S_{\text{viable, unique}} \subseteq S_{\text{viable}}$), retaining the highest-scoring candidate for identical sequences.
  - Report duplicate rate separately. Duplicates contribute distance $0.0$. Never silently regenerate duplicates.
- **Insufficient Viable Candidates Rule:**
  If $|S_{\text{viable, unique}}| < M=10$, mark arm/target as **`SELECTION_INFEASIBLE_LT_M`**. Do not silently regenerate, pad, or alter thresholds. Primary endpoint is undefined for complete-case analysis; reported under conservative zero-quality sensitivity.
- **Stage 2 (Greedy Diversity-Aware Selection Heuristic):**
  From $S_{\text{viable, unique}}$, greedily select $M = 10$ candidates:
  - First selection ($S' = \emptyset$):
    $$u_1 = \arg\max_{u \in S_{\text{viable, unique}}} \text{score}(u)$$
  - Subsequent selections ($1 \le |S'| < M$):
    $$u^* = \arg\max_{u \in S_{\text{viable, unique}} \setminus S'} \left[ \text{score}(u) + \gamma^* \cdot \min_{v \in S'} d(u, v) \right]$$
  where $d(u, v)$ is normalized Hamming distance in $[0, 1]$.
- **Normalization Consistency of Selection Scores:**
  Both primary arms use scores normalized to the matched $[0, 1]$ rank scale inside the greedy selector:
  - Primary Hybrid: $\text{score}_{\text{hybrid}}(u) = H(u) \in (0, 1]$
  - Primary MPNN-Only: $\text{score}_{\text{MPNN-only}}(u) = p_{\text{MPNN}}(u) \in (0, 1]$
  Underlying raw log-likelihood and perplexity remain diagnostic metrics.
- **Diversity Weight ($\gamma$) Search Grid:**
  Pre-registered dimensionless grid $\gamma \in \{0.0, 0.25, 0.5, 1.0, 2.0\}$, tuned strictly on the development set separately for MPNN-only ($\gamma^*_{\text{MPNN}}$) and hybrid selection ($\gamma^*_{\text{hybrid}}$) via Cartesian grid optimization of objective $J$, and frozen prior to TS50 evaluation.
- **Deterministic Tie Breaking:**
  All ties in primary score or greedy objective are broken deterministically by stable candidate identifier order (ascending lexicographical ID).
- *Methodological Rule:* This greedy score is a **construction heuristic** and must NEVER be reported as an intrinsic static candidate quality metric. Final library diversity is evaluated independently after selection.

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
  Calculated using the Henderson-Hasselbalch equation with standard EMBOSS pKa values (N-term: 8.6, C-term: 3.6, Lys: 10.8, Arg: 12.5, His: 6.5, Asp: 3.9, Glu: 4.1, Cys: 8.5, Tyr: 10.1) at neutral pH 7.4.
  *Terminology Rule:* This is strictly labeled **Net Charge at pH 7.4** ($Q_{\text{pH7.4}}$), explicitly NOT "pI".
- **Isoelectric Point (pI):**
  The theoretical pH at which the net charge equals zero: $Q(\text{pI}) = 0.0$, computed using the EMBOSS pKa scale via binary bisection on pH in $[0.0, 14.0]$ to within $\pm 0.01$ pH units.
  *Limitation:* Sequence-based heuristic ignoring 3D electrostatic microenvironments and tertiary salt bridges.
- **Hydrophobic Core Fraction ($f_{\text{core}}$):**
  Fraction of project-defined hydrophobic residues $\mathcal{H} = \{\text{Val, Leu, Ile, Phe, Met, Trp}\}$ buried in the structural core:
  $$f_{\text{core}} = \frac{|\{i \in \{1, \dots, L\} : s_i \in \mathcal{H} \land \text{RSA}_i < 0.20\}|}{|\{i \in \{1, \dots, L\} : s_i \in \mathcal{H}\}|}$$
  - **Numerator:** Count of project-defined hydrophobic residues ($\text{V, L, I, F, M, W}$) with Relative Solvent Accessibility $\text{RSA} < 0.20$.
  - **Denominator:** Total count of project-defined hydrophobic residues in the sequence ($N_{\text{hydrophobic}} = \sum_{i=1}^L \mathbb{I}(s_i \in \mathcal{H})$).
  - **Terminology Guard:** This metric is strictly designated the **Hydrophobic Core Fraction** ($f_{\text{core}}$), explicitly NOT "hydrophobic-core density" (which would divide by sequence length $L$).
  - **Zero-Hydrophobic Edge Case:** If a sequence contains zero hydrophobic residues ($N_{\text{hydrophobic}} = 0$), $f_{\text{core}}$ is defined as $0.0$, and the instance is flagged with `denominator_zero = True` in descriptive reporting rather than silently dividing by zero.
  - **RSA Calculation:** Computed from the 3D atomic coordinates using the Shrake-Rupley numerical surface area algorithm (probe radius $1.4\text{ \AA}$, 960 points/sphere; Biopython `Bio.PDB.ShrakeRupley`), normalized by Tien et al. (2013) empirical maximum accessible surface areas.
  - **Oracle Attribution for Structural Source:**
    - Screening-stage candidates: Evaluated on the **ESMFold** predicted 3D structure.
    - Final selected library ($M = 10$): Evaluated on the **AlphaFold2** predicted 3D structure.
    - Sensitivity analyses: Evaluated on the **Boltz-1** predicted 3D structure.
    - For every secondary metric report, log exact oracle metadata: oracle name, model checkpoint, package version, precision, and inference settings.
  - **Secondary Metric Status:** Strictly secondary and descriptive. $f_{\text{core}}$, $Q_{\text{pH7.4}}$, and $\text{pI}$ MUST NEVER become candidate selection criteria or optimization tuning objectives.

---

### J. Inference Latency & Computational Scaling
Computational speed must be reported with:
1. Exact hardware specifications (e.g. NVIDIA RTX 3050 6GB Laptop GPU vs. CPU).
2. Execution precision (FP32 on CPU, float16 / fp16 on GPU).
3. Batch size: Batch size 1 for iterative ProteinSolver; batch sizes 1 and 32 for ProteinMPNN.
4. Timing boundaries: Timing strictly measures inference forward passes (`torch.cuda.synchronize()` before and after); model loading and data extraction are measured and reported separately as initialization overhead.
5. Warmup & Repeatability: 5 warmup sequences followed by reporting median and interquartile range across 3 independent timing runs per target.
6. Scaling Note: ProteinSolver's iterative constraint satisfaction design loop executes $L$ sequential unmasking passes ($O(L \times \text{GNN inference})$), whereas ProteinMPNN evaluates autoregressive decoding in $O(L)$ message-passing steps with optimized GPU vectorization.

---

## 3. Structural Oracle Separation & Anti-Leakage Protocol

To ensure evaluation rigor and prevent circular selection biases:
1. **Screening vs. Validation Firewall:**
   - **Screening Oracle:** ESMFold (Meta AI `esm` v2.0.0 / Hugging Face `facebook/esmfold_v1`, `esmfold_v1` 3B checkpoint, sequence-only mode, 4 recycles, strictly float16 GPU with chunk size 128 for all registered benchmark stages including E1 development tuning and TS50 primary evaluation; CPU float32 and chunk size 64 classified strictly as non-confirmatory diagnostics; max len 1024 with preflight manifest validation, fixed screening seed 42) is used exclusively to compute initial structural screening metrics for generation pools and candidate selection ($K = 100–500$ sequences/target). Retried exactly once with identical frozen configuration upon infrastructure failure; never silently altered.
     - Operational screening thresholds: $\text{scRMSD}_{\text{screen}} \le 2.0\text{ \AA} \land \text{pLDDT}_{\text{screen}} \ge 80.0$ (project-chosen operational cutoffs informed by literature conventions).
   - **Primary Final Structural Validation Oracle:** **AlphaFold2 (v2.3.2, monomodel weights `model_1_ptm`, 3 recycles, no templates, single sequence mode, float16 / fp16 on GPU, fixed inference seed = 42, Amber disabled)** is the frozen primary validation oracle for the final selected library ($M = 10$ candidates/target). Retried exactly once with identical frozen configuration upon infrastructure failure; development failure yields $J = -\infty$.
     - Fixed inference seed controls stochastic initialization, but does not guarantee bitwise GPU determinism across differing CUDA drivers, cuBLAS algorithms, or hardware platforms.
     - 1-to-1 residue correspondence without gaps; 100% resolved native $C_\alpha$ coordinates required.

   - **Sensitivity Validation Oracle:** **Boltz-1 (v0.4.1, default diffusion steps, no templates, single sequence mode)** is designated strictly for sensitivity analysis.
2. **Anti-Leakage Prohibition:**
   A metric or oracle score used as an objective criterion during candidate selection (ESMFold) must NEVER be cited as independent evidence of success without confirmation by the primary independent validation oracle (AlphaFold2).
3. **Hyperparameter Isolation & Freezing:**
   All selection thresholds, mixing weight $\lambda^*$, diversity weights $\gamma^*$, and sampling temperatures $T^*$ must be determined strictly on the validation set (frozen manifest `data/manifests/development_20_cath42.txt`, 20 backbones) maximizing development objective $J$, and strictly frozen prior to unblinding or evaluating final benchmark test targets (TS50). Zero tuning or post hoc selection against test outcomes is permitted.


