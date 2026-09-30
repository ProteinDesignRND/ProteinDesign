# Experiment: EXP007_BESTSEL_CD_REPRODUCTION
# Cell Systems 2020 Fig 4/5 Experimental Validation & STAR Protocols 2021 Step 19 BeStSel Analysis
# Classification: RECONSTRUCTION_FROM_PRESERVED_BESTSEL_OUTPUTS

import io
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

# Preserved secondary structure deconvolution fractions from author notebook
# 07_protein_analysis_bestsel.ipynb (Cells 15-24)
RAW_1N5U = """\
1.000 20.39 10.73 1.70 6.72 6.52 4.25 12.12 37.56 0.0127
2.000 19.07 10.58 0.88 3.88 10.88 2.69 14.23 37.79 0.0170
3.000 17.94 10.38 0.74 4.65 10.53 4.56 13.82 37.37 0.0157
4.000 19.00 11.65 0.00 6.79 7.64 4.44 12.91 37.57 0.0073
5.000 17.71 10.52 1.15 5.66 7.97 5.50 13.16 38.33 0.0135
6.000 19.43 11.34 0.00 6.32 9.06 4.22 12.76 36.87 0.0049
"""

RAW_4BEU = """\
1.000 10.26 5.83 6.48 12.25 9.75 4.28 12.72 38.42 0.0143
2.000 7.99 8.55 1.88 8.40 10.23 0.00 16.89 46.06 0.0150
"""

def parse_data(raw_str):
    df = pd.read_csv(
        io.StringIO(raw_str),
        sep=r"\s+",
        names="Factor Helix1 Helix2 Anti1 Anti2 Anti3 Para Turn Others NRMSD".split(),
    )
    data_cols = [c for c in df.columns if c not in ["Factor", "NRMSD"]]
    df[data_cols] = df[data_cols] / 100.0
    half = len(df) // 2
    df["Name"] = df["Factor"].apply(lambda f: "reference" if f <= half else "design")
    return df

