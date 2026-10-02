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
  Layers
} from 'lucide-react';

interface LoginPageProps {
  projects: Project[];
  onLogin: (user: { userId: string; displayName: string; role: string }, selectedProjectId?: string) => void;
  onCreateProject: (name: string, template?: string) => Promise<Project | void>;
}

const PRESET_ACCOUNTS = [
  {
    id: 'user_a',
    name: 'Alice Chen',
    role: 'Lead Fullstack Engineer',
    badge: 'Dev A',
    color: '#007acc'
  },
  {
    id: 'user_b',
    name: 'Bob Miller',
    role: 'Backend Architect',
    badge: 'Dev B',
    color: '#4ec9b0'
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
              backgroundColor: 'rgba(0, 122, 204, 0.15)',
              border: '1px solid rgba(0, 122, 204, 0.3)',
              marginBottom: '0.75rem'
            }}>
              <Code2 size={24} color="#007acc" />
            </div>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--vscode-text-white)', marginBottom: '0.3rem' }}>
              Developer Sign In
            </h1>
            <p style={{ fontSize: '12px', color: 'var(--vscode-text-secondary)', lineHeight: '1.4' }}>
              Collaborative coding environment with real-time AI agents and persistent memory.
            </p>
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
