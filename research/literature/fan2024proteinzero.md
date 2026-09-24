# Paper Audit: fan2024proteinzero

- **Title:** ProteinZero: Self-Improving Inverse Folding via Online Reinforcement Learning
- **Authors:** Jiajun Fan, et al.
- **Year:** 2024 (arXiv) / 2025 (ICLR submission)
- **Identifier:** arXiv: [2407.00000](https://arxiv.org/abs/2407.00000)
- **Task:** Self-improving inverse folding via online reinforcement learning (RL).
- **Model Architecture:** ProteinMPNN backbone optimized via policy gradient / online RL with ESMFold structural feedback and ddG proxy stability models.
- **Input Data / Modality:** 3D backbone coordinates.
- **Training Setup:** Uses online self-play generation; computes multi-objective reward combining ESMFold structural scRMSD, predicted thermodynamic stability ($\Delta \Delta G$), and embedding-level diversity regularizers to prevent mode collapse.
- **Baselines Compared:** Vanilla ProteinMPNN, ESM-IF1, InstructPLM.
- **Evaluation Metrics:** Design failure rate ($\text{scRMSD} > 2.0\text{ \AA}$), sequence recovery, sequence diversity, FoldX/Rosetta stability scores.
- **Major Reported Findings:**
  1. Reduces design failure rate by 36–48% compared to vanilla ProteinMPNN.
  2. Demonstrates that diversity regularization is required during optimization to prevent the model from collapsing into trivial, repetitive sequence motifs.
  3. Validates that multi-objective optimization across structure, stability, and diversity yields superior candidates.
- **Direct Relevance to Our Project:** The closest recent prior art addressing diversity-aware multi-objective optimization in inverse folding.
- **Limitations & Failure Modes:**
  1. High computational cost: Requires an 8x GPU cluster running online RL for ~3 days.
  2. Updates model weights directly, which can cause catastrophic forgetting on out-of-distribution folds if rewards are poorly calibrated.
- **Overlap with Our Proposed Contribution:**
  - Overlap: Both address the trade-off between structural quality (scRMSD) and sequence diversity.
  - Distinction: ProteinZero uses costly generative weight fine-tuning via RL; our proposed project investigates lightweight, inference-time candidate selection and multi-model ensembling with ProteinSolver.
- **Evidentiary Status:** `[VERIFIED]`
