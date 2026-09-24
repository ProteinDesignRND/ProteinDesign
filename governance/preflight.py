"""
Deterministic preflight/retrieval system.

Matches governance rules against explicit context.
No embeddings, no vector DB, no semantic RAG.
Every match is explainable.
"""

from typing import Optional
from governance import PRECEDENCE_ORDER, PREFLIGHT_TIERS
from governance.store import GovernanceStore


def _context_matches(rule_conditions: dict, context: dict) -> tuple:
    """
    Check if context satisfies rule applicability conditions.

    Returns (matches: bool, explanation: str, unknown_fields: list).
    """
    if not rule_conditions:
        return True, "No conditions (applies universally)", []

    unknown_fields = []
    matched_fields = []
    mismatched_fields = []

    for key, required_value in rule_conditions.items():
        if key not in context:
            unknown_fields.append(key)
            continue
        actual = context[key]
        if isinstance(required_value, list):
            if actual in required_value:
                matched_fields.append(f"{key}={actual}")
            else:
                mismatched_fields.append(f"{key}: expected one of {required_value}, got {actual}")
        elif actual == required_value:
            matched_fields.append(f"{key}={actual}")
        else:
            mismatched_fields.append(f"{key}: expected {required_value}, got {actual}")

    if mismatched_fields:
        return False, f"Mismatched: {'; '.join(mismatched_fields)}", unknown_fields

    if matched_fields or not unknown_fields:
        explanation = f"Matched: {'; '.join(matched_fields)}" if matched_fields else "Universal"
        return True, explanation, unknown_fields

    # All conditions were unknown
    return False, f"All conditions unknown: {unknown_fields}", unknown_fields


def _precedence_rank(scope: str) -> int:
    """Lower number = higher precedence."""
    scope_map = {
        "integrity": 0,
        "project-wide": 1,
        "subsystem": 2,
        "task": 3,
        "informal": 4,
    }
    for prefix, rank in scope_map.items():
        if scope.lower().startswith(prefix):
            return rank
    return 99


def run_preflight(
    store: GovernanceStore,
    context: Optional[dict] = None,
    auto_derive: bool = False,
    check_integrity: bool = False,
) -> dict:
    """
    Run deterministic preflight check.

    Args:
        store: GovernanceStore instance.
        context: Dict of declared context fields (model_family, pipeline_stage, etc.)
        auto_derive: If True, safely derive git and runtime environment context.
        check_integrity: If True, run store integrity check for direct-mutation bypass.

    Returns:
        Dict with tiers (MUST, SHOULD, FYI), coverage summary,
        conflicts, novel conditions, context provenance, and integrity violations.
    """
    declared_context = dict(context or {})
    derived_context = {}
    context_provenance = {}

    if auto_derive:
        from governance.context import derive_context
        ctx_data = derive_context(declared_context=declared_context)
        derived_context = ctx_data["derived"]
        effective_context = ctx_data["effective"]
        context_provenance = ctx_data["provenance"]
    else:
        effective_context = declared_context
        for k in declared_context:
            context_provenance[k] = "DECLARED"

    integrity_violations = []
    if check_integrity:
        integrity_violations = store.verify_integrity(check_baseline=False)

    rules = store.load_rules()
    lessons = store.load_lessons()

    result = {
        "tiers": {"MUST": [], "SHOULD": [], "FYI": []},
        "coverage": {
            "rules_evaluated": 0,
            "rules_relevant": 0,
            "unknown_context_fields": set(),
            "unreviewed_matches": 0,
            "unenforced_relevant": 0,
            "novel_conditions": [],
        },
        "conflicts": [],
        "integrity_violations": integrity_violations,
        "context_provided": effective_context,
        "context_declared": declared_context,
        "context_derived": derived_context,
        "context_provenance": context_provenance,
    }

    # Process rules
    active_must_rules = []
    for rule_id, rule in rules.items():
        result["coverage"]["rules_evaluated"] += 1

        if rule.get("governance_lifecycle") not in ("ACTIVE", "PROPOSED"):
            continue

        matches, explanation, unknowns = _context_matches(
            rule.get("applicability_conditions", {}), context
        )
        result["coverage"]["unknown_context_fields"].update(unknowns)

        if not matches:
            continue

        result["coverage"]["rules_relevant"] += 1

        if rule.get("governance_lifecycle") == "PROPOSED":
            result["coverage"]["unreviewed_matches"] += 1

        if rule.get("enforcement_level") == "NONE":
            result["coverage"]["unenforced_relevant"] += 1

        tier = rule.get("priority", "SHOULD")
        if tier not in PREFLIGHT_TIERS:
            tier = "FYI"

        # Proposed rules can only be FYI
        if rule.get("governance_lifecycle") == "PROPOSED":
            tier = "FYI"

        entry = {
            "rule_id": rule_id,
            "title": rule.get("title", ""),
            "description": rule.get("description", ""),
            "priority": rule.get("priority", ""),
            "enforcement": rule.get("enforcement_level", ""),
            "lifecycle": rule.get("governance_lifecycle", ""),
            "match_explanation": explanation,
            "unknown_fields": unknowns,
            "check_pointer": rule.get("check_pointer", ""),
            "source_lesson": rule.get("source_lesson", ""),
        }

        result["tiers"][tier].append(entry)

        if tier == "MUST" and rule.get("governance_lifecycle") == "ACTIVE":
            active_must_rules.append(entry)

    # Detect MUST-MUST conflicts (narrow/task/subsystem scope with multiple competing MUST rules)
    must_by_scope = {}
    for r in active_must_rules:
        scope = rules.get(r["rule_id"], {}).get("scope", "")
        # Global project-wide and integrity rules coexist as complementary standards
        if scope.lower() in ("project-wide", "integrity", "integrity_safety", "universal"):
            continue
        must_by_scope.setdefault(scope, []).append(r)

    for scope, scope_rules in must_by_scope.items():
        if len(scope_rules) > 1:
            ids = [r["rule_id"] for r in scope_rules]
            result["conflicts"].append({
                "type": "MULTIPLE_MUST_SAME_SCOPE",
                "scope": scope,
                "rule_ids": ids,
                "resolution": "HUMAN_REVIEW_REQUIRED",
            })

    # Add relevant FYI lessons (PROPOSED/ACTIVE that matched context keywords)
    context_keywords = set()
    for v in context.values():
        if isinstance(v, str):
            context_keywords.add(v.lower())

    for lesson_id, lesson in lessons.items():
        lesson_keywords = {k.lower() for k in lesson.get("keywords", [])}
        overlap = context_keywords & lesson_keywords
        if overlap and lesson.get("governance_lifecycle") in ("PROPOSED", "ACTIVE"):
            # Check if already covered by a rule
            covered_by_rule = any(
                r.get("source_lesson") == lesson_id
                for tier_entries in result["tiers"].values()
                for r in tier_entries
            )
            if not covered_by_rule:
                result["tiers"]["FYI"].append({
                    "lesson_id": lesson_id,
                    "title": lesson.get("title", ""),
                    "lesson": lesson.get("lesson", ""),
                    "match_explanation": f"Keyword match: {overlap}",
                    "lifecycle": lesson.get("governance_lifecycle", ""),
                })

    # Novel condition detection
    all_known_conditions = set()
    for rule in rules.values():
        for key, val in rule.get("applicability_conditions", {}).items():
            if isinstance(val, list):
                for v in val:
                    all_known_conditions.add((key, str(v)))
            else:
                all_known_conditions.add((key, str(val)))

    for key, val in context.items():
        if not any(k == key for k, v in all_known_conditions):
            result["coverage"]["novel_conditions"].append({
                "field": key,
                "value": val,
                "status": "NOVEL_CONTEXT_AXIS",
                "action": "WARNING: No rules address this context dimension",
            })
        elif (key, str(val)) not in all_known_conditions:
            result["coverage"]["novel_conditions"].append({
                "field": key,
                "value": val,
                "status": "NOVEL_VALUE",
                "action": "WARNING: Known axis but unseen value",
            })

    # Convert set to list for JSON serialization
    result["coverage"]["unknown_context_fields"] = list(
        result["coverage"]["unknown_context_fields"]
    )

    # Sort tiers by precedence
    for tier in result["tiers"]:
        result["tiers"][tier].sort(
            key=lambda x: _precedence_rank(
                store.load_rules().get(x.get("rule_id", ""), {}).get("scope", "")
            )
        )

    return result


