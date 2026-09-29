"""
Statistical significance testing, effect size estimation, and bootstrap inference.

Authoritative Rules:
1. Primary Confirmatory Hypothesis Test:
   Two-sided paired Wilcoxon signed-rank test on target-level paired differences:
       d_t = mean_scTM_hybrid(t) - mean_scTM_MPNN_only(t)
   across the primary test set (N = 50 TS50 targets) at pre-registered significance level alpha = 0.01.

2. Exact Test Configuration (Frozen SciPy 1.17.1 Reference):
   - alternative = 'two-sided'
   - zero_method = 'wilcox' (discards zero differences from rank assignment)
   - correction = True (continuity correction enabled)
   - method = 'asymptotic' (normal/asymptotic approximation with continuity correction)

3. Numeric Validation:
   - All input paired differences must be finite real numbers. NaN or infinite values raise ValueError.
   - Requires at least N >= 2 paired observations.

4. Edge Cases:
   - If all d_t == 0: p-value = 1.0, Hodges-Lehmann median difference = 0.0, Cohen's d_z = 0.0.
   - If std(d_t) == 0 with non-zero d_t: Cohen's d_z = 0.0.

5. Bootstrap Confidence Intervals:
   - Derived strictly from 10,000 target-level paired resamples with fixed seed = 42.
   - Percentile method: 95% CI [2.5th, 97.5th percentiles] and 99% CI [0.5th, 99.5th percentiles].
   - Estimand: mean target-level paired difference Delta mean_scTM.
"""

from dataclasses import dataclass
from typing import Dict, Optional, Sequence, Tuple
import numpy as np
import scipy.stats as stats


@dataclass(frozen=True)
class WilcoxonResult:
    """Detailed result of the pre-registered paired Wilcoxon signed-rank test.

    Attributes:
        statistic: Wilcoxon test statistic (sum of ranks).
        pvalue: Two-sided p-value under the asymptotic normal approximation with continuity correction.
        hodges_lehmann: Hodges-Lehmann paired median difference estimator (median of pairwise Walsh averages).
        cohens_dz: Paired Cohen's d_z effect size (mean difference divided by sample standard deviation).
        n_total: Total number of input target-level pairs.
        n_non_zero: Number of non-zero paired differences included in rank assignment.
        method: Method used for p-value calculation ('asymptotic').
        zero_method: Zero difference handling convention ('wilcox').
        correction: Whether continuity correction was applied (True).
        alternative: Test alternative hypothesis ('two-sided').
    """
    statistic: float
    pvalue: float
    hodges_lehmann: float
    cohens_dz: float
    n_total: int
    n_non_zero: int
    method: str = "asymptotic"
    zero_method: str = "wilcox"
    correction: bool = True
    alternative: str = "two-sided"


def compute_hodges_lehmann_estimator(d_t: Sequence[float]) -> float:
    """Computes the Hodges-Lehmann paired median difference estimator.

    Formula:
        HL = median of all pairwise Walsh averages: (d_i + d_j) / 2 for 1 <= i <= j <= N.

    Args:
        d_t: Sequence of paired differences.

    Returns:
        Hodges-Lehmann estimator as float.
    """
    arr = np.asarray(d_t, dtype=np.float64)
    if len(arr) == 0:
        raise ValueError("Cannot compute Hodges-Lehmann estimator on empty sequence.")

    # Generate upper triangular indices including diagonal for Walsh averages
    n = len(arr)
    i_idx, j_idx = np.triu_indices(n)
    walsh_averages = (arr[i_idx] + arr[j_idx]) / 2.0
    return float(np.median(walsh_averages))


