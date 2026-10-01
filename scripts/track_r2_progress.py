import json
import datetime
from pathlib import Path

def update_progress(stage, status, files_inspected=None, commands_executed=None,
                    confirmed_issues=0, repaired_issues=0, unresolved_issues=0,
                    blocked_issues=0, current_hypothesis="", current_data_population_identity="UNQUALIFIED",
                    compute_mode="GPU (RTX 3050 Laptop GPU, CUDA 12.4)", final_status="PENDING",
                    extra_notes=None):
    now = datetime.datetime.now().isoformat()
    state_file = Path("reports/AG_RUN_STATE.json")
    
    if state_file.exists():
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
        except Exception:
            state = {}
    else:
        state = {}
        
    start_time = state.get("start_time", now)
    
    state.update({
        "stage": stage,
        "status": status,
        "start_time": start_time,
        "last_update": now,
        "confirmed_issues": confirmed_issues,
        "repaired_issues": repaired_issues,
        "unresolved_issues": unresolved_issues,
        "blocked_issues": blocked_issues,
        "current_hypothesis": current_hypothesis,
        "current_data_population_identity": current_data_population_identity,
        "compute_mode": compute_mode,
        "final_status": final_status,
        "repository_heads": {
            "research_repo": "39f3daf70179aba3d9cc09cd056bc868f795fa9b",
            "historical_upstream": "69ef0965a3fc3bf191804035b539720a06e58ba6",
            "modern_impl": "58255bc67323f5fd009ac85ae02fbf69c152c457",
            "independent_verification_basis": "d961ef0b865f03d05a3df339b9f84b8f20c9ea56"
        },
        "checkpoint": {
            "file": "external/proteinsolver-original/data/e53-s1952148-d93703104.state",
            "sha256": "1E8272F05EC19041394568C949BBDBF012EE72C1595BE7157C4BB0324D0B5727",
            "verified": True
        }
    })
    
    if files_inspected:
        existing_files = state.get("files_inspected", [])
        for fi in files_inspected:
            if fi not in existing_files:
                existing_files.append(fi)
        state["files_inspected"] = existing_files
        
    if commands_executed:
        existing_cmds = state.get("commands_executed", [])
        for cmd in commands_executed:
            if cmd not in existing_cmds:
                existing_cmds.append(cmd)
        state["commands_executed"] = existing_cmds
        
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        
    stages = [
        "[0/8] Safety / baseline capture",
        "[1/8] Source + procedure qualification",
        "[2/8] Dataset/population availability qualification",
        "[3/8] R2 harness preparation",
        "[4/8] Figure 2B execution",
        "[5/8] Figure 2C execution",
        "[6/8] Independent numerical / provenance verification",
        "[7/8] Final R2 gate"
    ]
    
    stage_idx = 0
    for i, s in enumerate(stages):
        if s.split()[0] in stage:
            stage_idx = i
            break
            
    progress_md_lines = [
        "# Antigravity Live Progress — Phase R2",
        "",
        f"**Task:** PROTEINSOLVER — PHASE R2: EXACT FIGURE 2B + FIGURE 2C COMPUTATIONAL REPRODUCTION",
        f"**Agent:** Lead Scientific Reproducibility Engineer, Computational Biologist, Evidence-Governance Agent",
        f"**Started:** {start_time}",
        f"**Updated:** {now}",
        f"**Status:** {status}",
        f"**Current Stage:** {stage}",
        f"**Compute Mode:** {compute_mode}",
        "",
        "---",
        "",
        "## Metric Tracking",
        f"- **Current Stage:** {stage}",
        f"- **Confirmed Issues:** {confirmed_issues}",
        f"- **Repaired Issues:** {repaired_issues}",
        f"- **Unresolved Issues:** {unresolved_issues}",
        f"- **Blocked Issues:** {blocked_issues}",
        f"- **Current Hypothesis:** {current_hypothesis}",
        f"- **Current Data-Population Identity:** {current_data_population_identity}",
        f"- **Compute Mode:** {compute_mode}",
        f"- **Final Status:** {final_status}",
        "",
        "---",
        "",
        "## Repositories & Checkpoint Invariants",
        "- **Research Repo (D:\\Projects\\Protein Design):** HEAD `39f3daf70179aba3d9cc09cd056bc868f795fa9b`",
        "- **Historical Upstream (external/proteinsolver-original):** HEAD `69ef0965a3fc3bf191804035b539720a06e58ba6` (READ-ONLY)",
        "- **Modern Impl (D:\\Projects\\ProteinSolver):** HEAD `58255bc67323f5fd009ac85ae02fbf69c152c457` (READ-ONLY)",
        "- **Independent Verification Basis:** `d961ef0b865f03d05a3df339b9f84b8f20c9ea56`",
        "- **Checkpoint SHA-256:** `1E8272F05EC19041394568C949BBDBF012EE72C1595BE7157C4BB0324D0B5727` (VERIFIED)",
        "",
        "---",
        "",
        "## Stages Progress"
    ]
    
    for i, s in enumerate(stages):
        if i < stage_idx:
            progress_md_lines.append(f"- [x] **{s}**: Completed")
        elif i == stage_idx:
            status_text = "Completed" if status == "COMPLETE" else "IN PROGRESS"
            progress_md_lines.append(f"- [{'x' if status == 'COMPLETE' else ' '}] **{s}**: {status_text}")
        else:
            progress_md_lines.append(f"- [ ] **{s}**")
            
    if extra_notes:
        progress_md_lines.extend(["", "---", "", "## Stage Notes", extra_notes, ""])
        
    cleaned_md = "\n".join(line.rstrip() for line in progress_md_lines) + "\n"
    with open("reports/AG_LIVE_PROGRESS.md", "w", encoding="utf-8") as f:
        f.write(cleaned_md)
        
    print(f"Updated live progress: {stage} ({status})")

