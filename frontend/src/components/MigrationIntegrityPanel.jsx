import React, { useState } from 'react';
import { Fingerprint, Copy, Check, CheckCircle2, AlertOctagon, RefreshCw, Search } from 'lucide-react';

export default function MigrationIntegrityPanel({ migrationIntegrity, currentSql, analyzedSql }) {
  const [copied, setCopied] = useState(false);
  const [inputFingerprint, setInputFingerprint] = useState('');
  const [verifyResult, setVerifyResult] = useState(null);
  const [isVerifying, setIsVerifying] = useState(false);

  if (!migrationIntegrity) return null;

  const { algorithm, fingerprint } = migrationIntegrity;
  const isModified = currentSql && analyzedSql && currentSql.trim() !== analyzedSql.trim();

  const handleCopy = () => {
    if (!fingerprint) return;
    navigator.clipboard.writeText(fingerprint);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleVerify = async () => {
    if (!inputFingerprint || !inputFingerprint.trim()) return;
    setIsVerifying(true);
    setVerifyResult(null);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/verify-fingerprint', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sql: currentSql,
          expected_fingerprint: inputFingerprint.trim()
        })
      });

      if (!response.ok) {
        throw new Error(`Verification failed: ${response.status}`);
      }

      const data = await response.json();
      setVerifyResult(data);
    } catch (err) {
      console.error("Fingerprint verification error:", err);
      setVerifyResult({ status: "ERROR", message: err.message });
    } finally {
      setIsVerifying(false);
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      
      {/* Fingerprint Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Fingerprint size={20} color="#38bdf8" />
          <h3 style={{ fontSize: '1rem', fontWeight: '700', color: 'var(--text-primary)' }}>
            Migration Content Integrity
          </h3>
        </div>
        <span style={{ background: 'rgba(56, 189, 248, 0.15)', border: '1px solid rgba(56, 189, 248, 0.3)', color: '#38bdf8', fontSize: '0.7rem', fontWeight: '700', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
          {algorithm} FINGERPRINT
        </span>
      </div>

      {/* Generated Fingerprint Section */}
      <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1rem' }}>
        
        {/* Status Badge */}
        <div style={{ marginBottom: '0.65rem' }}>
          {isModified ? (
            <span style={{ background: 'var(--medium-bg)', border: '1px solid var(--medium-border)', color: 'var(--medium-text)', fontSize: '0.75rem', fontWeight: '700', padding: '0.25rem 0.6rem', borderRadius: '6px', display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}>
              <RefreshCw size={13} className="spinner" />
              Migration modified — re-analyze to refresh fingerprint
            </span>
          ) : (
            <span style={{ background: 'var(--low-bg)', border: '1px solid var(--low-border)', color: 'var(--low-text)', fontSize: '0.75rem', fontWeight: '700', padding: '0.25rem 0.6rem', borderRadius: '6px', display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}>
              <CheckCircle2 size={13} />
              CONTENT INTEGRITY GENERATED
            </span>
          )}
        </div>

        {/* Monospace Fingerprint & Copy Button */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: '#090d16', padding: '0.6rem 0.85rem', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
          <code className="font-mono" style={{ fontSize: '0.78rem', color: '#e2e8f0', flex: 1, wordBreak: 'break-all' }}>
            {fingerprint}
          </code>
          <button
            type="button"
            className="btn btn-secondary"
            style={{ fontSize: '0.72rem', padding: '0.3rem 0.6rem', flexShrink: 0 }}
            onClick={handleCopy}
          >
            {copied ? <Check size={13} color="#4ade80" /> : <Copy size={13} color="#94a3b8" />}
            <span>{copied ? 'Copied!' : 'Copy'}</span>
          </button>
        </div>
      </div>

      {/* Verify Integrity Section */}
      <div style={{ background: 'rgba(15, 23, 42, 0.4)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        <h4 style={{ fontSize: '0.85rem', fontWeight: '700', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <Search size={14} color="#8b5cf6" />
          Verify Migration Integrity
        </h4>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <input
            type="text"
            className="font-mono"
            placeholder="Paste expected SHA-256 fingerprint to verify..."
            value={inputFingerprint}
            onChange={(e) => setInputFingerprint(e.target.value)}
            style={{
              flex: 1,
              background: '#090d16',
              border: '1px solid var(--border-color)',
              borderRadius: '6px',
              padding: '0.5rem 0.75rem',
              color: '#ffffff',
              fontSize: '0.78rem'
            }}
          />
          <button
            type="button"
            className="btn btn-secondary"
            onClick={handleVerify}
            disabled={isVerifying || !inputFingerprint.trim()}
            style={{ fontSize: '0.78rem', padding: '0.5rem 0.85rem' }}
          >
            {isVerifying ? 'Verifying...' : 'Verify Integrity'}
          </button>
        </div>

        {/* Verification Result Callouts */}
        {verifyResult && (
          <div style={{ marginTop: '0.3rem' }}>
            {verifyResult.status === 'MATCH' && (
              <div style={{ background: 'var(--low-bg)', border: '1px solid var(--low-border)', color: 'var(--low-text)', padding: '0.65rem 0.85rem', borderRadius: '6px', fontSize: '0.82rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <CheckCircle2 size={16} />
                <div>
                  <strong style={{ display: 'block', fontWeight: '700' }}>INTEGRITY VERIFIED</strong>
                  Migration content matches the expected fingerprint.
                </div>
              </div>
            )}

            {verifyResult.status === 'DRIFT_DETECTED' && (
              <div style={{ background: 'var(--critical-bg)', border: '1px solid var(--critical-border)', color: 'var(--critical-text)', padding: '0.65rem 0.85rem', borderRadius: '6px', fontSize: '0.82rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <AlertOctagon size={16} />
                <div>
                  <strong style={{ display: 'block', fontWeight: '700' }}>DRIFT DETECTED</strong>
                  Migration content has changed since the expected fingerprint was generated.
                </div>
              </div>
            )}
          </div>
        )}

      </div>

    </div>
  );
}
