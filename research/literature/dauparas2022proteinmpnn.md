# Paper Audit: dauparas2022proteinmpnn

- **Title:** Robust deep learning–based protein sequence design using ProteinMPNN
- **Authors:** Justas Dauparas, Ivan Anishchenko, Nathaniel Bennett, Hua Bai, Robert J. Ragotte, Lukas F. Milles, Basile I. M. Wicky, Alexis Courbet, Robbert J. de Haas, Neville Bethel, Philip J. Y. Leung, Frank DiMaio, Timothy F. Baker, Sergey Ovchinnikov, David Baker
- **Year:** 2022
- **Venue:** Science 378(6615): 49–56
- **Identifier:** DOI: [10.1126/science.add2187](https://doi.org/10.1126/science.add2187) | GitHub: [dauparas/ProteinMPNN](https://github.com/dauparas/ProteinMPNN)
- **Task:** Structure-conditioned sequence design (Inverse Folding).
- **Model Architecture:** Message Passing Neural Network (MPNN) consisting of 3 encoder layers and 3 decoder layers. Autoregressive decoding with random decoding order permutations. Hidden dimension: 128.
- **Input Data / Modality:** 3D coordinates of protein backbone atoms (N, CA, C, O). Featurized via local reference frames, relative distances, relative orientations, and backbone torsion angles across $k=48$ nearest neighbors.
- **Training Dataset & Split:** CATH 4.2 non-redundant subset (topological split) augmented with PDB assemblies; structures filtered at 3.5 Å resolution.
- **Training Objective:** Cross-entropy loss predicting amino acid identity under random decoding orders.
- **Baselines Compared:** Rosetta fixed-backbone design, Structured Transformer (Ingraham et al. 2019), GVP-GNN (Jing et al. 2021).
- **Evaluation Metrics:** Native sequence recovery (51.6% on CATH 4.2 test set), perplexity, in silico structural self-consistency (scRMSD via AlphaFold2), extensive wet-lab rescue rates (crystallography, cryo-EM, binding affinity).
- **Experimental Validation:** Solved crystal structures and cryo-EM structures for diverse monomeric, oligomeric, and binder designs; rescued failed Rosetta designs with >10-fold improved expression.
- **Direct Relevance to Our Project:** The universally acknowledged state-of-the-art benchmark for sequence design. Serves as our primary candidate sequence generator.
- **Limitations & Failure Modes:**
  1. Low-temperature sampling ($T=0.1$–$0.2$) leads to severe mode collapse (near-identical sequences in a generated library).
  2. Does not incorporate explicit multi-objective Pareto optimization or diversity regularization during candidate selection.
- **Overlap with Our Proposed Contribution:** Acts as the primary generative sequence engine in our pipeline.
- **Evidentiary Status:** `[VERIFIED]`
