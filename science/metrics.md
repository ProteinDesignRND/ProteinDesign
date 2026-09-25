# Evaluation Metrics & Scientific Justification

This document establishes the mathematical definitions, operational implementations, failure modes, and scientific justifications for all metrics used in the Protein Design project.

---

## 1. Primary Metrics Matrix

| Metric Name | Mathematical Definition | Property Measured | Gaming / Failure Mode | Threshold Classification |
|---|---|---|---|:---:|
| **Native Sequence Recovery (AAR)** | $\text{AAR} = \frac{1}{L} \sum_{i=1}^L \mathbb{I}(s_i = s_i^{\text{native}})$ | Agreement with natural evolutionary sequence | Penalizes valid alternative sequences (neutral drift); favors memorization over de novo foldability. | Reference agreement proxy (No universal threshold; single-target result $\ne$ benchmark) |
| **Perplexity (PPL)** | $\text{PPL} = \exp\left(-\frac{1}{L} \sum_{i=1}^L \log P(s_i \mid \text{context}_i)\right)$ | Model confidence on sequence under conditioning | Lower PPL does not guarantee thermodynamic stability; different model conditioning prevents cross-model comparability. | Model-specific diagnostic score (NOT cross-model comparable) |
| **Self-Consistency RMSD (scRMSD)** | $\text{scRMSD} = \sqrt{\frac{1}{L_{\text{aligned}}} \sum_{i \in \text{aligned}} \|\hat{\mathbf{x}}_i^{\text{CA}} - \mathbf{x}_i^{\text{CA}}\|^2}$ after optimal Kabsch superposition | Structural fidelity: Does predicted structure match design target backbone? | Hallucination on repeat motifs; sensitive to flexible loop ends. | Literature-supported screening threshold: $\le 2.0\text{ \AA}$ |
| **Self-Consistency TM-Score (scTM)** | $\text{scTM} = \max \frac{1}{L_{\text{target}}} \sum_{i=1}^{L_{\text{aligned}}} \frac{1}{1 + (d_i / d_0)^2}$ | Global fold topology similarity (length-scaled, scale-invariant) | Insensitive to local steric clashes or side-chain packing errors. | Literature-supported screening threshold: $\ge 0.7$ ($\ge 0.5$ indicates same global fold) |
| **Predicted lDDT (pLDDT)** | $\text{Mean per-residue predicted lDDT} \in [0, 100]$ from folding oracle | Folding oracle's confidence in local structural prediction | High confidence on non-protein repeating sequences; confidence is not free energy ($\Delta G$). | Literature-supported screening threshold: $\ge 80.0$ |
| **Structural Viability Rate (SVR)** | $\text{SVR} = \frac{|\{s \in S_{\text{generated}} : \text{scRMSD}(s) \le 2.0\text{ \AA} \land \text{pLDDT}(s) \ge 80\}|}{|S_{\text{generated}}|}$ | Raw structural yield of the generation model | Sensitive to choice of screening oracle and stringency of cutoffs. | Non-tautological generative yield metric |
| **Independent Validation Yield (IVY)** | $\text{IVY} = \frac{|\{s \in S_{\text{selected}} : \text{scRMSD}_{\text{indep}}(s) \le 2.0\text{ \AA} \land \text{pLDDT}_{\text{indep}}(s) \ge 80\}|}{|S_{\text{selected}}|}$ | Post-selection yield under independent validation oracle | Verifies that selected library is not an artifact of screening oracle bias. | Cross-oracle validation metric |
| **Pairwise Sequence Diversity (Div)** | $\text{Div}(S) = \frac{2}{K(K-1)} \sum_{j < k} \left(1 - \frac{\text{ID}(s_j, s_k)}{L}\right)$ | Mutual dispersion of candidates at specified evaluation stage | Trivial to maximize via random sequences; must be evaluated on structurally viable subset. | Stage-specific metric (Raw, Viable, Selected) |
| **Pareto Hypervolume (HV)** | Volume of objective space dominated by candidate set relative to fixed anti-ideal reference point $\mathbf{r}$ | Multi-objective trade-off between structural fidelity, confidence, and diversity | Sensitive to objective scaling and choice of reference point. | Planned multi-objective evaluation metric |
| **Biophysical Proxy: Isoelectric Point (pI)** | Henderson-Hasselbalch net charge titration curve at pH 7.4 | Theoretical charge and solubility tendency | Ignores 3D electrostatic environment and salt bridges. | Secondary heuristic proxy |
| **Biophysical Proxy: Hydrophobic Core Fraction** | Fraction of hydrophobic residues $\{\text{V, L, I, F, M, W}\}$ buried in core ($\text{RSA} < 0.20$) | Core packing integrity vs. aggregation risk | Heuristics do not model sidechain rotamer packing strain. | Secondary structural proxy |
| **Inference Compute Latency** | Wall-clock seconds per candidate sequence | Practical computational efficiency and scalability | Hardware-dependent; depends heavily on batching regime and iterative vs. single-pass decoding. | Operational metric (Must report hardware, precision, batch size) |

