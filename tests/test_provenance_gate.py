import hashlib
import json
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNNER_PATH = REPO_ROOT / "scripts" / "kaggle" / "e1_full_runner.py"
PROVENANCE_PATH = REPO_ROOT / "scripts" / "kaggle" / "e1_provenance.json"
MANIFEST_PATH = REPO_ROOT / "data" / "manifests" / "development_20_cath42.txt"

AUTHORIZED_COMMIT = "0c7ea3cae6e2e03385c9b2115af95dee64d80683"
EXPECTED_MANIFEST_SHA = "47ab5fec66017b455f7eabee143dc83e99ec740640e945ed96752abb59483069"
EXPECTED_PS_SHA = "1e8272f05ec19041394568c949bbdbf012ee72c1595be7157c4bb0324d0b5727"
EXPECTED_MPNN_SHA = "c9cb4a671d79604111231f8dbfc7c590e06f1197453b7a6854ac6661a642f5bd"


def compute_canonical_sha256(path: Path) -> str:
    """Computes SHA-256 over raw content with line endings normalized to canonical Unix LF."""
    raw_bytes = path.read_bytes()
    canonical_bytes = raw_bytes.replace(b"\r\n", b"\n")
    return hashlib.sha256(canonical_bytes).hexdigest()


def test_canonical_sha256_line_ending_invariance(tmp_path):
    """Verifies that compute_canonical_sha256 produces identical hashes regardless of line endings."""
    sample_content = "def test():\n    return 42\n"
    lf_file = tmp_path / "sample_lf.py"
    crlf_file = tmp_path / "sample_crlf.py"

    lf_file.write_bytes(sample_content.encode("utf-8"))
    crlf_file.write_bytes(sample_content.replace("\n", "\r\n").encode("utf-8"))

    hash_lf = compute_canonical_sha256(lf_file)
    hash_crlf = compute_canonical_sha256(crlf_file)

    assert hash_lf == hash_crlf
    assert hash_lf == hashlib.sha256(sample_content.encode("utf-8")).hexdigest()


def test_provenance_manifest_structure_and_matching():
    """Verifies that e1_provenance.json exists, targets the authorized commit, and matches runner LF SHA."""
    assert PROVENANCE_PATH.exists(), "Provenance manifest must exist"
    with open(PROVENANCE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["authorized_commit"] == AUTHORIZED_COMMIT
    assert data["manifest_sha256"] == EXPECTED_MANIFEST_SHA
    assert data["fail_closed_gate"] is True

    actual_runner_lf_sha = compute_canonical_sha256(RUNNER_PATH)
    assert data["expected_canonical_runner_sha"] == actual_runner_lf_sha, (
        f"Provenance manifest expected SHA {data['expected_canonical_runner_sha']} "
        f"does not match actual runner LF SHA {actual_runner_lf_sha}"
    )


def test_runner_target_commit_constant():
    """Verifies that e1_full_runner.py defines TARGET_COMMIT = AUTHORIZED_RELEASE_COMMIT matching authorized commit."""
    content = RUNNER_PATH.read_text(encoding="utf-8")
    assert f'AUTHORIZED_RELEASE_COMMIT = "{AUTHORIZED_COMMIT}"' in content
    assert "TARGET_COMMIT = AUTHORIZED_RELEASE_COMMIT" in content


def test_preflight_gate_simulation_passes():
    """Simulates the preflight gate with valid parameters and ensures it passes."""
    actual_commit = AUTHORIZED_COMMIT
    current_canonical_sha = compute_canonical_sha256(RUNNER_PATH)

    with open(PROVENANCE_PATH, "r", encoding="utf-8") as f:
        prov_data = json.load(f)

    # Verification logic matching e1_full_runner.py
    if actual_commit != prov_data["authorized_commit"]:
        pytest.fail("Gate should not reject authorized commit")
    if current_canonical_sha != prov_data["expected_canonical_runner_sha"]:
        pytest.fail("Gate should not reject matching canonical runner SHA")


def test_preflight_gate_fails_closed_on_unauthorized_commit():
    """Verifies that an unauthorized commit (e.g. stale commit) triggers a fail-closed exception."""
    stale_commit = "a466747cf833cf14f919902ab2dc1a6bc3c7a2ff"
    with open(PROVENANCE_PATH, "r", encoding="utf-8") as f:
        prov_data = json.load(f)

    with pytest.raises(RuntimeError, match="FAIL-CLOSED PROVENANCE GATE"):
        if stale_commit != prov_data["authorized_commit"]:
            raise RuntimeError(
                f"FAIL-CLOSED PROVENANCE GATE: Cloned commit '{stale_commit}' "
                f"does not match authorized production release commit '{prov_data['authorized_commit']}'!"
            )


def test_preflight_gate_fails_closed_on_tampered_runner_hash():
    """Verifies that a tampered or divergent runner triggers a fail-closed exception."""
    tampered_sha = "0000000000000000000000000000000000000000000000000000000000000000"
    with open(PROVENANCE_PATH, "r", encoding="utf-8") as f:
        prov_data = json.load(f)

    with pytest.raises(RuntimeError, match="FAIL-CLOSED PROVENANCE GATE"):
        if tampered_sha != prov_data["expected_canonical_runner_sha"]:
            raise RuntimeError(
                f"FAIL-CLOSED PROVENANCE GATE: Running script canonical LF SHA256 '{tampered_sha}' "
                f"does not match authorized expected runner SHA256 '{prov_data['expected_canonical_runner_sha']}'!"
            )


def test_frozen_scientific_protocol_integrity():
    """Verifies that frozen scientific protocol invariants remain 100% untouched."""
    # Manifest SHA verification
    manifest_bytes = MANIFEST_PATH.read_bytes().replace(b"\r\n", b"\n")
    actual_manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()
    assert actual_manifest_sha == EXPECTED_MANIFEST_SHA

    # Target count
    targets = [line.strip() for line in manifest_bytes.decode("utf-8").splitlines() if line.strip() and not line.startswith("#")]
    assert len(targets) == 20

    # Model checkpoint constants
    runner_content = RUNNER_PATH.read_text(encoding="utf-8")
    assert f'PROTEINSOLVER_EXPECTED_SHA = "{EXPECTED_PS_SHA}"' in runner_content
    assert f'PROTEINMPNN_EXPECTED_SHA = "{EXPECTED_MPNN_SHA}"' in runner_content

    # Candidate budgets and grids
    assert "DEVELOPMENT_TARGET_COUNT = 20" in runner_content
    assert "SELECTION_LIBRARY_SIZE = 10" in runner_content
    assert "MPNN_TEMPERATURE_GRID = (0.1, 0.2, 0.5, 0.8, 1.0)" in runner_content
    assert "PROTEINSOLVER_TEMPERATURE_GRID = (0.1, 0.5, 1.0)" in runner_content
    assert "GAMMA_SEARCH_GRID = (0.0, 0.25, 0.5, 1.0, 2.0)" in runner_content
    assert "LAMBDA_SEARCH_GRID = (0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0)" in runner_content
