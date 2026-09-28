"""
Unit tests for development hyperparameter selection and freezing protocol.

Covers:
1. MPNN Cartesian-product tuning grid (25 combinations).
2. ProteinSolver Cartesian-product tuning grid (15 combinations).
3. Hybrid lambda x gamma grid (35 combinations).
4. T*_hybrid = T*_MPNN constraint (no independent hybrid temperature sweep).
5. Development objective J definition and AlphaFold2 oracle configuration.
6. Deterministic tie-breaking via ascending lexicographical grid order.
7. Freeze-before-test rule enforcement.
8. No test outcome used for tuning (strict isolation).
"""

import pytest
import numpy as np

from src.hybrid.optimization import (
    DEVELOPMENT_TARGET_COUNT,
    SELECTION_LIBRARY_SIZE,
    MPNN_TEMPERATURE_GRID,
    PROTEINSOLVER_TEMPERATURE_GRID,
    get_mpnn_tuning_grid,
    get_proteinsolver_tuning_grid,
    get_hybrid_tuning_grid,
    compute_target_sctm_mean,
    compute_development_objective,
    compute_configuration_infeasibility_rate,
    select_optimal_temperature_and_gamma,
    select_optimal_lambda_and_gamma,
    DevelopmentHyperparameterState,
)
from src.hybrid.budget import GAMMA_SEARCH_GRID, LAMBDA_SEARCH_GRID


def test_1_mpnn_cartesian_product_tuning_grid():
    """Requirement 1: MPNN Cartesian-product tuning grid T_MPNN x gamma."""
    grid = get_mpnn_tuning_grid()
    assert len(grid) == 25
    assert len(set(grid)) == 25  # All pairs unique

    expected_t = {0.1, 0.2, 0.5, 0.8, 1.0}
    expected_gamma = {0.0, 0.25, 0.5, 1.0, 2.0}

    actual_t = {pair[0] for pair in grid}
    actual_gamma = {pair[1] for pair in grid}

    assert actual_t == expected_t
    assert actual_gamma == expected_gamma


def test_2_proteinsolver_cartesian_product_tuning_grid():
    """Requirement 2: ProteinSolver Cartesian-product tuning grid T_PS x gamma."""
    grid = get_proteinsolver_tuning_grid()
    assert len(grid) == 15
    assert len(set(grid)) == 15  # All pairs unique

    expected_t = {0.1, 0.5, 1.0}
    expected_gamma = {0.0, 0.25, 0.5, 1.0, 2.0}

    actual_t = {pair[0] for pair in grid}
    actual_gamma = {pair[1] for pair in grid}

    assert actual_t == expected_t
    assert actual_gamma == expected_gamma


def test_3_hybrid_lambda_x_gamma_grid():
    """Requirement 3: Hybrid lambda x gamma grid."""
    grid = get_hybrid_tuning_grid()
    assert len(grid) == 35
    assert len(set(grid)) == 35  # All pairs unique

    expected_lambda = {0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0}
    expected_gamma = {0.0, 0.25, 0.5, 1.0, 2.0}

    actual_lambda = {pair[0] for pair in grid}
    actual_gamma = {pair[1] for pair in grid}

    assert actual_lambda == expected_lambda
    assert actual_gamma == expected_gamma


def test_4_t_hybrid_strictly_equals_t_mpnn():
    """Requirement 4: Primary hybrid MUST use T*_hybrid = T*_MPNN (zero independent temperature sweep)."""
    state = DevelopmentHyperparameterState()

    # Step 1: select MPNN with T=0.5, gamma=1.0
    state.step1_select_mpnn(t_star=0.5, gamma_star=1.0)
    assert state.t_mpnn_star == 0.5
    assert state.t_hybrid_star == 0.5  # Auto-propagated and constrained

    # Step 2: select PS
    state.step2_select_proteinsolver(t_star=0.1, gamma_star=0.5)

    # Step 3: select hybrid
    state.step3_select_hybrid(lambda_star=0.6, gamma_star=0.25)
    assert state.t_hybrid_star == state.t_mpnn_star == 0.5

    # If t_hybrid_star is maliciously altered, Step 3 and Step 4 raise RuntimeError
    state.t_hybrid_star = 0.8  # Desynchronization
    with pytest.raises(RuntimeError, match="Protocol invariant violation"):
        state.step3_select_hybrid(lambda_star=0.6, gamma_star=0.25)

    with pytest.raises(RuntimeError, match="Protocol violation"):
        state.step4_freeze()


