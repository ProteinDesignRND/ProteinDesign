# PROVISIONAL RESEARCH GAP & PRIOR ART AUDIT

This document records the exhaustive audit of prior art, closest published baselines, known limitations, and the provisional research gap for the **Protein Design / ProteinSolver Research Extension**.

---

## 1. Explicit Prior Art Identification (10 Core Dimensions)

### 1. Most Direct Paper Improving / Replacing ProteinSolver
- **Paper:** *PiFold: Toward effective and efficient protein inverse folding* (Gao et al., ICLR 2023) and *ProteinInvBench* (Gao et al., NeurIPS 2023 / Briefings in Bioinformatics 2024).
- **Finding:** PiFold explicitly references ProteinSolver's graph constraint approach and replaces its simple edge convolutions with multi-scale residue featurization (1D sequential, 2D distance/angles, 3D direction vectors) and dual-track PiGNN layers. PiFold achieves 51.66% sequence recovery on CATH 4.2 in one forward pass, directly outperforming ProteinSolver (~33%).

### 2. Strongest Modern Alternative to ProteinSolver
- **Paper:** *Robust deep learning-based protein sequence design using ProteinMPNN* (Dauparas et al., Science 2022).
- **Finding:** ProteinMPNN is the universally accepted state-of-the-art benchmark. By conditioning on full backbone atomic coordinates (N, CA, C, O) via local reference frames and an autoregressive message-passing decoder with random decoding orders, ProteinMPNN achieves 51–52% sequence recovery and unparalleled experimental rescue rates across thousands of designed monomers and assemblies.

### 3. Closest Paper Using Multiple Sequence-Design Models (Ensembling)
- **Paper:** *Combining Language Models and Inverse Folding for Antibody Design via Inference-time Weighted Ensembles* (Shuai, Ruffolo, & Gray, bioRxiv 2023).
- **Finding:** Demonstrates that linearly combining logits at inference time between an inverse-folding model (ProteinMPNN) and a generative sequence language model (IgLM) outperforms either single model in sequence recovery, perplexity, and humanness.
- **Critical Distinction:** They ensembled an inverse-folding model with a protein language model for antibody CDR loops; they did **not** ensemble two distinct structure-conditioned models (e.g., ProteinSolver + ProteinMPNN) or evaluate general globular proteins.

### 4. Closest Paper Combining Sequence Design + Structure Prediction
- **Paper:** *De novo design of protein structure and function with RFdiffusion* (Watson et al., Nature 2023).
- **Finding:** Establishes the standard, universally employed pipeline:
  $$\text{Target / Backbone Diffusion (RFdiffusion)} \longrightarrow \text{Sequence Design (ProteinMPNN)} \longrightarrow \text{Structure Validation (AlphaFold2 self-consistency)}$$
  Filtering sequences where $\text{scRMSD} < 2.0\text{ \AA}$ and $\text{pLDDT} > 80$.
- **Novelty Implication:** The combination of `Sequence Generator + AlphaFold Filtering` is **strictly prior art** and cannot be claimed as novel.

### 5. Closest Paper Using Multi-Objective Optimization in Sequence Design
- **Paper:** *ProteinZero: Self-Improving Inverse Folding via Online Reinforcement Learning* (Fan et al., arXiv 2024 / ICLR 2025).
- **Finding:** Optimizes inverse folding across multiple objectives simultaneously (structural designability via ESMFold, thermodynamic stability via a learned ddG oracle, and sequence diversity via an embedding-space regularizer).
- **Critical Distinction:** ProteinZero uses online RL fine-tuning of network weights (computationally heavy, 3 days on 8x GPUs), whereas a test-time candidate ranking framework operates without expensive retraining.

