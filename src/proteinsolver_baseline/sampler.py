import random
from typing import Dict, List, Optional, Tuple
import numpy as np
import torch
import torch.nn.functional as F

from .graph import AMINO_ACIDS, AMINO_ACID_TO_IDX, MASK_TOKEN_IDX


def decode_indices_to_seq(indices: torch.Tensor) -> str:
    """Converts a 1D tensor of amino acid indices into a single-letter string."""
    indices_list = indices.cpu().tolist()
    return "".join(AMINO_ACIDS[idx] if idx < 20 else "-" for idx in indices_list)


@torch.no_grad()
def score_sequence_pll(
    net: torch.nn.Module,
    x: torch.Tensor,
    edge_index: torch.Tensor,
    edge_attr: torch.Tensor,
    device: str = "cpu",
) -> Tuple[float, float, torch.Tensor]:
    """Computes Pseudo-Log-Likelihood (PLL) by masking one residue at a time (Strokach et al. scan_with_mask).
    
    For each position i, sets x[i] = MASK_TOKEN_IDX (20), performs a forward pass,
    and extracts log P(x_i | x_{backslash i}, Graph).

    Args:
        net: Pretrained ProteinSolver network.
        x: 1D tensor of amino acid indices (length L).
        edge_index: Graph edge indices [2, E].
        edge_attr: Normalized edge attributes [E, 2].
        device: Torch execution device.

    Returns:
        (mean_pll_log_prob, perplexity, per_residue_pll_log_probs)
    """
    net.eval()
    x_dev = x.to(device)
    edge_index_dev = edge_index.to(device)
    edge_attr_dev = edge_attr.to(device)
    seq_len = x_dev.size(0)

    per_res_pll = torch.zeros(seq_len, dtype=torch.float, device=device)
    for i in range(seq_len):
        target_aa = x_dev[i].item()
        if target_aa >= 20:
            continue
        x_masked = x_dev.clone()
        x_masked[i] = MASK_TOKEN_IDX
        logits = net(x_masked, edge_index_dev, edge_attr_dev)
        log_prob = F.log_softmax(logits[i], dim=-1)[target_aa]
        per_res_pll[i] = log_prob

    mean_log_prob = per_res_pll.mean().item()
    perplexity = torch.exp(-per_res_pll.mean()).item()
    return mean_log_prob, perplexity, per_res_pll.cpu()


@torch.no_grad()
def score_sequence_oneshot(
    net: torch.nn.Module,
    x: torch.Tensor,
    edge_index: torch.Tensor,
    edge_attr: torch.Tensor,
    device: str = "cpu",
) -> Tuple[float, float, torch.Tensor]:
    """Computes one-shot zero-context log-likelihood with ALL residues masked simultaneously P(x_i | Graph)."""
    net.eval()
    x_dev = x.to(device)
    edge_index_dev = edge_index.to(device)
    edge_attr_dev = edge_attr.to(device)
    seq_len = x_dev.size(0)

    x_all_masked = torch.full((seq_len,), MASK_TOKEN_IDX, dtype=torch.long, device=device)
    logits = net(x_all_masked, edge_index_dev, edge_attr_dev)
    log_probs = F.log_softmax(logits, dim=-1)

    valid_mask = x_dev < 20
    target_tokens = x_dev[valid_mask].unsqueeze(1)
    gathered_log_probs = log_probs[valid_mask].gather(1, target_tokens).squeeze(1)

    mean_log_prob = gathered_log_probs.mean().item()
    perplexity = torch.exp(-gathered_log_probs.mean()).item()
    return mean_log_prob, perplexity, gathered_log_probs.cpu()


# Alias score_sequence to score_sequence_pll for biologically sound evaluation
score_sequence = score_sequence_pll


@torch.no_grad()
def generate_sequence_csp(
    net: torch.nn.Module,
    edge_index: torch.Tensor,
    edge_attr: torch.Tensor,
    seq_len: int,
    strategy: str = "map",
    temperature: float = 1.0,
    random_position: bool = False,
    fixed_positions: Optional[Dict[int, int]] = None,
    seed: Optional[int] = None,
    device: str = "cpu",
) -> Tuple[str, torch.Tensor, float]:
    """Designs a novel sequence for a target structure using iterative CSP masked inference.

    Args:
        net: Pretrained ProteinSolver model.
        edge_index: Graph connectivity [2, E].
        edge_attr: Edge features [E, 2].
        seq_len: Total length of the protein backbone.
        strategy: 'map' (greedy argmax) or 'multinomial' (stochastic sampling).
        temperature: Sampling temperature for multinomial selection.
        random_position: If True, selects random unassigned position; if False, selects most confident.
        fixed_positions: Dictionary mapping residue index -> amino acid index to keep fixed.
        seed: Random seed for exact determinism.
        device: Execution device.

    Returns:
        (designed_sequence_string, residue_indices_tensor, mean_confidence)
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)

    net.eval()
    edge_index_dev = edge_index.to(device)
    edge_attr_dev = edge_attr.to(device)

    # Initialize all positions as MASK (index 20)
    x = torch.full((seq_len,), MASK_TOKEN_IDX, dtype=torch.long, device=device)
    x_probas = torch.zeros(seq_len, dtype=torch.float, device=device)

    unassigned = set(range(seq_len))

    # Apply any fixed anchor positions
    if fixed_positions:
        for pos, aa_idx in fixed_positions.items():
            assert 0 <= pos < seq_len
            x[pos] = aa_idx
            x_probas[pos] = 1.0
            unassigned.remove(pos)

    # Iterative CSP filling loop
    while unassigned:
        logits = net(x, edge_index_dev, edge_attr_dev)
        scaled_logits = logits / max(temperature, 1e-4)
        probs = F.softmax(scaled_logits, dim=-1)

        unassigned_list = sorted(list(unassigned))
        unassigned_probs = probs[unassigned_list]

        max_p_per_unassigned, argmax_aa_per_unassigned = unassigned_probs.max(dim=-1)

        if random_position:
            chosen_sub_idx = random.randint(0, len(unassigned_list) - 1)
        else:
            # Pick position where the network is most confident
            chosen_sub_idx = max_p_per_unassigned.argmax().item()

        target_pos = unassigned_list[chosen_sub_idx]
        pos_probs = unassigned_probs[chosen_sub_idx]

        if strategy == "map":
            chosen_aa = argmax_aa_per_unassigned[chosen_sub_idx].item()
            chosen_prob = max_p_per_unassigned[chosen_sub_idx].item()
        elif strategy == "multinomial":
            chosen_aa = torch.multinomial(pos_probs, num_samples=1).item()
            chosen_prob = pos_probs[chosen_aa].item()
        else:
            raise ValueError(f"Unknown strategy: {strategy}. Choose 'map' or 'multinomial'.")

        x[target_pos] = chosen_aa
        x_probas[target_pos] = chosen_prob
        unassigned.remove(target_pos)

    designed_seq = decode_indices_to_seq(x)
    mean_confidence = x_probas.mean().item()

    return designed_seq, x.cpu(), mean_confidence
