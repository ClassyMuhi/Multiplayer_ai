import React from 'react';
import {
  Code2,
  FolderKanban,
  Square,
  RefreshCw,
  Users,
  Sparkles,
  ChevronRight,
  Radio,
  AlertCircle,
} from 'lucide-react';
import { Project, AgentSessionStatus } from '../../types';

interface TopBarProps {
  project: Project;
  agentStatus: AgentSessionStatus;
  wsConnected: boolean;
  connectedUsersCount: number;
  onOpenProjectSelector: () => void;
  onStopAgent?: () => void;
  onOpenSummaryModal?: () => void;
}

export const TopBar: React.FC<TopBarProps> = ({
  project,
  agentStatus,
  wsConnected,
  connectedUsersCount,
  onOpenProjectSelector,
  onStopAgent,
  onOpenSummaryModal,
}) => {
  const isAgentActive =
    agentStatus.status === 'thinking' ||
    agentStatus.status === 'working' ||
    agentStatus.status === 'running_command' ||
    agentStatus.status === 'THINKING' ||
    agentStatus.status === 'EXECUTING';

  const getStatusBadge = () => {
    const s = agentStatus.status.toLowerCase();
    switch (s) {
      case 'thinking':
        return (
          <span className="badge purple animate-pulse-glow">
            <Sparkles size={12} className="animate-spin" /> Thinking...
          </span>
        );
      case 'working':
      case 'executing':
      case 'running_command':
        return (
          <span className="badge info animate-pulse-glow">
            <RefreshCw size={12} className="animate-spin" /> {agentStatus.currentStep || agentStatus.current_action || 'Working...'}
          </span>
        );
      case 'completed':
        return <span className="badge success">✓ Agent Ready</span>;
      case 'stopped':
        return <span className="badge">■ Stopped</span>;
      case 'error':
        return <span className="badge danger">⚠ Error</span>;
      default:
        return <span className="badge success">● Agent Ready</span>;
    }
  };

  return (
    <div className="topbar-container">
      {/* Left: Branding & Breadcrumbs */}
      <div className="topbar-left">
        <div
          className="topbar-brand"
          onClick={onOpenProjectSelector}
          title="Return to Projects List"
        >
          <Code2 size={16} color="var(--accent-primary)" />
          <span className="brand-name">Agentic IDE</span>
        </div>

        <div className="topbar-breadcrumbs">
          <ChevronRight size={14} className="breadcrumb-separator" />
          <button
            className="breadcrumb-project-btn"
            onClick={onOpenProjectSelector}
            title="Switch Workspace"
          >
            <FolderKanban size={13} />
            <span>{project.name}</span>
          </button>
        </div>
      </div>

      {/* Right: Agent Status, Stop Button, Presence, Summary */}
      <div className="topbar-right">
        {getStatusBadge()}

        {isAgentActive && onStopAgent && (
          <button
            onClick={onStopAgent}
            className="topbar-btn-stop"
            title="Stop Current Agent Execution"
          >
            <Square size={11} fill="#f85149" />
            <span>Stop</span>
          </button>
        )}

        {onOpenSummaryModal && (
          <button
            onClick={onOpenSummaryModal}
            className="topbar-btn-subtle"
            title="View Project Summary"
          >
            <Sparkles size={12} color="var(--accent-amber)" />
            <span>Summary</span>
          </button>
        )}

        <div
          className="topbar-presence-badge"
          title={`${connectedUsersCount} developer(s) connected to this workspace`}
        >
          <Users size={12} color="var(--accent-green-bright)" />
          <span>{connectedUsersCount} Online</span>
        </div>

        <div
          className={`topbar-connection-badge ${wsConnected ? 'connected' : 'disconnected'}`}
          title={wsConnected ? 'WebSocket live connection active' : 'Disconnected from server'}
        >
          {wsConnected ? <Radio size={11} /> : <AlertCircle size={11} />}
          <span>{wsConnected ? 'Live' : 'Offline'}</span>
        </div>
      </div>
    </div>
  );
};
