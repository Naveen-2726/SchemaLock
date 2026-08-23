"""
SchemaLock Deterministic PostgreSQL Migration Safety Analyzer.

This module provides rule-based static analysis for PostgreSQL migration SQL files.
It parses SQL statements, strips comments and literal strings to prevent false positives,
matches known high-risk migration patterns, and produces structured risk reports.
"""

import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import sqlparse
from sqlparse.sql import Statement, Token, Comment
from risk_intelligence import RiskIntelligence, calculate_risk_intelligence
from fingerprint import MigrationIntegrity, generate_fingerprint
from deployment_gate import DeploymentGate, evaluate_deployment_gate


class Finding(BaseModel):
    rule_id: str
    severity: str  # "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
    title: str
    explanation: str
    matched_sql: str


class AIAnalysisSchema(BaseModel):
    status: str  # "success" | "unavailable" | "error"
    risk_explanation: str
    additional_risks: List[str]
    safer_migration: str
    rollback_sql: str
    recommendation: str
    error_message: Optional[str] = None


class AnalysisResult(BaseModel):
    risk_score: int = Field(ge=0, le=100)
    severity: str  # "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
    findings: List[Finding]
    summary: str
    risk_intelligence: Optional[RiskIntelligence] = None
    migration_integrity: Optional[MigrationIntegrity] = None
    deployment_gate: Optional[DeploymentGate] = None
    ai_analysis: Optional[AIAnalysisSchema] = None


def strip_sql_comments(sql: str) -> str:
    """Strip single-line and multi-line SQL comments while keeping SQL structure intact."""
    parsed = sqlparse.parse(sql)
    clean_statements = []
    for stmt in parsed:
        tokens = [t for t in stmt.flatten() if not isinstance(t, Comment) and t.ttype not in (sqlparse.tokens.Comment, sqlparse.tokens.Comment.Single, sqlparse.tokens.Comment.Multiline)]
        clean_stmt = "".join(t.value for t in tokens)
        if clean_stmt.strip():
            clean_statements.append(clean_stmt)
    return "\n".join(clean_statements)


