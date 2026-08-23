"""
SchemaLock Migration Fingerprint & Integrity Check Engine.

Generates deterministic SHA-256 fingerprints for PostgreSQL migration SQL files.
Normalizes whitespace, line endings, and comments so harmless formatting changes 
produce identical integrity fingerprints while detecting any content modification or drift.
"""

import hashlib
import re
from typing import Dict, Any
from pydantic import BaseModel
import sqlparse
from sqlparse.sql import Comment


class MigrationIntegrity(BaseModel):
    algorithm: str = "SHA-256"
    fingerprint: str
    status: str  # "GENERATED" | "MATCH" | "DRIFT_DETECTED"


class VerifyFingerprintRequest(BaseModel):
    sql: str
    expected_fingerprint: str


class VerifyFingerprintResponse(BaseModel):
    algorithm: str = "SHA-256"
    expected_fingerprint: str
    actual_fingerprint: str
    status: str  # "MATCH" | "DRIFT_DETECTED"


def normalize_migration_sql(sql: str) -> str:
    """
    Normalize PostgreSQL migration SQL for deterministic SHA-256 fingerprinting.
    - Converts CRLF to LF line endings
    - Strips comments (single & multi-line)
    - Trims whitespace and collapses repeated inline spaces/newlines
    """
    if not sql or not sql.strip():
        return ""

    # Normalize line endings
    normalized = sql.replace("\r\n", "\n").replace("\r", "\n")

    # Strip comments using sqlparse tokenization
    parsed = sqlparse.parse(normalized)
    clean_statements = []
    for stmt in parsed:
        tokens = [
            t.value for t in stmt.flatten() 
            if not isinstance(t, Comment) and t.ttype not in (
                sqlparse.tokens.Comment, 
                sqlparse.tokens.Comment.Single, 
                sqlparse.tokens.Comment.Multiline
            )
        ]
        stmt_text = "".join(tokens)
        if stmt_text.strip():
            clean_statements.append(stmt_text.strip())

    # Rejoin statements with single newline
    combined = "\n".join(clean_statements)

    # Collapse multiple consecutive spaces/tabs to single space
    lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in combined.split("\n")]
    lines = [line for line in lines if line]

    return "\n".join(lines).upper()


def generate_fingerprint(sql: str) -> str:
    """Generate SHA-256 hex digest for normalized migration SQL."""
    normalized = normalize_migration_sql(sql)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def verify_fingerprint(sql: str, expected_fingerprint: str) -> VerifyFingerprintResponse:
    """Verify if target SQL content matches expected SHA-256 fingerprint."""
    clean_expected = (expected_fingerprint or "").strip().lower()
    actual = generate_fingerprint(sql)
    
    is_match = (actual.lower() == clean_expected)
    status = "MATCH" if is_match else "DRIFT_DETECTED"

    return VerifyFingerprintResponse(
        algorithm="SHA-256",
        expected_fingerprint=clean_expected,
        actual_fingerprint=actual,
        status=status
    )
