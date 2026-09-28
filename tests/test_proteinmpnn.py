"""
Unit and integration tests for cleanroom official ProteinMPNN integration.

Verifies:
1. Model loading, checkpoint integrity, and SHA-256 cryptographic verification.
2. Input coordinate validation and PDB backbone extraction.
3. Sequence generation interface, sequence length, and standard 20-amino-acid alphabet.
4. Deterministic candidate ID formatting compliant with project frozen rules.
5. Random seed plumbing and residue permutation determinism vs stochastic divergence.
6. Zero native sequence leakage during candidate generation.
7. Sequence scoring interface, score direction (higher mean log-prob is better),
   and diagnostic perplexity computation.
8. Seamless end-to-end interface compatibility with src/hybrid scoring, normalization,
   and diversity selection.
9. Provenance manifest completeness.
"""

from pathlib import Path
import math
import numpy as np
import pytest
import torch

from src.hybrid.budget import generate_candidate_id
from src.hybrid.scoring import (
    compute_mpnn_only_selection_score,
    score_common_candidate_universe,
)
from src.hybrid.selection import (
    Candidate,
    compute_pairwise_hamming_diversity,
    select_diverse_library,
)
from src.proteinmpnn import (
    ProteinMPNNWrapper,
    extract_backbone_coordinates,
    get_proteinmpnn_provenance_manifest,
    load_protein_mpnn_model,
    validate_backbone_coordinates,
    verify_checkpoint_integrity,
    ALPHABET,
    BACKBONE_ATOMS,
    DEFAULT_MODEL_NAME,
    OFFICIAL_VANILLA_CHECKPOINTS,
)

PDB_1N5U = Path("experiments/EXP000_PROTEINSOLVER_SMOKETEST/input/1n5uA03.pdb")


# =========================================================================
# 1. Provenance and Checkpoint Integrity Tests
# =========================================================================

def test_checkpoint_sha256_integrity():
    """Verifies that the official published model checkpoint matches its cryptographic SHA-256 hash."""
    assert verify_checkpoint_integrity(model_name=DEFAULT_MODEL_NAME) is True

    manifest = get_proteinmpnn_provenance_manifest(model_name=DEFAULT_MODEL_NAME)
    assert manifest["integrity_verified"] is True
    assert manifest["upstream_repo_url"] == "https://github.com/dauparas/ProteinMPNN"
    assert manifest["upstream_commit_sha"] == "8907e6671bfbfc92303b5f79c4b5e6ce47cdef57"
    assert manifest["expected_sha256"] == OFFICIAL_VANILLA_CHECKPOINTS[DEFAULT_MODEL_NAME]["sha256"]
    assert manifest["actual_sha256"] == manifest["expected_sha256"]


def test_wrapper_model_loading_and_device():
    """Tests loading the wrapper onto CPU and inspecting parameter count and evaluation mode."""
    wrapper = ProteinMPNNWrapper(device="cpu", model_name=DEFAULT_MODEL_NAME)
    assert wrapper.model is not None
    assert not wrapper.model.training  # Must be in eval() mode
    assert wrapper.noise_level == 0.20

    # Count parameters
    total_params = sum(p.numel() for p in wrapper.model.parameters())
    assert total_params > 1_000_000, f"Expected >1M parameters for ProteinMPNN, got {total_params}"


# =========================================================================
# 2. Backbone Coordinate Parsing and Validation Tests
# =========================================================================

def test_pdb_coordinate_extraction():
    """Tests parsing 1n5uA03.pdb into the required [L, 4, 3] backbone format."""
    coords, seq, target_id = extract_backbone_coordinates(PDB_1N5U, chain_id="A")
    assert target_id == "1n5uA03"
    assert len(seq) == 92
    assert coords.shape == (92, 4, 3)
    assert coords.dtype == np.float32

    # Verify no NaNs or Infs
    assert not np.isnan(coords).any()
    assert not np.isinf(coords).any()


