import React, { useState, useEffect } from 'react';
import type { GitStatus } from '../types';
import * as api from '../api/client';
import {
  GitBranch,
  FileDiff,
  Check,
  Radio,
  X,
  UploadCloud,
  Link,
  CheckCircle2,
  AlertCircle,
  Loader2,
  FolderGit2
} from 'lucide-react';

const GithubIcon = ({ size = 13, color = 'currentColor' }: { size?: number; color?: string }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4" />
    <path d="M9 18c-4.51 2-5-2-7-2" />
  </svg>
);

interface GitPanelProps {
  projectId: string;
  status: GitStatus | null;
  onFetchDiff: () => void;
  diffContent: string | null;
  onRefreshStatus?: () => void;
}

export const GitPanel: React.FC<GitPanelProps> = ({
  projectId,
  status,
  onFetchDiff,
  diffContent,
  onRefreshStatus
}) => {
  const [showDiff, setShowDiff] = useState(false);
  const [showCommitModal, setShowCommitModal] = useState(false);
  const [showGithubModal, setShowGithubModal] = useState(false);

  // Commit & Push state
  const [commitMsg, setCommitMsg] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error' | 'info'; message: string } | null>(null);

  // GitHub Remote state
  const [remoteUrl, setRemoteUrl] = useState('');
  const [currentRemote, setCurrentRemote] = useState<string | null>(null);
  const [hasRemote, setHasRemote] = useState(false);
  const [branch, setBranch] = useState('main');
  const [isSavingRemote, setIsSavingRemote] = useState(false);

  // Fetch current remote on project change
  useEffect(() => {
    if (projectId) {
      api.fetchGitRemote(projectId)
        .then((res) => {
          setCurrentRemote(res.remote_url);
          setHasRemote(res.has_remote);
          setRemoteUrl(res.remote_url || '');
          if (res.branch) setBranch(res.branch);
        })
        .catch(() => {
          setHasRemote(false);
          setCurrentRemote(null);
        });
    }
  }, [projectId]);

  const handleCommitAndPush = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!commitMsg.trim()) return;

    setIsSubmitting(true);
    setFeedback(null);

    try {
      const res = await api.commitAndPush(projectId, commitMsg.trim(), true);
      if (res.pushed) {
        setFeedback({
          type: 'success',
          message: `Committed (${res.commit_hash}) & pushed to GitHub: ${res.push_output || 'Success'}`
        });
      } else {
        setFeedback({
          type: 'info',
          message: `Committed (${res.commit_hash}). ${res.push_output || 'Connect a GitHub remote repository to auto-push.'}`
        });
      }
      setCommitMsg('');
      if (onRefreshStatus) onRefreshStatus();
    } catch (err: any) {
      setFeedback({
        type: 'error',
        message: err.message || 'Failed to commit and push'
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSaveRemote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!remoteUrl.trim()) return;

    setIsSavingRemote(true);
    try {
      const res = await api.setGitRemote(projectId, remoteUrl.trim(), branch);
      setCurrentRemote(res.remote_url);
      setHasRemote(true);
      setShowGithubModal(false);
      setFeedback({
        type: 'success',
        message: `Connected to GitHub: ${res.remote_url}`
      });
    } catch (err: any) {
      alert(err.message || 'Failed to set GitHub remote');
    } finally {
      setIsSavingRemote(false);
    }
  };

  return (
    <div style={{
      height: '24px',
      backgroundColor: 'var(--vscode-bg-statusbar)',
      color: '#ffffff',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 0.6rem',
      fontSize: '11px',
      userSelect: 'none',
      zIndex: 5
    }}>
      {/* Left Items: Source Control, Errors, Warnings, GitHub Remote Status */}
      <div style={{ display: 'flex', alignItems: 'center', height: '100%' }}>
        {/* Branch Badge */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.3rem',
            padding: '0 0.5rem',
            height: '100%',
            cursor: 'pointer',
            backgroundColor: 'rgba(255,255,255,0.06)'
          }}
          title="Git Branch"
        >
          <GitBranch size={12} color="#fb923c" />
          <span style={{ fontWeight: 600 }}>{status?.branch || branch || 'main'}</span>
        </div>

        {/* Sync / Diff Status */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.3rem',
            padding: '0 0.5rem',
            height: '100%',
            cursor: 'pointer'
          }}
          onClick={() => {
            onFetchDiff();
            setShowDiff(!showDiff);
          }}
          title="View Git Working Directory Diff"
        >
          {status?.is_clean ? (
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.2rem', color: '#4ade80' }}>
              <Check size={11} color="#4ade80" /> Clean
            </span>
          ) : (
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.2rem', color: '#fbbf24' }}>
              <FileDiff size={11} color="#fbbf24" /> {status?.modified.length || 0} modified
            </span>
          )}
        </div>

        {/* Connect GitHub Status & Button */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.35rem',
            padding: '0 0.5rem',
            height: '100%',
            cursor: 'pointer',
            borderLeft: '1px solid rgba(255,255,255,0.1)'
          }}
          onClick={() => setShowGithubModal(true)}
          title={hasRemote ? `Connected to GitHub: ${currentRemote}` : 'Click to connect a GitHub repository'}
        >
          <GithubIcon size={12} color="#ffffff" />
          <span>{hasRemote ? 'GitHub Connected' : 'Connect GitHub'}</span>
        </div>
      </div>

      {/* Right Items: Quick Commit & Push Button, Editor info */}
      <div style={{ display: 'flex', alignItems: 'center', height: '100%' }}>
        {/* Commit & Push Button */}
        <button
          onClick={() => setShowCommitModal(true)}
          style={{
            background: 'none',
            border: 'none',
            color: '#ffffff',
            display: 'flex',
            alignItems: 'center',
            gap: '0.3rem',
            padding: '0 0.5rem',
            height: '100%',
            cursor: 'pointer',
            fontSize: '11px',
            backgroundColor: 'rgba(255,255,255,0.06)'
          }}
          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.15)'}
          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.06)'}
          title="Commit changes and push automatically to GitHub"
        >
          <UploadCloud size={12} color="#38bdf8" />
          <span style={{ fontWeight: 600 }}>Commit & Push</span>
        </button>

        <div style={{ padding: '0 0.5rem', borderLeft: '1px solid rgba(255,255,255,0.15)' }}>
          Spaces: 4
        </div>
        <div style={{ padding: '0 0.5rem' }}>
          UTF-8
        </div>
        <div style={{ padding: '0 0.5rem', display: 'flex', alignItems: 'center', gap: '0.3rem', color: '#4ade80' }}>
          <Radio size={10} color="#4ade80" />
          <span>Live Sync</span>
        </div>
      </div>

      {/* 1. Commit & Push Modal */}
      {showCommitModal && (
        <div className="modal-overlay" onClick={() => setShowCommitModal(false)}>
          <div className="modal-box" style={{ maxWidth: '540px' }} onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.8rem' }}>
              <h3 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--vscode-text-white)', display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
                <UploadCloud size={16} color="var(--vscode-accent)" />
                <span>Commit & Auto-Push to GitHub</span>
              </h3>
              <button className="btn-icon" onClick={() => setShowCommitModal(false)}>
                <X size={14} />
              </button>
            </div>

            <p style={{ fontSize: '12px', color: 'var(--vscode-text-secondary)', marginBottom: '0.8rem', lineHeight: '1.4' }}>
              Stage all modified files, create a commit, and automatically push to your remote GitHub repository.
            </p>

            {hasRemote ? (
              <div style={{
                padding: '0.4rem 0.6rem',
                backgroundColor: 'rgba(255, 255, 255, 0.06)',
                border: '1px solid rgba(255, 255, 255, 0.12)',
                borderRadius: '4px',
                fontSize: '11px',
                color: 'var(--vscode-text-primary)',
                marginBottom: '0.8rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem'
              }}>
                <GithubIcon size={13} />
                <span>Target: <b>{currentRemote}</b> (branch: {branch})</span>
              </div>
            ) : (
              <div style={{
                padding: '0.45rem 0.6rem',
                backgroundColor: 'rgba(255, 255, 255, 0.04)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '4px',
                fontSize: '11px',
                color: 'var(--vscode-text-secondary)',
                marginBottom: '0.8rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}>
                <span>No GitHub repository connected. Commits will be saved locally.</span>
                <button
                  type="button"
                  className="btn btn-secondary"
                  style={{ fontSize: '10px', padding: '0.2rem 0.4rem' }}
                  onClick={() => {
                    setShowCommitModal(false);
                    setShowGithubModal(true);
                  }}
                >
                  Connect GitHub
                </button>
              </div>
            )}

            <form onSubmit={handleCommitAndPush}>
              <div style={{ marginBottom: '0.8rem' }}>
                <label style={{ display: 'block', fontSize: '11px', color: 'var(--vscode-text-secondary)', marginBottom: '0.3rem', fontWeight: 500 }}>
                  Commit Message / Description
                </label>
                <textarea
                  className="input"
                  style={{ width: '100%', height: '65px', resize: 'none', padding: '0.4rem' }}
                  placeholder="e.g. Implement user authentication, updated styles, and unit tests"
                  value={commitMsg}
                  onChange={(e) => setCommitMsg(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                      e.preventDefault();
                      handleCommitAndPush();
                    }
                  }}
                  autoFocus
                />
              </div>

              {feedback && (
                <div style={{
                  padding: '0.5rem',
                  borderRadius: '3px',
                  fontSize: '11px',
                  marginBottom: '0.8rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  backgroundColor: feedback.type === 'success' ? 'rgba(78, 201, 176, 0.15)' : feedback.type === 'error' ? 'rgba(241, 76, 76, 0.15)' : 'rgba(0, 122, 204, 0.15)',
                  color: feedback.type === 'success' ? 'var(--vscode-accent-cyan)' : feedback.type === 'error' ? 'var(--vscode-accent-red)' : 'var(--vscode-accent-blue)',
                  border: '1px solid currentColor'
                }}>
                  {feedback.type === 'success' ? <CheckCircle2 size={13} /> : <AlertCircle size={13} />}
                  <span>{feedback.message}</span>
                </div>
              )}

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.4rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowCommitModal(false)}>
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={!commitMsg.trim() || isSubmitting}
                  style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}
                >
                  {isSubmitting ? <Loader2 size={12} className="animate-spin" /> : <UploadCloud size={12} />}
                  <span>{isSubmitting ? 'Pushing...' : 'Commit & Push'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 2. Connect GitHub Remote Modal */}
      {showGithubModal && (
        <div className="modal-overlay" onClick={() => setShowGithubModal(false)}>
          <div className="modal-box" style={{ maxWidth: '520px' }} onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.8rem' }}>
              <h3 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--vscode-text-white)', display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
                <GithubIcon size={16} />
                <span>Connect GitHub Repository</span>
              </h3>
              <button className="btn-icon" onClick={() => setShowGithubModal(false)}>
                <X size={14} />
              </button>
            </div>

            <p style={{ fontSize: '12px', color: 'var(--vscode-text-secondary)', marginBottom: '0.8rem', lineHeight: '1.4' }}>
              Connect your project workspace to an existing GitHub repository to enable automatic commits and pushing.
            </p>

            <form onSubmit={handleSaveRemote}>
              <div style={{ marginBottom: '0.8rem' }}>
                <label style={{ display: 'block', fontSize: '11px', color: 'var(--vscode-text-secondary)', marginBottom: '0.3rem', fontWeight: 500 }}>
                  GitHub Repository URL (HTTPS or SSH)
                </label>
                <input
                  type="text"
                  className="input"
                  style={{ width: '100%' }}
                  placeholder="https://github.com/username/my-project.git"
                  value={remoteUrl}
                  onChange={(e) => setRemoteUrl(e.target.value)}
                  autoFocus
                />
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '11px', color: 'var(--vscode-text-secondary)', marginBottom: '0.3rem', fontWeight: 500 }}>
                  Default Branch
                </label>
                <input
                  type="text"
                  className="input"
                  style={{ width: '100%' }}
                  placeholder="main"
                  value={branch}
                  onChange={(e) => setBranch(e.target.value)}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.4rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowGithubModal(false)}>
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={!remoteUrl.trim() || isSavingRemote}
                >
                  <Link size={12} />
                  <span>{isSavingRemote ? 'Connecting...' : 'Save & Connect'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 3. Git Diff Modal */}
      {showDiff && (
        <div className="modal-overlay" onClick={() => setShowDiff(false)}>
          <div className="modal-box" style={{ maxWidth: '800px' }} onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.6rem' }}>
              <h3 style={{ fontSize: '12px', fontWeight: 600, color: 'var(--vscode-text-white)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <FileDiff size={14} color="var(--vscode-accent)" />
                <span>Working Directory Git Diff</span>
              </h3>
              <button className="btn-icon" onClick={() => setShowDiff(false)}>
                <X size={14} />
              </button>
            </div>

            <pre style={{
              backgroundColor: '#121212',
              padding: '0.75rem',
              borderRadius: '3px',
              fontFamily: 'var(--font-mono)',
              fontSize: '11px',
              maxHeight: '400px',
              overflowY: 'auto',
              color: 'var(--vscode-text-primary)',
              whiteSpace: 'pre-wrap',
              border: '1px solid var(--vscode-border)'
            }}>
              {diffContent || 'Working tree is clean.'}
            </pre>
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '0.6rem' }}>
              <button className="btn btn-secondary" onClick={() => setShowDiff(false)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
