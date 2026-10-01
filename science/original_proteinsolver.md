# ORIGINAL PROTEINSOLVER: SPECIFICATION & SOURCE EVIDENCE

This document records the exact, source-grounded specifications of the original **ProteinSolver** model as described in the primary literature:
> **Strokach et al., 2020**, *"Fast and Flexible Protein Design Using Deep Graph Neural Networks"*, Cell Systems 11(4): 402-411.e4. DOI: [10.1016/j.cels.2020.08.016](https://doi.org/10.1016/j.cels.2020.08.016). Code: [ostrokach/proteinsolver](https://github.com/ostrokach/proteinsolver) (commit `69ef0965a3fc3bf191804035b539720a06e58ba6`).

---

## 1. Graph Representation

- **Graph Definition:** A protein structure is represented as an attributed undirected graph $G = (V, E)$, where residues correspond to nodes and spatial proximity corresponds to edges.
- **Nodes ($V$):**
  - Each node $v_i \in V$ corresponds to an amino acid position in the target sequence ($i = 1, \dots, N$).
  - **Node Vocabulary:** Exactly **21 categories** (20 standard canonical amino acids: `G, V, A, L, I, C, M, F, W, P, D, E, S, T, Y, Q, N, K, R, H` at indices $0 \dots 19$, plus index **20** as the `'-'` mask / unknown token; defined in `proteinsolver/utils/protein_sequence.py`).
  - **Node Embedding:** `nn.Sequential(nn.Embedding(21, 128), nn.ReLU(), nn.Linear(128, 128), nn.LayerNorm(128))` projecting discrete residue indices into $\mathbb{R}^{128}$.
- **Edges ($E$):**
  - An edge $e_{ij} \in E$ is formed between residues $i$ and $j$ if the shortest Cartesian distance between any two heavy (non-hydrogen) atoms of residue $i$ and residue $j$ is **strictly less than 12.0 \AA** ($d_{ij} < 12.0	ext{ \AA}$).
  - Edges are directed in implementation ($E 	imes 2$), with reversed edges added to ensure an undirected topology ($i 	o j$ and $j 	o i$).
  - **Self-Loops:** Strictly **excluded**. In `proteinsolver/datasets/protein.py`, self-loops are filtered during construction (`row_index != col_index`), and in `ProteinNet.forward`, `remove_self_loops(edge_index)` is explicitly invoked. Node self-state updates occur exclusively through additive residual skip connections ($x \leftarrow x + x_{	ext{out}}$).
- **Edge Features:**
  - **Cartesian Distance Feature:** Shortest heavy-atom distance $d_{ij}$, transformed via an **affine scalar linear transformation**:
    $$d_{	ext{norm}} = rac{d_{ij} - 6.0}{12.0}$$
    using offset 6.0 and scale 12.0. With distance cutoff $12.0	ext{ \AA}$, values span approximately $[-0.5, +0.5]$.
  - **Sequence Separation Feature:** Directed sequence index offset $\Delta_{ij} = j - i$ (where $i$ is source and $j$ is target), transformed via an affine linear transformation:
    $$\Delta_{	ext{norm}} = rac{\Delta_{ij} - 0.0}{68.1319}$$
    using offset 0.0 and scale 68.1319.
  - **Edge Embedding:** Concatenated 2-channel edge tensor $[d_{	ext{norm}}, \Delta_{	ext{norm}}] \in \mathbb{R}^{E 	imes 2}$, embedded via:
    `nn.Sequential(nn.Linear(2, 128), nn.ReLU(), nn.Linear(128, 128), nn.LayerNorm(128))` into $\mathbb{R}^{128}$.

---

## 2. Neural Network Architecture

- **Model Architecture:** Residual Graph Neural Network (`ProteinNet` / `ProteinSolverNet`) with **4 sequential residual EdgeConv blocks** (`graph_conv_1` through `graph_conv_4`).
- **Parameter Count:** Exactly **567,060 trainable parameters** (2.28 MB checkpoint `e53-s1952148-d93703104.state`).
- **Block Composition:**
  - Each `EdgeConvMod` layer takes concatenated representations $[h_i \,\|\, h_j \,\|\, e_{ij}] \in \mathbb{R}^{384}$.
  - Edge MLP: `nn.Sequential(nn.Linear(384, 256), nn.ReLU(), nn.Linear(256, 128))` updating edge state.
  - Node Aggregation: Summed scatter aggregation $\sum_{j \in \mathcal{N}(i)} e_{ij}$ over incoming edges to update node state.
  - Normalization: `nn.LayerNorm(128)` applied within `EdgeConvBatch` with training `dropout = 0.2`.
  - Non-linear Activation: Strictly **`ReLU()` / `F.relu()`** throughout all layers and inter-block transitions. (There is no `ELU` activation in `ProteinNet`).
  - Residual Connections: Additive skip connections for both nodes ($x \leftarrow x + x_{	ext{out}}$) and edges ($e \leftarrow e + e_{	ext{out}}$) after each block.
- **Output Head:**
  - A single linear projection `self.linear_out = nn.Linear(128, 20)` mapping final residue embeddings $h_i \in \mathbb{R}^{128}$ to unnormalized raw logits for the **20 canonical amino acids**.
  - The mask token (`index 20`) is **not** an output class.
  - Softmax / log-softmax is applied externally during loss evaluation or sampling.

---

## 3. Training Objective & Optimization

- **Training Paradigm:** Masked Language Modeling / Constraint Satisfaction Problem (CSP).
- **Masking Procedure:**
  - Performed dynamically per batch. Each residue is subjected to an independent Bernoulli trial with $p = 0.5$ (`frac_present = 0.5`):
    $$x_i = egin{cases} y_i & 	ext{with probability } 0.5 \ 20	ext{ (mask)} & 	ext{with probability } 0.5 \end{cases}$$
  - Masking is approximate (~50% of positions per structure), not an exact fixed count.
  - Validation masking uses the identical parameter (`frac_present_valid = 0.5`).
- **Loss Function:** Standard categorical cross-entropy loss computed strictly over masked positions ($x_i = 20$):
  $$\mathcal{L} = -rac{1}{|\mathcal{M}|} \sum_{i \in \mathcal{M}} \log P(s_i = s_i^* \mid \mathbf{x}_{	ext{masked}}, G)$$
- **Optimizer, Batch Size & Scheduler:**
  - Optimizer: `optim.Adam(net.parameters(), lr=1e-4)`.
  - **Batch Size:** Historical training used `batch_size = 4` structure graphs per step in the default 4-layer GCN training run (`04_protein_train.ipynb`), while validation evaluation and earlier exploratory runs (e.g. `0007604c`) used `batch_size = 1`.
  - Scheduler: Strictly `optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", verbose=True)` tracking validation accuracy. (There is no `CosineAnnealing` in the historical training code).
  - Pretrained Checkpoint: `e53-s1952148-d93703104.state` (trained across 53 epochs, 1.95M optimizer steps, 937M samples seen).

---

## 4. Training Corpus Reconciliation & Data Formats

### A. Training Corpus Layers
To resolve past descriptive contradictions, the training corpus is reconciled across its distinct structural and sequence layers:

| Layer / Quantity | Meaning | Source | Exact / Approx | Role in Study |
|:---|:---|:---|:---:|:---|
| **>70 Million Sequences** | Broad sequence universe mapped to structural domains | Published Cell Systems headline | Approximate | Macro headline of sequence diversity |
| **>80,000 Structures** | PDB structural domains providing contact topologies | Published Cell Systems headline | Approximate | Macro headline of structural coverage |
| **~72 Million Unique Domains** | Non-redundant Gene3D domain sequences from UniParc | Published Gene3D framing | Approximate | Domain sequence collection |
| **72,464,122 Records** | Prepared sequence/adjacency structural training pairs | Upstream dataset inventory | Exact | Model training instance corpus |
| **1,373 Gene3D Superfamilies** | Structural superfamilies partitioning the dataset | Primary paper & notebooks | Exact | Superfamily-level split basis |
| **1,029 / 172 / 172 Split** | Superfamily partition: Train (75%), Val (12.5%), Test (12.5%) | Primary paper & notebooks | Exact | Zero-topology-leakage partition |

*Canonical Phrasing:* Published paper: >70M sequences corresponding to >80k structures. The repository's prepared structural-pair inventory contains 72,464,122 records, where directly verified; these are not to be presented as a replacement for the paper's scientific headline.

### B. Data Storage Formats by Role
- **Historical Training Corpus:** Serialized as Apache Parquet (`.snappy.parquet`) and Apache Arrow (`.arrow`) tables distributed via cloud storage (`http://deep-protein-gen.data.proteinsolver.org/`).
- **Local Mutational Datasets (EXP005, EXP006):** CSV format (`protherm_design_wt_RUE.csv`, `GAPF_design_RUE_wt.csv`) and supplementary Parquet files (`rocklin_2017_ssm2_cartesian_ddg.parquet`, `rocklin_2017_ssm2_ddg_monomer.parquet`).
- **Local CD Deconvolution (EXP007):** CSV format (`bestsel_results.csv`).
- **Integration Targets (EXP008):** PDB format (`1n5uA03.pdb`, `4beuA02.pdb`, `4unuA00.pdb`, `4z8jA00.pdb`).

---

## 5. Inference Algorithms & Scoring

- **Inference Modes:**
  1. **One-Shot Generation:** All unassigned positions unmasked in a single forward pass ($x \to \text{logits} \to \text{argmax}$). (Historical notebook aggregate achieves 27.29% mean one-shot recovery across 1,283 test records in `06_protein_analysis.ipynb` Cell 35–36; published Figure 2B evaluates single-pass vs. repeated most-confident predictions on a test dataset of 10,000 sequence/adjacency-matrix instances).
  2. **Incremental CSP Generation (Canonical Paper Method):** Iterative single-residue unmasking: at each step, the network identifies the unassigned node with highest prediction confidence, commits that amino acid, re-evaluates the graph, and repeats until all positions are filled. (Compares against single-pass decoding on the published 10,000 sequence/adjacency test dataset in Figure 2B).
  3. **Stochastic Sampling:** At each unmasking step, sample residues from softmax distributions scaled by temperature $T$: $P(s_i = c) \propto \exp(z_{ic} / T)$.
  4. **Exploratory Search (Notebook Extensions):** Priority-queue A* / best-first search over partial assignments (`design_protein`). This is an implementation extension, not a canonical main-paper method.
- **Sequence Scoring & Pseudo-Log-Likelihood:**
  - Evaluated via leave-one-out masking (`scan_with_mask` in `proteinsolver/utils/protein_design.py`), representing the historical implementation scoring path:
    $$	ext{PLL}(s \mid G) = \sum_{i=1}^N \log P(s_i \mid s_{\setminus i}, G)$$
  - Mutational change score: $\Delta 	ext{score} = 	ext{PLL}(s_{	ext{mut}} \mid G) - 	ext{PLL}(s_{	ext{wt}} \mid G)$.

---

## 6. Primary Literature Validation & Exact Figure Correspondence

### A. Published Cell Systems 2020 Figure Inventory
The published peer-reviewed article (*Cell Systems* 11(4): 402–411.e4) contains strictly **Figure 1** and **Figure 2 (Panels A–N)** in the main text, with other targets placed in **Supplementary Figures S3–S5**:

- **Figure 1: Concept, Network Architecture, and CSP Formulation**
  - **Figure 1A:** ProteinSolver network architecture.
  - **Figure 1B:** Training a ProteinSolver network to solve Sudoku puzzles.
  - **Figure 1C:** Training a ProteinSolver network to reconstruct protein sequences.
  *(Note: Figure 1 contains strictly panels 1A, 1B, and 1C; it does not contain panels 1D or 1E).*
- **Figure 2: Empirical Performance, Biophysical Correlations, and De Novo Design (Panels A–N)**
  - **Figure 2A:** Training and validation accuracy trajectory across epochs (at ~100M training examples, training accuracy reaches ~22% and validation accuracy ~32% under 50% random masking).
  - **Figure 2B:** Native sequence recovery distributions on independent Gene3D test dataset (published paper evaluates 10,000 sequence and adjacency matrix instances comparing single-pass predictions [blue] vs. repeated prediction committing the most-confident residue [red]; historical notebook aggregate in `06_protein_analysis.ipynb` Cell 35–36 reports 27.29% mean one-shot recovery across 1,283 records as an auxiliary diagnostic).
  - **Figure 2C:** Sequence identity distributions under partial sequence availability (0%, 50%, 80% unmasked).
  - **Figure 2D:** ProTherm single-point mutation stability ($\Delta\Delta G$) correlation (Spearman $
ho = 0.444$).
  - **Figure 2E:** Rocklin single-point mutation stability correlation (Spearman $
ho = 0.50$).
  - **Figure 2F:** Whole-protein stability correlation on Rosetta de novo designs across 4 topologies.
  - **Figure 2G:** Contact map and structural geometry of serum albumin (1n5uA03).
  - **Figure 2H:** ProteinSolver scores vs. generated-sequence identity analysis.
  - **Figure 2I:** Sequence logo of generated designs.
  - **Figure 2J:** Secondary-structure and topology logo.
  - **Figure 2K:** MODELLER / Rosetta structural-energy analysis.
  - **Figure 2L:** QUARK structural prediction and comparison.
  - **Figure 2M:** 100-ns molecular dynamics residue fluctuation analysis.
  - **Figure 2N:** Circular dichroism (CD) spectra.
- **Supplementary Figures S3–S5: Target Fold Computational Designs**
  - **Figure S3:** Alanine Racemase fold design (`4beuA02`, 217 AA domain artifact spanning residues 49 to 265 of Chain A; full biological chain in PDB 4BEU is larger).
  - **Figure S4:** Immunoglobulin Light Chain fold design (`4unuA00`, 109 AA domain artifact).
  - **Figure S5:** PDZ3 Domain fold design (`4z8jA00`, 96 AA domain artifact).

### B. Experimental Validation Scope
The published study reports biophysical experimental validation including circular dichroism; the paper does not report atomic structure determination by NMR/X-ray as part of this validation.
