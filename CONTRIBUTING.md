# Contributing to Protein Design

## Branch Structure

| Branch Pattern | Purpose | Example |
| :--- | :--- | :--- |
| `main` | Stable integration branch | — |
| `feature/<name>` | New capabilities or infrastructure | `feature/proteinmpnn-baseline` |
| `experiment/<id>` | Experimental runs and analysis | `experiment/exp010-proteinmpnn-1n5u` |
| `research/<topic>` | Research investigations | `research/training-set-audit` |
| `fix/<issue>` | Bug fixes and corrections | `fix/scatter-compatibility` |
| `foundation/<version>` | Historical milestone branches | `foundation/team-handoff-v0.1` |
| `governance/<task>` | Governance development and release branches | `governance/final-acceptance-redteam-v1` |
| `research/ai-research-bootstrap` | Historical bootstrap branch | — |

## Commit Messages

Use conventional commit format:

```
feat: add ProteinMPNN baseline experiment
fix: correct edge featurization normalization constant
docs: update team onboarding with new environment instructions
experiment: EXP010 ProteinMPNN baseline on 1n5uA03
refactor: extract shared graph construction utilities
```

## Pull Request Requirements

1. **Clear description** of what changed and why.
2. **Experiment PRs** must include complete `metrics.json` and `run_log.txt`.
3. **No force-pushing.** History must be preserved.
4. **No direct pushes** to the `main` branch without review.
5. **Governance preflight**: Before running experiments or reporting, evaluate governance rules:
   ```powershell
   .\environment\proteinsolver-original\Scripts\python.exe governance/preflight_cli.py --stage evaluation
   ```
6. **Regression check**: verify all tests pass:
   ```powershell
   uv run --python environment/proteinsolver-original/Scripts/python.exe pytest tests/
   .\environment\proteinsolver-original\Scripts\python.exe test_original_execution.py
   ```

## Experiment Reproducibility Requirements

Every experiment directory must contain:

```
experiments/EXP_NNN_NAME/
├── README.md          # What, why, expected outcome
├── config.json        # All parameters
├── run.py             # Executable script
├── input/             # Input files
├── output/            # Generated outputs
├── metrics.json       # Machine-readable results
├── run_log.txt        # Full stdout/stderr
└── environment.txt    # pip freeze
```

Copy `experiments/TEMPLATE/` to create new experiments. Use sequential numbering (EXP000, EXP001, ..., EXP010, EXP011, ...).

## What NOT to Do

- **Do NOT modify files inside `external/proteinsolver-original/`.** This is a historical archive. All compatibility work goes in external wrappers.
- **Do NOT commit large generated artifacts** (model checkpoints, large PDB files, Parquet datasets) without discussing with the project lead. Use `.gitignore` for generated outputs.
- **Do NOT commit virtual environments** (`environment/`) or `__pycache__/` directories.
- **Do NOT force-push** any branch.
- **Do NOT change the baseline verification suite** (`test_original_execution.py`) without running a full regression test and documenting the reason in the PR.

## Review Process

- All PRs should be reviewed by at least one team member.
- The project lead has final merge authority.
- For cross-workstream changes (see `docs/TEAM_WORKSTREAMS.md`), get acknowledgment from the affected workstream owner.

## Code Style

- Python: follow standard PEP 8.
- Markdown: use consistent heading levels and table formatting.
- JSON configs: use 2-space indentation.
- File paths: use forward slashes in documentation, even on Windows.

## Getting Help

- Read `docs/TEAM_ONBOARDING.md` first.
- Check `docs/PROJECT_TRUTH.md` for verified facts vs. hypotheses.
- Check `docs/AI_AGENT_RULES_AND_LESSONS.md` for common pitfalls.
- If blocked, document the blocker in your branch and notify the project lead.
