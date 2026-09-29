"""
Seed the governance store with mandatory ProteinSolver lessons and rules.

These encode the six real project failure cases from Phase 1.
Run once to initialize governance/data/.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from governance.schemas import Lesson, Rule
from governance.store import GovernanceStore


def seed_lessons_and_rules():
    store = GovernanceStore()

    # ============================================================
    # LESSONS (from real ProteinSolver failures)
    # ============================================================

    lessons = [
        Lesson(
            id="L-001",
            title="Native sequence visibility produces false 100% recovery",
            what_happened="First ProteinSolver run showed 100% sequence recovery. Investigation revealed data.y contained the native sequence, and protein_design.py copied it position-by-position via strategy='ref'.",
            lesson="A native-sequence-visible run is NOT valid all-masked inverse-folding recovery. Always distinguish diagnostic scoring (natives visible) from true recovery (all residues masked).",
            type="METHOD_SCIENCE",
            scope="project-wide",
            trigger="Any experiment reporting sequence recovery metrics",
            evidence_status="REPRODUCED",
            evidence_scope="Demonstrated on 1n5uA03 via EXP004 mask invariance test",
            governance_lifecycle="ACTIVE",
            source="EXP004_MASK_INVARIANCE",
            owner="project-lead",
            related_experiments=["EXP004_MASK_INVARIANCE"],
            related_claims=["V-14"],
            keywords=["recovery", "leakage", "mask", "native", "diagnostic", "data.y", "information-leak"],
            applicability={"pipeline_stage": ["evaluation", "inference", "design"]},
        ),
        Lesson(
            id="L-002",
            title="PyG Data vs Batch interface mismatch crashes design_sequence",
            what_happened="ProteinSolver's design_sequence expected data.batch attribute (from PyG Batch). In PyG 2.x, plain Data objects have data.batch=None, causing 'NoneType has no attribute max' crash.",
            lesson="Always use Batch.from_data_list([data]) before calling functions that expect batch-level attributes. Check interface contracts before passing data between components.",
            type="BUG_ENVIRONMENT",
            scope="proteinsolver",
            trigger="Using PyG Data objects with functions expecting Batch",
            evidence_status="REPRODUCED",
            evidence_scope="Observed and fixed during ProteinSolver integration",
            governance_lifecycle="ACTIVE",
            source="Phase 1 integration",
            owner="project-lead",
            related_claims=["V-12"],
            keywords=["batch", "data", "pyg", "crash", "interface", "proteinsolver"],
            applicability={"model_family": "proteinsolver", "framework": "pytorch-geometric"},
        ),
        Lesson(
            id="L-003",
            title="Modern runtime != historical runtime equivalence",
            what_happened="Initial reports described ProteinSolver execution as 'reproduced'. Hardening review identified this overclaimed historical numerical equivalence that was never tested.",
            lesson="Use 'FUNCTIONALLY REPRODUCED WITH MODERN COMPATIBILITY ADAPTATION'. Never claim historical runtime equivalence without actually comparing outputs against the original Python 3.6 / PyG 1.3 / Linux stack.",
            type="DATA_PROVENANCE",
            scope="project-wide",
            trigger="Any claim about reproduction fidelity",
            evidence_status="REPRODUCED",
            evidence_scope="Hardening pass identified multiple instances across project docs",
            governance_lifecycle="ACTIVE",
            source="Scientific hardening pass",
            owner="project-lead",
            related_claims=["V-12", "V-13"],
            keywords=["reproduction", "equivalence", "historical", "fidelity", "compatibility"],
            applicability={"pipeline_stage": ["evaluation", "reporting"]},
        ),
        Lesson(
            id="L-004",
            title="Single-target result is not a benchmark",
            what_happened="41.30% recovery on 1n5uA03 (one 92-AA CATH domain) was at risk of being described as benchmark performance.",
            lesson="A single-target result is a 'single-target all-masked inverse-folding integration result'. It is NOT benchmark accuracy, generalization performance, or representative of average behavior across folds.",
            type="METHOD_SCIENCE",
            scope="project-wide",
            trigger="Reporting evaluation results from fewer than a representative benchmark set",
            evidence_status="REPRODUCED",
            evidence_scope="1n5uA03 result established in EXP000/EXP001",
            governance_lifecycle="ACTIVE",
            source="Scientific hardening pass",
            owner="project-lead",
            related_experiments=["EXP000_PROTEINSOLVER_SMOKETEST", "EXP001_PROTEINSOLVER_INFERENCE"],
            related_claims=["V-13"],
            keywords=["benchmark", "single-target", "generalization", "1n5uA03"],
            applicability={"pipeline_stage": ["evaluation", "reporting"]},
        ),
        Lesson(
            id="L-005",
            title="Training set membership is not verifiable from accessible metadata",
            what_happened="Author's notebook checked '1.10.246.10' in cath_ids (False), but the full 72M training Parquet corpus is on an external cluster, not in git.",
            lesson="Do not call 1n5uA03 'guaranteed held-out' or 'unseen'. Classify as 'NOT VERIFIABLE FROM ACCESSIBLE METADATA' unless full training data is directly queried.",
            type="DATA_PROVENANCE",
            scope="proteinsolver",
            trigger="Any claim about training/test membership of a structure",
            evidence_status="NOT_VERIFIABLE",
            evidence_scope="Author's notebook check is suggestive but not definitive",
            governance_lifecycle="ACTIVE",
            source="Provenance audit",
            owner="project-lead",
            related_claims=["NV-01"],
            keywords=["training", "membership", "held-out", "contamination", "1n5uA03", "provenance"],
            applicability={"model_family": "proteinsolver", "pipeline_stage": ["evaluation", "reporting"]},
        ),
        Lesson(
            id="L-006",
            title="Historical source repository must remain preserved and clean",
            what_happened="All six compatibility issues (fcntl, kmtools, scatter_, Batch, key mapping, CPU placement) were resolved without modifying external/proteinsolver-original/.",
            lesson="Never commit changes to external/proteinsolver-original/. All compatibility work belongs in external wrappers. Check git -C external/proteinsolver-original status before every project commit.",
            type="PROCESS_TEAM",
            scope="project-wide",
            trigger="Any modification near external/ or compatibility shims",
            evidence_status="REPRODUCED",
            evidence_scope="Verified clean at commit 69ef0965",
            governance_lifecycle="ACTIVE",
            source="Phase 1 integration",
            owner="project-lead",
            related_files=["external/proteinsolver-original/"],
            keywords=["historical", "source", "preservation", "external", "clean"],
            applicability={"pipeline_stage": ["development", "commit"]},
        ),
    ]

    # ============================================================
    # RULES (derived from lessons, all ACTIVE for core rules)
    # ============================================================

    rules = [
        Rule(
            id="R-001",
            title="Require all-masked setup for valid inverse-folding recovery claims",
            description="Any experiment claiming sequence recovery must verify that all residues were masked (data.x=20, data.y=None). Native-visible results are diagnostic scoring only.",
            source_lesson="L-001",
            scope="project-wide",
            applicability_conditions={"pipeline_stage": ["evaluation", "inference", "design"]},
            priority="MUST",
            enforcement_level="AUTOMATED",
            check_pointer="tests/test_governance.py::test_native_visible_not_valid_recovery",
            owner="project-lead",
            override_policy="Requires project lead written approval with justification",
            review_trigger="New model integration or new evaluation protocol",
            governance_lifecycle="ACTIVE",
            keywords=["recovery", "mask", "leakage", "evaluation"],
        ),
        Rule(
            id="R-002",
            title="Use Batch.from_data_list for ProteinSolver design_sequence",
            description="Always wrap PyG Data objects with Batch.from_data_list([data]) before calling design_sequence or other batch-expecting functions.",
            source_lesson="L-002",
            scope="proteinsolver",
            applicability_conditions={"model_family": "proteinsolver", "framework": "pytorch-geometric"},
            priority="MUST",
            enforcement_level="AUTOMATED",
            check_pointer="tests/test_governance.py::test_batch_interface_requirement",
            owner="project-lead",
            override_policy="Only if alternative batching mechanism is verified equivalent",
            review_trigger="PyG version upgrade or ProteinSolver wrapper refactor",
            governance_lifecycle="ACTIVE",
            keywords=["batch", "data", "pyg", "interface", "proteinsolver"],
        ),
        Rule(
            id="R-003",
            title="Use correct reproduction wording",
            description="Never claim 'historical equivalence' or '100% mathematical fidelity'. Use 'FUNCTIONALLY REPRODUCED WITH MODERN COMPATIBILITY ADAPTATION' unless historical-stack numerical comparison is performed.",
            source_lesson="L-003",
            scope="project-wide",
            applicability_conditions={"pipeline_stage": ["reporting", "evaluation"]},
            priority="MUST",
            enforcement_level="MANUAL",
            check_pointer="tests/test_governance.py::test_reproduction_wording",
            owner="project-lead",
            override_policy="Only with evidence from historical-stack comparison",
            review_trigger="If historical environment becomes available for comparison",
            governance_lifecycle="ACTIVE",
            keywords=["reproduction", "equivalence", "wording", "fidelity"],
        ),
        Rule(
            id="R-004",
            title="Single-target results cannot be described as benchmarks",
            description="Results from fewer targets than a representative benchmark set must be classified as integration results, not benchmark accuracy or generalization performance.",
            source_lesson="L-004",
            scope="project-wide",
            applicability_conditions={"pipeline_stage": ["evaluation", "reporting"]},
            priority="MUST",
            enforcement_level="MANUAL",
            check_pointer="tests/test_governance.py::test_single_target_not_benchmark",
            owner="project-lead",
            override_policy="Only when full benchmark set is evaluated",
            review_trigger="Multi-target evaluation begins",
            governance_lifecycle="ACTIVE",
            keywords=["benchmark", "single-target", "generalization"],
        ),
        Rule(
            id="R-005",
            title="Do not claim training membership without direct verification",
            description="Never describe a structure as 'held-out', 'unseen', or 'guaranteed not in training' unless training data is directly queried. Use 'NOT VERIFIABLE FROM ACCESSIBLE METADATA'.",
            source_lesson="L-005",
            scope="project-wide",
            applicability_conditions={"pipeline_stage": ["evaluation", "reporting"]},
            priority="MUST",
            enforcement_level="MANUAL",
            check_pointer="tests/test_governance.py::test_training_membership_uncertainty",
            owner="project-lead",
            override_policy="Only with direct training data query results",
            review_trigger="Training data becomes accessible",
            governance_lifecycle="ACTIVE",
            keywords=["training", "membership", "held-out", "contamination"],
        ),
        Rule(
            id="R-006",
            title="Historical source must remain unmodified",
            description="external/proteinsolver-original/ must have zero modifications. Verify with git status before every commit. All compatibility work goes in external wrappers.",
            source_lesson="L-006",
            scope="project-wide",
            applicability_conditions={"pipeline_stage": ["development", "commit"]},
            priority="MUST",
            enforcement_level="AUTOMATED",
            check_pointer="tests/test_governance.py::test_historical_source_clean",
            owner="project-lead",
            override_policy="Never. If source needs modification, fork into a new directory.",
            review_trigger="Any commit touching external/",
            governance_lifecycle="ACTIVE",
            keywords=["historical", "source", "preservation", "external"],
        ),
        Rule(
            id="R-007",
            title="Distinguish evidence scope from application scope",
            description="A claim verified on one target/condition must not be applied to broader contexts without explicit EXTRAPOLATION_REVIEW_REQUIRED flag.",
            source_lesson="L-004",
            scope="project-wide",
            applicability_conditions={"pipeline_stage": ["evaluation", "reporting"]},
            priority="SHOULD",
            enforcement_level="MANUAL",
            check_pointer="",
            owner="project-lead",
            override_policy="Explicit documentation of extrapolation rationale",
            review_trigger="Any claim applied outside its demonstrated scope",
            governance_lifecycle="ACTIVE",
            keywords=["scope", "extrapolation", "evidence", "claim"],
        ),
        Rule(
            id="R-008",
            title="AI agents cannot self-promote lessons or override governance",
            description="Agents may propose lessons and identify conflicts but cannot promote lessons to rules, change governance status, broaden scope, or resolve contradictory evidence autonomously.",
            source_lesson="",
            scope="project-wide",
            applicability_conditions={},
            priority="MUST",
            enforcement_level="AUTOMATED",
            check_pointer="tests/test_governance.py::test_ai_cannot_self_promote",
            owner="project-lead",
            override_policy="Never. This is a structural constraint.",
            review_trigger="Any governance system modification",
            governance_lifecycle="ACTIVE",
            keywords=["ai", "agent", "promotion", "governance", "boundary"],
        ),
    ]

    # Seed
    errors_found = False
    for lesson in lessons:
        errs = store.add_lesson(lesson)
        if errs:
            print(f"ERROR adding {lesson.id}: {errs}")
            errors_found = True
        else:
            print(f"Added lesson {lesson.id}: {lesson.title}")

    for rule in rules:
        errs = store.add_rule(rule)
        if errs:
            print(f"ERROR adding {rule.id}: {errs}")
            errors_found = True
        else:
            print(f"Added rule {rule.id}: {rule.title}")

    if not errors_found:
        print(f"\nSeeded {len(lessons)} lessons and {len(rules)} rules successfully.")
        print(f"Data directory: {store.base_dir}")
    else:
        print("\nSEEDING COMPLETED WITH ERRORS.")

    return not errors_found


if __name__ == "__main__":
    success = seed_lessons_and_rules()
    sys.exit(0 if success else 1)
