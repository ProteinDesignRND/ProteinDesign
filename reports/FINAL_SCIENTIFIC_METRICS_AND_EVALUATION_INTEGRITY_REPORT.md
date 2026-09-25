# FINAL SCIENTIFIC METRICS, METHODOLOGY, AND EVALUATION PROTOCOL INTEGRITY REPORT
**Task ID:** `PROTEIN-DESIGN-SCIENTIFIC-METRICS-EVALUATION-INTEGRITY-GATE-V3`  
**Execution Agent:** Gemini 3.8 Flash High (Pair Programming via Antigravity IDE 2.0)  
**Date:** 2026-09-25  
**Working Branch:** `governance/final-acceptance-redteam-v1`  
**Governance Foundation Status:** `FOUNDATION_FROZEN_WITH_LIMITATIONS`  
**Scientific Readiness Classification:** `READY_FOR_PROTEINMPNN_INTEGRATION`

---

## 1. Executive Summary

This report delivers the authoritative scientific-methodology and evaluation-protocol integrity audit for the Protein Design repository prior to beginning Phase 2 / Milestone 3 (ProteinMPNN Integration & Baseline Verification).

The governance foundation remains strictly frozen (no governance redesign or speculative entity expansion was performed). All audit actions were focused purely on:
- Mathematical rigor and operational completeness of all evaluation metrics;
- Elimination of circular/tautological evaluation leakage (particularly in candidate survival rates);
- Decoupling of non-equivalent within-model sequence likelihoods/perplexities;
- Structural oracle firewalling between initial screening and final independent validation;
- Rigorous formalization of multi-stage sequence diversity;
- Removal of uncalibrated claims, universal mask-invariance assertions, and unverified cross-model predictive wording.

All 25 pytest test suites (109 assertions) pass with zero errors. All historical ProteinSolver sources in `external/proteinsolver-original` remain 100% untouched and clean. No scientific experiments or ProteinMPNN integrations were prematurely initiated. The evaluation framework is mathematically coherent, reproducible, and ready for baseline integration.

---

## 2. Audit Scope

The following durable scientific documents, architecture files, governance rules, and implementation modules were audited:
- `science/metrics.md`: Primary metric definitions, formulas, operational ingredients, and proxy assumptions.
- `science/evaluation_protocol.md`: Experimental matrix (E0–E5), screening vs. validation pipelines, candidate selection formulations.
- `science/datasets.md`: Dataset definitions, CATH/TS50 splits, homology partition checks, data leakage prevention rules.
- `architecture/baseline_models.md`: Profiles, decoding methods, and comparative claims across baseline models.
- `docs/PROJECT_TRUTH.md`: Single source of truth for verified facts and empirical boundaries.
- `docs/TEAM_ONBOARDING.md`: Conceptual framing, model descriptions, and onboarding guidelines.
- `CLAIMS_REGISTRY.md`: Evidentiary registry of verified facts, unverified assertions, and rejected directions.
- `DECISION_LOG.md`: Architectural and scientific decision history.
- `PROJECT_STATE.md`: Milestone progression and risk registry.
- `reports/REPORT_INDEX.md`: Authority hierarchy and provenance mapping.
- Historical repository: `external/proteinsolver-original` git tree and commit status.

---

## 3. Errors Discovered

