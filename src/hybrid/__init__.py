"""
Hybrid scoring and candidate selection package for Protein Design.

Provides:
- Scale-free within-pool percentile rank hybrid scoring (Primary Method).
- Exploratory logit interpolation ablation (Exploratory Ablation).
- Two-stage candidate selection (Hard Viability Gate -> Diversity-Aware Selection).
- Order-independent set diversity metrics.
- Fixed-correspondence self-consistency TM-score.
- Biophysical heuristic proxies (Net charge at pH 7.4, Hydrophobic core fraction).
"""

from .scoring import (
    compute_percentile_ranks,
    compute_primary_hybrid_score,
    compute_exploratory_logit_hybrid,
)
from .selection import (
    Candidate,
    filter_viable_candidates,
    select_diverse_library,
    compute_pairwise_hamming_diversity,
    compute_fixed_correspondence_sctm,
    compute_net_charge_at_ph74,
    compute_hydrophobic_core_fraction,
)

__all__ = [
    "compute_percentile_ranks",
    "compute_primary_hybrid_score",
    "compute_exploratory_logit_hybrid",
    "Candidate",
    "filter_viable_candidates",
    "select_diverse_library",
    "compute_pairwise_hamming_diversity",
    "compute_fixed_correspondence_sctm",
    "compute_net_charge_at_ph74",
    "compute_hydrophobic_core_fraction",
]
