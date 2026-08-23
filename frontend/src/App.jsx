import React, { useState } from 'react';
import Header from './components/Header';
import MigrationEditor from './components/MigrationEditor';
import RiskScoreCard from './components/RiskScoreCard';
import RiskIntelligencePanel from './components/RiskIntelligencePanel';
import MigrationIntegrityPanel from './components/MigrationIntegrityPanel';
import DeploymentGatePanel from './components/DeploymentGatePanel';
import FindingsList from './components/FindingsList';
import AIAnalysisPanel from './components/AIAnalysisPanel';
import { AlertTriangle, ShieldCheck, Database, Sparkles } from 'lucide-react';

const DEFAULT_SQL = `ALTER TABLE users
ADD COLUMN phone VARCHAR(20) NOT NULL;

ALTER TABLE users
DROP COLUMN legacy_email;`;

export default function App() {
  const [sql, setSql] = useState(DEFAULT_SQL);
  const [analyzedSql, setAnalyzedSql] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    if (!sql || !sql.trim()) {
      setError("Please input or select a PostgreSQL migration SQL statement before analyzing.");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ sql }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server returned status ${response.status}`);
      }

      const data = await response.json();
      setAnalysisResult(data);
      setAnalyzedSql(sql);
    } catch (err) {
      console.error("Analysis request error:", err);
      setError(`Backend API Connection Failed: ${err.message}. Ensure FastAPI server is running on http://127.0.0.1:8000`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Brand Header */}
      <Header />

      {/* Main Analysis Interface */}
      <main className="main-grid">
        
        {/* Left Column: Migration Editor */}
        <div>
          <MigrationEditor
            sql={sql}
            setSql={setSql}
            onAnalyze={handleAnalyze}
            isLoading={isLoading}
          />
        </div>

        {/* Right Column: Analysis Results */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          
          {/* Error Banner */}
          {error && (
            <div className="glass-panel" style={{
              padding: '1rem 1.25rem',
              background: 'var(--critical-bg)',
              border: '1px solid var(--critical-border)',
              color: 'var(--critical-text)',
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem'
            }}>
              <AlertTriangle size={20} style={{ flexShrink: 0 }} />
              <div style={{ fontSize: '0.85rem' }}>
                <strong style={{ display: 'block', fontWeight: '700' }}>Analysis Error</strong>
                {error}
              </div>
            </div>
          )}

          {/* Analysis View or Initial State */}
          {analysisResult ? (
            <>
              {/* Top-Level Risk Score */}
              <RiskScoreCard
                riskScore={analysisResult.risk_score}
                severity={analysisResult.severity}
                summary={analysisResult.summary}
              />

              {/* Deployment Gate Decision */}
              <DeploymentGatePanel
                deploymentGate={analysisResult.deployment_gate}
              />

              {/* Migration Integrity & SHA-256 Fingerprint */}
              <MigrationIntegrityPanel
                migrationIntegrity={analysisResult.migration_integrity}
                currentSql={sql}
                analyzedSql={analyzedSql}
              />

              {/* Risk Intelligence & Blast Radius */}
              <RiskIntelligencePanel
                riskIntelligence={analysisResult.risk_intelligence}
              />

              {/* Deterministic Findings */}
              <FindingsList findings={analysisResult.findings} />

              {/* AI Analysis & Recommendations */}
              <AIAnalysisPanel aiAnalysis={analysisResult.ai_analysis} />
            </>
          ) : (
            <div className="glass-panel" style={{
              padding: '3rem 2rem',
              textAlign: 'center',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              minHeight: '480px'
            }}>
              <div style={{
                width: '64px',
                height: '64px',
                borderRadius: '50%',
                background: 'rgba(99, 102, 241, 0.15)',
                border: '1px solid rgba(99, 102, 241, 0.3)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '1rem'
              }}>
                <Sparkles size={32} color="#8b5cf6" />
              </div>

              <h3 style={{ fontSize: '1.2rem', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
                Ready to Safety-Check Your PostgreSQL Migration
              </h3>

              <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', maxWidth: '420px', lineHeight: '1.5', marginBottom: '1.5rem' }}>
                Paste your DDL statement into the editor or select an example preset, then click <strong>"Analyze Migration"</strong> to run AST rules, SHA-256 fingerprinting, and Gemini AI reasoning.
              </p>

              <div style={{
                display: 'flex',
                gap: '1rem',
                fontSize: '0.8rem',
                color: 'var(--text-muted)'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                  <Database size={14} color="#38bdf8" />
                  <span>AST Safety Rules</span>
                </div>
                <span>•</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                  <ShieldCheck size={14} color="#4ade80" />
                  <span>Zero Database Mutation</span>
                </div>
              </div>
            </div>
          )}

        </div>

      </main>
    </div>
  );
}