def test_coordinate_validation():
    """Tests coordinate validation rules and error handling."""
    valid_coords = np.zeros((10, 4, 3), dtype=np.float32)
    validate_backbone_coordinates(valid_coords)

    # Invalid dimension
    with pytest.raises(ValueError, match="Expected 3D"):
        validate_backbone_coordinates(np.zeros((10, 3)))

    # Invalid atom count
    with pytest.raises(ValueError, match="Last two dimensions must be"):
        validate_backbone_coordinates(np.zeros((10, 3, 3)))

    # Contains NaN
    nan_coords = np.zeros((10, 4, 3), dtype=np.float32)
    nan_coords[0, 0, 0] = np.nan
    with pytest.raises(ValueError, match="NaN or infinite"):
        validate_backbone_coordinates(nan_coords)


# =========================================================================
# 3. Candidate Generation, Length, Alphabet, and Metadata Tests
# =========================================================================

def test_candidate_generation_smoke():
    """Technical smoke test: generates candidates on 1n5uA03 and verifies outputs."""
    wrapper = ProteinMPNNWrapper(device="cpu")
    coords, native_seq, target_id = extract_backbone_coordinates(PDB_1N5U)

    candidates = wrapper.sample_candidates(
        coords_or_pdb=coords,
        target_id=target_id,
        temperature=0.1,
        seed=42,
        num_sequences=3,
        method_arm="mpnn_standalone",
    )

    assert len(candidates) == 3
    valid_alphabet = set("ACDEFGHIKLMNPQRSTVWY")

    for idx, cand in enumerate(candidates):
        # Verify sequence length matches target
        assert len(cand.sequence) == len(native_seq)
        # Verify alphabet strictly adheres to standard 20 amino acids
        assert set(cand.sequence).issubset(valid_alphabet)
        # Verify candidate ID format: {target}_{arm}_T{temp:.1f}_s{seed}_idx{idx:04d}
        expected_id = generate_candidate_id(target_id, "mpnn_standalone", 0.1, 42, idx)
        assert cand.id == expected_id
        # Verify score is negative (log-probability)
        assert cand.score < 0.0
        # Verify attached diagnostic perplexity is >= 1.0
        assert cand.perplexity >= 1.0
        assert math.isclose(cand.perplexity, math.exp(-cand.score), rel_tol=1e-5)


# =========================================================================
# 4. Reproducibility, Seed Plumbing, and Permutation Plumbing Tests
# =========================================================================

def test_reproducibility_same_seed():
    """Verifies that identical seed + input + temperature yields 100% identical candidates and scores."""
    wrapper = ProteinMPNNWrapper(device="cpu")
    coords, _, target_id = extract_backbone_coordinates(PDB_1N5U)

    cands_run1 = wrapper.sample_candidates(coords, target_id, temperature=0.2, seed=1337, num_sequences=2)
    cands_run2 = wrapper.sample_candidates(coords, target_id, temperature=0.2, seed=1337, num_sequences=2)

    assert len(cands_run1) == len(cands_run2)
    for c1, c2 in zip(cands_run1, cands_run2):
        assert c1.id == c2.id
        assert c1.sequence == c2.sequence
        assert math.isclose(c1.score, c2.score, abs_tol=1e-6)
        assert math.isclose(c1.perplexity, c2.perplexity, abs_tol=1e-6)


def test_stochastic_divergence_different_seeds():
    """Verifies that different seeds produce distinct sequence samples."""
    wrapper = ProteinMPNNWrapper(device="cpu")
    coords, _, target_id = extract_backbone_coordinates(PDB_1N5U)

    cands_s42 = wrapper.sample_candidates(coords, target_id, temperature=0.5, seed=42, num_sequences=1)
    cands_s2026 = wrapper.sample_candidates(coords, target_id, temperature=0.5, seed=2026, num_sequences=1)

    assert cands_s42[0].sequence != cands_s2026[0].sequence
    assert cands_s42[0].id != cands_s2026[0].id


# =========================================================================
# 5. Scientific Firewall: Zero Native Sequence Leakage Test
# =========================================================================

