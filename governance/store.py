"""
Governance Store: file-based persistence for lessons, rules, and events.

All data stored as JSON in governance/data/.
Event log is append-only JSONL.
"""

import json
from pathlib import Path
from typing import Optional

from governance.schemas import Lesson, Rule, Event, _now_iso


class GovernanceStore:
    """Repository-native governance data store."""

    def __init__(self, base_dir: Optional[Path] = None):
        if base_dir is None:
            base_dir = Path(__file__).resolve().parent / "data"
        self.base_dir = Path(base_dir)
        self.lessons_file = self.base_dir / "lessons.json"
        self.rules_file = self.base_dir / "rules.json"
        self.events_file = self.base_dir / "events.jsonl"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    # --- Lessons ---

    def load_lessons(self) -> dict:
        """Load all lessons as {id: dict}."""
        if not self.lessons_file.exists():
            return {}
        with open(self.lessons_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {item["id"]: item for item in data}

    def save_lessons(self, lessons: dict) -> None:
        """Save lessons dict to file."""
        with open(self.lessons_file, "w", encoding="utf-8") as f:
            json.dump(list(lessons.values()), f, indent=2, ensure_ascii=False)

    def add_lesson(self, lesson: Lesson) -> list:
        """Add a lesson. Returns validation errors (empty=success)."""
        errors = lesson.validate()
        if errors:
            return errors
        lessons = self.load_lessons()
        if lesson.id in lessons:
            return [f"Duplicate lesson ID: {lesson.id}"]
        if not lesson.created_at:
            lesson.created_at = _now_iso()
        lessons[lesson.id] = lesson.to_dict()
        self.save_lessons(lessons)
        self.append_event(Event(
            event_id=f"evt-{lesson.id}-created",
            timestamp=_now_iso(),
            actor="system",
            entity_type="LESSON",
            entity_id=lesson.id,
            event_type="LESSON_CREATED",
            context=f"Lesson '{lesson.title}' created",
        ))
        return []

    def get_lesson(self, lesson_id: str) -> Optional[dict]:
        """Get a single lesson by ID."""
        return self.load_lessons().get(lesson_id)

    def find_lessons(self, **kwargs) -> list:
        """Find lessons matching all provided field values."""
        lessons = self.load_lessons()
        results = []
        for lesson in lessons.values():
            match = True
            for key, value in kwargs.items():
                if key == "keyword":
                    if value.lower() not in [k.lower() for k in lesson.get("keywords", [])]:
                        match = False
                elif lesson.get(key) != value:
                    match = False
            if match:
                results.append(lesson)
        return results

    # --- Rules ---

    def load_rules(self) -> dict:
        """Load all rules as {id: dict}."""
        if not self.rules_file.exists():
            return {}
        with open(self.rules_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {item["id"]: item for item in data}

    def save_rules(self, rules: dict) -> None:
        with open(self.rules_file, "w", encoding="utf-8") as f:
            json.dump(list(rules.values()), f, indent=2, ensure_ascii=False)

    def add_rule(self, rule: Rule) -> list:
        """Add a rule. Returns validation errors."""
        errors = rule.validate()
        if errors:
            return errors
        rules = self.load_rules()
        if rule.id in rules:
            return [f"Duplicate rule ID: {rule.id}"]
        if not rule.created_at:
            rule.created_at = _now_iso()
        rules[rule.id] = rule.to_dict()
        self.save_rules(rules)
        self.append_event(Event(
            event_id=f"evt-{rule.id}-promoted",
            timestamp=_now_iso(),
            actor="system",
            entity_type="RULE",
            entity_id=rule.id,
            event_type="RULE_PROMOTED",
            context=f"Rule '{rule.title}' added",
        ))
        return []

    def get_rule(self, rule_id: str) -> Optional[dict]:
        return self.load_rules().get(rule_id)

    # --- Events ---

    def append_event(self, event: Event) -> list:
        """Append event to JSONL log. Returns validation errors."""
        errors = event.validate()
        if errors:
            return errors
        if not event.timestamp:
            event.timestamp = _now_iso()
        with open(self.events_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")
        return []

    def load_events(self) -> list:
        """Load all events from JSONL."""
        if not self.events_file.exists():
            return []
        events = []
        with open(self.events_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(json.loads(line))
        return events

    def find_events(self, entity_id: str = None, event_type: str = None) -> list:
        """Find events by entity_id or event_type."""
        events = self.load_events()
        results = []
        for event in events:
            if entity_id and event.get("entity_id") != entity_id:
                continue
            if event_type and event.get("event_type") != event_type:
                continue
            results.append(event)
        return results

    # --- Store Integrity & Direct-Mutation Detection ---

    MANDATORY_SAFETY_RULES = ["R-001", "R-002", "R-003", "R-004", "R-005", "R-006", "R-008"]

    def verify_integrity(self, check_baseline: bool = True) -> list:
        """
        Verify the repository governance integrity against direct-file bypass.
        
        Detects:
        - Missing mandatory safety rules (R-001 through R-006, R-008).
        - Direct promotion of rules to ACTIVE without promotion events or with PROPOSED source lessons.
        - Rules claiming AUTOMATED enforcement without a valid check_pointer.
        - Dangling source lessons (rule pointing to non-existent lesson).
        - Tampered or malformed event records in events.jsonl.
        - Schema violations in directly edited JSON files.
        """
        violations = []

        lessons = self.load_lessons()
        rules = self.load_rules()
        events = self.load_events()

        # 1. Check mandatory safety rules
        if check_baseline:
            for rid in self.MANDATORY_SAFETY_RULES:
                if rid not in rules:
                    violations.append(f"INTEGRITY_VIOLATION: Mandatory safety rule '{rid}' was deleted or missing from rules.json")

        # 2. Check rules integrity
        promoted_rule_ids = {e.get("entity_id") for e in events if e.get("event_type") == "RULE_PROMOTED"}
        for rid, rule_dict in rules.items():
            rule = Rule(**{k: v for k, v in rule_dict.items() if k in Rule.__dataclass_fields__})
            errs = rule.validate()
            if errs:
                violations.append(f"INTEGRITY_VIOLATION: Rule '{rid}' schema invalid: {errs}")

            # AUTOMATED enforcement requires valid check pointer
            if rule.enforcement_level == "AUTOMATED" and not rule.check_pointer:
                violations.append(f"INTEGRITY_VIOLATION: Rule '{rid}' claims AUTOMATED enforcement without check_pointer")

            # Source lesson consistency
            if rule.source_lesson:
                if rule.source_lesson not in lessons:
                    violations.append(f"INTEGRITY_VIOLATION: Rule '{rid}' references missing source lesson '{rule.source_lesson}'")
                else:
                    src_lesson = lessons[rule.source_lesson]
                    # A PROPOSED lesson cannot have an ACTIVE MUST rule
                    if src_lesson.get("governance_lifecycle") == "PROPOSED" and rule.governance_lifecycle == "ACTIVE" and rule.priority == "MUST":
                        violations.append(f"INTEGRITY_VIOLATION: Rule '{rid}' is ACTIVE MUST but source lesson '{rule.source_lesson}' is PROPOSED")

            # Promotion audit verification: if active, should be recorded in events if events exist
            if events and rule.governance_lifecycle == "ACTIVE" and rid not in self.MANDATORY_SAFETY_RULES and rid not in promoted_rule_ids:
                violations.append(f"INTEGRITY_VIOLATION: Rule '{rid}' is ACTIVE but lacks RULE_PROMOTED audit event")

        # 3. Check lessons integrity
        created_lesson_ids = {e.get("entity_id") for e in events if e.get("event_type") == "LESSON_CREATED"}
        for lid, lesson_dict in lessons.items():
            lesson = Lesson(**{k: v for k, v in lesson_dict.items() if k in Lesson.__dataclass_fields__})
            errs = lesson.validate()
            if errs:
                violations.append(f"INTEGRITY_VIOLATION: Lesson '{lid}' schema invalid: {errs}")

        # 4. Check events log integrity
        seen_event_ids = set()
        for idx, ev_dict in enumerate(events):
            eid = ev_dict.get("event_id")
            if not eid:
                violations.append(f"INTEGRITY_VIOLATION: Event at index {idx} has missing event_id")
                continue
            if eid in seen_event_ids:
                violations.append(f"INTEGRITY_VIOLATION: Duplicate event_id '{eid}' in audit log")
            seen_event_ids.add(eid)

            ev = Event(**{k: v for k, v in ev_dict.items() if k in Event.__dataclass_fields__})
            errs = ev.validate()
            if errs:
                violations.append(f"INTEGRITY_VIOLATION: Event '{eid}' invalid: {errs}")

        return violations

    # --- Duplicate Detection ---

    def find_potential_duplicates(self, lesson: Lesson) -> list:
        """
        Deterministic duplicate discovery using keywords, title, scope, and source.
        Returns matches with recommended resolution (merge, supersede, link).
        """
        lessons = self.load_lessons()
        duplicates = []
        new_keywords = {k.lower() for k in lesson.keywords}
        new_title = lesson.title.lower().strip()

        for lid, existing in lessons.items():
            if lid == lesson.id:
                continue
            ex_keywords = {k.lower() for k in existing.get("keywords", [])}
            ex_title = existing.get("title", "").lower().strip()

            overlap = new_keywords & ex_keywords
            title_match = (new_title == ex_title) or (new_title and new_title in ex_title) or (ex_title and ex_title in new_title)

            if title_match:
                duplicates.append({
                    "existing_id": lid,
                    "existing_title": existing.get("title"),
                    "match_type": "EXACT_OR_SUBSTRING_TITLE",
                    "recommendation": "MERGE_OR_REJECT",
                    "details": f"Title strongly matches existing lesson '{lid}'"
                })
            elif len(overlap) >= 3 and existing.get("scope") == lesson.scope:
                duplicates.append({
                    "existing_id": lid,
                    "existing_title": existing.get("title"),
                    "match_type": "HIGH_KEYWORD_AND_SCOPE_OVERLAP",
                    "recommendation": "SUPERSEDE_OR_LINK",
                    "details": f"Shared keywords: {overlap} in same scope '{lesson.scope}'"
                })

        return duplicates

    # --- Overrides & Audits ---

    def record_override(
        self,
        rule_id: str,
        approver: str,
        reason: str,
        scope: str,
        expiry: Optional[str] = None
    ) -> list:
        """Record an authorized rule override in the event log."""
        if not approver or not reason:
            return ["Approver and reason are required to record an override"]
        rule = self.get_rule(rule_id)
        if not rule:
            return [f"Rule '{rule_id}' not found"]

        event = Event(
            event_id=f"evt-override-{rule_id}-{_now_iso().replace(':', '-')}",
            timestamp=_now_iso(),
            actor=approver,
            entity_type="RULE",
            entity_id=rule_id,
            event_type="RULE_OVERRIDDEN",
            context=f"Override scope: {scope}. Reason: {reason}",
            evidence=f"Expiry: {expiry or 'none'}",
            result="OVERRIDDEN",
        )
        return self.append_event(event)

    def record_rule_applied(
        self,
        rule_id: str,
        experiment_id: str,
        artifact: Optional[str] = None,
        context: Optional[str] = None
    ) -> list:
        """Record that a rule was applied during an experiment."""
        event = Event(
            event_id=f"evt-applied-{rule_id}-{experiment_id}-{_now_iso().replace(':', '-')}",
            timestamp=_now_iso(),
            actor="system",
            entity_type="RULE",
            entity_id=rule_id,
            event_type="RULE_APPLIED",
            context=f"Experiment: {experiment_id}. Context: {context or 'standard'}",
            evidence=f"Artifact: {artifact or 'none'}",
            result="APPLIED",
        )
        return self.append_event(event)

    def record_rule_failed(
        self,
        rule_id: str,
        experiment_id: str,
        failure_class: str,
        error_message: str
    ) -> list:
        """Record that a rule failed or was violated."""
        event = Event(
            event_id=f"evt-failed-{rule_id}-{experiment_id}-{_now_iso().replace(':', '-')}",
            timestamp=_now_iso(),
            actor="system",
            entity_type="RULE",
            entity_id=rule_id,
            event_type="RULE_FAILED",
            context=f"Experiment: {experiment_id}. Failure class: {failure_class}",
            evidence=error_message,
            result="FAILED",
        )
        return self.append_event(event)

    def audit_retraction(self, rule_id: str) -> dict:
        """
        Audit the impact of retracting or modifying a rule.
        Traverses RULE_APPLIED events to identify affected experiments and artifacts.
        """
        applied_events = self.find_events(entity_id=rule_id, event_type="RULE_APPLIED")
        experiments = []
        artifacts = []

        for ev in applied_events:
            ctx = ev.get("context", "")
            if "Experiment: " in ctx:
                exp = ctx.split("Experiment: ")[1].split(".")[0].strip()
                if exp not in experiments:
                    experiments.append(exp)
            evi = ev.get("evidence", "")
            if "Artifact: " in evi:
                art = evi.split("Artifact: ")[1].strip()
                if art != "none" and art not in artifacts:
                    artifacts.append(art)

        audit_result = {
            "rule_id": rule_id,
            "total_applications": len(applied_events),
            "applied_experiments": experiments,
            "affected_artifacts": artifacts,
            "status": "REVIEW_REQUIRED" if applied_events else "NO_IMPACT",
            "action": "RETRACTION_AUDIT_COMPLETE",
        }

        # Append RETRACTION_AUDIT event to log
        self.append_event(Event(
            event_id=f"evt-retract-{rule_id}-{_now_iso().replace(':', '-')}",
            timestamp=_now_iso(),
            actor="system",
            entity_type="RULE",
            entity_id=rule_id,
            event_type="RETRACTION_AUDIT",
            context=f"Retraction audit for {rule_id}: {len(experiments)} experiments affected",
            evidence=f"Experiments: {experiments}, Artifacts: {artifacts}",
            result="REVIEW_REQUIRED" if experiments else "NO_IMPACT",
        ))

        return audit_result
