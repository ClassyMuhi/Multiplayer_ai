import React, { useState } from 'react';
import type { GitStatus } from '../types';
import { GitBranch, GitCommit, FileDiff, CheckCircle } from 'lucide-react';


interface GitPanelProps {
  status: GitStatus | null;
  onFetchDiff: () => void;
  diffContent: string | null;
  onCreateCheckpoint: (message: string) => void;
}

export const GitPanel: React.FC<GitPanelProps> = ({
  status,
  onFetchDiff,
  diffContent,
  onCreateCheckpoint
}) => {
  const [showDiff, setShowDiff] = useState(false);
  const [chkMessage, setChkMessage] = useState('');
  const [showChkModal, setShowChkModal] = useState(false);

  const handleCheckpointSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (chkMessage.trim()) {
      onCreateCheckpoint(chkMessage.trim());
      setChkMessage('');
      setShowChkModal(false);
    }
  };

  return (
    <div style={{
      height: '34px',
      backgroundColor: 'var(--bg-panel)',
      borderTop: '1px solid var(--border-color)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 0.8rem',
      fontSize: '0.75rem'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', color: 'var(--accent-blue)' }}>
          <GitBranch size={13} />
          <span style={{ fontWeight: 600 }}>{status?.branch || 'main'}</span>
        </div>

        {status?.is_clean ? (
          <span style={{ color: 'var(--accent-green)', display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
            <CheckCircle size={11} /> Clean working tree
          </span>
        ) : (
          <span style={{ color: 'var(--accent-amber)' }}>
            ● {status?.modified.length || 0} modified, {status?.untracked.length || 0} untracked
          </span>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
        <button
          className="btn btn-secondary"
          style={{ padding: '0.15rem 0.4rem', fontSize: '0.725rem' }}
          onClick={() => {
            onFetchDiff();
            setShowDiff(!showDiff);
          }}
        >
          <FileDiff size={12} /> {showDiff ? 'Hide Diff' : 'View Diff'}
        </button>

        <button
          className="btn btn-secondary"
          style={{ padding: '0.15rem 0.4rem', fontSize: '0.725rem' }}
          onClick={() => setShowChkModal(true)}
        >
          <GitCommit size={12} /> Checkpoint
        </button>
      </div>

      {/* Diff Drawer Modal */}
      {showDiff && (
        <div className="modal-overlay" onClick={() => setShowDiff(false)}>
          <div className="modal-box" style={{ maxWidth: '800px' }} onClick={(e) => e.stopPropagation()}>
            <h3 style={{ marginBottom: '0.5rem', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <FileDiff size={16} color="var(--accent-blue)" /> Working Directory Git Diff
            </h3>
            <pre style={{
              backgroundColor: '#000',
              padding: '0.8rem',
              borderRadius: '6px',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.775rem',
              maxHeight: '400px',
              overflowY: 'auto',
              color: 'var(--text-main)',
              whiteSpace: 'pre-wrap'
            }}>
              {diffContent || 'No changes detected.'}
            </pre>
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '0.8rem' }}>
              <button className="btn btn-secondary" onClick={() => setShowDiff(false)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Checkpoint Commit Modal */}
      {showChkModal && (
        <div className="modal-overlay" onClick={() => setShowChkModal(false)}>
          <div className="modal-box" onClick={(e) => e.stopPropagation()}>
            <h3 style={{ marginBottom: '0.8rem', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <GitCommit size={16} color="var(--accent-green)" /> Create Git Checkpoint
            </h3>
            <form onSubmit={handleCheckpointSubmit}>
              <input
                type="text"
                className="input"
                style={{ width: '100%', marginBottom: '0.8rem' }}
                placeholder="e.g., Before authentication refactor"
                value={chkMessage}
                onChange={(e) => setChkMessage(e.target.value)}
                autoFocus
              />
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.4rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowChkModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Commit Checkpoint
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