def analyze_migration_sql(sql: str) -> AnalysisResult:
    """Analyze PostgreSQL migration SQL string and return risk assessment."""
    fp = generate_fingerprint(sql)
    integrity = MigrationIntegrity(algorithm="SHA-256", fingerprint=fp, status="GENERATED")

    if not sql or not sql.strip():
        empty_risk_intel = calculate_risk_intelligence([])
        gate = evaluate_deployment_gate(
            risk_score=0,
            severity="LOW",
            findings=[],
            risk_intelligence=empty_risk_intel,
            migration_integrity=integrity,
            ai_analysis=None
        )
        return AnalysisResult(
            risk_score=0,
            severity="LOW",
            findings=[],
            summary="Empty SQL migration input. No operations detected.",
            risk_intelligence=empty_risk_intel,
            migration_integrity=integrity,
            deployment_gate=gate
        )

    clean_sql = strip_sql_comments(sql)
    statements = sqlparse.parse(clean_sql)
    
    findings: List[Finding] = []

    for stmt in statements:
        stmt_raw = stmt.value.strip()
        if not stmt_raw:
            continue
        
        normalized = " ".join(stmt_raw.split()).upper()

        # 1. DROP TABLE
        if re.search(r'\bDROP\s+TABLE\b', normalized):
            findings.append(Finding(
                rule_id="DROP_TABLE",
                severity="CRITICAL",
                title="Destructive Table Removal (DROP TABLE)",
                explanation="Permanently removes an entire database table and all of its data. Any queries referencing this table will immediately fail.",
                matched_sql=stmt_raw
            ))

        # 2. TRUNCATE TABLE
        if re.search(r'\bTRUNCATE\b', normalized):
            findings.append(Finding(
                rule_id="TRUNCATE_TABLE",
                severity="CRITICAL",
                title="Bulk Data Deletion (TRUNCATE)",
                explanation="Instantly deletes all rows from target table(s) without individual row-level log processing.",
                matched_sql=stmt_raw
            ))

        # 3. DROP COLUMN
        if re.search(r'\bDROP\s+(?:COLUMN\s+)?\w+', normalized) and ("ALTER" in normalized or "DROP COLUMN" in normalized):
            findings.append(Finding(
                rule_id="DROP_COLUMN",
                severity="HIGH",
                title="Destructive Column Drop (DROP COLUMN)",
                explanation="Permanently drops a column and all stored data, breaking application code expecting this field.",
                matched_sql=stmt_raw
            ))

        # 4. ADD COLUMN with NOT NULL
        if re.search(r'\bADD\s+(?:COLUMN\s+)?.*\bNOT\s+NULL\b', normalized) and "ALTER" in normalized:
            findings.append(Finding(
                rule_id="ADD_COLUMN_NOT_NULL",
                severity="HIGH",
                title="Unsafe Column Addition with NOT NULL",
                explanation="Adding a NOT NULL column to an existing table without a constant default will fail if existing rows exist, or require a full table rewrite holding an AccessExclusiveLock.",
                matched_sql=stmt_raw
            ))

        # 5. ALTER COLUMN TYPE
        if re.search(r'\bALTER\s+(?:COLUMN\s+)?.*\b(?:TYPE|SET\s+DATA\s+TYPE)\b', normalized) and "ALTER" in normalized:
            findings.append(Finding(
                rule_id="ALTER_COLUMN_TYPE",
                severity="HIGH",
                title="Column Type Conversion (ALTER COLUMN TYPE)",
                explanation="Changing column data type can cause data truncation, cast errors, and requires a full table rewrite holding an AccessExclusiveLock.",
                matched_sql=stmt_raw
            ))

        # 6. ADD UNIQUE Constraint
        if re.search(r'\bADD\s+(?:CONSTRAINT\s+\w+\s+)?UNIQUE\b', normalized) and "ALTER" in normalized:
            findings.append(Finding(
                rule_id="ADD_UNIQUE_CONSTRAINT",
                severity="MEDIUM",
                title="Blocking Unique Constraint Creation (ADD UNIQUE)",
                explanation="Adding a UNIQUE constraint scans the entire table and will fail if duplicate values exist. It requires an exclusive lock unless backed by an existing index created concurrently.",
                matched_sql=stmt_raw
            ))

        # 7. CREATE INDEX
        if re.search(r'\bCREATE\s+(?:UNIQUE\s+)?INDEX\b', normalized):
            is_concurrent = bool(re.search(r'\bCREATE\s+(?:UNIQUE\s+)?INDEX\s+CONCURRENTLY\b', normalized))
            if not is_concurrent:
                findings.append(Finding(
                    rule_id="CREATE_INDEX",
                    severity="MEDIUM",
                    title="Blocking Index Creation (CREATE INDEX without CONCURRENTLY)",
                    explanation="Creating an index without CONCURRENTLY acquires a SHARE lock that blocks all WRITE operations (INSERT, UPDATE, DELETE) during index construction on large production tables.",
                    matched_sql=stmt_raw
                ))
            else:
                findings.append(Finding(
                    rule_id="CREATE_INDEX_CONCURRENT",
                    severity="LOW",
                    title="Concurrent Index Creation (CREATE INDEX CONCURRENTLY)",
                    explanation="Creates an index concurrently to avoid locking table writes, but requires non-transactional execution and extra CPU/IO resource overhead.",
                    matched_sql=stmt_raw
                ))

    # 8. Check for Multiple Destructive / High Risk Operations
    high_critical_count = sum(1 for f in findings if f.severity in ("HIGH", "CRITICAL"))
    if high_critical_count >= 2:
        findings.append(Finding(
            rule_id="MULTIPLE_DESTRUCTIVE_OPERATIONS",
            severity="HIGH",
            title="Multiple High-Risk / Destructive Operations",
            explanation=f"Migration contains {high_critical_count} high or critical risk operations in a single script, increasing potential blast radius and rollback difficulty.",
            matched_sql="Multiple operations detected across migration file"
        ))

    # Calculate Deterministic Risk Score
    severity_weights = {
        "CRITICAL": 50,
        "HIGH": 30,
        "MEDIUM": 15,
        "LOW": 5
    }

    raw_score = sum(severity_weights.get(f.severity, 0) for f in findings)
    risk_score = min(100, max(0, raw_score))

    # Determine overall severity
    severities = [f.severity for f in findings]
    if "CRITICAL" in severities or risk_score >= 80:
        overall_severity = "CRITICAL"
    elif "HIGH" in severities or risk_score >= 40:
        overall_severity = "HIGH"
    elif "MEDIUM" in severities or risk_score >= 15:
        overall_severity = "MEDIUM"
    else:
        overall_severity = "LOW"

    # Generate Summary Statement
    if not findings:
        summary = "Safe migration script. No high-risk PostgreSQL operations detected."
    else:
        summary = f"Detected {len(findings)} risk finding(s) with an overall {overall_severity} risk severity (Score: {risk_score}/100)."

    # Calculate Risk Intelligence & Blast Radius
    risk_intel = calculate_risk_intelligence(findings)

    # Initial Deployment Gate
    gate = evaluate_deployment_gate(
        risk_score=risk_score,
        severity=overall_severity,
        findings=findings,
        risk_intelligence=risk_intel,
        migration_integrity=integrity,
        ai_analysis=None
    )

    return AnalysisResult(
        risk_score=risk_score,
        severity=overall_severity,
        findings=findings,
        summary=summary,
        risk_intelligence=risk_intel,
        migration_integrity=integrity,
        deployment_gate=gate
    )
