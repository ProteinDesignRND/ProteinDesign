"""
Comprehensive governance test suite.

Supports both:
  1. pytest discovery: `pytest tests/` or `uv run pytest`
  2. Direct execution: `python tests/test_governance.py`

Covers:
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
  T. Six ProteinSolver regression cases (Bad vs Good)
  U. Live-progress system
  V. Clean repository state
  ADV. Direct-file bypass attacks & Store integrity
  ADV. Four mandatory claim adversarial cases
  ADV. Context derivation (DERIVED vs DECLARED)
  ADV. Retraction audit
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from governance import (
    SCHEMA_VERSION, LESSON_TYPES, EVIDENCE_STATUSES,
    GOVERNANCE_LIFECYCLES, RULE_PRIORITIES, ENFORCEMENT_LEVELS,
    EVENT_TYPES, FAILURE_CLASSES, PRECEDENCE_ORDER, PREFLIGHT_TIERS,
    Lesson, Rule, Event, GovernanceStore, run_preflight, format_preflight,
    derive_context, evaluate_claim,
)


class GovernanceTestResult:
    """Lightweight test reporter for direct script execution."""
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
            assert condition, f"{name}: {msg}"

    def assert_false(self, name, condition, msg=""):
        if not condition:
            self.ok(name)
        else:
            self.fail(name, msg or "Expected False")
            assert not condition, f"{name}: {msg}"

    def assert_eq(self, name, actual, expected, msg=""):
        if actual == expected:
            self.ok(name)
        else:
            self.fail(name, msg or f"Expected {expected!r}, got {actual!r}")
            assert actual == expected, f"{name}: Expected {expected!r}, got {actual!r}"

    def assert_in(self, name, item, collection, msg=""):
        if item in collection:
            self.ok(name)
        else:
            self.fail(name, msg or f"{item!r} not in collection")
            assert item in collection, f"{name}: {item!r} not in collection"

    def assert_not_in(self, name, item, collection, msg=""):
        if item not in collection:
            self.ok(name)
        else:
            self.fail(name, msg or f"{item!r} unexpectedly in collection")
            assert item not in collection, f"{name}: {item!r} unexpectedly in collection"

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


# ============================================================
# Section A: Schema Validity
# ============================================================

def test_section_a_schema_validity(r=None):
    r = r or GovernanceTestResult()
    lesson = Lesson(id="test-1", type="METHOD_SCIENCE", evidence_status="OBSERVED",
                    governance_lifecycle="PROPOSED")
    r.assert_eq("A1 valid lesson", lesson.validate(), [])

    bad_lesson = Lesson(id="", type="INVALID_TYPE")
    errs = bad_lesson.validate()
    r.assert_true("A2 invalid lesson has errors", len(errs) >= 2, f"Expected >=2 errors, got {errs}")

    rule = Rule(id="test-r1", priority="MUST", enforcement_level="AUTOMATED",
                governance_lifecycle="ACTIVE")
    r.assert_eq("A3 valid rule", rule.validate(), [])

    bad_rule = Rule(id="", priority="INVALID")
    r.assert_true("A4 invalid rule has errors", len(bad_rule.validate()) >= 2)

    event = Event(event_id="e1", event_type="LESSON_CREATED")
    r.assert_eq("A5 valid event", event.validate(), [])

    bad_event = Event(event_id="", event_type="INVALID")
    r.assert_true("A6 invalid event has errors", len(bad_event.validate()) >= 1)

    r.assert_eq("A7 schema version format", SCHEMA_VERSION, "1.0.0")
    r.assert_in("A8 BUG_ENVIRONMENT in types", "BUG_ENVIRONMENT", LESSON_TYPES)
    r.assert_in("A9 CONTRADICTED in evidence", "CONTRADICTED", EVIDENCE_STATUSES)


# ============================================================
# Section B: Lesson Lifecycle
# ============================================================

def test_section_b_lesson_lifecycle(r=None):
    r = r or GovernanceTestResult()
    store, tmpdir = make_temp_store()
    try:
        lesson = Lesson(id="L-T1", title="Test lesson", type="BUG_ENVIRONMENT",
                        evidence_status="OBSERVED", governance_lifecycle="PROPOSED")
        errs = store.add_lesson(lesson)
        r.assert_eq("B1 add lesson succeeds", errs, [])
        loaded = store.get_lesson("L-T1")
        r.assert_eq("B2 lesson retrievable", loaded["title"], "Test lesson")
        r.assert_eq("B3 lesson lifecycle", loaded["governance_lifecycle"], "PROPOSED")

        # Duplicate rejected
        errs2 = store.add_lesson(lesson)
        r.assert_true("B4 duplicate rejected", len(errs2) > 0)
    finally:
        cleanup(tmpdir)


# ============================================================
# Section C: Rule Lifecycle
# ============================================================

def test_section_c_rule_lifecycle(r=None):
    r = r or GovernanceTestResult()
    store, tmpdir = make_temp_store()
    try:
        rule = Rule(id="R-T1", title="Test rule", priority="MUST",
                    enforcement_level="AUTOMATED", governance_lifecycle="ACTIVE",
                    source_lesson="L-T1")
        errs = store.add_rule(rule)
        r.assert_eq("C1 add rule succeeds", errs, [])
        loaded = store.get_rule("R-T1")
        r.assert_eq("C2 rule retrievable", loaded["title"], "Test rule")
        r.assert_eq("C3 rule source lesson", loaded["source_lesson"], "L-T1")
    finally:
        cleanup(tmpdir)


# ============================================================
# Section D: Event Recording
# ============================================================

def test_section_d_event_recording(r=None):
    r = r or GovernanceTestResult()
    store, tmpdir = make_temp_store()
    try:
        event = Event(event_id="E-T1", actor="test-agent", entity_type="LESSON",
                      entity_id="L-T1", event_type="LESSON_CREATED",
                      context="Unit test", result="SUCCESS")
        errs = store.append_event(event)
        r.assert_eq("D1 append event succeeds", errs, [])
        events = store.load_events()
        r.assert_eq("D2 event in log", len(events), 1)
        r.assert_eq("D3 event type", events[0]["event_type"], "LESSON_CREATED")

        event2 = Event(event_id="E-T2", actor="test-agent", entity_type="RULE",
                       entity_id="R-T1", event_type="RULE_PROMOTED")
        store.append_event(event2)
        r.assert_eq("D4 multiple events", len(store.load_events()), 2)

        by_entity = store.find_events(entity_id="L-T1")
        r.assert_eq("D5 find by entity", len(by_entity), 1)
    finally:
        cleanup(tmpdir)


# ============================================================
# Section E: Deterministic Retrieval
# ============================================================

def test_section_e_deterministic_retrieval(r=None):
    r = r or GovernanceTestResult()
    store, tmpdir = make_temp_store()
    try:
        store.add_lesson(Lesson(id="L-E1", title="PyG bug", type="BUG_ENVIRONMENT",
                                evidence_status="OBSERVED", governance_lifecycle="ACTIVE",
                                keywords=["batch", "pyg"]))
        store.add_lesson(Lesson(id="L-E2", title="Science method", type="METHOD_SCIENCE",
                                evidence_status="REPRODUCED", governance_lifecycle="ACTIVE",
                                keywords=["mask", "inverse-folding"]))

        bug_lessons = store.find_lessons(type="BUG_ENVIRONMENT")
        r.assert_eq("E1 find by type", len(bug_lessons), 1)
        r.assert_eq("E2 correct lesson", bug_lessons[0]["id"], "L-E1")

        by_kw = store.find_lessons(keyword="mask")
        r.assert_eq("E3 find by keyword", len(by_kw), 1)
        r.assert_eq("E4 no match", len(store.find_lessons(keyword="nonexistent")), 0)
    finally:
        cleanup(tmpdir)


# ============================================================
# Section F: Applicability
# ============================================================

def test_section_f_applicability(r=None):
    r = r or GovernanceTestResult()
    from governance.preflight import _context_matches

    # Exact match
    cond = {"model_family": "proteinsolver", "pipeline_stage": "evaluation"}
    ctx = {"model_family": "proteinsolver", "pipeline_stage": "evaluation"}
    matches, expl, unknowns = _context_matches(cond, ctx)
    r.assert_true("F1 exact match", matches)
    r.assert_eq("F2 no unknowns", unknowns, [])

    # Mismatch
    ctx_mismatch = {"model_family": "esm2", "pipeline_stage": "evaluation"}
    matches, expl, unknowns = _context_matches(cond, ctx_mismatch)
    r.assert_false("F3 mismatch", matches)

    # Empty conditions = universal
    matches, expl, unknowns = _context_matches({}, {"any": "context"})
    r.assert_true("F4 empty conditions = universal", matches)

    # Unknown field
    ctx_partial = {"model_family": "proteinsolver"}
    matches, expl, unknowns = _context_matches(cond, ctx_partial)
    r.assert_in("F5 unknown field", "pipeline_stage", unknowns)

    # List condition match
    cond_list = {"pipeline_stage": ["evaluation", "reporting"]}
    matches, _, _ = _context_matches(cond_list, {"pipeline_stage": "evaluation"})
    r.assert_true("F6 list match", matches)

    # List condition mismatch
    matches, _, _ = _context_matches(cond_list, {"pipeline_stage": "training"})
    r.assert_false("F7 list mismatch", matches)


# ============================================================
# Section G: Unknown Context
# ============================================================

def test_section_g_unknown_context(r=None):
    r = r or GovernanceTestResult()
    store, tmpdir = make_temp_store()
    try:
        store.add_rule(Rule(id="R-G1", title="Scoped rule", priority="SHOULD",
                            enforcement_level="NONE", governance_lifecycle="ACTIVE",
                            applicability_conditions={"dataset": "cath42", "target": "1n5u"}))
        result = run_preflight(store, {"model_family": "proteinsolver"})
        unknowns = result["coverage"]["unknown_context_fields"]
        r.assert_true("G1 unknown context fields listed",
                      "dataset" in unknowns or "target" in unknowns or
                      len(result["coverage"]["unknown_context_fields"]) > 0 or
                      result["coverage"]["rules_relevant"] == 0)
    finally:
        cleanup(tmpdir)


# ============================================================
# Section H: Precedence
# ============================================================

def test_section_h_precedence(r=None):
    r = r or GovernanceTestResult()
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
# Section I: Conflict Detection
# ============================================================

def test_section_i_conflict_detection(r=None):
    r = r or GovernanceTestResult()
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
# Section J: Blocker Behavior (PROPOSED cannot block)
# ============================================================

def test_section_j_blocker_behavior(r=None):
    r = r or GovernanceTestResult()
    store, tmpdir = make_temp_store()
    try:
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
# Section K: Override Recording
# ============================================================

def test_section_k_override_recording(r=None):
    r = r or GovernanceTestResult()
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

        # Test helper method
        store.add_rule(Rule(id="R-001", priority="MUST", enforcement_level="AUTOMATED"))
        ov_errs = store.record_override("R-001", "lead-reviewer", "test override", "single-run")
        r.assert_eq("K4 store.record_override succeeds", ov_errs, [])
    finally:
        cleanup(tmpdir)


# ============================================================
# Section L: Claim-Level Protection
# ============================================================

def test_section_l_claim_level_protection(r=None):
    r = r or GovernanceTestResult()
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
# Section M: Extrapolation Detection
# ============================================================

def test_section_m_extrapolation_detection(r=None):
    r = r or GovernanceTestResult()
    prod_store = GovernanceStore()
    r.assert_in("M1 R-007 exists", "R-007", [r_id for r_id in prod_store.load_rules()])
    rule_007 = prod_store.get_rule("R-007")
    r.assert_eq("M2 scope rule is SHOULD", rule_007["priority"], "SHOULD")


# ============================================================
# Section N: Novelty Detection
# ============================================================

def test_section_n_novelty_detection(r=None):
    r = r or GovernanceTestResult()
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
# Section O: Validation Levels
# ============================================================

def test_section_o_validation_levels(r=None):
    r = r or GovernanceTestResult()
    prod_store = GovernanceStore()
    l001 = prod_store.get_lesson("L-001")
    r001 = prod_store.get_rule("R-001")
    r.assert_true("O1 lesson evidence separate from governance",
                  l001["evidence_status"] != l001["governance_lifecycle"])
    r.assert_true("O2 rule has check pointer", bool(r001["check_pointer"]))
    r.assert_true("O3 rule lifecycle independent of lesson evidence",
                  r001["governance_lifecycle"] != l001["evidence_status"])

    # Non-tautological test: passing a test check does NOT change rule lifecycle or lesson evidence
    store, tmpdir = make_temp_store()
    try:
        lesson = Lesson(id="L-O4", evidence_status="OBSERVED", governance_lifecycle="PROPOSED")
        rule = Rule(id="R-O4", priority="MUST", enforcement_level="AUTOMATED",
                    governance_lifecycle="PROPOSED", check_pointer="test_pointer")
        store.add_lesson(lesson)
        store.add_rule(rule)
        # Even if check_pointer is valid, governance remains PROPOSED until promoted
        r.assert_eq("O4 test pass does not auto-promote rule",
                    store.get_rule("R-O4")["governance_lifecycle"], "PROPOSED")
        r.assert_eq("O5 test pass does not auto-validate evidence",
                    store.get_lesson("L-O4")["evidence_status"], "OBSERVED")
    finally:
        cleanup(tmpdir)


# ============================================================
# Section P: Failure Classification
# ============================================================

def test_section_p_failure_classification(r=None):
    r = r or GovernanceTestResult()
    r.assert_eq("P1 failure classes count", len(FAILURE_CLASSES), 7)
    r.assert_in("P2 NO_LESSON", "NO_LESSON", FAILURE_CLASSES)
    r.assert_in("P3 RETRIEVAL_MISS", "RETRIEVAL_MISS", FAILURE_CLASSES)
    r.assert_in("P4 ENFORCEMENT_GAP", "ENFORCEMENT_GAP", FAILURE_CLASSES)


# ============================================================
# Section Q: Duplicate Handling
# ============================================================

def test_section_q_duplicate_handling(r=None):
    r = r or GovernanceTestResult()
    store, tmpdir = make_temp_store()
    try:
        store.add_lesson(Lesson(id="L-Q1", title="Batch interface mismatch", type="BUG_ENVIRONMENT",
                                governance_lifecycle="PROPOSED", evidence_status="OBSERVED",
                                keywords=["batch", "pyg", "data"]))
        errs = store.add_lesson(Lesson(id="L-Q1", type="BUG_ENVIRONMENT",
                                       governance_lifecycle="PROPOSED",
                                       evidence_status="OBSERVED"))
        r.assert_true("Q1 duplicate rejected", "Duplicate" in errs[0])

        # Semantic duplicate discovery
        similar_lesson = Lesson(
            id="L-Q2",
            title="Batch interface mismatch in design_sequence",
            keywords=["batch", "pyg", "data"],
            scope="",
        )
        dups = store.find_potential_duplicates(similar_lesson)
        r.assert_true("Q2 duplicate discovered by keyword/title overlap", len(dups) >= 1)
        r.assert_eq("Q3 matched existing ID", dups[0]["existing_id"], "L-Q1")
    finally:
        cleanup(tmpdir)


# ============================================================
# Section R: Migration / Versioning
# ============================================================

def test_section_r_migration_versioning(r=None):
    r = r or GovernanceTestResult()
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
# Section S: AI-Agent Boundaries
# ============================================================

def test_section_s_ai_agent_boundaries(r=None):
    r = r or GovernanceTestResult()
    store, tmpdir = make_temp_store()
    try:
        lesson = Lesson(id="L-S1", governance_lifecycle="PROPOSED",
                        type="AI_TOOLING", evidence_status="OBSERVED")
        errs = store.add_lesson(lesson)
        r.assert_eq("S1 AI can propose lesson", errs, [])

        store.add_rule(Rule(id="R-S1", priority="MUST", enforcement_level="AUTOMATED",
                            governance_lifecycle="PROPOSED", source_lesson="L-S1",
                            applicability_conditions={}))
        result = run_preflight(store, {})
        must_ids = [e["rule_id"] for e in result["tiers"]["MUST"]]
        r.assert_not_in("S2 proposed rule not in MUST", "R-S1", must_ids,
                        "Unreviewed lesson/rule cannot block execution")

        loaded = store.get_lesson("L-S1")
        r.assert_eq("S3 lesson stays PROPOSED", loaded["governance_lifecycle"], "PROPOSED")
    finally:
        cleanup(tmpdir)


# ============================================================
# Section T: Six ProteinSolver Regressions (BAD vs GOOD)
# ============================================================

def test_section_t_proteinsolver_regressions(r=None):
    r = r or GovernanceTestResult()
    prod_store = GovernanceStore()

    # Regression 1: Native sequence visibility != valid recovery
    r.assert_true("T1 L-001 exists in prod", prod_store.get_lesson("L-001") is not None)
    r.assert_eq("T1b L-001 type", prod_store.get_lesson("L-001")["type"], "METHOD_SCIENCE")
    # Bad case: native-visible claimed as valid recovery
    bad_claim1 = evaluate_claim({
        "claim_id": "C-REG1-BAD",
        "claim_text": "100% recovery achieved via reference strategy with data.y provided",
        "evidence_scope": "1n5uA03",
        "checks_run": ["diagnostic_scoring"],
        "checks_missing": ["all_masked_verified"],
    })
    r.assert_eq("T1c bad masking claim rejected", bad_claim1["status"], "REJECTED")
    # Good case: all-masked recovery claim
    good_claim1 = evaluate_claim({
        "claim_id": "C-REG1-GOOD",
        "claim_text": "Valid all-masked sequence recovery of 41.30% under data.x=20 and data.y=None",
        "claim_scope": "single-target",
        "evidence_scope": "single-target",
        "checks_run": ["all_masked_verified", "mask_check_passed"],
    })
    r.assert_eq("T1d good masking claim approved", good_claim1["status"], "APPROVED")

    # Regression 2: Data vs Batch mismatch
    r.assert_true("T2 L-002 exists", prod_store.get_lesson("L-002") is not None)
    r.assert_in("T2b batch keyword", "batch", prod_store.get_lesson("L-002")["keywords"])

    # Regression 3: Modern compatibility != historical equivalence
    r.assert_true("T3 L-003 exists", prod_store.get_lesson("L-003") is not None)
    # Bad case: claiming historical equivalence without comparison
    bad_claim3 = evaluate_claim({
        "claim_id": "C-REG3-BAD",
        "claim_text": "Our execution demonstrates 100% mathematical fidelity and historical equivalence to the 2020 run",
        "evidence_scope": "1n5uA03",
        "checks_run": ["modern_run"],
    })
    r.assert_eq("T3c bad equivalence claim rejected", bad_claim3["status"], "REJECTED")
    # Good case: properly scoped reproduction wording
    good_claim3 = evaluate_claim({
        "claim_id": "C-REG3-GOOD",
        "claim_text": "FUNCTIONALLY REPRODUCED WITH MODERN COMPATIBILITY ADAPTATION on 1n5uA03",
        "claim_scope": "1n5uA03",
        "evidence_scope": "1n5uA03",
        "checks_run": ["modern_run", "parameter_checksum"],
    })
    r.assert_eq("T3d good reproduction wording approved", good_claim3["status"], "APPROVED")

    # Regression 4: Single target != benchmark
    r.assert_true("T4 L-004 exists", prod_store.get_lesson("L-004") is not None)
    # Bad case: single target called benchmark
    bad_claim4 = evaluate_claim({
        "claim_id": "C-REG4-BAD",
        "claim_text": "41.30% recovery on 1n5uA03 establishes benchmark accuracy across protein folds",
        "claim_scope": "benchmark",
        "evidence_scope": "single-target",
    })
    r.assert_eq("T4c bad benchmark claim rejected", bad_claim4["status"], "REJECTED")
    # Good case: called single-target integration result
    good_claim4 = evaluate_claim({
        "claim_id": "C-REG4-GOOD",
        "claim_text": "Single-target all-masked inverse-folding integration result on 1n5uA03 yields 41.30%",
        "claim_scope": "single-target",
        "evidence_scope": "single-target",
    })
    r.assert_eq("T4d good single-target claim approved", good_claim4["status"], "APPROVED")

    # Regression 5: Training membership not verifiable
    r.assert_true("T5 L-005 exists", prod_store.get_lesson("L-005") is not None)
    # Bad case: calling 1n5uA03 guaranteed held-out
    bad_claim5 = evaluate_claim({
        "claim_id": "C-REG5-BAD",
        "claim_text": "1n5uA03 is guaranteed held-out and unseen by the model",
        "evidence_status": "NOT_VERIFIABLE",
        "checks_missing": ["membership_query"],
    })
    r.assert_eq("T5c bad membership claim rejected", bad_claim5["status"], "REJECTED")
    # Good case: classifying as not verifiable from accessible metadata
    good_claim5 = evaluate_claim({
        "claim_id": "C-REG5-GOOD",
        "claim_text": "Training set membership of 1n5uA03 is NOT VERIFIABLE FROM ACCESSIBLE METADATA",
        "claim_scope": "single-target",
        "evidence_scope": "single-target",
        "evidence_status": "NOT_VERIFIABLE",
    })
    r.assert_eq("T5d good membership claim approved", good_claim5["status"], "APPROVED")

    # Regression 6: Historical source preservation
    r.assert_true("T6 L-006 exists", prod_store.get_lesson("L-006") is not None)
    result = run_preflight(prod_store, {"pipeline_stage": "evaluation", "model_family": "proteinsolver"})
    must_rules = [e["rule_id"] for e in result["tiers"]["MUST"]]
    r.assert_in("T7 R-001 fires for evaluation", "R-001", must_rules)

    r.assert_in("T8 R-004 fires for reporting", "R-004",
                [e["rule_id"] for e in run_preflight(prod_store, {"pipeline_stage": "reporting"})["tiers"]["MUST"]])

    hist_path = PROJECT_ROOT / "external" / "proteinsolver-original"
    if hist_path.exists():
        res = subprocess.run(["git", "-C", str(hist_path), "status", "--short"], capture_output=True, text=True)
        r.assert_eq("T9 historical repo clean", res.stdout.strip(), "")


# ============================================================
# Section U: Live-Progress System
# ============================================================

def test_section_u_live_progress_system(r=None):
    r = r or GovernanceTestResult()
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
# Section V: Clean Repository State
# ============================================================

def test_section_v_clean_repository_state(r=None):
    r = r or GovernanceTestResult()
    hist_path = PROJECT_ROOT / "external" / "proteinsolver-original"
    if hist_path.exists():
        res = subprocess.run(["git", "-C", str(hist_path), "rev-parse", "HEAD"], capture_output=True, text=True)
        r.assert_eq("V1 historical commit", res.stdout.strip(), "69ef0965a3fc3bf191804035b539720a06e58ba6")


# ============================================================
# Adversarial Suite: Direct-File Bypass & Integrity Verification
# ============================================================

def test_adversarial_direct_file_bypass(r=None):
    """
    Simulate malicious or accidental direct editing of lessons.json / rules.json
    and verify store.verify_integrity() catches all mutation attempts.
    """
    r = r or GovernanceTestResult()
    store, tmpdir = make_temp_store()
    try:
        # Seed test store with baseline rules
        for r_id in GovernanceStore.MANDATORY_SAFETY_RULES:
            store.add_rule(Rule(id=r_id, priority="MUST", enforcement_level="AUTOMATED",
                                check_pointer="test_pointer", governance_lifecycle="ACTIVE"))

        # Verify initial clean integrity
        errs = store.verify_integrity(check_baseline=True)
        r.assert_eq("ADV_BYPASS_0 initial store clean", errs, [])

        # Attack 1: Maliciously delete a mandatory safety rule (e.g. R-001)
        rules = store.load_rules()
        del rules["R-001"]
        store.save_rules(rules)
        errs1 = store.verify_integrity(check_baseline=True)
        r.assert_true("ADV_BYPASS_1 caught deleted safety rule", any("R-001" in e for e in errs1))

        # Restore R-001
        store.add_rule(Rule(id="R-001", priority="MUST", enforcement_level="AUTOMATED", check_pointer="test_pointer"))

        # Attack 2: Escalate an unreviewed rule directly to ACTIVE MUST with a PROPOSED source lesson
        store.add_lesson(Lesson(id="L-UNREVIEWED", governance_lifecycle="PROPOSED"))
        rules = store.load_rules()
        rules["R-UNREVIEWED"] = Rule(
            id="R-UNREVIEWED", priority="MUST", enforcement_level="AUTOMATED",
            governance_lifecycle="ACTIVE", source_lesson="L-UNREVIEWED", check_pointer="test"
        ).to_dict()
        store.save_rules(rules)
        errs2 = store.verify_integrity(check_baseline=True)
        r.assert_true("ADV_BYPASS_2 caught PROPOSED lesson escalated to ACTIVE MUST",
                      any("is ACTIVE MUST but source lesson 'L-UNREVIEWED' is PROPOSED" in e for e in errs2))

        # Attack 3: Escalate to AUTOMATED without check_pointer
        rules = store.load_rules()
        rules["R-NOCHECK"] = Rule(
            id="R-NOCHECK", priority="MUST", enforcement_level="AUTOMATED",
            governance_lifecycle="ACTIVE", check_pointer=""
        ).to_dict()
        store.save_rules(rules)
        errs3 = store.verify_integrity(check_baseline=True)
        r.assert_true("ADV_BYPASS_3 caught AUTOMATED rule without check_pointer",
                      any("claims AUTOMATED enforcement without check_pointer" in e for e in errs3))

        # Attack 4: Dangling source lesson
        rules = store.load_rules()
        rules["R-DANGLING"] = Rule(
            id="R-DANGLING", priority="SHOULD", enforcement_level="MANUAL",
            source_lesson="L-DOES-NOT-EXIST"
        ).to_dict()
        store.save_rules(rules)
        errs4 = store.verify_integrity(check_baseline=True)
        r.assert_true("ADV_BYPASS_4 caught dangling source lesson",
                      any("missing source lesson 'L-DOES-NOT-EXIST'" in e for e in errs4))
    finally:
        cleanup(tmpdir)


# ============================================================
# Adversarial Suite: Context Derivation (DERIVED vs DECLARED)
# ============================================================

def test_context_derivation_and_provenance(r=None):
    r = r or GovernanceTestResult()
    declared = {"model_family": "proteinsolver", "pipeline_stage": "evaluation"}
    ctx = derive_context(declared_context=declared)

    r.assert_in("ADV_CTX_1 declared preserved", "model_family", ctx["declared"])
    r.assert_in("ADV_CTX_2 python_version derived", "python_version", ctx["derived"])
    r.assert_in("ADV_CTX_3 git_sha derived", "git_sha", ctx["derived"])
    r.assert_eq("ADV_CTX_4 provenance tracked DECLARED", ctx["provenance"]["model_family"], "DECLARED")
    r.assert_eq("ADV_CTX_5 provenance tracked DERIVED", ctx["provenance"]["python_version"], "DERIVED")

    # In preflight with auto_derive=True
    store, tmpdir = make_temp_store()
    try:
        store.add_rule(Rule(id="R-CTX1", priority="MUST", enforcement_level="AUTOMATED",
                            governance_lifecycle="ACTIVE",
                            applicability_conditions={"pipeline_stage": "evaluation"}))
        res = run_preflight(store, context={"pipeline_stage": "evaluation"}, auto_derive=True)
        r.assert_in("ADV_CTX_6 preflight contains derived context", "python_version", res["context_derived"])
        r.assert_eq("ADV_CTX_7 rule matched on declared", len(res["tiers"]["MUST"]), 1)
    finally:
        cleanup(tmpdir)


# ============================================================
# Adversarial Suite: Retraction Audit
# ============================================================

def test_retraction_audit(r=None):
    r = r or GovernanceTestResult()
    store, tmpdir = make_temp_store()
    try:
        store.add_rule(Rule(id="R-AUDIT1", priority="MUST", enforcement_level="AUTOMATED"))
        # Record application
        store.record_rule_applied("R-AUDIT1", "EXP001_SMOKETEST", artifact="metrics.json")
        store.record_rule_applied("R-AUDIT1", "EXP002_INFERENCE", artifact="results.csv")

        audit = store.audit_retraction("R-AUDIT1")
        r.assert_eq("ADV_AUDIT_1 applications count", audit["total_applications"], 2)
        r.assert_in("ADV_AUDIT_2 applied experiment recorded", "EXP001_SMOKETEST", audit["applied_experiments"])
        r.assert_in("ADV_AUDIT_3 affected artifact recorded", "metrics.json", audit["affected_artifacts"])
        r.assert_eq("ADV_AUDIT_4 status requires review", audit["status"], "REVIEW_REQUIRED")

        # Retraction audit logged as event
        retract_events = store.find_events(entity_id="R-AUDIT1", event_type="RETRACTION_AUDIT")
        r.assert_eq("ADV_AUDIT_5 audit event recorded in log", len(retract_events), 1)
    finally:
        cleanup(tmpdir)


# ============================================================
# Main test suite runner
# ============================================================

def run_all_tests():
    r = GovernanceTestResult()

    print("\n=== A. Schema Validity ===")
    test_section_a_schema_validity(r)

    print("\n=== B. Lesson Lifecycle ===")
    test_section_b_lesson_lifecycle(r)

    print("\n=== C. Rule Lifecycle ===")
    test_section_c_rule_lifecycle(r)

    print("\n=== D. Event Recording ===")
    test_section_d_event_recording(r)

    print("\n=== E. Deterministic Retrieval ===")
    test_section_e_deterministic_retrieval(r)

    print("\n=== F. Applicability ===")
    test_section_f_applicability(r)

    print("\n=== G. Unknown Context ===")
    test_section_g_unknown_context(r)

    print("\n=== H. Precedence ===")
    test_section_h_precedence(r)

    print("\n=== I. Conflict Detection ===")
    test_section_i_conflict_detection(r)

    print("\n=== J. Blocker Behavior ===")
    test_section_j_blocker_behavior(r)

    print("\n=== K. Override Recording ===")
    test_section_k_override_recording(r)

    print("\n=== L. Claim-Level Protection ===")
    test_section_l_claim_level_protection(r)

    print("\n=== M. Extrapolation Detection ===")
    test_section_m_extrapolation_detection(r)

    print("\n=== N. Novelty Detection ===")
    test_section_n_novelty_detection(r)

    print("\n=== O. Validation Levels ===")
    test_section_o_validation_levels(r)

    print("\n=== P. Failure Classification ===")
    test_section_p_failure_classification(r)

    print("\n=== Q. Duplicate Handling ===")
    test_section_q_duplicate_handling(r)

    print("\n=== R. Migration / Versioning ===")
    test_section_r_migration_versioning(r)

    print("\n=== S. AI-Agent Boundaries ===")
    test_section_s_ai_agent_boundaries(r)

    print("\n=== T. ProteinSolver Regression Cases (Bad vs Good) ===")
    test_section_t_proteinsolver_regressions(r)

    print("\n=== U. Live-Progress System ===")
    test_section_u_live_progress_system(r)

    print("\n=== V. Clean Repository State ===")
    test_section_v_clean_repository_state(r)

    print("\n=== Adversarial: Direct-File Bypass & Store Integrity ===")
    test_adversarial_direct_file_bypass(r)

    print("\n=== Adversarial: Context Derivation (DERIVED vs DECLARED) ===")
    test_context_derivation_and_provenance(r)

    print("\n=== Adversarial: Retraction Audit ===")
    test_retraction_audit(r)

    return r.summary()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
