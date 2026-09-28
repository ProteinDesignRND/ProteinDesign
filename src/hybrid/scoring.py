"""
Scoring formulations for ProteinMPNN + ProteinSolver hybrid evaluation.

PRIMARY METHOD:
    Scale-free within-pool percentile rank normalization:
        p_MPNN(u) = percentile_rank(S_MPNN(u))
        p_PS(u)   = percentile_rank(S_PS(u))
        H(u)      = lambda * p_MPNN(u) + (1 - lambda) * p_PS(u)

    Where:
    - S_MPNN(u) is sequence-level mean autoregressive log-probability.
    - S_PS(u) is sequence-level mean single-site masked pseudo-log-likelihood (PLL scan).
      (Explicitly NOT called autoregressive log-likelihood).
    - Percentile normalization is performed strictly within the target's candidate pool.
    - Ties are resolved deterministically using average ranking.
    - Higher percentile always indicates better (more confident) sequence.

COMMON CANDIDATE UNIVERSE PIPELINE:
    For any target backbone t:
    1. Candidate Generation: Generate a single frozen candidate universe U_t of size K
       (K = 100 for tuning, K = 500 for primary test).
    2. MPNN Scoring: Compute sequence-level mean log-probability S_MPNN(u) for each u in U_t.
    3. ProteinSolver Scoring: Compute sequence-level mean masked pseudo-log-likelihood S_PS(u) for each u in U_t.
    4. Percentile Normalization: Compute within-universe percentile ranks p_MPNN(u) and p_PS(u)
       strictly across the identical candidate pool U_t.
    5. Hybrid Score: H(u) = lambda * p_MPNN(u) + (1 - lambda) * p_PS(u).
    6. Screening & Selection: Viability gate (scRMSD <= 2.0 Å, pLDDT >= 80.0) -> diverse library selection (M = 10).

    This pipeline guarantees that percentiles for ProteinMPNN and ProteinSolver are derived
    from the exact same candidate population, preventing asymmetric or cross-pool ranking leakage.

EXPLORATORY ABLATION:
    Raw logit interpolation:
        z_hybrid = lambda * z_MPNN + (1 - lambda) * z_PS
    Retained strictly as an exploratory ablation.
"""

from typing import List, Sequence, Union, Optional
import numpy as np
from scipy.stats import rankdata
import torch


def compute_percentile_ranks(
    scores: Union[Sequence[float], np.ndarray],
    tie_method: str = "average",
) -> np.ndarray:
    """Computes scale-free percentile ranks within a candidate pool.

    Higher raw score maps to higher percentile rank in (0, 1].

    Args:
        scores: Sequence of raw numerical scores of length K.
        tie_method: Tie-breaking method for rankdata ('average', 'min', 'max').
            Default is 'average' for deterministic, unbiased tie resolution.

    Returns:
        1D numpy array of percentile ranks of shape (K,), with values in (0, 1].
        If K == 0, returns an empty array.
        If K == 1, returns array([1.0]).
    """
    scores_arr = np.asarray(scores, dtype=np.float64)
    k = len(scores_arr)
    if k == 0:
        return np.empty(0, dtype=np.float64)
    if k == 1:
        return np.array([1.0], dtype=np.float64)

    # rankdata assigns 1 to lowest score, K to highest score
    ranks = rankdata(scores_arr, method=tie_method)
    percentiles = ranks / float(k)
    return percentiles


