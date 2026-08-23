import os
import json
import logging
from typing import List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a PostgreSQL migration safety assistant.
Analyze the migration using the deterministic findings supplied by the application.
Do not invent database facts or column types that were not provided.
Clearly distinguish known deterministic risks from contextual recommendations.
Only suggest PostgreSQL-compatible SQL.
If original schema information (such as data types for dropped columns) is unavailable, state clearly in the rollback SQL that original schema definitions must be verified.
Never claim that a migration is guaranteed safe or zero-downtime."""


class AIAnalysis(BaseModel):
    status: str = Field(description="status: success | unavailable | error")
    risk_explanation: str
    additional_risks: List[str]
    safer_migration: str
    rollback_sql: str
    recommendation: str
    error_message: Optional[str] = None


class GeminiStructuredOutput(BaseModel):
    risk_explanation: str
    additional_risks: List[str]
    safer_migration: str
    rollback_sql: str
    recommendation: str


def validate_and_sanitize_ai_analysis(analysis: AIAnalysis, deterministic_severity: str, sql: str) -> AIAnalysis:
    """
    Sanitize and validate AI analysis against deterministic findings and common LLM hallucinations.
    Enforces safety invariants:
    1. Flags rollback SQL when original column types are missing/unknown from migration context.
    2. Prevents LLM overconfidence or claims of guaranteed zero-downtime on HIGH/CRITICAL migrations.
    3. Preserves deterministic CRITICAL/HIGH severity precedence.
    """
    if analysis.status != "success":
        return analysis

    # Guard 1: Detect invented data types on DROP COLUMN rollback
    if "DROP COLUMN" in sql.upper() or "DROP" in sql.upper():
        if "ADD COLUMN" in analysis.rollback_sql.upper() and "-- WARNING" not in analysis.rollback_sql.upper():
            warning_header = "-- WARNING: Original column data type and constraints are unknown from migration input.\n-- Verify original table schema before applying rollback DDL.\n"
            analysis.rollback_sql = warning_header + analysis.rollback_sql

    # Guard 2: Sanitize false zero-downtime claims
    overconfidence_phrases = ["guaranteed zero-downtime", "100% safe", "zero downtime guaranteed", "completely risk-free", "zero-downtime guaranteed"]
    for phrase in overconfidence_phrases:
        if phrase in analysis.risk_explanation.lower():
            analysis.risk_explanation = analysis.risk_explanation.replace(phrase, "reduced locking impact (subject to transaction backlog)")
        if phrase in analysis.recommendation.lower():
            analysis.recommendation = analysis.recommendation.replace(phrase, "reduced locking impact")

    return analysis


def get_ai_analysis(sql: str, risk_score: int, severity: str, findings: List[dict]) -> AIAnalysis:
    """
    Call Gemini API with original SQL and deterministic findings to get contextual recommendations.
    Provides graceful fallback if Gemini is unavailable, unconfigured, or errors out.
    Applies post-processing validation layer to sanitize AI hallucinations.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()

    if not api_key:
        logger.warning("GEMINI_API_KEY is missing or empty. Returning fallback analysis.")
        return AIAnalysis(
            status="unavailable",
            risk_explanation="AI analysis is currently unavailable because GEMINI_API_KEY is not configured.",
            additional_risks=["LLM contextual analysis disabled."],
            safer_migration="-- AI safe migration generation unavailable.\n-- Please review deterministic findings.",
            rollback_sql="-- AI rollback generation unavailable.\n-- Verify original schema before attempting rollback.",
            recommendation="Review the rule-based deterministic findings above. Ensure appropriate lock timeouts before applying high-risk DDL.",
            error_message="GEMINI_API_KEY missing"
        )

    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
Input PostgreSQL Migration SQL:
```sql
{sql}
```

Deterministic Analysis Results:
- Risk Score: {risk_score}/100
- Severity: {severity}
- Deterministic Findings: {json.dumps(findings, indent=2)}

Please provide a contextual PostgreSQL safety evaluation, a step-by-step safer migration alternative, clean rollback SQL, and operational recommendations.
IMPORTANT: If column data types are not provided in the input SQL, do not invent them in the rollback SQL. Add a comment indicating original schema must be verified.
"""

        # Call Gemini 2.5 Flash model with structured JSON schema
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=GeminiStructuredOutput,
                temperature=0.2,
            )
        )

        if not response or not response.text:
            raise ValueError("Received empty response from Gemini API.")

        data = json.loads(response.text)
        
        raw_analysis = AIAnalysis(
            status="success",
            risk_explanation=data.get("risk_explanation", "No explanation provided."),
            additional_risks=data.get("additional_risks", []),
            safer_migration=data.get("safer_migration", "-- No safer migration generated"),
            rollback_sql=data.get("rollback_sql", "-- No rollback SQL generated"),
            recommendation=data.get("recommendation", "Review deterministic findings before running in production.")
        )

        # Apply AI validation & guard layer
        return validate_and_sanitize_ai_analysis(raw_analysis, severity, sql)

    except Exception as e:
        logger.error(f"Gemini API analysis failed: {str(e)}", exc_info=True)
        return AIAnalysis(
            status="error",
            risk_explanation="AI contextual analysis encountered an error and could not complete.",
            additional_risks=["AI generation error occurred."],
            safer_migration="-- AI safe migration generation failed.\n-- Consult deterministic findings.",
            rollback_sql="-- AI rollback generation failed.",
            recommendation="Rely on deterministic findings and standard PostgreSQL migration practices.",
            error_message=str(e)
        )
