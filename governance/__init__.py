"""
Protein Design Governance Architecture
=======================================
Lightweight, repository-native lesson/rule/event system.

Three primary entities: LESSON, RULE, EVENT.
No embeddings, no vector databases, no autonomous promotion.
Deterministic retrieval based on explicit context matching.
"""

SCHEMA_VERSION = "1.0.0"

# --- Bounded Lesson Types ---
LESSON_TYPES = {
    "BUG_ENVIRONMENT",
    "METHOD_SCIENCE",
    "DATA_PROVENANCE",
    "PROCESS_TEAM",
    "AI_TOOLING",
}

# --- Evidence Status ---
EVIDENCE_STATUSES = {
    "OBSERVED",
    "REPRODUCED",
    "EXTERNALLY_SUPPORTED",
    "INCONCLUSIVE",
    "CONTRADICTED",
    "NOT_VERIFIABLE",
}

# --- Governance Lifecycle ---
GOVERNANCE_LIFECYCLES = {
    "PROPOSED",
    "ACTIVE",
    "DORMANT",
    "RETIRED",
}

# --- Rule Priority ---
RULE_PRIORITIES = {"MUST", "SHOULD"}

# --- Enforcement Level ---
ENFORCEMENT_LEVELS = {"NONE", "MANUAL", "AUTOMATED"}

# --- Event Types ---
EVENT_TYPES = {
    "LESSON_CREATED",
    "LESSON_REVIEWED",
    "LESSON_VALIDATED",
    "LESSON_CONTRADICTED",
    "LESSON_SUPERSEDED",
    "RULE_PROMOTED",
    "RULE_APPLIED",
    "RULE_OVERRIDDEN",
    "RULE_FAILED",
    "RETRIEVAL_MISSED",
    "MIGRATION",
    "NOVEL_CONDITION",
    "RETRACTION_AUDIT",
}

# --- Failure Classification ---
FAILURE_CLASSES = {
    "NO_LESSON",
    "RETRIEVAL_MISS",
    "APPLICABILITY_ERROR",
    "ENFORCEMENT_GAP",
    "RULE_ERROR",
    "CONFLICT",
    "IMPLEMENTATION_BYPASS",
}

# --- Precedence (highest first) ---
PRECEDENCE_ORDER = [
    "INTEGRITY_SAFETY",
    "PROJECT_WIDE_REPRODUCIBILITY",
    "SCOPED_SUBSYSTEM",
    "TASK_SPECIFIC",
    "INFORMAL_GUIDANCE",
]

# --- Preflight Tiers ---
PREFLIGHT_TIERS = {"MUST", "SHOULD", "FYI"}
