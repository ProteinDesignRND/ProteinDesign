from typing import NamedTuple, Tuple
from Bio.PDB import PDBParser
from Bio.PDB.Polypeptide import is_aa
from Bio.SeqUtils import seq1
import numpy as np
from scipy.spatial.distance import cdist
import torch

AMINO_ACIDS = [
    "G", "V", "A", "L", "I", "C", "M", "F", "W", "P",
    "D", "E", "S", "T", "Y", "Q", "N", "K", "R", "H"
]
AMINO_ACID_TO_IDX = {aa: i for i, aa in enumerate(AMINO_ACIDS)}
MASK_TOKEN_IDX = 20


class ProteinStructureGraph(NamedTuple):
    sequence: str
    residue_indices: torch.LongTensor
    x: torch.LongTensor
    edge_index: torch.LongTensor
    edge_attr: torch.FloatTensor
    coords_ca: np.ndarray


def extract_protein_graph(pdb_path: str, chain_id: str = "A", r_cutoff: float = 12.0) -> ProteinStructureGraph:
    """Extracts sequence, contact graph, and normalized edge features from a PDB structure.

    Follows the exact normalization rules discovered from the original ProteinSolver source:
    - Distance cutoff: r_cutoff (default 12.0 Å between shortest heavy-atom contacts)
    - Normalized Cartesian distance: (d - 6.0) / 12.0
    - Normalized Sequence separation: (seq_dist - 0.0) / 68.1319
    """
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("target", pdb_path)

    # Resolve chain
    first_model = next(iter(structure))
    if chain_id not in first_model:
        # Fall back to first available chain if specified chain_id is absent
        chain = next(iter(first_model))
    else:
        chain = first_model[chain_id]

    residues = [res for res in chain if is_aa(res, standard=True)]
    assert len(residues) > 0, f"No standard amino acid residues found in chain {chain_id} of {pdb_path}"

    sequence = "".join(seq1(res.get_resname()) for res in residues)
    ca_coords = np.array([res["CA"].get_coord() for res in residues])

    # Extract all heavy (non-hydrogen) atom coordinates per residue
    heavy_coords = [
        np.array([atom.get_coord() for atom in res if atom.element != "H"])
        for res in residues
    ]

    row_indices = []
    col_indices = []
    distances = []

    num_residues = len(residues)
    for i in range(num_residues):
        for j in range(num_residues):
            if i == j:
                continue  # Self loops removed as per ProteinSolver implementation
            d = cdist(heavy_coords[i], heavy_coords[j]).min()
            if d < r_cutoff:
                row_indices.append(i)
                col_indices.append(j)
                distances.append(d)

    # Encode sequence to categorical integers (20 standard AAs, 20 for unknown)
    x = torch.tensor(
        [AMINO_ACID_TO_IDX.get(aa, MASK_TOKEN_IDX) for aa in sequence],
        dtype=torch.long
    )

    edge_index = torch.tensor([row_indices, col_indices], dtype=torch.long)

    # Apply exact normalization formulas from proteinsolver.datasets.protein
    edge_attr_cart = (torch.tensor(distances, dtype=torch.float).unsqueeze(1) - 6.0) / 12.0
    edge_attr_seq = ((edge_index[1] - edge_index[0]).to(torch.float).unsqueeze(1) - 0.0) / 68.1319
    edge_attr = torch.cat([edge_attr_cart, edge_attr_seq], dim=1)

    return ProteinStructureGraph(
        sequence=sequence,
        residue_indices=torch.arange(num_residues, dtype=torch.long),
        x=x,
        edge_index=edge_index,
        edge_attr=edge_attr,
        coords_ca=ca_coords,
    )
