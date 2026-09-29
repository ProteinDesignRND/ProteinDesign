"""
Candidate generation budget and temperature/seed allocation accounting.

Authoritative Rules:
1. K is the TOTAL candidate sequences generated PER TARGET PER METHOD/ARM
   across all temperature conditions and random seeds.
   - Primary test set (TS50): K = 500
   - Development set: K = 100
2. Exact Development Temperature & Seed Allocation Matrix:
   ProteinMPNN (K = 100 total):
       T=0.1: seed42=7, seed1337=7, seed2026=6 (sum=20)
       T=0.2: seed42=7, seed1337=6, seed2026=7 (sum=20)
       T=0.5: seed42=6, seed1337=7, seed2026=7 (sum=20)
       T=0.8: seed42=7, seed1337=7, seed2026=6 (sum=20)
       T=1.0: seed42=7, seed1337=6, seed2026=7 (sum=20)
       Total per seed: seed42=34, seed1337=33, seed2026=33. Overall total = 100.
   ProteinSolver E0-B (K = 100 total):
       T=0.1: seed42=12, seed1337=11, seed2026=11 (sum=34)
       T=0.5: seed42=11, seed1337=11, seed2026=11 (sum=33)
       T=1.0: seed42=11, seed1337=11, seed2026=11 (sum=33)
       Total per seed: seed42=34, seed1337=33, seed2026=33. Overall total = 100.
3. Frozen Test-Time Allocation (K = 500 total at frozen T*):
   - Generated strictly at optimal frozen temperature T*.
   - No test-time temperature sweep.
   - Seed allocation: seed42=167, seed1337=167, seed2026=166. Total = 500.
4. Historical Deterministic Control (E0-A):
   - Exactly 1 sequence on target 1n5uA03 (MAP decoding, 41.30% recovery).
   - Single target integration control, NOT part of TS50 benchmark.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass


PROTEINMPNN_DEV_ALLOCATION: Dict[float, Dict[int, int]] = {
    0.1: {42: 7, 1337: 7, 2026: 6},
    0.2: {42: 7, 1337: 6, 2026: 7},
    0.5: {42: 6, 1337: 7, 2026: 7},
    0.8: {42: 7, 1337: 7, 2026: 6},
    1.0: {42: 7, 1337: 6, 2026: 7},
}

PROTEINSOLVER_DEV_ALLOCATION: Dict[float, Dict[int, int]] = {
    0.1: {42: 12, 1337: 11, 2026: 11},
    0.5: {42: 11, 1337: 11, 2026: 11},
    1.0: {42: 11, 1337: 11, 2026: 11},
}

PRIMARY_TEST_SEED_ALLOCATION_500: Dict[int, int] = {
    42: 167,
    1337: 167,
    2026: 166,
}

GAMMA_SEARCH_GRID: Tuple[float, ...] = (0.0, 0.25, 0.5, 1.0, 2.0)
LAMBDA_SEARCH_GRID: Tuple[float, ...] = (0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0)


def get_development_temperature_allocation(method: str) -> Dict[float, Dict[int, int]]:
    """Returns the exact deterministic integer allocation matrix for development tuning (K=100).

    Args:
        method: Either 'proteinmpnn' or 'proteinsolver'.

    Returns:
        Mapping of temperature -> {seed: count}.
    """
    m = method.strip().lower()
    if m in ("proteinmpnn", "mpnn"):
        return {t: dict(s) for t, s in PROTEINMPNN_DEV_ALLOCATION.items()}
    elif m in ("proteinsolver", "ps", "e0-b"):
        return {t: dict(s) for t, s in PROTEINSOLVER_DEV_ALLOCATION.items()}
    else:
        raise ValueError(f"Unknown method for development allocation: {method}")


def get_test_seed_allocation(total_k: int = 500) -> Dict[int, int]:
    """Returns the frozen test-time seed allocation at T*.

    Args:
        total_k: Total generation budget K. Default 500.

    Returns:
        Mapping of seed -> count.
    """
    if total_k == 500:
        return dict(PRIMARY_TEST_SEED_ALLOCATION_500)
    elif total_k == 100:
        return {42: 34, 1337: 33, 2026: 33}
    else:
        # Balanced integer partition across the 3 pre-registered seeds
        seeds = [42, 1337, 2026]
        base = total_k // 3
        rem = total_k % 3
        res = {}
        for idx, seed in enumerate(seeds):
            res[seed] = base + (1 if idx < rem else 0)
        return res


def generate_candidate_id(
    target_id: str,
    method_arm: str,
    temperature: float,
    seed: int,
    seq_idx: int,
) -> str:
    """Generates a reproducible, globally unique candidate identifier.

    Format:
        {target_id}_{method_arm}_T{temperature}_s{seed}_idx{seq_idx:04d}
    """
    return f"{target_id}_{method_arm}_T{temperature:.1f}_s{seed}_idx{seq_idx:04d}"


def validate_budget_matrix(matrix: Dict[float, Dict[int, int]], expected_total: int) -> bool:
    """Validates that a temperature/seed allocation matrix sums exactly to expected_total."""
    total = sum(sum(seeds.values()) for seeds in matrix.values())
    return total == expected_total
