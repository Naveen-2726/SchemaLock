import React from 'react';
import { ShieldAlert, ShieldCheck, AlertTriangle } from 'lucide-react';

export default function RiskScoreCard({ riskScore, severity, summary }) {
  const getIcon = () => {
    if (severity === 'CRITICAL' || severity === 'HIGH') {
      return <ShieldAlert size={28} color={`var(--${severity.toLowerCase()}-text)`} />;
    } else if (severity === 'MEDIUM') {
      return <AlertTriangle size={28} color="var(--medium-text)" />;
    }
    return <ShieldCheck size={28} color="var(--low-text)" />;
  };

  return (
    <div className="glass-panel" style={{ padding: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap' }}>
        
        {/* Score & Badge */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {/* Score Circle */}
          <div style={{
            width: '68px',
            height: '68px',
            borderRadius: '50%',
            background: `var(--${severity.toLowerCase()}-bg)`,
            border: `2px solid var(--${severity.toLowerCase()}-border)`,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: `0 0 15px var(--${severity.toLowerCase()}-bg)`
          }}>
            <span style={{ fontSize: '1.4rem', fontWeight: '800', color: `var(--${severity.toLowerCase()}-text)`, lineHeight: 1 }}>
              {riskScore}
            </span>
            <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: '600' }}>
              / 100
            </span>
          </div>

          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.2rem' }}>
              <span className={`badge badge-${severity}`}>
                {severity} RISK
              </span>
            </div>
            <h3 style={{ fontSize: '1rem', fontWeight: '700', color: 'var(--text-primary)' }}>
              Migration Risk Score
            </h3>
          </div>
        </div>

        {/* Dynamic Risk Indicator */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(15, 23, 42, 0.4)', padding: '0.5rem 0.85rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
          {getIcon()}
        </div>

      </div>

      {/* Summary Description */}
      <p style={{ marginTop: '1rem', fontSize: '0.85rem', color: 'var(--text-secondary)', background: 'rgba(15, 23, 42, 0.5)', padding: '0.65rem 0.85rem', borderRadius: '6px', borderLeft: `3px solid var(--${severity.toLowerCase()}-badge)` }}>
        {summary}
      </p>
    </div>
  );
}
