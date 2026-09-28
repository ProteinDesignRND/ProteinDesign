"""
Development hyperparameter selection, Cartesian grid optimization, and freezing protocol.

Authoritative Rules:
1. Development Optimization Objective (J):
   Scalar objective computed strictly across the N_dev = 20 CATH 4.2 validation backbones:
       J = (1 / N_dev) * sum_{t=1}^{N_dev} [ (1 / M) * sum_{m=1}^M scTM_val(s_{t,m}) ]
   where scTM is produced by the frozen Primary Final Structural Validation Oracle:
       AlphaFold2 v2.3.2, model_1_ptm, single-sequence mode, no templates,
       3 recycles, float16 GPU, seed 42, Amber disabled.
   No surrogate objectives are permitted.

2. Development Infeasibility Rule:
   Every candidate hyperparameter configuration must successfully produce an M=10
   unique viable library on ALL 20 development targets to be eligible for the primary J argmax.
   If ANY one of the 20 development targets is SELECTION_INFEASIBLE_LT_M for that configuration,
   the configuration is INELIGIBLE and receives objective J = -infinity for argmax purposes.
   - Do NOT replace missing/infeasible development target scTM with 0.0.
   - Do NOT exclude the infeasible target and average over the remaining targets.
   - Do NOT reduce M.
   - Do NOT regenerate beyond K.
   - Do NOT alter screening thresholds.
   - Do NOT silently substitute another temperature or seed.
   - Report the configuration's infeasibility rate separately.
   - If every configuration for an arm is infeasible, STOP THAT TUNING ARM and classify
     the development tuning stage as INFEASIBLE rather than inventing a fallback.

3. MPNN-Only Parameter Selection:
   Complete Cartesian product: T_MPNN x gamma
       T_MPNN in {0.1, 0.2, 0.5, 0.8, 1.0}
       gamma in {0.0, 0.25, 0.5, 1.0, 2.0}
   (25 combinations). (T*_MPNN, gamma*_MPNN) = argmax J.

4. ProteinSolver E0-B Parameter Selection:
   Complete Cartesian product: T_PS x gamma
       T_PS in {0.1, 0.5, 1.0}
       gamma in {0.0, 0.25, 0.5, 1.0, 2.0}
   (15 combinations). (T*_PS, gamma*_PS) = argmax J.

5. Primary Hybrid Parameter Selection:
   Must evaluate the Common Candidate Universe generated at T*_MPNN.
   Therefore: T*_hybrid = T*_MPNN (zero independent temperature sweep).
   Complete Cartesian product: lambda x gamma
       lambda in {0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0}
       gamma in {0.0, 0.25, 0.5, 1.0, 2.0}
   (35 combinations). (lambda*, gamma*_hybrid) = argmax J.

6. Deterministic Selection Order:
   Step 1: Select (T*_MPNN, gamma*_MPNN)
   Step 2: Select (T*_PS, gamma*_PS)
   Step 3: Using T*_MPNN, select (lambda*, gamma*_hybrid)
   Step 4: Freeze ALL resulting parameters
   Step 5: Only then permit TS50 execution.

7. Deterministic Tie Breaking:
   Ascending lexicographical ordering over declared grids:
   - For (T, gamma): ascending T, then ascending gamma.
   - For (lambda, gamma): ascending lambda, then ascending gamma.
   No secondary optimization criteria (e.g. AAR, latency, diversity, perplexity) are permitted.
"""

from dataclasses import dataclass
from itertools import product
from typing import Dict, List, Optional, Sequence, Tuple
import numpy as np

from .budget import GAMMA_SEARCH_GRID, LAMBDA_SEARCH_GRID


DEVELOPMENT_TARGET_COUNT: int = 20
SELECTION_LIBRARY_SIZE: int = 10

MPNN_TEMPERATURE_GRID: Tuple[float, ...] = (0.1, 0.2, 0.5, 0.8, 1.0)
PROTEINSOLVER_TEMPERATURE_GRID: Tuple[float, ...] = (0.1, 0.5, 1.0)


def get_mpnn_tuning_grid() -> List[Tuple[float, float]]:
    """Returns the full Cartesian product grid for MPNN-only tuning: T_MPNN x gamma (25 combinations)."""
    return list(product(MPNN_TEMPERATURE_GRID, GAMMA_SEARCH_GRID))


def get_proteinsolver_tuning_grid() -> List[Tuple[float, float]]:
    """Returns the full Cartesian product grid for ProteinSolver E0-B tuning: T_PS x gamma (15 combinations)."""
    return list(product(PROTEINSOLVER_TEMPERATURE_GRID, GAMMA_SEARCH_GRID))