---

## 2. Rigorous Mathematical & Operational Definitions

### A. Native Sequence Recovery (Amino Acid Recovery, AAR)
- **Mathematical Definition:**
  For a designed sequence $s = (s_1, \dots, s_L)$ and wild-type target reference sequence $s^{\text{native}} = (s_1^{\text{native}}, \dots, s_L^{\text{native}})$ of length $L$:
  $$\text{AAR}(s, s^{\text{native}}) = \frac{1}{L} \sum_{i=1}^L \mathbb{I}(s_i = s_i^{\text{native}})$$
  where $\mathbb{I}(\cdot)$ is the indicator function ($1$ if identities match, $0$ otherwise).
- **Candidate Aggregation:**
  For a candidate pool $S = \{s^{(1)}, \dots, s^{(K)}\}$ generated for a given target structure:
  $$\overline{\text{AAR}} = \frac{1}{K} \sum_{k=1}^K \text{AAR}(s^{(k)}, s^{\text{native}})$$
- **Benchmark Aggregation:**
  Across a benchmark set of $M$ targets, mean AAR is reported both unweighted ($\frac{1}{M} \sum_{m=1}^M \overline{\text{AAR}}_m$) and residue-length-weighted ($\frac{\sum_{m=1}^M L_m \overline{\text{AAR}}_m}{\sum_{m=1}^M L_m}$).
- **Missing Residue Handling:**
  Only positions with experimentally resolved backbone coordinates in the reference PDB are included in $L$. Flexible terminal residues or unresolved loops lacking coordinates are excluded from evaluation.
- **Scientific Caveat:**
  AAR measures similarity to one historical evolutionary sequence. In natural biology, multiple distinct sequence families fold into the same topology (e.g. globin folds, TIM barrels). AAR rewards sequence memorization and can penalize valid, novel de novo sequences that fold into the target geometry. Comparative AAR must be measured experimentally on identical evaluation targets; no cross-model outcome is assumed in advance.

---

### B. Perplexity (PPL) & Model Likelihood
- **Mathematical Definition:**
  $$\text{PPL}(s \mid \text{backbone}) = \exp\left( -\frac{1}{L} \sum_{i=1}^L \log P(s_i \mid \text{context}_i) \right)$$
- **Critical Cross-Model Comparability Distinction:**
  The conditional probability mechanisms of the baseline models differ fundamentally:
  1. **ProteinMPNN:** Evaluates normalized autoregressive conditional probabilities along a designated residue decoding permutation order $\pi$:
     $$P_{\text{MPNN}}(s \mid \mathbf{X}, \pi) = \prod_{i=1}^L P(s_{\pi(i)} \mid \mathbf{X}, s_{\pi(<i)})$$
     Perplexity represents an exact, normalized autoregressive sequence likelihood factorized over the residue sequence.
  2. **ProteinSolver:** Formulated as a masked constraint satisfaction graph model. When scoring a full sequence in diagnostic mode (e.g. passing reference sequence via `data.y`), it evaluates each position's marginal conditional probability given the distance graph and masked context. It does NOT define a normalized autoregressive sequence joint distribution.
  3. **Operational Rule:**
     ProteinSolver pseudo-perplexity and ProteinMPNN autoregressive perplexity are **NOT directly comparable numerical quantities**. They serve strictly as **model-specific internal ranking diagnostics**. They must never be directly contrasted in a single numerical column without an explicit footnote explaining their different mathematical conditioning.

---

### C. Self-Consistency RMSD (scRMSD)
- **Mathematical Definition:**
  $$\text{scRMSD} = \sqrt{\frac{1}{L_{\text{aligned}}} \sum_{i \in \text{aligned}} \|\hat{\mathbf{x}}_i^{\text{CA}} - \mathbf{x}_i^{\text{CA}}\|^2}$$
  where $\mathbf{x}_i^{\text{CA}}$ are the coordinates of the $\text{C}\alpha$ atom in the target design backbone, and $\hat{\mathbf{x}}_i^{\text{CA}}$ are the coordinates of the $\text{C}\alpha$ atom in the predicted structure emitted by the folding oracle (ESMFold / AlphaFold2) after optimal rigid-body superposition.
