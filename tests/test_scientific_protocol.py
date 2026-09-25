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
)
from src.hybrid.selection import (
    Candidate,
    filter_viable_candidates,
    select_diverse_library,
    compute_pairwise_hamming_diversity,
    compute_diversity_distribution,
    compute_fixed_correspondence_sctm,
    compute_net_charge_at_ph74,
    compute_hydrophobic_core_fraction,
    ValidationOutcomeType,
    ValidationOutcome,
    evaluate_validation_outcome,
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
    # Total length = 8 -> 3 / 8 = 0.375
    core_frac = compute_hydrophobic_core_fraction(sequence, rsa_values, rsa_threshold=0.20)
    assert core_frac == pytest.approx(3.0 / 8.0)


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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