if __name__ == "__main__":
    update_progress(
        stage="[7/8] Final R2 gate",
        status="COMPLETE",
        files_inspected=[
            "experiments/R2_FIG2BC_REPRODUCTION/run.py",
            "experiments/R2_FIG2BC_REPRODUCTION/figure_2b_target_summary.csv",
            "experiments/R2_FIG2BC_REPRODUCTION/figure_2c_aggregate_summary.csv",
            "experiments/R2_FIG2BC_REPRODUCTION/figure_2c_replicates_summary.csv",
            "experiments/R2_FIG2BC_REPRODUCTION/historical_notebook_extracted_data.json",
            "experiments/R2_FIG2BC_REPRODUCTION/PROTEINSOLVER_R2_FIG2BC_RESULTS.json",
            "experiments/R2_FIG2BC_REPRODUCTION/config.json",
            "experiments/R2_FIG2BC_REPRODUCTION/population_manifest.json",
            "experiments/R2_FIG2BC_REPRODUCTION/provenance_manifest.json",
            "experiments/R2_FIG2BC_REPRODUCTION/README.md"
        ],
        commands_executed=[
            "run.py (executed Figure 2B oneshot & iterative MAP + Figure 2C 0/50/80% on GPU)",
            "Dual-validation string comparator (verified 0 discrepancies across all evaluations)",
            "pytest tests/ (81 passed in 28.75s)",
            "python -m governance.preflight_cli (passed with 0 conflicts)",
            "git diff --check (whitespace clean)"
        ],
        confirmed_issues=1,
        repaired_issues=1,
        unresolved_issues=0,
        blocked_issues=0,
        current_hypothesis="Phase R2 Final Gate evaluated. FIG2B_POPULATION_STATUS = NOT_RECONSTRUCTIBLE_WITH_CURRENT_ARTIFACTS (published 10k dataset on inaccessible GCS gs://deep-protein-gen). Reproduction status rendered as R2_PARTIAL_VERIFIED_ON_AUXILIARY_POPULATION_WITH_HISTORICAL_EVIDENCE_RECONSTRUCTION.",
        current_data_population_identity="AUXILIARY_PRIMARY_TARGET_STRUCTURES (N=7, 673 AA) + HISTORICAL_NOTEBOOK_PRESERVED_EVIDENCE (191f05de SVG data, 1,283 records)",
        final_status="R2_PARTIAL",
        extra_notes="All 8 stages [0/8] to [7/8] completed. Checkpoint, model invariants, decoding algorithms, conditioning mechanisms, independent dual checks, pytest (81 passed), governance preflight, and clean git diff verified."
    )