def compute_primary_hybrid_score(
    mpnn_scores: Union[Sequence[float], np.ndarray],
    ps_scores: Union[Sequence[float], np.ndarray],
    weight_lambda: float = 0.5,
    tie_method: str = "average",
) -> np.ndarray:
    """Computes the primary hybrid score using scale-free percentile normalization.

    Formula:
        H(u) = lambda * p_MPNN(u) + (1 - lambda) * p_PS(u)

    Args:
        mpnn_scores: Candidate sequence-level scores from ProteinMPNN (higher is better).
        ps_scores: Candidate sequence-level pseudo-log-likelihood scores from ProteinSolver (higher is better).
        weight_lambda: Mixing coefficient lambda in [0.0, 1.0].
            lambda = 1.0 represents pure ProteinMPNN.
            lambda = 0.0 represents pure ProteinSolver.
        tie_method: Tie resolution strategy for within-pool ranking. Default is 'average'.

    Returns:
        1D numpy array of hybrid scores in (0, 1], where higher indicates better candidate quality.

    Raises:
        ValueError: If weight_lambda is outside [0.0, 1.0] or input lengths mismatch.
    """
    if not (0.0 <= weight_lambda <= 1.0):
        raise ValueError(f"weight_lambda must be in [0.0, 1.0], got {weight_lambda}")

    mpnn_arr = np.asarray(mpnn_scores, dtype=np.float64)
    ps_arr = np.asarray(ps_scores, dtype=np.float64)

    if len(mpnn_arr) != len(ps_arr):
        raise ValueError(
            f"Input score lengths mismatch: len(mpnn)={len(mpnn_arr)} vs len(ps)={len(ps_arr)}"
        )

    if len(mpnn_arr) == 0:
        return np.empty(0, dtype=np.float64)

    p_mpnn = compute_percentile_ranks(mpnn_arr, tie_method=tie_method)
    p_ps = compute_percentile_ranks(ps_arr, tie_method=tie_method)

    hybrid_scores = weight_lambda * p_mpnn + (1.0 - weight_lambda) * p_ps
    return hybrid_scores


def compute_exploratory_logit_hybrid(
    mpnn_logits: torch.Tensor,
    ps_logits: torch.Tensor,
    weight_lambda: float = 0.5,
) -> torch.Tensor:
    """Computes exploratory logit interpolation (EXPLORATORY ABLATION ONLY).

    NOTE: This is NOT the primary hybrid method. It is retained solely as an
    exploratory ablation to compare against scale-free percentile normalization.

    Formula:
        z_hybrid = lambda * z_MPNN + (1 - lambda) * z_PS

    Args:
        mpnn_logits: Unnormalized logits from ProteinMPNN [L, 20].
        ps_logits: Unnormalized logits from ProteinSolver [L, 20].
        weight_lambda: Interpolation weight in [0.0, 1.0].

    Returns:
        Interpolated logit tensor [L, 20].
    """
    if not (0.0 <= weight_lambda <= 1.0):
        raise ValueError(f"weight_lambda must be in [0.0, 1.0], got {weight_lambda}")
    if mpnn_logits.shape != ps_logits.shape:
        raise ValueError(
            f"Logit shape mismatch: mpnn={mpnn_logits.shape} vs ps={ps_logits.shape}"
        )
    return weight_lambda * mpnn_logits + (1.0 - weight_lambda) * ps_logits


def validate_common_candidate_order(
    mpnn_candidate_ids: Sequence[str],
    ps_candidate_ids: Sequence[str],
    mpnn_sequences: Sequence[str],
    ps_sequences: Sequence[str],
) -> bool:
    """Verifies that sequences scored by both models are identical and in identical candidate identity order.

    Guarantees strict integrity of the Common Candidate Universe before percentile ranks are computed.

    Raises:
        ValueError: If lengths mismatch, candidate IDs differ, or sequences differ.
    """
    if len(mpnn_candidate_ids) != len(ps_candidate_ids):
        raise ValueError(
            f"Candidate ID length mismatch: mpnn={len(mpnn_candidate_ids)} vs ps={len(ps_candidate_ids)}"
        )
    if len(mpnn_sequences) != len(ps_sequences):
        raise ValueError(
            f"Sequence length mismatch: mpnn={len(mpnn_sequences)} vs ps={len(ps_sequences)}"
        )
    for idx, (m_id, p_id) in enumerate(zip(mpnn_candidate_ids, ps_candidate_ids)):
        if m_id != p_id:
            raise ValueError(
                f"Candidate ID mismatch at index {idx}: mpnn='{m_id}' vs ps='{p_id}'"
            )
    for idx, (m_seq, p_seq) in enumerate(zip(mpnn_sequences, ps_sequences)):
        if m_seq != p_seq:
            raise ValueError(
                f"Candidate sequence mismatch at index {idx} (ID '{mpnn_candidate_ids[idx]}'): "
                f"mpnn='{m_seq}' vs ps='{p_seq}'"
            )
    return True


