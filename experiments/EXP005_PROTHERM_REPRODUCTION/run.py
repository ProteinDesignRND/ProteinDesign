# Experiment: EXP005_PROTHERM_REPRODUCTION
# Cell Systems 2020 Figure 2D (ProTherm Single-Point Mutation Stability Correlation)
# Classification: RECONSTRUCTION_FROM_PRESERVED_NOTEBOOK_STATISTICS & RAW_DATA_RECOMPUTED

import os
import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd
import scipy.stats as stats

SCRIPT_DIR = Path(__file__).resolve().parent
INPUT_DIR = SCRIPT_DIR / "input"
OUTPUT_DIR = SCRIPT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

def generate_svg_fig2d(df_stats, output_svg_path):
    svg_width = 850
    svg_height = 420
    
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" font-family="Arial, sans-serif">',
        f'<rect width="{svg_width}" height="{svg_height}" fill="#ffffff" />',
        f'<text x="{svg_width/2}" y="28" font-size="15" font-weight="bold" text-anchor="middle" fill="#111111">Cell Systems 2020 Figure 2D: ProTherm Mutation Stability Correlation (Spearman ρ)</text>',
    ]

    panels = [
        ("protherm (All)", "Figure 2D: All ProTherm Mutations (N=3,471)", 60, 390, "#1f77b4"),
        ("protherm (Core)", "Notebook 07 Exploratory: Restricted Core Subset", 460, 790, "#2ca02c"),
    ]

    for group, title, x_left, x_right, highlight_color in panels:
        df_group = df_stats[df_stats["group"] == group].reset_index(drop=True)
        panel_w = x_right - x_left
        y_top = 70
        y_bottom = 350
        
        svg.append(f'<text x="{x_left + panel_w/2}" y="{y_top - 15}" font-size="12" font-weight="bold" text-anchor="middle" fill="#222222">{title}</text>')
        svg.append(f'<line x1="{x_left + 140}" y1="{y_top}" x2="{x_left + 140}" y2="{y_bottom}" stroke="#888888" stroke-width="1.5" />')
        svg.append(f'<line x1="{x_left + 140}" y1="{y_bottom}" x2="{x_right}" y2="{y_bottom}" stroke="#888888" stroke-width="1.5" />')
        
        for tick in [0.0, 0.2, 0.4, 0.6]:
            tick_x = (x_left + 140) + (tick / 0.7) * (x_right - (x_left + 140))
            svg.append(f'<line x1="{tick_x}" y1="{y_top}" x2="{tick_x}" y2="{y_bottom}" stroke="#e0e0e0" stroke-width="1" stroke-dasharray="3,3" />')
            svg.append(f'<text x="{tick_x}" y="{y_bottom + 18}" font-size="10" text-anchor="middle" fill="#555555">{tick:.1f}</text>')
        
        svg.append(f'<text x="{x_left + 140 + (x_right - x_left - 140)/2}" y="{y_bottom + 38}" font-size="11" text-anchor="middle" fill="#333333">Spearman Correlation (ρ)</text>')

        n_bars = len(df_group)
        bar_height = 24
        spacing = (y_bottom - y_top - (n_bars * bar_height)) / (n_bars + 1)

        for i, row in df_group.iterrows():
            bar_y = y_top + spacing + i * (bar_height + spacing)
            corr = row["corr"]
            bar_w = max(0.0, (corr / 0.7) * (x_right - (x_left + 140)))
            fill = highlight_color if row["method"] == "ProteinSolver" else "#8c8c8c"
            
            svg.append(f'<text x="{x_left + 132}" y="{bar_y + 16}" font-size="10" text-anchor="end" fill="#222222">{row["method"]}</text>')
            svg.append(f'<rect x="{x_left + 140}" y="{bar_y}" width="{bar_w:.1f}" height="{bar_height}" fill="{fill}" rx="3" />')
            
            ci_low_x = (x_left + 140) + (row["ci_lower"] / 0.7) * (x_right - (x_left + 140))
            ci_high_x = (x_left + 140) + (row["ci_upper"] / 0.7) * (x_right - (x_left + 140))
            mid_y = bar_y + bar_height / 2
            svg.append(f'<line x1="{ci_low_x:.1f}" y1="{mid_y}" x2="{ci_high_x:.1f}" y2="{mid_y}" stroke="#111111" stroke-width="1.5" />')
            svg.append(f'<line x1="{ci_low_x:.1f}" y1="{mid_y - 4}" x2="{ci_low_x:.1f}" y2="{mid_y + 4}" stroke="#111111" stroke-width="1.5" />')
            svg.append(f'<line x1="{ci_high_x:.1f}" y1="{mid_y - 4}" x2="{ci_high_x:.1f}" y2="{mid_y + 4}" stroke="#111111" stroke-width="1.5" />')
            svg.append(f'<text x="{ci_high_x + 6:.1f}" y="{mid_y + 4}" font-size="10" font-weight="bold" fill="#111111">ρ={corr:.3f}</text>')

    svg.append('</svg>')
    with open(output_svg_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(svg))
    print(f"Generated standalone SVG figure: {output_svg_path}")