def generate_svg_bestsel(summary_df, output_svg_path):
    svg_w = 750
    svg_h = 380

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}" font-family="Arial, sans-serif">',
        f'<rect width="{svg_w}" height="{svg_h}" fill="#ffffff" />',
        f'<text x="{svg_w/2}" y="26" font-size="14" font-weight="bold" text-anchor="middle" fill="#111111">CD Secondary Structure Deconvolution (BeStSel Preserved Outputs)</text>',
    ]

    elements = ["Helix1", "Helix2", "Anti1", "Anti2", "Anti3", "Para", "Turn"]
    palette = ["#3182bd", "#6baed6", "#31a354", "#74c476", "#a1d99b", "#e6550d", "#756bb1"]

    targets = [("1n5u", "Serum albumin (1n5u, N=3 replicates)", 80), ("4beu", "Alanine racemase (4beu, N=1 unreplicated)", 420)]
    panel_w = 260
    y_top = 70
    y_bottom = 290

    for target_key, target_title, x_left in targets:
        x_right = x_left + panel_w
        svg.append(f'<text x="{x_left + panel_w/2}" y="{y_top - 12}" font-size="11" font-weight="bold" text-anchor="middle" fill="#222222">{target_title}</text>')
        svg.append(f'<line x1="{x_left}" y1="{y_top}" x2="{x_left}" y2="{y_bottom}" stroke="#888888" stroke-width="1.2" />')
        svg.append(f'<line x1="{x_left}" y1="{y_bottom}" x2="{x_right}" y2="{y_bottom}" stroke="#888888" stroke-width="1.2" />')

        for tick in [0.0, 0.1, 0.2, 0.3, 0.4]:
            tick_y = y_bottom - (tick / 0.45) * (y_bottom - y_top)
            svg.append(f'<line x1="{x_left}" y1="{tick_y}" x2="{x_right}" y2="{tick_y}" stroke="#eeeeee" stroke-width="1" stroke-dasharray="2,2" />')
            svg.append(f'<text x="{x_left - 8}" y="{tick_y + 4}" font-size="9" text-anchor="end" fill="#555555">{int(tick*100)}%</text>')

        tg_df = summary_df[summary_df["target"] == target_key]
        x_bar_ref = x_left + 50
        x_bar_des = x_left + 150
        bar_w = 40

        cum_y_ref = y_bottom
        cum_y_des = y_bottom

        for elem_idx, elem in enumerate(elements):
            row = tg_df[tg_df["element"] == elem]
            if len(row) == 0:
                continue
            r_val = row.iloc[0]["ref_mean"]
            d_val = row.iloc[0]["des_mean"]
            color = palette[elem_idx]

            h_ref = (r_val / 0.45) * (y_bottom - y_top)
            cum_y_ref -= h_ref
            svg.append(f'<rect x="{x_bar_ref}" y="{cum_y_ref}" width="{bar_w}" height="{h_ref}" fill="{color}" stroke="#ffffff" stroke-width="0.5" />')

            h_des = (d_val / 0.45) * (y_bottom - y_top)
            cum_y_des -= h_des
            svg.append(f'<rect x="{x_bar_des}" y="{cum_y_des}" width="{bar_w}" height="{h_des}" fill="{color}" stroke="#ffffff" stroke-width="0.5" />')

        svg.append(f'<text x="{x_bar_ref + bar_w/2}" y="{y_bottom + 16}" font-size="9" text-anchor="middle" fill="#333333">Ref</text>')
        svg.append(f'<text x="{x_bar_des + bar_w/2}" y="{y_bottom + 16}" font-size="9" text-anchor="middle" fill="#333333">Design</text>')

    leg_x = 80
    leg_y = y_bottom + 45
    for idx, (elem, color) in enumerate(zip(elements, palette)):
        lx = leg_x + idx * 85
        svg.append(f'<rect x="{lx}" y="{leg_y}" width="10" height="10" fill="{color}" />')
        svg.append(f'<text x="{lx + 14}" y="{leg_y + 9}" font-size="8.5" fill="#333333">{elem}</text>')

    svg.append("</svg>")
    with open(output_svg_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Generated standalone SVG figure: {output_svg_path}")

def main():
    print("======================================================================")
    print("EXP007: BeStSel Secondary Structure Deconvolution Reconstruction")
    print("Classification: RECONSTRUCTION_FROM_PRESERVED_BESTSEL_OUTPUTS")
    print("Author Notebook 07 (Cells 15-24) / STAR Protocols Step 19")
    print("======================================================================")

    df_1n5u = parse_data(RAW_1N5U)
    df_4beu = parse_data(RAW_4BEU)
    print(f"Parsed 1n5u: {len(df_1n5u)} rows ({sum(df_1n5u['Name']=='reference')} ref, {sum(df_1n5u['Name']=='design')} des)")
    print(f"Parsed 4beu: {len(df_4beu)} rows ({sum(df_4beu['Name']=='reference')} ref, {sum(df_4beu['Name']=='design')} des)")

    elements = ["Helix1", "Helix2", "Anti1", "Anti2", "Anti3", "Para", "Turn", "Others"]
    summary_rows = []

    for target_name, df in [("1n5u", df_1n5u), ("4beu", df_4beu)]:
        ref_df = df[df["Name"] == "reference"]
        des_df = df[df["Name"] == "design"]

        for elem in elements:
            ref_vals = ref_df[elem].values
            des_vals = des_df[elem].values

            ref_mean = float(np.mean(ref_vals))
            ref_sem = float(stats.sem(ref_vals)) if len(ref_vals) > 1 else 0.0
            des_mean = float(np.mean(des_vals))
            des_sem = float(stats.sem(des_vals)) if len(des_vals) > 1 else 0.0

            if len(ref_vals) > 1 and len(des_vals) > 1:
                pval = float(stats.ttest_ind(ref_vals, des_vals).pvalue)
            else:
                pval = float("nan")

            summary_rows.append({
                "target": target_name,
                "element": elem,
                "ref_mean": ref_mean,
                "ref_sem": ref_sem,
                "des_mean": des_mean,
                "des_sem": des_sem,
                "delta_mean": abs(des_mean - ref_mean),
                "ttest_pvalue": pval,
            })

    summary_df = pd.DataFrame(summary_rows)
    csv_path = OUTPUT_DIR / "bestsel_secondary_structure_summary.csv"
    summary_df.to_csv(csv_path, index=False)
    print(f"Saved secondary structure deconvolution summary: {csv_path}")

    pvals_1n5u = [r["ttest_pvalue"] for r in summary_rows if r["target"] == "1n5u" and not np.isnan(r["ttest_pvalue"])]
    all_insignificant = all(p > 0.05 for p in pvals_1n5u)
    print(f"1n5u reference vs design t-test p-values (all > 0.05): {all_insignificant} (min p = {min(pvals_1n5u):.4f})")
    print("Scientific note: p > 0.05 indicates no statistically significant difference detected under tested conditions; it does NOT prove structural equivalence.")
    print("4beu has N=1 per group; two-sample t-test cannot be performed.")

    svg_path = OUTPUT_DIR / "bestsel_deconvolution_summary.svg"
    generate_svg_bestsel(summary_df, svg_path)

    metrics = {
        "experiment_id": "EXP007_BESTSEL_CD_REPRODUCTION",
        "status": "RECONSTRUCTION_FROM_PRESERVED_BESTSEL_OUTPUTS",
        "primary_provenance": "Author notebook 07_protein_analysis_bestsel.ipynb Cells 15-24; STAR Protocols 2021 Step 19 (BeStSel protocol).",
        "note_on_figure_attribution": "STAR Protocols Figure 2B depicts sequence logos without pairwise interactions, not BeStSel. BeStSel deconvolution supports protocol Step 19 and Cell Systems experimental validation.",
        "targets": ["1n5u", "4beu"],
        "elements_evaluated": elements,
        "n5u_total_alpha_helix_ref": float(df_1n5u[df_1n5u["Name"]=="reference"][["Helix1", "Helix2"]].sum(axis=1).mean()),
        "n5u_total_alpha_helix_des": float(df_1n5u[df_1n5u["Name"]=="design"][["Helix1", "Helix2"]].sum(axis=1).mean()),
        "beu4_total_beta_strand_ref": float(df_4beu[df_4beu["Name"]=="reference"][["Anti1", "Anti2", "Anti3", "Para"]].sum(axis=1).mean()),
        "beu4_total_beta_strand_des": float(df_4beu[df_4beu["Name"]=="design"][["Anti1", "Anti2", "Anti3", "Para"]].sum(axis=1).mean()),
        "hypothesis_testing": {
            "1n5u_no_statistically_significant_difference_detected": all_insignificant,
            "1n5u_min_pvalue": float(min(pvals_1n5u)),
            "4beu_inferential_test": "Not performed: N=1 observation per group (reference vs design) precludes two-sample t-testing."
        }
    }
    metrics_path = SCRIPT_DIR / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved metrics to: {metrics_path}")
    print("EXP007 completed successfully.")

if __name__ == "__main__":
    main()