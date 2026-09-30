# PROTEINSOLVER: MASTER PAPER REPRODUCTION FORENSIC AUDIT & ZERO-WASTE ROADMAP (PHASE R1.1)

**Document Status:** AUTHORITATIVE RESEARCH AUDIT & EXECUTION ROADMAP (CORRECTED R1.1)  
**Date:** 2026-09-30  
**Audit Lead:** Lead Scientific Reproducibility Engineer & Research Auditor  
**Primary Reference:** Strokach et al., *"Fast and Flexible Protein Design Using Deep Graph Neural Networks"*, *Cell Systems* 11(4): 402–411.e4 (October 21, 2020). DOI: [10.1016/j.cels.2020.08.016](https://doi.org/10.1016/j.cels.2020.08.016). PMID: [32971019](https://pubmed.ncbi.nlm.nih.gov/32971019/).  
**Official Protocol Reference:** Strokach et al., *"Computational generation of proteins with predetermined three-dimensional shapes using ProteinSolver"*, *STAR Protocols* 2(2): 100505 (June 18, 2021). DOI: [10.1016/j.xpro.2021.100505](https://doi.org/10.1016/j.xpro.2021.100505). PMCID: [PMC8102803](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8102803/). PMID: [33997819](https://pubmed.ncbi.nlm.nih.gov/33997819/).  
**Evaluated Repository (Historical Immutable):** `external/proteinsolver-original` (Git commit `69ef0965a3fc3bf191804035b539720a06e58ba6`, clean working tree).  
**Evaluated Modern Implementation:** `D:\Projects\ProteinSolver` (Git commit `58255bc67323f5fd009ac85ae02fbf69c152c457`, clean working tree, UNMODIFIED during this audit).  
**Audit Verification Environment:** Python 3.11.9, PyTorch 2.6.0+cu124, PyG 2.8.0.post1, BioPython 1.88, NVIDIA GeForce RTX 3050 6GB Laptop GPU.  

---

## 1. Executive Summary & Forensic Determination

This audit provides the single, authoritative reconciliation across the original *Cell Systems* paper, its *STAR Protocols* companion, the official upstream repository (`ostrokach/proteinsolver`), all historical AI reports (Antigravity, Claude, Perplexity), and our verified local implementations.

### Key Forensic Determinations (Calibrated R1.1)

1. **What the Original Work Implemented:**
   - **Architecture:** A 4-block residual Edge-Convolutional Graph Neural Network (`ProteinNet`) with 128-dimensional hidden node/edge embeddings, totaling exactly **567,060 parameters** (NOT 1.5M).
   - **Featurization:** Residues as nodes (20 standard AA + 1 mask token `'-'`); edges defined by heavy-atom pairwise distance $< 12.0\text{ \AA}$; 2-channel normalized edge feature vector using **scalar linear normalization**:
     $$d_{\text{norm}} = \frac{d - 6.0}{12.0}, \quad \Delta_{\text{norm}} = \frac{|j-i| - 0.0}{68.1319}$$
     (defined in `proteinsolver/datasets/protein.py` lines 168–182 as `normalize_cart_distances` and `normalize_seq_distances`).
   - **Pretrained Checkpoint:** The author published `e53-s1952148-d93703104.state` (epoch 53, step 1,952,148; run `191f05de`; SHA-256: `1E8272F05EC19041394568C949BBDBF012EE72C1595BE7157C4BB0324D0B5727`).
   - **Scope of Pretrained Checkpoint:** **The published checkpoint is the relevant pretrained model artifact used for downstream inference, sequence generation, sequence scoring, and design analyses. It does not reproduce the historical training trajectory itself.**
   - **Retraining Requirement:** **ZERO retrained models are required** to reproduce downstream inference, sequence generation, profile recovery, ProTherm mutation correlations, Rocklin miniprotein stability scoring, or downstream structural evaluation. Retraining would be required *only* if attempting to reconstruct the historical epoch 0–52 training loss trajectory (Figure 2A). Because the original training logs and exact multi-GPU cluster states are unavailable, and under project governance Decision [DEC-004], full model retraining is **NOT PERFORMED**.

2. **Current Reproduction Baseline:**
   - **Level 1 (Software/Engineering Reproduction):** **Core ProteinSolver software/inference path functionally reproduced with modern compatibility adaptation.** The original `ProteinNet` instantiates, loads official weights under `strict=True` (0 missing, 0 unexpected keys), and executes all-masked CSP inverse folding deterministically.
   - **1n5uA03 Integration Fixture:** On target structure 1n5uA03 (92 AA), valid all-masked inverse folding (MAP, seed 42) achieves **41.30% native sequence identity** (38/92 residues) in **1.67 seconds**.
   - **Full Test Suite:** 81/81 unit/integration tests passing across four test modules. Clean governance preflight.

3. **Figure Mapping Realignment (Cell Systems vs. Protocol vs. Notebooks):**
   - The final *Cell Systems* paper establishes ProTherm and Rocklin stability correlations in **Figure 2D–F** (NOT Figure 3).
   - Figure 3 in *Cell Systems* establishes de novo sequence design for four target folds (1n5uA03, 4beuA02, 4unuA00, 4z8jA00).
   - Figure 4 in *Cell Systems* establishes in silico structural validation (MODELLER, Rosetta FastRelax REU, QUARK, AMBER16 MD).
   - Figure 5 in *Cell Systems* establishes in vitro experimental validation (expression, SDS-PAGE gel, far-UV CD spectra, thermal melt).
   - *STAR Protocols* (2021) establishes webserver UI in Figure 1 and sequence logos / BeStSel CD secondary structure deconvolution in Figure 2.

4. **Multi-Target Candidate Generation Scope:**
   - The paper generated **over 600,000 sequences for each of four target folds** (>2.4 million sequences total).
   - The historical output libraries are not bundled in git. Generating 2.4M sequences is classified as **REGENERATION_REQUIRED_BUT_EXPENSIVE** (exact current regeneration cost unbenchmarked; previous claims of 67–1,113 GPU-hours were unmeasured extrapolations).
   - A single 1n5uA03 design run is strictly an **integration fixture**, not full four-fold generation reproduction.

---

## 2. Project Authority Hierarchy & Evidence Classification

Evidence sources are strictly classified into four authority tiers:

- **Tier A: Primary Scientific Source**
  - Original Paper: Strokach et al., *Cell Systems* 2020 (DOI: [10.1016/j.cels.2020.08.016](https://doi.org/10.1016/j.cels.2020.08.016))
  - STAR Protocols: Strokach et al., *STAR Protocols* 2021 (DOI: [10.1016/j.xpro.2021.100505](https://doi.org/10.1016/j.xpro.2021.100505), PMCID: PMC8102803)
  - Upstream Source: `external/proteinsolver-original` (commit `69ef0965a3fc3bf191804035b539720a06e58ba6`)
  - Canonical Checkpoint: `e53-s1952148-d93703104.state` (SHA-256: `1E8272F05EC19041394568C949BBDBF012EE72C1595BE7157C4BB0324D0B5727`)

- **Tier B: Current Project Authority**
  - `docs/PROJECT_TRUTH.md` (Verified implementation facts & limitations)
  - `science/PREREGISTRATION.md` & `evaluation_protocol.md` (Scientific Protocol)
  - `CLAIMS_REGISTRY.md` (Active registered claims V-01..V-15, NV-01, H-01..H-03)
  - `DECISION_LOG.md` (Decisions DEC-001 through DEC-019)
  - `reports/AG_LIVE_PROGRESS.md` (Active phase progress)

- **Tier C: Historical Supporting Evidence**
  - `reports/PHASE1_PROTEINSOLVER_REPRODUCTION.md`
  - `reports/PROTEINSOLVER_PROVENANCE_MANIFEST.md`
  - `reports/paper_vs_implementation.md`
  - `experiments/EXP000_`, `EXP001_`, `EXP004_` records

- **Tier D: Obsolete / Superseded Material**
  - Stale parameter counts (~1.5M -> 567,060)
  - Stale recovery overclaims (100% leak -> 41.30% valid all-masked recovery)
  - Stale 1n5uA03 generalization assertions (single target != benchmark)

---

## 3. Final-Paper Figure Crosswalk & Provenance Mapping

The following crosswalk maps every major paper output from the primary literature to protocol panels, author notebooks, underlying data files, and research artifacts:

| Final Paper Unit | What It Measures | STAR Protocol Unit | Upstream Notebook | Upstream Data File | Research Status & Artifact |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Figure 1A–E** | CSP concept, distance graph, EdgeConv architecture, masking, unmasking | Fig 1A–D (UI) | `xx_graphic_abstract.ipynb`, `proteinsolver/models/proteinnet.py` | Synthetic / code | **REPRODUCED** (`src/proteinsolver_baseline/`, unit tests) |
| **Figure 2A** | Training loss & validation accuracy (epochs 0–53) | N/A | `04_protein_train.ipynb`, `05_select_best_model.ipynb` | 72M training corpus (Parquet) | **HISTORICAL_TRAINING_TRAJECTORY_NOT_REPRODUCED** (DEC-004) |
| **Figure 2B** | Native sequence recovery on Gene3D test superfamilies (oneshot vs incremental) | N/A | `06_protein_analysis.ipynb` | `deep-protein-gen/processed/test_data/` (1,283 test domain graphs) | **PARTIALLY_REPRODUCED** (1n5u fixture verified; 172-superfamily benchmark pending download) |
| **Figure 2C** | Sequence identity under partial information (0%, 50%, 80% reference residues available) | Fig 2A (Logos) | `17_profile_recovery.ipynb`, `18_profile_recovery_combined.ipynb` | CATH domain alignments (`cath-domain-seqs-S*.fa`) | **NOT_REPRODUCED** (Notebook workflow mapped; execution pending) |
| **Figure 2D** | ProTherm single-point mutation stability correlation (Spearman $\rho = 0.444$, $N=3,471$) | N/A | `06_protein_analysis.ipynb`, `07_protein_analysis_figures.ipynb` | `notebooks/07_protein_analysis_figures/protherm_design_wt_RUE.csv` | **RECONSTRUCTION_FROM_PRESERVED_NOTEBOOK_STATISTICS** (`experiments/EXP005_PROTHERM_REPRODUCTION/`) |
| **Figure 2E** | Rocklin single-point mutation stability dataset correlation across miniproteins and known proteins | N/A | `07_protein_analysis_figures.ipynb` (Cell 80-91) | `GAPF_design_RUE_wt.csv`, `rocklin_2017_mutation_ssm2.parquet` | **RECONSTRUCTION_FROM_PRESERVED_NOTEBOOK_STATISTICS** (`experiments/EXP006_ROCKLIN_STABILITY_REPRODUCTION/`) |
| **Figure 2F** | Whole-protein stability correlations for Rosetta-designed de novo proteins across 4 topologies & rounds | N/A | `06_global_analysis_of_protein_folding_stability.ipynb`, `07_protein_analysis_figures.ipynb` (Cell 92-104) | `extra-data/rocklin_*.parquet`, `GAPF_design_RUE_wt.csv` | **RECONSTRUCTION_FROM_PRESERVED_NOTEBOOK_STATISTICS** (`experiments/EXP006_ROCKLIN_STABILITY_REPRODUCTION/`) |
| **Figure 3A-D** | De novo sequence design for 4 target folds (1n5uA03, 4beuA02, 4unuA00, 4z8jA00; >600k/fold) | Fig 1E-L (Generation) | `10_generate_protein_sequences.ipynb`, `11_analyze_generated_sequences.ipynb` | `notebooks/protein_demo/inputs/*.pdb` | **INTEGRATION_FIXTURE** (`experiments/EXP008_FOUR_TARGET_INTEGRATION_FIXTURE/`; 2.4M generation = `REGENERATION_REQUIRED_BUT_EXPENSIVE`) |
| **Figure 4A-D** | In silico structural validation (MODELLER DOPE, Rosetta REU, QUARK, AMBER16 MD) | Steps 11-14 | `16_david_analysis.ipynb`, `16_david_analysis_quark.ipynb` | `Scores/*` (historical outputs) | **HISTORICALLY_PRESERVED** (QUARK/MD external; ESMFold modern equivalent) |
| **Figure 5A-B** | Serum albumin domain 3 target structure & pairwise alignment of top design | N/A | `16_protein_analysis_experimental.ipynb` | `inputs/1n5uA03.pdb` | **REPRODUCED** (Design sequence alignment verified) |
| **Figure 5C** | SDS-PAGE gel of soluble E. coli expression for 1n5u design | Step 18 | Wet-lab protocol | Physical bacterial culture | **WET_LAB_ONLY / HISTORICALLY_PRESERVED** (`static/albert/gells-1n5u.png`) |
| **Figure 5D-E** | Far-UV Circular Dichroism (CD) spectrum & thermal denaturation melt at 222 nm | Step 19 | CD spectrophotometer | Physical purified protein | **WET_LAB_ONLY / HISTORICALLY_PRESERVED** |
| **STAR Step 19** | CD secondary structure deconvolution (BeStSel) for reference vs design (1n5u & 4beu) | Step 19 | `07_protein_analysis_bestsel.ipynb` | Embedded numerical data in notebook | **RECONSTRUCTION_FROM_PRESERVED_BESTSEL_OUTPUTS** (`experiments/EXP007_BESTSEL_CD_REPRODUCTION/`) |

---

## 4. Primary-Source Paper & Protocol Specifications

### A. Model Specification
- **Graph Formulation:** Attributed undirected graph $G = (V, E)$. Nodes $v_i$ represent residues ($i = 1, \dots, N$). Edges $e_{ij}$ represent pairwise spatial interactions with $\min_{a \in i, b \in j} \|\mathbf{r}_{ia} - \mathbf{r}_{jb}\|_2 < 12.0\text{ \AA}$.
- **Input Featurization:**
  - Nodes: Categorical index $x_i \in \{0, \dots, 20\}$ (indices $0..19$ canonical amino acids; index $20$ mask token `'-'`). Embedding: `nn.Embedding(21, 128)` $\to$ `ReLU` $\to$ `Linear(128, 128)` $\to$ `LayerNorm(128)`.
  - Edges: Continuous normalized float vector $[d_{\text{norm}}, \Delta_{\text{norm}}] = \left[\frac{d - 6.0}{12.0}, \frac{|j-i| - 0.0}{68.1319}\right]$ (scalar linear normalization). Embedding: `Linear(2, 128)` $\to$ `ReLU` $\to$ `Linear(128, 128)` $\to$ `LayerNorm(128)`.
- **GNN Architecture:** 4 residual blocks based on modified `EdgeConv`. In each block:
  1. Edge update: Concatenation $[h_i \| h_j \| e_{ij}] \in \mathbb{R}^{384} \to \text{MLP}(384 \to 256 \to 128) \to e'_{ij}$.
  2. Node update: Aggregation $\sum_{j \in \mathcal{N}(i)} e'_{ij} \in \mathbb{R}^{128}$, added to $h_i$ with LayerNorm and residual connection.
- **Output Projection:** `Linear(128, 20)` generating unnormalized class logits $z_{i, a}$ for the 20 amino acids.
- **Training Paradigm:** Masked language modeling predicting ~50% randomly masked residues using cross-entropy loss over masked positions.
- **Training Corpus:** 72,464,122 sequence/adjacency pairs from 1,373 Gene3D superfamilies (split: 1,029 train, 172 validation, 172 test superfamilies).
- **Optimizer & Scheduler:** Adam optimizer with initial learning rate $1 \times 10^{-4}$ and `optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'max', verbose=True)`.

### B. Sequence Generation (Inference as CSP)
- **Problem Setup:** Target distance matrix $D$ ($d_{ij} < 12\text{ \AA}$) with all positions initialized to mask token ($x_i = 20, \forall i$).
- **Inference Algorithms:**
  1. *Greedy MAP / Argmax:* Iteratively unmasks the position with highest marginal confidence $p^* = \max_{i, a} P(s_i = a \mid G)$, assigns $s_i = a^*$, re-runs forward pass, repeats until all positions filled.
  2. *Multinomial Sampling with Temperature:* At each step, scales logits by $1/T$ ($T \in [0.01, 1.0]$) and samples residue from conditional softmax distribution.
  3. *A* / Expectimax Search:* Priority queue search optimizing path likelihood $\prod_i P(s_i \mid G)$ (`10_generate_protein_sequences.ipynb`).
- **Fixed Residues:** Any position $k$ with pre-assigned amino acid is initialized with $x_k \in \{0..19\}$ and excluded from unmasking.

### C. Downstream Structural & Dynamic Validation
- **Homology Modeling:** MODELLER (`automodel`, PIR alignment format) evaluating GA341, DOPE, DOPE-HR, and normalized DOPE scores.
- **Energy Scoring:** Rosetta `FastRelax` with `ref2015` scoring function, generating Rosetta Energy Units (REU).
- **Ab Initio Structure Prediction:** QUARK web server (Yang Zhang lab) predicting 3D coordinates from sequence alone without template (models QA4879, QA4880, QA4893, QA4902).
- **Molecular Dynamics (MD):** AMBER16 with `ff14SB` force field, explicit TIP3P water box (12 \AA\ buffer / 12 nm$^3$), Na$^+$/Cl$^-$ counter-ions, 800 ps equilibration, 2 fs timestep, SHAKE on bonds to H, PME electrostatics, 30–100+ ns duration.

### D. Experimental Validation In Vitro
- **Targets:** 1n5uA03 (serum albumin domain 3, 92 AA, 4-helix bundle) and 4beuA02 (racemase domain).
- **Expression & Purification:** E. coli BL21(DE3), induced with 0.5 mM IPTG (3 h, 37°C), BugBuster Master Mix lysis, Ni-NTA agarose affinity purification, dialysis into PBS.
- **Sample Characterization:** SDS-PAGE purity verification, concentration via A280/BCA, ESI Mass Spectrometry confirming theoretical molecular weight.
- **Circular Dichroism (CD) & Thermal Denaturation:** Far-UV CD spectra (190–260 nm, 10–20 $\mu$M, 1 mm cuvette) showing $\alpha$-helical double minima at 208 nm and 222 nm; thermal melt at 222 nm showing cooperative unfolding. BeStSel secondary structure deconvolution for 1n5u design (~30% $\alpha$-helix, matching ~31% reference) and 4beu design (~21% $\beta$-sheet, matching ~33% reference); see STAR Protocols Step 19.

---

## 5. Master Paper-to-Code-to-Data Master Matrix

Below is the master reproduction matrix mapping all 19 major units of the Strokach et al. 2020 paper with corrected figure numbering and calibrated reproduction categories:

| ID | Final Paper Unit | Scientific Purpose | Original Notebook / Code Path | Required Input Data | Required Checkpoint | External Software | Required Compute | Reproduction Category | Evidence Strength | Can Reuse Checkpoint? | Retrain Required? | Wet-Lab Required? | Priority |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **U01** | Figure 1C | 4-block EdgeConv GNN verification | `proteinsolver/models/proteinnet.py` | None (synthetic) | None | PyTorch, PyG | CPU (<1s) | **CODE_RECONSTRUCTION_VERIFIED** | Cryptographic / Code | Yes | No | No | Complete |
| **U02** | Figure 1B | Residue contact graph (<12 \AA) & linear norms | `proteinsolver/datasets/protein.py` | PDB structure | None | BioPython / kmtools | CPU (<1s) | **RAW_DATA_RECOMPUTED** | Empirical / Tests | Yes | No | No | Complete |
| **U03** | Figure 1D | MLM forward pass & pseudo-perplexity | `proteinsolver/utils/protein_design.py` | Protein graph | `e53` state | PyTorch | CPU / GPU (<1s) | **RAW_DATA_RECOMPUTED** | Empirical / EXP004 | Yes | No | No | Complete |
| **U04** | Methods | Strict state dict key mapping & shapes | `proteinsolver/models/proteinnet.py` | State dict file | `e53` state | PyTorch | CPU (<2s) | **CRYPTOGRAPHIC_INTEGRITY_VERIFIED** | Cryptographic (SHA-256) | Yes | No | No | Complete |
| **U05** | Figure 2A | Epoch 0-53 loss & validation accuracy | `04_protein_train.ipynb` | 72M Gene3D Parquet | Training recipe | Slurm / PyTorch | Multi-GPU (~500h) | **HISTORICAL_TRAINING_TRAJECTORY_NOT_REPRODUCED** | Historical Absent | No | Yes (for trajectory) | No | Excluded (DEC-004) |
| **U06** | Figure 2B (Oneshot) | Unmasking all positions in single pass | `06_protein_analysis.ipynb` | Gene3D test partition | `e53` state | PyTorch | GPU (~10m) | **PARTIALLY_REPRODUCED** | Historical Notebook | Yes | No | No | High (Phase R2) |
| **U07** | Figure 2B (Incremental) | Sequential CSP design on 172 superfamilies | `06_protein_analysis.ipynb` | Gene3D test partition | `e53` state | PyTorch | GPU (~1h) | **PARTIALLY_REPRODUCED** | Single-target fixture | Yes | No | No | High (Phase R2) |
| **U08** | Figure 2C | Sequence identity under 0%, 50%, 80% reference | `17_profile_recovery.ipynb`, `18_*.ipynb` | CATH domain alignments | `e53` state | MUSCLE, BioPython | CPU (~15m) | **PENDING_RECOMPUTATION** | Historical Notebook | Yes | No | No | High (Phase R2) |
| **U09** | Figure 2D | ProTherm single-point mutation $\Delta\Delta G$ corr | `07_protein_analysis_figures.ipynb` | `protherm_design_wt_RUE.csv` | Precomputed / `e53` | Pandas, SciPy | CPU (<10s) | **PARTIAL_RECOMPUTATION / RECONSTRUCTION_FROM_PRESERVED_NOTEBOOK_STATISTICS** | Local CSV ($N=3,471$) / Notebook | Yes | No | No | Complete (EXP005) |
| **U10** | Figure 2E | Rocklin single-point mutation stability dataset ($N=9,912$) | `07_protein_analysis_figures.ipynb` (Cell 80-91) | `GAPF_design_RUE_wt.csv` | Precomputed / `e53` | Pandas, SciPy | CPU (<10s) | **PRESERVED_SOURCE_MATERIAL** | Local CSV present | Yes | No | No | Complete |
| **U11** | Figure 2F | Whole-protein stability across 4 topologies & rounds | `06_global_analysis_of_protein_folding_stability.ipynb` (Cell 53) | Notebook 06 & 07 statistics | Precomputed / `e53` | Pandas, SciPy | CPU (<15s) | **RECONSTRUCTION_FROM_PRESERVED_NOTEBOOK_STATISTICS** | Notebook cells 53 & 102 | Yes | No | No | Complete (EXP006) |
| **U12** | Figure 3 | 1n5uA03 all-masked CSP sequence design | `10_generate_protein_sequences.ipynb` | `1n5uA03.pdb` | `e53` state | PyTorch | CPU (1.67s) | **INTEGRATION_FIXTURE_VERIFIED** | Empirical (EXP001) | Yes | No | No | Complete (Fixture) |
| **U13** | Figure 3 | 600,000+ candidate generation across 4 folds | `10_generate_protein_sequences.ipynb` | Inputs `*.pdb` | `e53` state | PyTorch | Unbenchmarked | **REGENERATION_REQUIRED_BUT_EXPENSIVE** | Missing local libraries | Yes | No | No | Excluded (Scope) |
| **U14** | Figure 4 | Homology modeling & REU FastRelax | `16_david_analysis.ipynb` | Homology models | None | MODELLER, Rosetta | CPU cluster | **HISTORICAL_RESULT_PRESERVED** | Scores in notebook | Yes | No | No | Modern Equivalent |
| **U15** | Figure 4 | Ab initio structure folding of designs | `16_david_analysis_quark.ipynb` | Designed sequences | None | QUARK web server | External server | **HISTORICAL_RESULT_PRESERVED** | Server Job IDs | Yes | No | No | Modern Equivalent |
| **U16** | Methods | Explicit solvent MD trajectory stability | STAR Protocol PMC8102803 | Solvated PDB | None | AMBER16 / OpenMM | GPU (~5 days) | **NOT_REPRODUCED** | Protocol Spec | Yes | No | No | Low / Heavy |
| **U17** | Figure 5C | Soluble E. coli protein expression & gel | Lab protocol / wet-lab | Synthetic DNA | None | Wet-lab | Wet-lab | **WET_LAB_ONLY / HISTORICALLY_PRESERVED** | Gel image in repo | Yes | No | Yes | Physical |
| **U18** | Figure 5D-E | Far-UV CD spectra & thermal melt curve | Lab protocol / wet-lab | CD spectrophotometer | None | Wet-lab | Wet-lab | **WET_LAB_ONLY / HISTORICALLY_PRESERVED** | Paper curves | Yes | No | Yes | Physical |
| **U19** | STAR Step 19 | BeStSel secondary structure deconvolution | `07_protein_analysis_bestsel.ipynb` | CD data strings | None | Matplotlib, BeStSel | CPU (<5s) | **RECONSTRUCTION_FROM_PRESERVED_BESTSEL_OUTPUTS** | Embedded numbers | Yes | No | Yes | Complete (EXP007) |

---

## 6. Scientific Fidelity & Modern Substitution Policy

1. **Rule of Exact Scientific Meaning:**
   - Any modern substitute must be explicitly labeled `MODERN_EQUIVALENT_NOT_EXACT_HISTORICAL_REPRODUCTION`.
   - Substituting ESMFold for QUARK or AlphaFold2 for Rosetta FastRelax changes the scoring potential from empirical physics-based energy to deep co-evolutionary representations.
2. **Brute Force vs. Smart Workaround:**
   - *Brute Force:* Used when original data is local, runtime is short, and exact method is known (e.g. ProTherm and Rocklin stability correlations from existing local CSVs).
   - *Smart Workaround:* Used when historical infrastructure is obsolete (e.g. `kmbio` Cython parser replaced by cleanroom BioPython extractor; modern PyTorch scatter fallback).
3. **Strict Separation of Diagnostic Scoring vs. Inverse-Folding Design:**
   - Diagnostic scoring (`data.y` provided, `strategy='ref'`) evaluates sequence likelihood on a solved structure.
   - Valid sequence recovery requires `data.x = 20` and `data.y = None`.

---

## 7. Stop / Continue Decision

**DECISION: PHASE R1.2.1 FINAL RECONCILIATION COMPLETE. READY FOR PHASE R2 COMPUTATIONAL BENCHMARK REPRODUCTION.**