def format_preflight(result: dict) -> str:
    """Format preflight result as human-readable text."""
    lines = ["=" * 60, "PREFLIGHT CHECK RESULTS", "=" * 60, ""]

    # Context
    lines.append("Context (Effective):")
    for k, v in result.get("context_provided", {}).items():
        prov = result.get("context_provenance", {}).get(k, "UNKNOWN")
        lines.append(f"  [{prov}] {k}: {v}")
    lines.append("")

    # Integrity Violations (Critical)
    violations = result.get("integrity_violations", [])
    if violations:
        lines.append("--- CRITICAL INTEGRITY VIOLATIONS (DIRECT BYPASS DETECTED) ---")
        for v in violations:
            lines.append(f"  [X] {v}")
        lines.append("ACTION REQUIRED: Direct-file mutation detected! Restore store integrity.")
        lines.append("")

    # Tiers
    for tier in ["MUST", "SHOULD", "FYI"]:
        entries = result["tiers"].get(tier, [])
        lines.append(f"--- {tier} ({len(entries)}) ---")
        if not entries:
            lines.append("  (none)")
        for entry in entries:
            eid = entry.get("rule_id", entry.get("lesson_id", "?"))
            title = entry.get("title", "")
            match = entry.get("match_explanation", "")
            lines.append(f"  [{eid}] {title}")
            lines.append(f"    Match: {match}")
            if entry.get("unknown_fields"):
                lines.append(f"    Unknown context: {entry['unknown_fields']}")
            if entry.get("check_pointer"):
                lines.append(f"    Check: {entry['check_pointer']}")
        lines.append("")

    # Coverage
    cov = result.get("coverage", {})
    lines.append("--- COVERAGE ---")
    lines.append(f"  Rules evaluated: {cov.get('rules_evaluated', 0)}")
    lines.append(f"  Rules relevant: {cov.get('rules_relevant', 0)}")
    lines.append(f"  Unknown context fields: {cov.get('unknown_context_fields', [])}")
    lines.append(f"  Unreviewed matches: {cov.get('unreviewed_matches', 0)}")
    lines.append(f"  Unenforced relevant: {cov.get('unenforced_relevant', 0)}")
    novel = cov.get("novel_conditions", [])
    if novel:
        lines.append(f"  Novel conditions: {len(novel)}")
        for n in novel:
            lines.append(f"    {n['field']}={n['value']}: {n['status']}")
    lines.append("")

    # Conflicts
    conflicts = result.get("conflicts", [])
    if conflicts:
        lines.append("--- CONFLICTS (HUMAN REVIEW REQUIRED) ---")
        for c in conflicts:
            lines.append(f"  {c['type']}: {c['rule_ids']} in scope '{c['scope']}'")
    else:
        lines.append("--- CONFLICTS ---")
        lines.append("  (none detected)")
    lines.append("")

    lines.append("NOTE: 'No warnings' does NOT mean 'safe'.")
    lines.append("      Check unknown context fields and novel conditions.")
    lines.append("=" * 60)

    return "\n".join(lines)
