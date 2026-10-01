# ProteinSolver R1.2.2 Final Evidence Closure Report
**Lead Scientific Reproducibility Engineer & Evidence-Governance Agent**
**Phase:** R1 Final Closure & R2 Release Gate
**Authority Scope:** Definitive source-of-truth reconciliation across Cell Systems publication, STAR Protocols, upstream repository, and research-repo experimental artifacts.
**Parent Verification Basis:** `d961ef0b865f03d05a3df339b9f84b8f20c9ea56`
**Historical Upstream Commit:** `69ef0965a3fc3bf191804035b539720a06e58ba6`
**Modern Implementation Commit:** `58255bc67323f5fd009ac85ae02fbf69c152c457`
**Pretrained Checkpoint SHA-256:** `1E8272F05EC19041394568C949BBDBF012EE72C1595BE7157C4BB0324D0B5727`
**Status:** R1 CLOSURE VERIFIED / R2_READY

---

## 1. Executive Summary

This report establishes the final, immutable evidence closure for Phase R1 of the ProteinSolver reproduction and validation program. Phase R1 had the mandate to reconcile the published literature (*Cell Systems* 2020, *STAR Protocols* 2021), the historical upstream source code (`external/proteinsolver-original`), the modern cleanroom implementation (`d:\Projects\ProteinSolver`), and all preliminary experimental reproductions (EXP000 through EXP008) into an exact, internally consistent evidence graph.

Through exhaustive source-level adjudication across primary code and literature, all historical AI hallucinations, phantom figure attributions, mischaracterized loss trajectories, conflated training corpus metrics, ungrounded execution cost claims, and checkpoint hash mismatches have been identified and permanently eliminated from current authority.

**Key Bounded Epistemic Finding:**
No additional material contradictions were identified within the audited current-authority corpus after reconciliation. All current-authority documents (`docs/PROJECT_TRUTH.md`, `science/original_proteinsolver.md`, `reports/REPORT_INDEX.md`, and this closure report) align strictly with Tier A primary sources. Phase R1 is formally closed, and the program is declared **R2_READY**.

---

## 2. Primary Literature Authority & Final Paper Panels

