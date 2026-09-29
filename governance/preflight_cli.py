"""
Command-line interface for governance preflight checks and workflow integration.

Usage:
    python governance/preflight_cli.py --model-family proteinsolver --stage evaluation
    python governance/preflight_cli.py --stage reporting --strict
"""

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from governance.store import GovernanceStore
from governance.preflight import run_preflight, format_preflight


def main():
    parser = argparse.ArgumentParser(description="Protein Design Governance Preflight CLI")
    parser.add_argument("--model-family", type=str, default=None, help="Model family (e.g. proteinsolver, proteinmpnn)")
    parser.add_argument("--stage", type=str, default="evaluation", help="Pipeline stage (evaluation, inference, reporting, development, commit)")
    parser.add_argument("--target", type=str, default=None, help="Target ID or PDB code (e.g. 1n5uA03)")
    parser.add_argument("--dataset", type=str, default=None, help="Dataset name or split")
    parser.add_argument("--experiment-id", type=str, default=None, help="Experiment ID (e.g. EXP004)")
    parser.add_argument("--framework", type=str, default=None, help="Framework (e.g. pytorch-geometric)")
    parser.add_argument("--no-auto-derive", action="store_true", help="Disable automatic environment context derivation")
    parser.add_argument("--strict", action="store_true", help="Exit with error if any MUST rule or conflict is present")
    parser.add_argument("--record", action="store_true", help="Record RULE_APPLIED events for all matched active rules")

    args = parser.parse_args()

    declared_context = {}
    if args.stage:
        declared_context["pipeline_stage"] = args.stage
    if args.model_family:
        declared_context["model_family"] = args.model_family
    if args.target:
        declared_context["target"] = args.target
    if args.dataset:
        declared_context["dataset"] = args.dataset
    if args.experiment_id:
        declared_context["experiment_id"] = args.experiment_id
    if args.framework:
        declared_context["framework"] = args.framework

    store = GovernanceStore()
    result = run_preflight(
        store=store,
        context=declared_context,
        auto_derive=not args.no_auto_derive,
        check_integrity=True,
    )

    print(format_preflight(result))

    # Optional recording of applied rules
    if args.record and args.experiment_id:
        for entry in result["tiers"]["MUST"] + result["tiers"]["SHOULD"]:
            rid = entry.get("rule_id")
            if rid:
                store.record_rule_applied(
                    rule_id=rid,
                    experiment_id=args.experiment_id,
                    context=f"CLI preflight (stage={args.stage})",
                )
        print(f"Recorded applied rules for experiment '{args.experiment_id}'.")

    # Strict check
    violations = result.get("integrity_violations", [])
    conflicts = result.get("conflicts", [])
    must_rules = result["tiers"].get("MUST", [])

    if violations:
        print(f"\nFAILED: {len(violations)} store integrity violations detected.")
        sys.exit(2)

    if conflicts:
        print(f"\nFAILED: Unresolved MUST-rule conflicts detected. Human review required.")
        sys.exit(3)

    if args.strict and must_rules:
        print(f"\nNOTICE: {len(must_rules)} MUST rules apply. Review check requirements before proceeding.")

    sys.exit(0)


if __name__ == "__main__":
    main()
