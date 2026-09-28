"""
Official ProteinMPNN source and provenance metadata.

Records:
- Upstream canonical repository
- Exact commit SHA
- Checkpoint weights and cryptographic hashes (SHA-256)
- Model licenses and publication references
"""

from pathlib import Path
from typing import Dict, Any, Optional
import hashlib

UPSTREAM_REPO_URL = "https://github.com/dauparas/ProteinMPNN"
UPSTREAM_COMMIT_SHA = "8907e6671bfbfc92303b5f79c4b5e6ce47cdef57"
UPSTREAM_COMMIT_DATE = "2023-06-27"
INTEGRATION_DATE = "2026-09-28"
LICENSE = "MIT License (Copyright (c) 2022 Justas Dauparas)"
CANONICAL_CITATION = "Dauparas et al., Robust deep learning based protein sequence design using ProteinMPNN, Science 378, 49-56 (2022). DOI: 10.1126/science.add2187"

# Official vanilla model checkpoints and their verified SHA-256 hashes
OFFICIAL_VANILLA_CHECKPOINTS: Dict[str, Dict[str, Any]] = {
    "v_48_002": {
        "relpath": "external/proteinmpnn/vanilla_model_weights/v_48_002.pt",
        "sha256": "925F2CA1007BF9B02E0E7F420FF00EB91F50FCC2722F64B42E644AE95ADAA131",
        "noise_level": 0.02,
        "k_neighbors": 48,
        "description": "Vanilla ProteinMPNN trained with 0.02 Å backbone noise",
    },
    "v_48_010": {
        "relpath": "external/proteinmpnn/vanilla_model_weights/v_48_010.pt",
        "sha256": "DB866FAE956A28661F926053D630610C55E9FC4BC03922F2AEEB98A37435CCCE",
        "noise_level": 0.10,
        "k_neighbors": 48,
        "description": "Vanilla ProteinMPNN trained with 0.10 Å backbone noise",
    },
    "v_48_020": {
        "relpath": "external/proteinmpnn/vanilla_model_weights/v_48_020.pt",
        "sha256": "C9CB4A671D79604111231F8DBFC7C590E06F1197453B7A6854AC6661A642F5BD",
        "noise_level": 0.20,
        "k_neighbors": 48,
        "description": "Vanilla ProteinMPNN standard baseline trained with 0.20 Å backbone noise (Official Default)",
    },
    "v_48_030": {
        "relpath": "external/proteinmpnn/vanilla_model_weights/v_48_030.pt",
        "sha256": "C34B7BFB38418EA30989FDA3314F4781AC4E3920F9825731CF555F1FED44AC66",
        "noise_level": 0.30,
        "k_neighbors": 48,
        "description": "Vanilla ProteinMPNN trained with 0.30 Å backbone noise",
    },
}

DEFAULT_MODEL_NAME = "v_48_020"


def compute_sha256(file_path: Path) -> str:
    """Computes SHA-256 hash in uppercase hex for a given file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().upper()


def verify_checkpoint_integrity(
    repo_root: Optional[Path] = None,
    model_name: str = DEFAULT_MODEL_NAME,
) -> bool:
    """Verifies that the specified official checkpoint exists and matches its expected SHA-256 hash.

    Args:
        repo_root: Path to the repository root. Defaults to finding it from file location.
        model_name: Checkpoint key ('v_48_002', 'v_48_010', 'v_48_020', 'v_48_030').

    Returns:
        True if checkpoint exists and SHA-256 matches.

    Raises:
        ValueError: If model_name is not recognized.
        FileNotFoundError: If the checkpoint file is missing.
        RuntimeError: If SHA-256 does not match.
    """
    if model_name not in OFFICIAL_VANILLA_CHECKPOINTS:
        raise ValueError(
            f"Unknown model_name: {model_name}. Allowed: {list(OFFICIAL_VANILLA_CHECKPOINTS.keys())}"
        )

    if repo_root is None:
        # Default to 2 directories up from src/proteinmpnn/
        repo_root = Path(__file__).resolve().parent.parent.parent

    entry = OFFICIAL_VANILLA_CHECKPOINTS[model_name]
    ckpt_path = repo_root / entry["relpath"]

    if not ckpt_path.is_file():
        raise FileNotFoundError(f"ProteinMPNN checkpoint not found at: {ckpt_path}")

    actual_hash = compute_sha256(ckpt_path)
    expected_hash = entry["sha256"]

    if actual_hash != expected_hash:
        raise RuntimeError(
            f"Checkpoint SHA-256 mismatch for {model_name}!\n"
            f"  Expected: {expected_hash}\n"
            f"  Actual:   {actual_hash}"
        )

    return True


def get_proteinmpnn_provenance_manifest(
    repo_root: Optional[Path] = None,
    model_name: str = DEFAULT_MODEL_NAME,
) -> Dict[str, Any]:
    """Returns a dictionary manifest with complete provenance and integrity status."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parent.parent.parent

    entry = OFFICIAL_VANILLA_CHECKPOINTS.get(model_name, {})
    ckpt_path = repo_root / entry.get("relpath", "")
    exists = ckpt_path.is_file()
    actual_hash = compute_sha256(ckpt_path) if exists else None
    matches = actual_hash == entry.get("sha256") if exists else False

    return {
        "upstream_repo_url": UPSTREAM_REPO_URL,
        "upstream_commit_sha": UPSTREAM_COMMIT_SHA,
        "upstream_commit_date": UPSTREAM_COMMIT_DATE,
        "integration_date": INTEGRATION_DATE,
        "license": LICENSE,
        "citation": CANONICAL_CITATION,
        "model_name": model_name,
        "checkpoint_relpath": entry.get("relpath"),
        "expected_sha256": entry.get("sha256"),
        "actual_sha256": actual_hash,
        "integrity_verified": matches,
        "noise_level": entry.get("noise_level"),
        "k_neighbors": entry.get("k_neighbors"),
    }
