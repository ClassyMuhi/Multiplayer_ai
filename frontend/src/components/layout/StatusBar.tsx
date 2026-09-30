import React from 'react';
import {
  GitBranch,
  Radio,
  FileCode2,
  AlertCircle,
  Clock,
  Sparkles,
  Info,
} from 'lucide-react';
import { AgentSessionStatus } from '../../types';

interface StatusBarProps {
  activeFilePath: string | null;
  wsConnected: boolean;
  agentStatus: AgentSessionStatus;
  notification: string | null;
}

export const StatusBar: React.FC<StatusBarProps> = ({
  activeFilePath,
  wsConnected,
  agentStatus,
  notification,
}) => {
  const getLanguage = (path: string | null) => {
    if (!path) return 'Plain Text';
    const ext = path.split('.').pop()?.toLowerCase();
    switch (ext) {
      case 'py':
        return 'Python';
      case 'ts':
      case 'tsx':
        return 'TypeScript';
      case 'js':
      case 'jsx':
        return 'JavaScript';
      case 'json':
        return 'JSON';
      case 'md':
        return 'Markdown';
      case 'html':
        return 'HTML';
      case 'css':
        return 'CSS';
      case 'sql':
        return 'SQL';
      case 'sh':
        return 'Shell';
      default:
        return 'Plain Text';
    }
  };

  return (
    <div className="statusbar-container">
      {/* Left side: Branch, notification, active agent action */}
      <div className="statusbar-left">
        <div className="statusbar-item">
          <GitBranch size={12} color="var(--accent-primary)" />
          <span>main</span>
        </div>

        {notification ? (
          <div className="statusbar-notification">
            <Info size={12} />
            <span>{notification}</span>
          </div>
        ) : (
          agentStatus.currentStep && (
            <div className="statusbar-item agent-action">
              <Sparkles size={11} className="spin-slow" />
              <span>{agentStatus.currentStep}</span>
            </div>
          )
        )}
      </div>

      {/* Right side: Language, UTF-8, Spaces, Connection */}
      <div className="statusbar-right">
        {activeFilePath && (
          <div className="statusbar-item">
            <FileCode2 size={12} />
            <span>{getLanguage(activeFilePath)}</span>
          </div>
        )}

        <span className="statusbar-item">UTF-8</span>
        <span className="statusbar-item">Spaces: 2</span>

        <div className={`statusbar-item ${wsConnected ? 'text-green' : 'text-rose'}`}>
          {wsConnected ? <Radio size={11} /> : <AlertCircle size={11} />}
          <span>{wsConnected ? 'Connected' : 'Reconnecting...'}</span>
        </div>
      </div>
    </div>
  );
};
