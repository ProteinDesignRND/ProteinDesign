# Team Onboarding

Welcome to the Protein Design research project. This document gives you everything you need to understand the repo, the science, and how to contribute — without needing to talk to the project lead first.

---

## 1. What the project is

This is a computational biology research project investigating whether an older protein sequence design model (ProteinSolver, 2020) can complement modern state-of-the-art models (ProteinMPNN, 2022) to produce better or more diverse protein sequences.

We are NOT building a product. We are conducting a controlled scientific investigation.

## 2. The problem we are solving

**Inverse folding** = given a 3D protein backbone, design an amino acid sequence that folds into that shape.

Modern models like ProteinMPNN do this well (~51% native sequence recovery on standard benchmarks), but they tend to produce narrow, low-diversity sequence pools. If we could intelligently combine signals from different models, we might get better quality-diversity trade-offs.

## 3. Why ProteinSolver matters

ProteinSolver (Strokach et al., Cell Systems 2020) is a graph neural network that treats sequence design as a constraint satisfaction problem (CSP). It uses a different architecture and different input features than ProteinMPNN:

- **ProteinSolver**: pairwise heavy-atom distances (< 12 Å), masked-token BERT-style prediction, iterative unmasking
- **ProteinMPNN**: backbone atom coordinates (N, CA, C, O), autoregressive left-to-right prediction with random order

These differences mean their errors might be uncorrelated — which is the hypothesis we're testing.

## 4. Current research question

> *"Does ProteinSolver's distance-graph constraint-satisfaction scoring provide orthogonal structural signal that improves modern inverse-folding candidate selection, or does modern inverse folding combined with structural validation dominate hybrid selection?"*

This is a **two-sided question**, not an assumption that ProteinSolver helps. It might hurt.

## 5. Current hypothesis (UNTESTED)

Combining ProteinSolver scores with ProteinMPNN outputs through multi-objective candidate selection might improve the quality-diversity trade-off. This has NOT been tested yet.

## 6. What has already been established

- ProteinSolver's historical source code has been cloned and verified (commit `69ef0965`). The working tree is 100% clean.
- The published 567,060-parameter checkpoint loads correctly under `strict=True` after a documented key prefix mapping.
- On one test structure (CATH domain 1n5uA03, 92 amino acids), ProteinSolver's all-masked CSP design achieves 41.30% native sequence identity (38/92 residues).
- The model is 100% mask-invariant: hidden labels have zero effect on logits when all residues are masked.
- An earlier "100% recovery" result was correctly identified as an information leak bug in the evaluation setup (not a model bug).
- A cleanroom Biopython-based graph extractor produces tensors identical to the original repo pipeline on the tested target.

## 7. What has NOT been established

- Whether ProteinSolver actually complements ProteinMPNN (the main research question)
- ProteinMPNN baseline performance (not yet integrated)
- Multi-target benchmark evaluation
- Historical runtime numerical equivalence (original Python 3.6 / PyG 1.3 environment)
- General kmbio/Biopython parser equivalence across diverse PDB structures
- Training set membership of 1n5uA03 in the 72M training corpus
- Statistical significance of any comparison

## 8. Current baseline

ProteinSolver, one target, CPU inference, 41.30% recovery, deterministic. This is an **integration result**, not a benchmark.

## 9. Repository map

```
Protein Design/
├── docs/                          # Project documentation (you are here)
│   ├── PROJECT_TRUTH.md          # Single source of truth
│   ├── TEAM_ONBOARDING.md        # This file
│   ├── TEAM_WORKSTREAMS.md       # Who works on what
│   └── AI_AGENT_RULES_AND_LESSONS.md  # Rules for AI agents
├── external/
│   └── proteinsolver-original/    # Historical repo (DO NOT MODIFY)
├── environment/
│   └── proteinsolver-original/    # Python virtualenv
├── src/
│   └── proteinsolver_baseline/    # Cleanroom ProteinSolver wrapper
│       ├── model.py              # Reconstructed ProteinNet
│       ├── graph.py              # Biopython-based graph extractor
│       └── sampler.py            # CSP sampling utilities
├── experiments/
│   ├── TEMPLATE/                  # Copy this for new experiments
│   ├── EXP000_PROTEINSOLVER_SMOKETEST/
│   ├── EXP001_PROTEINSOLVER_INFERENCE/
│   └── EXP004_MASK_INVARIANCE/
├── reports/                       # Analysis reports and audit documents
├── research/                      # Literature review and paper audits
├── science/                       # Evaluation protocol, datasets docs
├── architecture/                  # Architecture documentation
├── CLAIMS_REGISTRY.md            # Formal claim tracking
├── DECISION_LOG.md               # Decision history
├── PROJECT_STATE.md              # Current project state
├── CONTRIBUTING.md               # Git and contribution rules
├── test_original_execution.py    # Phase 1 verification suite
└── 1UBQ.pdb                      # Test PDB file
```

