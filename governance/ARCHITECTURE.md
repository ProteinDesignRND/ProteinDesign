# Governance Architecture

**Version:** 1.0.0  
**Date:** 2026-09-24  
**Status:** IMPLEMENTED AND TESTED (83/83 tests pass)

---

## Overview

This project uses a lightweight, repository-native governance system with three primary entities:

1. **LESSON** — A durable record of something learned from project experience
2. **RULE** — A governance directive derived from a lesson
3. **EVENT** — An append-only audit trail entry

No embeddings. No vector databases. No autonomous promotion. All retrieval is deterministic and explainable.

---

## Quick Start (for teammates)

### Run preflight before an experiment

```python
from governance.store import GovernanceStore
from governance.preflight import run_preflight, format_preflight

store = GovernanceStore()
result = run_preflight(store, {
    "pipeline_stage": "evaluation",
    "model_family": "proteinsolver",
})
print(format_preflight(result))
```

### Submit a new lesson (~3 minutes)

```python
from governance.schemas import Lesson
from governance.store import GovernanceStore

store = GovernanceStore()
store.add_lesson(Lesson(
    id="L-NEW",
    title="Brief description of what happened",
    what_happened="Detailed description",
    lesson="What we learned",
    type="METHOD_SCIENCE",  # or BUG_ENVIRONMENT, DATA_PROVENANCE, PROCESS_TEAM, AI_TOOLING
    scope="proteinsolver",
    evidence_status="OBSERVED",
    governance_lifecycle="PROPOSED",  # Always start as PROPOSED
    keywords=["relevant", "keywords"],
))
```

### Run governance tests

```bash
python tests/test_governance.py
```

---

## Architecture Details

### Lesson Schema

| Field | Required | Description |
| :--- | :--- | :--- |
| `id` | Yes | Unique identifier (e.g., `L-001`) |
| `version` | No | Integer version, starts at 1 |
| `schema_version` | No | Schema version (currently `1.0.0`) |
| `title` | Yes | Short description |
| `what_happened` | Yes | Narrative of the incident |
| `lesson` | Yes | What was learned |
| `type` | Yes | One of: `BUG_ENVIRONMENT`, `METHOD_SCIENCE`, `DATA_PROVENANCE`, `PROCESS_TEAM`, `AI_TOOLING` |
| `scope` | Yes | `project-wide` or subsystem name |
| `trigger` | No | When this lesson becomes relevant |
| `evidence_status` | Yes | One of: `OBSERVED`, `REPRODUCED`, `EXTERNALLY_SUPPORTED`, `INCONCLUSIVE`, `CONTRADICTED`, `NOT_VERIFIABLE` |
| `evidence_scope` | No | What was actually tested |
| `governance_lifecycle` | Yes | `PROPOSED`, `ACTIVE`, `DORMANT`, `RETIRED` |
| `applicability` | No | Dict of context conditions |
| `keywords` | No | List of searchable tags |

### Rule Schema

| Field | Required | Description |
| :--- | :--- | :--- |
| `id` | Yes | Unique identifier (e.g., `R-001`) |
| `source_lesson` | Yes | Lesson ID this rule derives from |
| `priority` | Yes | `MUST` or `SHOULD` |
| `enforcement_level` | Yes | `NONE`, `MANUAL`, or `AUTOMATED` |
| `governance_lifecycle` | Yes | Same as lessons |
| `applicability_conditions` | No | Dict of context → value requirements |
| `check_pointer` | No | File/test that checks this rule |
| `override_policy` | No | What's needed to override |

### Event Schema

| Field | Required | Description |
| :--- | :--- | :--- |
| `event_id` | Yes | Unique identifier |
| `timestamp` | Auto | ISO timestamp |
| `actor` | Yes | Who triggered it |
| `entity_type` | Yes | `LESSON` or `RULE` |
| `entity_id` | Yes | ID of the affected entity |
| `event_type` | Yes | See event types below |

---

## Key Constraints

### Lessons cannot self-promote

