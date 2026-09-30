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
    (Note: This is an empirical affine scaling, not bounded $[0, 1]$ min-max normalization; with cutoff $12.0	ext{ \AA}$, values span approximately $[-0.5, +0.5]$).
  - **Sequence Separation Feature:** Directed sequence index offset $\Delta_{ij} = j - i$, transformed via:
    $$\Delta_{	ext{norm}} = rac{\Delta_{ij} - 0.0}{68.1319}$$
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
  - Non-linear Activation: Strictly **`ReLU()` / `F.relu()`** throughout all layers and inter-block transitions. (There is **no `ELU`** activation in `ProteinNet`).
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
- **Optimizer & Scheduler:**
  - Optimizer: `optim.Adam(net.parameters(), lr=1e-4)` with batch size 1 (or 4).
  - Scheduler: Strictly `optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", verbose=True)` tracking validation accuracy. (There is **no CosineAnnealing** in the historical training code).
  - Pretrained Checkpoint: `e53-s1952148-d93703104.state` (trained across 53 epochs, 1.95M optimizer steps, 937M samples seen).

---

## 4. Training Corpus & Data Formats

- **Training Corpus Structure:**
  - Total Training Instances: **72,464,122 sequence/adjacency-matrix pairs** (formed by pairing homologous sequences with representative structural domain graphs).
  - Sourced from **1,373 Gene3D superfamilies** partitioned at the superfamily level:
    - **1,029 training superfamilies** (75%)
    - **172 validation superfamilies** (12.5%)
    - **172 test superfamilies** (12.5%)
  - (Clarification: The claim that ProteinSolver was trained on "~4.4 million sequences across 70,000 CATH domains" was an ungrounded conflation with external CATH-ProteinNet datasets; the authoritative primary dataset is the 72,464,122 Gene3D pairs).
- **Data Storage Formats by Role:**
  - **Historical Training Corpus:** Serialized as Apache Parquet (`.snappy.parquet`) and Apache Arrow (`.arrow`) tables distributed via cloud storage (`http://deep-protein-gen.data.proteinsolver.org/`).
  - **Local Mutational Datasets (EXP005, EXP006):** CSV format (`protherm_design_wt_RUE.csv`, `GAPF_design_RUE_wt.csv`) and supplementary Parquet files (`rocklin_2017_ssm2_cartesian_ddg.parquet`, `rocklin_2017_ssm2_ddg_monomer.parquet`).
  - **Local CD Deconvolution (EXP007):** CSV format (`bestsel_results.csv`).
  - **Integration Targets (EXP008):** PDB format (`1n5uA03.pdb`, `4beuA02.pdb`, `4unuA00.pdb`, `4z8jA00.pdb`).

---

## 5. Inference Algorithms & Scoring

- **Inference Modes:**
  1. **One-Shot Generation:** All unassigned positions unmasked in a single forward pass ($x 	o 	ext{logits} 	o 	ext{argmax}$). Achieves ~27.29% native sequence recovery on test domains.
  2. **Incremental CSP Generation (Canonical Paper Method):** Iterative single-residue unmasking: at each step, the network identifies the unassigned node with highest prediction confidence, commits that amino acid, re-evaluates the graph, and repeats until all positions are filled. Achieves ~33-35% native sequence recovery.
  3. **Stochastic Sampling:** At each unmasking step, sample residues from softmax distributions scaled by temperature $T$: $P(s_i = c) \propto \exp(z_{ic} / T)$.
  4. **Exploratory Search (Notebook Extensions):** Priority-queue A* / best-first search over partial assignments (`design_protein`).
- **Sequence Scoring & Pseudo-Log-Likelihood:**
  - Evaluated via leave-one-out masking (`scan_with_mask` in `proteinsolver/utils/protein_design.py`). Passing fully unmasked sequences causes label leakage due to residual connections.
  - The model masks each position $i$ individually, queries the network, and gathers log-probabilities:
    $$	ext{PLL}(s \mid G) = \sum_{i=1}^N \log P(s_i \mid s_{\setminus i}, G)$$
  - Mutational change score: $\Delta 	ext{score} = 	ext{PLL}(s_{	ext{mut}} \mid G) - 	ext{PLL}(s_{	ext{wt}} \mid G)$.

---

## 6. Primary Literature Validation & Figure Correspondence

- **Final Published Paper Figure Layout (Cell Systems 2020, 11(4): 402-411.e4):**
  - **Figure 1:** Overview of ProteinSolver graph formulation, CSP analogy, network architecture, and masking.
  - **Figure 2 (Panels A–N):** The single comprehensive results figure in the main text:
    - *Figure 2A:* Training and validation loss trajectory across epochs.
    - *Figure 2B:* Native sequence recovery distributions (oneshot ~27.29% vs incremental ~33-35%).
    - *Figure 2C:* Sequence identity distributions under partial information (0%, 50%, 80% reference availability).
    - *Figure 2D:* ProTherm single-mutation $\Delta\Delta G$ correlation ($ho = 0.444$).
    - *Figure 2E:* Rocklin single-mutation stability correlation ($ho = 0.50$).
    - *Figure 2F:* Whole-protein stability correlation on Rosetta de novo designs.
    - *Figure 2G–N:* Computational design and experimental validation of Serum Albumin (1n5uA03).
  - **Supplementary Figures S3–S5:** Computational design evaluations for the other three target folds:
    - *Figure S3:* Alanine Racemase (4beuA02).
    - *Figure S4:* Immunoglobulin Light Chain (4unuA00).
    - *Figure S5:* PDZ3 Domain (4z8jA00).
- **Experimental Validation Scope:**
  - In vitro expression in *E. coli*, SDS-PAGE, and size-exclusion chromatography (SEC).
  - Far-UV Circular Dichroism (CD) spectroscopy and thermal denaturation curves.
  - **Important Provenance Correction:** The authors did **not** solve atomic structures via NMR or X-ray crystallography; experimental validation was strictly biophysical (CD and SEC).
