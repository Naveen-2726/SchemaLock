import pytest
from analyzer import analyze_migration_sql


def test_safe_migration_risk_intel():
    sql = "ALTER TABLE users ADD COLUMN last_login TIMESTAMP;"
    res = analyze_migration_sql(sql)
    intel = res.risk_intelligence
    
    assert intel is not None
    assert intel.data_loss_risk.level == "LOW"
    assert intel.locking_risk.level == "LOW"
    assert intel.compatibility_risk.level == "LOW"
    assert intel.performance_risk.level == "LOW"
    assert intel.blast_radius.destructive_operations == 0
    assert intel.blast_radius.level == "LOW"


def test_drop_table_risk_intel():
    sql = "DROP TABLE users;"
    res = analyze_migration_sql(sql)
    intel = res.risk_intelligence
    
    assert intel.data_loss_risk.level == "CRITICAL"
    assert intel.compatibility_risk.level == "CRITICAL"
    assert intel.locking_risk.level == "HIGH"
    assert intel.blast_radius.destructive_operations == 1
    assert intel.blast_radius.level == "CRITICAL"


def test_drop_column_risk_intel():
    sql = "ALTER TABLE users DROP COLUMN legacy_email;"
    res = analyze_migration_sql(sql)
    intel = res.risk_intelligence
    
    assert intel.data_loss_risk.level == "HIGH"
    assert intel.compatibility_risk.level == "HIGH"
    assert intel.locking_risk.level == "MEDIUM"
    assert intel.blast_radius.destructive_operations == 1
    assert intel.blast_radius.level == "HIGH"


def test_add_column_not_null_risk_intel():
    sql = "ALTER TABLE users ADD COLUMN phone VARCHAR(20) NOT NULL;"
    res = analyze_migration_sql(sql)
    intel = res.risk_intelligence
    
    assert intel.locking_risk.level == "HIGH"
    assert intel.compatibility_risk.level == "HIGH"
    assert intel.blast_radius.destructive_operations == 0
    assert intel.blast_radius.level == "HIGH"


def test_alter_column_type_risk_intel():
    sql = "ALTER TABLE users ALTER COLUMN age TYPE BIGINT;"
    res = analyze_migration_sql(sql)
    intel = res.risk_intelligence
    
    assert intel.locking_risk.level == "HIGH"
    assert intel.compatibility_risk.level == "HIGH"
    assert intel.performance_risk.level == "HIGH"


def test_create_index_risk_intel():
    sql = "CREATE INDEX idx_users_email ON users(email);"
    res = analyze_migration_sql(sql)
    intel = res.risk_intelligence
    
    assert intel.locking_risk.level == "MEDIUM"
    assert intel.performance_risk.level == "MEDIUM"
    assert intel.blast_radius.level == "MEDIUM"


def test_create_index_concurrent_risk_intel():
    sql = "CREATE INDEX CONCURRENTLY idx_users_email ON users(email);"
    res = analyze_migration_sql(sql)
    intel = res.risk_intelligence
    
    assert intel.locking_risk.level == "LOW"
    assert intel.performance_risk.level == "MEDIUM"
    assert intel.blast_radius.level == "MEDIUM"


def test_truncate_table_risk_intel():
    sql = "TRUNCATE TABLE users;"
    res = analyze_migration_sql(sql)
    intel = res.risk_intelligence
    
    assert intel.data_loss_risk.level == "CRITICAL"
    assert intel.locking_risk.level == "HIGH"
    assert intel.blast_radius.destructive_operations == 1
    assert intel.blast_radius.level == "CRITICAL"


def test_multiple_destructive_operations_risk_intel():
    sql = "DROP TABLE logs;\nALTER TABLE users DROP COLUMN legacy_id;"
    res = analyze_migration_sql(sql)
    intel = res.risk_intelligence
    
    assert intel.blast_radius.destructive_operations == 2
    assert intel.blast_radius.level == "CRITICAL"
    assert intel.data_loss_risk.level == "CRITICAL"
    assert intel.compatibility_risk.level == "CRITICAL"