### 6. Closest Paper Optimizing Sequence Diversity
- **Paper:** *Illuminating Protein Sequence Spaces with Quality-Diversity Algorithms and Gradient-Informed Emitters (ME-GIDE)* (Fontaine et al., ACM GECCO 2023) and *ProteinZero* (Fan et al., 2024).
- **Finding:** ME-GIDE uses MAP-Elites with gradient-informed discrete emitters to populate behavioral niches in protein fitness landscapes. ProteinZero uses an explicit KL-divergence and embedding diversity penalty to counteract the severe mode collapse of low-temperature autoregressive decoding.

### 7. Closest Paper to Our Exact Proposed Pipeline
- **Status:** **No exact 1-to-1 match exists** that integrates:
  $$\text{ProteinSolver CSP Scores} + \text{ProteinMPNN Likelihood} + \text{Structure Oracle (AF2/ESMFold/Boltz-1)} + \text{Diversity-Aware Pareto Selection}$$
- **However:** All individual components (ensembling, structural filtering, multi-objective ranking, diversity preservation) exist in adjacent papers (Shuai et al. 2023, Watson et al. 2023, Fan et al. 2024, Fontaine et al. 2023).

### 8. Exact Parts of Our Current Idea That Are Already Known
1. Framed protein design as a graph constraint problem (Strokach et al. 2020).
2. Generating sequences with ProteinMPNN and validating foldability via AlphaFold2 (Watson et al. 2023).
3. Test-time logit combination between inverse folding models and external sequence scoring models (Shuai et al. 2023).
4. Multi-objective trade-offs between structural foldability and sequence diversity (Fan et al. 2024, Fontaine et al. 2023).

### 9. Parts That Appear Insufficiently Studied
1. **Representational Complementarity:** Whether an older distance-graph constraint satisfaction network (ProteinSolver, trained on Gene3D superfamilies) contains orthogonal structural inductive biases that compensate for ProteinMPNN's local-coordinate geometric blind spots (e.g., in long-range contact networks or flexible loops).
2. **Post-Hoc Quality-Diversity Candidate Selection vs. Generative Fine-Tuning:** While ProteinZero addresses diversity via expensive RL retraining, lightweight, test-time diversity-aware Pareto selection across a candidate pool generated by complementary models has not been rigorously benchmarked across standard test suites (CATH 4.2, TS50, CASP15).

### 10. Evidence Still Missing Before We Can Claim a Defensible Research Gap
- **Empirical Correlation Audit:** Do ProteinSolver scores correlate with physical stability or AlphaFold confidence on ProteinMPNN-generated designs, or are they uncorrelated / negatively correlated?
- **Ablation Evidence:** Does a simple temperature sweep or clustering of ProteinMPNN alone match or exceed the diversity-quality frontier achieved by incorporating ProteinSolver? If simple temperature scaling on ProteinMPNN achieves identical results, the hypothesis collapses.

---

## 2. Structured Research Gap Analysis

### A. What ProteinSolver Originally Solved
ProteinSolver (Strokach et al., Cell Systems 2020) demonstrated that protein sequence design could be solved efficiently as a Constraint Satisfaction Problem (CSP) using deep graph neural networks. By representing residues as nodes and pairs with $<12\text{ \AA}$ heavy-atom distance as edges, with 4 residual edge-convolution blocks, it enabled rapid sequence generation that folded into target 4-helix bundles in vitro.

### B. Known Limitations Reported in the Literature
1. **Low Sequence Recovery:** Independent benchmarks (ProteinInvBench 2023) show ProteinSolver achieves ~32–35% recovery on CATH 4.2, compared to >51% for ProteinMPNN and PiFold.
2. **Lack of Invariant 3D Coordinate Frames:** ProteinSolver only consumes pairwise distance scalars and sequence separation $|i - j|$. It lacks orientation tensors (quaternions / rotation matrices), making it blind to chiral arrangements and precise backbone dihedral geometries.
3. **Iterative Generation Speed:** Autoregressive CSP-based masked sampling in ProteinSolver requires sequential re-inference, making it slower than non-autoregressive alternatives like PiFold.

