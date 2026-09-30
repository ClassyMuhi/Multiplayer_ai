import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Square,
  Bot,
  Sparkles,
  RefreshCw,
  Terminal,
  FileCode,
  CheckCircle2,
  AlertTriangle,
  Flame,
} from 'lucide-react';
import { ChatMessage, AgentSessionStatus } from '../../types';
import { ChatMessageItem } from './ChatMessage';

interface AIChatProps {
  projectId: string;
  messages: ChatMessage[];
  agentStatus: AgentSessionStatus;
  onSendMessage: (prompt: string) => void;
  onStopAgent: () => void;
  onOpenFile?: (path: string) => void;
  onClearChat?: () => void;
}

export const AIChat: React.FC<AIChatProps> = ({
  projectId,
  messages,
  agentStatus,
  onSendMessage,
  onStopAgent,
  onOpenFile,
  onClearChat,
}) => {
  const [promptInput, setPromptInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const isAgentActive =
    agentStatus.status === 'thinking' ||
    agentStatus.status === 'working' ||
    agentStatus.status === 'running_command';

  // Auto-scroll on new messages or status changes
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, agentStatus]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!promptInput.trim() || isAgentActive) return;

    onSendMessage(promptInput.trim());
    setPromptInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const quickPrompts = [
    'Explain the architecture and main components of this project',
    'Run pytest to verify all existing backend tests',
    'Inspect the memory system and describe its ChromaDB integration',
    'Review files for security or traversal vulnerabilities',
  ];

  const renderStatusBadge = () => {
    switch (agentStatus.status) {
      case 'thinking':
        return (
          <div className="agent-status-badge thinking">
            <span className="pulsing-dot" />
            <span>Thinking...</span>
          </div>
        );
      case 'working':
        return (
          <div className="agent-status-badge working">
            <span className="pulsing-dot" />
            <span>Working ({agentStatus.currentStep || 'executing'}</span>
          </div>
        );
      case 'running_command':
        return (
          <div className="agent-status-badge running-cmd">
            <Terminal size={12} className="spinning-icon" />
            <span>Running: {agentStatus.activeCommand || 'command'}</span>
          </div>
        );
      case 'stopped':
        return (
          <div className="agent-status-badge stopped">
            <Square size={11} />
            <span>Stopped</span>
          </div>
        );
      case 'error':
        return (
          <div className="agent-status-badge error">
            <AlertTriangle size={12} />
            <span>Error</span>
          </div>
        );
      case 'completed':
        return (
          <div className="agent-status-badge completed">
            <CheckCircle2 size={12} />
            <span>Completed</span>
          </div>
        );
      default:
        return (
          <div className="agent-status-badge ready">
            <span className="status-dot-green" />
            <span>Ready</span>
          </div>
        );
    }
  };

  return (
    <div className="ai-chat-panel">
      {/* Top Header */}
      <div className="ai-chat-header">
        <div className="ai-header-left">
          <Bot size={16} className="ai-brand-icon" />
          <span className="ai-header-title">AI Coding Agent</span>
          {renderStatusBadge()}
        </div>

        <div className="ai-header-actions">
          {isAgentActive && (
            <button
              className="btn-stop-agent"
              onClick={onStopAgent}
              title="Stop Agent Execution"
            >
              <Square size={13} fill="currentColor" />
              <span>Stop</span>
            </button>
          )}
          {onClearChat && (
            <button
              className="btn-icon-subtle"
              onClick={onClearChat}
              title="Clear Chat History"
            >
              <RefreshCw size={13} />
            </button>
          )}
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="ai-chat-messages">
        {messages.length === 0 ? (
          <div className="ai-chat-welcome">
            <div className="welcome-icon-box">
              <Sparkles size={28} />
            </div>
            <h3>Project-Aware AI Assistant</h3>
            <p>
              I have full access to this project's code structure, semantic memories, and context.
              I can read files, write code, run terminal commands, and remember project architecture.
            </p>

            <div className="quick-suggestions-box">
              <span className="suggestions-title">Try asking:</span>
              <div className="quick-chips">
                {quickPrompts.map((prompt, i) => (
                  <button
                    key={i}
                    className="suggestion-chip"
                    onClick={() => {
                      setPromptInput(prompt);
                      textareaRef.current?.focus();
                    }}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <ChatMessageItem key={msg.id} message={msg} onOpenFile={onOpenFile} />
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Prompt Input Form */}
      <form className="ai-chat-input-area" onSubmit={handleSubmit}>
        <div className="input-container">
          <textarea
            ref={textareaRef}
            className="ai-chat-textarea"
            placeholder="Ask AI agent to inspect code, edit files, run tests... (Ctrl+Enter to send)"
            value={promptInput}
            onChange={(e) => setPromptInput(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={3}
            disabled={isAgentActive}
          />
          <div className="input-bottom-bar">
            <span className="input-hint">
              <kbd>Ctrl</kbd> + <kbd>Enter</kbd> to submit
            </span>
            {isAgentActive ? (
              <button
                type="button"
                className="ai-send-btn stop-mode"
                onClick={onStopAgent}
                title="Stop Agent"
              >
                <Square size={13} fill="currentColor" />
                <span>Stop</span>
              </button>
            ) : (
              <button
                type="submit"
                className="ai-send-btn"
                disabled={!promptInput.trim()}
                title="Send Prompt (Ctrl+Enter)"
              >
                <Send size={14} />
                <span>Ask Agent</span>
              </button>
            )}
          </div>
        </div>
      </form>
    </div>
  );
};