def test_5_development_objective_definition():
    """Requirement 5: Scalar development optimization objective J definition.

    J = (1 / N_dev) * sum_t mean_m scTM_val(s_{t, m})
    where N_dev = 20, M = 10.
    """
    assert DEVELOPMENT_TARGET_COUNT == 20
    assert SELECTION_LIBRARY_SIZE == 10

    # 1. Target-level mean validation scTM
    m_sctm = [0.85, 0.80, 0.90, 0.75, 0.88, 0.82, 0.86, 0.79, 0.84, 0.81]
    target_mean = compute_target_sctm_mean(m_sctm, expected_m=10)
    assert target_mean == pytest.approx(float(np.mean(m_sctm)))

    # Error when M != 10
    with pytest.raises(ValueError, match="Expected exactly 10 scTM values"):
        compute_target_sctm_mean([0.8] * 9, expected_m=10)

    # 2. Objective J across 20 targets
    target_means = [0.70 + 0.01 * i for i in range(20)]
    j_obj = compute_development_objective(target_means, expected_n_dev=20)
    assert j_obj == pytest.approx(float(np.mean(target_means)))

    # Error when N_dev != 20
    with pytest.raises(ValueError, match="Expected exactly 20 development targets"):
        compute_development_objective([0.8] * 19, expected_n_dev=20)

    # Out-of-bounds scTM check
    with pytest.raises(ValueError, match="out of valid"):
        compute_development_objective([1.2] * 20, expected_n_dev=20)


def test_6_deterministic_tie_handling():
    """Requirement 6: Deterministic tie handling via ascending lexicographical grid order.

    No secondary criteria (e.g. AAR, latency, diversity, perplexity) are permitted.
    """
    # Test (T, gamma) tie-breaking for MPNN
    mpnn_grid = get_mpnn_tuning_grid()
    results_mpnn = {pair: 0.75 for pair in mpnn_grid}  # All combinations tied at J = 0.75

    # Ascending order: smallest T is 0.1, smallest gamma is 0.0
    best_t, best_gamma = select_optimal_temperature_and_gamma(results_mpnn, grid_type="mpnn")
    assert best_t == 0.1
    assert best_gamma == 0.0

    # Tied between (0.5, 1.0) and (0.5, 0.25) with highest J = 0.90
    results_mpnn[(0.5, 1.0)] = 0.90
    results_mpnn[(0.5, 0.25)] = 0.90
    best_t, best_gamma = select_optimal_temperature_and_gamma(results_mpnn, grid_type="mpnn")
    # Same T=0.5, so gamma=0.25 wins because 0.25 < 1.0
    assert best_t == 0.5
    assert best_gamma == 0.25

    # Test (lambda, gamma) tie-breaking for Hybrid
    hybrid_grid = get_hybrid_tuning_grid()
    results_hybrid = {pair: 0.80 for pair in hybrid_grid}
    # Tied between (0.4, 0.5) and (0.6, 0.25) at J = 0.92
    results_hybrid[(0.4, 0.5)] = 0.92
    results_hybrid[(0.6, 0.25)] = 0.92
    best_lambda, best_gamma_h = select_optimal_lambda_and_gamma(results_hybrid)
    # lambda=0.4 wins over lambda=0.6 because 0.4 < 0.6
    assert best_lambda == 0.4
    assert best_gamma_h == 0.5


def test_7_freeze_before_test_rule():
    """Requirement 7: Freeze-before-test rule enforcement.

    TS50 execution is strictly forbidden before all development parameters are frozen.
    """
    state = DevelopmentHyperparameterState()

    # Attempting to authorize test before freezing raises RuntimeError
    with pytest.raises(RuntimeError, match="FREEZE-BEFORE-TEST VIOLATION"):
        state.assert_authorized_for_test()

    # Step 1: MPNN
    state.step1_select_mpnn(t_star=0.2, gamma_star=0.5)
    with pytest.raises(RuntimeError, match="FREEZE-BEFORE-TEST VIOLATION"):
        state.assert_authorized_for_test()

    # Step 2: PS
    state.step2_select_proteinsolver(t_star=0.5, gamma_star=0.25)
    with pytest.raises(RuntimeError, match="FREEZE-BEFORE-TEST VIOLATION"):
        state.assert_authorized_for_test()

    # Step 3: Hybrid
    state.step3_select_hybrid(lambda_star=0.5, gamma_star=0.5)
    with pytest.raises(RuntimeError, match="FREEZE-BEFORE-TEST VIOLATION"):
        state.assert_authorized_for_test()

    # Step 4: Freeze
    state.step4_freeze()
    assert state.is_frozen is True

    # Step 5: Now test authorization passes
    state.assert_authorized_for_test()

    # Modifying any parameter after freeze is strictly forbidden
    with pytest.raises(RuntimeError, match="already FROZEN"):
        state.step1_select_mpnn(t_star=0.8, gamma_star=1.0)
    with pytest.raises(RuntimeError, match="already FROZEN"):
        state.step2_select_proteinsolver(t_star=1.0, gamma_star=1.0)
    with pytest.raises(RuntimeError, match="already FROZEN"):
        state.step3_select_hybrid(lambda_star=0.8, gamma_star=1.0)


