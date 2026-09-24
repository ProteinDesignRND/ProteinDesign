# Paper Audit: strokach2020proteinsolver

- **Title:** Fast and Flexible Protein Design Using Deep Graph Neural Networks
- **Authors:** Alexey Strokach, David Becerra, Carles Corbi-Verge, Albert Perez-Riba, Philip M. Kim
- **Year:** 2020
- **Venue:** Cell Systems 11(4): 402–411.e4
- **Identifier:** DOI: [10.1016/j.cels.2020.08.016](https://doi.org/10.1016/j.cels.2020.08.016) | GitHub: [ostrokach/proteinsolver](https://github.com/ostrokach/proteinsolver)
- **Task:** Structure-conditioned sequence design (Inverse Folding) framed as a Constraint Satisfaction Problem (CSP).
- **Model Architecture:** Residual Graph Neural Network with 4 residual blocks, updating node and edge representations using edge convolutions (`EdgeConv`) and layer normalization. Node and edge embedding dimension: 128.
- **Input Data / Modality:** Undirected graph where nodes are residues and edges represent spatial proximity. Distance cutoff: shortest heavy-atom distance $<12.0\text{ \AA}$. Edge features include shortest distance and sequence separation $|i - j|$.
- **Training Dataset & Split:** 72,464,122 sequence/adjacency-matrix pairs from 1,373 Gene3D superfamilies partitioned into 1,029 training, 172 validation, and 172 test superfamilies.
- **Training Objective:** Masked language modeling predicting ~50% randomly masked residues using cross-entropy loss.
- **Baselines Compared:** Rosetta fixed-backbone design (`fixbb`), random baseline.
- **Evaluation Metrics:** Native sequence recovery (~32–39% on Gene3D test domains), validation loss, classification of stable vs unstable designs on Rocklin miniproteins, correlation with $\Delta \Delta G$ on ProTherm.
- **Experimental Validation:** In vitro expression of de novo designed 4-helix bundle sequences; circular dichroism (CD) spectra showing $\alpha$-helical cooperativity; thermal denaturation; structure determination by NMR.
- **Direct Relevance to Our Project:** Foundational architecture under study. Defines the specific distance-graph CSP formulation.
- **Limitations & Failure Modes:**
  1. Relies purely on scalar distance cutoffs ($<12\text{ \AA}$) and sequence offset; cannot perceive 3D backbone frame orientations or chiral arrangements.
  2. Sequential CSP sampling is relatively slow during generation.
  3. Lower native sequence recovery compared to later equivariant and invariant MPNNs.
- **Overlap with Our Proposed Contribution:** Serves as the candidate constraint-satisfaction scoring prior.
- **Evidentiary Status:** `[VERIFIED]`