## 10. Environment setup

The Python environment already exists at `environment/proteinsolver-original/`. To use it:

```powershell
# Activate the environment
.\environment\proteinsolver-original\Scripts\Activate.ps1

# Verify it works
python -c "import torch; import torch_geometric; print('OK')"
```

Key packages: Python 3.11.9, PyTorch 2.6.0+cu124, PyG 2.8.0.post1, BioPython 1.88.

If you need to recreate it (only if broken):
```powershell
python -m venv environment/proteinsolver-original
.\environment\proteinsolver-original\Scripts\Activate.ps1
pip install torch torch_geometric torch_scatter biopython scipy
```

## 11. How to run the verified baseline

```powershell
# Run the full verification suite
.\environment\proteinsolver-original\Scripts\python.exe test_original_execution.py

# Run just the mask invariance audit
.\environment\proteinsolver-original\Scripts\python.exe experiments\EXP004_MASK_INVARIANCE\run_mask_invariance.py
```

Expected output for the baseline: 41.30% native sequence recovery on 1n5uA03 (38/92 residues).

## 12. Experiment conventions

Every experiment lives in `experiments/EXP_NNN_DESCRIPTIVE_NAME/` and must contain:

| File | Purpose |
| :--- | :--- |
| `README.md` | What this experiment tests, why, expected outcome |
| `config.json` | All parameters (target, seed, temperature, etc.) |
| `run.py` | The executable script |
| `input/` | Input files (PDB structures, sequences) |
| `output/` | Generated outputs |
| `metrics.json` | Machine-readable results |
| `run_log.txt` | Full stdout/stderr capture |
| `environment.txt` | `pip freeze` or equivalent |

Copy `experiments/TEMPLATE/` to start a new experiment.

## 13. How to record results

- Always save `metrics.json` with quantitative results.
- Always capture `run_log.txt` with full output.
- Record your Python environment in `environment.txt`.
- If results change from previous runs, investigate before overwriting.

## 14. Git workflow

- **Main branch**: `research/ai-research-bootstrap` (current working branch)
- **Feature branches**: `feature/<descriptive-name>` for new capabilities
- **Experiment branches**: `experiment/<exp-id>` for experimental runs
- **Fix branches**: `fix/<issue-description>` for bug fixes
- See `CONTRIBUTING.md` for full details.

## 15. Branch naming

```
feature/proteinmpnn-baseline
experiment/exp010-proteinmpnn-cath42
fix/scatter-compatibility
research/training-set-audit
```

## 16. Pull request expectations

- Every PR needs a clear description of what changed and why.
- Experiments must include complete results (metrics.json, run_log.txt).
- No force-pushing. No direct pushes to the main branch.
- If you modify compatibility shims, verify the baseline still passes.

## 17. What files should NOT be modified casually

| File/Directory | Why |
| :--- | :--- |
| `external/proteinsolver-original/` | Historical repo. NEVER modify. |
| `CLAIMS_REGISTRY.md` | Formal evidentiary tracking. Discuss changes with lead. |
| `docs/PROJECT_TRUTH.md` | Single source of truth. Changes require evidence. |
| `test_original_execution.py` | Baseline verification suite. Modifications need regression testing. |

## 18. Known pitfalls

1. **The 100% recovery trap**: If you supply native residues to `data.y`, `design_sequence` copies them back. This is NOT sequence recovery. Always use `data.x = 20` (mask) and `data.y = None`.
2. **PyG Data.batch**: In PyG 2.x, `Data.batch` defaults to `None`. You must wrap with `Batch.from_data_list([data])` before calling `design_sequence`.
3. **CUDA design loop**: The iterative CSP design crashes on CUDA under PyTorch 2.6 due to a CPU-default `torch.arange`. Run design on CPU.
4. **Checkpoint key names**: The checkpoint uses different layer names than the packaged class. The mapping is documented in the provenance manifest.

## 19. Current workstreams

See `docs/TEAM_WORKSTREAMS.md` for the full breakdown. Summary:
- **A**: Research lead / integration (project lead)
- **B**: Modern inverse-folding baselines (ProteinMPNN integration)
- **C**: Structural validation (AlphaFold/ESMFold self-consistency)
- **D**: Candidate selection / multi-objective analysis
- **E**: Evaluation / statistics / visualization

## 20. How to hand work back to the lead

1. Push your branch to the remote.
2. Create a PR with a clear description.
3. Include: what you did, what worked, what failed, what's left.
4. If you're blocked, document exactly what's blocking you in your PR description.
5. Don't merge your own PRs without review.
