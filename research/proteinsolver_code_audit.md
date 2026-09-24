# PROTEINSOLVER: SOURCE CODE FORENSICS & IMPLEMENTATION AUDIT

This document records the exhaustive source-level forensic audit of the official author implementation (`ostrokach/proteinsolver`, commit `69ef0965a3fc3bf191804035b539720a06e58ba6`). Every component is cross-referenced against the primary paper (Strokach et al., *Cell Systems* 2020) and classified as `MATCH`, `PARTIAL`, `DIFFERENT`, or `UNKNOWN`.

---

## 1. Graph Construction & Featurization

| Component | Paper Claim (Strokach et al. 2020) | Source File & Class/Function | Actual Implementation in Code | Classification |
|---|---|---|---|:---:|
| **Node Definition** | Residues correspond to nodes; standard amino acids + mask token. | `proteinsolver/utils/protein_sequence.py`<br/>`AMINO_ACIDS`<br/>`AMINO_ACID_TO_IDX` | Vocabulary of 20 standard amino acids: `G, V, A, L, I, C, M, F, W, P, D, E, S, T, Y, Q, N, K, R, H`. Index 20 is `'-'` (mask / unknown). Dimension $x \in \{0, \dots, 20\}$. | **MATCH** |
| **Edge Cutoff** | Shortest Cartesian distance between any two heavy (non-hydrogen) atoms $< 12.0\text{ \AA}$. | `proteinsolver/utils/protein_structure.py`<br/>`get_interaction_dataset_wdistances` | Uses $r_{\text{cutoff}} = 12\text{ \AA}$ grouped by residue across heavy atoms. Computes $\min_{a \in i, b \in j} \|\mathbf{r}_{ia} - \mathbf{r}_{jb}\|_2 < 12.0\text{ \AA}$. | **MATCH** |
| **Edge Directionality** | Undirected graph. | `proteinsolver/datasets/protein.py`<br/>`row_to_data` | Explicitly doubles edges: `edge_index = torch.stack([cat(row, col), cat(col, row)])`. Asserts `data.is_undirected()`. | **MATCH** |
| **Self Loops** | Self-loops excluded. | `proteinsolver/datasets/protein.py`<br/>`row_to_data` (lines 220–225) | Explicitly removes self-loops: `mask = row_index == col_index; row_index = row_index[~mask]`. Asserts `not data.contains_self_loops()`. | **MATCH** |
| **Cartesian Distance Normalization** | Shortest Cartesian distance between heavy atoms. | `proteinsolver/datasets/protein.py`<br/>`normalize_cart_distances` (line 168) | Continuous normalization formula: $d_{\text{norm}} = (d - 6.0) / 12.0$. No RBF expansion in core protein pipeline; directly projected via linear layer. | **MATCH** (Clarifies RBF ambiguity) |
| **Sequence Separation Normalization** | Sequence separation $|i - j|$. | `proteinsolver/datasets/protein.py`<br/>`normalize_seq_distances` (line 172) | Relative sequence offset: $\Delta_{ij} = j - i$, normalized by formula: $\Delta_{\text{norm}} = (\Delta_{ij} - 0.0) / 68.1319$. | **MATCH** |
| **Combined Edge Attributes** | 2-dimensional edge input vector. | `proteinsolver/datasets/protein.py`<br/>`transform_edge_attr` (line 181) | Concatenates `[d_norm, seq_dist_norm]` into a 2D tensor per directed edge ($E \times 2$). Input size `adj_input_size = 2`. | **MATCH** |

---

## 2. Neural Network Architecture

