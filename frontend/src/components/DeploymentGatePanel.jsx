import React from 'react';
import { ShieldCheck, ShieldAlert, ShieldX, Ban, CircleAlert, CheckCircle2, GitBranch } from 'lucide-react';

const STATUS_CONFIG = {
  READY_FOR_REVIEW: {
    label: 'READY FOR REVIEW',
    variant: 'low',
    icon: ShieldCheck,
    description: 'This migration is a low-risk candidate for standard deployment review.'
  },
  REQUIRES_REVIEW: {
    label: 'REQUIRES REVIEW',
    variant: 'medium',
    icon: ShieldAlert,
    description: 'This migration requires senior peer review before staging execution.'
  },
  BLOCKED: {
    label: 'BLOCKED',
    variant: 'critical',
    icon: ShieldX,
    description: 'This migration is blocked from deployment due to critical risk factors.'
  }
};

export default function DeploymentGatePanel({ deploymentGate }) {
  if (!deploymentGate) return null;

  const { status, reason, blocking_factors, review_factors } = deploymentGate;
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.REQUIRES_REVIEW;
  const Icon = config.icon;
  const factors = status === 'BLOCKED' ? blocking_factors : review_factors;
  const FactorIcon = status === 'BLOCKED' ? Ban : (status === 'READY_FOR_REVIEW' ? CheckCircle2 : CircleAlert);

  return (
    <div
      className="glass-panel"
      style={{
        padding: '1.25rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem',
        border: `1px solid var(--${config.variant}-border)`,
        background: `linear-gradient(180deg, var(--${config.variant}-bg) 0%, var(--bg-card) 45%)`
      }}
    >
      {/* Panel Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <GitBranch size={20} color={`var(--${config.variant}-text)`} />
          <h3 style={{ fontSize: '1rem', fontWeight: '700', color: 'var(--text-primary)' }}>
            Deployment Gate
          </h3>
        </div>
        <span className={`badge badge-${status === 'READY_FOR_REVIEW' ? 'LOW' : status === 'REQUIRES_REVIEW' ? 'MEDIUM' : 'CRITICAL'}`}>
          {config.label}
        </span>
      </div>

      {/* Status Callout */}
      <div style={{
        display: 'flex',
        alignItems: 'flex-start',
        gap: '0.75rem',
        background: `var(--${config.variant}-bg)`,
        border: `1px solid var(--${config.variant}-border)`,
        borderRadius: '8px',
        padding: '0.9rem 1.1rem'
      }}>
        <Icon size={22} color={`var(--${config.variant}-text)`} style={{ flexShrink: 0, marginTop: '0.1rem' }} />
        <div>
          <strong style={{ display: 'block', fontSize: '0.9rem', fontWeight: '700', color: `var(--${config.variant}-text)`, marginBottom: '0.2rem' }}>
            {reason}
          </strong>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            {config.description}
          </p>
        </div>
      </div>

      {/* Blocking / Review Factors */}
      {factors && factors.length > 0 && (
        <div style={{ background: 'rgba(15, 23, 42, 0.5)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '0.85rem 1rem' }}>
          <h4 style={{ fontSize: '0.78rem', fontWeight: '700', color: 'var(--text-secondary)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            {status === 'BLOCKED' ? 'Blocking Factors' : 'Review Factors'}
          </h4>
          <ul style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem', paddingLeft: 0, listStyle: 'none' }}>
            {factors.map((factor, idx) => (
              <li key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem', fontSize: '0.83rem', color: 'var(--text-primary)', lineHeight: '1.4' }}>
                <FactorIcon size={14} color={`var(--${config.variant}-text)`} style={{ flexShrink: 0, marginTop: '0.15rem' }} />
                <span>{factor}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
