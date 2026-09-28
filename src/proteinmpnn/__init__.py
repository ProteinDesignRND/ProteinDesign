"""
ProteinMPNN Cleanroom Integration Package.

Exports:
- ProteinMPNNWrapper: Core model wrapper for generation and scoring.
- load_protein_mpnn_model: Factory function for loading wrapper.
- extract_backbone_coordinates: PDB parser for 4-atom backbone extraction.
- validate_backbone_coordinates: Coordinate tensor validator.
- get_proteinmpnn_provenance_manifest: Provenance and integrity dictionary.
- verify_checkpoint_integrity: Cryptographic hash verifier.
"""

from .coords import (
    extract_backbone_coordinates,
    validate_backbone_coordinates,
    coords_to_proteinmpnn_batch,
    BACKBONE_ATOMS,
)
from .provenance import (
    DEFAULT_MODEL_NAME,
    OFFICIAL_VANILLA_CHECKPOINTS,
    get_proteinmpnn_provenance_manifest,
    verify_checkpoint_integrity,
)
from .wrapper import (
    ProteinMPNNWrapper,
    load_protein_mpnn_model,
    ALPHABET,
    ALPHABET_DICT,
)

__all__ = [
    "ProteinMPNNWrapper",
    "load_protein_mpnn_model",
    "extract_backbone_coordinates",
    "validate_backbone_coordinates",
    "coords_to_proteinmpnn_batch",
    "BACKBONE_ATOMS",
    "DEFAULT_MODEL_NAME",
    "OFFICIAL_VANILLA_CHECKPOINTS",
    "get_proteinmpnn_provenance_manifest",
    "verify_checkpoint_integrity",
    "ALPHABET",
    "ALPHABET_DICT",
]
