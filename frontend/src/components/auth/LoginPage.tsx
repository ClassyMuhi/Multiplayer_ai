import React, { useState } from 'react';
import type { Project } from '../../types';
import {
  Code2,
  User,
  Shield,
  FolderGit2,
  Plus,
  ArrowRight,
  Terminal,
  Check,
  Cpu,
  Layers,
  AlertCircle,
  Loader2
} from 'lucide-react';
import { signInWithGoogle } from '../../services/firebase';

interface LoginPageProps {
  projects: Project[];
  onLogin: (user: { userId: string; displayName: string; role: string; email?: string | null; photoURL?: string | null }, selectedProjectId?: string) => void;
  onCreateProject: (name: string, template?: string) => Promise<Project | void>;
}

const PRESET_ACCOUNTS = [
  {
    id: 'user_a',
    name: 'Alice Chen',
    role: 'Lead Fullstack Engineer',
    badge: 'Dev A',
    color: '#d4d4d8'
  },
  {
    id: 'user_b',
    name: 'Bob Miller',
    role: 'Backend Architect',
    badge: 'Dev B',
    color: '#a1a1aa'
  }
];

export const LoginPage: React.FC<LoginPageProps> = ({
  projects,
  onLogin,
  onCreateProject
}) => {
  const [activeTab, setActiveTab] = useState<'preset' | 'custom'>('preset');
  const [selectedPreset, setSelectedPreset] = useState<string>('user_a');
  
  // Custom user fields
  const [customName, setCustomName] = useState('');
  const [customUserId, setCustomUserId] = useState('');
  const [customRole, setCustomRole] = useState('Fullstack Engineer');
  
  // Workspace selection
  const [selectedProjectId, setSelectedProjectId] = useState<string>(projects[0]?.id || '');
  const [isCreatingProject, setIsCreatingProject] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');
  const [newProjectTemplate, setNewProjectTemplate] = useState('blank');
  const [rememberMe, setRememberMe] = useState(true);

  // Firebase Google Auth state
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);

  const handleGoogleSignIn = async () => {
    setAuthError(null);
    setIsGoogleLoading(true);
    try {
      const googleUser = await signInWithGoogle();
      const userObj = {
        userId: googleUser.uid,
        displayName: googleUser.displayName || googleUser.email?.split('@')[0] || 'Google Developer',
        role: 'Fullstack Engineer',
        email: googleUser.email,
        photoURL: googleUser.photoURL
      };

      if (rememberMe) {
        localStorage.setItem('summit_auth_session', JSON.stringify({ ...userObj, selectedProjectId }));
      } else {
        localStorage.removeItem('summit_auth_session');
      }

      onLogin(userObj, selectedProjectId);
    } catch (err: any) {
      console.error('Firebase Google Sign-In error:', err);
      setAuthError(err.message || 'Authentication failed. Please try again.');
    } finally {
      setIsGoogleLoading(false);
    }
  };

  const handleCreateNewProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProjectName.trim()) return;
    const created = await onCreateProject(newProjectName.trim(), newProjectTemplate);
    if (created && created.id) {
      setSelectedProjectId(created.id);
    }
    setIsCreatingProject(false);
    setNewProjectName('');
  };

  const handleLaunch = (e: React.FormEvent) => {
    e.preventDefault();
    
    let userObj = {
      userId: 'user_a',
      displayName: 'Alice (Dev A)',
      role: 'Lead Fullstack Engineer'
    };

    if (activeTab === 'preset') {
      const preset = PRESET_ACCOUNTS.find((p) => p.id === selectedPreset) || PRESET_ACCOUNTS[0];
      userObj = {
        userId: preset.id,
        displayName: `${preset.name} (${preset.badge})`,
        role: preset.role
      };
    } else {
      const name = customName.trim() || 'Developer';
      const uid = customUserId.trim() || `user_${Date.now().toString().slice(-4)}`;
      userObj = {
        userId: uid,
        displayName: name,
        role: customRole
      };
    }

    if (rememberMe) {
      localStorage.setItem('summit_auth_session', JSON.stringify({ ...userObj, selectedProjectId }));
    } else {
      localStorage.removeItem('summit_auth_session');
    }

    onLogin(userObj, selectedProjectId);
  };

  return (
    <div style={{
      height: '100vh',
      width: '100vw',
      backgroundColor: '#181818',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1.5rem',
      position: 'relative'
    }}>
      {/* Background Subtle Grid */}
      <div style={{
        position: 'absolute',
        inset: 0,
        backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(255,255,255,0.03) 1px, transparent 0)',
        backgroundSize: '24px 24px',
        pointerEvents: 'none'
      }} />

      {/* Main Authentication Window Card */}
      <div style={{
        width: '100%',
        maxWidth: '520px',
        backgroundColor: 'var(--vscode-bg-sidebar)',
        border: '1px solid var(--vscode-border-light)',
        borderRadius: '6px',
        boxShadow: '0 20px 60px rgba(0,0,0,0.7)',
        overflow: 'hidden',
        position: 'relative',
        zIndex: 1
      }}>
        {/* VSCodium Titlebar Header */}
        <div style={{
          height: '36px',
          backgroundColor: '#1f1f1f',
          borderBottom: '1px solid var(--vscode-border)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 1rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{ display: 'flex', gap: '6px' }}>
              <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#f14c4c' }} />
              <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#cca700' }} />
              <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#6a9955' }} />
            </div>
            <span style={{ fontSize: '12px', color: 'var(--vscode-text-muted)', marginLeft: '0.4rem', fontWeight: 500 }}>
              Summit Studio — VSCodium Edition
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--vscode-text-muted)', fontSize: '11px' }}>
            <Terminal size={12} />
            <span>v0.1.0</span>
          </div>
        </div>

        {/* Card Body */}
        <div style={{ padding: '1.75rem' }}>
          {/* Header Branding */}
          <div style={{ marginBottom: '1.5rem', textAlign: 'center' }}>
            <div style={{
              display: 'inline-flex',
              padding: '0.6rem',
              borderRadius: '8px',
              backgroundColor: 'rgba(255, 255, 255, 0.08)',
              border: '1px solid rgba(255, 255, 255, 0.15)',
              marginBottom: '0.75rem'
            }}>
              <Code2 size={24} color="#f4f4f5" />
            </div>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--vscode-text-white)', marginBottom: '0.3rem' }}>
              Developer Sign In
            </h1>
            <p style={{ fontSize: '12px', color: 'var(--vscode-text-secondary)', lineHeight: '1.4' }}>
              Collaborative coding environment with real-time AI agents and persistent memory.
            </p>
          </div>

          {/* Auth Error Banner */}
          {authError && (
            <div style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: '0.6rem',
              padding: '0.65rem 0.8rem',
              backgroundColor: 'rgba(241, 76, 76, 0.12)',
              border: '1px solid rgba(241, 76, 76, 0.35)',
              borderRadius: '4px',
              color: '#f14c4c',
              fontSize: '11px',
              lineHeight: '1.4',
              marginBottom: '1rem'
            }}>
              <AlertCircle size={15} style={{ flexShrink: 0, marginTop: '1px' }} />
              <div style={{ flex: 1 }}>{authError}</div>
            </div>
          )}

          {/* Primary: Real Google Sign-In Button */}
          <div style={{ marginBottom: '1.25rem' }}>
            <button
              type="button"
              onClick={handleGoogleSignIn}
              disabled={isGoogleLoading}
              style={{
                width: '100%',
                padding: '0.65rem 1rem',
                backgroundColor: '#ffffff',
                color: '#1f1f1f',
                border: '1px solid #d1d5db',
                borderRadius: '4px',
                fontSize: '13px',
                fontWeight: 600,
                cursor: isGoogleLoading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.65rem',
                transition: 'all 0.15s ease',
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.2)',
                opacity: isGoogleLoading ? 0.7 : 1
              }}
              onMouseEnter={(e) => {
                if (!isGoogleLoading) e.currentTarget.style.backgroundColor = '#f3f4f6';
              }}
              onMouseLeave={(e) => {
                if (!isGoogleLoading) e.currentTarget.style.backgroundColor = '#ffffff';
              }}
            >
              {isGoogleLoading ? (
                <>
                  <Loader2 size={16} className="animate-spin" style={{ animation: 'spin 1s linear infinite' }} />
                  <span>Connecting with Google...</span>
                </>
              ) : (
                <>
                  {/* Google SVG Multi-Color Logo */}
                  <svg width="16" height="16" viewBox="0 0 24 24">
                    <path
                      fill="#4285F4"
                      d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.17z"
                    />
                    <path
                      fill="#34A853"
                      d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.36 24 12 24z"
                    />
                    <path
                      fill="#FBBC05"
                      d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.98 0 12s.45 3.82 1.25 5.42l4.03-3.15z"
                    />
                    <path
                      fill="#EA4335"
                      d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.36 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"
                    />
                  </svg>
                  <span>Continue with Google</span>
                </>
              )}
            </button>
          </div>

          {/* Divider */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.6rem',
            marginBottom: '1.25rem'
          }}>
            <div style={{ flex: 1, height: '1px', backgroundColor: 'var(--vscode-border)' }} />
            <span style={{ fontSize: '10px', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--vscode-text-muted)', fontWeight: 600 }}>
              Or use workspace profile
            </span>
            <div style={{ flex: 1, height: '1px', backgroundColor: 'var(--vscode-border)' }} />
          </div>

          {/* Account Mode Tabs */}
          <div style={{
            display: 'flex',
            backgroundColor: '#1e1e1e',
            border: '1px solid var(--vscode-border)',
            borderRadius: '4px',
            padding: '2px',
            marginBottom: '1.25rem'
          }}>
            <button
              type="button"
              onClick={() => setActiveTab('preset')}
              style={{
                flex: 1,
                padding: '0.4rem 0.6rem',
                fontSize: '12px',
                fontWeight: 500,
                border: 'none',
                borderRadius: '3px',
                backgroundColor: activeTab === 'preset' ? 'var(--vscode-bg-card-hover)' : 'transparent',
                color: activeTab === 'preset' ? 'var(--vscode-text-white)' : 'var(--vscode-text-muted)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.4rem',
                transition: 'all 0.15s ease'
              }}
            >
              <User size={13} />
              <span>Multiplayer Profiles</span>
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('custom')}
              style={{
                flex: 1,
                padding: '0.4rem 0.6rem',
                fontSize: '12px',
                fontWeight: 500,
                border: 'none',
                borderRadius: '3px',
                backgroundColor: activeTab === 'custom' ? 'var(--vscode-bg-card-hover)' : 'transparent',
                color: activeTab === 'custom' ? 'var(--vscode-text-white)' : 'var(--vscode-text-muted)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.4rem',
                transition: 'all 0.15s ease'
              }}
            >
              <Shield size={13} />
              <span>Custom Account</span>
            </button>
          </div>

          <form onSubmit={handleLaunch}>
            {/* Tab 1: Preset Profiles */}
            {activeTab === 'preset' ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', marginBottom: '1.25rem' }}>
                {PRESET_ACCOUNTS.map((account) => {
                  const isSelected = selectedPreset === account.id;
                  return (
                    <div
                      key={account.id}
                      onClick={() => setSelectedPreset(account.id)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: '0.75rem 0.9rem',
                        borderRadius: '4px',
                        backgroundColor: isSelected ? 'rgba(0, 122, 204, 0.15)' : 'var(--vscode-bg-editor)',
                        border: isSelected ? '1px solid var(--vscode-accent)' : '1px solid var(--vscode-border)',
                        cursor: 'pointer',
                        transition: 'all 0.15s ease'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <div style={{
                          width: '32px',
                          height: '32px',
                          borderRadius: '4px',
                          backgroundColor: '#181818',
                          border: `1px solid ${account.color}`,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontWeight: 700,
                          fontSize: '11px',
                          color: account.color
                        }}>
                          {account.badge}
                        </div>
                        <div>
                          <div style={{ fontWeight: 600, fontSize: '13px', color: 'var(--vscode-text-white)' }}>
                            {account.name}
                          </div>
                          <div style={{ fontSize: '11px', color: 'var(--vscode-text-muted)' }}>
                            {account.role}
                          </div>
                        </div>
                      </div>

                      {isSelected && (
                        <div style={{
                          width: '20px',
                          height: '20px',
                          borderRadius: '50%',
                          backgroundColor: 'var(--vscode-accent)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}>
                          <Check size={12} color="#ffffff" />
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            ) : (
              /* Tab 2: Custom Account */
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem', marginBottom: '1.25rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '11px', color: 'var(--vscode-text-secondary)', marginBottom: '0.3rem', fontWeight: 500 }}>
                    Developer Name / Handle
                  </label>
                  <input
                    type="text"
                    className="input"
                    style={{ width: '100%' }}
                    placeholder="e.g., Jane Doe"
                    value={customName}
                    onChange={(e) => setCustomName(e.target.value)}
                  />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.6rem' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '11px', color: 'var(--vscode-text-secondary)', marginBottom: '0.3rem', fontWeight: 500 }}>
                      User ID
                    </label>
                    <input
                      type="text"
                      className="input"
                      style={{ width: '100%' }}
                      placeholder="e.g., dev_jane"
                      value={customUserId}
                      onChange={(e) => setCustomUserId(e.target.value)}
                    />
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '11px', color: 'var(--vscode-text-secondary)', marginBottom: '0.3rem', fontWeight: 500 }}>
                      Role
                    </label>
                    <select
                      className="input"
                      style={{ width: '100%' }}
                      value={customRole}
                      onChange={(e) => setCustomRole(e.target.value)}
                    >
                      <option value="Fullstack Engineer">Fullstack Engineer</option>
                      <option value="Backend Specialist">Backend Specialist</option>
                      <option value="Frontend Specialist">Frontend Specialist</option>
                      <option value="AI / ML Engineer">AI / ML Engineer</option>
                      <option value="System Architect">System Architect</option>
                      <option value="Guest Developer">Guest Developer</option>
                    </select>
                  </div>
                </div>
              </div>
            )}

            {/* Workspace / Project Selection */}
            <div style={{
              padding: '0.85rem',
              backgroundColor: 'var(--vscode-bg-editor)',
              border: '1px solid var(--vscode-border)',
              borderRadius: '4px',
              marginBottom: '1.25rem'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '11px', fontWeight: 600, color: 'var(--vscode-text-secondary)' }}>
                  <FolderGit2 size={13} color="var(--vscode-accent)" />
                  <span>Target Workspace</span>
                </div>

                <button
                  type="button"
                  onClick={() => setIsCreatingProject(!isCreatingProject)}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: 'var(--vscode-accent)',
                    fontSize: '11px',
                    fontWeight: 500,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.2rem'
                  }}
                >
                  <Plus size={11} /> {isCreatingProject ? 'Select Existing' : 'New Workspace'}
                </button>
              </div>

              {isCreatingProject ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                  <input
                    type="text"
                    className="input"
                    style={{ width: '100%' }}
                    placeholder="Workspace Name (e.g., My Web App)"
                    value={newProjectName}
                    onChange={(e) => setNewProjectName(e.target.value)}
                    autoFocus
                  />
                  <div style={{ display: 'flex', gap: '0.4rem' }}>
                    <select
                      className="input"
                      style={{ flex: 1 }}
                      value={newProjectTemplate}
                      onChange={(e) => setNewProjectTemplate(e.target.value)}
                    >
                      <option value="blank">Blank Workspace</option>
                      <option value="demo-calculator">Calculator Template</option>
                    </select>
                    <button
                      type="button"
                      className="btn btn-secondary"
                      style={{ fontSize: '11px', padding: '0.3rem 0.6rem' }}
                      onClick={handleCreateNewProject}
                    >
                      Create
                    </button>
                  </div>
                </div>
              ) : (
                <select
                  className="input"
                  style={{ width: '100%' }}
                  value={selectedProjectId}
                  onChange={(e) => setSelectedProjectId(e.target.value)}
                >
                  {projects.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name} ({p.id})
                    </option>
                  ))}
                </select>
              )}
            </div>

            {/* Remember Me & Action */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', fontSize: '11px', color: 'var(--vscode-text-secondary)', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  style={{ accentColor: 'var(--vscode-accent)', cursor: 'pointer' }}
                />
                <span>Remember session on this device</span>
              </label>
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              style={{
                width: '100%',
                padding: '0.65rem',
                fontSize: '13px',
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem'
              }}
            >
              <span>Launch VSCodium Workspace</span>
              <ArrowRight size={15} />
            </button>
          </form>
        </div>

        {/* Footer info bar */}
        <div style={{
          backgroundColor: '#1f1f1f',
          borderTop: '1px solid var(--vscode-border)',
          padding: '0.5rem 1rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '11px',
          color: 'var(--vscode-text-muted)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Cpu size={12} color="var(--vscode-accent-cyan)" />
            <span>Autonomous AI Engine Active</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Layers size={12} />
            <span>Multiplayer Protocol Ready</span>
          </div>
        </div>
      </div>
    </div>
  );
};
