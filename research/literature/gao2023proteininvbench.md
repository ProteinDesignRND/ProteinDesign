# Paper Audit: gao2023proteininvbench

- **Title:** Benchmarking Evaluated Protein Inverse Folding Models
- **Authors:** Zhangyang Gao, Cheng Tan, Stan Z. Li
- **Year:** 2023 (NeurIPS 2023 Datasets & Benchmarks) / 2024 (Briefings in Bioinformatics)
- **Identifier:** arXiv: [2306.16819](https://arxiv.org/abs/2306.16819) | GitHub: [A4Bio/OpenCPD](https://github.com/A4Bio/OpenCPD)
- **Task:** Standardized benchmark evaluation of deep learning inverse-folding algorithms.
- **Models Evaluated:** ProteinSolver, ProteinMPNN, PiFold, ESM-IF1, AlphaDesign, GraphTrans, StructGNN, GVP.
- **Input Data / Modality:** Standardized PDB backbones across multiple datasets.
- **Datasets Used:** CATH 4.2, TS50, TS500, CASP15 targets, and de novo designed structures.
- **Evaluation Metrics:**
  - Native Sequence Recovery (AAR)
  - Self-Consistency RMSD (scRMSD) using ESMFold / AlphaFold2
  - Self-Consistency TM-score (scTM)
  - Sequence Diversity (mean pairwise distance)
  - Inference Latency (seconds per sequence)
- **Major Reported Findings:**
  1. ProteinMPNN, PiFold, and ESM-IF1 form the top tier of sequence recovery (~51–52% on CATH 4.2).
  2. ProteinSolver achieves ~32.8% on CATH 4.2, significantly trailing modern models in raw sequence recovery.
  3. However, ProteinSolver exhibits distinct sequence diversity profiles and alternative amino acid composition distributions.
  4. Structural self-consistency drops precipitously when sequence recovery falls below ~35%, unless guided by partial sequence constraints or structural filtering.
- **Direct Relevance to Our Project:** Provides the most authoritative, independent, and direct empirical comparison between ProteinSolver and ProteinMPNN on identical test splits.
- **Limitations & Failure Modes:** Benchmark study only; did not investigate hybrid ensembling or multi-objective candidate selection.
- **Overlap with Our Proposed Contribution:** Establishes the exact baseline numbers and comparative metrics against which our evaluation must be measured.
- **Evidentiary Status:** `[VERIFIED]`
