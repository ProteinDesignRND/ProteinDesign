# AI Agent Rules and Lessons

This document records hard-won lessons from the Phase 1 ProteinSolver reproduction. Future AI agents working on this repository MUST read and follow these rules.

---

## Scientific Integrity Rules

### 1. Never trust a successful-looking metric without checking the information flow
The first ProteinSolver run showed "100% sequence recovery." It was actually a label leak: `data.y` contained the native sequence, and `protein_design.py` copied it position-by-position via `strategy="ref"`. Always trace what data the model can see.

### 2. Never call a native sequence result "recovery" if native residues were visible
If the native sequence is supplied anywhere in the input graph (e.g., `data.y`, `data.x`, or via partial masking that leaves native residues exposed), the output is **diagnostic scoring**, not sequence recovery. Valid inverse-folding recovery requires all residues masked.

### 3. Always distinguish these four concepts
- **Diagnostic scoring**: model evaluates probability of known native residues (natives visible)
- **Masked-position recovery**: model predicts only masked positions while some positions remain native (partial masking)
- **All-masked generation**: model designs the entire sequence from scratch with zero native sequence information (the valid inverse-folding test)
- **Generated-sequence identity**: fraction of designed residues matching the native sequence

### 4. Never modify historical source code when an external compatibility adapter is sufficient
The historical ProteinSolver repository (`external/proteinsolver-original`) has ZERO modifications. All six compatibility issues (fcntl, kmtools, scatter_, Batch, key mapping, CPU placement) were resolved via external caller-side adapters. This preserves provenance.

### 5. Never claim historical numerical equivalence without testing it
"FUNCTIONALLY REPRODUCED WITH MODERN COMPATIBILITY ADAPTATION" is the correct claim. "100% mathematical fidelity" would require running the same checkpoint on the original Python 3.6 / PyG 1.3 / Linux stack and comparing outputs numerically. That has not been done.

### 6. Never infer dataset membership from incomplete metadata
The ProteinSolver notebook checked `"1.10.246.10" in cath_ids` → `False`, which is suggestive but NOT definitive. The full 72M training corpus is not in git. Unless you can directly query the training data files, classify membership as "NOT VERIFIABLE FROM ACCESSIBLE METADATA."

### 7. Never call a single target a benchmark
41.30% on 1n5uA03 is a "single-target all-masked inverse-folding integration result." It is NOT benchmark accuracy, generalization performance, or representative of the model's average behavior across protein folds.

### 8. Never choose a target after seeing its result and present it as an unbiased benchmark
1n5uA03 was selected because it was the repository's demo structure, not because of its recovery rate. This is acceptable provenance. But if you later test additional targets, you must declare the full set before running experiments, not cherry-pick after seeing results.

### 9. Always record exact provenance for every experiment
Every experiment must document:
- Commit SHA of the repository
- SHA-256 hashes of input files (checkpoints, PDBs)
- Full environment specification (Python, PyTorch, PyG, GPU, OS)
- Random seed
- Sampling strategy (MAP, multinomial, temperature)
- Target provenance (where the structure came from, whether training membership is known)
- Exact command used to run the experiment

### 10. Preserve historical repository cleanliness
Never commit changes to `external/proteinsolver-original/`. If you need to modify behavior, create an external wrapper. Check `git -C external/proteinsolver-original status` before every commit to the main project.

---

## Engineering Rules

### 11. Use brute force only when the task is cheap and decisive
Don't re-download 72M training records to check one structure's membership. Don't recreate virtual environments when they already exist. Inspect first, act second.

### 12. Prefer smart workarounds for obsolete dependencies when the workaround does not alter scientific semantics
Stubbing `fcntl` and `kmtools` with empty modules is safe because the neural network, design algorithm, and data pipeline have zero functional dependency on them. This is preferable to spending hours rebuilding ancient Cython packages.

