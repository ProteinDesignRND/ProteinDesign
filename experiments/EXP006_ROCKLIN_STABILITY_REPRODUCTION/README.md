# Experiment: EXP006_ROCKLIN_STABILITY_REPRODUCTION

## Objective
Reconstruct the miniprotein protease stability score correlations across four de novo topologies published in *Cell Systems* 2020 Figure 2F:
1. \alpha\alpha\alpha (HHH)
2. \alpha\beta\beta\alpha (HEEH)
3. \beta\alpha\beta\beta (EHEE)
4. \beta\beta\alpha\beta\beta (EEHEE)

## Provenance and Status Classification
- **Status:** RECONSTRUCTION_FROM_PRESERVED_NOTEBOOK_STATISTICS
- **Cell Systems Paper Mapping:** Figure 2F (Whole-protein stability scores of Rosetta-designed proteins across four geometries and selection rounds).
- **Note on Figure 2E vs 2F:** Figure 2E displays the Rocklin mutation-stability dataset (N=9,912). Figure 2F displays the de novo whole-protein stability correlations across rounds 1-4.
- **Data Availability:** Raw per-design network score tensors (stability_scores_for_selections.*.torch) were not tracked in the upstream git repository. The statistics are reconstructed faithfully from author Notebook 06 (Cell 53) and Notebook 07 (Cell 102).

## Scientific Observations & EEHEE Round 4 Exception
- **Topology Correlations (Round 4):**
  - \alpha\alpha\alpha (HHH): Spearman \rho = 0.422
  - \alpha\beta\beta\alpha (HEEH): Spearman \rho = 0.313
  - \beta\alpha\beta\beta (EHEE): Spearman \rho = 0.245
  - \beta\beta\alpha\beta\beta (EEHEE): Spearman \rho = -0.142 (negative correlation)
- **Baseline Comparison & Critical Correction:**
  - ProteinSolver network score significantly correlates with protease stability in HHH, HEEH, and EHEE topologies.
  - However, in EEHEE Round 4, both methods exhibit negative correlations: Rosetta talaris2013 \rho \approx -0.401 and ProteinSolver \rho \approx -0.142.
  - Therefore, claims of universal method superiority or that ProteinSolver consistently exceeds Rosetta across all rounds are scientifically incorrect and have been removed.