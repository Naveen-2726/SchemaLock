import pytest
from fingerprint import generate_fingerprint, verify_fingerprint, normalize_migration_sql
from main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_identical_sql_identical_fingerprint():
    sql1 = "ALTER TABLE users ADD COLUMN age INT;"
    sql2 = "ALTER TABLE users ADD COLUMN age INT;"
    assert generate_fingerprint(sql1) == generate_fingerprint(sql2)


def test_harmless_whitespace_and_comment_changes_same_fingerprint():
    sql1 = "ALTER TABLE users ADD COLUMN age INT;"
    sql2 = """
    -- Add age column to users table
    ALTER TABLE   users   ADD   COLUMN   age   INT;  
    """
    assert generate_fingerprint(sql1) == generate_fingerprint(sql2)


def test_different_sql_different_fingerprint():
    sql1 = "ALTER TABLE users ADD COLUMN age INT;"
    sql2 = "ALTER TABLE users DROP COLUMN age;"
    assert generate_fingerprint(sql1) != generate_fingerprint(sql2)


def test_empty_sql_fingerprint_behavior():
    fp = generate_fingerprint("")
    assert isinstance(fp, str)
    assert len(fp) == 64  # SHA-256 length


def test_verify_matching_fingerprint():
    sql = "DROP TABLE users;"
    fp = generate_fingerprint(sql)
    res = verify_fingerprint(sql, fp)
    assert res.status == "MATCH"
    assert res.actual_fingerprint == fp


def test_verify_mismatching_fingerprint():
    sql = "DROP TABLE users;"
    wrong_fp = "0000000000000000000000000000000000000000000000000000000000000000"
    res = verify_fingerprint(sql, wrong_fp)
    assert res.status == "DRIFT_DETECTED"


def test_verify_fingerprint_endpoint_match():
    sql = "ALTER TABLE users DROP COLUMN old_pass;"
    fp = generate_fingerprint(sql)
    
    response = client.post("/api/verify-fingerprint", json={
        "sql": sql,
        "expected_fingerprint": fp
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "MATCH"
    assert data["algorithm"] == "SHA-256"


def test_verify_fingerprint_endpoint_drift():
    sql = "ALTER TABLE users DROP COLUMN old_pass;"
    
    response = client.post("/api/verify-fingerprint", json={
        "sql": sql,
        "expected_fingerprint": "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "DRIFT_DETECTED"