def get_hybrid_tuning_grid() -> List[Tuple[float, float]]:
    """Returns the full Cartesian product grid for Primary Hybrid tuning: lambda x gamma (35 combinations)."""
    return list(product(LAMBDA_SEARCH_GRID, GAMMA_SEARCH_GRID))


def compute_target_sctm_mean(
    sctm_values: Sequence[float],
    expected_m: int = SELECTION_LIBRARY_SIZE,
) -> float:
    """Computes target-level mean scTM over the selected M=10 library.

    Args:
        sctm_values: scTM values for the M candidates of a target.
        expected_m: Expected library size (default 10).

    Returns:
        Target-level mean scTM.
    """
    if len(sctm_values) != expected_m:
        raise ValueError(
            f"Expected exactly {expected_m} scTM values for target library, got {len(sctm_values)}"
        )
    for val in sctm_values:
        if val < 0.0 or val > 1.0:
            raise ValueError(f"scTM value out of valid [0.0, 1.0] bounds: {val}")
    return float(np.mean(sctm_values))


def compute_development_objective(
    target_sctm_means: Sequence[Optional[float]],
    expected_n_dev: int = DEVELOPMENT_TARGET_COUNT,
    infeasible_mask: Optional[Sequence[bool]] = None,
) -> float:
    """Computes the scalar development optimization objective J.

    Formula:
        J = (1 / N_dev) * sum_{t=1}^{N_dev} mean_m scTM_val(s_{t,m})

    Infeasibility Rule (Pre-E1 Freeze):
        Every candidate hyperparameter configuration must successfully produce an M=10
        unique viable library on ALL N_dev=20 development targets to be eligible for
        the primary J argmax.
        If ANY single target is SELECTION_INFEASIBLE_LT_M for that configuration
        (signaled via infeasible_mask[i]=True, target_sctm_means[i] is None, or
        target_sctm_means[i] == -inf), the entire configuration is INELIGIBLE and
        receives objective J = -infinity for argmax purposes.
        - Do NOT replace missing/infeasible development target scTM with 0.0.
        - Do NOT exclude the infeasible target and average over the remaining targets.
        - Do NOT reduce M.
        - Do NOT regenerate beyond K.
        - Do NOT alter screening thresholds.
        - Do NOT silently substitute another temperature or seed.

    Args:
        target_sctm_means: Target-level mean scTM values across the 20 development backbones.
                           Can contain None or float('-inf') if a target was infeasible.
        expected_n_dev: Expected number of development targets (default 20).
        infeasible_mask: Optional boolean mask of length N_dev where True indicates SELECTION_INFEASIBLE_LT_M.

    Returns:
        Scalar development objective J in [0.0, 1.0] if all 20 targets are feasible,
        or -infinity (float('-inf')) if any target is infeasible.
    """
    if len(target_sctm_means) != expected_n_dev:
        raise ValueError(
            f"Expected exactly {expected_n_dev} development targets, got {len(target_sctm_means)}"
        )
    if infeasible_mask is not None:
        if len(infeasible_mask) != expected_n_dev:
            raise ValueError(
                f"Expected infeasible_mask of length {expected_n_dev}, got {len(infeasible_mask)}"
            )
        if any(infeasible_mask):
            return float("-inf")

    clean_means = []
    for val in target_sctm_means:
        if val is None or val == float("-inf") or np.isneginf(val):
            return float("-inf")
        if val < 0.0 or val > 1.0:
            raise ValueError(f"Target-level mean scTM out of valid [0.0, 1.0] bounds: {val}")
        clean_means.append(val)

    return float(np.mean(clean_means))


def compute_configuration_infeasibility_rate(
    infeasible_mask: Sequence[bool],
    expected_n_dev: int = DEVELOPMENT_TARGET_COUNT,
) -> float:
    """Computes the development target infeasibility rate for a configuration.

    Formula:
        infeasibility_rate = (number of infeasible targets) / N_dev
    """
    if len(infeasible_mask) != expected_n_dev:
        raise ValueError(f"Expected {expected_n_dev} targets, got {len(infeasible_mask)}")
    return float(sum(1 for x in infeasible_mask if x) / expected_n_dev)


