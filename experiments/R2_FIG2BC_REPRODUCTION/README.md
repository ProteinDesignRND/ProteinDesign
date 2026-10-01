# Experiment: R2_FIG2BC_REPRODUCTION
## Phase R2: Exact Figure 2B & Figure 2C Computational Reproduction

### Executive Status
- **Phase Outcome:** `R2_PARTIAL_VERIFIED_ON_AUXILIARY_POPULATION_WITH_HISTORICAL_EVIDENCE_RECONSTRUCTION`
- **Population Qualification (Fig 2B):** `NOT_RECONSTRUCTIBLE_WITH_CURRENT_ARTIFACTS` (10,000-instance paper dataset was stored on remote Google Cloud Storage `gs://deep-protein-gen`, which returns `HTTP 403 Forbidden`; no local copy exists).
- **Auxiliary Verification:** Executed on 7 primary target structures (including all 4 primary targets from *Cell Systems* Figure 3: 1n5uA03, 4beuA02, 4unuA00, 4z8jA00, plus 3fndA02, 5vli02, 1UBQ; 673 residues total) using canonical pretrained checkpoint `e53-s1952148-d93703104.state` (SHA-256: `1E8272F05EC19041394568C949BBDBF012EE72C1595BE7157C4BB0324D0B5727`).
- **Historical Evidence Reconstruction:** Extracted exact numerical distributions from author notebook `06_protein_analysis.ipynb` and preserved artifact `docs/images/protein_analysis/191f05de-test-oneshot-incremental.svg`, confirming historical notebook aggregate performance of 27.29% oneshot and 26.80% incremental recovery.

### Mathematical Procedures

#### 1. Figure 2B: Single-Pass vs. Iterative Most-Confident MAP
- **Single-Pass (Oneshot):**
  All positions masked simultaneously with token 20 ($x_i = 20, \forall i$). A single forward pass computes $P(x_i \mid G)$, and the argmax token is assigned: $\hat{s}_i = \operatorname{argmax}_a P(x_i = a \mid G)$.
- **Iterative MAP (Most-Confident):**
  All positions initialized to token 20. At each iteration, forward pass computes conditional probabilities. Unmasked positions are masked out from selection ($\max_{a} P = -1$). The position with the highest marginal confidence across the entire protein is committed:
  $$i^* = \operatorname{argmax}_{i \in \text{unassigned}} \max_a P(x_i = a \mid \mathbf{x}, G)$$
  The chosen amino acid is fixed, and the procedure repeats until no positions remain masked.

#### 2. Figure 2C: Conditioning under Partial Reference Information
- Conditioning fractions: 0%, 50%, 80% reference residues present.
- Mask selection: Random Bernoulli sampling with probability $f$:
  $$m_i \sim \operatorname{Bernoulli}(f)$$
- Residues with $m_i = 1$ are fixed to the wild-type reference sequence token; residues with $m_i = 0$ are set to token 20.
- Sequence recovery evaluated strictly on reconstructed (missing) residues:
  $$\text{Identity}_{\text{missing}} = \frac{1}{\sum_i (1 - m_i)} \sum_{i: m_i = 0} \mathbb{I}(\hat{s}_i = s_i^{\text{wt}})$$
  Conditioning context residues are strictly excluded from the accuracy numerator and denominator.

### Manifest of Generated Artifacts
- `run.py`: Self-contained reproduction runner.
- `config.json`: Execution parameters and target definitions.
- `population_manifest.json`: Rigorous population status classification and audit rationale.
- `provenance_manifest.json`: Checkpoint hash, parameter count, environment specifications.
- `figure_2b_target_summary.csv`: Target-by-target Figure 2B performance metrics.
- `figure_2c_replicates_summary.csv`: Replicate-level Figure 2C evaluations across 0%, 50%, 80% context.
- `figure_2c_aggregate_summary.csv`: Summary statistics by conditioning fraction.
- `figure_2b_reproduction.svg`: Publication-grade comparison plot for Figure 2B.
- `figure_2c_reproduction.svg`: Publication-grade comparison plot for Figure 2C.
- `historical_notebook_reconstruction.svg`: Vector reconstruction of historical notebook aggregate distribution.
- `PROTEINSOLVER_R2_FIG2BC_RESULTS.json`: Full machine-readable execution results.
