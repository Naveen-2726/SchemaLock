import pytest
from ai_service import validate_and_sanitize_ai_analysis, AIAnalysis
from analyzer import analyze_migration_sql


def test_guard_flags_hallucinated_rollback_column_type():
    raw_ai = AIAnalysis(
        status="success",
        risk_explanation="Dropping legacy_email removes column data.",
        additional_risks=["Application breakage"],
        safer_migration="-- Deprecate first",
        rollback_sql="ALTER TABLE users ADD COLUMN legacy_email VARCHAR(255);",
        recommendation="Deploy carefully."
    )
    
    sanitized = validate_and_sanitize_ai_analysis(
        analysis=raw_ai,
        deterministic_severity="HIGH",
        sql="ALTER TABLE users DROP COLUMN legacy_email;"
    )
    
    assert "-- WARNING: Original column data type" in sanitized.rollback_sql
    assert "ALTER TABLE users ADD COLUMN legacy_email VARCHAR(255);" in sanitized.rollback_sql


def test_guard_sanitizes_zero_downtime_claims():
    raw_ai = AIAnalysis(
        status="success",
        risk_explanation="This migration pattern is 100% safe and guaranteed zero-downtime.",
        additional_risks=[],
        safer_migration="-- Safe DDL",
        rollback_sql="-- Rollback DDL",
        recommendation="This strategy is guaranteed zero-downtime."
    )
    
    sanitized = validate_and_sanitize_ai_analysis(
        analysis=raw_ai,
        deterministic_severity="HIGH",
        sql="ALTER TABLE users ADD COLUMN age INT NOT NULL DEFAULT 0;"
    )
    
    assert "guaranteed zero-downtime" not in sanitized.risk_explanation
    assert "reduced locking impact" in sanitized.risk_explanation
    assert "guaranteed zero-downtime" not in sanitized.recommendation


def test_all_10_phase5_cases_deterministic_safety():
    test_cases = [
        ("DROP TABLE users;", "CRITICAL", ["DROP_TABLE"]),
        ("ALTER TABLE users DROP COLUMN legacy_email;", "HIGH", ["DROP_COLUMN"]),
        ("ALTER TABLE users ADD COLUMN phone VARCHAR(20) NOT NULL;", "HIGH", ["ADD_COLUMN_NOT_NULL"]),
        ("ALTER TABLE users ADD COLUMN phone VARCHAR(20) NOT NULL DEFAULT 'UNKNOWN';", "HIGH", ["ADD_COLUMN_NOT_NULL"]),
        ("ALTER TABLE users ALTER COLUMN age TYPE INTEGER;", "HIGH", ["ALTER_COLUMN_TYPE"]),
        ("CREATE INDEX idx_users_email ON users(email);", "MEDIUM", ["CREATE_INDEX"]),
        ("CREATE INDEX CONCURRENTLY idx_users_email ON users(email);", "LOW", ["CREATE_INDEX_CONCURRENT"]),
        ("TRUNCATE TABLE users;", "CRITICAL", ["TRUNCATE_TABLE"]),
        ("-- DROP TABLE users;\nCREATE TABLE items (id INT);", "LOW", []),
        ("DROP TABLE logs;\nALTER TABLE users DROP COLUMN legacy_id;", "CRITICAL", ["DROP_TABLE", "DROP_COLUMN", "MULTIPLE_DESTRUCTIVE_OPERATIONS"])
    ]
    
    for sql, expected_severity, expected_rules in test_cases:
        res = analyze_migration_sql(sql)
        assert res.severity == expected_severity
        rules = [f.rule_id for f in res.findings]
        for rule in expected_rules:
            assert rule in rules
