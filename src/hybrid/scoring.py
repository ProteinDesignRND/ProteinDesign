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
    - lambda is tuned ONLY on the development/tuning set and frozen before primary test evaluation.

EXPLORATORY ABLATION:
    Raw logit interpolation:
        z_hybrid = lambda * z_MPNN + (1 - lambda) * z_PS
    Retained strictly as an exploratory ablation.
"""

from typing import List, Sequence, Union
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
