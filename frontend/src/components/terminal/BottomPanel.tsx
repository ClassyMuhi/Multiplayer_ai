import React, { useState, useEffect } from 'react';
import {
  Terminal as TerminalIcon,
  Activity,
  Brain,
  FileText,
  Search,
  Plus,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  X,
  Trash2,
  Tag,
  Clock,
  CheckCircle2,
  AlertCircle,
  FileCode,
  Sparkles,
} from 'lucide-react';
import { ProjectMemory, ProjectSummary, AppEvent } from '../../types';

interface BottomPanelProps {
  projectId: string;
  terminalOutput: string;
  agentEvents: AppEvent[];
  memories: ProjectMemory[];
  summary: ProjectSummary | null;
  activeTab: 'terminal' | 'activity' | 'memory' | 'summary';
  isOpen: boolean;
  onTabChange: (tab: 'terminal' | 'activity' | 'memory' | 'summary') => void;
  onToggleOpen: () => void;
  onClearTerminal: () => void;
  onSearchMemories: (query: string) => void;
  onRefreshMemories: () => void;
  onRefreshSummary: () => void;
  onOpenAddMemoryModal: () => void;
  onOpenEditSummaryModal: () => void;
  onDeleteMemory?: (memoryId: string) => void;
}

export const BottomPanel: React.FC<BottomPanelProps> = ({
  projectId,
  terminalOutput,
  agentEvents,
  memories,
  summary,
  activeTab,
  isOpen,
  onTabChange,
  onToggleOpen,
  onClearTerminal,
  onSearchMemories,
  onRefreshMemories,
  onRefreshSummary,
  onOpenAddMemoryModal,
  onOpenEditSummaryModal,
  onDeleteMemory,
}) => {
  const [memorySearchQuery, setMemorySearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearchMemories(memorySearchQuery);
  };

  const categories = ['all', 'architecture', 'conventions', 'decisions', 'bugs', 'general'];

  const filteredMemories = memories.filter((mem) => {
    if (selectedCategory === 'all') return true;
    return mem.category?.toLowerCase() === selectedCategory.toLowerCase();
  });

  const formatEventTime = (timestamp: string) => {
    try {
      const d = new Date(timestamp);
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch {
      return '';
    }
  };

  const renderEventIcon = (type: string) => {
    switch (type) {
      case 'tool_call':
      case 'tool_result':
        return <FileCode size={13} className="ev-icon code" />;
      case 'terminal_output':
        return <TerminalIcon size={13} className="ev-icon terminal" />;
      case 'memory_saved':
      case 'memory_retrieved':
        return <Brain size={13} className="ev-icon memory" />;
      case 'agent_error':
        return <AlertCircle size={13} className="ev-icon error" />;
      default:
        return <Activity size={13} className="ev-icon info" />;
    }
  };

  if (!isOpen) {
    return (
      <div className="bottom-panel-collapsed" onClick={onToggleOpen}>
        <div className="collapsed-tabs">
          <span className="collapsed-tab-btn">
            <TerminalIcon size={13} /> Terminal
          </span>
          <span className="collapsed-tab-btn">
            <Activity size={13} /> Activity ({agentEvents.length})
          </span>
          <span className="collapsed-tab-btn">
            <Brain size={13} /> Memory ({memories.length})
          </span>
          <span className="collapsed-tab-btn">
            <FileText size={13} /> Summary
          </span>
        </div>
        <button className="panel-expand-btn" title="Expand Bottom Panel">
          <ChevronUp size={14} />
        </button>
      </div>
    );
  }

  return (
    <div className="bottom-panel-container">
      {/* Panel Tab Header */}
      <div className="bottom-panel-header">
        <div className="panel-tabs">
          <button
            className={`panel-tab ${activeTab === 'terminal' ? 'active' : ''}`}
            onClick={() => onTabChange('terminal')}
          >
            <TerminalIcon size={14} />
            <span>Terminal Output</span>
          </button>

          <button
            className={`panel-tab ${activeTab === 'activity' ? 'active' : ''}`}
            onClick={() => onTabChange('activity')}
          >
            <Activity size={14} />
            <span>Agent Activity</span>
            {agentEvents.length > 0 && <span className="tab-count">{agentEvents.length}</span>}
          </button>

          <button
            className={`panel-tab ${activeTab === 'memory' ? 'active' : ''}`}
            onClick={() => onTabChange('memory')}
          >
            <Brain size={14} />
            <span>Project Memory</span>
            {memories.length > 0 && <span className="tab-count">{memories.length}</span>}
          </button>

          <button
            className={`panel-tab ${activeTab === 'summary' ? 'active' : ''}`}
            onClick={() => onTabChange('summary')}
          >
            <FileText size={14} />
            <span>Project Summary</span>
          </button>
        </div>

        <div className="panel-controls">
          {activeTab === 'terminal' && (
            <button className="btn-icon-panel" onClick={onClearTerminal} title="Clear Terminal">
              <Trash2 size={13} />
            </button>
          )}

          {activeTab === 'memory' && (
            <>
              <button
                className="btn-text-panel"
                onClick={onOpenAddMemoryModal}
                title="Add New Memory"
              >
                <Plus size={13} />
                <span>Add Memory</span>
              </button>
              <button
                className="btn-icon-panel"
                onClick={onRefreshMemories}
                title="Refresh Memories"
              >
                <RefreshCw size={13} />
              </button>
            </>
          )}

          {activeTab === 'summary' && (
            <>
              <button
                className="btn-text-panel"
                onClick={onOpenEditSummaryModal}
                title="Edit Summary"
              >
                <Sparkles size={13} />
                <span>Edit Summary</span>
              </button>
              <button
                className="btn-icon-panel"
                onClick={onRefreshSummary}
                title="Refresh Summary"
              >
                <RefreshCw size={13} />
              </button>
            </>
          )}

          <button className="btn-icon-panel" onClick={onToggleOpen} title="Minimize Panel">
            <ChevronDown size={14} />
          </button>
        </div>
      </div>

      {/* Panel Body Content */}
      <div className="bottom-panel-content">
        {/* TAB 1: TERMINAL */}
        {activeTab === 'terminal' && (
          <div className="terminal-view">
            {terminalOutput ? (
              <pre className="terminal-pre">{terminalOutput}</pre>
            ) : (
              <div className="terminal-empty">
                <TerminalIcon size={24} className="dimmed-icon" />
                <p>No terminal or test output yet. Run a command with the AI agent to see live output here.</p>
              </div>
            )}
          </div>
        )}

        {/* TAB 2: AGENT ACTIVITY TIMELINE */}
        {activeTab === 'activity' && (
          <div className="activity-view">
            {agentEvents.length === 0 ? (
              <div className="activity-empty">
                <Activity size={24} className="dimmed-icon" />
                <p>No agent activity recorded yet. Send a prompt to the AI agent to see real-time steps.</p>
              </div>
            ) : (
              <div className="activity-timeline">
                {agentEvents.map((ev, index) => (
                  <div key={index} className="activity-item">
                    <div className="activity-time">{formatEventTime(ev.timestamp)}</div>
                    <div className="activity-icon-col">{renderEventIcon(ev.type)}</div>
                    <div className="activity-content">
                      <span className="activity-type-badge">{ev.type.replace('_', ' ')}</span>
                      <span className="activity-detail">
                        {typeof ev.data === 'string'
                          ? ev.data
                          : ev.data?.message ||
                            ev.data?.tool ||
                            ev.data?.file_path ||
                            ev.data?.command ||
                            JSON.stringify(ev.data)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* TAB 3: PROJECT MEMORY */}
        {activeTab === 'memory' && (
          <div className="memory-view">
            {/* Search & Category Filter Bar */}
            <div className="memory-toolbar">
              <form className="memory-search-form" onSubmit={handleSearchSubmit}>
                <Search size={14} className="search-icon" />
                <input
                  type="text"
                  placeholder="Semantic search project memories..."
                  value={memorySearchQuery}
                  onChange={(e) => setMemorySearchQuery(e.target.value)}
                />
                {memorySearchQuery && (
                  <button
                    type="button"
                    className="clear-search-btn"
                    onClick={() => {
                      setMemorySearchQuery('');
                      onSearchMemories('');
                    }}
                  >
                    <X size={12} />
                  </button>
                )}
              </form>

              <div className="category-chips">
                {categories.map((cat) => (
                  <button
                    key={cat}
                    className={`category-chip ${selectedCategory === cat ? 'active' : ''}`}
                    onClick={() => setSelectedCategory(cat)}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>

            {/* Memories List */}
            {filteredMemories.length === 0 ? (
              <div className="memory-empty">
                <Brain size={24} className="dimmed-icon" />
                <p>No memories found for this project. Memories are automatically saved by the agent or can be added manually.</p>
              </div>
            ) : (
              <div className="memory-cards-grid">
                {filteredMemories.map((mem) => (
                  <div key={mem.id} className="memory-card">
                    <div className="memory-card-header">
                      <span className="memory-category-tag">
                        <Tag size={11} />
                        {mem.category || 'general'}
                      </span>
                      {mem.importance !== undefined && (
                        <span className="memory-importance-tag">
                          Importance: {mem.importance}/5
                        </span>
                      )}
                      {onDeleteMemory && (
                        <button
                          className="memory-delete-btn"
                          onClick={() => onDeleteMemory(mem.id)}
                          title="Delete memory"
                        >
                          <Trash2 size={12} />
                        </button>
                      )}
                    </div>
                    <div className="memory-card-content">{mem.content}</div>
                    <div className="memory-card-footer">
                      <span className="memory-date">
                        <Clock size={10} />
                        {formatEventTime(mem.created_at || '')}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* TAB 4: PROJECT SUMMARY */}
        {activeTab === 'summary' && (
          <div className="summary-view">
            {summary && summary.content ? (
              <div className="summary-content-box">
                <div className="summary-header-row">
                  <h3>Project Context & Architecture</h3>
                  <span className="summary-updated">
                    Updated: {summary.updated_at ? new Date(summary.updated_at).toLocaleString() : 'Recently'}
                  </span>
                </div>
                <div className="summary-markdown">
                  {summary.content.split('\n').map((line, i) => (
                    <p key={i}>{line}</p>
                  ))}
                </div>
              </div>
            ) : (
              <div className="summary-empty">
                <FileText size={24} className="dimmed-icon" />
                <p>No project summary generated yet.</p>
                <button className="btn-primary-small" onClick={onOpenEditSummaryModal}>
                  Create Project Summary
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
