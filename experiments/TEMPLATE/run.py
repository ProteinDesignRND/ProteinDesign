"""
Experiment: EXP_NNN_NAME

[Brief description of what this experiment does.]

Usage:
    .\\environment\\proteinsolver-original\\Scripts\\python.exe experiments\\EXP_NNN_NAME\\run.py
"""

import json
import sys
import time
from pathlib import Path


def main():
    exp_dir = Path(__file__).resolve().parent
    config_path = exp_dir / "config.json"
    with open(config_path, "r") as f:
        config = json.load(f)

    log_lines = []

    def log(msg: str):
        print(msg)
        log_lines.append(str(msg))

    log("=" * 60)
    log(f"EXPERIMENT: {config['experiment_id']}")
    log("=" * 60)

    # =====================================================
    # 0. Governance Preflight & Safety Evaluation
    # =====================================================
    project_root = exp_dir.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from governance import GovernanceStore, run_preflight, format_preflight

    store = GovernanceStore()
    preflight_context = {
        "pipeline_stage": "evaluation",
        "model_family": config.get("model", "unknown"),
        "target": config.get("target_pdb", ""),
        "experiment_id": config.get("experiment_id", ""),
    }
    gov_result = run_preflight(store, context=preflight_context, auto_derive=True, check_integrity=True)
    log(format_preflight(gov_result))

    if gov_result.get("integrity_violations"):
        raise RuntimeError(f"Governance integrity violations detected: {gov_result['integrity_violations']}")
    if gov_result.get("conflicts"):
        raise RuntimeError("Governance conflicts detected! Human review required before execution.")

    # Record rule applications in append-only audit trail
    for rule_entry in gov_result["tiers"]["MUST"]:
        store.record_rule_applied(
            rule_id=rule_entry["rule_id"],
            experiment_id=config["experiment_id"],
            context=f"Stage: evaluation, Model: {config.get('model')}",
        )

    t0 = time.perf_counter()

    # =====================================================
    # TODO: Implement experiment logic here
    # =====================================================

    runtime = time.perf_counter() - t0
    log(f"\nRuntime: {runtime:.4f} seconds")

    # Save log
    with open(exp_dir / "run_log.txt", "w") as f:
        f.write("\n".join(log_lines) + "\n")

    # Save metrics
    metrics = {
        "experiment_id": config["experiment_id"],
        "date": config["date"],
        "runtime_seconds": round(runtime, 4),
        # TODO: Add experiment-specific metrics
    }
    with open(exp_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    log("Done.")


if __name__ == "__main__":
    main()