def select_optimal_temperature_and_gamma(
    grid_results: Dict[Tuple[float, float], float],
    grid_type: str = "mpnn",
    atol: float = 1e-12,
) -> Tuple[float, float]:
    """Selects (T*, gamma*) maximizing development objective J with deterministic lexicographical tie-breaking.

    Tie-breaking rule:
        If two or more parameter combinations achieve identical J (within atol),
        select the combination that is first under ascending lexicographical order:
        primary key: T ascending; secondary key: gamma ascending.

    Infeasibility handling:
        Configurations receiving J = -infinity are ineligible.
        If all configurations are infeasible (max_j == -infinity), STOP THAT TUNING ARM
        and raise RuntimeError classifying the development tuning stage as INFEASIBLE.

    Args:
        grid_results: Mapping of (T, gamma) -> development objective J.
        grid_type: Either 'mpnn' or 'proteinsolver'.
        atol: Absolute tolerance for floating-point equality.

    Returns:
        Tuple of (T*, gamma*).
    """
    g_type = grid_type.strip().lower()
    if g_type in ("mpnn", "proteinmpnn"):
        declared_grid = get_mpnn_tuning_grid()
    elif g_type in ("ps", "proteinsolver", "e0-b"):
        declared_grid = get_proteinsolver_tuning_grid()
    else:
        raise ValueError(f"Unknown grid type: {grid_type}")

    missing = [pair for pair in declared_grid if pair not in grid_results]
    if missing:
        raise ValueError(f"Incomplete grid evaluation: missing {len(missing)} combinations (e.g. {missing[0]})")

    # Find maximum J
    max_j = max(grid_results[pair] for pair in declared_grid)
    if max_j == float("-inf") or np.isneginf(max_j):
        raise RuntimeError(
            f"DEVELOPMENT_TUNING_STAGE_INFEASIBLE: All {len(declared_grid)} configurations in {grid_type} tuning "
            f"arm are ineligible (SELECTION_INFEASIBLE_LT_M on one or more development targets). "
            f"Zero fallback substitution permitted."
        )

    # Collect candidate pairs with maximum J (within tolerance)
    tied_pairs = [pair for pair in declared_grid if abs(grid_results[pair] - max_j) <= atol]

    # Deterministic lexicographical tie-break: T ascending, then gamma ascending
    tied_pairs.sort(key=lambda pair: (pair[0], pair[1]))
    return tied_pairs[0]


def select_optimal_lambda_and_gamma(
    grid_results: Dict[Tuple[float, float], float],
    atol: float = 1e-12,
) -> Tuple[float, float]:
    """Selects (lambda*, gamma*_hybrid) maximizing development objective J with deterministic lexicographical tie-breaking.

    Tie-breaking rule:
        If two or more parameter combinations achieve identical J (within atol),
        select the combination that is first under ascending lexicographical order:
        primary key: lambda ascending; secondary key: gamma ascending.

    Infeasibility handling:
        Configurations receiving J = -infinity are ineligible.
        If all configurations are infeasible (max_j == -infinity), STOP THAT TUNING ARM
        and raise RuntimeError classifying the development tuning stage as INFEASIBLE.

    Args:
        grid_results: Mapping of (lambda, gamma) -> development objective J.
        atol: Absolute tolerance for floating-point equality.

    Returns:
        Tuple of (lambda*, gamma*_hybrid).
    """
    declared_grid = get_hybrid_tuning_grid()
    missing = [pair for pair in declared_grid if pair not in grid_results]
    if missing:
        raise ValueError(f"Incomplete grid evaluation: missing {len(missing)} combinations (e.g. {missing[0]})")

    # Find maximum J
    max_j = max(grid_results[pair] for pair in declared_grid)
    if max_j == float("-inf") or np.isneginf(max_j):
        raise RuntimeError(
            "DEVELOPMENT_TUNING_STAGE_INFEASIBLE: All 35 configurations in hybrid tuning arm are ineligible "
            "(SELECTION_INFEASIBLE_LT_M on one or more development targets). Zero fallback substitution permitted."
        )

    # Collect candidate pairs with maximum J (within tolerance)
    tied_pairs = [pair for pair in declared_grid if abs(grid_results[pair] - max_j) <= atol]

    # Deterministic lexicographical tie-break: lambda ascending, then gamma ascending
    tied_pairs.sort(key=lambda pair: (pair[0], pair[1]))
    return tied_pairs[0]


