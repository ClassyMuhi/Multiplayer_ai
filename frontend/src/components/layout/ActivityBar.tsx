import React from 'react';
import {
  Files,
  Brain,
  FileText,
} from 'lucide-react';

export type ActivityTab = 'explorer' | 'memory' | 'summary';

interface ActivityBarProps {
  activeView: ActivityTab;
  onSelectView: (view: ActivityTab) => void;
  agentRunning?: boolean;
}

export const ActivityBar: React.FC<ActivityBarProps> = ({
  activeView,
  onSelectView,
}) => {
  return (
    <div className="activity-bar-container">
      {/* Top Navigation Icons */}
      <div className="activity-bar-top">
        <button
          title="File Explorer (Ctrl+Shift+E)"
          onClick={() => onSelectView('explorer')}
          className={`activity-bar-btn ${activeView === 'explorer' ? 'active' : ''}`}
        >
          <Files size={20} />
        </button>

        <button
          title="Project Memories"
          onClick={() => onSelectView('memory')}
          className={`activity-bar-btn ${activeView === 'memory' ? 'active' : ''}`}
        >
          <Brain size={20} />
        </button>

        <button
          title="Project Summary"
          onClick={() => onSelectView('summary')}
          className={`activity-bar-btn ${activeView === 'summary' ? 'active' : ''}`}
        >
          <FileText size={20} />
        </button>
      </div>
    </div>
  );
};