| Issue ID | Document / Area | Error Description | Scientific Risk |
|---|---|---|---|
| **ERR-MET-01** | `science/metrics.md` | Incomplete TM-score formulation: missing distance scale parameter $d_0(L)$, length normalization identity, and Kabsch superposition requirement. | Inconsistent structural similarity evaluation; nonstandard TM-score values. |
| **ERR-MET-02** | `science/metrics.md` & `science/evaluation_protocol.md` | Tautological Candidate Survival Rate (CSR): evaluating candidate survival using the same conditions ($\text{scRMSD} \le 2.0\text{ \AA} \land \text{pLDDT} \ge 80$) used to select candidates, guaranteeing a trivial 100% yield. | Circular evaluation; false appearance of candidate design success. |
| **ERR-MET-03** | `science/metrics.md` & `science/evaluation_protocol.md` | Conflation of ProteinSolver and ProteinMPNN Perplexity: treating masked pseudo-perplexity and autoregressive joint sequence perplexity as directly comparable cross-model metrics. | Apples-to-oranges comparison of conditional likelihood mechanisms. |
| **ERR-MET-04** | `science/evaluation_protocol.md` | Structural oracle leakage: lack of explicit separation between initial screening oracle and post-selection validation oracle. | Confirmation bias / oracle overfitting (ESMFold evaluating ESMFold-selected designs). |
| **ERR-MET-05** | `docs/TEAM_ONBOARDING.md` & `CLAIMS_REGISTRY.md` | Universal mask-invariance assertion ("The model is 100% mask-invariant"). | Generalizing a single adversarial test (EXP004) into a universal mathematical invariant. |
| **ERR-MET-06** | `docs/TEAM_ONBOARDING.md` | ProteinMPNN decoding description error: described as "autoregressive left-to-right prediction with random order" (an internal contradiction). | Confusion regarding ProteinMPNN's actual arbitrary/random permutation decoding mechanism. |
| **ERR-MET-07** | `docs/TEAM_ONBOARDING.md` | Speculative hypothesis framing: "These differences mean their errors might be uncorrelated". | Prematurely implying empirical independence rather than framing as a hypothesis to be tested. |
| **ERR-MET-08** | Multiple documents | Uncalibrated terminology: "canonical threshold", "state-of-the-art" (unqualified), "predictably underperform by definition". | Loss of scientific neutrality; dogmatic phrasing. |
| **ERR-MET-09** | `science/metrics.md` | Unspecified Pareto Hypervolume (HV) reference point and objective transformations. | Post-hoc reference point selection manipulating hypervolume rankings. |
| **ERR-MET-10** | `reports/REPORT_INDEX.md` | Dual-listing confusion: `research/paper_vs_implementation.md` listed under reference documents and superseded documents without clear subordination. | Ambiguous truth authority. |

---

## 4. Scientific-Methodology Corrections

1. **Replaced Predictive Language with Empirical Hypotheses:**
   - Removed: *"ProteinSolver will predictably underperform on this metric alone by definition."*
   - Replaced with: Clarification that Native Sequence Recovery (AAR) measures exact wild-type agreement and can penalize viable alternative sequences that preserve fold; cross-model recovery must be empirically measured on the same evaluation splits without advance outcome assumptions.
2. **Reframed Error Independence as an Untested Research Hypothesis:**
   - Replaced speculative assertions that model errors "might be uncorrelated" with:
     > *"The architectural differences motivate testing whether the models provide complementary signals — which is the research hypothesis under investigation."*
3. **Qualified Modern Baseline Terminology:**
   - Replaced unqualified "state-of-the-art" (SOTA) labels with date- and citation-specific references: "Primary modern inverse-folding baseline (Dauparas et al. 2022)".
4. **Clarified Single-Target Scope of Current 1n5uA03 Results:**
   - Re-audited all references to the 1n5uA03 41.30% recovery result to guarantee it is strictly documented as a *single-target all-masked inverse-folding integration result* and never conflated with general benchmark performance.

---

## 5. Metric-Definition Corrections

### 5.1 Native Sequence Recovery (AAR)
- **Mathematical Formula:**
  $$\text{AAR}(s, s^{\text{native}}) = \frac{1}{|I_{\text{eval}}|} \sum_{i \in I_{\text{eval}}} \mathbb{I}(s_i = s_i^{\text{native}})$$
- **Operational Ingredients:**
  - $I_{\text{eval}}$ is the set of evaluated residue indices for a single target chain (excluding missing residues in experimental electron density).
  - Multi-target / multi-candidate aggregation defined explicitly at candidate level, target level (mean across candidates), and benchmark level (macro-average across targets).
  - Explicit limitation documented: AAR is an evolutionary-agreement metric, not direct proof of thermodynamic stability, folding fidelity, or functional viability.

### 5.2 Decoupled Model-Specific Perplexity (PPL)
- **ProteinSolver Masked Pseudo-Perplexity:**
  $$\text{PPL}_{\text{PS}}(s \mid \mathcal{G}) = \exp\left( -\frac{1}{L} \sum_{i=1}^L \log p_{\text{PS}}(s_i \mid \mathcal{G}, s_{\setminus i}) \right)$$
  Evaluates masked residue conditional likelihoods.
- **ProteinMPNN Autoregressive Joint Perplexity:**
  $$\text{PPL}_{\text{MPNN}}(s \mid \mathbf{X}, \pi) = \exp\left( -\frac{1}{L} \sum_{i=1}^L \log p_{\text{MPNN}}(s_{\pi_i} \mid \mathbf{X}, s_{\pi_{<i}}) \right)$$
  Evaluates conditional likelihoods under permutation decoding order $\pi$.
- **Critical Cross-Model Comparability Rule:**
  Because the conditional conditioning mechanisms differ fundamentally (masked marginal pseudo-likelihood vs. autoregressive joint decomposition), $\text{PPL}_{\text{PS}}$ and $\text{PPL}_{\text{MPNN}}$ are **NOT directly comparable cross-model evaluation metrics**. They are documented strictly as **model-specific internal diagnostics**.

