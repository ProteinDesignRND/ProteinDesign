# Experiment: EXP008_FOUR_TARGET_INTEGRATION_FIXTURE

## Objective
Verify the end-to-end all-masked inverse folding design pipeline on all four primary target folds from *Cell Systems* 2020 Figure 3 using the exact historical PDB inputs and chain definitions:
1. 1n5uA03 (PDB: 1n5uA03.pdb, Chain A, 92 residues, all-\alpha)
2. 4beuA02 (PDB: 4beuA02.pdb, Chain A, 217 residues, \alpha/\beta)
3. 4unuA00 (PDB: 4unuA00.pdb, Chain A, 109 residues, Rossmann fold)
4. 4z8jA00 (PDB: 4z8jA00.pdb, Chain A, 96 residues, two-layer \alpha/\beta sandwich)

## Target Definition Provenance
- Target PDB input files are located in xternal/proteinsolver-original/proteinsolver/data/inputs/ and xternal/proteinsolver-original/notebooks/protein_demo/inputs/.
- In author notebook 10_generate_protein_sequences.ipynb (Cell 29), the reference sequence for 4beuA02 is explicitly printed as:
  217 LGQFQSNIEQFKSHMNANTKICAIMKADAYGNGIRGLMPTIIAQGIPCVGVASNAEARAVRESGFKGELIRVRSASLSEMSSALDLNIEELIGTHQQALDLAELAKQSGKTLKVHIALNDGGMGRNGIDMTTEAGKKEAVSIATQPSLSVVGIMTHFPNYNADEVRAKLAQFKESSTWLMQQANLKREEITLHVANSYTALNVPEAQLDMVRPGGVL
  confirming that the exact historical target length is **217 residues** (previous reports claiming 130 AA were in error).
- 1n5uA03.pdb contains 92 residues (Chain A).
- 4unuA00.pdb contains 109 residues (Chain A).
- 4z8jA00.pdb contains 96 residues (Chain A).

## Candidate Generation Feasibility & Scope Boundary
- **Status Classification:** INTEGRATION_FIXTURE_VERIFIED.
- **Large-Scale Generation Decision:** Strokach et al. generated **over 600,000 sequences for each fold** (>2,400,000 sequences total) across an academic SLURM compute cluster. The full 2.4-million sequence candidate libraries are not tracked in the upstream repository.
- **Cost Classification:** REGENERATION_REQUIRED_BUT_EXPENSIVE.
- **Cost Note:** Exact current regeneration cost is **unbenchmarked**. Previous R1.1 claims of 67 to 1,113 GPU-hours were unmeasured extrapolations and are NOT retained as measured facts.
- **Fixture Role:** In strict adherence to project governance, million-sequence campaigns were NOT launched. Instead, this integration fixture executes 1 sequence per target fold to verify multi-target featurization, graph construction, deterministic MAP inference, and ProtParam validation without computational waste.

## Results Summary
All four target folds successfully featurize, load into ProteinNet, and generate de novo sequences:
- 1n5uA03: 92 AA, 41.30% recovery in 1.70 s
- 4beuA02: 217 AA, 41.94% recovery in 7.99 s
- 4unuA00: 109 AA, 43.12% recovery in 1.92 s
- 4z8jA00: 96 AA, 46.88% recovery in 1.44 s