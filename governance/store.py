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