### 5.3 Self-Consistency RMSD (scRMSD)
- **Mathematical Formula:**
  $$\text{scRMSD}(\mathbf{X}_{\text{pred}}, \mathbf{X}_{\text{target}}) = \min_{\mathbf{R} \in \text{SO}(3), \mathbf{t} \in \mathbb{R}^3} \sqrt{\frac{1}{L} \sum_{i=1}^L \|\mathbf{R} \mathbf{x}_{\text{pred}, i}^{\text{C}\alpha} + \mathbf{t} - \mathbf{x}_{\text{target}, i}^{\text{C}\alpha}\|^2}$$
- **Operational Ingredients:**
  - Evaluated strictly over backbone C$\alpha$ atoms ($N=L$ matched pairs).
  - Optimal rigid-body rotation $\mathbf{R}$ and translation $\mathbf{t}$ computed via the Kabsch algorithm.
  - Direction: Lower is better ($0.0\text{ \AA}$ indicates identical backbone geometry).
  - Screening threshold: $\le 2.0\text{ \AA}$ is classified as a *project screening threshold* (supported by RFdiffusion / Baker Lab literature), NOT a universal canonical constant.

### 5.4 Standard TM-Score (scTM)
- **Mathematical Formula (Zhang & Skolnick 2004):**
  $$\text{scTM}(\mathbf{X}_{\text{pred}}, \mathbf{X}_{\text{target}}) = \frac{1}{L_{\text{target}}} \sum_{i=1}^{L_{\text{target}}} \frac{1}{1 + \left( \frac{d_i(\mathbf{R}^*, \mathbf{t}^*)}{d_0(L_{\text{target}})} \right)^2}$$
- **Length-Scaling Parameter:**
  $$d_0(L_{\text{target}}) = 1.24 \sqrt[3]{L_{\text{target}} - 15} - 1.8$$
- **Operational Ingredients:**
  - Normalized strictly by $L_{\text{target}}$ to prevent length-dependent score distortion.
  - $d_i$ is the distance between the $i$-th aligned C$\alpha$ residue pair after optimal superposition $(\mathbf{R}^*, \mathbf{t}^*)$ maximizing the TM-score.
  - Direction: Higher is better ($\in (0, 1]$; $\text{scTM} > 0.5$ generally indicates identical global topological fold).

### 5.5 Structural Confidence (pLDDT)
- **Operational Definition:** Predicted Local Distance Difference Test extracted directly from folding oracle output (ESMFold / AlphaFold2).
- **Explicit Limitations:** pLDDT measures local structural prediction confidence of the specific folding oracle; it is **NOT** thermodynamic stability ($\Delta G$), physical rigidity, or experimental crystallographic validation. Inter-oracle pLDDT values are not directly interchangeable.

### 5.6 Non-Tautological Viability Metrics (SVR and IVY)
To eliminate circular evaluation, Candidate Survival Rate was replaced by two decoupled, non-tautological metrics:
1. **Generative Structural Viability Rate (SVR):**
   $$\text{SVR} = \frac{|\{s \in S_{\text{raw}} \mid \text{scRMSD}_{\text{screen}}(s) \le 2.0\text{ \AA} \land \text{pLDDT}_{\text{screen}}(s) \ge 80.0\}|}{|S_{\text{raw}}|}$$
   Measures raw generative yield of the design model on initial screening oracle (ESMFold).
2. **Independent Validation Yield (IVY):**
   $$\text{IVY} = \frac{|\{s \in S_{\text{selected}} \mid \text{scRMSD}_{\text{val}}(s) \le 2.0\text{ \AA} \land \text{pLDDT}_{\text{val}}(s) \ge 80.0\}|}{|S_{\text{selected}}|}$$
   Measures post-selection survival when evaluated by a distinct, independent structural validation oracle (AlphaFold2 or Boltz-1). Because $S_{\text{selected}}$ was selected on screening scores, evaluating it on an independent oracle avoids circularity and can fail (non-trivial yield).

### 5.7 Multi-Stage Sequence Diversity
Codified three distinct sequence diversity stages to prevent conflating raw sample dispersion with final library quality:
1. **Raw Generation Diversity ($D_{\text{raw}}$):** Mean pairwise Hamming distance over $S_{\text{raw}}$.
2. **Structurally Viable Diversity ($D_{\text{viable}}$):** Pairwise distance computed strictly over candidate subset satisfying structural screening ($\text{scRMSD} \le 2.0\text{ \AA} \land \text{pLDDT} \ge 80$).
3. **Selected Library Diversity ($D_{\text{selected}}$):** Pairwise distance computed across the final chosen $M$ candidates.
- Explicit rule: High diversity is trivial to achieve via random mutation; diversity metrics are meaningful only when reported alongside structural viability (SVR/IVY) and recovery.