### C. What Later Models Improved
- **ProteinMPNN (2022):** Introduced invariant 3D backbone featurization and autoregressive message passing, lifting sequence recovery to >51% and drastically lowering experimental failure rates.
- **ESM-IF1 (2022):** Leveraged 12M AlphaFold structures and GVP-GNN layers, establishing strong zero-shot mutational prediction capabilities.
- **PiFold (2023):** Introduced comprehensive 1D/2D/3D featurization and non-autoregressive decoding, matching ProteinMPNN accuracy at 10–70x faster inference.

### D. What Later Pipelines Already Combine
- **Canonical Design Pipeline:** RFdiffusion $\rightarrow$ ProteinMPNN $\rightarrow$ AlphaFold2 / ESMFold self-consistency filtering (scRMSD $< 2.0\text{ \AA}$, $\text{pLDDT} > 80$). This is standard practice in thousands of laboratories worldwide.

### E. What Has Been Done with Diversity and Multi-Objective Methods
- **ME-GIDE (2023):** MAP-Elites with gradient emitters on discrete protein sequences.
- **ProteinZero (2024):** Online RL balancing ESMFold scRMSD, predicted ddG stability, and embedding-level diversity regularizers to avoid mode collapse.

### F. Closest Prior-Art Combinations
- **Shuai et al. (2023):** Weighted inference-time ensemble of ProteinMPNN + IgLM for antibody design.
- **ProteinInvBench (2023):** Standardized comparative evaluation of ProteinSolver alongside ProteinMPNN.

### G. Remaining Candidate Gaps
1. **The Complementarity Question:** Does ProteinSolver's distance-constraint formulation provide useful orthogonal inductive bias when evaluated alongside modern coordinate-based models (ProteinMPNN), or is ProteinSolver strictly suboptimal in all regimes?
2. **Lightweight Test-Time Candidate Selection:** Can a post-generation multi-objective Pareto ranking framework (jointly optimizing ProteinMPNN perplexity, ProteinSolver CSP score, AlphaFold/ESMFold self-consistency, and maximum-dispersion sequence diversity) systematically outperform standard temperature sampling without requiring multi-GPU reinforcement learning?

### H. Threats to Novelty & Invalidation Scenarios
1. **Severe Performance Asymmetry:** Because ProteinSolver's error rate is substantially higher than ProteinMPNN's, any ensemble combination may simply degrade ProteinMPNN's outputs.
2. **Redundancy with Simple Temperature Scaling:** Increasing ProteinMPNN sampling temperature ($T \in [0.1, 0.5]$) and applying standard greedy clustering (e.g., MMseqs2 or CD-HIT) might yield an equal or superior quality-diversity curve without needing ProteinSolver.
3. **Modern PLM Dominance:** If an external scoring model is needed to complement ProteinMPNN, using ESM-2 (a 650M–3B parameter language model) or ESM-IF1 would almost certainly provide a stronger, higher-capacity prior than the 4-block ProteinSolver GNN.

### I. Recommended Provisional Research Question
> **"Does ProteinSolver's constraint-satisfaction scoring provide orthogonal structural signal that improves modern inverse-folding candidate selection, or does standard temperature-scaled sampling from ProteinMPNN combined with direct structure validation dominate hybrid multi-model selection?"**

*Note:* Formulating the question as a **fair, two-sided scientific contest** protects the project from confirmation bias and guarantees a publishable, scientifically sound outcome regardless of whether the hybrid method wins or loses.

### J. Confidence Level in the Research Gap
- **Overall Confidence:** **MODERATE (5/10)**.
- **Rationale:** The pipeline components are easily integrated, but the likelihood that ProteinSolver genuinely complements ProteinMPNN (rather than degrading it) is scientifically questionable given the 18% sequence recovery gap. A rigorous negative result disproving complementarity is scientifically valuable, but the project must be designed to test this impartially.
