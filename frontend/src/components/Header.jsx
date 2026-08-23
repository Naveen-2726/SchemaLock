import React from 'react';
import { ShieldCheck, Cpu, ArrowRight, Database, AlertTriangle } from 'lucide-react';

export default function Header() {
  return (
    <header className="glass-panel" style={{ padding: '1.25rem 1.5rem' }}>
      <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', gap: '1rem' }}>
        
        {/* Brand Title */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            background: 'linear-gradient(135deg, #6366f1, #38bdf8)',
            padding: '0.6rem',
            borderRadius: '10px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 15px rgba(99, 102, 241, 0.5)'
          }}>
            <ShieldCheck size={26} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <h1 style={{ fontSize: '1.5rem', fontWeight: '800', letterSpacing: '-0.02em', background: 'linear-gradient(to right, #ffffff, #94a3b8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                SchemaLock
              </h1>
              <span style={{
                background: 'rgba(56, 189, 248, 0.15)',
                color: '#38bdf8',
                border: '1px solid rgba(56, 189, 248, 0.3)',
                fontSize: '0.7rem',
                fontWeight: '700',
                padding: '0.15rem 0.5rem',
                borderRadius: '4px'
              }}>
                PostgreSQL MVP
              </span>
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '0.1rem' }}>
              AI-powered PostgreSQL migration safety analyzer
            </p>
          </div>
        </div>

        {/* How It Works Pipeline */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          background: 'rgba(15, 23, 42, 0.6)',
          padding: '0.5rem 1rem',
          borderRadius: '8px',
          border: '1px solid var(--border-color)',
          fontSize: '0.78rem',
          color: 'var(--text-secondary)'
        }}>
          <span style={{ fontWeight: '600', color: 'var(--text-muted)' }}>How it works:</span>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: '#f1f5f9' }}>
            <Database size={13} color="#38bdf8" />
            <span>Deterministic AST Checks</span>
          </div>
          <ArrowRight size={12} color="#64748b" />

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: '#f1f5f9' }}>
            <Cpu size={13} color="#8b5cf6" />
            <span>Gemini AI Reasoning</span>
          </div>
          <ArrowRight size={12} color="#64748b" />

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: '#4ade80', fontWeight: '600' }}>
            <ShieldCheck size={13} />
            <span>Safer Migration & Rollback</span>
          </div>
        </div>

      </div>
    </header>
  );
}
