# Experiment: EXP007_BESTSEL_CD_REPRODUCTION

## Objective
Reconstruct the secondary structure deconvolution from circular dichroism (CD) spectra preserved from the experimental validation of ProteinSolver de novo designs:
- Targets: Serum albumin domain 3 (1n5u) and Alanine racemase (4beu)
- Methodology: BeStSel (http://bestsel.elte.hu/) secondary structure composition analysis
- Primary Provenance: Upstream notebook 07_protein_analysis_bestsel.ipynb (Cells 15-24) supporting STAR Protocols Step 19 and Cell Systems Figures 4/5 experimental validation.

## Provenance and Status Classification
- **Status:** RECONSTRUCTION_FROM_PRESERVED_BESTSEL_OUTPUTS
- **Clarification on Figure Attribution:** STAR Protocols 2021 Figure 2B depicts sequence logos generated without pairwise residue interactions, NOT BeStSel deconvolution. BeStSel deconvolution is described in STAR Protocols Step 19 as the method for secondary structure estimation from CD spectra.
- **End-to-End Scope:** This experiment does NOT rerun raw CD spectrometer spectra through the external BeStSel web server; it reconstructs the secondary structure fractions and statistical analyses preserved in author notebook 07.

## Statistical Interpretation & Scientific Rigor
- **1n5u (Serum albumin domain 3, N=3 replicates per group):**
  - Reference Total \alpha-helix: 30.01%
  - Design Total \alpha-helix: 28.79%
  - Two-sample t-test across all 7 secondary structure elements yielded p > 0.05 (minimum p = 0.1599).
  - **Calibrated interpretation:** No statistically significant difference was detected between reference and design secondary structure compositions under the tested conditions. This does not constitute proof of structural equivalence.
- **4beu (Alanine racemase domain 2, N=1 observation per group):**
  - Reference Total \beta-sheet: 32.76%
  - Design Total \beta-sheet: 20.51%
  - **Inferential limitation:** With only a single observation per group, a two-sample t-test is mathematically undefined and cannot be performed. No inferential test was manufactured.