### 13. Escalate to brute-force reproduction when the unresolved issue could affect scientific conclusions
If the compatibility issue is in the core computation path (e.g., the scatter aggregation, the edge featurization math, the design loop), a stub is NOT sufficient. You must verify that the workaround produces the same numerical output.

### 14. Never silently reinterpret a failed experiment as a success
If `design_sequence` crashes with an `AttributeError`, that is a FAILURE. Document it, diagnose it, fix it, then re-run. Don't skip the fix and call the crash "expected behavior."

### 15. Use precise evidentiary labels
| Label | Meaning |
| :--- | :--- |
| `[VERIFIED]` | Directly confirmed by inspection, execution, or primary literature |
| `[OBSERVED]` | Empirically observed but not yet explained or reproduced independently |
| `[INFERRED]` | Logical deduction from verified facts, not directly tested |
| `[HYPOTHESIS]` | Untested conjecture requiring experimental falsification |
| `[NOT VERIFIABLE]` | Cannot be determined from accessible data/metadata |
| `[BLOCKED]` | Requires external action, data, or resources not currently available |

### 16. If a result is not comparable to a published metric, do not compare it
41.30% on one CATH domain ≠ the paper's reported ~33% average across 172 test superfamilies. Different targets, different evaluation setup, different denominator.

### 17. Do not repeatedly restart completed work
Before re-cloning, re-creating environments, or re-running experiments, check whether the artifacts already exist. Read logs. Inspect files. Save hours.

### 18. Before executing expensive work, inspect existing artifacts
Check `experiments/*/metrics.json`, `experiments/*/run_log.txt`, environment directories, and cached outputs before launching new computations.

### 19. Every new experiment must have a complete record
Required structure:
```
experiments/EXP_NNN_NAME/
├── README.md          # What this experiment tests
├── config.json        # All parameters
├── run.py             # Executable script
├── input/             # Input files (PDBs, sequences)
├── output/            # Generated outputs
├── metrics.json       # Machine-readable results
├── run_log.txt        # Full stdout/stderr
└── environment.txt    # pip freeze or equivalent
```

### 20. Project identity must never be mixed with another project
This repository is **Protein Design**. It is not Ocean Sentinel or any other project. Do not import architecture, terminology, assumptions, datasets, or decisions from other projects.

### 21. Run governance preflight before experiments
Before starting any experiment or reporting any result, run `python -c "from governance.store import GovernanceStore; from governance.preflight import run_preflight, format_preflight; print(format_preflight(run_preflight(GovernanceStore(), {'pipeline_stage': 'YOUR_STAGE', 'model_family': 'YOUR_MODEL'})))"`. Check MUST rules.

### 22. Fix related issues together in one pass
When you find a problem, search the entire repository for the same pattern. Fix all instances in one coherent pass instead of fixing one and leaving others for future sessions to rediscover.

### 23. Never report a diagnostic as an evaluation
If native residues were visible during inference (e.g., via `data.y`), the output is diagnostic scoring. If you write "sequence recovery" anywhere in a report, verify the setup was truly all-masked.

### 24. Do not create governance complexity without demonstrated need
Every lesson, rule, or check must address a real problem that already happened or is concretely likely. Do not invent governance infrastructure preemptively.

### 25. AI agents may propose lessons but cannot promote them
Submit new lessons as `governance_lifecycle="PROPOSED"`. Only human review can change a lesson to ACTIVE or promote it into a rule. See `governance/ARCHITECTURE.md`.

---

## Error Recovery Rules

### Level 1: Inspect first
Read current files, logs, and git status before doing anything.

### Level 2: Narrow workaround
Use a minimal compatibility shim if scientific semantics are clearly preserved.

### Level 3: Regression test
Run a minimal test to verify the workaround didn't break anything.

### Level 4: Investigate deeply
If the workaround might alter scientific semantics, stop and analyze the computation path.

### Level 5: Full reproduction
Only reconstruct the historical environment when the unresolved issue could materially affect scientific conclusions.

