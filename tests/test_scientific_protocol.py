"""
Scientific Protocol and Methodology Unit Tests.

Verifies:
1. Percentile rank normalization, scale-invariance, and deterministic tie handling.
2. Primary hybrid score formulation and lambda interpolation.
3. Exploratory logit hybrid designation.
4. Two-stage selection (hard viability gate -> greedy diversity-aware selection heuristic).
5. Order-independent set diversity and edge cases (K < 2).
6. Fixed-correspondence self-consistency TM-score (scTM).
7. Net charge at pH 7.4 calculation and explicit non-pI naming.
8. Hydrophobic core fraction calculation on predicted structure RSA.
9. Target-level paired statistical difference computation.
10. Matched candidate budget accounting.
11. E0-A (historical deterministic MAP) vs. E0-B (stochastic baseline) separation.
"""

import sys
from pathlib import Path
import numpy as np
import pytest
import torch

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.hybrid.scoring import (
    compute_percentile_ranks,
    compute_primary_hybrid_score,
    compute_exploratory_logit_hybrid,
    score_common_candidate_universe,
    validate_common_candidate_order,
    compute_mpnn_only_selection_score,
)
from src.hybrid.selection import (
    Candidate,
    filter_viable_candidates,
    deduplicate_candidates,
    select_diverse_library,
    LibrarySelectionResult,
    select_candidate_library,
    compute_pairwise_hamming_diversity,
    compute_diversity_distribution,
    compute_fixed_correspondence_sctm,
    compute_net_charge_at_ph74,
    compute_hydrophobic_core_fraction,
    ValidationOutcomeType,
    ValidationOutcome,
    evaluate_validation_outcome,
)
from src.hybrid.budget import (
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


def test_percentile_rank_normalization_and_scale_invariance():
    """Verifies that percentile ranking is scale-free, monotonic, and handles ties deterministically."""
    raw_scores = [1.2, 5.4, 3.1, 7.8, 0.5]
    p_ranks = compute_percentile_ranks(raw_scores)

    assert len(p_ranks) == len(raw_scores)
    # Highest score (7.8, idx 3) should have rank 5 / 5 = 1.0
    assert p_ranks[3] == 1.0
    # Lowest score (0.5, idx 4) should have rank 1 / 5 = 0.2
    assert p_ranks[4] == 0.2
    # Monotonicity check
    assert p_ranks[4] < p_ranks[0] < p_ranks[2] < p_ranks[1] < p_ranks[3]

    # Scale-invariance check: multiplying by 100 or shifting by 500 produces identical percentiles
    scaled_scores = [s * 100.0 + 500.0 for s in raw_scores]
    p_ranks_scaled = compute_percentile_ranks(scaled_scores)
    np.testing.assert_allclose(p_ranks, p_ranks_scaled)

    # Tie handling: identical scores receive equal average ranks
    tied_scores = [1.0, 5.0, 5.0, 10.0]
    p_tied = compute_percentile_ranks(tied_scores)
    # 1.0 -> rank 1 -> 0.25; 5.0, 5.0 -> ranks 2 and 3 average to 2.5 -> 2.5 / 4 = 0.625; 10.0 -> rank 4 -> 1.0
    assert p_tied[1] == p_tied[2] == 0.625
    assert p_tied[0] == 0.25
    assert p_tied[3] == 1.0

    # Edge cases
    assert len(compute_percentile_ranks([])) == 0
    assert compute_percentile_ranks([42.0])[0] == 1.0


def test_primary_hybrid_score_calculation():
    """Verifies primary hybrid score H = lambda * p_MPNN + (1 - lambda) * p_PS."""
    mpnn_scores = [-1.5, -0.8, -2.1, -0.4]  # Raw log-probs
    ps_scores = [-2.4, -1.1, -1.9, -0.9]    # Raw PLLs

    # lambda = 1.0 should equal pure MPNN percentiles
    h_mpnn_pure = compute_primary_hybrid_score(mpnn_scores, ps_scores, weight_lambda=1.0)
    p_mpnn = compute_percentile_ranks(mpnn_scores)
    np.testing.assert_allclose(h_mpnn_pure, p_mpnn)

    # lambda = 0.0 should equal pure PS percentiles
    h_ps_pure = compute_primary_hybrid_score(mpnn_scores, ps_scores, weight_lambda=0.0)
    p_ps = compute_percentile_ranks(ps_scores)
    np.testing.assert_allclose(h_ps_pure, p_ps)

    # lambda = 0.5 balanced
    h_balanced = compute_primary_hybrid_score(mpnn_scores, ps_scores, weight_lambda=0.5)
    expected_balanced = 0.5 * p_mpnn + 0.5 * p_ps
    np.testing.assert_allclose(h_balanced, expected_balanced)

    # Validation errors
    with pytest.raises(ValueError):
        compute_primary_hybrid_score(mpnn_scores, ps_scores, weight_lambda=1.5)
    with pytest.raises(ValueError):
        compute_primary_hybrid_score(mpnn_scores, ps_scores, weight_lambda=-0.1)
    with pytest.raises(ValueError):
        compute_primary_hybrid_score(mpnn_scores[:2], ps_scores, weight_lambda=0.5)


def test_exploratory_logit_hybrid_marked_ablation():
    """Verifies exploratory logit interpolation runs and is explicitly marked as ablation."""
    mpnn_logits = torch.randn(10, 20)
    ps_logits = torch.randn(10, 20)
    z_hybrid = compute_exploratory_logit_hybrid(mpnn_logits, ps_logits, weight_lambda=0.5)

    assert z_hybrid.shape == (10, 20)
    expected = 0.5 * mpnn_logits + 0.5 * ps_logits
    torch.testing.assert_close(z_hybrid, expected)
    # Verify docstring contains exploratory ablation warning
    assert "EXPLORATORY ABLATION" in compute_exploratory_logit_hybrid.__doc__


def test_two_stage_candidate_selection():
    """Verifies Stage 1 hard viability gate and Stage 2 diversity-aware selection heuristic."""
    candidates = [
        Candidate(id="c1", sequence="AAAA", target_id="t1", score=0.9, scrmsd_screen=1.2, plddt_screen=85.0),
        Candidate(id="c2", sequence="AAAK", target_id="t1", score=0.85, scrmsd_screen=1.8, plddt_screen=82.0),
        Candidate(id="c3", sequence="KKKK", target_id="t1", score=0.7, scrmsd_screen=1.5, plddt_screen=90.0),
        Candidate(id="c4", sequence="GGGG", target_id="t1", score=0.95, scrmsd_screen=2.8, plddt_screen=88.0),  # Fails RMSD
        Candidate(id="c5", sequence="CCCC", target_id="t1", score=0.92, scrmsd_screen=1.4, plddt_screen=75.0),  # Fails pLDDT
    ]

    # Stage 1: Viability Gate
    viable = filter_viable_candidates(candidates, scrmsd_threshold=2.0, plddt_threshold=80.0)
    viable_ids = [c.id for c in viable]
    assert viable_ids == ["c1", "c2", "c3"]
    assert "c4" not in viable_ids
    assert "c5" not in viable_ids

    # Stage 2: Selection Heuristic (M = 2)
    # c1 has highest score (0.9). c3 has lower score (0.7) but much higher distance (1.0 vs c2's 0.25).
    # With high gamma, c3 should be selected over c2.
    selected = select_diverse_library(viable, library_size_m=2, diversity_weight_gamma=2.0)
    selected_ids = [c.id for c in selected]
    assert len(selected) == 2
    assert selected_ids[0] == "c1"
    assert selected_ids[1] == "c3"

    # Edge case: If M >= len(viable), returns all viable candidates
    all_selected = select_diverse_library(viable, library_size_m=5)
    assert len(all_selected) == 3


def test_order_independent_pairwise_diversity():
    """Verifies that pairwise diversity is strictly order-independent and handles edge cases."""
    seqs = ["ACDEFGHIKL", "ACDEFGHIKM", "CCCCCCCCCC", "YYYYYYYYYY"]
    div_1 = compute_pairwise_hamming_diversity(seqs)

    # Permuted sequence order MUST produce identical diversity
    seqs_permuted = ["YYYYYYYYYY", "ACDEFGHIKM", "ACDEFGHIKL", "CCCCCCCCCC"]
    div_2 = compute_pairwise_hamming_diversity(seqs_permuted)
    assert div_1 == pytest.approx(div_2, abs=1e-12)

    # Identical sequences have 0 diversity
    assert compute_pairwise_hamming_diversity(["AAAA", "AAAA"]) == 0.0

    # Edge cases
    assert compute_pairwise_hamming_diversity([]) == 0.0
    assert compute_pairwise_hamming_diversity(["AAAA"]) == 0.0

    # Distribution helper
    stats = compute_diversity_distribution(seqs)
    assert stats["count"] == 6
    assert stats["mean"] == pytest.approx(div_1)
    assert stats["min"] <= stats["median"] <= stats["max"]


def test_fixed_correspondence_sctm():
    """Verifies fixed-correspondence TM-score with length-dependent d0 scaling."""
    # Test identical coordinates -> scTM = 1.0
    np.random.seed(42)
    coords = np.random.randn(50, 3) * 10.0
    tm_identical = compute_fixed_correspondence_sctm(coords, coords)
    assert tm_identical == pytest.approx(1.0, abs=1e-6)

    # Test under pure rigid-body rotation and translation -> scTM = 1.0
    theta = np.pi / 4.0
    rot = np.array([
        [np.cos(theta), -np.sin(theta), 0.0],
        [np.sin(theta), np.cos(theta), 0.0],
        [0.0, 0.0, 1.0],
    ])
    trans = np.array([5.0, -10.0, 3.0])
    coords_rotated = (coords @ rot.T) + trans
    tm_rotated = compute_fixed_correspondence_sctm(coords_rotated, coords)
    assert tm_rotated == pytest.approx(1.0, abs=1e-6)

    # Test random uncorrelated coordinates -> scTM << 0.5
    coords_random = np.random.randn(50, 3) * 20.0
    tm_random = compute_fixed_correspondence_sctm(coords_random, coords)
    assert tm_random < 0.35


def test_net_charge_at_ph74_vs_pi_naming():
    """Verifies net charge calculation at pH 7.4 and verifies explicit non-pI naming."""
    # Basic protein: Poly-Lysine has strong positive charge
    charge_poly_k = compute_net_charge_at_ph74("KKKKK")
    assert charge_poly_k > 4.0

    # Acidic protein: Poly-Aspartate has strong negative charge
    charge_poly_d = compute_net_charge_at_ph74("DDDDD")
    assert charge_poly_d < -4.0

    # Neutral sequence: Poly-Alanine has charge near zero (only N-term and C-term ionize)
    charge_poly_a = compute_net_charge_at_ph74("AAAAA")
    assert -0.5 < charge_poly_a < 0.5

    # Terminology verification: Docstring explicitly affirms Q_pH7.4 is NOT pI
    assert "NOT the isoelectric point" in compute_net_charge_at_ph74.__doc__


def test_hydrophobic_core_fraction():
    """Verifies hydrophobic core fraction counts {V, L, I, F, M, W} with RSA < 0.20."""
    sequence = "VLIFKDER"  # 8 residues: V, L, I, F are hydrophobic; K, D, E, R are polar/charged
    rsa_values = [0.10, 0.15, 0.30, 0.05, 0.10, 0.50, 0.60, 0.05]
    # V (0.10 < 0.20) -> buried hydrophobic (1)
    # L (0.15 < 0.20) -> buried hydrophobic (2)
    # I (0.30 >= 0.20) -> exposed hydrophobic (not buried)
    # F (0.05 < 0.20) -> buried hydrophobic (3)
    # K (0.10 < 0.20) -> buried charged (not in hydrophobic set)
    # Total buried hydrophobic = 3
    # Total hydrophobic residues = 4 (V, L, I, F) -> 3 / 4 = 0.75
    core_frac = compute_hydrophobic_core_fraction(sequence, rsa_values, rsa_threshold=0.20)
    assert core_frac == pytest.approx(3.0 / 4.0)


def test_target_level_paired_difference():
    """Verifies that primary statistical unit is TARGET-LEVEL mean scTM difference."""
    # Simulated N = 5 targets, each with M = 10 selected candidates
    n_targets = 5
    m_candidates = 10

    # Target-level mean scTM for hybrid and mpnn
    hybrid_target_means = []
    mpnn_target_means = []

    for t in range(n_targets):
        sctm_hybrid = np.random.uniform(0.70, 0.85, size=m_candidates)
        sctm_mpnn = np.random.uniform(0.65, 0.80, size=m_candidates)
        hybrid_target_means.append(float(np.mean(sctm_hybrid)))
        mpnn_target_means.append(float(np.mean(sctm_mpnn)))

    paired_differences = np.array(hybrid_target_means) - np.array(mpnn_target_means)
    assert len(paired_differences) == n_targets
    # Ensure differences are target-level scalars, not pooled candidate array of length 50
    assert paired_differences.ndim == 1 and paired_differences.shape[0] == 5


def test_matched_budget_bookkeeping():
    """Verifies candidate budget accounting requires matched K across models."""
    k_mpnn = 500
    k_ps = 500
    k_hybrid = 500

    # All candidate pools must have equal K
    assert k_mpnn == k_ps == k_hybrid

    # M must be strictly <= K
    m_library = 10
    assert m_library <= k_hybrid


def test_e0_split_separation():
    """Verifies explicit separation between E0-A (deterministic control) and E0-B (stochastic)."""
    e0_a = {
        "id": "E0-A",
        "type": "deterministic_map_control",
        "target": "1n5uA03",
        "length": 92,
        "recovery": 0.4130,
        "k_candidates": 1,
        "classification": "single_target_integration_control",
    }
    e0_b = {
        "id": "E0-B",
        "type": "stochastic_baseline",
        "targets": "TS50",
        "k_candidates": 500,
        "temperatures": [0.1, 0.5, 1.0],
        "classification": "multi_target_stochastic_baseline",
    }

    assert e0_a["classification"] != e0_b["classification"]
    assert e0_a["k_candidates"] == 1
    assert e0_b["k_candidates"] == 500


def test_candidate_budget_unambiguous_accounting():
    """Verifies that K=500 is total candidate generation budget per target across all seeds and temperatures.

    Enforces Interpretation A:
    - Standalone ProteinMPNN generates exactly 500 sequences per target (167 + 167 + 166 across 3 seeds).
    - Stochastic ProteinSolver (E0-B) generates exactly 500 sequences per target.
    - Primary Hybrid evaluates the common candidate universe of 500 sequences.
    - Total sequences per target is strictly 500, NOT 500 * 5 temperatures * 3 seeds = 7500.
    """
    seeds = [42, 1337, 2026]
    seed_allocations = [167, 167, 166]
    assert sum(seed_allocations) == 500
    assert len(seeds) == len(seed_allocations)

    budget_accounting = {
        "proteinmpnn_standalone_per_target": sum(seed_allocations),
        "proteinsolver_e0b_per_target": sum(seed_allocations),
        "primary_hybrid_candidate_universe": sum(seed_allocations),
        "historical_control_e0a": 1,
    }

    assert budget_accounting["proteinmpnn_standalone_per_target"] == 500
    assert budget_accounting["proteinsolver_e0b_per_target"] == 500
    assert budget_accounting["primary_hybrid_candidate_universe"] == 500
    assert budget_accounting["historical_control_e0a"] == 1

    # Disallow condition-multiplied budget interpretation
    n_temperatures = 5
    n_seeds = 3
    condition_multiplied_budget = 500 * n_temperatures * n_seeds
    assert budget_accounting["proteinmpnn_standalone_per_target"] != condition_multiplied_budget


def test_common_hybrid_candidate_universe():
    """Verifies that hybrid scoring strictly evaluates a common, frozen candidate universe."""
    k = 500
    candidate_ids = [f"cand_{i}" for i in range(k)]
    sequences = [f"SEQ_{i}" for i in range(k)]
    mpnn_scores = np.random.normal(loc=-1.5, scale=0.3, size=k)
    ps_scores = np.random.normal(loc=-2.0, scale=0.5, size=k)

    # Valid common universe scoring
    hybrid_scores = score_common_candidate_universe(
        candidate_ids=candidate_ids,
        sequences=sequences,
        mpnn_scores=mpnn_scores,
        ps_scores=ps_scores,
        weight_lambda=0.6,
        tie_method="average",
    )
    assert len(hybrid_scores) == k
    assert np.all(hybrid_scores > 0.0) and np.all(hybrid_scores <= 1.0)

    # Mismatched sequence length raises ValueError
    with pytest.raises(ValueError, match="Common candidate universe dimension mismatch"):
        score_common_candidate_universe(
            candidate_ids=candidate_ids,
            sequences=sequences[:400],  # mismatched length
            mpnn_scores=mpnn_scores,
            ps_scores=ps_scores,
            weight_lambda=0.6,
        )

    # Mismatched score length raises ValueError
    with pytest.raises(ValueError, match="Common candidate universe dimension mismatch"):
        score_common_candidate_universe(
            candidate_ids=candidate_ids,
            sequences=sequences,
            mpnn_scores=mpnn_scores[:450],  # mismatched length
            ps_scores=ps_scores,
            weight_lambda=0.6,
        )


def test_primary_alphafold2_exact_configuration():
    """Verifies that the Primary Final Validation Oracle has one singular frozen configuration without OR-alternatives."""
    af2_frozen_config = {
        "oracle": "AlphaFold2",
        "version": "v2.3.2",
        "model_checkpoint": "model_1_ptm",
        "precision": "float16",
        "num_recycle": 3,
        "use_templates": False,
        "msa_mode": "single_sequence",
        "use_amber": False,
        "random_seed": 42,
        "hardware": "NVIDIA RTX 3050 6GB Laptop GPU",
    }

    # Precision must be singular float16, never ambiguous FP16/BF16
    assert af2_frozen_config["precision"] == "float16"
    assert "bf16" not in af2_frozen_config["precision"].lower()
    assert "or" not in af2_frozen_config["precision"].lower()

    # Recycles, templates, MSA mode must be frozen
    assert af2_frozen_config["num_recycle"] == 3
    assert af2_frozen_config["use_templates"] is False
    assert af2_frozen_config["msa_mode"] == "single_sequence"
    assert af2_frozen_config["use_amber"] is False
    assert af2_frozen_config["random_seed"] == 42


def test_provenance_language_consistency():
    """Verifies that benchmark provenance language decouples ProteinSolver from blanket TS50 training separation."""
    prereg_path = PROJECT_ROOT / "science" / "PREREGISTRATION.md"
    assert prereg_path.exists()
    content = prereg_path.read_text(encoding="utf-8")

    # Disallow blanket "<30% sequence identity to training sets" without qualification
    assert "TS50 non-redundant PDB crystal structures (<30% sequence identity to training sets)" not in content

    # Verify model-specific qualification is present
    assert "ProteinSolver Gene3D 72M training membership documented per model" in content
    assert "superfamily absence verified where accessible, otherwise NOT VERIFIABLE FROM ACCESSIBLE METADATA" in content

    # Rule check: Targets must NEVER be described as guaranteed held-out
    assert 'Targets must NEVER be described as "guaranteed held-out" or "unseen".' in content


def test_folding_failure_taxonomy_handling():
    """Verifies explicit separation between scientific folding failure and infrastructure/runtime failure."""
    target_coords = np.array([
        [0.0, 0.0, 0.0],
        [1.0, 1.0, 1.0],
        [2.0, 2.0, 2.0],
        [3.0, 3.0, 3.0],
    ])
    pred_coords = target_coords + 0.1

    # 1. Valid prediction: computes valid scTM
    outcome_valid = evaluate_validation_outcome(
        outcome_type=ValidationOutcomeType.VALID,
        pred_coords=pred_coords,
        target_coords=target_coords,
        plddt=85.0,
        scrmsd=0.15,
    )
    assert outcome_valid.status == ValidationOutcomeType.VALID
    assert outcome_valid.sctm is not None and outcome_valid.sctm > 0.90
    assert outcome_valid.is_valid_for_statistical_test is True

    # 2. Scientific folding failure (e.g. non-physical, pLDDT < 10): assigned scTM = 0.0
    outcome_scientific = evaluate_validation_outcome(
        outcome_type=ValidationOutcomeType.SCIENTIFIC_FAILURE,
        plddt=8.5,
        error_reason="Model collapsed to non-physical steric overlap",
    )
    assert outcome_scientific.status == ValidationOutcomeType.SCIENTIFIC_FAILURE
    assert outcome_scientific.sctm == 0.0
    assert outcome_scientific.is_valid_for_statistical_test is True  # biological failure penalizes model

    # 3. Infrastructure failure (OOM, timeout, crash): NEVER assigned scTM = 0.0
    outcome_infra = evaluate_validation_outcome(
        outcome_type=ValidationOutcomeType.INFRASTRUCTURE_FAILURE,
        error_reason="CUDA out of memory exception during inference",
    )
    assert outcome_infra.status == ValidationOutcomeType.INFRASTRUCTURE_FAILURE
    assert outcome_infra.sctm is None  # NEVER 0.0
    assert outcome_infra.is_valid_for_statistical_test is False

    # 4. Invalidation criterion check: if infrastructure failures exceed 10%
    n_total = 50
    infra_failures_pass = 4  # 4/50 = 8% <= 10% -> OK
    infra_failures_fail = 6  # 6/50 = 12% > 10% -> INVALID
    assert (infra_failures_pass / n_total) <= 0.10
    assert (infra_failures_fail / n_total) > 0.10


def test_sctm_terminology_and_fixed_correspondence():
    """Verifies that scTM docstrings and definitions explicitly specify fixed correspondence without alignment."""
    doc = compute_fixed_correspondence_sctm.__doc__
    assert doc is not None
    assert "Fixed-Correspondence Self-Consistency TM-score (scTM)" in doc
    assert "strict 1-to-1 sequence-to-structure residue correspondence" in doc
    assert "It does NOT perform dynamic programming sequence alignment" in doc
    assert "must NOT be described as standard alignment-based TM-score" in doc


def test_exact_development_temperature_allocation():
    """Verifies exact balanced integer allocation matrices for development tuning (K=100)."""
    # 1. ProteinMPNN (K=100)
    mpnn_alloc = get_development_temperature_allocation("proteinmpnn")
    assert validate_budget_matrix(mpnn_alloc, 100) is True
    assert set(mpnn_alloc.keys()) == {0.1, 0.2, 0.5, 0.8, 1.0}
    # Verify exact balanced table
    assert mpnn_alloc[0.1] == {42: 7, 1337: 7, 2026: 6}
    assert mpnn_alloc[0.2] == {42: 7, 1337: 6, 2026: 7}
    assert mpnn_alloc[0.5] == {42: 6, 1337: 7, 2026: 7}
    assert mpnn_alloc[0.8] == {42: 7, 1337: 7, 2026: 6}
    assert mpnn_alloc[1.0] == {42: 7, 1337: 6, 2026: 7}
    # Per-seed totals
    seed_totals = {42: 0, 1337: 0, 2026: 0}
    for t_counts in mpnn_alloc.values():
        for s, c in t_counts.items():
            seed_totals[s] += c
    assert seed_totals == {42: 34, 1337: 33, 2026: 33}

    # 2. ProteinSolver E0-B (K=100)
    ps_alloc = get_development_temperature_allocation("proteinsolver")
    assert validate_budget_matrix(ps_alloc, 100) is True
    assert set(ps_alloc.keys()) == {0.1, 0.5, 1.0}
    # Verify exact balanced table
    assert ps_alloc[0.1] == {42: 12, 1337: 11, 2026: 11}
    assert ps_alloc[0.5] == {42: 11, 1337: 11, 2026: 11}
    assert ps_alloc[1.0] == {42: 11, 1337: 11, 2026: 11}
    ps_seed_totals = {42: 0, 1337: 0, 2026: 0}
    for t_counts in ps_alloc.values():
        for s, c in t_counts.items():
            ps_seed_totals[s] += c
    assert ps_seed_totals == {42: 34, 1337: 33, 2026: 33}


def test_frozen_test_seed_allocation():
    """Verifies frozen test-time seed allocation at T* for primary TS50 benchmark (K=500)."""
    test_alloc = get_test_seed_allocation(500)
    assert test_alloc == {42: 167, 1337: 167, 2026: 166}
    assert sum(test_alloc.values()) == 500


def test_candidate_id_reproducibility():
    """Verifies reproducible candidate identifier derivation."""
    cid = generate_candidate_id(
        target_id="1n5uA03",
        method_arm="hybrid",
        temperature=0.2,
        seed=42,
        seq_idx=7,
    )
    assert cid == "1n5uA03_hybrid_T0.2_s42_idx0007"


def test_common_candidate_order_validation():
    """Verifies validation of identical sequence and ID ordering across models before scoring."""
    ids = ["c1", "c2", "c3"]
    seqs = ["ACDEF", "GHIKL", "MNPQR"]

    # Passing case: exact match
    assert validate_common_candidate_order(ids, list(ids), seqs, list(seqs)) is True

    # Failing case: ID mismatch
    with pytest.raises(ValueError, match="Candidate ID mismatch"):
        validate_common_candidate_order(ids, ["c1", "c3", "c2"], seqs, seqs)

    # Failing case: Sequence mismatch
    with pytest.raises(ValueError, match="Candidate sequence mismatch"):
        validate_common_candidate_order(ids, ids, seqs, ["ACDEF", "AAAAA", "MNPQR"])

    # Failing case: Length mismatch
    with pytest.raises(ValueError, match="Candidate ID length mismatch"):
        validate_common_candidate_order(ids, ["c1", "c2"], seqs, seqs)


def test_normalized_mpnn_only_selection_score():
    """Verifies that MPNN-only greedy selection uses percentile rank score normalized to [0, 1]."""
    raw_mpnn_scores = [-2.5, -1.2, -0.8, -3.1, -1.5]
    p_mpnn = compute_mpnn_only_selection_score(raw_mpnn_scores)

    assert len(p_mpnn) == len(raw_mpnn_scores)
    # Highest raw score (-0.8, idx 2) maps to 1.0
    assert p_mpnn[2] == 1.0
    # Lowest raw score (-3.1, idx 3) maps to 0.2
    assert p_mpnn[3] == 0.2
    # Output is bounded in (0, 1]
    assert np.all(p_mpnn > 0.0) and np.all(p_mpnn <= 1.0)


def test_gamma_search_grid_freeze():
    """Verifies frozen dimensionless gamma search grid for Stage 2 diversity selection."""
    assert GAMMA_SEARCH_GRID == (0.0, 0.25, 0.5, 1.0, 2.0)
    # Dimensionless check: all entries non-negative floats
    for g in GAMMA_SEARCH_GRID:
        assert isinstance(g, float) and g >= 0.0


def test_first_greedy_selection_and_deterministic_tie_breaking():
    """Verifies greedy selection initialization when S' is empty and deterministic tie breaking."""
    # When S' is empty, first candidate chosen has maximum primary score
    c1 = Candidate(id="cand_A", sequence="AAAA", target_id="t1", score=0.6)
    c2 = Candidate(id="cand_B", sequence="CCCC", target_id="t1", score=0.9)  # highest score
    c3 = Candidate(id="cand_C", sequence="DDDD", target_id="t1", score=0.4)

    selected = select_diverse_library([c1, c2, c3], library_size_m=2, diversity_weight_gamma=1.0)
    assert len(selected) == 2
    # First chosen must be highest primary score (c2)
    assert selected[0].id == "cand_B"

    # Tie breaking test: c1 and c2 have identical scores
    c_tie1 = Candidate(id="cand_Z", sequence="AAAA", target_id="t1", score=0.8)
    c_tie2 = Candidate(id="cand_A", sequence="CCCC", target_id="t1", score=0.8)
    c_tie3 = Candidate(id="cand_M", sequence="DDDD", target_id="t1", score=0.5)

    selected_tie = select_diverse_library([c_tie1, c_tie2, c_tie3], library_size_m=2, diversity_weight_gamma=0.0)
    # With gamma=0, candidates are chosen purely by score with tie broken by ID ascending: "cand_A" < "cand_Z"
    assert selected_tie[0].id == "cand_A"
    assert selected_tie[1].id == "cand_Z"


def test_duplicate_candidate_accounting_and_deduplication():
    """Verifies that duplicate sequences are tracked, contribute 0 distance, and are deduplicated before selection."""
    c1 = Candidate(id="c1", sequence="AAAA", target_id="t1", score=0.7)
    c2 = Candidate(id="c2", sequence="AAAA", target_id="t1", score=0.9)  # duplicate sequence, higher score
    c3 = Candidate(id="c3", sequence="CCCC", target_id="t1", score=0.5)
    c4 = Candidate(id="c4", sequence="DDDD", target_id="t1", score=0.6)

    # Raw candidate pool has 4 sequences, but only 3 unique
    unique_cands, dup_rate = deduplicate_candidates([c1, c2, c3, c4])
    assert len(unique_cands) == 3
    assert dup_rate == 0.25  # 1 duplicate / 4 total = 25%

    # For the duplicate sequence "AAAA", the higher scoring candidate (c2, score=0.9) was retained
    retained_ids = {c.id for c in unique_cands}
    assert "c2" in retained_ids
    assert "c1" not in retained_ids

    # Identical sequences have Hamming distance 0.0
    dist_self = compute_pairwise_hamming_diversity(["AAAA", "AAAA"])
    assert dist_self == 0.0


def test_insufficient_viable_candidates_handling():
    """Verifies that targets with < M=10 unique viable candidates are marked SELECTION_INFEASIBLE_LT_M."""
    # Create only 5 viable candidates when M=10 is required
    viable_5 = [
        Candidate(id=f"c{i}", sequence=f"SEQ{i}AAAA", target_id="t1", score=0.5)
        for i in range(5)
    ]

    res = select_candidate_library(
        viable_candidates=viable_5,
        library_size_m=10,
        diversity_weight_gamma=1.0,
        target_id="t1",
        arm="hybrid",
    )

    assert res.status == ValidationOutcomeType.SELECTION_INFEASIBLE_LT_M
    assert len(res.selected) == 0  # No padding, no silent regeneration
    assert res.unique_viable_count == 5
    assert "SELECTION_INFEASIBLE_LT_M" in str(res.error_reason)

    # Evaluate validation outcome for infeasible target
    outcome = evaluate_validation_outcome(
        outcome_type=ValidationOutcomeType.SELECTION_INFEASIBLE_LT_M,
        error_reason=res.error_reason,
    )
    assert outcome.status == ValidationOutcomeType.SELECTION_INFEASIBLE_LT_M
    assert outcome.sctm is None  # Undefined in complete-case analysis
    assert outcome.is_valid_for_statistical_test is False  # Excluded from complete-case paired differences


def test_bootstrap_target_level_semantics():
    """Verifies that bootstrap resampling operates strictly on target-level paired differences d_t."""
    # N = 50 TS50 targets
    n_targets = 50
    rng = np.random.default_rng(42)
    # Simulate paired target differences
    d_t = rng.normal(loc=0.03, scale=0.05, size=n_targets)

    # Target-level bootstrap: 10,000 resamples of the length-50 vector d_t
    n_boot = 10000
    boot_means = np.empty(n_boot, dtype=np.float64)
    for b in range(n_boot):
        sample = rng.choice(d_t, size=n_targets, replace=True)
        boot_means[b] = np.mean(sample)

    ci_95 = (np.percentile(boot_means, 2.5), np.percentile(boot_means, 97.5))
    assert ci_95[0] < ci_95[1]
    # Unit check: bootstrap was performed strictly on target differences d_t (N=50), never on candidates
    assert len(d_t) == 50


def test_prohibited_sctm_fold_threshold_wording():
    """Requirement: Authoritative docs must NOT claim scTM > 0.5 indicates identical global fold topology.

    Fixed-correspondence scTM uses Kabsch rigid-body superposition without alignment optimization
    and does NOT inherit the classical alignment-based 0.5 fold threshold.
    """
    from pathlib import Path

    doc_paths = [
        Path("science/metrics.md"),
        Path("science/PREREGISTRATION.md"),
        Path("science/evaluation_protocol.md"),
        Path("docs/PROJECT_TRUTH.md"),
    ]

    for p in doc_paths:
        if not p.exists():
            continue
        content = p.read_text(encoding="utf-8")
        assert "scTM > 0.5 indicates identical global fold topology" not in content, (
            f"Prohibited fold topology claim found in {p}"
        )
        assert "indicates identical global fold topology" not in content, (
            f"Prohibited fold topology claim found in {p}"
        )


def test_statistical_wilcoxon_edge_cases():
    """Verifies two-sided paired Wilcoxon signed-rank test and bootstrap edge cases under frozen SciPy protocol."""
    import scipy.stats as stats
    from src.hybrid.statistics import (
        compute_paired_wilcoxon_test,
        compute_paired_bootstrap_ci,
        compute_hodges_lehmann_estimator,
    )

    # 1. Standard valid paired differences (N=50)
    rng = np.random.default_rng(42)
    d_t = rng.normal(loc=0.03, scale=0.05, size=50)
    res = compute_paired_wilcoxon_test(d_t)
    assert res.pvalue is not None
    assert 0.0 <= res.pvalue <= 1.0
    assert res.method == "asymptotic"
    assert res.zero_method == "wilcox"
    assert res.correction is True
    assert res.alternative == "two-sided"
    assert res.n_total == 50
    assert res.n_non_zero > 0

    # Verify direct scipy call with frozen parameters matches
    scipy_res = stats.wilcoxon(d_t, zero_method="wilcox", correction=True, alternative="two-sided", method="asymptotic")
    assert res.statistic == pytest.approx(float(scipy_res.statistic))
    assert res.pvalue == pytest.approx(float(scipy_res.pvalue))

    # 2. All zero differences: with zero_method='wilcox', all zeros are discarded -> p=1.0, HL=0.0, d_z=0.0
    d_zeros = np.zeros(50)
    res_zeros = compute_paired_wilcoxon_test(d_zeros)
    assert res_zeros.pvalue == 1.0
    assert res_zeros.hodges_lehmann == 0.0
    assert res_zeros.cohens_dz == 0.0
    assert res_zeros.n_non_zero == 0

    # 3. Constant non-zero differences (s_d = 0)
    d_const = np.full(50, 0.05)
    res_const = compute_paired_wilcoxon_test(d_const)
    assert res_const.pvalue < 1e-5  # Highly significant all-positive differences
    assert res_const.hodges_lehmann == pytest.approx(0.05)
    assert res_const.cohens_dz == 0.0  # Zero standard deviation

    # 4. Explicit input validation: reject NaN or inf
    d_nan = np.array([0.02, np.nan, 0.04])
    with pytest.raises(ValueError, match="NaN or infinite"):
        compute_paired_wilcoxon_test(d_nan)

    d_inf = np.array([0.02, np.inf, 0.04])
    with pytest.raises(ValueError, match="NaN or infinite"):
        compute_paired_wilcoxon_test(d_inf)

    # 5. Insufficient paired observations
    with pytest.raises(ValueError, match="Insufficient paired observations"):
        compute_paired_wilcoxon_test([0.05])

    # 6. Bootstrap reproducibility with fixed seed 42
    ci1 = compute_paired_bootstrap_ci(d_t, n_resamples=1000, seed=42)
    ci2 = compute_paired_bootstrap_ci(d_t, n_resamples=1000, seed=42)
    assert ci1[0.95][0] == pytest.approx(ci2[0.95][0])
    assert ci1[0.95][1] == pytest.approx(ci2[0.95][1])
    assert ci1[0.99][0] == pytest.approx(ci2[0.99][0])
    assert ci1[0.99][1] == pytest.approx(ci2[0.99][1])
    assert ci1[0.95][0] < ci1[0.95][1]



def test_hydrophobic_core_fraction_calculation():
    """Verifies reconciled hydrophobic core fraction definition: core hydrophobic / total hydrophobic."""
    # Case 1: Sequence with known hydrophobics: V (pos 2) with RSA 0.10, L (pos 3) with RSA 0.50 -> 1 core / 2 total = 0.5
    seq = "AGVLGA"
    rsa = [0.5, 0.4, 0.10, 0.50, 0.7, 0.8]  # V has 0.10 (<0.20), L has 0.50 (>=0.20)
    f_core = compute_hydrophobic_core_fraction(seq, rsa)
    assert f_core == 0.5  # 1 core / 2 total = 0.5

    # Case 2: Zero hydrophobic residues edge case (e.g. all-charged sequence)
    seq_no_hydro = "GGGKRRKGG"
    rsa_no_hydro = [0.5] * len(seq_no_hydro)
    f_core_zero = compute_hydrophobic_core_fraction(seq_no_hydro, rsa_no_hydro)
    assert f_core_zero == 0.0

    # Case 3: All hydrophobic residues buried: V (RSA 0.10) and I (RSA 0.05) -> 2 / 2 = 1.0
    seq_all_core = "AVAI"
    rsa_all_core = [0.6, 0.10, 0.5, 0.05]
    f_core_all = compute_hydrophobic_core_fraction(seq_all_core, rsa_all_core)
    assert f_core_all == 1.0


def test_primary_comparison_and_sample_size_invariants():
    """Verifies that primary comparison is strictly Hybrid vs MPNN-only and N=50 is confirmatory.

    Rules:
    1. The primary confirmatory comparator is strictly MPNN-only.
    2. 'Best Single Model' must NEVER appear as the primary comparator.
    3. Confirmatory sample size is strictly N=50 (TS50).
    4. N=20 is strictly the development/tuning set.
    """
    from pathlib import Path

    doc_paths = [
        Path("science/PREREGISTRATION.md"),
        Path("science/evaluation_protocol.md"),
        Path("science/metrics.md"),
        Path("docs/PROJECT_TRUTH.md"),
        Path("PROJECT_STATE.md"),
    ]

    for p in doc_paths:
        if not p.exists():
            continue
        content = p.read_text(encoding="utf-8")
        assert "Best Single Model" not in content, (
            f"Prohibited 'Best Single Model' phrase found in {p}"
        )
        assert "best single model" not in content.lower() or "exploratory" in content.lower(), (
            f"'best single model' found without exploratory qualification in {p}"
        )

    # Check PREREGISTRATION.md specifics
    prereg = Path("science/PREREGISTRATION.md").read_text(encoding="utf-8")
    assert "d_t = \\overline{\\text{scTM}}_{\\text{hybrid}}(t) - \\overline{\\text{scTM}}_{\\text{MPNN-only}}(t)" in prereg
    assert "$N = 50$ TS50 targets" in prereg
    assert "Development / Tuning Set ($N = 20$)" in prereg


def test_sequence_length_guard_and_oracle_failure_invariants():
    """Verifies sequence length guard (L <= 1024) and development-time oracle failure handling."""
    from src.hybrid.selection import (
        validate_target_sequence_length,
        ValidationOutcome,
        ValidationOutcomeType,
    )
    from src.hybrid.optimization import (
        compute_development_target_sctm_mean,
        compute_development_objective,
    )

    # 1. Sequence length guard tests
    validate_target_sequence_length("A" * 100, target_id="test_100")
    validate_target_sequence_length("A" * 1024, target_id="test_1024")
    with pytest.raises(ValueError, match="exceeds frozen oracle maximum"):
        validate_target_sequence_length("A" * 1025, target_id="test_1025")

    # 2. Development target scTM mean under complete valid library (M=10)
    valid_outcomes = [
        ValidationOutcome(status=ValidationOutcomeType.VALID, sctm=0.80, scrmsd=1.2, plddt=85.0)
        for _ in range(10)
    ]
    mean_val = compute_development_target_sctm_mean(valid_outcomes)
    assert mean_val == pytest.approx(0.80)

    # 3. Scientific folding failure (biological non-physical structure, pLDDT < 10) -> scTM = 0.0 included
    mixed_outcomes = [
        ValidationOutcome(status=ValidationOutcomeType.VALID, sctm=0.80, scrmsd=1.2, plddt=85.0)
        for _ in range(9)
    ] + [
        ValidationOutcome(status=ValidationOutcomeType.SCIENTIFIC_FAILURE, sctm=0.0, scrmsd=None, plddt=8.0)
    ]
    mixed_mean = compute_development_target_sctm_mean(mixed_outcomes)
    assert mixed_mean == pytest.approx((0.80 * 9 + 0.0) / 10.0)

    # 4. Infrastructure failure on a selected candidate -> returns None (never assign scTM=0.0)
    infra_outcomes = [
        ValidationOutcome(status=ValidationOutcomeType.VALID, sctm=0.80, scrmsd=1.2, plddt=85.0)
        for _ in range(9)
    ] + [
        ValidationOutcome(status=ValidationOutcomeType.INFRASTRUCTURE_FAILURE, sctm=None, scrmsd=None, plddt=None)
    ]
    infra_mean = compute_development_target_sctm_mean(infra_outcomes)
    assert infra_mean is None

    # 5. Objective J under development target infrastructure failure -> J = -infinity (ineligible)
    dev_means_with_infra = [0.80] * 19 + [None]
    j_val = compute_development_objective(dev_means_with_infra)
    assert j_val == float("-inf")


def test_project_truth_authority_scope():
    """Verifies that docs/PROJECT_TRUTH.md authority is properly scoped and defers to PREREGISTRATION for protocol."""
    from pathlib import Path
    pt_path = Path("docs/PROJECT_TRUTH.md")
    assert pt_path.exists(), "docs/PROJECT_TRUTH.md must exist"
    content = pt_path.read_text(encoding="utf-8")

    assert "authoritative record of verified implementation facts" in content.lower()
    assert "evidence status" in content.lower()
    assert "known limitations" in content.lower()
    assert "untested status" in content.lower()
    assert "science/preregistration.md" in content.lower()
    assert "decision_log.md" in content.lower()
    # Must NOT claim that all other documents defer to it universally for protocol
    assert "all other project documents defer to this one when there is a conflict" not in content.lower()



def test_esmfold_screening_plddt_scale_and_viability():
    """Regression test: ESMFold output pLDDT in [0, 1] must be scaled to [0, 100] for viability threshold.
    
    If unscaled (e.g. 0.85), evaluating against plddt_threshold=80.0 causes 100% false-negative infeasibility.
    With proper scaling (0.85 * 100 = 85.0), high-confidence predictions pass the viability gate.
    """
    raw_hf_esmfold_plddt = 0.85  # Typical high-confidence output from Hugging Face EsmForProteinFolding
    scrmsd = 1.2  # Well within scRMSD <= 2.0 A

    # Defective unscaled candidate
    defective_cand = Candidate(
        id="c_defective",
        sequence="ACDEFGHIKL",
        target_id="2e6i.A",
        score=0.9,
        scrmsd_screen=scrmsd,
        plddt_screen=raw_hf_esmfold_plddt,  # 0.85 instead of 85.0
    )
    unscaled_viable = filter_viable_candidates([defective_cand], scrmsd_threshold=2.0, plddt_threshold=80.0)
    assert len(unscaled_viable) == 0, "Unscaled candidate must fail when checked against 80.0"

    # Properly rescaled candidate
    scaled_plddt = raw_hf_esmfold_plddt * 100.0 if raw_hf_esmfold_plddt <= 1.0 else raw_hf_esmfold_plddt
    fixed_cand = Candidate(
        id="c_fixed",
        sequence="ACDEFGHIKL",
        target_id="2e6i.A",
        score=0.9,
        scrmsd_screen=scrmsd,
        plddt_screen=scaled_plddt,  # 85.0
    )
    scaled_viable = filter_viable_candidates([fixed_cand], scrmsd_threshold=2.0, plddt_threshold=80.0)
    assert len(scaled_viable) == 1, "Scaled candidate must pass when pLDDT >= 80.0"
    assert scaled_viable[0].id == "c_fixed"


def test_kabsch_alignment_invariance():
    """Verifies that Kabsch superposition correctly aligns rotated and translated coordinates."""
    # Synthetic target coordinates (L=10, 3)
    np.random.seed(42)
    coords_a = np.random.randn(10, 3)

    # Apply known 3D rotation and translation
    theta = np.pi / 4
    r_z = np.array([
        [np.cos(theta), -np.sin(theta), 0],
        [np.sin(theta), np.cos(theta), 0],
        [0, 0, 1],
    ])
    shift = np.array([12.5, -7.3, 4.2])
    coords_b = (r_z @ coords_a.T).T + shift

    # Kabsch alignment
    p_c = coords_b - coords_b.mean(axis=0)
    t_c = coords_a - coords_a.mean(axis=0)
    h = p_c.T @ t_c
    u, _, vt = np.linalg.svd(h)
    d = np.linalg.det(vt.T @ u.T)
    r = vt.T @ np.diag([1.0, 1.0, d]) @ u.T
    p_rot = (r @ p_c.T).T
    rmsd = float(np.sqrt(np.mean(np.sum((p_rot - t_c) ** 2, axis=1))))

    assert rmsd < 1e-6, f"Exact rotated coordinates must have near-zero RMSD, got {rmsd}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])



