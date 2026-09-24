"""
Governance schemas: Lesson, Rule, Event.

JSON-serializable dataclasses. No external dependencies.
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

from governance import (
    SCHEMA_VERSION, LESSON_TYPES, EVIDENCE_STATUSES,
    GOVERNANCE_LIFECYCLES, RULE_PRIORITIES, ENFORCEMENT_LEVELS, EVENT_TYPES,
)


@dataclass
class Lesson:
    """A durable lesson learned from project experience."""
    id: str
    version: int = 1
    schema_version: str = SCHEMA_VERSION
    title: str = ""
    what_happened: str = ""
    lesson: str = ""
    type: str = ""  # from LESSON_TYPES
    scope: str = ""  # e.g., "proteinsolver", "project-wide"
    trigger: str = ""  # what triggers this lesson's relevance
    evidence_status: str = ""  # from EVIDENCE_STATUSES
    evidence_scope: str = ""  # what was actually tested
    governance_lifecycle: str = "PROPOSED"  # from GOVERNANCE_LIFECYCLES
    source: str = ""  # where the lesson came from
    owner: str = ""  # who is responsible
    created_at: str = ""
    last_reviewed: str = ""
    related_experiments: list = field(default_factory=list)
    related_files: list = field(default_factory=list)
    related_claims: list = field(default_factory=list)
    related_rules: list = field(default_factory=list)
    origin_event: str = ""
    applicability: dict = field(default_factory=dict)
    keywords: list = field(default_factory=list)

    def validate(self) -> list:
        """Return list of validation errors. Empty = valid."""
        errors = []
        if not self.id:
            errors.append("id is required")
        if self.type and self.type not in LESSON_TYPES:
            errors.append(f"type '{self.type}' not in {LESSON_TYPES}")
        if self.evidence_status and self.evidence_status not in EVIDENCE_STATUSES:
            errors.append(f"evidence_status '{self.evidence_status}' not in {EVIDENCE_STATUSES}")
        if self.governance_lifecycle not in GOVERNANCE_LIFECYCLES:
            errors.append(f"governance_lifecycle '{self.governance_lifecycle}' not in {GOVERNANCE_LIFECYCLES}")
        return errors

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Rule:
    """A governance rule derived from a lesson."""
    id: str
    version: int = 1
    schema_version: str = SCHEMA_VERSION
    title: str = ""
    description: str = ""
    source_lesson: str = ""  # lesson ID this rule derives from
    scope: str = ""
    applicability_conditions: dict = field(default_factory=dict)
    priority: str = "SHOULD"  # from RULE_PRIORITIES
    enforcement_level: str = "NONE"  # from ENFORCEMENT_LEVELS
    check_pointer: str = ""  # file/function/test that checks this
    owner: str = ""
    override_policy: str = ""  # what's needed to override
    supersedes: str = ""  # rule ID this replaces
    review_trigger: str = ""  # when to re-examine
    governance_lifecycle: str = "PROPOSED"
    created_at: str = ""
    last_reviewed: str = ""
    keywords: list = field(default_factory=list)

    def validate(self) -> list:
        errors = []
        if not self.id:
            errors.append("id is required")
        if self.priority not in RULE_PRIORITIES:
            errors.append(f"priority '{self.priority}' not in {RULE_PRIORITIES}")
        if self.enforcement_level not in ENFORCEMENT_LEVELS:
            errors.append(f"enforcement_level '{self.enforcement_level}' not in {ENFORCEMENT_LEVELS}")
        if self.governance_lifecycle not in GOVERNANCE_LIFECYCLES:
            errors.append(f"governance_lifecycle '{self.governance_lifecycle}' not in {GOVERNANCE_LIFECYCLES}")
        return errors

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Event:
    """An append-only event in the governance audit trail."""
    event_id: str
    timestamp: str = ""
    actor: str = ""
    entity_type: str = ""  # "LESSON" or "RULE"
    entity_id: str = ""
    event_type: str = ""  # from EVENT_TYPES
    context: str = ""
    evidence: str = ""
    result: str = ""
    schema_version: str = SCHEMA_VERSION

    def validate(self) -> list:
        errors = []
        if not self.event_id:
            errors.append("event_id is required")
        if self.event_type and self.event_type not in EVENT_TYPES:
            errors.append(f"event_type '{self.event_type}' not in {EVENT_TYPES}")
        return errors

    def to_dict(self) -> dict:
        return asdict(self)


def _now_iso() -> str:
    return datetime.now().isoformat()
