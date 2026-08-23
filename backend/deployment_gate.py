"""
SchemaLock Deployment Gate Engine.

Provides deterministic deployment readiness recommendations based on:
- Deterministic AST risk findings & overall severity
- Risk Intelligence & Blast Radius metrics
- AI Validation Guard warnings
- Migration Content Integrity SHA-256 status

Statuses:
- BLOCKED: High risk of data loss, destructive operations, or unverified rollback schema
- REQUIRES_REVIEW: Elevated locking, compatibility, or schema migration risks needing manual review
- READY_FOR_REVIEW: Low-risk migration candidate for standard peer review
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class DeploymentGate(BaseModel):
    status: str  # "READY_FOR_REVIEW" | "REQUIRES_REVIEW" | "BLOCKED"
    reason: str
    blocking_factors: List[str]
    review_factors: List[str]


def evaluate_deployment_gate(
    risk_score: int,
    severity: str,
    findings: List[Any],
    risk_intelligence: Optional[Any],
    migration_integrity: Optional[Any],
    ai_analysis: Optional[Any]
) -> DeploymentGate:
    """Evaluate deterministic deployment gate status and decision factors."""
    blocking_factors = []
    review_factors = []

    # Extract blast radius & risk dimensions
    blast_level = "LOW"
    destructive_ops = 0
    high_dimensions = []
    
    if risk_intelligence:
        blast_radius = getattr(risk_intelligence, "blast_radius", None)
        if blast_radius:
            blast_level = getattr(blast_radius, "level", "LOW")
            destructive_ops = getattr(blast_radius, "destructive_operations", 0)

        for dim_name in ["data_loss_risk", "locking_risk", "compatibility_risk", "performance_risk"]:
            dim_obj = getattr(risk_intelligence, dim_name, None)
            if dim_obj and getattr(dim_obj, "level", "LOW") in ("MEDIUM", "HIGH", "CRITICAL"):
                dim_label = dim_name.replace("_risk", "").replace("_", " ").title()
                high_dimensions.append(f"{dim_label} ({getattr(dim_obj, 'level')})")

    # Extract AI Guard warning status
    has_ai_guard_warning = False
    if ai_analysis:
        rollback_sql = getattr(ai_analysis, "rollback_sql", "") or ""
        ai_status = getattr(ai_analysis, "status", "") or ""
        if "-- WARNING:" in rollback_sql or ai_status == "error":
            has_ai_guard_warning = True

    # Extract integrity status
    integrity_status = "GENERATED"
    if migration_integrity:
        integrity_status = getattr(migration_integrity, "status", "GENERATED")

    # 1. BLOCKED Conditions
    if severity == "CRITICAL":
        blocking_factors.append("Deterministic severity is CRITICAL.")
    if risk_score >= 80:
        blocking_factors.append(f"Overall risk score is high ({risk_score}/100).")
    if blast_level == "CRITICAL":
        blocking_factors.append("Blast radius level is CRITICAL.")
    if destructive_ops >= 2:
        blocking_factors.append(f"Migration contains {destructive_ops} destructive DDL operations.")
    if has_ai_guard_warning:
        blocking_factors.append("AI guard warning: Original schema data type required for rollback verification.")
    if integrity_status == "DRIFT_DETECTED":
        blocking_factors.append("Migration integrity failure: Content drift detected against expected fingerprint.")

    if blocking_factors:
        return DeploymentGate(
            status="BLOCKED",
            reason="Deployment blocked due to critical risk factors or unverified rollback schema.",
            blocking_factors=blocking_factors,
            review_factors=[]
        )

    # 2. REQUIRES_REVIEW Conditions
    if severity in ("HIGH", "MEDIUM"):
        review_factors.append(f"Deterministic severity is {severity}.")
    if risk_score >= 15:
        review_factors.append(f"Elevated risk score ({risk_score}/100).")
    if blast_level in ("HIGH", "MEDIUM"):
        review_factors.append(f"Blast radius level is {blast_level}.")
    if destructive_ops == 1:
        review_factors.append("Contains 1 destructive operation (e.g. DROP COLUMN).")
    if high_dimensions:
        review_factors.append(f"Elevated risk dimensions: {', '.join(high_dimensions)}.")

    if review_factors:
        return DeploymentGate(
            status="REQUIRES_REVIEW",
            reason="Migration requires senior peer review prior to staging execution.",
            blocking_factors=[],
            review_factors=review_factors
        )

    # 3. READY_FOR_REVIEW Condition
    return DeploymentGate(
        status="READY_FOR_REVIEW",
        reason="Low risk migration candidate ready for standard deployment review.",
        blocking_factors=[],
        review_factors=["No high or critical AST findings detected."]
    )