**Maximum recovery attempts for one issue: 3 meaningful attempts.** After 3 failures, document as BLOCKED and continue with independent tasks.

Do not enter an infinite repair loop.

---

## Multi-AI Team Model

This project uses multiple AI systems with distinct roles:

| System | Role | Repository Access |
| :--- | :--- | :--- |
| **Antigravity (Gemini)** | Local execution, repository management, coding, experiment running | READ + WRITE |
| **Perplexity** | Literature search, prior-art verification, source discovery | READ ONLY (external) |
| **Claude** | Independent scientific/technical red-team, methodology review | READ ONLY (review) |
| **ChatGPT** | Research strategy, synthesis, hypothesis/experiment design | READ ONLY (advisory) |
| **OpenRouter** | Optional independent second opinion when needed | READ ONLY (advisory) |

### Critical Rules

1. **One system modifies the repository at a time.** Concurrent writes from multiple AI agents are forbidden.
2. **Gemini inside Antigravity is NOT an independent reviewer.** It is the executor. Independent review comes from Claude, ChatGPT, or Perplexity.
3. **Do not duplicate all work across AI systems.** Each system has a specific role. Use the right tool for the right task.
4. **Independent AI systems challenge conclusions.** The executor proposes; the reviewers critique.

---

## Durable Principles (Permanent Governance Memory)

1. **Unit-tested != Integrated**: A requirement is not integrated simply because a unit test passes. Production workflows (e.g. experiment runners, reporting pipelines) must actively invoke the governance checks.
2. **Documented != Enforced**: Writing a rule or policy in markdown does not enforce it. Rules require explicit machine evaluation (`run_preflight`, `verify_integrity`, `evaluate_claim`) or automated checks.
3. **Diagnostic != Evaluation**: When native residues are visible to the model (e.g. via `data.y` or partial masks), the run is a diagnostic score, NOT sequence recovery. Valid inverse-folding recovery strictly requires all positions masked (`data.x = 20`, `data.y = None`).
4. **One Target != Benchmark**: A result on a single structure (such as 41.30% on 1n5uA03) is a single-target integration result. It must never be described as benchmark performance, generalization, or fold-representative.
5. **Unknown Membership != Held-Out**: When training corpus data cannot be directly queried, membership is "NOT VERIFIABLE FROM ACCESSIBLE METADATA". Never describe a target as "held-out" or "unseen" without direct corpus proof.
6. **Modern Compatibility != Historical Equivalence**: Functional reproduction on a modern Python/PyTorch stack does not prove numerical equivalence to historical Linux/PyG 1.3 runs. Always claim "FUNCTIONALLY REPRODUCED WITH MODERN COMPATIBILITY ADAPTATION".
7. **Detected != Prevented (Direct-File Mutation)**: Directly editing JSON files (`lessons.json`, `rules.json`) bypasses store API logic. The store maintains repository-level integrity validation (`store.verify_integrity()`) to DETECT unauthorized mutations, deleted safety rules, or improper escalations at preflight and test time. However, application-level Python code does not physically PREVENT raw filesystem writes; the repository relies on integrity detection and verification, not illusory physical write prevention.
8. **AI Cannot Self-Promote**: AI agents may propose lessons and surface conflicts, but can NEVER autonomously promote lessons to ACTIVE rules, escalate priority (SHOULD -> MUST), or override blockers.
9. **Unknown Context Must Be Visible**: Incomplete context must never silently mean "no rules apply". Missing context dimensions and novel context values must be surfaced visibly as review warnings.
10. **Negative Validation Matters**: A failed check or contradicted hypothesis is essential project knowledge. Negative validation events (`RULE_FAILED`, `LESSON_CONTRADICTED`) must be preserved in the append-only event log.
11. **Recurring Failures Must Update Existing Knowledge**: When a known failure repeats, link it to the existing lesson or rule (`find_potential_duplicates`), update its recurrence record, or supersede it—do not create disconnected duplicate lessons.
