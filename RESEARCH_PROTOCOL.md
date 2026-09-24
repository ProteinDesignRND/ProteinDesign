# RESEARCH PROTOCOL & SCIENTIFIC EVIDENCE STANDARDS

This protocol establishes the mandatory evidentiary and documentation standards for all research inquiries, literature audits, architectural formulations, and experimental evaluations conducted within this project.

---

## 1. Evidentiary Classification Scheme

Every assertion, literature reference, and scientific claim made in this project must be labeled with one of the following five evidentiary tiers:

1. **VERIFIED FACT (`[VERIFIED]`)**:
   - Directly confirmed via primary research literature (peer-reviewed journal or verified conference proceeding), or directly inspected and reproduced from verified source code / datasets.
   - Example: *"ProteinSolver uses 4 residual blocks with 128-dimensional node and edge embeddings (Strokach et al., Cell Systems 2020)."*

2. **REPORTED CLAIM (`[REPORTED CLAIM]`)**:
   - An empirical result or claim stated by authors in a published paper or preprint, but not independently verified in our local codebase.
   - Example: *"ProteinInvBench reports that ProteinMPNN achieves 51.6% native sequence recovery on CATH 4.2 (Gao et al., 2023)."*

3. **INFERENCE (`[INFERENCE]`)**:
   - A logical or theoretical deduction derived by combining verified facts or reported claims, but not yet explicitly tested as a combined system.
   - Example: *"Because ProteinSolver conditions strictly on 12 Å distance matrices without explicit 3D backbone orientation tensors, its conditional probability distribution should exhibit different error modes than ProteinMPNN."*

4. **OPEN HYPOTHESIS (`[HYPOTHESIS]`)**:
   - A scientific conjecture or proposed mechanism that is currently untested and must be subjected to falsification.
   - Example: *"Ensembling ProteinSolver logits with ProteinMPNN will improve the Pareto front of structural fidelity vs. sequence diversity."*

5. **REJECTED (`[REJECTED]`)**:
   - A previously considered hypothesis or methodology that has been disproven by empirical evidence, theoretical invalidation, or prior art audit.
   - Example: *"Claiming that ProteinSolver outperforms modern inverse folding models in standalone sequence recovery on full PDB benchmarks."*

---

## 2. Paper Audit Documentation Standard

For every paper added to `research/literature/` or recorded in `research/literature_matrix.csv`, the following standard schema must be documented:

```markdown
### [Paper ID / Citation Key]
- **Title:** [Full formal title]
- **Authors:** [Complete author list or primary authors et al.]
- **Year:** [Publication / preprint year]
- **Venue:** [Journal / Conference / bioRxiv / arXiv]
- **Identifier:** [DOI / arXiv ID / PMID / Stable URL]
- **Task:** [e.g., Structure-conditioned sequence design (Inverse Folding), De novo backbone generation, Mutation effect prediction]
- **Model Architecture:** [e.g., Message Passing GNN, Equivariant GNN, Autoregressive Transformer, Diffusion]
- **Input Data / Modality:** [e.g., Backbone coordinates (N, CA, C, O), Distance matrix (12 Å cutoff), Contact map]
- **Training Dataset & Split:** [e.g., CATH 4.2 topological split, Gene3D superfamilies (1029/172/172), PDB clustered at 30% identity]
- **Baselines Compared:** [Exact baseline models included in their experiments]
- **Evaluation Metrics:** [e.g., Native Sequence Recovery (AAR), scRMSD via AlphaFold2, scTM, Perplexity, Diversity]
- **Major Reported Findings:** [Quantitative and qualitative results reported by the authors]
- **Direct Relevance to Our Project:** [How this paper informs our problem formulation, architecture, or evaluation]
- **Limitations & Failure Modes:** [What the paper failed to address, weaknesses, or artificial evaluation setups]
- **Overlap with Our Proposed Contribution:** [Exact components that overlap with our candidate hypothesis]
- **Evidentiary Status:** [VERIFIED / REPORTED CLAIM]
```

---

## 3. Strict Rules on Novelty Claims

1. **Ban on Unqualified Superlatives:**
   - The words **"first"**, **"novel"**, **"unprecedented"**, or **"unique"** must NEVER be used without exhaustive citation verification and explicit red-team challenge.
2. **Deconstruction of Novelty:**
   - Rather than claiming a whole pipeline is novel, decompose the proposed work into concrete sub-components:
     - Component 1: Feature / representation complementarity (Is it known?)
     - Component 2: Ensembling / fusion mechanism (Is it known?)
     - Component 3: Diversity-aware candidate selection (Is it known?)
     - Component 4: Downstream multi-objective filtering (Is it known?)
3. **Audit Against Negative Results:**
   - If an idea has not been published, do not immediately assume it is an unexplored breakthrough. Actively consider whether it is an *obvious idea that fails in practice* (e.g., an inferior model corrupting a superior model).

---

## 4. Evaluation & Metric Justification Protocol

1. **No Metric Without Justification:**
   - Every metric reported in `science/metrics.md` and `science/evaluation_protocol.md` must have an explicit scientific justification detailing:
     - What physical, structural, or statistical property it measures.
     - Known failure modes (e.g., how a trivial or degenerate model can game the metric).
     - Expected baseline values from the literature.
2. **Structural Oracle Caveat:**
   - When using structure prediction models (AlphaFold2, ESMFold, Boltz-1) to evaluate designed sequences (*self-consistency validation*), acknowledge that:
     - Predicted structures are computational estimates, not experimental X-ray/cryo-EM structures.
     - Deep learning folding models have specific confidence biases and out-of-distribution blind spots.
