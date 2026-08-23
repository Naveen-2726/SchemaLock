import os
import json
from unittest.mock import patch, MagicMock
import pytest
from analyzer import analyze_migration_sql
from ai_service import get_ai_analysis, AIAnalysis
from main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_gemini_missing_api_key_fallback(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    
    analysis = get_ai_analysis(
        sql="ALTER TABLE users DROP COLUMN email;",
        risk_score=30,
        severity="HIGH",
        findings=[]
    )
    
    assert analysis.status == "unavailable"
    assert "GEMINI_API_KEY is not configured" in analysis.risk_explanation
    assert analysis.error_message == "GEMINI_API_KEY missing"


def test_gemini_success_mocked(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "dummy_test_key_123")
    
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "risk_explanation": "Dropping column email is destructive.",
        "additional_risks": ["Active application code referencing email will throw SQL errors."],
        "safer_migration": "-- Step 1: Deprecate column in application code\n-- Step 2: Drop column later",
        "rollback_sql": "ALTER TABLE users ADD COLUMN email VARCHAR(255);",
        "recommendation": "Deploy code updates before dropping database columns."
    })

    with patch("google.genai.Client") as MockClient:
        mock_client_instance = MagicMock()
        MockClient.return_value = mock_client_instance
        mock_client_instance.models.generate_content.return_value = mock_response

        analysis = get_ai_analysis(
            sql="ALTER TABLE users DROP COLUMN email;",
            risk_score=30,
            severity="HIGH",
            findings=[{"rule_id": "DROP_COLUMN", "severity": "HIGH"}]
        )

        assert analysis.status == "success"
        assert "Dropping column email" in analysis.risk_explanation
        assert len(analysis.additional_risks) == 1
        assert "ALTER TABLE users ADD COLUMN email" in analysis.rollback_sql


def test_gemini_malformed_json_fallback(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "dummy_test_key_123")
    
    mock_response = MagicMock()
    mock_response.text = "NOT_VALID_JSON_STRING"

    with patch("google.genai.Client") as MockClient:
        mock_client_instance = MagicMock()
        MockClient.return_value = mock_client_instance
        mock_client_instance.models.generate_content.return_value = mock_response

        analysis = get_ai_analysis(
            sql="ALTER TABLE users DROP COLUMN email;",
            risk_score=30,
            severity="HIGH",
            findings=[]
        )

        assert analysis.status == "error"
        assert "encountered an error" in analysis.risk_explanation
        assert analysis.error_message is not None


def test_gemini_api_exception_fallback(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "dummy_test_key_123")

    with patch("google.genai.Client") as MockClient:
        mock_client_instance = MagicMock()
        MockClient.return_value = mock_client_instance
        mock_client_instance.models.generate_content.side_effect = Exception("API rate limit exceeded")

        analysis = get_ai_analysis(
            sql="ALTER TABLE users DROP COLUMN email;",
            risk_score=30,
            severity="HIGH",
            findings=[]
        )

        assert analysis.status == "error"
        assert "API rate limit exceeded" in analysis.error_message


def test_api_endpoint_preserves_deterministic_findings_on_ai_failure(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    
    response = client.post("/api/analyze", json={
        "sql": "DROP TABLE critical_data;"
    })

    assert response.status_code == 200
    data = response.json()
    
    # Deterministic findings must be intact
    assert data["risk_score"] == 50
    assert data["severity"] == "CRITICAL"
    assert len(data["findings"]) == 1
    assert data["findings"][0]["rule_id"] == "DROP_TABLE"
    
    # AI analysis should reflect fallback status without crashing API
    assert data["ai_analysis"]["status"] == "unavailable"