def compute_mpnn_only_selection_score(
    mpnn_scores: Union[Sequence[float], np.ndarray],
    tie_method: str = "average",
) -> np.ndarray:
    """Computes the normalized score for the primary MPNN-only arm inside greedy selection.

    Scale-Normalization Rule:
        The greedy selector combines score(u) + gamma * diversity_term.
        Because diversity distance d(u, v) in [0, 1] and hybrid score H(u) in (0, 1],
        the primary MPNN-only arm must also use scores normalized to the [0, 1] rank scale:
            score_MPNN_only(u) = p_MPNN(u) = percentile_rank(S_MPNN(u))
        This guarantees scale compatibility across arms under the shared diversity formulation.
        Underlying raw autoregressive log-likelihood and perplexity remain diagnostic metrics.

    Args:
        mpnn_scores: Sequence-level log-probability scores from ProteinMPNN.
        tie_method: Tie resolution method ('average').

    Returns:
        1D numpy array of normalized percentile rank scores in (0, 1].
    """
    return compute_percentile_ranks(mpnn_scores, tie_method=tie_method)


def score_common_candidate_universe(
    candidate_ids: Sequence[str],
    sequences: Sequence[str],
    mpnn_scores: Union[Sequence[float], np.ndarray],
    ps_scores: Union[Sequence[float], np.ndarray],
    weight_lambda: float = 0.5,
    tie_method: str = "average",
    ps_candidate_ids: Optional[Sequence[str]] = None,
    ps_sequences: Optional[Sequence[str]] = None,
) -> np.ndarray:
    """Computes primary hybrid scores for a common, frozen candidate universe.

    Guarantees that:
    1. The candidate universe has identical length K across candidate IDs, sequences,
       MPNN scores, and ProteinSolver scores.
    2. Sequences scored by both models are identical and in identical candidate identity order,
       before percentile ranks are computed.
    3. Percentile ranks for MPNN and ProteinSolver are computed across the EXACT SAME
       candidate universe, preventing any cross-pool or asymmetric rank leakage.
    4. Hybrid score H(u) = lambda * p_MPNN(u) + (1 - lambda) * p_PS(u) is in (0, 1].

    Args:
        candidate_ids: List of candidate identifier strings of length K (from ProteinMPNN generation).
        sequences: List of candidate sequence strings of length K.
        mpnn_scores: Raw sequence-level log-probabilities from ProteinMPNN of length K.
        ps_scores: Raw sequence-level pseudo-log-likelihoods from ProteinSolver of length K.
        weight_lambda: Mixing coefficient lambda in [0.0, 1.0].
        tie_method: Tie resolution method for within-pool ranking ('average').
        ps_candidate_ids: Optional candidate IDs from ProteinSolver scoring to verify identity.
        ps_sequences: Optional sequences from ProteinSolver scoring to verify identity.

    Returns:
        1D numpy array of hybrid scores of length K.

    Raises:
        ValueError: If array lengths mismatch, ordering mismatches, or inputs are inconsistent.
    """
    k = len(candidate_ids)
    if len(sequences) != k or len(mpnn_scores) != k or len(ps_scores) != k:
        raise ValueError(
            f"Common candidate universe dimension mismatch: "
            f"ids={k}, sequences={len(sequences)}, mpnn={len(mpnn_scores)}, ps={len(ps_scores)}. "
            f"All scores must be computed on the exact same candidate universe."
        )

    if ps_candidate_ids is not None or ps_sequences is not None:
        p_ids = ps_candidate_ids if ps_candidate_ids is not None else candidate_ids
        p_seqs = ps_sequences if ps_sequences is not None else sequences
        validate_common_candidate_order(candidate_ids, p_ids, sequences, p_seqs)

    if k == 0:
        return np.empty(0, dtype=np.float64)

    return compute_primary_hybrid_score(
        mpnn_scores=mpnn_scores,
        ps_scores=ps_scores,
        weight_lambda=weight_lambda,
        tie_method=tie_method,
    )