def compute_paired_wilcoxon_test(
    d_t: Sequence[float],
    alpha: float = 0.01,
) -> WilcoxonResult:
    """Executes the pre-registered two-sided paired Wilcoxon signed-rank test on target-level differences.

    Enforces the frozen protocol configuration:
        scipy.stats.wilcoxon(..., zero_method='wilcox', correction=True, alternative='two-sided', method='asymptotic')

    Args:
        d_t: Target-level paired differences d_t = scTM_hybrid(t) - scTM_MPNN_only(t).
        alpha: Pre-registered significance threshold (default 0.01).

    Returns:
        WilcoxonResult with test statistic, asymptotic p-value, HL estimator, and Cohen's d_z.

    Raises:
        ValueError: If d_t contains NaN/inf or has fewer than 2 observations.
    """
    arr = np.asarray(d_t, dtype=np.float64)

    # 1. Numeric validation: reject NaN or infinite values
    if not np.all(np.isfinite(arr)):
        raise ValueError("Input array contains NaN or infinite values; all differences must be finite numeric values.")

    n_total = len(arr)
    if n_total < 2:
        raise ValueError(
            f"Insufficient paired observations for Wilcoxon signed-rank test: expected N >= 2, got N={n_total}."
        )

    # 2. Non-zero count check under zero_method='wilcox'
    non_zeros = arr[arr != 0.0]
    n_non_zero = len(non_zeros)

    # 3. All-zeros edge case
    if n_non_zero == 0:
        return WilcoxonResult(
            statistic=0.0,
            pvalue=1.0,
            hodges_lehmann=0.0,
            cohens_dz=0.0,
            n_total=n_total,
            n_non_zero=0,
            method="asymptotic",
            zero_method="wilcox",
            correction=True,
            alternative="two-sided",
        )

    # 4. Standard execution with frozen parameters
    res = stats.wilcoxon(
        arr,
        zero_method="wilcox",
        correction=True,
        alternative="two-sided",
        method="asymptotic",
    )

    stat_val = float(res.statistic)
    pval = float(res.pvalue)

    # 5. Effect sizes
    hl = compute_hodges_lehmann_estimator(arr)

    mean_d = float(np.mean(arr))
    std_d = float(np.std(arr, ddof=1))
    cohens_dz = (mean_d / std_d) if std_d > 1e-9 else 0.0


    return WilcoxonResult(
        statistic=stat_val,
        pvalue=pval,
        hodges_lehmann=hl,
        cohens_dz=cohens_dz,
        n_total=n_total,
        n_non_zero=n_non_zero,
        method="asymptotic",
        zero_method="wilcox",
        correction=True,
        alternative="two-sided",
    )


def compute_paired_bootstrap_ci(
    d_t: Sequence[float],
    n_resamples: int = 10000,
    seed: int = 42,
    ci_levels: Tuple[float, ...] = (0.95, 0.99),
) -> Dict[float, Tuple[float, float]]:
    """Computes nonparametric target-level percentile bootstrap confidence intervals.

    Rules:
    - 10,000 target-level paired resamples with replacement.
    - Fixed RNG seed (default 42).
    - Percentile method.
    - Strictly bootstraps TARGET-LEVEL paired differences, NEVER individual candidates.

    Args:
        d_t: Target-level paired differences d_t.
        n_resamples: Number of bootstrap resamples (default 10,000).
        seed: Fixed random seed for reproducibility (default 42).
        ci_levels: Confidence levels to compute (default 95% and 99%).

    Returns:
        Mapping of confidence level -> (lower_bound, upper_bound).
    """
    arr = np.asarray(d_t, dtype=np.float64)
    if not np.all(np.isfinite(arr)):
        raise ValueError("Input array contains NaN or infinite values.")
    if len(arr) < 2:
        raise ValueError(f"Insufficient observations for bootstrap CI: expected N >= 2, got N={len(arr)}.")

    rng = np.random.default_rng(seed)
    n = len(arr)

    # Resample target-level differences
    resamples = rng.choice(arr, size=(n_resamples, n), replace=True)
    resample_means = np.mean(resamples, axis=1)

    ci_dict = {}
    for level in ci_levels:
        alpha = 1.0 - level
        lower_pct = 100.0 * (alpha / 2.0)
        upper_pct = 100.0 * (1.0 - alpha / 2.0)
        lower_val = float(np.percentile(resample_means, lower_pct))
        upper_val = float(np.percentile(resample_means, upper_pct))
        ci_dict[level] = (lower_val, upper_val)

    return ci_dict
