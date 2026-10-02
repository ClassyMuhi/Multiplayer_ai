import React, { useState } from 'react';
import type { Project, UserPresence } from '../types';
import {
  Code2,
  Users,
  FolderGit2,
  Plus,
  PanelLeft,
  PanelRight,
  LogOut,
  ChevronDown
} from 'lucide-react';

interface ProjectHeaderProps {
  projects: Project[];
  currentProject: Project | null;
  onSelectProject: (id: string) => void;
  onCreateProject: (name: string, template?: string) => void;
  connectedUsers: UserPresence[];
  currentUser: { userId: string; displayName: string; role?: string };
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
      height: '38px',
      backgroundColor: 'var(--vscode-bg-topbar)',
      borderBottom: '1px solid var(--vscode-border)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 0.6rem',
      fontSize: '12px',
      zIndex: 10
    }}>
      {/* Left: VSCodium Logo & Main Menu */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        {onToggleExplorer && (
          <button
            className="btn-icon"
            onClick={onToggleExplorer}
            title={showExplorer ? 'Hide Primary Side Bar (Ctrl+B)' : 'Show Primary Side Bar (Ctrl+B)'}
            style={{
              color: showExplorer ? 'var(--vscode-accent)' : 'var(--vscode-text-muted)',
              padding: '3px 5px'
            }}
          >
            <PanelLeft size={15} />
          </button>
        )}

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--vscode-accent)' }}>
          <Code2 size={16} />
          <span style={{ fontWeight: 600, fontSize: '12px', color: 'var(--vscode-text-white)' }}>
            Summit VSCodium
          </span>
        </div>

        {/* VS Code Menu Items */}
        <div style={{ display: 'flex', gap: '0.2rem', marginLeft: '0.25rem' }}>
          {['File', 'Edit', 'Selection', 'View', 'Go', 'Terminal'].map((menu) => (
            <span
              key={menu}
              style={{
                padding: '0.2rem 0.4rem',
                color: 'var(--vscode-text-secondary)',
                cursor: 'pointer',
                borderRadius: '3px',
                fontSize: '11px'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.06)';
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
          gap: '0.4rem',
          backgroundColor: 'var(--vscode-bg-input)',
          border: '1px solid var(--vscode-border-light)',
          borderRadius: '4px',
          padding: '0.2rem 0.6rem',
          minWidth: '260px'
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
          <Users size={13} color="var(--vscode-accent-cyan)" />
          <div style={{ display: 'flex', gap: '0.25rem' }}>
            {connectedUsers.map((u) => (
              <span
                key={u.user_id}
                title={`Connected: ${u.display_name}`}
                style={{
                  fontSize: '10px',
                  padding: '0.1rem 0.35rem',
                  borderRadius: '3px',
                  backgroundColor: u.user_id === currentUser.userId ? 'rgba(0, 122, 204, 0.25)' : 'rgba(78, 201, 176, 0.15)',
                  color: u.user_id === currentUser.userId ? 'var(--vscode-accent-blue)' : 'var(--vscode-accent-cyan)',
                  border: '1px solid currentColor',
                  fontWeight: 500
                }}
              >
                {u.display_name}
              </span>
            ))}
          </div>
        </div>

        {/* User Account / Profile Menu */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
              backgroundColor: 'rgba(255,255,255,0.06)',
              border: '1px solid var(--vscode-border)',
              padding: '0.2rem 0.5rem',
              borderRadius: '3px',
              color: 'var(--vscode-text-white)',
              cursor: 'pointer',
              fontSize: '11px',
              fontWeight: 500
            }}
          >
            <div style={{
              width: '16px',
              height: '16px',
              borderRadius: '50%',
              backgroundColor: 'var(--vscode-accent)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '9px',
              fontWeight: 700
            }}>
              {currentUser.displayName.charAt(0).toUpperCase()}
            </div>
            <span>{currentUser.displayName}</span>
            <ChevronDown size={11} color="var(--vscode-text-muted)" />
          </button>

          {/* User Dropdown */}
          {showUserMenu && (
            <div
              style={{
                position: 'absolute',
                top: '100%',
                right: 0,
                marginTop: '4px',
                width: '190px',
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
                  <span>Switch Account / Sign Out</span>
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
