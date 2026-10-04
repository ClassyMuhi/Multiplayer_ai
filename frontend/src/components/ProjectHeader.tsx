import React, { useState } from 'react';
import type { Project, UserPresence } from '../types';
import { Sparkles, Users, FolderGit2, Plus, UserCheck } from 'lucide-react';


interface ProjectHeaderProps {
  projects: Project[];
  currentProject: Project | null;
  onSelectProject: (id: string) => void;
  onCreateProject: (name: string, template?: string) => void;
  connectedUsers: UserPresence[];
  currentUser: { userId: string; displayName: string };
  onSwitchUser: (userId: string, displayName: string) => void;
}

export const ProjectHeader: React.FC<ProjectHeaderProps> = ({
  projects,
  currentProject,
  onSelectProject,
  onCreateProject,
  connectedUsers,
  currentUser,
  onSwitchUser
}) => {
  const [showNewModal, setShowNewModal] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');
  const [template, setTemplate] = useState('blank');

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
      height: '52px',
      backgroundColor: 'var(--bg-panel)',
      borderBottom: '1px solid var(--border-color)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 1rem'
    }}>
      {/* Left: Branding & Project Selector */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Sparkles size={20} color="var(--accent-blue)" />
          <span style={{ fontWeight: 700, fontSize: '1rem', letterSpacing: '-0.02em', background: 'linear-gradient(to right, #38bdf8, #818cf8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Summit AI Workspace
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <FolderGit2 size={16} color="var(--text-muted)" />
          <select
            className="input"
            value={currentProject?.id || ''}
            onChange={(e) => onSelectProject(e.target.value)}
            style={{ fontWeight: 500 }}
          >
            {projects.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.id})
              </option>
            ))}
          </select>

          <button className="btn btn-secondary" onClick={() => setShowNewModal(true)}>
            <Plus size={14} /> New
          </button>
        </div>
      </div>

      {/* Right: Presence & Multi-User Switcher */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
        {/* User Identity Switcher */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', backgroundColor: 'var(--bg-card)', padding: '0.2rem 0.5rem', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
          <UserCheck size={14} color="var(--accent-green)" />
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Acting as:</span>
          <select
            style={{ background: 'transparent', border: 'none', color: 'var(--accent-blue)', fontWeight: 600, fontSize: '0.8rem', cursor: 'pointer', outline: 'none' }}
            value={currentUser.userId}
            onChange={(e) => {
              const val = e.target.value;
              if (val === 'user_a') onSwitchUser('user_a', 'Alice (Dev A)');
              else if (val === 'user_b') onSwitchUser('user_b', 'Bob (Dev B)');
              else onSwitchUser(val, `Developer (${val.slice(0, 4)})`);
            }}
          >
            <option value="user_a">Alice (Dev A)</option>
            <option value="user_b">Bob (Dev B)</option>
          </select>
        </div>

        {/* Online Users List */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Users size={16} color="var(--accent-green)" />
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 500 }}>Online:</span>
          <div style={{ display: 'flex', gap: '0.3rem' }}>
            {connectedUsers.map((u) => (
              <span
                key={u.user_id}
                title={`Connected since ${new Date(u.connected_at).toLocaleTimeString()}`}
                style={{
                  fontSize: '0.725rem',
                  padding: '0.15rem 0.45rem',
                  borderRadius: '12px',
                  backgroundColor: u.user_id === currentUser.userId ? 'rgba(56, 189, 248, 0.2)' : 'rgba(52, 211, 153, 0.15)',
                  color: u.user_id === currentUser.userId ? 'var(--accent-blue)' : 'var(--accent-green)',
                  border: '1px solid currentColor',
                  fontWeight: 500
                }}
              >
                ● {u.display_name}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* New Project Modal */}
      {showNewModal && (
        <div className="modal-overlay" onClick={() => setShowNewModal(false)}>
          <div className="modal-box" onClick={(e) => e.stopPropagation()}>
            <h3 style={{ marginBottom: '1rem', fontSize: '1.1rem' }}>Create New Project Workspace</h3>
            <form onSubmit={handleCreate}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
                  Project Name
                </label>
                <input
                  type="text"
                  className="input"
                  style={{ width: '100%' }}
                  placeholder="e.g., Authentication Service"
                  value={newProjectName}
                  onChange={(e) => setNewProjectName(e.target.value)}
                  autoFocus
                />
              </div>
              <div style={{ marginBottom: '1.25rem' }}>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
                  Project Template
                </label>
                <select
                  className="input"
                  style={{ width: '100%' }}
                  value={template}
                  onChange={(e) => setTemplate(e.target.value)}
                >
                  <option value="blank">✨ Blank Workspace (Empty / Clean)</option>
                  <option value="demo-calculator">🧮 Demo Calculator Template</option>
                </select>
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowNewModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Create Project
                </button>
              </div>
            </form>

          </div>
        </div>
      )}
    </header>
  );
};
