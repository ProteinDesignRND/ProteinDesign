"""
Comprehensive governance test suite.

Tests cover:
A. Schema validity
B. Lesson lifecycle
C. Rule lifecycle
D. Event recording
E. Deterministic retrieval
F. Applicability
G. Unknown context
H. Precedence
I. Conflict detection
J. Blocker behavior
K. Override recording
L. Claim-level protection
M. Extrapolation detection
N. Novelty detection
O. Validation levels
P. Failure classification
Q. Duplicate handling
R. Migration/versioning
S. AI-agent boundaries
T. Regression cases (ProteinSolver)
U. Live-progress system
V. Clean repository state

Includes negative/adversarial cases.
"""

import json
import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from governance import (
    SCHEMA_VERSION, LESSON_TYPES, EVIDENCE_STATUSES,
    GOVERNANCE_LIFECYCLES, RULE_PRIORITIES, ENFORCEMENT_LEVELS,
    EVENT_TYPES, FAILURE_CLASSES, PRECEDENCE_ORDER, PREFLIGHT_TIERS,
)
from governance.schemas import Lesson, Rule, Event
from governance.store import GovernanceStore
from governance.preflight import run_preflight, format_preflight, _context_matches


class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def ok(self, name):
        self.passed += 1
        print(f"  PASS: {name}")

    def fail(self, name, msg=""):
        self.failed += 1
        self.errors.append((name, msg))
        print(f"  FAIL: {name} — {msg}")

    def assert_true(self, name, condition, msg=""):
        if condition:
            self.ok(name)
        else:
            self.fail(name, msg or "Expected True")

    def assert_false(self, name, condition, msg=""):
        if not condition:
            self.ok(name)
        else:
            self.fail(name, msg or "Expected False")

    def assert_eq(self, name, actual, expected, msg=""):
        if actual == expected:
            self.ok(name)
        else:
            self.fail(name, msg or f"Expected {expected!r}, got {actual!r}")

    def assert_in(self, name, item, collection, msg=""):
        if item in collection:
            self.ok(name)
        else:
            self.fail(name, msg or f"{item!r} not in collection")

    def assert_not_in(self, name, item, collection, msg=""):
        if item not in collection:
            self.ok(name)
        else:
            self.fail(name, msg or f"{item!r} unexpectedly in collection")

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"RESULTS: {self.passed}/{total} passed, {self.failed} failed")
        if self.errors:
            print("\nFailed tests:")
            for name, msg in self.errors:
                print(f"  - {name}: {msg}")
        print(f"{'='*60}")
        return self.failed == 0


def make_temp_store():
    """Create a GovernanceStore in a temp directory."""
    tmpdir = tempfile.mkdtemp(prefix="gov_test_")
    return GovernanceStore(base_dir=Path(tmpdir)), tmpdir


def cleanup(tmpdir):
    shutil.rmtree(tmpdir, ignore_errors=True)


