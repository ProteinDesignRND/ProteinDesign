# Team Workstreams

These are starting boundaries for dividing work. They are not immutable. If your work naturally crosses into another workstream, coordinate with the owner of that workstream and document the shared interface before making cross-workstream changes.

---

## Workstream A — Research Lead / Integration

**Owner:** Project lead

**Responsibilities:**
- Overall research direction and hypothesis management
- Cross-workstream integration and conflict resolution
- Final experimental design approval
- Paper writing and figure generation
- Repository governance and merge decisions

**Current state:**
- ProteinSolver baseline verified (41.30% on 1n5uA03)
- Literature audit complete (initial pass)
- Research question formulated (two-sided)
- Foundation documents established

**Next steps:**
- Review and approve team workstream plans
- Define the multi-target benchmark set (CATH 4.2 test targets)
- Coordinate ProteinMPNN integration with Workstream B
- Define the complementarity analysis protocol

---

## Workstream B — Modern Inverse-Folding Baselines

**Owner:** Team member (TBD)

**Responsibilities:**
- Clone and set up the official ProteinMPNN repository
- Verify ProteinMPNN runs locally on the same targets as ProteinSolver
- Run ProteinMPNN baseline on shared benchmark targets
- Document ProteinMPNN's input/output format, sampling parameters, and runtime
- Produce comparable metrics (native sequence recovery, perplexity, runtime)

**Current state:**
- NOT STARTED

**Next steps:**
- Clone `https://github.com/dauparas/ProteinMPNN`
- Set up environment (may need a separate venv)
- Run inference on 1n5uA03 for initial comparison
- Create `experiments/EXP010_PROTEINMPNN_BASELINE/`

**Shared interfaces:**
- Benchmark target list (defined by Workstream A)
- Output format: designed sequences as FASTA + `metrics.json`
- PDB input format: same structures used by ProteinSolver baseline

**Future experiment stubs:**
```
experiments/EXP010_PROTEINMPNN_BASELINE/
experiments/EXP011_PROTEINMPNN_MULTI_TARGET/
```

---

## Workstream C — Structural Validation

**Owner:** Team member (TBD)

**Responsibilities:**
- Set up structural prediction tools (ESMFold or AlphaFold2/ColabFold)
- Implement self-consistency evaluation: fold designed sequences and compare to input backbone
- Compute scRMSD (self-consistency RMSD) and scTM (self-consistency TM-score)
- Compute pLDDT confidence for designed sequences
- Validate that designed sequences are physically plausible

**Current state:**
- NOT STARTED

**Next steps:**
- Evaluate ESMFold vs. AlphaFold2 for local self-consistency computation
- Define the structural validation pipeline
- Run validation on existing ProteinSolver-designed sequences from EXP000

**Shared interfaces:**
- Input: designed sequences (FASTA) from Workstreams B and D
- Output: scRMSD, scTM, pLDDT per sequence in `metrics.json`
- Reference backbone: original PDB files from `experiments/*/input/`

---

## Workstream D — Candidate Selection / Multi-Objective Analysis

**Owner:** Team member (TBD)

**Responsibilities:**
- Implement multi-objective candidate ranking (Pareto front analysis)
- Define the objective axes: recovery, structural fidelity, sequence diversity
- Implement pairwise sequence diversity computation
- Test whether ProteinSolver scores add orthogonal information to ProteinMPNN scores
- Evaluate hybrid selection strategies

**Current state:**
- NOT STARTED (depends on Workstreams B and C producing comparable outputs)

**Next steps:**
- Define the candidate scoring framework
- Implement Pareto front computation
- Design the complementarity analysis protocol

**Shared interfaces:**
- Input: per-sequence scores from Workstreams B (ProteinMPNN confidence) and C (structural validation)
- Input: ProteinSolver log-likelihoods from the baseline
- Output: ranked candidate lists, Pareto front plots, diversity metrics

**Future experiment stubs:**
```
experiments/EXP012_COMPLEMENTARITY/
experiments/EXP013_HYBRID_SELECTION/
```

---

## Workstream E — Evaluation / Statistics / Visualization

**Owner:** Team member (TBD)

**Responsibilities:**
- Implement standardized evaluation metrics across all experiments
- Compute statistical significance tests (paired tests, bootstrap CIs)
- Create publication-quality figures and tables
- Audit for length-dependent biases, batch effects, and confounding variables
- Maintain the evaluation protocol document

**Current state:**
- Evaluation protocol outlined in `science/evaluation_protocol.md`
- Basic metrics defined (AAR, perplexity, scRMSD, scTM, diversity)

**Next steps:**
- Implement the metrics computation library
- Create visualization templates (sequence recovery plots, Pareto front plots)
- Define the statistical analysis plan

**Shared interfaces:**
- Input: `metrics.json` files from all experiment directories
- Output: summary tables, figures, statistical test results

---

## Cross-Workstream Rules

1. **Document shared interfaces before making cross-workstream changes.** If Workstream B changes the output format of ProteinMPNN results, Workstreams D and E need to know.

2. **Use `experiments/` for all experimental work.** Don't scatter results across random directories.

3. **Don't modify `external/proteinsolver-original/`.** All compatibility work goes in external wrappers.

4. **All experiments must follow the template in `experiments/TEMPLATE/`.** This ensures reproducibility and comparability.

5. **Coordinate with the research lead before starting new experiments.** The lead maintains the experiment numbering scheme and overall research direction.
