# ORIGINAL PROTEINSOLVER: SPECIFICATION & SOURCE EVIDENCE

This document records the exact, source-grounded specifications of the original **ProteinSolver** model as described in the primary literature:
> **Strokach et al., 2020**, *"Fast and Flexible Protein Design Using Deep Graph Neural Networks"*, Cell Systems 11(4): 402–411.e4. DOI: [10.1016/j.cels.2020.08.016](https://doi.org/10.1016/j.cels.2020.08.016). Code: [ostrokach/proteinsolver](https://github.com/ostrokach/proteinsolver).

---

## 1. Graph Representation

- **Graph Definition:** A protein is represented as an attributed undirected graph $G = (V, E)$, where residues correspond to nodes and spatial interactions correspond to edges.
- **Nodes ($V$):**
  - Each node $v_i \in V$ corresponds to an amino acid position in the target sequence ($i = 1, \dots, N$).
  - Node feature vocabulary consists of the 20 standard amino acids plus a special `MASK` / unknown residue token (total vocabulary size: 21 or 22 with special tokens).
  - Node embedding dimension: **128**.
- **Edges ($E$):**
  - An edge $e_{ij} \in E$ is formed between residues $i$ and $j$ if the shortest Cartesian distance between any two heavy (non-hydrogen) atoms of residue $i$ and residue $j$ is **less than 12 Å** ($d_{ij} < 12\text{ \AA}$).
  - Self-loops ($i = j$) are omitted or handled via separate node update pathways.
- **Edge Features:**
  - Shortest Cartesian distance between any two heavy atoms $d_{ij}$. (In the implementation, distances are transformed via radial basis functions or scalar binning).
  - Sequence separation: $|i - j|$ (relative sequence position offset).
  - Edge embedding dimension: **128**.

---

## 2. Neural Network Architecture

- **Model Family:** Residual Graph Neural Network (GNN) based on modified Edge-Convolution (`EdgeConv`) layers.
- **Number of Blocks:** **4 residual blocks**.
- **Block Composition:**
  - Each residual block consists of:
    1. Edge update / edge convolution: Combines incoming node embeddings $h_i, h_j$ and current edge embedding $e_{ij}$ through a multi-layer perceptron (MLP).
    2. Node aggregation: Aggregates updated incident edge features $\sum_{j \in \mathcal{N}(i)} e_{ij}$ to update node state $h_i$.
    3. Layer Normalization (`LayerNorm`) applied across representations.
    4. Non-linear activation functions (`ReLU` / `ELU`).
    5. Residual (skip) connections adding input states to block outputs: $h^{(l+1)} = h^{(l)} + \text{Block}(h^{(l)})$.
- **Output Layer:**
  - A linear classification projection mapping final node embeddings $h_i \in \mathbb{R}^{128}$ to a 20-dimensional logit vector corresponding to the 20 standard amino acid probabilities:
    $$P(s_i = a \mid G) = \frac{\exp(z_{i, a})}{\sum_{a'=1}^{20} \exp(z_{i, a'})}$$

---

## 3. Training Objective & Dataset

- **Training Paradigm:** Masked Language Modeling / Constraint Satisfaction.
- **Masking Strategy:**
  - Approximately **50% of the residues** in each training structure are randomly masked (replaced with the `MASK` token).
  - The model is trained to predict the true identities of the masked residues given the unmasked residues and the full structural distance graph.
- **Loss Function:** Standard cross-entropy loss computed exclusively over the masked positions:
  $$\mathcal{L} = -\frac{1}{|\mathcal{M}|} \sum_{i \in \mathcal{M}} \log P(s_i = s_i^* \mid G)$$
  where $\mathcal{M}$ is the set of masked residue indices and $s_i^*$ is the ground-truth amino acid.
- **Training Corpus:**
  - Total instances: **72,464,122 sequence/adjacency-matrix pairs**.
  - Sourced from sequence and domain annotations associated with **1,373 Gene3D superfamilies**.
- **Superfamily Partition:**
  - **1,029** training superfamilies.
  - **172** validation superfamilies.
  - **172** test superfamilies.
  - Superfamily-level splitting ensures no structural topology leakage between train and evaluation sets.

---

## 4. Sequence Generation Mechanism (Inference as CSP)

- ProteinSolver frames sequence generation as solving a **Constraint Satisfaction Problem (CSP)**:
  1. Initialize all positions to be designed as `MASK`.
  2. Compute forward pass through the 4-block GNN to obtain class probabilities for all masked positions.
  3. Select a position (either with the highest prediction confidence, or sequentially, or according to a specific sampling schedule).
  4. Sample or greedily assign an amino acid at that position from its conditional distribution.
  5. Update the graph with the chosen amino acid, and repeat steps 2–5 until all positions are filled.
- **Scoring Mechanism:**
  - The model provides a log-likelihood or log-probability score representing how well a sequence satisfies the structural contact constraints:
    $$\text{Score}_{\text{PS}}(s \mid D) = \frac{1}{N} \sum_{i=1}^N \log P(s_i \mid G)$$

---

## 5. Original Validation Experiments

- **ProTherm Benchmark:**
  - Evaluated on predicting changes in thermodynamic stability ($\Delta \Delta G$) upon single-point mutations in the ProTherm database.
  - ProteinSolver scores showed statistically significant correlation with experimentally measured $\Delta \Delta G$.
- **Rocklin et al. De Novo Miniprotein Benchmark:**
  - Evaluated on thousands of computationally designed miniproteins tested for folding stability via high-throughput protease assays (Rocklin et al., Science 2017).
  - ProteinSolver assigned higher probabilities to stable designs than unstable designs.
- **De Novo In Vitro Experimental Validation:**
  - Designed novel sequences for 4-helix bundle topologies.
  - Expressed proteins in *E. coli*; validated via circular dichroism (CD) spectroscopy showing typical $\alpha$-helical spectra and cooperative thermal denaturation.
  - Solved atomic structures via NMR verifying fold agreement.

---

## 6. Known Gaps & Unrecorded Specifications
*Items where the exact literal implementation is not explicitly detailed in the main paper and must be verified in `ostrokach/proteinsolver` codebase:*
- **Distance Transformation:** Exact number of RBF kernels vs linear bins used to embed $d_{ij}$ (`[UNKNOWN - PENDING CODE CHECK]`).
- **Exact HDF5 Schema:** On-disk dataset column naming and compression filters (`[UNKNOWN - PENDING CODE CHECK]`).
- **Dropout & Learning Rate Schedule:** Exact initial learning rate and scheduler decay rate across the 72M training run (`[UNKNOWN - PENDING CODE CHECK]`).
