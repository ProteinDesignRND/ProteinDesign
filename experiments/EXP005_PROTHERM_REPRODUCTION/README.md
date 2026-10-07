# Experiment: EXP005_PROTHERM_REPRODUCTION

## Objective
Reconstruct the ProTherm single-point mutation $\Delta\Delta G$ stability correlation published in *Cell Systems* 2020 **Figure 2D** ($N=3,471$ mutations).

## Scientific & Provenance Clarification (R1.2)
1. **Metric Definition:** The published statistic is **Spearman's rank correlation ($\rho$)**, NOT Pearson's $R$.
2. **Figure Mapping:** Figure 2D is the ProTherm correlation panel ($\rho = 0.444$). The $\rho = 0.551$ value represents an internal exploratory subset of mutations lacking close homologs from Notebook `07_protein_analysis_figures.ipynb` Cell 72, **NOT Figure 2E**.
3. **Data Recomputation vs. Preservation:**
   - **Rosetta Baseline:** `RAW_DATA_RECOMPUTED`. Recomputed from raw energies in `input/protherm_design_wt_RUE.csv` using 10,000 bootstrap iterations: Spearman $\rho = -0.0080$, $p = 0.638$, 90% CI $[-0.0360, 0.0200]$.
   - **ProteinSolver Score:** `RECONSTRUCTION_FROM_PRESERVED_NOTEBOOK_STATISTICS`. The per-mutation raw network score tensor (`protherm_wresults.torch`) is not bundled in the upstream repository. The ProteinSolver Spearman $\rho = 0.444$ ($p = 1.78 \times 10^{-167}$, 90% CI $[0.419, 0.468]$) is reconstructed from upstream notebook outputs.

## Environment
- Python 3.11.9, Scipy 1.15.2, Pandas 2.2.3, NumPy 2.2.3

## How to Run
```powershell
.\environment\proteinsolver-original\Scripts\python.exe experiments\EXP005_PROTHERM_REPRODUCTION\run.py
```

## Status
COMPLETE (Reconstruction & Raw Recomputation Documented)