def main():
    print("======================================================================")
    print("EXP005: ProTherm Mutation DeltaDeltaG Correlation Reproduction")
    print("Cell Systems 2020 Figure 2D / Upstream Notebook 07 Cell 11-16 & 70-74")
    print("======================================================================")

    # 1. Recompute Rosetta baseline from raw data in protherm_design_wt_RUE.csv
    csv_path = INPUT_DIR / "protherm_design_wt_RUE.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing input file: {csv_path}")
    
    df_rue = pd.read_csv(csv_path, index_col=0)
    print(f"Loaded raw ProTherm dataset: {len(df_rue)} mutations across {df_rue['filename'].nunique()} structures.")

    df_rue["filename_prefix"] = df_rue["filename"].str.split("-").str[0]
    filename_prefix_to_reu_wt = df_rue.groupby("filename_prefix")["RUE_wt"].mean().to_dict()
    df_rue["RUE_wt_2"] = df_rue["filename_prefix"].map(filename_prefix_to_reu_wt)
    df_rue["rosetta_reu_change"] = df_rue["RUE_mut"] - df_rue["RUE_wt_2"]

    # Original notebook formula: values_ref = ddg_exp, values = sign * feature (sign=-1 for Rosetta REU)
    val_ref = df_rue["ddg_exp"].values
    val_rosetta = -df_rue["rosetta_reu_change"].values

    sp_rosetta = stats.spearmanr(val_ref, val_rosetta)
    print(f"[RAW RECOMPUTATION] Rosetta REU change Spearman rho: {sp_rosetta.correlation:.6f}, p={sp_rosetta.pvalue:.4e}")

    # 10,000-bootstrap procedure from Notebook 07 Cell 11
    print("Running 10,000 bootstrap iterations for Rosetta REU confidence interval...")
    rng = np.random.default_rng(42)
    boot_corrs = []
    for _ in range(10000):
        idx = rng.choice(len(val_ref), len(val_ref), replace=True)
        boot_corrs.append(stats.spearmanr(val_ref[idx], val_rosetta[idx])[0])
    rosetta_ci_lower = float(np.quantile(boot_corrs, 0.05))
    rosetta_ci_upper = float(np.quantile(boot_corrs, 0.95))
    print(f"[RAW RECOMPUTATION] Rosetta REU 90% bootstrap CI: [{rosetta_ci_lower:.4f}, {rosetta_ci_upper:.4f}]")

    # 2. Reconstructed ProteinSolver score from preserved upstream notebook 07 Cell 72/74
    # The per-mutation raw network score (protherm_wresults.torch) was not bundled in the repo.
    # Therefore, this statistic is explicitly documented as reconstructed from preserved source output.
    protherm_all_ps_rho = 0.443801
    protherm_all_ps_pval = 1.783294e-167
    protherm_all_ps_ci = [0.418884, 0.467848]

    # Notebook 07 Cell 72 exploratory analysis (restricted core subset lacking close homologs)
    protherm_core_ps_rho = 0.551231
    protherm_core_ps_pval = 1.286834e-15
    protherm_core_ps_ci = [0.460245, 0.626613]

    print("\nPreserved Literature Statistics (Spearman rho):")
    print(f"  Figure 2D (All 3,471 mutations):        Spearman rho = {protherm_all_ps_rho:.3f} (p = {protherm_all_ps_pval:.2e}), 90% CI [{protherm_all_ps_ci[0]:.3f}, {protherm_all_ps_ci[1]:.3f}]")
    print(f"  Exploratory Core Subset (Notebook 07):  Spearman rho = {protherm_core_ps_rho:.3f} (p = {protherm_core_ps_pval:.2e}), 90% CI [{protherm_core_ps_ci[0]:.3f}, {protherm_core_ps_ci[1]:.3f}]")

    stats_summary = [
        {"group": "protherm (All)", "method": "ProteinSolver", "corr": protherm_all_ps_rho, "pvalue": protherm_all_ps_pval, "ci_lower": protherm_all_ps_ci[0], "ci_upper": protherm_all_ps_ci[1], "source": "preserved_notebook_stat"},
        {"group": "protherm (All)", "method": "Ingraham et al.", "corr": 0.423651, "pvalue": 5.097932e-147, "ci_lower": 0.398339, "ci_upper": 0.448537, "source": "preserved_notebook_stat"},
        {"group": "protherm (All)", "method": "Rosetta (score)", "corr": sp_rosetta.correlation, "pvalue": sp_rosetta.pvalue, "ci_lower": rosetta_ci_lower, "ci_upper": rosetta_ci_upper, "source": "raw_recomputed"},
        {"group": "protherm (All)", "method": "Rosetta (ddg_monomer)", "corr": 0.316684, "pvalue": 1.052233e-81, "ci_lower": 0.288679, "ci_upper": 0.343957, "source": "preserved_notebook_stat"},
        {"group": "protherm (All)", "method": "Rosetta (cartesian_ddg)", "corr": 0.591317, "pvalue": 0.0, "ci_lower": 0.569914, "ci_upper": 0.611849, "source": "preserved_notebook_stat"},
        {"group": "protherm (Core)", "method": "ProteinSolver", "corr": protherm_core_ps_rho, "pvalue": protherm_core_ps_pval, "ci_lower": protherm_core_ps_ci[0], "ci_upper": protherm_core_ps_ci[1], "source": "preserved_notebook_stat"},
        {"group": "protherm (Core)", "method": "Ingraham et al.", "corr": 0.402468, "pvalue": 2.338008e-08, "ci_lower": 0.292393, "ci_upper": 0.501931, "source": "preserved_notebook_stat"},
        {"group": "protherm (Core)", "method": "Rosetta (score)", "corr": 0.426413, "pvalue": 2.654239e-09, "ci_lower": 0.314821, "ci_upper": 0.526722, "source": "preserved_notebook_stat"},
        {"group": "protherm (Core)", "method": "Rosetta (ddg_monomer)", "corr": 0.334282, "pvalue": 4.800736e-06, "ci_lower": 0.210696, "ci_upper": 0.450418, "source": "preserved_notebook_stat"},
        {"group": "protherm (Core)", "method": "Rosetta (cartesian_ddg)", "corr": 0.463448, "pvalue": 6.447494e-11, "ci_lower": 0.351755, "ci_upper": 0.562951, "source": "preserved_notebook_stat"},
    ]
    df_stats = pd.DataFrame(stats_summary)
    stats_csv_path = OUTPUT_DIR / "protherm_reproduced_stats.csv"
    df_stats.to_csv(stats_csv_path, index=False)
    print(f"\nSaved reproduced stats to: {stats_csv_path}")

    svg_path = OUTPUT_DIR / "fig2d_protherm_reproduction.svg"
    generate_svg_fig2d(df_stats, svg_path)

    metrics = {
        "experiment_id": "EXP005_PROTHERM_REPRODUCTION",
        "cell_systems_figure": "Figure 2D",
        "status": "RECONSTRUCTION_FROM_PRESERVED_NOTEBOOK_STATISTICS",
        "provenance_notes": {
            "rosetta_baseline": "RAW_DATA_RECOMPUTED (10,000 bootstrap iterations from local protherm_design_wt_RUE.csv)",
            "proteinsolver_score": "PRESERVED_NOTEBOOK_STATISTIC (from upstream 07_protein_analysis_figures.ipynb Cell 72; raw per-mutation network scores protherm_wresults.torch are absent from git)",
            "correlation_type": "Spearman rank correlation (rho), NOT Pearson R",
            "figure_mapping_clarification": "Cell Systems Figure 2D is the ProTherm panel (rho=0.444). The rho=0.551 core subset is an internal exploratory analysis from Notebook 07 Cell 72, NOT Figure 2E."
        },
        "recomputed_rosetta_metrics": {
            "spearman_rho": float(sp_rosetta.correlation),
            "pvalue": float(sp_rosetta.pvalue),
            "bootstrap_ci90": [rosetta_ci_lower, rosetta_ci_upper],
        },
        "preserved_proteinsolver_metrics": {
            "all_mutations_spearman_rho": protherm_all_ps_rho,
            "all_mutations_pvalue": protherm_all_ps_pval,
            "all_mutations_ci90": protherm_all_ps_ci,
            "core_subset_spearman_rho": protherm_core_ps_rho,
            "core_subset_pvalue": protherm_core_ps_pval,
            "core_subset_ci90": protherm_core_ps_ci,
        }
    }
    metrics_path = SCRIPT_DIR / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved metrics to: {metrics_path}")
    print("EXP005 completed successfully.")

if __name__ == "__main__":
    main()
