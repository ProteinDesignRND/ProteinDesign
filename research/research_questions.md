# FORMAL RESEARCH QUESTIONS & HYPOTHESIS SPECIFICATION

This document outlines the primary, secondary, and falsification questions guiding the project. All questions are formulated with explicit null hypotheses ($H_0$) and operational criteria.

---

## 1. Primary Research Question (RQ1)
> **Does the integration of ProteinSolver's constraint-satisfaction scoring with ProteinMPNN's inverse-folding likelihood provide complementary inductive bias that improves the quality-diversity trade-off of designed protein sequences?**

- **Alternative Hypothesis ($H_1$):** Combining ProteinMPNN likelihood with ProteinSolver scoring via an inference-time Pareto candidate selection framework yields a higher Pareto hypervolume across structural self-consistency (scRMSD / scTM via ESMFold/AlphaFold2) and sequence diversity (mean pairwise edit distance) than temperature-varied sampling from ProteinMPNN alone.
- **Null Hypothesis ($H_0$):** Incorporating ProteinSolver scoring either degrades structural self-consistency or provides no statistically significant improvement in the Pareto hypervolume compared to ProteinMPNN baseline sampling across standard test backbones (CATH 4.2 / TS50).
- **Falsification Metric:** Two-sample Wilcoxon signed-rank test on Pareto hypervolume across $N=50$ diverse benchmark structures with significance threshold $\alpha = 0.05$.

---

## 2. Secondary Research Questions

### RQ2: Scoring Complementarity vs. Degradation
> **At what weighting or filtering regime, if any, does ProteinSolver act as a beneficial regularizer rather than destructive noise?**
- **Test Mechanism:** Evaluate linear and rank-based logit mixtures:
  $$S_{\text{hybrid}}(s) = \lambda \cdot S_{\text{MPNN}}(s \mid X) + (1 - \lambda) \cdot S_{\text{PS}}(s \mid D)$$
  across $\lambda \in [0.0, 1.0]$.
- **Critical Milestone:** Measure whether any $\lambda < 1.0$ improves self-consistency success rate ($\text{scRMSD} < 2.0\text{ \AA}$) compared to pure ProteinMPNN ($\lambda = 1.0$).

### RQ3: Diversity-Aware Selection vs. Heuristic Clustering
> **Does formal Quality-Diversity / Pareto selection offer measurable advantages over naive greedy clustering (e.g., CD-HIT or MMseqs2 at 30% sequence identity) on candidate survival rate?**
- **Evaluation Criteria:** Candidate Survival Rate = percentage of final selected sequences passing structural validation ($\text{pLDDT} \ge 80$, $\text{scRMSD} \le 2.0\text{ \AA}$) while maintaining maximum mutual sequence distance.

### RQ4: Structural Robustness across Protein Classes
> **Does the relative utility of ProteinSolver differ systematically across protein structural classes ($\alpha$-helical, $\beta$-sheet-rich, $\alpha/\beta$, and loop-heavy structures)?**
- **Hypothesis:** Because ProteinSolver relies strictly on distance cutoffs ($<12\text{ \AA}$), it may perform differently on densely packed $\alpha$-helical cores (where local packing dominates) versus nonlocal $\beta$-sheet topologies requiring exact backbone hydrogen-bonding geometry.

---

## 3. Decision Criteria for Hypothesis Pivoting
If the empirical tests in Phase 1 (Experiments E0–E2) show:
1. $S_{\text{PS}}$ has zero or negative rank correlation with structural self-consistency on ProteinMPNN designs, and
2. Every $\lambda < 1.0$ strictly lowers sequence recovery and self-consistency without improving diversity,

**THEN:** We will formally reject the complementarity hypothesis ($H_1$) in `DECISION_LOG.md` and pivot to evaluating why constraint-satisfaction GNNs fail to complement modern MPNNs, or substitute ProteinSolver with a pretrained protein language model (e.g., ESM-2) as the complementary prior.