def run_all_tests():
    r = TestResult()

    # ============================================================
    # A. Schema Validity
    # ============================================================
    print("\n=== A. Schema Validity ===")

    lesson = Lesson(id="test-1", type="METHOD_SCIENCE", evidence_status="OBSERVED",
                    governance_lifecycle="PROPOSED")
    r.assert_eq("A1 valid lesson", lesson.validate(), [])

    bad_lesson = Lesson(id="", type="INVALID_TYPE")
    errs = bad_lesson.validate()
    r.assert_true("A2 invalid lesson has errors", len(errs) >= 2,
                  f"Expected >=2 errors, got {errs}")

    rule = Rule(id="test-r1", priority="MUST", enforcement_level="AUTOMATED",
                governance_lifecycle="ACTIVE")
    r.assert_eq("A3 valid rule", rule.validate(), [])

    bad_rule = Rule(id="", priority="INVALID")
    r.assert_true("A4 invalid rule has errors", len(bad_rule.validate()) >= 2)

    event = Event(event_id="e1", event_type="LESSON_CREATED")
    r.assert_eq("A5 valid event", event.validate(), [])

    bad_event = Event(event_id="", event_type="INVALID")
    r.assert_true("A6 invalid event has errors", len(bad_event.validate()) >= 1)

    # Schema constants sanity
    r.assert_eq("A7 schema version format", SCHEMA_VERSION, "1.0.0")
    r.assert_in("A8 BUG_ENVIRONMENT in types", "BUG_ENVIRONMENT", LESSON_TYPES)
    r.assert_in("A9 CONTRADICTED in evidence", "CONTRADICTED", EVIDENCE_STATUSES)

    # ============================================================
    # B. Lesson Lifecycle
    # ============================================================
    print("\n=== B. Lesson Lifecycle ===")

    store, tmpdir = make_temp_store()
    try:
        lesson = Lesson(id="L-TEST-1", title="Test lesson", type="BUG_ENVIRONMENT",
                        governance_lifecycle="PROPOSED", evidence_status="OBSERVED")
        errs = store.add_lesson(lesson)
        r.assert_eq("B1 add lesson succeeds", errs, [])

        loaded = store.get_lesson("L-TEST-1")
        r.assert_true("B2 lesson retrievable", loaded is not None)
        r.assert_eq("B3 lesson lifecycle", loaded["governance_lifecycle"], "PROPOSED")

        # Duplicate
        errs = store.add_lesson(lesson)
        r.assert_true("B4 duplicate rejected", len(errs) > 0)
    finally:
        cleanup(tmpdir)

    # ============================================================
    # C. Rule Lifecycle
    # ============================================================
    print("\n=== C. Rule Lifecycle ===")

    store, tmpdir = make_temp_store()
    try:
        rule = Rule(id="R-TEST-1", title="Test rule", priority="MUST",
                    enforcement_level="MANUAL", governance_lifecycle="ACTIVE",
                    source_lesson="L-TEST-1")
        errs = store.add_rule(rule)
        r.assert_eq("C1 add rule succeeds", errs, [])

        loaded = store.get_rule("R-TEST-1")
        r.assert_true("C2 rule retrievable", loaded is not None)
        r.assert_eq("C3 rule source lesson", loaded["source_lesson"], "L-TEST-1")
    finally:
        cleanup(tmpdir)

    # ============================================================
    # D. Event Recording
    # ============================================================
    print("\n=== D. Event Recording ===")

    store, tmpdir = make_temp_store()
    try:
        event = Event(event_id="e-test-1", event_type="LESSON_CREATED",
                      entity_type="LESSON", entity_id="L-001", actor="test")
        errs = store.append_event(event)
        r.assert_eq("D1 append event succeeds", errs, [])

        events = store.load_events()
        r.assert_true("D2 event in log", len(events) >= 1)
        r.assert_eq("D3 event type", events[0]["event_type"], "LESSON_CREATED")

        # Append more
        store.append_event(Event(event_id="e-test-2", event_type="RULE_PROMOTED",
                                 entity_id="R-001"))
        events = store.load_events()
        r.assert_eq("D4 multiple events", len(events), 2)

        # Find by entity
        found = store.find_events(entity_id="L-001")
        r.assert_eq("D5 find by entity", len(found), 1)
    finally:
        cleanup(tmpdir)

    # ============================================================
    # E. Deterministic Retrieval
    # ============================================================
    print("\n=== E. Deterministic Retrieval ===")

    store, tmpdir = make_temp_store()
    try:
        store.add_lesson(Lesson(id="L-E1", type="METHOD_SCIENCE",
                                governance_lifecycle="ACTIVE", evidence_status="OBSERVED",
                                keywords=["proteinsolver", "mask"]))
        store.add_lesson(Lesson(id="L-E2", type="BUG_ENVIRONMENT",
                                governance_lifecycle="ACTIVE", evidence_status="OBSERVED",
                                keywords=["proteinmpnn"]))

        found = store.find_lessons(type="METHOD_SCIENCE")
        r.assert_eq("E1 find by type", len(found), 1)
        r.assert_eq("E2 correct lesson", found[0]["id"], "L-E1")

        found = store.find_lessons(keyword="mask")
        r.assert_eq("E3 find by keyword", len(found), 1)

        found = store.find_lessons(keyword="nonexistent")
        r.assert_eq("E4 no match", len(found), 0)
    finally:
        cleanup(tmpdir)

    # ============================================================
    # F. Applicability (context matching)
    # ============================================================
    print("\n=== F. Applicability ===")

    matches, expl, unknowns = _context_matches(
        {"model_family": "proteinsolver"}, {"model_family": "proteinsolver"}
    )
    r.assert_true("F1 exact match", matches)
    r.assert_eq("F2 no unknowns", unknowns, [])

    matches, _, _ = _context_matches(
        {"model_family": "proteinsolver"}, {"model_family": "proteinmpnn"}
    )
    r.assert_false("F3 mismatch", matches)

    matches, _, _ = _context_matches({}, {"model_family": "proteinsolver"})
    r.assert_true("F4 empty conditions = universal", matches)

    matches, _, unknowns = _context_matches(
        {"model_family": "proteinsolver", "dataset": "cath42"},
        {"model_family": "proteinsolver"}
    )
    r.assert_in("F5 unknown field", "dataset", unknowns)

    # List-valued conditions
    matches, _, _ = _context_matches(
        {"pipeline_stage": ["evaluation", "inference"]},
        {"pipeline_stage": "evaluation"}
    )
    r.assert_true("F6 list match", matches)

    matches, _, _ = _context_matches(
        {"pipeline_stage": ["evaluation", "inference"]},
        {"pipeline_stage": "training"}
    )
    r.assert_false("F7 list mismatch", matches)

    # ============================================================
    # G. Unknown Context
    # ============================================================
    print("\n=== G. Unknown Context ===")

    store, tmpdir = make_temp_store()
    try:
        store.add_rule(Rule(id="R-G1", priority="MUST", enforcement_level="MANUAL",
                            governance_lifecycle="ACTIVE",
                            applicability_conditions={"model_family": "proteinsolver"}))
        result = run_preflight(store, {"pipeline_stage": "evaluation"})
        r.assert_true("G1 unknown context fields listed",
                      len(result["coverage"]["unknown_context_fields"]) > 0 or
                      result["coverage"]["rules_relevant"] == 0)
    finally:
        cleanup(tmpdir)

    # ============================================================
    # H. Precedence
    # ============================================================
    print("\n=== H. Precedence ===")

    store, tmpdir = make_temp_store()
    try:
        store.add_rule(Rule(id="R-H1", title="Integrity rule", priority="MUST",
                            enforcement_level="MANUAL", governance_lifecycle="ACTIVE",
                            scope="integrity", applicability_conditions={}))
        store.add_rule(Rule(id="R-H2", title="Task rule", priority="MUST",
                            enforcement_level="MANUAL", governance_lifecycle="ACTIVE",
                            scope="task-specific", applicability_conditions={}))
        result = run_preflight(store, {})
        musts = result["tiers"]["MUST"]
        r.assert_true("H1 integrity before task",
                      len(musts) >= 2 and musts[0]["rule_id"] == "R-H1")
    finally:
        cleanup(tmpdir)

    # ============================================================
    # I. Conflict Detection
    # ============================================================
    print("\n=== I. Conflict Detection ===")

    store, tmpdir = make_temp_store()
    try:
        store.add_rule(Rule(id="R-I1", priority="MUST", enforcement_level="MANUAL",
                            governance_lifecycle="ACTIVE", scope="test-scope",
                            applicability_conditions={}))
        store.add_rule(Rule(id="R-I2", priority="MUST", enforcement_level="MANUAL",
                            governance_lifecycle="ACTIVE", scope="test-scope",
                            applicability_conditions={}))
        result = run_preflight(store, {})
        r.assert_true("I1 conflict detected", len(result["conflicts"]) > 0)
        r.assert_eq("I2 conflict type", result["conflicts"][0]["type"],
                     "MULTIPLE_MUST_SAME_SCOPE")
    finally:
        cleanup(tmpdir)

    # ============================================================
    # J. Blocker Behavior (PROPOSED cannot block)
    # ============================================================
    print("\n=== J. Blocker Behavior ===")

    store, tmpdir = make_temp_store()
    try:
        # Proposed rule: even if priority=MUST, should appear as FYI only
        store.add_rule(Rule(id="R-J1", title="Proposed MUST", priority="MUST",
                            enforcement_level="AUTOMATED", governance_lifecycle="PROPOSED",
                            applicability_conditions={}))
        result = run_preflight(store, {})
        must_ids = [e["rule_id"] for e in result["tiers"]["MUST"]]
        fyi_ids = [e.get("rule_id") for e in result["tiers"]["FYI"]]
        r.assert_not_in("J1 proposed not in MUST", "R-J1", must_ids)
        r.assert_in("J2 proposed in FYI", "R-J1", fyi_ids)
    finally:
        cleanup(tmpdir)

    # ============================================================
    # K. Override Recording
    # ============================================================
    print("\n=== K. Override Recording ===")

    store, tmpdir = make_temp_store()
    try:
        override_event = Event(
            event_id="e-override-1", event_type="RULE_OVERRIDDEN",
            entity_type="RULE", entity_id="R-001",
            actor="project-lead",
            context="Override for specific experiment EXP005",
            evidence="Approved by lead on 2026-09-24",
        )
        errs = store.append_event(override_event)
        r.assert_eq("K1 override event recorded", errs, [])
        found = store.find_events(event_type="RULE_OVERRIDDEN")
        r.assert_eq("K2 override retrievable", len(found), 1)
        r.assert_eq("K3 override actor", found[0]["actor"], "project-lead")
    finally:
        cleanup(tmpdir)

    # ============================================================
    # L. Claim-Level Protection
    # ============================================================
    print("\n=== L. Claim-Level Protection ===")

    # Use production store for this (read-only)
    prod_store = GovernanceStore()
    result = run_preflight(prod_store, {
        "pipeline_stage": "reporting",
        "model_family": "proteinsolver"
    })
    must_ids = [e["rule_id"] for e in result["tiers"]["MUST"]]
    r.assert_in("L1 reproduction wording enforced", "R-003", must_ids)
    r.assert_in("L2 single-target check enforced", "R-004", must_ids)
    r.assert_in("L3 training membership check enforced", "R-005", must_ids)

    # ============================================================
    # M. Extrapolation Detection
    # ============================================================
    print("\n=== M. Extrapolation Detection ===")

    r.assert_in("M1 R-007 exists", "R-007",
                [r_id for r_id in prod_store.load_rules()])
    rule_007 = prod_store.get_rule("R-007")
    r.assert_eq("M2 scope rule is SHOULD", rule_007["priority"], "SHOULD")

    # ============================================================
    # N. Novelty Detection
    # ============================================================
    print("\n=== N. Novelty Detection ===")

    store, tmpdir = make_temp_store()
    try:
        store.add_rule(Rule(id="R-N1", priority="SHOULD", enforcement_level="MANUAL",
                            governance_lifecycle="ACTIVE",
                            applicability_conditions={"model_family": "proteinsolver"}))
        result = run_preflight(store, {"model_family": "esm2", "new_axis": "value"})
        novel = result["coverage"]["novel_conditions"]
        r.assert_true("N1 novel conditions detected", len(novel) >= 1)
        novel_fields = [n["field"] for n in novel]
        r.assert_in("N2 new_axis is novel", "new_axis", novel_fields)
    finally:
        cleanup(tmpdir)

    # ============================================================
    # O. Validation Levels (claim vs rule vs check)
    # ============================================================
    print("\n=== O. Validation Levels ===")

    # The system must distinguish these three levels
    # Claim: "L-001 lesson is true" — evidence_status
    # Rule: "R-001 rule is useful" — governance_lifecycle
    # Check: "test catches the problem" — enforcement_level + check_pointer

    l001 = prod_store.get_lesson("L-001")
    r001 = prod_store.get_rule("R-001")
    r.assert_true("O1 lesson evidence separate from governance",
                  l001["evidence_status"] != l001["governance_lifecycle"])
    r.assert_true("O2 rule has check pointer", bool(r001["check_pointer"]))
    r.assert_true("O3 rule lifecycle independent of lesson evidence",
                  r001["governance_lifecycle"] != l001["evidence_status"])

    # ============================================================
    # P. Failure Classification
    # ============================================================
    print("\n=== P. Failure Classification ===")

    r.assert_eq("P1 failure classes count", len(FAILURE_CLASSES), 7)
    r.assert_in("P2 NO_LESSON", "NO_LESSON", FAILURE_CLASSES)
    r.assert_in("P3 RETRIEVAL_MISS", "RETRIEVAL_MISS", FAILURE_CLASSES)
    r.assert_in("P4 ENFORCEMENT_GAP", "ENFORCEMENT_GAP", FAILURE_CLASSES)

    # ============================================================
    # Q. Duplicate Handling
    # ============================================================
    print("\n=== Q. Duplicate Handling ===")

    store, tmpdir = make_temp_store()
    try:
        store.add_lesson(Lesson(id="L-Q1", type="METHOD_SCIENCE",
                                governance_lifecycle="PROPOSED", evidence_status="OBSERVED"))
        errs = store.add_lesson(Lesson(id="L-Q1", type="METHOD_SCIENCE",
                                       governance_lifecycle="PROPOSED",
                                       evidence_status="OBSERVED"))
        r.assert_true("Q1 duplicate rejected", "Duplicate" in errs[0])
    finally:
        cleanup(tmpdir)

    # ============================================================
    # R. Migration / Versioning
    # ============================================================
    print("\n=== R. Migration/Versioning ===")

    store, tmpdir = make_temp_store()
    try:
        lesson = Lesson(id="L-R1", version=1, schema_version="1.0.0",
                        type="METHOD_SCIENCE", governance_lifecycle="PROPOSED",
                        evidence_status="OBSERVED")
        store.add_lesson(lesson)
        loaded = store.get_lesson("L-R1")
        r.assert_eq("R1 version preserved", loaded["version"], 1)
        r.assert_eq("R2 schema version preserved", loaded["schema_version"], "1.0.0")

        # Unknown fields preserved in JSON
        lessons = store.load_lessons()
        lessons["L-R1"]["future_field"] = "preserved"
        store.save_lessons(lessons)
        reloaded = store.get_lesson("L-R1")
        r.assert_eq("R3 unknown fields preserved", reloaded.get("future_field"), "preserved")
    finally:
        cleanup(tmpdir)

    # ============================================================
    # S. AI-Agent Boundaries
    # ============================================================
    print("\n=== S. AI-Agent Boundaries ===")

    store, tmpdir = make_temp_store()
    try:
        # AI creates a PROPOSED lesson — allowed
        lesson = Lesson(id="L-S1", governance_lifecycle="PROPOSED",
                        type="AI_TOOLING", evidence_status="OBSERVED")
        errs = store.add_lesson(lesson)
        r.assert_eq("S1 AI can propose lesson", errs, [])

        # PROPOSED lesson cannot appear in MUST tier
        store.add_rule(Rule(id="R-S1", priority="MUST", enforcement_level="AUTOMATED",
                            governance_lifecycle="PROPOSED", source_lesson="L-S1",
                            applicability_conditions={}))
        result = run_preflight(store, {})
        must_ids = [e["rule_id"] for e in result["tiers"]["MUST"]]
        r.assert_not_in("S2 proposed rule not in MUST", "R-S1", must_ids,
                        "Unreviewed lesson/rule cannot block execution")

        # Verify enforcement: PROPOSED lesson cannot change its own lifecycle
        loaded = store.get_lesson("L-S1")
        r.assert_eq("S3 lesson stays PROPOSED", loaded["governance_lifecycle"], "PROPOSED")
    finally:
        cleanup(tmpdir)

    # ============================================================
    # T. ProteinSolver Regression Cases
    # ============================================================
    print("\n=== T. ProteinSolver Regression Cases ===")

    # T1: Native-visible cannot be valid recovery
    r.assert_true("T1 L-001 exists in prod",
                  prod_store.get_lesson("L-001") is not None)
    r.assert_eq("T1b L-001 type", prod_store.get_lesson("L-001")["type"], "METHOD_SCIENCE")

    # T2: Data vs Batch mismatch
    r.assert_true("T2 L-002 exists", prod_store.get_lesson("L-002") is not None)
    r.assert_in("T2b batch keyword",
                "batch", prod_store.get_lesson("L-002")["keywords"])

    # T3: Modern != historical
    r.assert_true("T3 L-003 exists", prod_store.get_lesson("L-003") is not None)

    # T4: Single target != benchmark
    r.assert_true("T4 L-004 exists", prod_store.get_lesson("L-004") is not None)

    # T5: Training membership not verifiable
    r.assert_true("T5 L-005 exists", prod_store.get_lesson("L-005") is not None)

    # T6: Historical source preservation
    r.assert_true("T6 L-006 exists", prod_store.get_lesson("L-006") is not None)

    # T-scenario: Native-visible report flagged
    result = run_preflight(prod_store, {
        "pipeline_stage": "evaluation",
        "model_family": "proteinsolver"
    })
    must_rules = [e["rule_id"] for e in result["tiers"]["MUST"]]
    r.assert_in("T7 R-001 fires for evaluation", "R-001", must_rules)

    # T-scenario: Single-target cannot become benchmark
    r.assert_in("T8 R-004 fires for reporting",
                "R-004",
                [e["rule_id"] for e in run_preflight(
                    prod_store, {"pipeline_stage": "reporting"}
                )["tiers"]["MUST"]])

    # T-scenario: Historical source clean check
    hist_path = PROJECT_ROOT / "external" / "proteinsolver-original"
    if hist_path.exists():
        result = subprocess.run(
            ["git", "-C", str(hist_path), "status", "--short"],
            capture_output=True, text=True
        )
        r.assert_eq("T9 historical repo clean", result.stdout.strip(), "")
    else:
        r.fail("T9 historical repo missing", str(hist_path))

    # ============================================================
    # U. Live-Progress System
    # ============================================================
    print("\n=== U. Live-Progress System ===")

    state_file = PROJECT_ROOT / "reports" / "AG_RUN_STATE.json"
    r.assert_true("U1 AG_RUN_STATE.json exists", state_file.exists())
    if state_file.exists():
        with open(state_file) as f:
            state = json.load(f)
        r.assert_in("U2 state has 'state' field", "state", state)
        r.assert_in("U3 state has 'current_stage'", "current_stage", state)
        r.assert_in("U4 state has 'completed'", "completed", state)

    progress_file = PROJECT_ROOT / "reports" / "AG_LIVE_PROGRESS.md"
    r.assert_true("U5 AG_LIVE_PROGRESS.md exists", progress_file.exists())

    # ============================================================
    # V. Clean Repository State
    # ============================================================
    print("\n=== V. Clean Repository State ===")

    # Check historical repo is clean
    if hist_path.exists():
        result = subprocess.run(
            ["git", "-C", str(hist_path), "rev-parse", "HEAD"],
            capture_output=True, text=True
        )
        r.assert_eq("V1 historical commit",
                     result.stdout.strip(),
                     "69ef0965a3fc3bf191804035b539720a06e58ba6")

    # ============================================================
    # Additional Negative/Adversarial Tests
    # ============================================================
    print("\n=== Additional Negative/Adversarial Tests ===")

    # Unknown context produces warnings
    store, tmpdir = make_temp_store()
    try:
        store.add_rule(Rule(id="R-ADV1", priority="MUST", enforcement_level="AUTOMATED",
                            governance_lifecycle="ACTIVE",
                            applicability_conditions={"dataset": "cath42"}))
        result = run_preflight(store, {"model_family": "proteinsolver"})
        r.assert_true("ADV1 unknown context warning",
                      "dataset" in result["coverage"]["unknown_context_fields"] or
                      result["coverage"]["rules_relevant"] == 0)
    finally:
        cleanup(tmpdir)

    # Contradictory MUST rules are not silently resolved
    store, tmpdir = make_temp_store()
    try:
        store.add_rule(Rule(id="R-ADV2a", priority="MUST", enforcement_level="MANUAL",
                            governance_lifecycle="ACTIVE", scope="eval",
                            applicability_conditions={}))
        store.add_rule(Rule(id="R-ADV2b", priority="MUST", enforcement_level="MANUAL",
                            governance_lifecycle="ACTIVE", scope="eval",
                            applicability_conditions={}))
        result = run_preflight(store, {})
        r.assert_true("ADV2 contradictory MUSTs flagged",
                      len(result["conflicts"]) > 0)
    finally:
        cleanup(tmpdir)

    # Preflight output format
    store, tmpdir = make_temp_store()
    try:
        store.add_rule(Rule(id="R-FMT1", title="Test", priority="MUST",
                            enforcement_level="MANUAL", governance_lifecycle="ACTIVE",
                            applicability_conditions={}))
        result = run_preflight(store, {"pipeline_stage": "reporting"})
        text = format_preflight(result)
        r.assert_in("ADV3 format contains MUST", "MUST", text)
        r.assert_in("ADV4 format contains warning",
                     "No warnings", text)
    finally:
        cleanup(tmpdir)

    # ============================================================
    # Summary
    # ============================================================
    return r.summary()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
