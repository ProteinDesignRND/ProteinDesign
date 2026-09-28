"""
Backbone coordinate parsing, extraction, and validation for ProteinMPNN.

ProteinMPNN requires 4 backbone heavy atoms per residue in standard order:
    Index 0: N   (Nitrogen)
    Index 1: CA  (Alpha Carbon)
    Index 2: C   (Carbonyl Carbon)
    Index 3: O   (Carbonyl Oxygen)

Tensor shape convention:
    Single structure: (L, 4, 3) where L is sequence length.
    Batch: (B, L, 4, 3) where B is batch size.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import torch
from Bio.PDB import PDBParser
from Bio.PDB.Polypeptide import is_aa
from Bio.SeqUtils import seq1

BACKBONE_ATOMS = ["N", "CA", "C", "O"]


def validate_backbone_coordinates(coords: Union[np.ndarray, torch.Tensor]) -> None:
    """Validates backbone coordinate tensor dimensions and numerical validity.

    Args:
        coords: Tensor or ndarray of shape (L, 4, 3) or (B, L, 4, 3).

    Raises:
        ValueError: If shape is invalid, contains NaNs, or sequence length is 0.
    """
    if isinstance(coords, torch.Tensor):
        shape = coords.shape
        has_nan = torch.isnan(coords).any().item()
        has_inf = torch.isinf(coords).any().item()
    elif isinstance(coords, np.ndarray):
        shape = coords.shape
        has_nan = np.isnan(coords).any()
        has_inf = np.isinf(coords).any()
    else:
        raise TypeError(f"Expected numpy.ndarray or torch.Tensor, got {type(coords)}")

    if len(shape) not in (3, 4):
        raise ValueError(
            f"Expected 3D (L, 4, 3) or 4D (B, L, 4, 3) coordinate tensor, got shape {shape}"
        )

    if shape[-2:] != (4, 3):
        raise ValueError(
            f"Last two dimensions must be (4, 3) corresponding to [N, CA, C, O] in 3D, got {shape[-2:]}"
        )

    seq_len = shape[-3]
    if seq_len == 0:
        raise ValueError("Sequence length L must be greater than 0.")

    if has_nan or has_inf:
        raise ValueError("Coordinates contain NaN or infinite values.")


def extract_backbone_coordinates(
    pdb_path: Union[str, Path],
    chain_id: Optional[str] = None,
) -> Tuple[np.ndarray, str, str]:
    """Extracts backbone coordinates, native sequence, and target ID from a PDB file.

    Args:
        pdb_path: Path to the PDB file.
        chain_id: Specific chain identifier (e.g. 'A'). If None, defaults to first chain.

    Returns:
        Tuple of:
            - coords: numpy.ndarray of shape (L, 4, 3), dtype float32.
            - native_sequence: String of 1-letter amino acid codes of length L.
            - target_id: Basename identifier without .pdb extension.

    Raises:
        FileNotFoundError: If pdb_path does not exist.
        ValueError: If no valid residues or backbone atoms are found.
    """
    path = Path(pdb_path)
    if not path.is_file():
        raise FileNotFoundError(f"PDB file not found at: {path}")

    target_id = path.stem
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure(target_id, str(path))

    # Resolve chain
    first_model = next(iter(structure))
    if chain_id is not None:
        if chain_id not in first_model:
            raise ValueError(f"Chain '{chain_id}' not found in PDB file {path}")
        chain = first_model[chain_id]
    else:
        chain = next(iter(first_model))
        chain_id = chain.id

    # Filter to standard amino acid residues
    residues = [res for res in chain if is_aa(res, standard=True)]
    if not residues:
        raise ValueError(f"No standard amino acid residues found in chain '{chain_id}' of {path}")

    # Verify all residues contain N, CA, C, O backbone atoms
    for res in residues:
        for atom in BACKBONE_ATOMS:
            if atom not in res:
                raise ValueError(
                    f"Residue {res.get_resname()}{res.id[1]} in chain '{chain_id}' missing backbone atom '{atom}'"
                )

    seq = "".join(seq1(res.get_resname()) for res in residues)
    num_res = len(residues)
    coords = np.zeros((num_res, 4, 3), dtype=np.float32)

    for i, res in enumerate(residues):
        for j, atom in enumerate(BACKBONE_ATOMS):
            coords[i, j] = res[atom].get_coord()

    validate_backbone_coordinates(coords)
    return coords, seq, target_id


def coords_to_proteinmpnn_batch(
    coords: Union[np.ndarray, torch.Tensor],
    target_id: str = "target",
    chain_id: str = "A",
) -> List[Dict[str, Any]]:
    """Converts a coordinate array into the batch dictionary format expected by ProteinMPNN.

    Args:
        coords: Backbone coordinates of shape (L, 4, 3).
        target_id: Target identifier string.
        chain_id: Chain label string (default 'A').

    Returns:
        List containing a single dictionary formatted for tied_featurize.
    """
    validate_backbone_coordinates(coords)

    if isinstance(coords, torch.Tensor):
        coords_np = coords.detach().cpu().numpy()
    else:
        coords_np = coords

    if coords_np.ndim == 4:
        # If batch dimension given with B=1, squeeze to 3D
        if coords_np.shape[0] != 1:
            raise ValueError("Only single-target coordinate tensors (shape (L, 4, 3)) are currently converted.")
        coords_np = coords_np[0]

    seq_len = coords_np.shape[0]
    dummy_seq = "A" * seq_len

    coords_dict = {
        f"N_chain_{chain_id}": coords_np[:, 0, :].tolist(),
        f"CA_chain_{chain_id}": coords_np[:, 1, :].tolist(),
        f"C_chain_{chain_id}": coords_np[:, 2, :].tolist(),
        f"O_chain_{chain_id}": coords_np[:, 3, :].tolist(),
    }

    entry = {
        "name": target_id,
        "num_of_chains": 1,
        "seq": dummy_seq,
        f"seq_chain_{chain_id}": dummy_seq,
        f"coords_chain_{chain_id}": coords_dict,
    }

    return [entry]
