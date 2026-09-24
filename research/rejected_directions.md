# REJECTED RESEARCH DIRECTIONS & DISCARDED METHODOLOGIES

This document records research avenues, architectural designs, and experimental formulations that have been evaluated and deliberately rejected. Recording rejected paths prevents redundant exploration, protects project scope, and maintains high scientific integrity.

---

## 1. Rejected Direction: Retraining Foundation Models from Scratch
- **Proposal:** Download the complete 72,464,122 sequence/adjacency-matrix Gene3D corpus and train a new ProteinSolver model from random initialization.
- **Reason for Rejection:**
  - **Prohibitive Computational Overhead:** Training across 72M pairs requires hundreds of GPU hours, massive storage (>1 TB), and weeks of runtime.
  - **Zero Scientific Incremental Value:** Retraining would replicate Strokach et al.'s already-converged model without addressing any new theoretical question.
  - **Decision:** Use the official published model weights from `ostrokach/proteinsolver` for inference and scoring.

---

## 2. Rejected Claim: Claiming Sequence Generation + Structure Validation as Novel
- **Proposal:** Pitch the combination of deep learning inverse folding with AlphaFold2 self-consistency verification as a novel pipeline contribution.
- **Reason for Rejection:**
  - **Ubiquitous Prior Art:** Watson et al. (*Nature* 2023, RFdiffusion) and hundreds of follow-up studies have made `Inverse Folding + AlphaFold2 Validation` the universal community standard.
  - **Severe Credibility Risk:** Any reviewer would immediately flag this claim as ignorance of canonical prior art.
  - **Decision:** Treat structural validation strictly as a standard evaluation oracle and control, not as an invented contribution.

---

## 3. Rejected Direction: Full-Scale Online Reinforcement Learning (RL)
- **Proposal:** Train an online RL policy (similar to PPO or DPO) to update ProteinSolver or ProteinMPNN weights using AlphaFold / ESMFold rewards.
- **Reason for Rejection:**
  - **Prior Art Preemption:** ProteinZero (Fan et al., arXiv 2024 / ICLR 2025) has already executed this exact formulation (online RL on inverse folding with ESMFold + ddG rewards and diversity regularizers).
  - **Resource Infeasibility:** RL on 3D folding oracles requires high-end multi-GPU clusters and days of wall-clock time per run.
  - **Decision:** Focus on **inference-time / test-time** multi-objective candidate selection and scoring complementarity, which requires no fine-tuning and provides immediate practical utility to practitioners with single-GPU workstations.

---

## 4. Rejected Metric: Relying Solely on Native Sequence Recovery (AAR)
- **Proposal:** Optimize and evaluate models purely on their percentage identity to native wild-type sequences on CATH test sets.
- **Reason for Rejection:**
  - **Flawed Biological Premise:** Natural proteins are not uniquely optimized for single structures. Many divergent sequences can fold into identical 3D topologies (neutral drift / sequence plasticity).
  - **Adversarial to Diversity:** Solely maximizing AAR penalizes novel or diverse sequences that are fully foldable and stable.
  - **Decision:** Pair sequence recovery with structural self-consistency (scRMSD, scTM) and biophysical property distributions.

---

## 5. Rejected Metric: Unconstrained Sequence Diversity
- **Proposal:** Maximize pairwise sequence distance without controlling for structural foldability.
- **Reason for Rejection:**
  - **Trivial Gaming:** A model outputting completely random amino acid sequences achieves maximum theoretical diversity (~95% pairwise distance), but 0% foldability.
  - **Decision:** Diversity must only be reported for the subset of candidates that satisfy the structural self-consistency filter ($\text{scRMSD} \le 2.0\text{ \AA}$, $\text{pLDDT} \ge 80$).
