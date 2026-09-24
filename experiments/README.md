# EXPERIMENTS DIRECTORY

This directory houses all experimental configurations, execution scripts, run logs, and intermediate checkpoints for the empirical evaluations (E0 through E5).

---

## Directory Organization

```
experiments/
├── configs/             # YAML / JSON configuration files for each experiment
│   ├── e0_proteinsolver.yaml
│   ├── e1_proteinmpnn.yaml
│   ├── e2_fusion.yaml
│   ├── e3_validation.yaml
│   ├── e4_selection.yaml
│   └── e5_ablations.yaml
├── scripts/             # Lightweight runner scripts (to be created in Phase 1)
│   ├── run_e0_baseline.py
│   ├── run_e1_proteinmpnn.py
│   ├── run_e2_hybrid.py
│   ├── run_e3_validate.py
│   └── run_e4_select.py
├── targets/             # Benchmark PDB coordinate files (TS50 / CATH 4.2 subset)
│   └── target_manifest.json
└── logs/                # Timestamped execution logs, stdout/stderr, and run metadata
```

---

## Reproducibility Standards

1. **Deterministic Execution:** Every run script must set fixed seeds across PyTorch (`torch.manual_seed`), NumPy (`np.random.seed`), and Python (`random.seed`).
2. **Environment Metadata:** Every log file must record Python version, PyTorch version, CUDA version (if applicable), and GPU device name.
3. **No Overwrites:** Outputs from individual experimental runs must be written to unique timestamped subdirectories under `evaluation/results/`.
