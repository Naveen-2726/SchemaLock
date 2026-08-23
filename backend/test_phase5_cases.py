import json
import pytest
from analyzer import analyze_migration_sql
from ai_service import get_ai_analysis

TEST_CASES = [
    ("1. DROP TABLE", "DROP TABLE users;"),
    ("2. DROP COLUMN", "ALTER TABLE users DROP COLUMN legacy_email;"),
    ("3. ADD COLUMN NOT NULL", "ALTER TABLE users ADD COLUMN phone VARCHAR(20) NOT NULL;"),
    ("4. ADD COLUMN NOT NULL DEFAULT", "ALTER TABLE users ADD COLUMN phone VARCHAR(20) NOT NULL DEFAULT 'UNKNOWN';"),
    ("5. ALTER COLUMN TYPE", "ALTER TABLE users ALTER COLUMN age TYPE INTEGER;"),
    ("6. CREATE INDEX", "CREATE INDEX idx_users_email ON users(email);"),
    ("7. CREATE INDEX CONCURRENTLY", "CREATE INDEX CONCURRENTLY idx_users_email ON users(email);"),
    ("8. TRUNCATE TABLE", "TRUNCATE TABLE users;"),
    ("9. DANGEROUS KEYWORD IN COMMENT", "-- DROP TABLE users;\nCREATE TABLE items (id INT);"),
    ("10. MULTIPLE RISKS", "DROP TABLE logs;\nALTER TABLE users DROP COLUMN legacy_id;")
]

def run_tests():
    print("=== RUNNING PHASE 5 TEST CASES ===")
    for title, sql in TEST_CASES:
        res = analyze_migration_sql(sql)
        print(f"\n--- {title} ---")
        print(f"SQL: {sql.strip()}")
        print(f"Score: {res.risk_score} | Severity: {res.severity}")
        print(f"Findings: {[f.rule_id for f in res.findings]}")
        print(f"Summary: {res.summary}")

if __name__ == "__main__":
    run_tests()
