# PROTEINSOLVER: DETAILED ARCHITECTURAL SPECIFICATION

This document provides a formal, in-depth technical specification of the original **ProteinSolver** neural network architecture based on Strokach et al. (Cell Systems 2020) and the reference PyTorch Geometric implementation (`ostrokach/proteinsolver`).

---

## 1. Mathematical Representation of the Input Graph

A target protein of length $N$ residues is mapped to a spatial interaction graph $G = (V, E, \mathbf{X}_v, \mathbf{X}_e)$:

1. **Node Set ($V$):**
   - $V = \{v_1, v_2, \dots, v_N\}$.
   - Node feature vector $\mathbf{x}_i \in \{0, 1\}^{22}$ (one-hot encoding of 20 standard amino acids, 1 unknown token, and 1 `MASK` token).
2. **Edge Set ($E$):**
   - An edge exists between residue $i$ and residue $j$ if and only if:
     $$\min_{a \in \text{atoms}(i), b \in \text{atoms}(j)} \|\mathbf{r}_{i, a} - \mathbf{r}_{j, b}\|_2 < 12.0\text{ \AA}$$
   - Self-loops are excluded from the adjacency matrix.
3. **Edge Feature Vector ($\mathbf{e}_{ij}$):**
   - Shortest heavy-atom Cartesian distance $d_{ij}$.
   - Sequence position offset: $\Delta_{ij} = |i - j|$.
   - In implementation: $d_{ij}$ and $\Delta_{ij}$ are projected through embedding layers / radial basis functions into continuous vectors $\mathbf{e}_{ij}^{(0)} \in \mathbb{R}^{128}$.

---

## 2. Embedding Layers

- **Node Embedding:**
  $$\mathbf{h}_i^{(0)} = \mathbf{W}_v \mathbf{x}_i + \mathbf{b}_v, \quad \mathbf{h}_i^{(0)} \in \mathbb{R}^{128}$$
- **Edge Embedding:**
  $$\mathbf{e}_{ij}^{(0)} = \mathbf{W}_e \phi(d_{ij}, \Delta_{ij}) + \mathbf{b}_e, \quad \mathbf{e}_{ij}^{(0)} \in \mathbb{R}^{128}$$
  where $\phi(\cdot)$ is the distance and sequence featurizer.

---

## 3. Residual Edge-Convolution Blocks (4 Blocks)

The network stacks **4 identical residual blocks**. In each block $l \in \{1, 2, 3, 4\}$, node and edge states are updated via message passing:

### A. Edge Representation Update
For each directed edge $(i, j) \in E$, an updated edge representation is computed by concatenating the source node state, destination node state, and the previous edge state:
$$\tilde{\mathbf{e}}_{ij}^{(l)} = \text{MLP}_e^{(l)}\left([\mathbf{h}_i^{(l-1)} \,\|\, \mathbf{h}_j^{(l-1)} \,\|\, \mathbf{e}_{ij}^{(l-1)}]\right)$$
$$\mathbf{e}_{ij}^{(l)} = \text{LayerNorm}\left(\mathbf{e}_{ij}^{(l-1)} + \tilde{\mathbf{e}}_{ij}^{(l)}\right)$$

### B. Node Representation Update
Edge messages incident to node $i$ are aggregated (summed) and combined with the current node state:
$$\mathbf{m}_i^{(l)} = \sum_{j \in \mathcal{N}(i)} \mathbf{e}_{ij}^{(l)}$$
$$\tilde{\mathbf{h}}_i^{(l)} = \text{MLP}_v^{(l)}\left([\mathbf{h}_i^{(l-1)} \,\|\, \mathbf{m}_i^{(l)}]\right)$$
$$\mathbf{h}_i^{(l)} = \text{LayerNorm}\left(\mathbf{h}_i^{(l-1)} + \tilde{\mathbf{h}}_i^{(l)}\right)$$

- **Activation Function:** Non-linear activations (`ReLU` / `ELU`) are applied within intermediate MLP layers.
- **Hidden Dimensions:** All intermediate MLP layers maintain dimension 128.

---

## 4. Output Classification Head

After 4 residual blocks, the final node representations $\mathbf{h}_i^{(4)} \in \mathbb{R}^{128}$ are projected into the 20 amino acid output classes:
$$\mathbf{z}_i = \mathbf{W}_{\text{out}} \mathbf{h}_i^{(4)} + \mathbf{b}_{\text{out}}, \quad \mathbf{z}_i \in \mathbb{R}^{20}$$
$$P(s_i = a \mid G) = \frac{\exp(z_{i, a} / T)}{\sum_{a'=1}^{20} \exp(z_{i, a'} / T)}$$
where $T$ is the sampling temperature.

---

## 5. Constraint Satisfaction Sequence Generation Protocol

Because the network was trained with 50% random masking, generating a full sequence is executed iteratively as a Constraint Satisfaction Problem:

```python
# Algorithmic sketch of CSP sequence design
def generate_sequence_csp(distance_graph, mask_token_id, T=0.1):
    seq = [mask_token_id] * num_nodes
    unassigned = set(range(num_nodes))
    
    while unassigned:
        logits = model(seq, distance_graph)  # [N, 20]
        probs = softmax(logits / T, dim=-1)
        
        # Strategy A: Pick position with maximum confidence
        best_pos = max(unassigned, key=lambda i: probs[i].max().item())
        
        # Sample amino acid at best_pos
        aa = sample_categorical(probs[best_pos])
        seq[best_pos] = aa
        unassigned.remove(best_pos)
        
    return seq
```

---

## 6. Structural Differences Compared to Modern Invariant/Equivariant MPNNs

| Architectural Property | ProteinSolver (2020) | ProteinMPNN (2022) | PiFold (2023) |
|---|---|---|---|
| **Input Modality** | Distance matrix ($d_{ij} < 12\text{ \AA}$) | Atomic 3D backbone coords (N, CA, C, O) | Atomic 3D backbone coords |
| **Coordinate Invariance** | Pairwise distances are trivially SE(3)-invariant | Constructed via local reference frames (rigid body transformations) | Constructed via multi-scale geometric angles/vectors |
| **Orientation Awareness** | **NO** (Cannot distinguish chiral flips or backbone torsion angles) | **YES** (Uses relative rotation matrices between residue frames) | **YES** (Uses 3D directional unit vectors and torsion angles) |
| **Decoding Strategy** | Iterative masked prediction (CSP) | Autoregressive with random order permutation | Non-autoregressive (single forward pass) |
| **Number of Parameters** | ~1.5 Million | ~1.8 Million | ~2.5 Million |
