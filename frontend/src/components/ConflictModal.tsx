import React from 'react';
import type { FileConflictData } from '../types';
import { ShieldAlert, RefreshCw, AlertTriangle, X } from 'lucide-react';

interface ConflictModalProps {
  conflict: FileConflictData | null;
  onAcceptServer: (path: string, serverContent: string, serverVersion: number) => void;
  onForceSave: (path: string) => void;
  onDismiss: () => void;
}

export const ConflictModal: React.FC<ConflictModalProps> = ({
  conflict,
  onAcceptServer,
  onForceSave,
  onDismiss
}) => {
  if (!conflict) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-box" style={{ maxWidth: '620px', border: '1px solid var(--vscode-accent-red)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.6rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--vscode-accent-red)' }}>
            <ShieldAlert size={18} />
            <h3 style={{ fontSize: '13px', fontWeight: 600 }}>Concurrent Edit Conflict Detected</h3>
          </div>
          <button className="btn-icon" onClick={onDismiss}>
            <X size={14} />
          </button>
        </div>

        <p style={{ fontSize: '12px', color: 'var(--vscode-text-secondary)', marginBottom: '0.6rem', lineHeight: '1.4' }}>
          File <b>{conflict.path}</b> was modified by another collaborator or AI agent on the server while you were editing.
          <br />
          Server version is <b>v{conflict.server_version}</b>, but your local buffer was based on <b>v{conflict.expected_version}</b>.
        </p>

        <div style={{ marginBottom: '0.8rem' }}>
          <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--vscode-accent-yellow)', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <AlertTriangle size={12} />
            <span>Server Content (v{conflict.server_version}):</span>
          </div>
          <pre style={{
            backgroundColor: '#121212',
            padding: '0.5rem',
            borderRadius: '3px',
            fontSize: '11px',
            fontFamily: 'var(--font-mono)',
            maxHeight: '160px',
            overflowY: 'auto',
            border: '1px solid var(--vscode-border)',
            color: 'var(--vscode-text-primary)'
          }}>
            {conflict.server_content}
          </pre>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.4rem' }}>
          <button className="btn btn-secondary" onClick={onDismiss}>
            Cancel
          </button>
          <button
            className="btn btn-secondary"
            style={{ color: 'var(--vscode-accent-blue)', borderColor: 'var(--vscode-accent-blue)' }}
            onClick={() => onAcceptServer(conflict.path, conflict.server_content, conflict.server_version)}
          >
            <RefreshCw size={12} />
            <span>Reload Server Version (v{conflict.server_version})</span>
          </button>
          <button
            className="btn btn-danger"
            onClick={() => onForceSave(conflict.path)}
          >
            Force Overwrite
          </button>
        </div>
      </div>
    </div>
  );
};
