import React from 'react';
import Editor from '@monaco-editor/react';
import { Play, RotateCcw, AlertOctagon, CheckCircle2, Loader2, Code2 } from 'lucide-react';

const RISKY_EXAMPLE = `ALTER TABLE users
ADD COLUMN phone VARCHAR(20) NOT NULL;

ALTER TABLE users
DROP COLUMN legacy_email;`;

const SAFE_EXAMPLE = `ALTER TABLE users
ADD COLUMN last_login TIMESTAMP;`;

export default function MigrationEditor({ sql, setSql, onAnalyze, isLoading }) {
  return (
    <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', height: '100%', minHeight: '520px' }}>
      
      {/* Panel Header */}
      <div style={{
        padding: '0.85rem 1.25rem',
        borderBottom: '1px solid var(--border-color)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: 'rgba(15, 23, 42, 0.4)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Code2 size={18} color="#38bdf8" />
          <h2 style={{ fontSize: '0.95rem', fontWeight: '700', color: 'var(--text-primary)' }}>
            PostgreSQL Migration SQL
          </h2>
        </div>

        <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
          <button
            type="button"
            className="btn btn-secondary"
            style={{ fontSize: '0.75rem', padding: '0.35rem 0.65rem' }}
            onClick={() => setSql(RISKY_EXAMPLE)}
            disabled={isLoading}
          >
            <AlertOctagon size={13} color="#f87171" />
            Risky Example
          </button>

          <button
            type="button"
            className="btn btn-secondary"
            style={{ fontSize: '0.75rem', padding: '0.35rem 0.65rem' }}
            onClick={() => setSql(SAFE_EXAMPLE)}
            disabled={isLoading}
          >
            <CheckCircle2 size={13} color="#4ade80" />
            Safe Example
          </button>

          <button
            type="button"
            className="btn btn-secondary"
            style={{ fontSize: '0.75rem', padding: '0.35rem 0.65rem' }}
            onClick={() => setSql('')}
            disabled={isLoading || !sql}
          >
            <RotateCcw size={13} color="#94a3b8" />
            Clear
          </button>
        </div>
      </div>

      {/* Editor Body */}
      <div style={{ flex: 1, minHeight: '340px', padding: '0.5rem 0', background: '#1e1e1e' }}>
        <Editor
          height="100%"
          defaultLanguage="sql"
          language="sql"
          theme="vs-dark"
          value={sql}
          onChange={(value) => setSql(value || '')}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 2,
            wordWrap: 'on',
            padding: { top: 12, bottom: 12 }
          }}
        />
      </div>

      {/* Action Footer */}
      <div style={{
        padding: '0.85rem 1.25rem',
        borderTop: '1px solid var(--border-color)',
        background: 'rgba(15, 23, 42, 0.6)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          Dialect: PostgreSQL • AST Tokenized
        </span>

        <button
          type="button"
          className="btn btn-primary"
          onClick={onAnalyze}
          disabled={isLoading || !sql.strip ? !sql.trim() : false}
          style={{ width: '180px' }}
        >
          {isLoading ? (
            <>
              <Loader2 size={16} className="spinner" />
              Analyzing...
            </>
          ) : (
            <>
              <Play size={16} fill="currentColor" />
              Analyze Migration
            </>
          )}
        </button>
      </div>

    </div>
  );
}
