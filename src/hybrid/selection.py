"""
Candidate selection, diversity calculation, and structural validation utilities.

Provides:
- Stage 1: Hard structural viability filtering.
- Stage 2: Greedy diversity-aware candidate selection heuristic.
- Order-independent pairwise Hamming diversity.
- Fixed-correspondence self-consistency TM-score (scTM).
- Biophysical proxy metrics: Net charge at pH 7.4 and Hydrophobic core fraction.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple
import numpy as np


@dataclass
class Candidate:
    """Represents a generated sequence candidate with screening and validation metadata."""
    id: str
    sequence: str
    target_id: str
    score: float = 0.0
    scrmsd_screen: Optional[float] = None
    plddt_screen: Optional[float] = None
    scrmsd_val: Optional[float] = None
    plddt_val: Optional[float] = None
    sctm_val: Optional[float] = None


def filter_viable_candidates(
    candidates: Sequence[Candidate],
    scrmsd_threshold: float = 2.0,
    plddt_threshold: float = 80.0,
) -> List[Candidate]:
    """Stage 1: Hard viability gate using pre-frozen screening criteria.

    A candidate passes if:
        scrmsd_screen <= scrmsd_threshold AND plddt_screen >= plddt_threshold

    Args:
        candidates: Sequence of candidates with screening metadata.
        scrmsd_threshold: Maximum allowed scRMSD under screening oracle (default 2.0 Å).
        plddt_threshold: Minimum allowed mean pLDDT under screening oracle (default 80.0).

    Returns:
        List of viable candidates satisfying both screening thresholds.
    """
    viable = []
    for c in candidates:
        if c.scrmsd_screen is not None and c.plddt_screen is not None:
            if c.scrmsd_screen <= scrmsd_threshold and c.plddt_screen >= plddt_threshold:
                viable.append(c)
    return viable


def compute_normalized_hamming_distance(seq_a: str, seq_b: str) -> float:
    """Computes normalized Hamming distance between two equal-length sequences.

    d(u, v) = (1 / L) * sum_i I(u_i != v_i) in [0.0, 1.0].
    """
    if len(seq_a) != len(seq_b):
        raise ValueError(f"Sequence length mismatch: {len(seq_a)} vs {len(seq_b)}")
    if len(seq_a) == 0:
        return 0.0
    diffs = sum(1 for a, b in zip(seq_a, seq_b) if a != b)
    return diffs / float(len(seq_a))


def compute_pairwise_hamming_diversity(
    sequences: Sequence[str],
) -> float:
    """Computes order-independent mean pairwise sequence diversity across a candidate set.

    Formula:
        Div(S) = (2 / (M * (M - 1))) * sum_{j < k} d(s_j, s_k)

    Where d is normalized Hamming distance.

    Edge Cases:
    - If |S| < 2, returns 0.0 by definition.
    - Duplicate sequences have distance 0.0 and reduce the average naturally.

    Args:
        sequences: Collection of amino acid sequence strings of identical length L.

    Returns:
        Mean pairwise normalized Hamming distance in [0.0, 1.0].
    """
    m = len(sequences)
    if m < 2:
        return 0.0

    total_dist = 0.0
    pair_count = 0
    for j in range(m):
        for k in range(j + 1, m):
            total_dist += compute_normalized_hamming_distance(sequences[j], sequences[k])
            pair_count += 1

    return total_dist / float(pair_count)


def compute_diversity_distribution(
    sequences: Sequence[str],
) -> Dict[str, float]:
    """Computes complete order-independent distribution statistics for pairwise diversity."""
    m = len(sequences)
    if m < 2:
        return {"mean": 0.0, "std": 0.0, "median": 0.0, "min": 0.0, "max": 0.0, "count": 0}

    distances = []
    for j in range(m):
        for k in range(j + 1, m):
            distances.append(compute_normalized_hamming_distance(sequences[j], sequences[k]))

    dist_arr = np.asarray(distances, dtype=np.float64)
    return {
        "mean": float(np.mean(dist_arr)),
        "std": float(np.std(dist_arr)),
        "median": float(np.median(dist_arr)),
        "min": float(np.min(dist_arr)),
        "max": float(np.max(dist_arr)),
        "count": len(distances),
    }


def select_diverse_library(
    candidates: Sequence[Candidate],
    library_size_m: int = 10,
    diversity_weight_gamma: float = 1.0,
) -> List[Candidate]:
    """Stage 2: Greedy diversity-aware selection heuristic.

    NOTE ON METHODOLOGY:
    This function implements a greedy construction heuristic to choose M candidates
    from a viable pool. The selection criterion maximizes a trade-off between intrinsic
    candidate quality score and mutual dispersion from previously chosen candidates:
        u* = argmax_{u in S_viable \\ S'} [ score(u) + gamma * min_{v in S'} d(u, v) ]

    IMPORTANT: The greedy score evaluated during selection is a construction heuristic
    and MUST NOT be reported as an order-independent static candidate metric. Final set
    diversity must be computed after selection using compute_pairwise_hamming_diversity().

    Args:
        candidates: Candidate pool from Stage 1 (viable candidates).
        library_size_m: Target library size M (default 10).
        diversity_weight_gamma: Trade-off parameter gamma >= 0.0.
            gamma = 0.0 selects top M purely by score.

    Returns:
        List of selected Candidate objects of length min(M, len(candidates)).
    """
    if len(candidates) <= library_size_m:
        return list(candidates)

    remaining = list(candidates)
    # Pick first candidate with highest score
    remaining.sort(key=lambda c: c.score, reverse=True)
    selected = [remaining.pop(0)]

    while len(selected) < library_size_m and remaining:
        best_candidate = None
        best_objective = -float("inf")
        best_idx = -1

        for idx, cand in enumerate(remaining):
            # Compute min distance to any already-selected candidate (facility dispersion)
            min_dist = min(
                compute_normalized_hamming_distance(cand.sequence, sel.sequence)
                for sel in selected
            )
            obj = cand.score + diversity_weight_gamma * min_dist
            if obj > best_objective:
                best_objective = obj
                best_candidate = cand
                best_idx = idx

        selected.append(best_candidate)
        remaining.pop(best_idx)

    return selected


def compute_fixed_correspondence_sctm(
    pred_coords: np.ndarray,
    target_coords: np.ndarray,
) -> float:
    """Computes the Fixed-Correspondence Self-Consistency TM-score (scTM).

    Uses Zhang & Skolnick (2004) formulation with length-dependent d0(L)
    under optimal rigid-body Kabsch superposition on matched C-alpha coordinates.

    CRITICAL TERMINOLOGY DISTINCTION:
        This function evaluates the Fixed-Correspondence Self-Consistency TM-score (scTM)
        under strict 1-to-1 sequence-to-structure residue correspondence (residue i in
        prediction mapped to residue i in target backbone).
        It does NOT perform dynamic programming sequence alignment, heuristic gap insertion,
        or residue reordering, and must NOT be described as standard alignment-based TM-score (such as TM-align).

    Formula:
        scTM = (1 / L_target) * sum_{i=1}^{L_target} [ 1 / (1 + (d_i / d0(L_target))^2) ]
        d0(L_target) = 1.24 * (L_target - 15)^(1/3) - 1.8  (for L_target > 15)

    Args:
        pred_coords: Array of C-alpha coordinates from oracle [L, 3].
        target_coords: Array of C-alpha coordinates from reference backbone [L, 3].

    Returns:
        scTM score in (0, 1]. Higher is better.
    """
    pred = np.asarray(pred_coords, dtype=np.float64)
    target = np.asarray(target_coords, dtype=np.float64)

    if pred.shape != target.shape or pred.ndim != 2 or pred.shape[1] != 3:
        raise ValueError(f"Coordinate shape mismatch: {pred.shape} vs {target.shape}")

    l_target = len(target)
    if l_target == 0:
        return 0.0

    # Optimal Kabsch superposition
    p_center = pred - pred.mean(axis=0)
    t_center = target - target.mean(axis=0)

    # Covariance matrix H
    h = p_center.T @ t_center
    u, s, vt = np.linalg.svd(h)
    d = np.linalg.det(vt.T @ u.T)
    correction = np.diag([1.0, 1.0, d])
    r = vt.T @ correction @ u.T

    # Superimposed pred
    pred_aligned = (p_center @ r.T) + target.mean(axis=0)

    # Pairwise C-alpha Euclidean distances
    distances = np.linalg.norm(pred_aligned - target, axis=1)

    # d0 scaling
    if l_target > 15:
        d0 = 1.24 * np.cbrt(l_target - 15) - 1.8
        d0 = max(d0, 0.5)
    else:
        d0 = 0.5

    tm_terms = 1.0 / (1.0 + (distances / d0) ** 2)
    sctm = float(np.sum(tm_terms) / l_target)
    return sctm


# Standard EMBOSS pKa values for amino acid ionizable groups
EMBOSS_PKA = {
    "N_term": 8.6,
    "C_term": 3.6,
    "K": 10.8,
    "R": 12.5,
    "H": 6.5,
    "D": 3.9,
    "E": 4.1,
    "C": 8.5,
    "Y": 10.1,
}


def compute_net_charge_at_ph74(sequence: str, ph: float = 7.4) -> float:
    """Computes Net Charge at pH 7.4 via Henderson-Hasselbalch equation.

    NOTE ON TERMINOLOGY:
    This metric computes the net electrostatic charge at physiological pH 7.4 (Q_pH7.4).
    It is explicitly NOT the isoelectric point (pI), which is the pH where Q = 0.

    Args:
        sequence: Amino acid sequence string (single-letter uppercase).
        ph: Target pH (default 7.4).

    Returns:
        Net charge in elementary charge units (e).
    """
    seq_clean = sequence.upper().replace("-", "")
    if not seq_clean:
        return 0.0

    # Positive charges: N-terminus, Lys (K), Arg (R), His (H)
    n_term_charge = 1.0 / (1.0 + 10.0 ** (ph - EMBOSS_PKA["N_term"]))
    k_charge = seq_clean.count("K") * (1.0 / (1.0 + 10.0 ** (ph - EMBOSS_PKA["K"])))
    r_charge = seq_clean.count("R") * (1.0 / (1.0 + 10.0 ** (ph - EMBOSS_PKA["R"])))
    h_charge = seq_clean.count("H") * (1.0 / (1.0 + 10.0 ** (ph - EMBOSS_PKA["H"])))

    # Negative charges: C-terminus, Asp (D), Glu (E), Cys (C), Tyr (Y)
    c_term_charge = -1.0 / (1.0 + 10.0 ** (EMBOSS_PKA["C_term"] - ph))
    d_charge = -seq_clean.count("D") * (1.0 / (1.0 + 10.0 ** (EMBOSS_PKA["D"] - ph)))
    e_charge = -seq_clean.count("E") * (1.0 / (1.0 + 10.0 ** (EMBOSS_PKA["E"] - ph)))
    c_charge = -seq_clean.count("C") * (1.0 / (1.0 + 10.0 ** (EMBOSS_PKA["C"] - ph)))
    y_charge = -seq_clean.count("Y") * (1.0 / (1.0 + 10.0 ** (EMBOSS_PKA["Y"] - ph)))

    net_charge = (
        n_term_charge + k_charge + r_charge + h_charge +
        c_term_charge + d_charge + e_charge + c_charge + y_charge
    )
    return float(net_charge)


HYDROPHOBIC_RESIDUES = frozenset(["V", "L", "I", "F", "M", "W"])


def compute_hydrophobic_core_fraction(
    sequence: str,
    rsa_values: Sequence[float],
    rsa_threshold: float = 0.20,
) -> float:
    """Computes the hydrophobic core fraction of a folded candidate structure.

    Numerator: Residues in {V, L, I, F, M, W} with Relative Solvent Accessibility RSA < 0.20.
    Denominator: Total sequence length L.
    Structural Reference: Evaluated on the predicted structure from the folding oracle.

    Args:
        sequence: Amino acid sequence string.
        rsa_values: Per-residue RSA values (floats in [0.0, 1.0]) computed on predicted 3D structure.
        rsa_threshold: Burial cutoff for RSA (default 0.20).

    Returns:
        Hydrophobic core fraction in [0.0, 1.0].
    """
    seq_clean = sequence.upper().replace("-", "")
    if len(seq_clean) != len(rsa_values):
        raise ValueError(
            f"Length mismatch: sequence={len(seq_clean)} vs rsa_values={len(rsa_values)}"
        )
    if not seq_clean:
        return 0.0

    buried_hydrophobic_count = sum(
        1 for aa, rsa in zip(seq_clean, rsa_values)
        if aa in HYDROPHOBIC_RESIDUES and rsa < rsa_threshold
    )
    return float(buried_hydrophobic_count) / float(len(seq_clean))


class ValidationOutcomeType:
    """Taxonomy of structural folding validation outcomes."""
    VALID = "valid_structure"
    SCIENTIFIC_FAILURE = "scientific_folding_failure"
    INFRASTRUCTURE_FAILURE = "infrastructure_runtime_failure"


@dataclass
class ValidationOutcome:
    """Detailed structural validation result for a candidate.

    Attributes:
        status: One of ValidationOutcomeType (VALID, SCIENTIFIC_FAILURE, INFRASTRUCTURE_FAILURE).
        sctm: Self-consistency TM-score. Valid float in (0, 1] if VALID, 0.0 if SCIENTIFIC_FAILURE,
            None if INFRASTRUCTURE_FAILURE.
        scrmsd: Self-consistency RMSD (None if failure).
        plddt: Oracle confidence pLDDT (None if infrastructure failure).
        error_reason: Diagnostic explanation of failure (None if VALID).
        is_valid_for_statistical_test: Boolean indicating whether this candidate is valid
            for inclusion in paired statistical comparisons. False for infrastructure failures.
    """
    status: str
    sctm: Optional[float]
    scrmsd: Optional[float]
    plddt: Optional[float]
    error_reason: Optional[str] = None
    is_valid_for_statistical_test: bool = True


def evaluate_validation_outcome(
    outcome_type: str,
    pred_coords: Optional[np.ndarray] = None,
    target_coords: Optional[np.ndarray] = None,
    plddt: Optional[float] = None,
    scrmsd: Optional[float] = None,
    error_reason: Optional[str] = None,
) -> ValidationOutcome:
    """Processes oracle output according to the pre-registered failure handling taxonomy.

    Rules:
    1. VALID: Oracle completed normally, coordinates are physical. scTM is computed normally.
    2. SCIENTIFIC_FAILURE: Biological/generative failure (NaN coordinates, steric clash collapse,
       pLDDT < 10.0). Handled as a true biological failure to form a folded protein.
       Assigned scTM = 0.0, is_valid_for_statistical_test = True.
    3. INFRASTRUCTURE_FAILURE: Runtime/system failure (OOM, timeout, driver crash, missing file).
       Must NOT be assigned scTM = 0.0 (doing so artificially distorts model comparisons).
       Assigned scTM = None, is_valid_for_statistical_test = False.
       Subject to the <= 10% infrastructure-failure invalidation rule.

    Args:
        outcome_type: One of ValidationOutcomeType values.
        pred_coords: Predicted C-alpha coordinates (required if VALID).
        target_coords: Target reference C-alpha coordinates (required if VALID).
        plddt: Mean pLDDT from oracle.
        scrmsd: scRMSD value if available.
        error_reason: Diagnostic reason string if failure occurred.

    Returns:
        ValidationOutcome instance.
    """
    if outcome_type == ValidationOutcomeType.VALID:
        if pred_coords is None or target_coords is None:
            raise ValueError("VALID outcome requires pred_coords and target_coords")
        sctm = compute_fixed_correspondence_sctm(pred_coords, target_coords)
        return ValidationOutcome(
            status=ValidationOutcomeType.VALID,
            sctm=sctm,
            scrmsd=scrmsd,
            plddt=plddt,
            error_reason=None,
            is_valid_for_statistical_test=True,
        )

    elif outcome_type == ValidationOutcomeType.SCIENTIFIC_FAILURE:
        return ValidationOutcome(
            status=ValidationOutcomeType.SCIENTIFIC_FAILURE,
            sctm=0.0,
            scrmsd=scrmsd,
            plddt=plddt,
            error_reason=error_reason or "Biological/generative folding failure",
            is_valid_for_statistical_test=True,
        )

    elif outcome_type == ValidationOutcomeType.INFRASTRUCTURE_FAILURE:
        return ValidationOutcome(
            status=ValidationOutcomeType.INFRASTRUCTURE_FAILURE,
            sctm=None,  # NEVER assign 0.0 to infrastructure crashes
            scrmsd=None,
            plddt=None,
            error_reason=error_reason or "Infrastructure/runtime crash",
            is_valid_for_statistical_test=False,
        )

    else:
        raise ValueError(f"Unknown outcome_type: {outcome_type}")
