import pytest
from analyzer import analyze_migration_sql
from deployment_gate import evaluate_deployment_gate, DeploymentGate
from ai_service import AIAnalysis
from fingerprint import MigrationIntegrity


def test_safe_migration_ready_for_review():
    sql = "ALTER TABLE users ADD COLUMN last_login TIMESTAMP;"
    res = analyze_migration_sql(sql)
    assert res.deployment_gate.status == "READY_FOR_REVIEW"
    assert "low risk" in res.deployment_gate.reason.lower()


def test_medium_risk_migration_requires_review():
    sql = "CREATE INDEX idx_users_email ON users(email);"
    res = analyze_migration_sql(sql)
    assert res.deployment_gate.status == "REQUIRES_REVIEW"
    assert len(res.deployment_gate.review_factors) > 0


def test_high_risk_migration_requires_review():
    sql = "ALTER TABLE users ALTER COLUMN age TYPE BIGINT;"
    res = analyze_migration_sql(sql)
    assert res.deployment_gate.status == "REQUIRES_REVIEW"


def test_drop_table_blocked():
    sql = "DROP TABLE users;"
    res = analyze_migration_sql(sql)
    assert res.deployment_gate.status == "BLOCKED"
    assert any("CRITICAL" in factor for factor in res.deployment_gate.blocking_factors)


def test_multiple_destructive_operations_blocked():
    sql = "DROP TABLE logs;\nALTER TABLE users DROP COLUMN legacy_id;"
    res = analyze_migration_sql(sql)
    assert res.deployment_gate.status == "BLOCKED"
    assert any("destructive" in factor.lower() for factor in res.deployment_gate.blocking_factors)


def test_ai_guard_warning_causes_blocked():
    ai = AIAnalysis(
        status="success",
        risk_explanation="Dropping legacy_email removes data.",
        additional_risks=[],
        safer_migration="-- Deprecate first",
        rollback_sql="-- WARNING: Original column data type unknown from migration input.\nALTER TABLE users ADD COLUMN legacy_email VARCHAR(255);",
        recommendation="Deploy carefully."
    )
    
    gate = evaluate_deployment_gate(
        risk_score=30,
        severity="HIGH",
        findings=[],
        risk_intelligence=None,
        migration_integrity=None,
        ai_analysis=ai
    )
    
    assert gate.status == "BLOCKED"
    assert any("AI guard warning" in f for f in gate.blocking_factors)


def test_integrity_drift_causes_blocked():
    integrity = MigrationIntegrity(
        algorithm="SHA-256",
        fingerprint="abc",
        status="DRIFT_DETECTED"
    )
    
    gate = evaluate_deployment_gate(
        risk_score=10,
        severity="LOW",
        findings=[],
        risk_intelligence=None,
        migration_integrity=integrity,
        ai_analysis=None
    )
    
    assert gate.status == "BLOCKED"
    assert any("Content drift detected" in f for f in gate.blocking_factors)
