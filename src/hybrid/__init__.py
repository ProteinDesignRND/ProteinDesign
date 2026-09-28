"""
Hybrid scoring and candidate selection package for Protein Design.

Provides:
- Scale-free within-pool percentile rank hybrid scoring (Primary Method).
- Normalized MPNN-only selection score (Primary Baseline).
- Exploratory logit interpolation ablation (Exploratory Ablation).
- Two-stage candidate selection (Hard Viability Gate -> Diversity-Aware Selection).
- Unique candidate deduplication and library selection with infeasibility handling.
- Candidate generation budget and deterministic temperature/seed allocation.
- Order-independent set diversity metrics.
- Fixed-correspondence self-consistency TM-score.
- Biophysical heuristic proxies (Net charge at pH 7.4, Hydrophobic core fraction).
"""

from .scoring import (
    compute_percentile_ranks,
    compute_primary_hybrid_score,
    compute_exploratory_logit_hybrid,
    score_common_candidate_universe,
    validate_common_candidate_order,
    compute_mpnn_only_selection_score,
)
from .selection import (
    Candidate,
    filter_viable_candidates,
    deduplicate_candidates,
    select_diverse_library,
    LibrarySelectionResult,
    select_candidate_library,
    compute_pairwise_hamming_diversity,
    compute_fixed_correspondence_sctm,
    compute_net_charge_at_ph74,
    compute_hydrophobic_core_fraction,
    ValidationOutcomeType,
    ValidationOutcome,
    evaluate_validation_outcome,
)
from .budget import (
    PROTEINMPNN_DEV_ALLOCATION,
    PROTEINSOLVER_DEV_ALLOCATION,
    PRIMARY_TEST_SEED_ALLOCATION_500,
    GAMMA_SEARCH_GRID,
    LAMBDA_SEARCH_GRID,
    get_development_temperature_allocation,
    get_test_seed_allocation,
    generate_candidate_id,
    validate_budget_matrix,
)
from .optimization import (
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

__all__ = [
    "compute_percentile_ranks",
    "compute_primary_hybrid_score",
    "compute_exploratory_logit_hybrid",
    "score_common_candidate_universe",
    "validate_common_candidate_order",
    "compute_mpnn_only_selection_score",
    "Candidate",
    "filter_viable_candidates",
    "deduplicate_candidates",
    "select_diverse_library",
    "LibrarySelectionResult",
    "select_candidate_library",
    "compute_pairwise_hamming_diversity",
    "compute_fixed_correspondence_sctm",
    "compute_net_charge_at_ph74",
    "compute_hydrophobic_core_fraction",
    "ValidationOutcomeType",
    "ValidationOutcome",
    "evaluate_validation_outcome",
    "PROTEINMPNN_DEV_ALLOCATION",
    "PROTEINSOLVER_DEV_ALLOCATION",
    "PRIMARY_TEST_SEED_ALLOCATION_500",
    "GAMMA_SEARCH_GRID",
    "LAMBDA_SEARCH_GRID",
    "get_development_temperature_allocation",
    "get_test_seed_allocation",
    "generate_candidate_id",
    "validate_budget_matrix",
    "DEVELOPMENT_TARGET_COUNT",
    "SELECTION_LIBRARY_SIZE",
    "MPNN_TEMPERATURE_GRID",
    "PROTEINSOLVER_TEMPERATURE_GRID",
    "get_mpnn_tuning_grid",
    "get_proteinsolver_tuning_grid",
    "get_hybrid_tuning_grid",
    "compute_target_sctm_mean",
    "compute_development_objective",
    "compute_configuration_infeasibility_rate",
    "select_optimal_temperature_and_gamma",
    "select_optimal_lambda_and_gamma",
    "DevelopmentHyperparameterState",
]

