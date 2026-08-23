from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from analyzer import analyze_migration_sql, AnalysisResult
from ai_service import get_ai_analysis
from fingerprint import VerifyFingerprintRequest, VerifyFingerprintResponse, verify_fingerprint
from deployment_gate import evaluate_deployment_gate

app = FastAPI(
    title="SchemaLock API",
    description="AI-Powered PostgreSQL Migration Safety Analyzer API",
    version="1.0.0"
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    sql: str


@app.get("/")
def read_root():
    return {
        "message": "SchemaLock API is running",
        "docs": "/docs",
        "health": "/api/health"
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "SchemaLock API",
        "version": "1.0.0"
    }


@app.post("/api/analyze", response_model=AnalysisResult)
def analyze_sql(request: AnalyzeRequest):
    try:
        # Step 1: Run deterministic analysis & generate fingerprint
        result = analyze_migration_sql(request.sql)
        
        # Step 2: Pass deterministic findings to AI service
        findings_dict = [f.model_dump() for f in result.findings]
        ai_res = get_ai_analysis(
            sql=request.sql,
            risk_score=result.risk_score,
            severity=result.severity,
            findings=findings_dict
        )
        
        # Step 3: Attach AI analysis & re-evaluate Deployment Gate with AI Guard context
        result.ai_analysis = ai_res
        result.deployment_gate = evaluate_deployment_gate(
            risk_score=result.risk_score,
            severity=result.severity,
            findings=result.findings,
            risk_intelligence=result.risk_intelligence,
            migration_integrity=result.migration_integrity,
            ai_analysis=result.ai_analysis
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Analysis failed: {str(e)}")


@app.post("/api/verify-fingerprint", response_model=VerifyFingerprintResponse)
def verify_sql_fingerprint(request: VerifyFingerprintRequest):
    try:
        return verify_fingerprint(
            sql=request.sql,
            expected_fingerprint=request.expected_fingerprint
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Verification failed: {str(e)}")
