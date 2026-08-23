import React, { useState } from 'react';
import { Copy, Check, Code2 } from 'lucide-react';

export default function SqlPanel({ title, sql, icon: Icon = Code2 }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (!sql) return;
    navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div style={{
      background: 'rgba(15, 23, 42, 0.6)',
      border: '1px solid var(--border-color)',
      borderRadius: '8px',
      overflow: 'hidden'
    }}>
      {/* Panel Header */}
      <div style={{
        padding: '0.5rem 0.85rem',
        background: 'rgba(30, 41, 59, 0.7)',
        borderBottom: '1px solid var(--border-color)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.82rem', fontWeight: '700', color: 'var(--text-primary)' }}>
          <Icon size={14} color="#38bdf8" />
          <span>{title}</span>
        </div>

        <button
          type="button"
          className="btn btn-secondary"
          style={{ fontSize: '0.72rem', padding: '0.2rem 0.5rem', height: '26px' }}
          onClick={handleCopy}
          disabled={!sql}
        >
          {copied ? (
            <>
              <Check size={12} color="#4ade80" />
              <span style={{ color: '#4ade80' }}>Copied!</span>
            </>
          ) : (
            <>
              <Copy size={12} color="#94a3b8" />
              <span>Copy SQL</span>
            </>
          )}
        </button>
      </div>

      {/* SQL Content */}
      <pre
        className="font-mono"
        style={{
          padding: '0.85rem 1rem',
          fontSize: '0.8rem',
          color: '#e2e8f0',
          background: '#090d16',
          overflowX: 'auto',
          whiteSpace: 'pre-wrap',
          lineHeight: '1.5',
          margin: 0
        }}
      >
        {sql || '-- No SQL available'}
      </pre>
    </div>
  );
}
