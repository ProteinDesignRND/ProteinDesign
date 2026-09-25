# EVALUATION METRICS & SCIENTIFIC JUSTIFICATION

This document establishes the mathematical definitions, operational implementations, failure modes, and scientific justifications for all metrics used in the project.

---

## 1. Primary Metrics Matrix

| Metric Name | Mathematical Definition | Property Measured | Gaming / Failure Mode | Scientific Justification Required? |
|---|---|---|---|:---:|
| **Native Sequence Recovery (AAR)** | $\text{AAR} = \frac{1}{N} \sum_{i=1}^N \mathbb{I}(s_i = s_i^{\text{native}})$ | Agreement with natural evolutionary sequence | Penalizes valid alternative sequences (neutral drift); artificially favors memorization. | **YES** (Standard proxy, but flawed for de novo design) |
| **Perplexity (PPL)** | $\text{PPL} = \exp\left(-\frac{1}{N} \sum_{i=1}^N \log P(s_i^{\text{native}} \mid X)\right)$ | Model confidence on native sequence | Lower PPL does not guarantee thermodynamic stability or structural foldability. | **YES** |
| **Self-Consistency RMSD (scRMSD)** | $\text{scRMSD} = \sqrt{\frac{1}{N} \sum_{i=1}^N \|\hat{\mathbf{x}}_i^{\text{CA}} - \mathbf{x}_i^{\text{CA}}\|^2}$ after optimal alignment | Structural fidelity: Does predicted structure match design target? | Can be fooled by folding model hallucination on repeat motifs; sensitive to flexible loop ends. | **YES** (Canonical threshold: $<2.0\text{ \AA}$) |
| **Self-Consistency TM-Score (scTM)** | $\text{scTM} = \frac{1}{L} \sum_{i=1}^{L} \frac{1}{1 + (d_i / d_0)^2}$ | Global fold topology similarity (scale-invariant) | Less sensitive to local packing errors or side-chain clashes. | **YES** (Canonical threshold: $>0.7$) |
| **Predicted lDDT (pLDDT)** | Mean per-residue predicted local distance difference test from ESMFold / AF2 / Boltz-1 ($\in [0, 100]$) | Folding oracle's confidence in its prediction | Confidence is not free energy ($\Delta G$); models can be confidently wrong on unnatural sequences. | **YES** (Canonical threshold: $>80$) |
| **Pairwise Sequence Diversity (Div)** | $\text{Div}(S) = \frac{2}{K(K-1)} \sum_{j < k} \left(1 - \frac{\text{ID}(s_j, s_k)}{L}\right)$ | Mutual dispersion of the designed candidate set | Trivial to maximize by generating random garbage sequences. | **CRITICAL: ONLY VALID AMONG STRUCTURALLY VIABLE CANDIDATES** |
| **Candidate Survival Rate (CSR)** | $\text{CSR} = \frac{|\{s \in S_{\text{selected}} : \text{scRMSD}(s) \le 2.0\text{ \AA} \land \text{pLDDT}(s) \ge 80\}|}{|S_{\text{selected}}|}$ | Practical yield of the selection pipeline | Dependent on the stringency of the validation oracle. | **YES** |
| **Pareto Hypervolume (HV)** | Volume of objective space dominated by the candidate set relative to a reference anti-ideal point | Multi-objective trade-off between structural quality and sequence diversity | Sensitive to scaling and choice of reference point. | **YES** |
| **Biophysical Proxy: Net Charge & Isoelectric Point (pI)** | Computed Henderson-Hasselbalch charge at pH 7.4 | Aggregation and expression feasibility | Does not capture 3D electrostatic spatial localization. | Secondary proxy |
| **Biophysical Proxy: Hydrophobic Core Fraction** | Percentage of hydrophobic residues (V, L, I, F, M, W) buried in core vs solvent-exposed | Core packing stability vs aggregation risk | Surface hydrophobicity heuristics can penalize functional interaction patches. | Secondary proxy |
| **Inference Compute Latency** | Wall-clock seconds per candidate sequence | Practical scalability on standard hardware | Machine-dependent; must report GPU specifications and batch size. | Operational metric |

---

## 2. In-Depth Scientific Justification for Controversial Metrics

### A. Why Sequence Recovery (AAR) is NOT Sufficient
- **Biological Reality:** Protein folding landscapes are degenerate. Many distinct sequence families fold into identical topologies (e.g., the Globin fold, TIM barrels).
- **Project Implication:** ProteinSolver has a lower average reported AAR (~33%) than ProteinMPNN (~51%). If we only evaluate AAR, ProteinSolver will predictably underperform on this metric alone by definition. However, if ProteinSolver samples structurally viable alternative sequences that ProteinMPNN ignores, it may provide genuine diversity benefits. Therefore, **scRMSD + scTM must take precedence over AAR**.

### B. Why Sequence Diversity Requires a Gatekeeper
- Any model can achieve 100% diversity by emitting uniform random characters from the 20 amino acid alphabet.
- **Strict Protocol Requirement:** Sequence diversity **must never be reported in isolation**. It must strictly be computed on the subset of candidates that **survive structural validation** ($\text{scRMSD} \le 2.0\text{ \AA}$ and $\text{pLDDT} \ge 80$). Diversity among unfolded or misfolded candidates is scientific noise.

### C. Structural Oracle Limitations (ESMFold vs. AlphaFold2 vs. Boltz-1)
- Deep learning folding oracles have known "hallucination" regimes where they output high pLDDT on non-protein sequences.
- To safeguard against oracle bias:
  1. The primary structural filter should use **ESMFold** for rapid screening.
  2. Top Pareto candidates should be cross-validated with an independent architecture (**AlphaFold2** or **Boltz-1**).
  3. Concordance between independent oracles serves as a strong filter against oracle-specific artifacts.
