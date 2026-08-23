import React from 'react';
import { AlertCircle, FileCode2, CheckCircle2 } from 'lucide-react';

export default function FindingsList({ findings }) {
  if (!findings || findings.length === 0) {
    return (
      <div className="glass-panel" style={{ padding: '1.25rem', textAlign: 'center' }}>
        <div style={{ display: 'inline-flex', padding: '0.75rem', borderRadius: '50%', background: 'var(--low-bg)', border: '1px solid var(--low-border)', marginBottom: '0.5rem' }}>
          <CheckCircle2 size={24} color="var(--low-text)" />
        </div>
        <h4 style={{ fontSize: '0.95rem', fontWeight: '700', color: 'var(--low-text)' }}>
          No High-Risk Operations Found
        </h4>
        <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
          Deterministic checks passed. No destructive DDL statements detected.
        </p>
      </div>
    );
  }

  return (
    <div className="glass-panel" style={{ padding: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
        <AlertCircle size={18} color="#f97316" />
        <h3 style={{ fontSize: '1rem', fontWeight: '700', color: 'var(--text-primary)' }}>
          Deterministic Findings ({findings.length})
        </h3>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
        {findings.map((item, idx) => (
          <div
            key={idx}
            style={{
              background: `var(--${item.severity.toLowerCase()}-bg)`,
              border: `1px solid var(--${item.severity.toLowerCase()}-border)`,
              borderRadius: '8px',
              padding: '0.9rem 1rem',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.5rem'
            }}
          >
            {/* Header with Title & Badge */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.5rem' }}>
              <div>
                <span className={`badge badge-${item.severity}`} style={{ marginBottom: '0.3rem' }}>
                  {item.severity}
                </span>
                <h4 style={{ fontSize: '0.9rem', fontWeight: '700', color: '#ffffff' }}>
                  {item.title}
                </h4>
              </div>
              <span className="font-mono" style={{ fontSize: '0.7rem', color: 'var(--text-muted)', background: 'rgba(0, 0, 0, 0.3)', padding: '0.15rem 0.4rem', borderRadius: '4px' }}>
                {item.rule_id}
              </span>
            </div>

            {/* Explanation */}
            <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: '1.4' }}>
              {item.explanation}
            </p>

            {/* Matched SQL Code snippet */}
            {item.matched_sql && (
              <div style={{ marginTop: '0.2rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '0.2rem' }}>
                  <FileCode2 size={12} />
                  <span>Matched SQL:</span>
                </div>
                <pre
                  className="font-mono"
                  style={{
                    background: '#090d16',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    borderRadius: '6px',
                    padding: '0.5rem 0.75rem',
                    fontSize: '0.78rem',
                    color: '#e2e8f0',
                    overflowX: 'auto',
                    whiteSpace: 'pre-wrap'
                  }}
                >
                  {item.matched_sql}
                </pre>
              </div>
            )}

          </div>
        ))}
      </div>
    </div>
  );
}