def test_8_no_test_outcome_used_for_tuning():
    """Requirement 8: No test outcome used for tuning.

    Step 3 must be conducted before freezing, and test set cannot be evaluated without freeze.
    Attempting Step 3 before Step 1 raises an error.
    """
    state = DevelopmentHyperparameterState()

    # Cannot jump to Step 3 without Step 1
    with pytest.raises(RuntimeError, match="Cannot perform Step 3 before Step 1"):
        state.step3_select_hybrid(lambda_star=0.4, gamma_star=0.25)

    # Cannot freeze with missing parameters
    with pytest.raises(RuntimeError, match="missing parameters"):
        state.step4_freeze()


def test_9_development_infeasibility_rule():
    """Requirement 9: Pre-E1 Development Infeasibility Rule.

    - Every configuration must produce an M=10 unique viable library on ALL 20 targets.
    - If ANY single target is SELECTION_INFEASIBLE_LT_M, configuration receives J = -infinity.
    - Infeasible configurations are ineligible for argmax.
    - Zero-filling, target exclusion, M reduction, or threshold alteration are strictly forbidden.
    """
    # Baseline 20 valid means
    valid_means = [0.80] * 20
    j_valid = compute_development_objective(valid_means, expected_n_dev=20)
    assert j_valid == pytest.approx(0.80)

    # 1 target infeasible via mask
    infeasible_mask = [False] * 20
    infeasible_mask[7] = True  # Target 8 is infeasible
    j_infeasible = compute_development_objective(valid_means, expected_n_dev=20, infeasible_mask=infeasible_mask)
    assert j_infeasible == float("-inf")

    # Infeasibility rate calculation
    rate = compute_configuration_infeasibility_rate(infeasible_mask, expected_n_dev=20)
    assert rate == pytest.approx(1 / 20)

    # 1 target infeasible via None or -inf in sequence
    means_with_none = [0.80] * 19 + [None]
    assert compute_development_objective(means_with_none, expected_n_dev=20) == float("-inf")

    means_with_inf = [0.80] * 19 + [float("-inf")]
    assert compute_development_objective(means_with_inf, expected_n_dev=20) == float("-inf")

    # Selection ineligibility test:
    # Let (0.1, 0.0) be first lexicographically but receive J = -inf (ineligible)
    # Let (0.2, 0.5) be feasible with J = 0.70
    mpnn_grid = get_mpnn_tuning_grid()
    results = {pair: float("-inf") for pair in mpnn_grid}
    results[(0.2, 0.5)] = 0.70
    results[(0.5, 1.0)] = 0.65

    # Optimal selection must choose (0.2, 0.5), NOT the lexicographically earlier (0.1, 0.0)
    best_t, best_gamma = select_optimal_temperature_and_gamma(results, grid_type="mpnn")
    assert (best_t, best_gamma) == (0.2, 0.5)


def test_10_all_configurations_infeasible_stops_tuning_arm():
    """Requirement 10: If every configuration in an arm is infeasible, stop that tuning arm and raise.

    Classification: DEVELOPMENT_TUNING_STAGE_INFEASIBLE. Zero fallback substitution.
    """
    # MPNN arm where all 25 configurations produce J = -inf
    mpnn_grid = get_mpnn_tuning_grid()
    all_infeasible_mpnn = {pair: float("-inf") for pair in mpnn_grid}

    with pytest.raises(RuntimeError, match="DEVELOPMENT_TUNING_STAGE_INFEASIBLE"):
        select_optimal_temperature_and_gamma(all_infeasible_mpnn, grid_type="mpnn")

    # Hybrid arm where all 35 configurations produce J = -inf
    hybrid_grid = get_hybrid_tuning_grid()
    all_infeasible_hybrid = {pair: float("-inf") for pair in hybrid_grid}

    with pytest.raises(RuntimeError, match="DEVELOPMENT_TUNING_STAGE_INFEASIBLE"):
        select_optimal_lambda_and_gamma(all_infeasible_hybrid)