- **Operational Ingredients:**
  - **Atom Subset:** Backbone $\text{C}\alpha$ atoms exclusively.
  - **Superposition:** Optimal rotation matrix $\mathbf{R}$ and translation vector $\mathbf{t}$ determined via the Kabsch algorithm minimizing mean squared error over aligned $\text{C}\alpha$ pairs.
  - **Score Direction:** Lower is better ($0.0\text{ \AA}$ indicates identical $\text{C}\alpha$ trace).
  - **Threshold Context:** $\text{scRMSD} \le 2.0\text{ \AA}$ is adopted as a **project screening threshold** based on standard literature practices in computational structural design (e.g. Baker Lab de novo design pipelines). It is not an absolute physical constant.

---

### D. Self-Consistency TM-Score (scTM)
- **Mathematical Definition:**
  Following the standard Zhang & Skolnick (2004) formulation:
  $$\text{scTM} = \max_{\text{superposition}} \frac{1}{L_{\text{target}}} \sum_{i=1}^{L_{\text{aligned}}} \frac{1}{1 + \left(\frac{d_i}{d_0(L_{\text{target}})}\right)^2}$$
- **Operational Ingredients:**
  - $L_{\text{target}}$: Total length of the reference target backbone.
  - $L_{\text{aligned}}$: Number of aligned residue pairs (equal to $L_{\text{target}}$ for fixed-backbone inverse folding).
  - $d_i$: Euclidean distance between the $\text{C}\alpha$ atoms of the $i$-th residue pair after optimal structural alignment.
  - $d_0(L_{\text{target}})$: Length-dependent scaling parameter:
    $$d_0(L_{\text{target}}) = 1.24 \sqrt[3]{L_{\text{target}} - 15} - 1.8 \quad (\text{for } L_{\text{target}} > 15\text{ residues})$$
  - **Score Direction:** Higher is better ($\in (0, 1]$).
  - **Interpretation:** $\text{scTM} > 0.5$ indicates the predicted structure shares the same global topology as the target; $\text{scTM} \ge 0.7$ is adopted as the **project screening threshold** for high topological fidelity.

---

### E. Predicted Local Distance Difference Test (pLDDT)
- **Definition:** Mean per-residue predicted lDDT confidence metric emitted by the structural folding oracle:
  $$\overline{\text{pLDDT}} = \frac{1}{L} \sum_{i=1}^L \text{pLDDT}_i \in [0, 100]$$
- **Scientific Caveat:**
  pLDDT is an oracle-specific local confidence score. It is NOT free energy of folding ($\Delta G$), NOT thermodynamic stability, and NOT wet-lab verification. Neural folding models can exhibit confident hallucinations (high pLDDT) on repeating or non-globular sequences. Threshold $\ge 80.0$ is an **empirically supported screening cutoff**, not a universal physical law. The exact oracle and model version must always be reported alongside the metric.

---

### F. Candidate Viability vs. Independent Validation Yield
To prevent tautological metric definitions where filtering and evaluation use identical criteria:
1. **Structural Viability Rate (SVR) — Generative Yield:**
   $$\text{SVR} = \frac{|\{s \in S_{\text{generated}} : \text{scRMSD}_{\text{screen}}(s) \le 2.0\text{ \AA} \land \text{pLDDT}_{\text{screen}}(s) \ge 80\}|}{|S_{\text{generated}}|}$$
   Measures the raw generative efficiency of the sequence generation model under the initial screening oracle (e.g. ESMFold).
2. **Independent Validation Yield (IVY) — Post-Selection Evaluation:**
   $$\text{IVY} = \frac{|\{s \in S_{\text{selected}} : \text{scRMSD}_{\text{indep}}(s) \le 2.0\text{ \AA} \land \text{pLDDT}_{\text{indep}}(s) \ge 80\}|}{|S_{\text{selected}}|}$$
   Evaluates the final candidate library using an **independent folding oracle** (e.g. AlphaFold2 or Boltz-1) that was NOT used during initial generation or screening, providing non-circular validation of candidate foldability.

---

### G. Pairwise Sequence Diversity Across Evaluation Stages
- **Mathematical Definition:**
  For any candidate sequence set $S = \{s^{(1)}, \dots, s^{(K)}\}$ of size $K \ge 2$, where each sequence has length $L$:
  $$\text{Div}(S) = \frac{2}{K(K - 1)} \sum_{1 \le j < k \le K} \left( 1 - \frac{\text{ID}(s^{(j)}, s^{(k)})}{L} \right)$$
  where $\text{ID}(s^{(j)}, s^{(k)}) = \sum_{i=1}^L \mathbb{I}(s_i^{(j)} = s_i^{(k)})$ counts matching amino acids across corresponding backbone positions.
- **Stage-Specific Diversity Reporting:**
  Diversity MUST be evaluated and reported at three distinct stages:
  1. **Raw Generation Diversity ($\text{Div}_{\text{raw}}$):** Computed over all $K$ generated samples in $S_{\text{generated}}$.
  2. **Viable Candidate Diversity ($\text{Div}_{\text{viable}}$):** Computed over the subset $S_{\text{viable}}$ passing structural screening criteria ($\text{scRMSD} \le 2.0\text{ \AA}, \text{pLDDT} \ge 80$).
  3. **Selected Library Diversity ($\text{Div}_{\text{selected}}$):** Computed over the final top-$M$ candidate library $S_{\text{selected}}$ chosen for downstream analysis.