### 5.8 Pareto Hypervolume (HV)
- **Mathematical Formula:**
  $$\text{HV}(S_{\text{selected}}, \mathbf{r}) = \Lambda\left( \bigcup_{s \in S_{\text{selected}}} [\mathbf{r}, \mathbf{f}(s)] \right)$$
- **Operational Ingredients:**
  - Objective vector $\mathbf{f}(s) = (f_1(s), f_2(s), f_3(s))$:
    1. Inverse-folding score (maximized);
    2. Structural fidelity ($-\text{scRMSD}$, maximized);
    3. Structural confidence ($\text{pLDDT}$, maximized).
  - All objectives normalized to $[0, 1]$ via min-max scaling across benchmark pool bounds.
  - **A Priori Fixed Reference Point:** $\mathbf{r} = (0.0, 0.0, 0.0)$ defined prior to observing candidates to prevent retrospective manipulation.

### 5.9 Biophysical Proxies
- **Isoelectric Point ($\text{pI}$):** Henderson-Hasselbalch charge balance equation using standard EMBOSS pKa values; documented as an in silico sequence heuristic that ignores 3D electrostatic microenvironments.
- **Hydrophobic Core Fraction ($f_{\text{core}}$):** Fraction of defined hydrophobic residues $\{\text{V, L, I, F, M, W}\}$ having relative solvent accessibility $\text{RSA} < 0.20$ in the folded structure (computed via DSSP / Shrake-Rupley).

---

## 6. Selection vs. Evaluation Leakage Checks

The audit verified an anti-leakage lifecycle separating candidate generation from final validation:

```
[GENERATION]
   Raw candidate sequences generated under fixed candidate budget K
   (Deterministic MAP or stochastic sampling under predefined seeds and temperatures)
         │
         ▼
[SCREENING]
   Screening Oracle (ESMFold) evaluates scRMSD_screen, scTM_screen, pLDDT_screen
   Compute Generative Structural Viability Rate (SVR)
         │
         ▼
[SELECTION]
   Multi-objective Pareto ranking + Diversity dispersion over S_viable
   Candidate library S_selected (top M) chosen
         │
         ▼
[INDEPENDENT VALIDATION]
   Independent Oracle (AlphaFold2 / Boltz-1) evaluates S_selected
   Compute Independent Validation Yield (IVY)
   (Never evaluate selection success using the screening oracle alone)
         │
         ▼
[STATISTICAL ANALYSIS]
   Paired Wilcoxon signed-rank test across benchmark backbones (p < 0.01)
```

**Anti-Leakage Safeguards Enforced:**
1. Hyperparameters ($\lambda, T, \gamma$) must be tuned on the validation split, never on the final test set.
2. Screening scores ($-\text{scRMSD}_{\text{screen}}$) used for Pareto selection cannot be presented as independent evidence that selection produced folding candidates.
3. IVY must be evaluated on an independent structural oracle.

---

## 7. Structural-Oracle Protocol Corrections

1. **Screening Oracle:** ESMFold is allocated for high-throughput initial candidate filtering ($K = 100$ to $500$ per target) due to fast single-pass transformer inference.
2. **Independent Validation Oracle:** AlphaFold2 (or Boltz-1) is reserved for validating final selected libraries ($M = 10$ to $20$).
3. **Threshold Calibration:** Structural thresholds ($\text{scRMSD} \le 2.0\text{ \AA}$ and $\text{pLDDT} \ge 80$) are explicitly designated as *project screening thresholds* rather than "canonical community laws".
4. **Oracle Independence Logging:** Every reported structural metric must explicitly record the identity and version of the generating oracle (e.g., `scRMSD_ESMFold_v1` vs. `scRMSD_AlphaFold2_v2.3.2`).

---

## 8. Documentation Corrections

