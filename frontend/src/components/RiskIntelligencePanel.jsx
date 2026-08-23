import React from 'react';
import { ShieldAlert, Lock, Code2, Gauge, Flame, AlertCircle } from 'lucide-react';

export default function RiskIntelligencePanel({ riskIntelligence }) {
  if (!riskIntelligence) return null;

  const { data_loss_risk, locking_risk, compatibility_risk, performance_risk, blast_radius } = riskIntelligence;

  const dimensions = [
    {
      title: 'Data Loss Risk',
      data: data_loss_risk,
      icon: ShieldAlert,
      color: '#ef4444'
    },
    {
      title: 'Locking Impact',
      data: locking_risk,
      icon: Lock,
      color: '#f97316'
    },
    {
      title: 'App Compatibility',
      data: compatibility_risk,
      icon: Code2,
      color: '#eab308'
    },
    {
      title: 'Performance Risk',
      data: performance_risk,
      icon: Gauge,
      color: '#38bdf8'
    }
  ];

  return (
    <div className="glass-panel" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      
      {/* Panel Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Flame size={20} color="#f97316" />
          <h3 style={{ fontSize: '1rem', fontWeight: '700', color: 'var(--text-primary)' }}>
            Risk Intelligence & Blast Radius
          </h3>
        </div>
        <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
          Deterministic Multi-Dimensional Matrix
        </span>
      </div>

      {/* 4 Categories Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem' }}>
        {dimensions.map((dim, idx) => {
          const Icon = dim.icon;
          const { level, score, reasons } = dim.data;
          return (
            <div
              key={idx}
              style={{
                background: 'rgba(15, 23, 42, 0.5)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                padding: '0.85rem 0.95rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.4rem'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.82rem', fontWeight: '700', color: 'var(--text-primary)' }}>
                  <Icon size={14} color={dim.color} />
                  <span>{dim.title}</span>
                </div>
                <span className={`badge badge-${level}`} style={{ fontSize: '0.65rem', padding: '0.15rem 0.4rem' }}>
                  {level}
                </span>
              </div>

              <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.3rem', marginTop: '0.2rem' }}>
                <span style={{ fontSize: '1.2rem', fontWeight: '800', color: `var(--${level.toLowerCase()}-text)` }}>
                  {score}
                </span>
                <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>/ 100</span>
              </div>

              <div style={{ marginTop: '0.2rem' }}>
                {reasons && reasons.length > 0 && (
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', lineHeight: '1.3', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                    • {reasons[0]}
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Potential Blast Radius Card */}
      {blast_radius && (
        <div style={{
          background: `var(--${blast_radius.level.toLowerCase()}-bg)`,
          border: `1px solid var(--${blast_radius.level.toLowerCase()}-border)`,
          borderRadius: '8px',
          padding: '0.9rem 1.1rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '0.75rem'
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.2rem' }}>
              <AlertCircle size={16} color={`var(--${blast_radius.level.toLowerCase()}-text)`} />
              <h4 style={{ fontSize: '0.88rem', fontWeight: '700', color: '#ffffff' }}>
                Potential Blast Radius
              </h4>
              <span className={`badge badge-${blast_radius.level}`} style={{ fontSize: '0.65rem' }}>
                {blast_radius.level}
              </span>
            </div>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
              Operational impact metrics calculated across database schema and application boundaries.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '1.25rem', flexWrap: 'wrap' }}>
            <div style={{ textAlign: 'center' }}>
              <span style={{ display: 'block', fontSize: '1.1rem', fontWeight: '800', color: '#ffffff' }}>
                {blast_radius.destructive_operations}
              </span>
              <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                Destructive Ops
              </span>
            </div>

            <div style={{ textAlign: 'center' }}>
              <span style={{ display: 'block', fontSize: '1.1rem', fontWeight: '800', color: '#ffffff' }}>
                {blast_radius.affected_operations}
              </span>
              <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                Affected Ops
              </span>
            </div>

            <div style={{ textAlign: 'center' }}>
              <span className={`badge badge-${blast_radius.application_compatibility}`} style={{ fontSize: '0.75rem', marginTop: '0.2rem' }}>
                {blast_radius.application_compatibility}
              </span>
              <span style={{ display: 'block', fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginTop: '0.15rem' }}>
                App Compatibility
              </span>
            </div>
          </div>

        </div>
      )}

    </div>
  );
}
