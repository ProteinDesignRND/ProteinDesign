# EVALUATION & RESULTS DIRECTORY

This directory contains evaluation scripts, statistical analysis notebooks, raw candidate evaluation logs, and aggregated performance summaries.

---

## Directory Organization

```
evaluation/
├── scripts/             # Metric computation scripts
│   ├── compute_recovery.py       # Computes AAR and perplexity
│   ├── compute_scrmsd.py         # Runs TM-align / Kabsch RMSD against target backbones
│   ├── compute_diversity.py      # Computes pairwise sequence edit distance / BLOSUM
│   └── compute_pareto.py         # Computes non-dominated fronts and hypervolume
├── results/             # Raw tabular outputs from experiments (CSV/Parquet)
│   ├── e0_proteinsolver/
│   ├── e1_proteinmpnn/
│   ├── e2_fusion/
│   ├── e3_validation/
│   ├── e4_selection/
│   └── e5_ablations/
└── summaries/           # Aggregated tables and figures for reporting
    ├── main_benchmark_table.csv
    └── figures/
```

---

## Analysis Protocol

- **Statistical Significance:** All comparative claims between E0, E1, and E2–E4 must report p-values from two-tailed Wilcoxon signed-rank tests across test targets.
- **Reporting Uncertainty:** Point estimates (mean recovery, mean scRMSD) must be accompanied by 95% bootstrap confidence intervals ($B=1000$).
- **Impartial Reporting:** If the hybrid system or ProteinSolver exhibits inferior metrics, document the negative result with full statistical fidelity.
