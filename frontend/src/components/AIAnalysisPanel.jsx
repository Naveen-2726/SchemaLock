import React from 'react';
import { Cpu, AlertTriangle, CheckCircle, ShieldCheck, Undo2, Lightbulb } from 'lucide-react';
import SqlPanel from './SqlPanel';

export default function AIAnalysisPanel({ aiAnalysis }) {
  if (!aiAnalysis) return null;

  const { status, risk_explanation, additional_risks, safer_migration, rollback_sql, recommendation } = aiAnalysis;

  const renderStatusBadge = () => {
    if (status === 'success') {
      return (
        <span style={{
          background: 'var(--low-bg)',
          border: '1px solid var(--low-border)',
          color: 'var(--low-text)',
          fontSize: '0.72rem',
          fontWeight: '700',
          padding: '0.2rem 0.55rem',
          borderRadius: '6px',
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.3rem'
        }}>
          <CheckCircle size={12} />
          AI Analysis Available
        </span>
      );
    } else if (status === 'unavailable') {
      return (
        <span style={{
          background: 'var(--medium-bg)',
          border: '1px solid var(--medium-border)',
          color: 'var(--medium-text)',
          fontSize: '0.72rem',
          fontWeight: '700',
          padding: '0.2rem 0.55rem',
          borderRadius: '6px',
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.3rem'
        }}>
          <AlertTriangle size={12} />
          AI Unavailable
        </span>
      );
    } else {
      return (
        <span style={{
          background: 'var(--critical-bg)',
          border: '1px solid var(--critical-border)',
          color: 'var(--critical-text)',
          fontSize: '0.72rem',
          fontWeight: '700',
          padding: '0.2rem 0.55rem',
          borderRadius: '6px',
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.3rem'
        }}>
          <AlertTriangle size={12} />
          AI Error
        </span>
      );
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      
      {/* AI Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Cpu size={20} color="#8b5cf6" />
          <h3 style={{ fontSize: '1rem', fontWeight: '700', color: 'var(--text-primary)' }}>
            Gemini Contextual AI Reasoning
          </h3>
        </div>
        {renderStatusBadge()}
      </div>

      {/* Risk Explanation */}
      <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '0.85rem 1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
        <h4 style={{ fontSize: '0.82rem', fontWeight: '700', color: 'var(--text-secondary)', marginBottom: '0.3rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Contextual Risk Assessment
        </h4>
        <p style={{ fontSize: '0.86rem', color: 'var(--text-primary)', lineHeight: '1.5' }}>
          {risk_explanation}
        </p>
      </div>

      {/* Additional Risks */}
      {additional_risks && additional_risks.length > 0 && (
        <div style={{ background: 'rgba(15, 23, 42, 0.4)', padding: '0.85rem 1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
          <h4 style={{ fontSize: '0.82rem', fontWeight: '700', color: 'var(--text-secondary)', marginBottom: '0.4rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Additional Contextual Risks
          </h4>
          <ul style={{ paddingLeft: '1.2rem', display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
            {additional_risks.map((risk, idx) => (
              <li key={idx} style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                {risk}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Safer Migration Code Panel */}
      <SqlPanel
        title="Recommended Safer Migration SQL"
        sql={safer_migration}
        icon={ShieldCheck}
      />

      {/* Rollback Code Panel */}
      <SqlPanel
        title="Rollback SQL"
        sql={rollback_sql}
        icon={Undo2}
      />

      {/* Operational Recommendation */}
      {recommendation && (
        <div style={{
          background: 'rgba(99, 102, 241, 0.1)',
          border: '1px solid rgba(99, 102, 241, 0.3)',
          padding: '0.85rem 1rem',
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '0.6rem'
        }}>
          <Lightbulb size={18} color="#8b5cf6" style={{ flexShrink: 0, marginTop: '0.1rem' }} />
          <div>
            <h4 style={{ fontSize: '0.82rem', fontWeight: '700', color: '#c7d2fe', marginBottom: '0.2rem' }}>
              Operational Deployment Advice
            </h4>
            <p style={{ fontSize: '0.82rem', color: '#a5b4fc', lineHeight: '1.4' }}>
              {recommendation}
            </p>
          </div>
        </div>
      )}

    </div>
  );
}
