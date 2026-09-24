# Experiment: [EXP_NNN_NAME]

## Objective
[What scientific question does this experiment answer?]

## Input Provenance
- **Target Structure(s):** [PDB ID, chain, domain, source]
- **Model Checkpoint:** [Path, SHA-256 hash]
- **Training Set Membership:** [VERIFIED / NOT VERIFIABLE / NOT APPLICABLE]

## Environment
- **Python:** [version]
- **PyTorch:** [version]
- **Key packages:** [list with versions]
- **Hardware:** [GPU model, CPU, RAM]
- **OS:** [OS version]

## Configuration
See `config.json` for all parameters.

Key parameters:
- **Seed:** [random seed]
- **Sampling Strategy:** [MAP / multinomial / other]
- **Temperature:** [if applicable]
- **Mask Fraction:** [if applicable]

## How to Run
```powershell
.\environment\proteinsolver-original\Scripts\python.exe experiments\EXP_NNN_NAME\run.py
```

## Result
[Fill in after running]

## Controls
[What comparisons or controls validate this result?]

## Limitations
[What does this experiment NOT tell us?]

## Interpretation
[What can we conclude from this result?]

## Reproducibility
- [ ] `config.json` contains all parameters
- [ ] `run.py` is self-contained and executable
- [ ] `metrics.json` contains machine-readable results
- [ ] `run_log.txt` contains full stdout/stderr
- [ ] `environment.txt` contains `pip freeze` output
- [ ] Random seed is fixed and documented

## Status
[PLANNED / RUNNING / COMPLETE / FAILED / BLOCKED]