- A PROPOSED lesson appears only as FYI in preflight
- Only human review can promote PROPOSED → ACTIVE
- A lesson's governance lifecycle is separate from its evidence status

### AI agent boundaries

Agents **may**: propose lessons, identify conflicts, run checks, record evidence.

Agents **may NOT**: promote lessons, change governance status, broaden scope, override blockers, declare scientific validation.

### Precedence (highest first)

1. Integrity / safety
2. Project-wide validated reproducibility
3. Scoped subsystem
4. Task-specific
5. Informal guidance

### Conflict handling

- Multiple MUST rules in the same scope → flagged as `MULTIPLE_MUST_SAME_SCOPE`
- Resolution: `HUMAN_REVIEW_REQUIRED`
- Contradictory MUST rules are NEVER silently resolved

---

## Current Always-On Core (8 rules)

| Rule | Priority | Enforcement | What it protects |
| :--- | :--- | :--- | :--- |
| R-001 | MUST | AUTOMATED | No native-visible runs reported as valid recovery |
| R-002 | MUST | AUTOMATED | Batch interface for ProteinSolver |
| R-003 | MUST | MANUAL | Correct reproduction wording |
| R-004 | MUST | MANUAL | Single-target ≠ benchmark |
| R-005 | MUST | MANUAL | Training membership uncertainty |
| R-006 | MUST | AUTOMATED | Historical source preservation |
| R-007 | SHOULD | MANUAL | Evidence/application scope separation |
| R-008 | MUST | AUTOMATED | AI cannot self-promote |

---

## Preflight Output Format

```
MUST (N)    — Rules that MUST be satisfied. Blocking if ACTIVE.
SHOULD (N)  — Rules that SHOULD be followed. Advisory.
FYI (N)     — Informational. Includes PROPOSED lessons/rules.

COVERAGE    — How many rules were evaluated, relevant, unknown, etc.
CONFLICTS   — Any MUST-MUST conflicts requiring human review.
NOVEL       — Context fields/values not seen in any existing rule.
```

"No warnings" does NOT mean "safe". Always check unknown context fields and novel conditions.

---

## Learning Loop

```
INCIDENT → ANALYZE → CLASSIFY → GENERALIZE → LESSON → RULE (if warranted) → CHECK → DEPLOY → VALIDATE → PROMOTE / REVISE / RETIRE
```

This is not automatic ML learning. It is durable repository changes and validated governance events.

---

## Failure Classification

When a governance failure occurs, classify the root cause:

| Class | Meaning |
| :--- | :--- |
| `NO_LESSON` | Problem occurred with no relevant lesson in the system |
| `RETRIEVAL_MISS` | Lesson exists but was not retrieved |
| `APPLICABILITY_ERROR` | Lesson retrieved but applied to wrong context |
| `ENFORCEMENT_GAP` | Rule exists but enforcement didn't trigger |
| `RULE_ERROR` | Rule itself is incorrect |
| `CONFLICT` | Contradictory rules prevented correct action |
| `IMPLEMENTATION_BYPASS` | Rule was known but deliberately ignored |

---

## File Layout

```
governance/
├── __init__.py           # Constants, taxonomy definitions
├── schemas.py            # Lesson, Rule, Event dataclasses
├── store.py              # File-based persistence
├── preflight.py          # Deterministic retrieval and preflight
├── seed.py               # Initial data seeding script
└── data/
    ├── lessons.json      # All lessons
    ├── rules.json        # All rules
    └── events.jsonl      # Append-only event log

tests/
└── test_governance.py    # 83-test comprehensive suite
```

---

## Retraction Audit

When a rule or lesson materially changes:

1. Record version increment in the entity
2. Log `LESSON_SUPERSEDED` or `RETRACTION_AUDIT` event
3. The event references affected experiments via `context` field
4. Review downstream artifacts that relied on the old version

This is traceable through the event log.

---

## What This System Does NOT Do

- No embeddings or vector search
- No autonomous lesson promotion
- No numeric trust scores
- No cross-project federation
- No dashboards
- No LLM-inferred scope as authority
- No forced executable lessons
