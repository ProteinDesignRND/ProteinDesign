"""
Cleanroom wrapper for the official ProteinMPNN implementation (Dauparas et al. 2022).

Integrates the official ProteinMPNN model with the Protein Design project architecture:
- Explicit model loading with SHA-256 verification and device management.
- Zero-leakage backbone coordinate featurization (no native sequence conditioning).
- Deterministic candidate generation compliant with project temperature & seed allocation.
- Sequence-level autoregressive log-probability scoring ($S_{MPNN}(u)$).
- Diagnostic autoregressive perplexity calculation ($PPL_{MPNN}(u)$).
- Production of Candidate records directly interoperable with src/hybrid.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import math
import sys
import numpy as np
import torch
import torch.nn.functional as F

from src.hybrid.budget import generate_candidate_id
from src.hybrid.selection import Candidate
from .coords import (
    coords_to_proteinmpnn_batch,
    extract_backbone_coordinates,
    validate_backbone_coordinates,
)
from .provenance import (
    DEFAULT_MODEL_NAME,
    OFFICIAL_VANILLA_CHECKPOINTS,
    get_proteinmpnn_provenance_manifest,
    verify_checkpoint_integrity,
)

ALPHABET = "ACDEFGHIKLMNPQRSTVWYX"
ALPHABET_DICT = {aa: i for i, aa in enumerate(ALPHABET)}


class ProteinMPNNWrapper:
    """Cleanroom wrapper around official ProteinMPNN neural network."""

    def __init__(
        self,
        checkpoint_path: Optional[Union[str, Path]] = None,
        model_name: str = DEFAULT_MODEL_NAME,
        device: Optional[str] = None,
        repo_root: Optional[Union[str, Path]] = None,
    ):
        """Initializes the ProteinMPNN model wrapper.

        Args:
            checkpoint_path: Explicit path to model weights .pt file. If None,
                resolves from official repository weights.
            model_name: Checkpoint key ('v_48_020', 'v_48_010', 'v_48_002', 'v_48_030').
            device: 'cuda', 'cpu', or None (auto-detect).
            repo_root: Path to workspace root. Defaults to auto-resolving.
        """
        if repo_root is None:
            self.repo_root = Path(__file__).resolve().parent.parent.parent
        else:
            self.repo_root = Path(repo_root)

        self.model_name = model_name

        # Resolve checkpoint path and verify integrity
        if checkpoint_path is None:
            verify_checkpoint_integrity(self.repo_root, model_name=model_name)
            relpath = OFFICIAL_VANILLA_CHECKPOINTS[model_name]["relpath"]
            self.checkpoint_path = self.repo_root / relpath
        else:
            self.checkpoint_path = Path(checkpoint_path)
            if not self.checkpoint_path.is_file():
                raise FileNotFoundError(f"Checkpoint file not found: {self.checkpoint_path}")

        # Resolve execution device
        if device is not None:
            self.device = torch.device(device)
        else:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Dynamically import official ProteinMPNN utilities from external/proteinmpnn
        external_dir = str(self.repo_root / "external" / "proteinmpnn")
        if external_dir not in sys.path:
            sys.path.insert(0, external_dir)

        try:
            from protein_mpnn_utils import (
                ProteinMPNN,
                tied_featurize,
                _scores,
                _S_to_seq,
            )
            self._ProteinMPNN_cls = ProteinMPNN
            self._tied_featurize_fn = tied_featurize
            self._scores_fn = _scores
            self._S_to_seq_fn = _S_to_seq
        except ImportError as exc:
            raise ImportError(
                f"Failed to import official ProteinMPNN from {external_dir}: {exc}"
            ) from exc

        # Load checkpoint and instantiate model
        self.checkpoint = torch.load(self.checkpoint_path, map_location=self.device)
        k_neighbors = self.checkpoint.get("num_edges", 48)
        self.noise_level = self.checkpoint.get("noise_level", 0.2)

        self.model = self._ProteinMPNN_cls(
            num_letters=21,
            node_features=128,
            edge_features=128,
            hidden_dim=128,
            num_encoder_layers=3,
            num_decoder_layers=3,
            augment_eps=0.0,  # Zero backbone noise for deterministic inference/scoring
            k_neighbors=k_neighbors,
        )
        self.model.to(self.device)
        self.model.load_state_dict(self.checkpoint["model_state_dict"])
        self.model.eval()

    def get_provenance(self) -> Dict[str, Any]:
        """Returns provenance and cryptographic integrity metadata for this wrapper."""
        return get_proteinmpnn_provenance_manifest(self.repo_root, self.model_name)

    def _prepare_tensors(
        self,
        coords_or_pdb: Union[str, Path, np.ndarray, torch.Tensor],
        chain_id: str = "A",
        target_id: Optional[str] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, int, str]:
        """Parses backbone coordinates and builds ProteinMPNN input tensors.

        Guarantees ZERO native sequence label leakage by creating blank sequence tokens.

        Returns:
            Tuple of (X, mask, chain_M, residue_idx, chain_encoding_all, seq_len, target_id)
        """
        if isinstance(coords_or_pdb, (str, Path)):
            coords, _, parsed_id = extract_backbone_coordinates(coords_or_pdb, chain_id=chain_id)
            if target_id is None:
                target_id = parsed_id
        else:
            coords = coords_or_pdb
            if target_id is None:
                target_id = "target"

        batch_dict = coords_to_proteinmpnn_batch(coords, target_id=target_id, chain_id=chain_id)

        # Call official tied_featurize
        res = self._tied_featurize_fn(batch_dict, self.device, chain_dict=None)
        X = res[0]
        # res[1] is S (derived from dummy seq), but we do not use native sequence
        mask = res[2]
        chain_M = res[4]
        chain_encoding_all = res[5]
        residue_idx = res[12]

        seq_len = int(mask.sum().item())
        return X, mask, chain_M, residue_idx, chain_encoding_all, seq_len, target_id

    @torch.no_grad()
    def sample_candidates(
        self,
        coords_or_pdb: Union[str, Path, np.ndarray, torch.Tensor],
        target_id: str,
        temperature: float = 0.1,
        seed: int = 42,
        num_sequences: int = 1,
        method_arm: str = "mpnn_standalone",
        chain_id: str = "A",
    ) -> List[Candidate]:
        """Samples sequence candidates for a target backbone under official ProteinMPNN.

        Adheres strictly to the frozen protocol:
        - PyTorch RNG is seeded with the exact pre-registered integer seed.
        - Residue decoding permutations are drawn under this RNG.
        - Zero native sequence information is supplied as conditioning input.
        - Sequence-level mean autoregressive log-probability ($S_{MPNN}$) is computed.
        - Candidate IDs are deterministically formatted via src.hybrid.budget.

        Args:
            coords_or_pdb: PDB file path or coordinate tensor [L, 4, 3].
            target_id: Target identifier (e.g. '1n5uA03').
            temperature: Sampling temperature (e.g. 0.1, 0.2, 0.5, 0.8, 1.0).
            seed: Integer random seed (e.g. 42, 1337, 2026).
            num_sequences: Number of sequences to generate under this seed.
            method_arm: Method arm name for candidate ID generation.
            chain_id: Chain label (default 'A').

        Returns:
            List of Candidate objects with deterministic IDs and raw scores.
        """
        if num_sequences <= 0:
            return []

        X, mask, chain_M, residue_idx, chain_encoding_all, seq_len, _ = self._prepare_tensors(
            coords_or_pdb, chain_id=chain_id, target_id=target_id
        )

        # Strict cleanroom guarantee: blank conditioning sequence
        S_blank = torch.zeros((1, seq_len), dtype=torch.long, device=self.device)
        chain_M_pos = torch.ones((1, seq_len), dtype=torch.int32, device=self.device)
        bias_by_res = torch.zeros((1, seq_len, 21), dtype=torch.float32, device=self.device)
        omit_AAs_np = np.zeros(21, dtype=np.float32)
        bias_AAs_np = np.zeros(21, dtype=np.float32)

        # Seed the random number generators deterministically
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        np.random.seed(seed)

        candidates: List[Candidate] = []

        for seq_idx in range(num_sequences):
            # Draw residue permutation random tensor under seeded PyTorch RNG
            randn = torch.randn(chain_M.shape, device=self.device)

            sample_dict = self.model.sample(
                X,
                randn,
                S_blank,
                chain_M,
                chain_encoding_all,
                residue_idx,
                mask=mask,
                temperature=temperature,
                omit_AAs_np=omit_AAs_np,
                bias_AAs_np=bias_AAs_np,
                chain_M_pos=chain_M_pos,
                bias_by_res=bias_by_res,
            )

            S_sample = sample_dict["S"]
            decoding_order = sample_dict["decoding_order"]

            # Compute exact autoregressive log-probabilities along the sampled decoding order
            log_probs = self.model(
                X,
                S_sample,
                mask,
                chain_M * chain_M_pos,
                residue_idx,
                chain_encoding_all,
                randn,
                use_input_decoding_order=True,
                decoding_order=decoding_order,
            )

            mask_for_loss = mask * chain_M * chain_M_pos
            nll_loss = self._scores_fn(S_sample, log_probs, mask_for_loss)
            mean_nll = float(nll_loss.cpu().item())
            mean_log_prob = -mean_nll

            seq_str = self._S_to_seq_fn(S_sample[0], chain_M[0])

            cand_id = generate_candidate_id(
                target_id=target_id,
                method_arm=method_arm,
                temperature=temperature,
                seed=seed,
                seq_idx=seq_idx,
            )

            cand = Candidate(
                id=cand_id,
                sequence=seq_str,
                target_id=target_id,
                score=mean_log_prob,
            )
            # Attach diagnostic perplexity as an extra attribute
            cand.perplexity = float(math.exp(mean_nll))
            candidates.append(cand)

        return candidates

    @torch.no_grad()
    def score_sequence(
        self,
        coords_or_pdb: Union[str, Path, np.ndarray, torch.Tensor],
        sequence: str,
        decoding_order: Optional[torch.Tensor] = None,
        seed: Optional[int] = 42,
        chain_id: str = "A",
    ) -> Dict[str, Any]:
        """Scores a specific amino acid sequence conditioned on a target backbone.

        Computes:
        - Mean autoregressive log-probability $S_{MPNN}(u)$ (higher is better, $\\le 0$).
        - Diagnostic autoregressive perplexity $PPL_{MPNN}(u) = \\exp(-S_{MPNN}(u)) \\ge 1.0$.
        - Per-residue log-probabilities and probabilities for downstream analyses.

        Args:
            coords_or_pdb: PDB file path or coordinate tensor [L, 4, 3].
            sequence: 1-letter amino acid sequence of length L.
            decoding_order: Specific decoding permutation tensor. If None, draws from seed.
            seed: Random seed for decoding permutation if decoding_order is None.
            chain_id: Chain label (default 'A').

        Returns:
            Dictionary containing:
                - 'mean_log_prob': float (higher is better)
                - 'perplexity': float (model diagnostic)
                - 'per_residue_log_probs': np.ndarray of shape [L]
                - 'per_residue_probs': np.ndarray of shape [L, 20]
                - 'decoding_order': torch.Tensor
        """
        X, mask, chain_M, residue_idx, chain_encoding_all, seq_len, _ = self._prepare_tensors(
            coords_or_pdb, chain_id=chain_id
        )

        if len(sequence) != seq_len:
            raise ValueError(
                f"Sequence length ({len(sequence)}) does not match backbone length ({seq_len})"
            )

        # Convert sequence characters to token indices
        token_indices = [ALPHABET_DICT.get(aa, 20) for aa in sequence]
        S = torch.tensor(token_indices, dtype=torch.long, device=self.device).unsqueeze(0)
        chain_M_pos = torch.ones((1, seq_len), dtype=torch.int32, device=self.device)

        if decoding_order is not None:
            use_input_order = True
            randn = torch.zeros(chain_M.shape, device=self.device)
            order_tensor = decoding_order.to(self.device)
        else:
            use_input_order = False
            order_tensor = None
            if seed is not None:
                torch.manual_seed(seed)
                if torch.cuda.is_available():
                    torch.cuda.manual_seed_all(seed)
            randn = torch.randn(chain_M.shape, device=self.device)

        log_probs = self.model(
            X,
            S,
            mask,
            chain_M * chain_M_pos,
            residue_idx,
            chain_encoding_all,
            randn,
            use_input_decoding_order=use_input_order,
            decoding_order=order_tensor,
        )

        mask_for_loss = mask * chain_M * chain_M_pos
        nll_loss = self._scores_fn(S, log_probs, mask_for_loss)
        mean_nll = float(nll_loss.cpu().item())
        mean_log_prob = -mean_nll
        perplexity = float(math.exp(mean_nll))

        # Per-residue log probabilities
        criterion = torch.nn.NLLLoss(reduction="none")
        per_res_nll = criterion(
            log_probs.contiguous().view(-1, log_probs.size(-1)),
            S.contiguous().view(-1),
        ).view(S.size())
        per_res_log_prob = (-per_res_nll[0] * mask[0]).cpu().numpy()

        # Per-residue amino acid probabilities (standard 20 AAs)
        per_res_probs = torch.exp(log_probs[0, :, :20]).cpu().numpy()

        return {
            "mean_log_prob": mean_log_prob,
            "perplexity": perplexity,
            "per_residue_log_probs": per_res_log_prob,
            "per_residue_probs": per_res_probs,
            "decoding_order": order_tensor if order_tensor is not None else randn,
        }

    def score_candidates(
        self,
        coords_or_pdb: Union[str, Path, np.ndarray, torch.Tensor],
        candidates: Sequence[Candidate],
        seed: Optional[int] = 42,
        chain_id: str = "A",
    ) -> List[Candidate]:
        """Rescores a sequence of Candidates, populating each Candidate's score.

        Args:
            coords_or_pdb: Target backbone coordinates or PDB file.
            candidates: Sequence of Candidate objects.
            seed: Seed for autoregressive decoding order during rescoring.
            chain_id: Target chain.

        Returns:
            List of Candidates with updated scores.
        """
        rescored = []
        for cand in candidates:
            res = self.score_sequence(
                coords_or_pdb=coords_or_pdb,
                sequence=cand.sequence,
                seed=seed,
                chain_id=chain_id,
            )
            updated_cand = Candidate(
                id=cand.id,
                sequence=cand.sequence,
                target_id=cand.target_id,
                score=res["mean_log_prob"],
                scrmsd_screen=cand.scrmsd_screen,
                plddt_screen=cand.plddt_screen,
                scrmsd_val=cand.scrmsd_val,
                plddt_val=cand.plddt_val,
                sctm_val=cand.sctm_val,
            )
            updated_cand.perplexity = res["perplexity"]
            rescored.append(updated_cand)
        return rescored


def load_protein_mpnn_model(
    model_name: str = DEFAULT_MODEL_NAME,
    device: Optional[str] = None,
    checkpoint_path: Optional[Union[str, Path]] = None,
) -> ProteinMPNNWrapper:
    """Convenience factory function to load the official ProteinMPNN wrapper."""
    return ProteinMPNNWrapper(
        checkpoint_path=checkpoint_path,
        model_name=model_name,
        device=device,
    )
