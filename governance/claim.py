"""
Claim-level governance evaluation and extrapolation detection.

Enforces:
1. Scope consistency (evidence scope vs application/claim scope).
2. EXTRAPOLATION_REVIEW_REQUIRED when claim scope exceeds demonstrated evidence.
3. Four mandatory adversarial cases:
   A. Single-target result described as benchmark / generalization.
   B. Unknown training membership described as held-out / unseen.
   C. Native-visible sequence result described as valid all-masked recovery.
   D. Modern compatibility described as historical equivalence.
"""

from typing import Dict, Any, List, Optional


# Scope hierarchy for extrapolation check (higher index = broader scope)
SCOPE_HIERARCHY = {
    "single-target": 1,
    "1n5ua03": 1,
    "target-specific": 1,
    "subsystem": 2,
    "proteinsolver": 2,
    "benchmark": 3,
    "generalization": 3,
    "multi-target": 3,
    "project-wide": 4,
}


def evaluate_claim(claim: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate a scientific or governance claim for scope extrapolation,
    wording violations, and required checks.

    Expected claim dict structure:
      - claim_id (str)
      - claim_text (str)
      - claim_scope (str)
      - evidence_scope (str)
      - evidence_status (str: e.g. OBSERVED, REPRODUCED, NOT_VERIFIABLE)
      - checks_run (list)
      - checks_missing (list)
      - allowed_claim_level (str, optional)
    """
    claim_id = claim.get("claim_id", "UNKNOWN_CLAIM")
    claim_text = claim.get("claim_text", "").strip()
    claim_scope = str(claim.get("claim_scope", "")).lower()
    evidence_scope = str(claim.get("evidence_scope", "")).lower()
    evidence_status = claim.get("evidence_status", "")
    checks_run = list(claim.get("checks_run", []))
    checks_missing = list(claim.get("checks_missing", []))

    violations = []
    warnings = []
    text_lower = claim_text.lower()

    # Adversarial Case A: Single-target result described as benchmark
    is_single_target = (
        "single-target" in evidence_scope or
        "1n5u" in evidence_scope or
        "1n5ua03" in text_lower or
        "single-target" in text_lower
    )
    if is_single_target:
        if any(term in text_lower for term in ["benchmark", "generalization", "representative of folds", "general performance"]):
            violations.append({
                "rule": "R-004",
                "code": "SINGLE_TARGET_BENCHMARK_ESCALATION",
                "message": "Single-target results cannot be described as benchmark or generalization performance.",
                "action": "REJECT: Reclassify as 'single-target all-masked inverse-folding integration result'."
            })

    # Adversarial Case B: Unknown training membership described as held-out / unseen
    if any(term in text_lower for term in ["held-out", "held out", "unseen", "guaranteed not in training"]):
        if evidence_status == "NOT_VERIFIABLE" or "membership_query" in checks_missing or not ("direct_corpus_query" in checks_run):
            violations.append({
                "rule": "R-005",
                "code": "UNVERIFIED_TRAINING_MEMBERSHIP",
                "message": "Structure cannot be described as held-out or unseen without direct verification against full training corpus.",
                "action": "REJECT: Classify training membership as 'NOT VERIFIABLE FROM ACCESSIBLE METADATA'."
            })

    # Adversarial Case C: Native-visible sequence result described as valid all-masked recovery
    if any(term in text_lower for term in ["100% recovery", "valid recovery", "inverse-folding recovery", "all-masked recovery"]):
        if "native_visible" in text_lower or "diagnostic" in text_lower or "data.y" in text_lower or ("mask_check_passed" not in checks_run):
            if not ("all_masked_verified" in checks_run):
                violations.append({
                    "rule": "R-001",
                    "code": "NATIVE_VISIBLE_RECOVERY_LEAK",
                    "message": "Native-sequence-visible runs are diagnostic scoring only, not valid all-masked recovery.",
                    "action": "REJECT: Verify all residues masked (data.x=20, data.y=None) before claiming recovery."
                })

    # Adversarial Case D: Modern compatibility described as historical equivalence
    if any(term in text_lower for term in ["historical equivalence", "100% mathematical fidelity", "mathematically identical", "identical to 2020"]):
        if "historical_stack_numerical_comparison" not in checks_run:
            violations.append({
                "rule": "R-003",
                "code": "HISTORICAL_EQUIVALENCE_OVERCLAIM",
                "message": "Cannot claim historical runtime equivalence without numerical comparison on original historical stack.",
                "action": "REJECT: Use 'FUNCTIONALLY REPRODUCED WITH MODERN COMPATIBILITY ADAPTATION'."
            })

    # Scope Extrapolation Check
    ev_rank = SCOPE_HIERARCHY.get(evidence_scope, 2)
    cl_rank = SCOPE_HIERARCHY.get(claim_scope, 2)
    extrapolation_required = False

    if cl_rank > ev_rank or (is_single_target and claim_scope in ("benchmark", "generalization", "project-wide")):
        extrapolation_required = True
        warnings.append({
            "rule": "R-007",
            "code": "EXTRAPOLATION_REVIEW_REQUIRED",
            "message": f"Claim scope '{claim_scope}' is broader than demonstrated evidence scope '{evidence_scope}'.",
            "action": "EXTRAPOLATION_REVIEW_REQUIRED: Explicit lead review and documented rationale required."
        })

    # Determine status and allowed claim level
    if violations:
        status = "REJECTED"
        allowed_level = "REJECTED"
    elif extrapolation_required:
        status = "EXTRAPOLATION_REVIEW_REQUIRED"
        allowed_level = "PROVISIONAL_PENDING_REVIEW"
    else:
        status = "APPROVED"
        allowed_level = "VALIDATED_CLAIM"

    return {
        "claim_id": claim_id,
        "status": status,
        "allowed_claim_level": allowed_level,
        "violations": violations,
        "warnings": warnings,
        "checks_run": checks_run,
        "checks_missing": checks_missing,
        "is_extrapolated": extrapolation_required,
    }
