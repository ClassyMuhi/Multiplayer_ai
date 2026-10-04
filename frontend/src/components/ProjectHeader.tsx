import React, { useState, useEffect } from 'react';
import type { Project, UserPresence } from '../types';
import {
  Code2,
  Users,
  FolderGit2,
  Plus,
  PanelLeft,
  PanelRight,
  LogOut,
  ChevronDown,
  UserPlus,
  Mail,
  Copy,
  Check,
  Trash2,
  ShieldCheck
} from 'lucide-react';

interface InvitedTeammate {
  email: string;
  role: string;
  invitedAt: string;
}

interface ProjectHeaderProps {
  projects: Project[];
  currentProject: Project | null;
  onSelectProject: (id: string) => void;
  onCreateProject: (name: string, template?: string) => void;
  connectedUsers: UserPresence[];
  currentUser: { userId: string; displayName: string; role?: string; email?: string | null; photoURL?: string | null };
  onSwitchUser: (userId: string, displayName: string) => void;
  onSignOut?: () => void;
  showExplorer?: boolean;
  onToggleExplorer?: () => void;
  showAgentPanel?: boolean;
  onToggleAgentPanel?: () => void;
}

export const ProjectHeader: React.FC<ProjectHeaderProps> = ({
  projects,
  currentProject,
  onSelectProject,
  onCreateProject,
  connectedUsers,
  currentUser,
  onSignOut,
  showExplorer = true,
  onToggleExplorer,
  showAgentPanel = true,
  onToggleAgentPanel
}) => {
  const [showNewModal, setShowNewModal] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');
  const [template, setTemplate] = useState('blank');
  const [showUserMenu, setShowUserMenu] = useState(false);

  // Teammate Invitation Modal State
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('Fullstack Engineer');
  const [invitedMembers, setInvitedMembers] = useState<InvitedTeammate[]>([]);
  const [copySuccess, setCopySuccess] = useState(false);
  const [inviteSuccessMsg, setInviteSuccessMsg] = useState<string | null>(null);

  // Load teammates from localStorage for the active workspace
  useEffect(() => {
    if (!currentProject) return;
    try {
      const stored = localStorage.getItem(`summit_teammates_${currentProject.id}`);
      if (stored) {
        setInvitedMembers(JSON.parse(stored));
      } else {
        setInvitedMembers([]);
      }
    } catch (e) {
      setInvitedMembers([]);
    }
  }, [currentProject?.id]);

  const handleInviteTeammate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inviteEmail.trim() || !currentProject) return;

    const email = inviteEmail.trim().toLowerCase();

    // Avoid duplicate email
    if (invitedMembers.some((m) => m.email === email)) {
      setInviteSuccessMsg(`Teammate with email ${email} is already added.`);
      setTimeout(() => setInviteSuccessMsg(null), 3000);
      return;
    }

    const newMember: InvitedTeammate = {
      email,
      role: inviteRole,
      invitedAt: new Date().toLocaleDateString()
    };

    const updated = [newMember, ...invitedMembers];
    setInvitedMembers(updated);
    localStorage.setItem(`summit_teammates_${currentProject.id}`, JSON.stringify(updated));

    setInviteEmail('');
    setInviteSuccessMsg(`Teammate ${email} added successfully with ${inviteRole} access.`);
    setTimeout(() => setInviteSuccessMsg(null), 3500);
  };

  const handleRemoveTeammate = (email: string) => {
    if (!currentProject) return;
    const updated = invitedMembers.filter((m) => m.email !== email);
    setInvitedMembers(updated);
    localStorage.setItem(`summit_teammates_${currentProject.id}`, JSON.stringify(updated));
  };

  const handleCopyInviteLink = () => {
    const url = window.location.origin + (currentProject ? `?project=${currentProject.id}` : '');
    navigator.clipboard.writeText(url);
    setCopySuccess(true);
    setTimeout(() => setCopySuccess(false), 2000);
  };

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (newProjectName.trim()) {
      onCreateProject(newProjectName.trim(), template);
      setNewProjectName('');
      setShowNewModal(false);
    }
  };

  return (
    <header style={{
      height: '44px',
      background: 'var(--vscode-bg-topbar)',
      borderBottom: '1px solid var(--vscode-border)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 0.85rem',
      fontSize: '12px',
      zIndex: 10,
      backdropFilter: 'blur(20px)',
      WebkitAppRegion: 'drag' as any
    }}>
      {/* Left: VSCodium Logo & Main Menu */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        {onToggleExplorer && (
          <button
            className="btn-icon"
            onClick={onToggleExplorer}
            title={showExplorer ? 'Hide Primary Side Bar (Ctrl+B)' : 'Show Primary Side Bar (Ctrl+B)'}
            style={{
              color: showExplorer ? 'var(--vscode-text-primary)' : 'var(--vscode-text-muted)',
              padding: '3px 5px'
            }}
          >
            <PanelLeft size={15} />
          </button>
        )}

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {/* macOS Authentic Traffic Lights */}
          <div style={{ display: 'flex', gap: '7px', marginRight: '6px' }}>
            <div style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #ff5f56 0%, #e0443e 100%)',
              boxShadow: '0 1px 4px rgba(255, 95, 86, 0.55)',
              border: '1px solid rgba(0, 0, 0, 0.2)',
              cursor: 'pointer',
              transition: 'transform 0.15s ease'
            }}
              title="Close"
              onMouseEnter={e => e.currentTarget.style.transform = 'scale(1.15)'}
              onMouseLeave={e => e.currentTarget.style.transform = 'scale(1)'}
            />
            <div style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #ffbd2e 0%, #dea123 100%)',
              boxShadow: '0 1px 4px rgba(255, 189, 46, 0.55)',
              border: '1px solid rgba(0, 0, 0, 0.2)',
              cursor: 'pointer',
              transition: 'transform 0.15s ease'
            }}
              title="Minimize"
              onMouseEnter={e => e.currentTarget.style.transform = 'scale(1.15)'}
              onMouseLeave={e => e.currentTarget.style.transform = 'scale(1)'}
            />
            <div style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #27c93f 0%, #1aab29 100%)',
              boxShadow: '0 1px 4px rgba(39, 201, 63, 0.55)',
              border: '1px solid rgba(0, 0, 0, 0.2)',
              cursor: 'pointer',
              transition: 'transform 0.15s ease'
            }}
              title="Maximize"
              onMouseEnter={e => e.currentTarget.style.transform = 'scale(1.15)'}
              onMouseLeave={e => e.currentTarget.style.transform = 'scale(1)'}
            />
          </div>
          <Code2 size={16} color="#60a5fa" />
          <span style={{ fontWeight: 600, fontSize: '13px', color: 'var(--vscode-text-white)', letterSpacing: '-0.01em' }}>
            Summit Studio
          </span>
        </div>

        {/* VS Code Menu Items */}
        <div style={{ display: 'flex', gap: '1px', marginLeft: '0.3rem' }}>
          {['File', 'Edit', 'Selection', 'View', 'Go', 'Terminal'].map((menu) => (
            <span
              key={menu}
              style={{
                padding: '0.25rem 0.55rem',
                color: 'var(--vscode-text-secondary)',
                cursor: 'pointer',
                borderRadius: '6px',
                fontSize: '12px',
                transition: 'all 0.15s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.08)';
                e.currentTarget.style.color = '#ffffff';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
                e.currentTarget.style.color = 'var(--vscode-text-secondary)';
              }}
            >
              {menu}
            </span>
          ))}
        </div>
      </div>

      {/* Center: Command Palette / Workspace Title Bar */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          backgroundColor: 'var(--vscode-bg-input)',
          border: '1px solid var(--vscode-border-light)',
          borderRadius: '10px',
          padding: '0.3rem 0.75rem',
          minWidth: '280px',
          transition: 'all 0.2s ease',
          boxShadow: '0 1px 4px rgba(0,0,0,0.2)'
        }}>
          <FolderGit2 size={13} color="var(--vscode-accent)" />
          <select
            value={currentProject?.id || ''}
            onChange={(e) => onSelectProject(e.target.value)}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--vscode-text-primary)',
              fontSize: '11px',
              fontWeight: 500,
              cursor: 'pointer',
              outline: 'none',
              flex: 1
            }}
          >
            {projects.map((p) => (
              <option key={p.id} value={p.id} style={{ backgroundColor: 'var(--vscode-bg-sidebar)', color: '#fff' }}>
                {p.name} ({p.id})
              </option>
            ))}
          </select>
        </div>

        <button
          className="btn btn-secondary"
          style={{ padding: '0.2rem 0.45rem', fontSize: '11px' }}
          onClick={() => setShowNewModal(true)}
          title="Create New Project Workspace"
        >
          <Plus size={12} />
          <span>New</span>
        </button>
      </div>

      {/* Right: Presence, User Profile, SideBar Toggles */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        {/* Connected Multiplayer Developers */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <Users size={13} color="var(--vscode-text-secondary)" />
          <div style={{ display: 'flex', gap: '0.25rem' }}>
            {connectedUsers.map((u) => (
              <span
                key={u.user_id}
                title={`Connected: ${u.display_name}`}
                style={{
                  fontSize: '10px',
                  padding: '0.1rem 0.35rem',
                  borderRadius: '3px',
                  backgroundColor: u.user_id === currentUser.userId ? 'rgba(255, 255, 255, 0.12)' : 'rgba(255, 255, 255, 0.06)',
                  color: u.user_id === currentUser.userId ? '#ffffff' : 'var(--vscode-text-secondary)',
                  border: '1px solid rgba(255, 255, 255, 0.15)',
                  fontWeight: 500
                }}
              >
                {u.display_name}
              </span>
            ))}
          </div>
        </div>

        {/* Add Teammate Button */}
        <button
          className="btn"
          onClick={() => setShowInviteModal(true)}
          title="Add Teammate by Email"
          style={{
            padding: '0.28rem 0.65rem',
            fontSize: '11px',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            background: 'linear-gradient(135deg, rgba(37, 99, 235, 0.28) 0%, rgba(59, 130, 246, 0.18) 100%)',
            border: '1px solid rgba(96, 165, 250, 0.45)',
            borderRadius: '6px',
            color: '#93c5fd',
            fontWeight: 600,
            cursor: 'pointer',
            boxShadow: '0 1px 4px rgba(37, 99, 235, 0.2)',
            transition: 'all 0.15s ease'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'linear-gradient(135deg, rgba(37, 99, 235, 0.45) 0%, rgba(59, 130, 246, 0.35) 100%)';
            e.currentTarget.style.borderColor = '#60a5fa';
            e.currentTarget.style.color = '#ffffff';
            e.currentTarget.style.boxShadow = '0 0 12px rgba(59, 130, 246, 0.35)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'linear-gradient(135deg, rgba(37, 99, 235, 0.28) 0%, rgba(59, 130, 246, 0.18) 100%)';
            e.currentTarget.style.borderColor = 'rgba(96, 165, 250, 0.45)';
            e.currentTarget.style.color = '#93c5fd';
            e.currentTarget.style.boxShadow = '0 1px 4px rgba(37, 99, 235, 0.2)';
          }}
        >
          <UserPlus size={13} color="#60a5fa" />
          <span>Add Teammate</span>
        </button>

        {/* User Account / Profile Menu Button */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.45rem',
              background: 'linear-gradient(135deg, rgba(30, 58, 138, 0.35) 0%, rgba(37, 99, 235, 0.2) 100%)',
              border: '1px solid rgba(96, 165, 250, 0.4)',
              padding: '0.22rem 0.55rem',
              borderRadius: '6px',
              color: '#ffffff',
              cursor: 'pointer',
              fontSize: '11px',
              fontWeight: 500,
              boxShadow: '0 1px 4px rgba(0, 0, 0, 0.3)',
              transition: 'all 0.15s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'linear-gradient(135deg, rgba(30, 58, 138, 0.5) 0%, rgba(37, 99, 235, 0.35) 100%)';
              e.currentTarget.style.borderColor = '#60a5fa';
              e.currentTarget.style.boxShadow = '0 0 10px rgba(59, 130, 246, 0.25)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'linear-gradient(135deg, rgba(30, 58, 138, 0.35) 0%, rgba(37, 99, 235, 0.2) 100%)';
              e.currentTarget.style.borderColor = 'rgba(96, 165, 250, 0.4)';
              e.currentTarget.style.boxShadow = '0 1px 4px rgba(0, 0, 0, 0.3)';
            }}
          >
            {currentUser.photoURL ? (
              <img
                src={currentUser.photoURL}
                alt="Avatar"
                style={{ width: '18px', height: '18px', borderRadius: '50%', objectFit: 'cover', border: '1px solid #60a5fa' }}
              />
            ) : (
              <div style={{
                width: '18px',
                height: '18px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
                border: '1px solid rgba(147, 197, 253, 0.5)',
                color: '#ffffff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '10px',
                fontWeight: 700,
                boxShadow: '0 0 6px rgba(37, 99, 235, 0.5)'
              }}>
                {currentUser.displayName.charAt(0).toUpperCase()}
              </div>
            )}
            <span style={{ color: '#e0f2fe', fontWeight: 600 }}>{currentUser.displayName}</span>
            <ChevronDown size={11} color="#60a5fa" />
          </button>

          {/* User Dropdown */}
          {showUserMenu && (
            <div
              style={{
                position: 'absolute',
                top: '100%',
                right: 0,
                marginTop: '4px',
                width: '210px',
                backgroundColor: 'var(--vscode-bg-sidebar)',
                border: '1px solid var(--vscode-border-light)',
                borderRadius: '4px',
                boxShadow: '0 8px 24px rgba(0,0,0,0.6)',
                padding: '0.4rem',
                zIndex: 100
              }}
              onClick={() => setShowUserMenu(false)}
            >
              <div style={{ padding: '0.4rem 0.5rem', borderBottom: '1px solid var(--vscode-border)', marginBottom: '0.3rem' }}>
                <div style={{ fontWeight: 600, fontSize: '11px', color: 'var(--vscode-text-white)' }}>
                  {currentUser.displayName}
                </div>
                {currentUser.email && (
                  <div style={{ fontSize: '10px', color: 'var(--vscode-accent-blue)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {currentUser.email}
                  </div>
                )}
                <div style={{ fontSize: '10px', color: 'var(--vscode-text-muted)' }}>
                  {currentUser.role || 'Developer'}
                </div>
              </div>

              {onSignOut && (
                <button
                  onClick={onSignOut}
                  style={{
                    width: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.4rem',
                    padding: '0.35rem 0.5rem',
                    backgroundColor: 'transparent',
                    border: 'none',
                    borderRadius: '3px',
                    color: 'var(--vscode-accent-red)',
                    fontSize: '11px',
                    cursor: 'pointer',
                    textAlign: 'left'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(241, 76, 76, 0.15)'}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                >
                  <LogOut size={12} />
                  <span>Sign Out / Switch Account</span>
                </button>
              )}
            </div>
          )}
        </div>

        {/* AI Agent Panel Toggle */}
        {onToggleAgentPanel && (
          <button
            className="btn-icon"
            onClick={onToggleAgentPanel}
            title={showAgentPanel ? 'Hide AI Assistant Panel' : 'Show AI Assistant Panel'}
            style={{
              color: showAgentPanel ? 'var(--vscode-accent)' : 'var(--vscode-text-muted)',
              padding: '3px 5px'
            }}
          >
            <PanelRight size={15} />
          </button>
        )}
      </div>

      {/* Add / Invite Teammate Modal */}
      {showInviteModal && (
        <div className="modal-overlay" onClick={() => setShowInviteModal(false)}>
          <div className="modal-box" style={{ maxWidth: '480px' }} onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <div style={{
                padding: '0.4rem',
                borderRadius: '6px',
                backgroundColor: 'rgba(0, 122, 204, 0.2)',
                color: 'var(--vscode-accent-blue)',
                display: 'flex'
              }}>
                <UserPlus size={18} />
              </div>
              <div>
                <h3 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--vscode-text-white)', margin: 0 }}>
                  Add Teammate to Workspace
                </h3>
                <p style={{ fontSize: '11px', color: 'var(--vscode-text-muted)', margin: 0 }}>
                  Workspace: <span style={{ color: 'var(--vscode-accent)' }}>{currentProject?.name || 'Current'}</span>
                </p>
              </div>
            </div>

            {/* Notification message */}
            {inviteSuccessMsg && (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                padding: '0.5rem 0.75rem',
                backgroundColor: 'rgba(106, 153, 85, 0.15)',
                border: '1px solid rgba(106, 153, 85, 0.4)',
                borderRadius: '4px',
                color: '#6a9955',
                fontSize: '11px',
                marginBottom: '0.85rem'
              }}>
                <Check size={13} />
                <span>{inviteSuccessMsg}</span>
              </div>
            )}

            {/* Add Teammate Form */}
            <form onSubmit={handleInviteTeammate} style={{ marginBottom: '1.25rem' }}>
              <div style={{ marginBottom: '0.75rem' }}>
                <label style={{ display: 'block', fontSize: '11px', color: 'var(--vscode-text-secondary)', marginBottom: '0.3rem', fontWeight: 500 }}>
                  Teammate Email Address
                </label>
                <div style={{ position: 'relative' }}>
                  <input
                    type="email"
                    required
                    className="input"
                    style={{ width: '100%', paddingLeft: '2rem' }}
                    placeholder="e.g. colleague@company.com or gmail"
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                    autoFocus
                  />
                  <Mail
                    size={13}
                    color="var(--vscode-text-muted)"
                    style={{ position: 'absolute', left: '0.65rem', top: '50%', transform: 'translateY(-50%)' }}
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '0.5rem', alignItems: 'flex-end' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '11px', color: 'var(--vscode-text-secondary)', marginBottom: '0.3rem', fontWeight: 500 }}>
                    Role & Permissions
                  </label>
                  <select
                    className="input"
                    style={{ width: '100%' }}
                    value={inviteRole}
                    onChange={(e) => setInviteRole(e.target.value)}
                  >
                    <option value="Fullstack Engineer">Fullstack Engineer (Full Read/Write)</option>
                    <option value="Frontend Specialist">Frontend Specialist</option>
                    <option value="Backend Architect">Backend Architect</option>
                    <option value="Code Reviewer">Code Reviewer (Read Only)</option>
                  </select>
                </div>

                <button
                  type="submit"
                  className="btn btn-primary"
                  style={{ height: '30px', padding: '0 0.85rem', fontSize: '11px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.35rem' }}
                >
                  <UserPlus size={13} />
                  <span>Add Member</span>
                </button>
              </div>
            </form>

            {/* Direct Workspace Sharing Link */}
            <div style={{
              padding: '0.65rem 0.8rem',
              backgroundColor: 'var(--vscode-bg-editor)',
              border: '1px solid var(--vscode-border)',
              borderRadius: '4px',
              marginBottom: '1rem'
            }}>
              <div style={{ fontSize: '11px', color: 'var(--vscode-text-muted)', marginBottom: '0.35rem', fontWeight: 500 }}>
                Direct Workspace Link
              </div>
              <div style={{ display: 'flex', gap: '0.4rem' }}>
                <input
                  type="text"
                  readOnly
                  className="input"
                  style={{ flex: 1, fontSize: '11px', color: 'var(--vscode-text-secondary)', backgroundColor: '#181818' }}
                  value={window.location.origin + (currentProject ? `?project=${currentProject.id}` : '')}
                />
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handleCopyInviteLink}
                  style={{ fontSize: '11px', padding: '0 0.6rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}
                >
                  {copySuccess ? <Check size={12} color="#6a9955" /> : <Copy size={12} />}
                  <span>{copySuccess ? 'Copied' : 'Copy'}</span>
                </button>
              </div>
            </div>

            {/* List of Teammates & Collaborators */}
            <div>
              <div style={{ fontSize: '11px', color: 'var(--vscode-text-secondary)', fontWeight: 600, marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                <ShieldCheck size={13} color="var(--vscode-accent-cyan)" />
                <span>Workspace Members ({invitedMembers.length + 1})</span>
              </div>

              <div style={{
                maxHeight: '140px',
                overflowY: 'auto',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.4rem',
                border: '1px solid var(--vscode-border)',
                borderRadius: '4px',
                padding: '0.4rem',
                backgroundColor: '#181818'
              }}>
                {/* Active Current User */}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '0.35rem 0.5rem',
                  backgroundColor: 'rgba(0, 122, 204, 0.12)',
                  borderRadius: '3px',
                  border: '1px solid rgba(0, 122, 204, 0.3)'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#6a9955' }} />
                    <div>
                      <div style={{ fontSize: '11px', fontWeight: 600, color: '#fff' }}>
                        {currentUser.displayName} <span style={{ fontSize: '10px', color: 'var(--vscode-accent-blue)' }}>(You / Owner)</span>
                      </div>
                      <div style={{ fontSize: '10px', color: 'var(--vscode-text-muted)' }}>
                        {currentUser.email || 'Workspace Lead'}
                      </div>
                    </div>
                  </div>
                  <span style={{ fontSize: '10px', color: 'var(--vscode-text-muted)', backgroundColor: 'var(--vscode-bg-sidebar)', padding: '2px 6px', borderRadius: '3px' }}>
                    Owner
                  </span>
                </div>

                {/* Invited Members */}
                {invitedMembers.map((member) => (
                  <div
                    key={member.email}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '0.35rem 0.5rem',
                      backgroundColor: 'var(--vscode-bg-sidebar)',
                      borderRadius: '3px',
                      border: '1px solid var(--vscode-border)'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#cca700' }} />
                      <div>
                        <div style={{ fontSize: '11px', fontWeight: 500, color: '#fff' }}>
                          {member.email}
                        </div>
                        <div style={{ fontSize: '10px', color: 'var(--vscode-text-muted)' }}>
                          {member.role} • Added {member.invitedAt}
                        </div>
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={() => handleRemoveTeammate(member.email)}
                      title="Remove Teammate"
                      style={{
                        background: 'transparent',
                        border: 'none',
                        color: 'var(--vscode-text-muted)',
                        cursor: 'pointer',
                        padding: '2px 4px',
                        borderRadius: '3px'
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.color = 'var(--vscode-accent-red)'}
                      onMouseLeave={(e) => e.currentTarget.style.color = 'var(--vscode-text-muted)'}
                    >
                      <Trash2 size={12} />
                    </button>
                  </div>
                ))}
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1rem' }}>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setShowInviteModal(false)}
                style={{ fontSize: '11px', padding: '0.35rem 0.8rem' }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* New Project Modal */}
      {showNewModal && (
        <div className="modal-overlay" onClick={() => setShowNewModal(false)}>
          <div className="modal-box" onClick={(e) => e.stopPropagation()}>
            <h3 style={{ marginBottom: '1rem', fontSize: '13px', fontWeight: 600, color: 'var(--vscode-text-white)' }}>
              Create New Project Workspace
            </h3>
            <form onSubmit={handleCreate}>
              <div style={{ marginBottom: '0.85rem' }}>
                <label style={{ display: 'block', fontSize: '11px', color: 'var(--vscode-text-secondary)', marginBottom: '0.3rem' }}>
                  Project Name
                </label>
                <input
                  type="text"
                  className="input"
                  style={{ width: '100%' }}
                  placeholder="e.g., Auth Service or Data API"
                  value={newProjectName}
                  onChange={(e) => setNewProjectName(e.target.value)}
                  autoFocus
                />
              </div>
              <div style={{ marginBottom: '1.25rem' }}>
                <label style={{ display: 'block', fontSize: '11px', color: 'var(--vscode-text-secondary)', marginBottom: '0.3rem' }}>
                  Project Template
                </label>
                <select
                  className="input"
                  style={{ width: '100%' }}
                  value={template}
                  onChange={(e) => setTemplate(e.target.value)}
                >
                  <option value="blank">Blank Workspace (Clean)</option>
                  <option value="demo-calculator">Calculator Service Template</option>
                </select>
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.4rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowNewModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Create Workspace
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </header>
  );
};