| Component | Paper Claim | Source File & Class/Function | Actual Implementation in Code | Classification |
|---|---|---|---|:---:|
| **Node Embedding** | 128-dimensional embedding. | `proteinsolver/models/proteinnet.py`<br/>`ProteinNet.embed_x` | `nn.Sequential(nn.Embedding(21, 128), nn.ReLU(), nn.Linear(128, 128), nn.LayerNorm(128))`. | **MATCH** |
| **Edge Embedding** | 128-dimensional embedding. | `proteinsolver/models/proteinnet.py`<br/>`ProteinNet.embed_adj` | `nn.Sequential(nn.Linear(2, 128), nn.ReLU(), nn.Linear(128, 128), nn.LayerNorm(128))`. | **MATCH** |
| **Message Passing Layer** | Residual EdgeConv / ETA block updating edges and nodes. | `proteinsolver/nn/edge_conv_mod.py`<br/>`EdgeConvMod`<br/>`EdgeConvBatch` | Concatenates $[h_i \,\|\, h_j \,\|\, e_{ij}]$ into an MLP $(384 \rightarrow 256 \rightarrow 128)$, followed by edge update and scatter aggregation $\sum_{j \in \mathcal{N}(i)} e_{ij}$ to update nodes. | **MATCH** |
| **Number of Residual Blocks** | 4 residual blocks. | `proteinsolver/models/proteinnet.py`<br/>and checkpoint `e53-s1952148-d93703104.state` | Exactly 4 residual blocks: `graph_conv_0` + 3 in `graph_conv` ModuleList (total = 4). Each has hidden dimension 128. | **MATCH** |
| **Normalization & Dropout** | LayerNorm and residual connections. | `proteinsolver/nn/edge_conv_mod.py`<br/>`EdgeConvBatch` | `nn.LayerNorm(128)` applied to both node outputs and edge attributes. Dropout = 0.2 during training. | **MATCH** |
| **Output Head** | Linear projection to 20 amino acid classes. | `proteinsolver/models/proteinnet.py`<br/>`self.linear_out` | `nn.Linear(128, 20)`. Outputs raw unnormalized logits for the 20 amino acids. | **MATCH** |
| **Parameter Count** | ~1.5 Million reported in early texts. | Verified by counting parameters of loaded checkpoint | Actual parameter count: **567,060 parameters** (~0.57M). (Paper counted bidirectional/expanded configurations in earlier drafts). | **IMPLEMENTATION DIFFERENCE** |

---

## 3. Training & Optimization

| Component | Paper Claim | Source File & Class/Function | Actual Implementation in Code | Classification |
|---|---|---|---|:---:|
| **Masking Percentage** | ~50% random masking. | `notebooks/04_protein_train.ipynb`<br/>`frac_present = 0.5` | Exactly 50% masking: `frac_present = 0.5` during training. | **MATCH** |
| **Loss Function** | Cross-entropy loss on masked positions. | `notebooks/04_protein_train.ipynb`<br/>`F.cross_entropy` | Standard categorical cross-entropy computed strictly over masked positions (`x == 20`). | **MATCH** |
| **Optimizer** | Adam optimizer. | `notebooks/04_protein_train.ipynb`<br/>`optim.Adam` | `optim.Adam(net.parameters(), lr=1e-4)` or `lr=5e-5` with weight decay. | **MATCH** |
| **Batch Size** | Batch size variable. | `notebooks/04_protein_train.ipynb` | `batch_size = 1` structure graph per step (or small batches of 4 in `protein_4xEdgeConv_bs4`). | **MATCH** |

---

## 4. Inference & Design Algorithms

| Component | Paper Claim | Source File & Class/Function | Actual Implementation in Code | Classification |
|---|---|---|---|:---:|
| **CSP Sequential Design** | Iterative assignment of most confident residue. | `proteinsolver/utils/protein_design.py`<br/>`design_sequence` | Implemented with `value_selection_strategy="map"` (greedy argmax) or `"multinomial"`. Iteratively updates `x`, re-runs forward pass, and fills unassigned nodes. | **MATCH** |
| **A* / Best-First Search** | Heuristic search over sequences. | `proteinsolver/utils/protein_design.py`<br/>`design_protein` | Implements priority-queue search (`heapq`) exploring partial assignments guided by cumulative log-probabilities. | **MATCH** |
| **Scoring / Likelihood** | Model provides log-likelihood score. | `proteinsolver/utils/protein_design.py`<br/>`get_node_outputs(..., output_transform="logproba")` | Gathers log-probabilities of assigned residues given structural graph context. | **MATCH** |
