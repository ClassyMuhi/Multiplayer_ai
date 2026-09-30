import React from 'react';
import type { FileConflictData } from '../types';
import { ShieldAlert, RefreshCw, AlertTriangle } from 'lucide-react';


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
      <div className="modal-box" style={{ maxWidth: '650px', border: '1px solid var(--accent-red)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-red)', marginBottom: '0.8rem' }}>
          <ShieldAlert size={22} />
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Concurrent Edit Conflict Detected</h3>
        </div>

        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.8rem', lineHeight: '1.4' }}>
          File <b>{conflict.path}</b> was modified by another collaborator or Summit AI on the server while you were editing!
          <br />
          Server version is <b>v{conflict.server_version}</b>, but your editor was based on <b>v{conflict.expected_version}</b>.
        </p>

        <div style={{ marginBottom: '1rem' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--accent-amber)', marginBottom: '0.3rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <AlertTriangle size={12} /> Server Content (v{conflict.server_version}):
          </div>
          <pre style={{
            backgroundColor: '#000',
            padding: '0.6rem',
            borderRadius: '6px',
            fontSize: '0.75rem',
            fontFamily: 'var(--font-mono)',
            maxHeight: '180px',
            overflowY: 'auto',
            border: '1px solid var(--border-color)',
            color: 'var(--text-main)'
          }}>
            {conflict.server_content}
          </pre>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
          <button className="btn btn-secondary" onClick={onDismiss}>
            Cancel
          </button>
          <button
            className="btn btn-secondary"
            style={{ color: 'var(--accent-blue)', borderColor: 'var(--accent-blue)' }}
            onClick={() => onAcceptServer(conflict.path, conflict.server_content, conflict.server_version)}
          >
            <RefreshCw size={13} /> Reload Server Version (v{conflict.server_version})
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
