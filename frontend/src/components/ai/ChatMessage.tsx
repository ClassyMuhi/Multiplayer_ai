import React, { useState } from 'react';
import {
  User,
  Bot,
  CheckCircle2,
  FileCode,
  Terminal,
  ChevronDown,
  ChevronRight,
  AlertCircle,
  Clock,
  Sparkles,
  Search,
} from 'lucide-react';
import { ChatMessage as ChatMessageType, ToolExecution } from '../../types';

interface ChatMessageProps {
  message: ChatMessageType;
  onOpenFile?: (path: string) => void;
}

export const ChatMessageItem: React.FC<ChatMessageProps> = ({ message, onOpenFile }) => {
  const [expandedTools, setExpandedTools] = useState<Record<string, boolean>>({});

  const toggleTool = (toolId: string) => {
    setExpandedTools((prev) => ({ ...prev, [toolId]: !prev[toolId] }));
  };

  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';

  const formatTime = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch {
      return '';
    }
  };

  const renderToolIcon = (name: string) => {
    switch (name) {
      case 'read_file':
      case 'read_file_lines':
      case 'list_dir':
      case 'search_files':
        return <Search size={14} className="tool-icon search" />;
      case 'write_file':
      case 'create_file':
      case 'patch_file':
        return <FileCode size={14} className="tool-icon file" />;
      case 'run_terminal':
      case 'execute_command':
        return <Terminal size={14} className="tool-icon terminal" />;
      default:
        return <Sparkles size={14} className="tool-icon ai" />;
    }
  };

  return (
    <div className={`chat-message ${message.role}`}>
      <div className="message-header">
        <div className="message-avatar">
          {isUser ? <User size={14} /> : <Bot size={14} />}
        </div>
        <span className="message-sender">
          {isUser ? message.userName || 'You' : 'Agentic AI'}
        </span>
        <span className="message-time">
          <Clock size={11} />
          {formatTime(message.timestamp)}
        </span>
      </div>

      <div className="message-body">
        {/* Thinking / Context retrieval note if present */}
        {message.thought && (
          <div className="agent-thought-card">
            <div className="thought-title">
              <Sparkles size={12} />
              <span>Thought Process</span>
            </div>
            <div className="thought-content">{message.thought}</div>
          </div>
        )}

        {/* Text content */}
        {message.content && (
          <div className="message-text-content">
            {message.content.split('\n').map((line, i) => (
              <p key={i}>{line}</p>
            ))}
          </div>
        )}

        {/* Tool executions (e.g. read_file, write_file, run_terminal) */}
        {message.toolExecutions && message.toolExecutions.length > 0 && (
          <div className="tool-executions-list">
            {message.toolExecutions.map((tool: ToolExecution, idx: number) => {
              const toolKey = `${tool.name}-${idx}`;
              const isExpanded = expandedTools[toolKey] || false;
              const hasOutput = tool.output && tool.output.trim().length > 0;

              return (
                <div key={toolKey} className={`tool-item-card ${tool.status}`}>
                  <div
                    className="tool-item-header"
                    onClick={() => hasOutput && toggleTool(toolKey)}
                  >
                    <div className="tool-item-meta">
                      {renderToolIcon(tool.name)}
                      <span className="tool-name">{tool.name}</span>
                      {tool.input && (
                        <span
                          className="tool-input-hint"
                          onClick={(e) => {
                            if (tool.input.file_path && onOpenFile) {
                              e.stopPropagation();
                              onOpenFile(tool.input.file_path);
                            }
                          }}
                        >
                          {tool.input.file_path ||
                            tool.input.command ||
                            tool.input.path ||
                            tool.input.query ||
                            JSON.stringify(tool.input).slice(0, 40)}
                        </span>
                      )}
                    </div>

                    <div className="tool-item-status-col">
                      {tool.status === 'completed' ? (
                        <span className="tool-badge success">
                          <CheckCircle2 size={12} /> Done
                        </span>
                      ) : tool.status === 'error' ? (
                        <span className="tool-badge error">
                          <AlertCircle size={12} /> Failed
                        </span>
                      ) : (
                        <span className="tool-badge running">Running...</span>
                      )}
                      {hasOutput && (
                        <button className="tool-expand-btn">
                          {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Collapsible output block */}
                  {isExpanded && tool.output && (
                    <div className="tool-output-block">
                      <pre>{tool.output}</pre>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
