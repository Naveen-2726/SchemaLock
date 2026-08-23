import pytest
from analyzer import analyze_migration_sql


def test_safe_migration():
    sql = """
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    result = analyze_migration_sql(sql)
    assert result.risk_score == 0
    assert result.severity == "LOW"
    assert len(result.findings) == 0


def test_drop_table():
    sql = "DROP TABLE legacy_users;"
    result = analyze_migration_sql(sql)
    assert result.severity == "CRITICAL"
    assert result.risk_score >= 50
    rule_ids = [f.rule_id for f in result.findings]
    assert "DROP_TABLE" in rule_ids


def test_drop_column():
    sql = "ALTER TABLE users DROP COLUMN old_token;"
    result = analyze_migration_sql(sql)
    assert result.severity == "HIGH"
    assert result.risk_score >= 30
    rule_ids = [f.rule_id for f in result.findings]
    assert "DROP_COLUMN" in rule_ids


def test_add_column_not_null():
    sql = "ALTER TABLE users ADD COLUMN age INT NOT NULL;"
    result = analyze_migration_sql(sql)
    assert result.severity == "HIGH"
    assert result.risk_score >= 30
    rule_ids = [f.rule_id for f in result.findings]
    assert "ADD_COLUMN_NOT_NULL" in rule_ids


def test_alter_column_type():
    sql = "ALTER TABLE users ALTER COLUMN age TYPE BIGINT;"
    result = analyze_migration_sql(sql)
    assert result.severity == "HIGH"
    assert result.risk_score >= 30
    rule_ids = [f.rule_id for f in result.findings]
    assert "ALTER_COLUMN_TYPE" in rule_ids


def test_multiple_risks():
    sql = """
    DROP TABLE logs;
    ALTER TABLE users DROP COLUMN legacy_id;
    """
    result = analyze_migration_sql(sql)
    assert result.severity == "CRITICAL"
    assert result.risk_score >= 80
    rule_ids = [f.rule_id for f in result.findings]
    assert "DROP_TABLE" in rule_ids
    assert "DROP_COLUMN" in rule_ids
    assert "MULTIPLE_DESTRUCTIVE_OPERATIONS" in rule_ids


def test_truncate_table():
    sql = "TRUNCATE TABLE active_sessions;"
    result = analyze_migration_sql(sql)
    assert result.severity == "CRITICAL"
    assert result.risk_score >= 50
    rule_ids = [f.rule_id for f in result.findings]
    assert "TRUNCATE_TABLE" in rule_ids


def test_comment_false_positive_prevention():
    sql = """
    -- Remember to DROP TABLE legacy_users manually later
    CREATE TABLE items (
        id INT PRIMARY KEY
    );
    """
    result = analyze_migration_sql(sql)
    assert result.risk_score == 0
    assert result.severity == "LOW"
    assert len(result.findings) == 0