- **Scientific Caveat:**
  Unconstrained sequence diversity is trivial to maximize (e.g. uniform random noise produces $\approx 95\%$ diversity). High diversity is scientifically meaningful ONLY when accompanied by demonstrated structural viability ($\text{Div}_{\text{viable}}$).

---

### H. Pareto Hypervolume (HV)
- **Status:** Planned multi-objective candidate selection metric (Phase 2 / Workstream D).
- **Objective Space Formulation:**
  For each candidate $u \in S$, evaluate an objective vector $\mathbf{f}(u) = (f_1, f_2, f_3, f_4) \in \mathbb{R}^4$:
  1. $f_1(u) = \text{scTM}(u) \in [0, 1]$ (maximize)
  2. $f_2(u) = 1.0 - \min(1.0, \text{scRMSD}(u) / 10.0) \in [0, 1]$ (maximize / normalized inverted RMSD)
  3. $f_3(u) = \text{pLDDT}(u) / 100.0 \in [0, 1]$ (maximize)
  4. $f_4(u) = \text{Mean pairwise distance of } u \text{ to current library } S' \in [0, 1]$ (maximize)
- **Reference Point Protocol:**
  The anti-ideal reference point $\mathbf{r} = (0.0, 0.0, 0.0, 0.0)$ must be fixed a priori before seeing experimental outputs.
- **Viability Gate:**
  Candidates failing minimal structural sanity ($\text{scRMSD} > 5.0\text{ \AA}$ or $\text{pLDDT} < 50$) are clipped to zero contribution to prevent rewarding diverse misfolded artifacts.

---

### I. Biophysical Proxies
- **Net Charge & Isoelectric Point (pI):**
  Calculated using the Henderson-Hasselbalch equation with standard EMBOSS pKa values (Asp: 3.9, Glu: 4.1, His: 6.5, Cys: 8.5, Tyr: 10.1, Lys: 10.8, Arg: 12.5; N-terminal: 8.6, C-terminal: 3.6) at neutral pH 7.4.
  *Limitation:* Sequence-based heuristic ignoring 3D electrostatic environments and tertiary salt bridges.
- **Hydrophobic Core Fraction:**
  Calculated as the fraction of project-defined hydrophobic residues $\mathcal{H} = \{\text{Val, Leu, Ile, Phe, Met, Trp}\}$ occupying core positions (relative solvent accessibility $\text{RSA} < 0.20$, computed on the target backbone via DSSP or Shrake-Rupley).
  *Limitation:* Does not measure internal steric packing strain, rotamer strain, or core void volume.

---

### J. Inference Latency & Computational Scaling
- **Standardized Reporting Requirements:**
  Computational speed must be reported with:
  1. Exact hardware specifications (e.g. NVIDIA RTX 3050 6GB Laptop GPU vs. CPU).
  2. Execution precision (FP32 vs FP16/AMP).
  3. Batching regime (single-sequence sequential unmasking vs. batched autoregressive sampling).
  4. Timing boundaries: Timing strictly measures inference forward passes (`torch.cuda.synchronize()` before and after); model loading and data extraction are measured and reported separately.
  5. Repeatability: 1 warmup run followed by reporting mean $\pm$ standard deviation across $\ge 5$ runs.
- **Architectural Scaling Note:**
  ProteinSolver's iterative constraint satisfaction design loop executes $L$ sequential unmasking passes ($O(L \times \text{GNN inference})$), whereas ProteinMPNN evaluates autoregressive decoding in $O(L)$ message-passing steps with optimized GPU vectorization. This structural difference must be documented when comparing wall-clock throughput.

---

## 3. Structural Oracle Separation & Anti-Leakage Protocol

To ensure evaluation rigor and prevent circular selection biases:
1. **Screening vs. Validation Firewall:**
   - **Screening Oracle:** ESMFold (fast, local single-pass inference) is used to compute initial structural metrics for generation pools and Pareto candidate selection.
   - **Independent Validation Oracle:** Selected candidate libraries must be evaluated under an independent structural predictor (AlphaFold2 or Boltz-1) with orthogonal architecture and training data.
2. **Anti-Leakage Prohibition:**
   A metric or oracle score used as an objective criterion during candidate selection must NEVER be cited as independent evidence of success without confirmation by the independent validation oracle.
3. **Hyperparameter Isolation:**
   All selection thresholds, Pareto trade-off weights, and sampling temperatures must be determined on validation sets (e.g. CATH 4.2 validation split), NEVER on final benchmark test targets.