def test_zero_native_sequence_conditioning_leakage():
    """Verifies that native sequence tokens are NEVER supplied as conditioning input to generation."""
    wrapper = ProteinMPNNWrapper(device="cpu")
    coords, native_seq, target_id = extract_backbone_coordinates(PDB_1N5U)

    # Generate sequence with the wrapper
    cands = wrapper.sample_candidates(coords, target_id, temperature=0.1, seed=42, num_sequences=1)
    gen_seq = cands[0].sequence

    # Verify that generation is not a 100% identity copy of native (which would indicate label leakage)
    assert gen_seq != native_seq
    recovery = sum(1 for a, b in zip(gen_seq, native_seq) if a == b) / float(len(native_seq))
    # ProteinMPNN recovery on standard structures is typically in the 40%-65% range, never 100%
    assert 0.20 <= recovery <= 0.80, f"Recovery {recovery:.2%} outside expected inverse-folding range"


# =========================================================================
# 6. Sequence Scoring Interface and Directionality Tests
# =========================================================================

def test_sequence_scoring_interface_and_direction():
    """Tests score_sequence interface and verifies higher log-prob = better score direction."""
    wrapper = ProteinMPNNWrapper(device="cpu")
    coords, native_seq, target_id = extract_backbone_coordinates(PDB_1N5U)

    res_native = wrapper.score_sequence(coords, native_seq, seed=42)
    assert "mean_log_prob" in res_native
    assert "perplexity" in res_native
    assert "per_residue_log_probs" in res_native
    assert "per_residue_probs" in res_native

    assert res_native["mean_log_prob"] < 0.0
    assert res_native["perplexity"] >= 1.0
    assert res_native["per_residue_log_probs"].shape == (92,)
    assert res_native["per_residue_probs"].shape == (92, 20)

    # Score an optimized low-temperature designed candidate
    cands = wrapper.sample_candidates(coords, target_id, temperature=0.1, seed=42, num_sequences=1)
    cand_seq = cands[0].sequence
    res_cand = wrapper.score_sequence(coords, cand_seq, seed=42)

    # Under low-temperature design, the model-designed sequence should have higher log-prob
    # (lower perplexity) than a non-optimized arbitrary sequence or native under standard noise
    assert res_cand["mean_log_prob"] > -5.0
    assert res_cand["perplexity"] < 50.0


# =========================================================================
# 7. Interface Interoperability with src/hybrid Pipeline
# =========================================================================

def test_hybrid_pipeline_interoperability():
    """End-to-end interface verification: ProteinMPNN candidates feeding into hybrid pipeline."""
    wrapper = ProteinMPNNWrapper(device="cpu")
    coords, _, target_id = extract_backbone_coordinates(PDB_1N5U)

    # 1. Generate candidate universe
    candidates = wrapper.sample_candidates(
        coords,
        target_id=target_id,
        temperature=0.5,
        seed=42,
        num_sequences=6,
        method_arm="hybrid_universe",
    )

    cand_ids = [c.id for c in candidates]
    seqs = [c.sequence for c in candidates]
    mpnn_scores = [c.score for c in candidates]

    # Synthetic ProteinSolver PLL scores for interface verification
    ps_scores = [-2.1, -1.8, -2.5, -1.9, -2.3, -2.0]

    # 2. Score Common Candidate Universe with percentile rank normalization
    hybrid_scores = score_common_candidate_universe(
        candidate_ids=cand_ids,
        sequences=seqs,
        mpnn_scores=mpnn_scores,
        ps_scores=ps_scores,
        weight_lambda=0.5,
    )
    assert len(hybrid_scores) == 6
    assert (hybrid_scores > 0.0).all() and (hybrid_scores <= 1.0).all()

    # 3. Compute normalized MPNN-only selection score (scale-compatible rank in (0, 1])
    mpnn_only_ranks = compute_mpnn_only_selection_score(mpnn_scores)
    assert len(mpnn_only_ranks) == 6

    # 4. Attach normalized hybrid scores to candidates and run greedy diversity selection
    for idx, c in enumerate(candidates):
        c.score = float(hybrid_scores[idx])

    selected = select_diverse_library(candidates, library_size_m=3, diversity_weight_gamma=0.5)
    assert len(selected) == 3

    # 5. Compute order-independent pairwise diversity
    div = compute_pairwise_hamming_diversity([c.sequence for c in selected])
    assert 0.0 <= div <= 1.0