@dataclass
class DevelopmentHyperparameterState:
    """Tracks and enforces the deterministic 5-step development hyperparameter freezing protocol.

    Protocol Order:
        Step 1: Select (T*_MPNN, gamma*_MPNN)
        Step 2: Select (T*_PS, gamma*_PS)
        Step 3: Using T*_MPNN, select (lambda*, gamma*_hybrid).
                Strictly enforces T*_hybrid = T*_MPNN.
        Step 4: Freeze ALL resulting parameters.
        Step 5: Only then permit TS50 benchmark execution.
    """
    t_mpnn_star: Optional[float] = None
    gamma_mpnn_star: Optional[float] = None
    t_ps_star: Optional[float] = None
    gamma_ps_star: Optional[float] = None
    t_hybrid_star: Optional[float] = None
    lambda_star: Optional[float] = None
    gamma_hybrid_star: Optional[float] = None
    is_frozen: bool = False

    def step1_select_mpnn(self, t_star: float, gamma_star: float) -> None:
        """Step 1: Select (T*_MPNN, gamma*_MPNN) and propagate T*_hybrid = T*_MPNN."""
        if self.is_frozen:
            raise RuntimeError("Cannot alter parameters: development state is already FROZEN.")
        if t_star not in MPNN_TEMPERATURE_GRID:
            raise ValueError(f"T*_MPNN {t_star} not in declared grid {MPNN_TEMPERATURE_GRID}")
        if gamma_star not in GAMMA_SEARCH_GRID:
            raise ValueError(f"gamma*_MPNN {gamma_star} not in declared grid {GAMMA_SEARCH_GRID}")

        self.t_mpnn_star = float(t_star)
        self.gamma_mpnn_star = float(gamma_star)
        # Authoritative constraint: hybrid uses common candidate universe generated at T*_MPNN
        self.t_hybrid_star = float(t_star)

    def step2_select_proteinsolver(self, t_star: float, gamma_star: float) -> None:
        """Step 2: Select (T*_PS, gamma*_PS)."""
        if self.is_frozen:
            raise RuntimeError("Cannot alter parameters: development state is already FROZEN.")
        if t_star not in PROTEINSOLVER_TEMPERATURE_GRID:
            raise ValueError(f"T*_PS {t_star} not in declared grid {PROTEINSOLVER_TEMPERATURE_GRID}")
        if gamma_star not in GAMMA_SEARCH_GRID:
            raise ValueError(f"gamma*_PS {gamma_star} not in declared grid {GAMMA_SEARCH_GRID}")

        self.t_ps_star = float(t_star)
        self.gamma_ps_star = float(gamma_star)

    def step3_select_hybrid(self, lambda_star: float, gamma_star: float) -> None:
        """Step 3: Select (lambda*, gamma*_hybrid) on candidate universe generated at T*_MPNN."""
        if self.is_frozen:
            raise RuntimeError("Cannot alter parameters: development state is already FROZEN.")
        if self.t_mpnn_star is None:
            raise RuntimeError("Cannot perform Step 3 before Step 1: T*_MPNN must be selected first.")
        if lambda_star not in LAMBDA_SEARCH_GRID:
            raise ValueError(f"lambda* {lambda_star} not in declared grid {LAMBDA_SEARCH_GRID}")
        if gamma_star not in GAMMA_SEARCH_GRID:
            raise ValueError(f"gamma*_hybrid {gamma_star} not in declared grid {GAMMA_SEARCH_GRID}")

        # Ensure hybrid temperature invariant holds
        if self.t_hybrid_star != self.t_mpnn_star:
            raise RuntimeError(
                f"Protocol invariant violation: T*_hybrid ({self.t_hybrid_star}) != T*_MPNN ({self.t_mpnn_star})"
            )

        self.lambda_star = float(lambda_star)
        self.gamma_hybrid_star = float(gamma_star)

    def step4_freeze(self) -> None:
        """Step 4: Freezes all parameters. Verifies complete state."""
        required = [
            ("t_mpnn_star", self.t_mpnn_star),
            ("gamma_mpnn_star", self.gamma_mpnn_star),
            ("t_ps_star", self.t_ps_star),
            ("gamma_ps_star", self.gamma_ps_star),
            ("t_hybrid_star", self.t_hybrid_star),
            ("lambda_star", self.lambda_star),
            ("gamma_hybrid_star", self.gamma_hybrid_star),
        ]
        missing = [name for name, val in required if val is None]
        if missing:
            raise RuntimeError(f"Cannot freeze incomplete development state; missing parameters: {missing}")

        if self.t_hybrid_star != self.t_mpnn_star:
            raise RuntimeError("Protocol violation: T*_hybrid must equal T*_MPNN upon freezing.")

        self.is_frozen = True

    def assert_authorized_for_test(self) -> None:
        """Step 5 verification: Asserts that all parameters are strictly frozen prior to TS50 benchmark execution."""
        if not self.is_frozen:
            raise RuntimeError(
                "FREEZE-BEFORE-TEST VIOLATION: TS50 execution is strictly forbidden before development parameters are frozen."
            )
        if None in (
            self.t_mpnn_star,
            self.gamma_mpnn_star,
            self.t_ps_star,
            self.gamma_ps_star,
            self.t_hybrid_star,
            self.lambda_star,
            self.gamma_hybrid_star,
        ):
            raise RuntimeError("Corrupt state: is_frozen is True but one or more parameters are None.")