### 2.1 Bibliographic Metadata & Authority
Direct verification against CrossRef and the published *Cell Systems* archive establishes the authoritative bibliographic citation:
- **Title:** Fast and Flexible Protein Design Using Deep Graph Neural Networks
- **Authors:** Alexey Strokach, David Becerra, Carles Corbi-Verge, Albert Perez-Riba, Philip M. Kim
- **Journal:** *Cell Systems*
- **Volume & Issue:** Volume 11, Issue 4
- **Pages:** 402–411.e4
- **Date:** October 21, 2020 (published online August 20, 2020)
- **DOI:** [10.1016/j.cels.2020.08.016](https://doi.org/10.1016/j.cels.2020.08.016)

*Correction Record:* Prior draft reports referenced page numbers "498–507" and dates of "November 18, 2020". These erroneous bibliographic markers have been excised from current authority.

### 2.2 Final Published Figure 1
Direct forensic inspection of the final published *Cell Systems* paper establishes that Main Figure 1 consists strictly of three panels:
- **Figure 1A:** Graph representation of protein structures and the graph neural network architecture (spatial distance thresholding at 12 Å, node embeddings, edge features, and message-passing layers).
- **Figure 1B:** Training procedure formulating protein design as a masked language modeling constraint-satisfaction problem over structured graphs (stochastic masking of amino acids, cross-entropy training against native residues).
- **Figure 1C:** Sequence generation strategies (iterative stochastic decoding, probability-guided MAP decoding, and evaluation on structural topologies).

*Correction Record:* Prior AI reports referenced "Figure 1A–E", incorrectly importing panel divisions from early bioRxiv preprints or internal notebook plots. In the final Cell Systems paper, panels D and E do not exist in Main Figure 1. All current authority documents have been corrected to strictly cite **Figure 1A, 1B, 1C**.

### 2.3 Final Published Figure 2A: Training and Validation Accuracy
Direct inspection of the final published Figure 2A confirms that its y-axis displays **accuracy** (the proportion of correctly predicted masked residues), NOT loss.
- **Canonical Definition:** Training and validation accuracy trajectory across training iterations.
- **Empirical Value:** Accuracy increases rapidly during initial iterations, plateauing at approximately 30–40% on heterogeneous masked validation sets.
- **Correction Record:** All references in current-authority documents describing Figure 2A as "training loss", "validation loss", or "loss trajectory" have been eliminated. Where historical loss trajectories are referenced, they are explicitly qualified as non-paper training artifacts from `04_protein_train.ipynb`.

### 2.4 Final Published Figure 2B–2F Semantics
- **Figure 2B:** Native sequence recovery distributions on independent Gene3D test domains (one-shot generation achieving ~27.29% median/mean recovery).
- **Figure 2C:** Sequence recovery distributions under partial sequence availability / conditioning (0%, 50%, 80% unmasked).
- **Figure 2D:** ProTherm single-point mutation stability ($\Delta\Delta G$) correlation (published ProteinSolver $\rho \approx 0.444$).
- **Figure 2E:** Rocklin single-point mutation stability dataset ($N = 9,912$).
- **Figure 2F:** De novo whole-protein stability of Rosetta-designed proteins across 4 topologies ($\alpha\alpha\alpha$, $\beta\alpha\beta\beta$, $\alpha\beta\beta\alpha$, $\beta\beta\alpha\beta\beta$) across selection rounds 1–4.

### 2.5 Exact Published Figure 2G–N Panel Mapping
Main Figure 2 panels 2G through 2N illustrate the computational evaluation and experimental biophysical characterization of *de novo* designed sequences for Human Serum Albumin domain 3 (**1n5uA03**, 92 residues, all-$\alpha$ fold). The exact panel-to-method mapping from the published Cell Systems caption is:
- **Figure 2G:** Contact map / geometry (comparison of reference structure distance matrix vs. model-designed contact graph).
- **Figure 2H:** ProteinSolver scores / generated-sequence identity analysis (scatter plot of generated designs: sequence identity to wild-type vs. ProteinSolver log-likelihood score).
- **Figure 2I:** Sequence logo (amino acid profile across positions for generated sequences compared to wild-type sequence).
- **Figure 2J:** Secondary-structure / topology logo (predicted secondary structure propensities across the fold).
- **Figure 2K:** MODELLER / Rosetta structural-energy analysis (evaluation of homology-model relaxed structures with Rosetta total energy).
- **Figure 2L:** QUARK structural prediction / comparison (*de novo* structural folding predictions of generated sequences evaluated against the target crystal structure).
- **Figure 2M:** 100-ns molecular-dynamics residue fluctuation analysis (root-mean-square fluctuations [RMSF] comparing native and designed sequences over 100 ns explicit-solvent simulations).
- **Figure 2N:** Circular-dichroism (CD) spectra (experimental far-UV circular dichroism wavelength scans measuring secondary structure content of purified expressed designs).

*Correction Record:* Prior drafts improperly assigned wet-lab workflow steps (SEC, SDS-PAGE, expression) into panels 2G–2M. Furthermore, the target was mislabeled as "serum response factor core domain". 1N5U is Human Serum Albumin domain 3. Current authority strictly enforces the exact panel crosswalk and biological identity.

### 2.6 Final Supplementary Figures S3–S5 Target Mapping & Domain Boundaries
The *Cell Systems* paper validates three additional target structural folds in the Supplementary Information:
- **Supplementary Figure S3:** Alanine Racemase fold design (**4beuA02**), length = **217 residues** ($\alpha/\beta$ fold).
  - *Critical Provenance Distinction:* The length 217 AA corresponds strictly to the **local CATH domain artifact** (residues 49–265 of Chain A) used for graph featurization and model inference. The full biological PDB chain 4BEU chain A contains over 380 residues. Current authority explicitly documents this domain vs. full chain boundary.
- **Supplementary Figure S4:** Immunoglobulin Light Chain fold design (**4unuA00**), length = **109 residues** (all-$\beta$ fold; dimer of lambda variable domains). Erroneous references to "Formyl-CoA transferase" have been eliminated.
- **Supplementary Figure S5:** PDZ3 Domain fold design (**4z8jA00**), length = **96 residues** (mainly-$\beta$ fold; SNX27 PDZ domain). Erroneous references to "Translation initiation factor IF-3" have been eliminated.

---

## 3. Training Corpus Representation Reconciliation

To avoid conflation between high-level paper descriptions and low-level data artifacts, the training corpus is reconciled across its distinct operational layers:

| Layer / Quantity | Meaning | Source | Exact / Approx. | Role in Pipeline |
| :--- | :--- | :--- | :--- | :--- |
| **Headline Sequences** (>70M) | Total biological sequences associated with structural models | *Cell Systems* Abstract & Intro | Approximate (>70,000,000) | Published scientific narrative & scope |
| **Headline Structures** (>80k) | Unique protein structural coordinate files ingested | *Cell Systems* Abstract & Methods | Approximate (>80,000) | Structural diversity scope |
| **Gene3D Domain Sequences** (~72M) | Homologous domain sequences extracted from UniParc | *Cell Systems* STAR Methods | Approximate (~72 million) | Sequence corpus for MSA/homology transfer |
| **Unique CATH Domains** (82,148) | Non-redundant structural domains filtered from CATH v4.2 | Repository `01_process_structures.ipynb` | Exact (82,148) | Master structural coordinate templates |
| **Prepared Training Records** (72,464,122) | Sequence/adjacency/structure-pair records partitioned across splits | Repository `03_generate_training_data.ipynb` | Exact (72,464,122) | Processed network training dataset |
| **Superfamily Partitioning** (1,373) | Distinct Gene3D superfamilies split 75% / 12.5% / 12.5% | *Cell Systems* & repo split files | Exact (1,373: 1,029 train, 172 val, 172 test) | Cluster-disjoint generalization split |

**Canonical Corpus Reconciliation Statement:**
*Published paper: >70M sequences corresponding to >80k structures. The repository's prepared structural-pair inventory contains 72,464,122 records, where directly verified; these are not to be presented as a replacement for the paper's scientific headline.*

---

## 4. Original Model Specification & Implementation Adjudication

The definitive model architecture and training hyperparameters are established through direct inspection of the upstream source code (`external/proteinsolver-original/proteinsolver/`) and historical training notebooks (`04_protein_train.ipynb`):

### 4.1 Architecture & Dimensionality
- **Model Family:** Residual Graph Neural Network (`ProteinNet` / `ProteinSolverNet`).
- **Graph Convolutional Blocks:** 4 sequential residual blocks (`graph_conv_1` through `graph_conv_4`).
- **Parameter Count:** Exactly **567,060 trainable parameters** (45/45 tensors matching checkpoint `e53-s1952148-d93703104.state`).
- **Block Composition:**
  - `EdgeConvMod` layer receives concatenated node and edge representations:
    $$\mathbf{h}_{\text{edge\_in}} = [\mathbf{x}_{\text{row}} \,\|\, \mathbf{x}_{\text{col}} \,\|\, \mathbf{e}_{ij}] \in \mathbb{R}^{384}$$
  - Edge MLP: `nn.Sequential(nn.Linear(384, 256), nn.ReLU(), nn.Linear(256, 128))` mapping edge state to $\mathbb{R}^{128}$.
  - Node Aggregation: Summed scatter aggregation $\sum_{j \in \mathcal{N}(i)} \mathbf{e}_{ij}$ across incoming edges to update node state.
  - Postprocessing: `EdgeConvBatch` applies `nn.LayerNorm(128)` and `nn.Dropout(0.2)` to both node and edge tensors.
  - Block Skip Connections: Additive residual connections for both nodes ($\mathbf{x} \leftarrow \mathbf{x} + \mathbf{x}_{\text{out}}$) and edges ($\mathbf{e} \leftarrow \mathbf{e} + \mathbf{e}_{\text{out}}$) followed by `F.relu()`.

### 4.2 Edge Representation Adjudication (Paper vs. Implementation)
To eliminate previous conflicting descriptions regarding 2 vs. 3 edge features:
- **Paper-Level Conceptual Representation:** The published paper prose describes edges connecting residues within 12 Å, incorporating both continuous Euclidean distance and linear sequence separation.
- **Historical Implementation Representation:** In `proteinsolver/datasets/protein.py` (`transform_edge_attr`), `data.edge_attr` is constructed strictly as a **2-channel float tensor** of shape $[E, 2]$:
  - Channel 0: $d_{\text{norm}} = (d_{ij} - 6.0) / 12.0$
  - Channel 1: $\Delta_{\text{norm}} = (j - i) / 68.1319$
- **Dimension Entering Edge Embedding:** $[E, 2]$ (`adj_input_size = 2`).
- **Dimension After Edge Embedding:** $[E, 128]$ (`embed_adj = nn.Sequential(nn.Linear(2, 128), nn.ReLU(), nn.Linear(128, 128), nn.LayerNorm(128))`).
- **Raw Distance Retention:** Raw Cartesian distance $d_{ij}$ is **NOT** retained as an additional input channel to the neural network.
- **Sequence Separation Retention:** Retained as the second normalized channel, preserving sequence directionality ($j - i$).
- **Reason for Difference:** Difference observed; the paper presents geometric features conceptually as distance and sequence separation, while the implementation normalizes both scalar features before passing them to a 2-channel linear embedding layer.

### 4.3 Structural Distance Definition
- **Primary Source Evidence:** Both the published paper STAR Methods and the upstream implementation (`proteinsolver/utils/protein_structure.py`) establish that edge connectivity is based on the **shortest heavy-atom distance**:
  - Paper: *"distances between all pairs of residues that are within 12 Angstroms of one another, considering both the backbone and the sidechain residues in this calculation."*
  - Implementation: `cdist(heavy_coords[i], heavy_coords[j]).min() < 12.0` across all non-hydrogen atoms.
- **Status:** **VERIFIED MATCH**. The model operates on shortest heavy-atom distance, NOT $C_\alpha$-only distance.

### 4.4 Distance & Sequence Scaling
- **Cartesian Normalization:** $d_{\text{norm}} = (d_{ij} - 6.0) / 12.0$ is an **affine scalar shift-and-scale** (offset 6.0, scale 12.0). For $d \in [0, 12]$ Å, the output spans approximately $[-0.5, +0.5]$.
- **Sequence Separation Scaling:** $\Delta_{\text{norm}} = (j - i) / 68.1319$ is an affine linear scaling (offset 0.0, scale 68.1319).
- **Epistemic Rationale:** 68.1319 is a fixed historical scaling constant; its rationale was not established from the audited source. It must not be asserted as an empirically proven standard deviation.

### 4.5 Self-Loops & Residual State Updates
- **Primary Source Code:**
  1. In `proteinsolver/datasets/protein.py` (`row_to_data`):
     ```python
     mask = row_index == col_index
     if mask.any():
         row_index = row_index[~mask]
         col_index = col_index[~mask]
         edge_attr = edge_attr[~mask, :]
     ...
     assert not data.contains_self_loops()
     ```
  2. In `ProteinNet.forward`:
     ```python
     edge_index, _ = remove_self_loops(edge_index)
     ```
- **Adjudicated Truth:** Self-loop edges are strictly **absent** from the contact graph. They are filtered at creation, asserted absent, and stripped defensively in `forward`.
- **Node Self-State Updates:** Occur strictly via inter-block additive residual skip connections ($\mathbf{x} \leftarrow \mathbf{x} + \mathbf{x}_{\text{out}}$). Historical reports that referred to "native self-loops" conflated residual skip connections with graph topology.

### 4.6 Vocabulary, Activations & Head
- **Node Vocabulary:** Exactly **21 tokens** (20 canonical amino acids at indices 0–19, plus index 20 as mask token; `nn.Embedding(21, 128)`).
- **Node Output Head:** `nn.Linear(128, 20)` outputting raw logits for the 20 canonical amino acids. Mask token is not an output prediction target.
- **Activations:** Strictly **ReLU** throughout `ProteinNet`. No ELU or LeakyReLU.

### 4.7 Training Hyperparameters & Batch Size Contexts
The historical repository utilized different batch sizes depending on operational context:
- **Primary GCN Training Run:** `batch_size = 4` structures per step (`04_protein_train.ipynb` Cell 25; directory `notebooks/protein_4xEdgeConv_bs4/`).
- **Exploratory GCN Training Run:** `batch_size = 1` (`UNIQUE_ID = "0007604c"`).
- **Validation & Test Evaluation:** `batch_size = 1` (`05_select_best_model.ipynb`, `06_protein_analysis.ipynb`).
- **Inference & Scoring:** `batch_size = 1` (`06_global_analysis_of_protein_folding_stability.ipynb`, `20_protein_demo.ipynb`).
- **Sequence Generation:** `batch_size = 1` or dynamic length-bounded batches (`10_generate_protein_sequences.ipynb`).
- **Optimizer & Scheduler:** Adam ($\eta = 10^{-4}$), `ReduceLROnPlateau(mode='max', factor=0.5, patience=2)`.

---

## 5. Inference, Scoring, and Implementation Boundary

### 5.1 Generation Strategies
- **Canonical Paper Generation:** Iterative masked language modeling generation, where masked positions are sampled either stochastically from temperature-scaled softmax probabilities or deterministically via Maximum A Posteriori (MAP) decoding.
- **Search Extensions:** Graph-search extensions (A* search, best-first search, Expectimax) explored in specific author notebooks are designated as **historical exploratory extensions**, not canonical methods of the published Cell Systems paper.

### 5.2 Scoring and Pseudo-Log-Likelihood
- **Scoring Formulas:** Sequence evaluation uses pseudo-log-likelihood (PLL) computed by leave-one-out masking across all residues (`scan_with_mask` in `proteinsolver/utils/protein_design.py`).
- **Status:** Designated as **historical implementation scoring path**, maintaining exact mathematical fidelity to `proteinsolver.score()` while distinguishing implementation choices from high-level paper prose.

---

## 6. Experimental Evidence Forensic Calibration (EXP005–EXP008)

### 6.1 EXP005: ProTherm Mutation Stability Reproduction
- **Evidence Classification:** `PARTIAL_RECOMPUTATION / RECONSTRUCTION_FROM_PRESERVED_NOTEBOOK_STATISTICS`
- **Scientific Subject:** Main Figure 2D mutation stability correlation against experimental $\Delta\Delta G$ from the ProTherm database ($N = 3,471$ clean evaluation pairs from 3,524 raw records).
- **ProteinSolver Metric:** Published Spearman correlation $\rho \approx 0.444$ ($p = 1.78 \times 10^{-167}$, CI [0.419, 0.468]). An exploratory core-residue subset yielding $\rho \approx 0.551$ ($p = 1.28 \times 10^{-15}$, CI [0.460, 0.627]) is preserved strictly as an exploratory notebook finding (`07_protein_analysis_figures.ipynb` Cell 72), not as the primary paper headline.
- **Rosetta Metrics & Provenance:**
  - Raw unnormalized Rosetta REU difference vs. $\Delta\Delta G_{\text{exp}}$: $\rho \approx +0.008$ (recomputed) / $-0.008$ (notebook Cell 72).
  - Normalized Rosetta REU difference: $\rho = 0.0826$ in notebook (and $-0.407$ in certain inverted stability scoring).
  - Cartesian $\Delta\Delta G$: $\rho = 0.591$.
  - Monomer $\Delta\Delta G$: $\rho = 0.317$.
  - *Governance Standard:* Current authority explicitly distinguishes raw REU, normalized REU, Cartesian $\Delta\Delta G$, and monomer $\Delta\Delta G$, forbidding their collapse into an ambiguous "Rosetta $\Delta\Delta G$" statistic.

### 6.2 EXP006: Rocklin De Novo Protein Stability Reproduction
- **Evidence Classification:** `RECONSTRUCTION_FROM_PRESERVED_NOTEBOOK_STATISTICS`
- **Scientific Subject:** Main Figure 2E (single-point mutation stability, $N = 9,912$) and Figure 2F (*de novo* designed protein stability across 4 structural topologies: $\alpha\alpha\alpha$, $\beta\alpha\beta\beta$, $\alpha\beta\beta\alpha$, and $\beta\beta\alpha\beta\beta$ across design rounds 1–4).
- **Round 4 ProteinSolver Correlations:**
  - $\alpha\alpha\alpha$ (HHH): $\rho = 0.422$
  - $\alpha\beta\beta\alpha$ (HEEH): $\rho = 0.313$
  - $\beta\alpha\beta\beta$ (EHEE): $\rho = 0.245$
  - $\beta\beta\alpha\beta\beta$ (EEHEE): $\rho = -0.1421$
- **EEHEE Round 4 Exception:** Preserved evidence confirms that for the complex $\beta\beta\alpha\beta\beta$ (EEHEE) topology in Round 4, Rosetta talaris2013 scores yielded $\rho \approx -0.4012$ while ProteinSolver yielded $\rho \approx -0.1421$.
- **Governance Standard:** Conflicting summaries (e.g. 0.145 representing Round 2 peak vs. ungrounded draft artifact 0.185) are removed or qualified. Universal claims that ProteinSolver "always outperforms Rosetta" are prohibited and eliminated.

### 6.3 EXP007: BeStSel Secondary Structure Reconstruction
- **Evidence Classification:** `RECONSTRUCTION_FROM_PRESERVED_BESTSEL_OUTPUTS`
- **Scientific Subject:** Reconstructed secondary structure deconvolution of circular dichroism spectra using BeStSel, supporting STAR Protocols Step 19.
- **Statistical Wording:** For 1n5u designs vs. wild-type, paired testing across secondary structure elements yields $p > 0.05$ (min $p = 0.1599$). The calibrated epistemic description is:
  *"no statistically significant difference was detected under tested conditions"*,
  strictly rejecting the claim of "proven structural equivalence".
- **4beu Evaluation:** For 4beu, $N = 1$ experimental design; documented as descriptive single-instance data only.

### 6.4 EXP008: Multi-Target Integration Fixture
- **Evidence Classification:** `INTEGRATION_FIXTURE_VERIFIED`
- **Scientific Subject:** Bounded end-to-end integration fixture verifying data loading, graph featurization, checkpoint inference, MAP decoding, and sequence recovery across all 4 target folds:
  - 1n5uA03 (Human Serum Albumin, 92 AA): 41.30% native sequence recovery (38/92 residues).
  - 4beuA02 (Alanine Racemase, 217 AA domain artifact): 35.02% recovery (76/217 residues).
  - 4unuA00 (Immunoglobulin lambda variable, 109 AA): 39.45% recovery (43/109 residues).
  - 4z8jA00 (SNX27 PDZ domain, 96 AA): 36.46% recovery (35/96 residues).
- **Boundary:** EXP008 is an architectural and pipeline verification fixture, NOT a benchmark, generalization proof, or paper-scale candidate reproduction.
- **Regeneration Cost Boundary:** The full-scale paper campaign generated >600,000 sequences per target fold (>2,400,000 sequences total). Current authority classifies this as `REGENERATION_REQUIRED_BUT_EXPENSIVE`. The exact GPU-hour cost for modern hardware remains unbenchmarked (unsupported numbers such as 67 h or 1,113 h have been excised).

---

## 7. Biophysical Experimental Validation & Structural Equivalence Calibration

Current authority adheres strictly to the biophysical data presented in the *Cell Systems* paper:
- **Biophysical Modalities:** The published study conducted wet-lab characterization comprising recombinant expression, purification, size-exclusion chromatography (SEC), and far-UV circular dichroism (CD) wavelength scans.
- **Absence of Atomic Structure Determination:** The paper does not report atomic structure determination by NMR or X-ray crystallography for designed sequences. The canonical calibrated statement is:
  *"The published study reports biophysical experimental validation including circular dichroism; the paper does not report atomic structure determination by NMR/X-ray as part of this validation."*

---

## 8. Checkpoint Forensics & Cryptographic Verification

All copies of `.state` checkpoint files in the workspace were located and cryptographically verified:

| File Path | File Size (Bytes) | Cryptographic SHA-256 Checksum | Status |
| :--- | :---: | :--- | :--- |
| `external/proteinsolver-original/data/e53-s1952148-d93703104.state` | 2,278,071 | `1E8272F05EC19041394568C949BBDBF012EE72C1595BE7157C4BB0324D0B5727` | **PRIMARY PUBLISHED CHECKPOINT** |
| `external/proteinsolver-original/notebooks/protein_4xEdgeConv_bs4/e12-s1652709-d6610836.state` | 2,278,037 | `AAA242C96A7DD6AB69DF2E260455BD8B6661481BD10BA3B1AFB3E68FE1792C06` | Historical intermediate checkpoint |
| `d:\Projects\ProteinSolver\data\e53-s1952148-d93703104.state` | 2,278,071 | `1E8272F05EC19041394568C949BBDBF012EE72C1595BE7157C4BB0324D0B5727` | Cleanroom replica (identical) |
| `d:\Projects\ProteinSolver\notebooks\protein_4xEdgeConv_bs4/e12-s1652709-d6610836.state` | 2,278,037 | `AAA242C96A7DD6AB69DF2E260455BD8B6661481BD10BA3B1AFB3E68FE1792C06` | Cleanroom replica (identical) |

*Correction Record:* Prior draft reports introduced a hallucinated hash string (`c830026e...`). The true cryptographic hash for the published ProteinSolver model weights is confirmed as `1E8272F05EC19041394568C949BBDBF012EE72C1595BE7157C4BB0324D0B5727`.

---

## 9. Verification Basis vs. Final Closure Commit Separation

To preserve epistemic hygiene, the independent sources verifying the model and data are strictly distinguished from the final closure commit:

| Entity | Identifier / Commit / Hash | Epistemic Role |
| :--- | :--- | :--- |
| **Historical Upstream Source** | `69ef0965a3fc3bf191804035b539720a06e58ba6` | Independent primary implementation ground truth |
| **Research Repo Verification Basis** | `d961ef0b865f03d05a3df339b9f84b8f20c9ea56` | Parent research-repo commit grounding all audits |
| **Pretrained Checkpoint** | `1E8272F05EC19041394568C949BBDBF012EE72C1595BE7157C4BB0324D0B5727` | Verified cryptographic model weights SHA-256 |
| **Modern Implementation Reference** | `58255bc67323f5fd009ac85ae02fbf69c152c457` | Verified cleanroom implementation reference |
| **Final Closure Commit** | Pending single bounded commit | Packaging and freezing verified current authority |

---

## 10. Final Binary R2 Readiness Gate

Evaluation of the 25 release criteria:

- [x] **A. Final paper metadata correct?** Yes. *Cell Systems* 11(4): 402–411.e4, October 2020.
- [x] **B. Figure 1 exact panel semantics correct?** Yes. Strictly Figure 1A, 1B, 1C.
- [x] **C. Figure 2A = accuracy?** Yes. Canonicalized to training and validation accuracy trajectory.
- [x] **D. Figure 2B–F semantics correct?** Yes. Verified against published paper text and figures notebook.
- [x] **E. Figure 2G–N mapping exact?** Yes. Verified against published Cell Systems caption.
- [x] **F. Target identities correct?** Yes. 1N5U = Human Serum Albumin; 4BEU = Alanine racemase; 4UNU = Immunoglobulin lambda variable; 4Z8J = SNX27 PDZ domain.
- [x] **G. Domain/chain boundaries correct?** Yes. 4beuA02 = 217 AA domain artifact vs full biological chain.
- [x] **H. Self-loop behavior resolved?** Yes. Self-loops are strictly excluded; residual skip connections were previously mislabeled.
- [x] **I. Edge-feature dimensionality resolved?** Yes. Implementation uses 2 numeric channels entering `embed_adj` (`adj_input_size = 2`).
- [x] **J. Distance definition resolved?** Yes. Both paper and code use shortest heavy-atom distance ($< 12.0$ Å).
- [x] **K. Edge scaling resolved?** Yes. $(d - 6.0)/12.0$ and $(j - i)/68.1319$ are affine scalar transformations; 68.1319 is a fixed historical scaling constant.
- [x] **L. Batch-size contexts resolved?** Yes. Documented as batch size 4 (primary training) and batch size 1 (validation/eval).
- [x] **M. Checkpoint identity/hash independently verified?** Yes. Cryptographic SHA-256 = `1E8272F05EC19041394568C949BBDBF012EE72C1595BE7157C4BB0324D0B5727`.
- [x] **N. Corpus quantities role-separated?** Yes. 6-row reconciliation table deployed.
- [x] **O. EXP005 provenance acceptable?** Yes. $N = 3,471$, distinct Rosetta metrics preserved.
- [x] **P. EXP006 provenance acceptable?** Yes. Classified as preserved-statistics reconstruction; EEHEE Rd 4 exception preserved.
- [x] **Q. EXP007 epistemology acceptable?** Yes. $p > 0.05$ indicates failure to detect difference, not structural equivalence; 4beu $N = 1$ descriptive.
- [x] **R. EXP008 boundaries preserved?** Yes. Single-target MAP recovery diagnostic; full regeneration cost unbenchmarked.
- [x] **S. Current Tier-B contradiction sweep clean?** Yes. All verified contradictions eliminated.
- [x] **T. Verification basis separated from final closure commit?** Yes. Parent commit `d961ef0...` vs final closure commit.
- [x] **U. Research repo clean?** Verified prior to commit.
- [x] **V. Historical upstream untouched?** Clean at `69ef0965a3fc3bf191804035b539720a06e58ba6`.
- [x] **W. Modern implementation untouched?** Clean at `58255bc67323f5fd009ac85ae02fbf69c152c457`.
- [x] **X. Tests/preflight pass?** Verified via preflight CLI and test suite.
- [x] **Y. R2 scope remains strictly bounded?** Yes. Strictly scoped to:
  *Figure 2B and Figure 2C computational reproduction using the published pretrained checkpoint, with procedure/data definitions taken directly from the final Cell Systems paper and validated against historical notebooks before execution.*

### Final Binary Release Determination
**R2_READY**