1. **`science/metrics.md`:** Completely rewritten to establish rigorous formulas, operational definitions, anti-leakage rules, and biophysical proxy specifications.
2. **`science/evaluation_protocol.md`:** Updated to incorporate non-tautological SVR and IVY metrics, modern baseline phrasing, oracle separation firewall, and a priori fixed Pareto reference point.
3. **`architecture/baseline_models.md`:** Updated ProteinMPNN profile from "Primary SOTA Baseline" to "Primary Modern Baseline (Dauparas et al. 2022)"; clarified random/arbitrary permutation decoding orders.
4. **`docs/TEAM_ONBOARDING.md`:**
   - Corrected model descriptions (removed casual "BERT-style" phrasing for ProteinSolver; eliminated "autoregressive left-to-right" contradiction for ProteinMPNN).
   - Scoped mask-invariance assertion to empirical EXP004 test result.
   - Reframed error independence as an untested research hypothesis.
   - Qualified modern baseline wording.
5. **`docs/PROJECT_TRUTH.md`:** Scoped mask-invariance verification statement to tested experiment evidence (`EXP004`).
6. **`CLAIMS_REGISTRY.md`:** Scoped claim `V-14` to tested experiment evidence (`EXP004`).
7. **`reports/REPORT_INDEX.md`:** Restructured into an unambiguous authority hierarchy; eliminated dual-listing ambiguity for historical pre-hardening documents; registered this integrity report.
8. **`DECISION_LOG.md`:** Added `[DEC-011]` documenting the scientific metrics and evaluation protocol integrity pass.
9. **`PROJECT_STATE.md`:** Recorded completion of `Milestone 2.6: Scientific Metrics & Evaluation Protocol Integrity Gate`.

---

## 9. Verification Results

### 9.1 Test Suite Execution
- **Pytest Suite (`tests/test_governance.py`):**
  - Command: `environment/proteinsolver-original/Scripts/python.exe -m pytest tests/ -v`
  - Result: **25 passed in 0.90s** (109 assertions verified, 0 failures, 0 warnings).
- **Direct Governance Test (`tests/test_governance.py`):**
  - Command: `environment/proteinsolver-original/Scripts/python.exe tests/test_governance.py`
  - Result: **25/25 test suites passed** (109 assertions).
- **Historical Execution & Baseline Verification (`test_original_execution.py`):**
  - Command: `environment/proteinsolver-original/Scripts/python.exe test_original_execution.py`
  - Result: **All tests passed** (Forward pass execution, checkpoint key mapping, deterministic CSP sampling on 1n5uA03 producing 41.30% recovery [38/92 residues]).
- **Governance Preflight CLI Verification:**
  - Command: `environment/proteinsolver-original/Scripts/python.exe governance/preflight_cli.py --model-family proteinsolver --stage evaluation`
  - Result: **`PREFLIGHT PASSED`** (Preflight check returned 0 errors, MUST/SHOULD rules evaluated).
- **External Repository Integrity Check:**
  - Command: `git -C external/proteinsolver-original status`
  - Result: Clean on branch `master`, commit `69ef0965a3fc3bf191804035b539720a06e58ba6`, 0 untracked files, 0 modifications.

---

## 10. Intentional Limitations

1. **Single-Target Integration Scope:** Current empirical recovery data is strictly limited to 1n5uA03 (92 AA, 41.30% recovery). It is NOT general benchmark performance.
2. **Full Training Corpus Unverifiability:** Training set membership of 1n5uA03 in the 72M Gene3D corpus remains *not verifiable from accessible metadata* without downloading the full external multi-terabyte dataset.
3. **In Silico Proxy Nature of Folding Oracles:** ESMFold and AlphaFold2 predictions represent computational structural models, not in vitro biophysical measurements of thermodynamic folding stability or experimental function.
4. **Model Perplexity Asymmetry:** ProteinSolver pseudo-perplexity and ProteinMPNN autoregressive perplexity cannot be placed on a common quantitative axis; they remain separate internal diagnostics.

---

## 11. Remaining Unresolved Issues

No material scientific-methodology or evaluation-protocol blockers remain. The evaluation protocol is fully defined, mathematically coherent, and guarded against evaluation leakage.

---

## 12. Final Readiness Classification

**Classification:** **`READY_FOR_PROTEINMPNN_INTEGRATION`**

The governance foundation is frozen with documented limitations, and the scientific metrics and evaluation protocol pass is complete. The repository possesses clean provenance, verified historical baseline execution, and an unambiguous evaluation protocol.

---

## 13. Exact Next Phase

**Phase 2 / Milestone 3: ProteinMPNN Integration & Baseline Verification**  
- Workstream: `Workstream B` (Modern Inverse-Folding Baselines)
- Action: Integrate official ProteinMPNN repository into cleanroom environment, verify forward pass and autoregressive decoding on shared benchmark backbones (including 1n5uA03 integration control), and establish the standard baseline sequence recovery before initiating hybrid ensembling (E2).
