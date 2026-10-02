import React, { useState, useRef, useEffect } from 'react';
import type { AgentStatusType, AppEvent, MessageRecord } from '../types';
import {
  Bot,
  Send,
  Pause,
  Play,
  Square,
  Terminal,
  Wrench,
  FileEdit,
  AlertCircle,
  Cpu,
  CheckCircle2,
  Sparkles,
  GitCommit,
  Tag
} from 'lucide-react';

export const AVAILABLE_MODELS = [
  { id: 'groq/openai/gpt-oss-120b', label: 'Groq: GPT-OSS 120B (Active)' },
  { id: 'groq/openai/gpt-oss-20b', label: 'Groq: GPT-OSS 20B' },
  { id: 'groq/qwen/qwen3.8-27b', label: 'Groq: Qwen 3.8 27B' },
  { id: 'gemini/gemini-2.0-flash', label: 'Gemini: 2.0 Flash' },
  { id: 'gemini/gemini-1.5-flash', label: 'Gemini: 1.5 Flash' },
  { id: 'gpt-4o', label: 'OpenAI: GPT-4o' },
  { id: 'autonomous', label: 'Summit Autonomous Engine' },
  { id: 'custom', label: 'Custom Model ID...' }
];

interface AgentPanelProps {
  status: AgentStatusType;
  events: AppEvent[];
  messages: MessageRecord[];
  onSendMessage: (msg: string, model?: string) => void;
  onStop: () => void;
  onPause: () => void;
  onResume: () => void;
}

export const AgentPanel: React.FC<AgentPanelProps> = ({
  status,
  events,
  messages,
  onSendMessage,
  onStop,
  onPause,
  onResume
}) => {
  const [prompt, setPrompt] = useState('');
  const [selectedModel, setSelectedModel] = useState<string>(() => {
    const saved = localStorage.getItem('summit_selected_model');
    if (saved && !saved.includes('llama') && saved !== 'groq/llama-3.3-70b-versatile') {
      return saved;
    }
    return 'groq/openai/gpt-oss-120b';
  });
  const [customModel, setCustomModel] = useState<string>(() => {
    return localStorage.getItem('summit_custom_model') || 'groq/openai/gpt-oss-120b';
  });
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [events, messages]);

  const handleModelChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    setSelectedModel(val);
    localStorage.setItem('summit_selected_model', val);
  };

  const handleCustomModelChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setCustomModel(val);
    localStorage.setItem('summit_custom_model', val);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (prompt.trim()) {
      const activeModel = selectedModel === 'custom' ? customModel.trim() : selectedModel;
      onSendMessage(prompt.trim(), activeModel);
      setPrompt('');
    }
  };

  const getStatusBadge = () => {
    switch (status) {
      case 'THINKING':
        return <span className="badge badge-thinking">Thinking</span>;
      case 'EXECUTING':
        return <span className="badge badge-executing">Executing</span>;
      case 'PAUSED':
        return <span className="badge badge-paused">Paused</span>;
      case 'COMPLETED':
        return <span className="badge badge-completed">Ready</span>;
      case 'ERROR':
        return <span className="badge badge-error">Error</span>;
      default:
        return <span className="badge badge-idle">Ready</span>;
    }
  };

  return (
    <div style={{
      width: '380px',
      minWidth: '320px',
      flexShrink: 0,
      backgroundColor: 'var(--vscode-bg-sidebar)',
      borderLeft: '1px solid var(--vscode-border)',
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      userSelect: 'none'
    }}>
      {/* Header & Controls */}
      <div style={{
        height: '35px',
        padding: '0 0.8rem',
        borderBottom: '1px solid var(--vscode-border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
          <Bot size={15} color="var(--vscode-accent)" />
          <span style={{ fontWeight: 600, fontSize: '12px', color: 'var(--vscode-text-white)' }}>
            AI Assistant
          </span>
          {getStatusBadge()}
        </div>

        <div style={{ display: 'flex', gap: '0.2rem' }}>
          {status === 'EXECUTING' || status === 'THINKING' ? (
            <button className="btn-icon" onClick={onPause} title="Pause Agent">
              <Pause size={12} />
            </button>
          ) : status === 'PAUSED' ? (
            <button className="btn-icon" onClick={onResume} title="Resume Agent">
              <Play size={12} />
            </button>
          ) : null}

          {(status === 'EXECUTING' || status === 'THINKING' || status === 'PAUSED') && (
            <button className="btn-icon" onClick={onStop} title="Stop Agent" style={{ color: 'var(--vscode-accent-red)' }}>
              <Square size={12} />
            </button>
          )}
        </div>
      </div>

      {/* Model Selector Bar */}
      <div style={{
        padding: '0.4rem 0.6rem',
        borderBottom: '1px solid var(--vscode-border)',
        backgroundColor: '#1e1e1e',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.3rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <Cpu size={12} color="var(--vscode-accent)" style={{ flexShrink: 0 }} />
          <select
            value={selectedModel}
            onChange={handleModelChange}
            style={{
              flex: 1,
              backgroundColor: 'var(--vscode-bg-input)',
              color: 'var(--vscode-text-primary)',
              border: '1px solid var(--vscode-border-light)',
              borderRadius: '2px',
              fontSize: '11px',
              padding: '0.2rem 0.4rem',
              outline: 'none',
              cursor: 'pointer'
            }}
            title="Active Model Provider"
          >
            {AVAILABLE_MODELS.map((m) => (
              <option key={m.id} value={m.id}>
                {m.label}
              </option>
            ))}
          </select>
        </div>

        {selectedModel === 'custom' && (
          <input
            type="text"
            className="input"
            style={{ fontSize: '11px', padding: '0.2rem 0.4rem' }}
            placeholder="e.g. groq/openai/gpt-oss-120b"
            value={customModel}
            onChange={handleCustomModelChange}
          />
        )}
      </div>

      {/* Messages & Events Stream */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '0.6rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.6rem',
        userSelect: 'text'
      }}>
        {/* Past Messages */}
        {messages.map((m) => (
          <div
            key={m.id}
            style={{
              padding: '0.55rem 0.7rem',
              borderRadius: '4px',
              backgroundColor: m.role === 'user' ? 'rgba(0, 122, 204, 0.1)' : '#1e1e1e',
              border: m.role === 'user' ? '1px solid rgba(0, 122, 204, 0.3)' : '1px solid var(--vscode-border)'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.2rem', fontSize: '11px', color: 'var(--vscode-text-muted)' }}>
              <span style={{ fontWeight: 600, color: m.role === 'user' ? 'var(--vscode-accent-blue)' : 'var(--vscode-accent-purple)' }}>
                {m.role === 'user' ? (m.user_name || 'Developer') : 'Summit Agent'}
              </span>
              <span>{new Date(m.timestamp).toLocaleTimeString()}</span>
            </div>
            <div style={{ fontSize: '12px', whiteSpace: 'pre-wrap', lineHeight: '1.4', color: 'var(--vscode-text-primary)' }}>
              {m.content}
            </div>
          </div>
        ))}

        {/* Live Events Stream */}
        {events.map((evt) => {
          if (evt.type === 'tool_call') {
            return (
              <div key={evt.id} style={{
                padding: '0.35rem 0.5rem',
                backgroundColor: '#1e1e1e',
                borderRadius: '3px',
                fontSize: '11px',
                borderLeft: '2px solid var(--vscode-accent-yellow)',
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem',
                color: 'var(--vscode-text-secondary)'
              }}>
                <Wrench size={12} color="var(--vscode-accent-yellow)" />
                <span>Tool: <b>{evt.data.tool}</b> {JSON.stringify(evt.data.args)}</span>
              </div>
            );
          }
          if (evt.type === 'file_changed' || evt.type === 'file_created') {
            return (
              <div key={evt.id} style={{
                padding: '0.35rem 0.5rem',
                backgroundColor: 'rgba(78, 201, 176, 0.1)',
                borderRadius: '3px',
                fontSize: '11px',
                borderLeft: '2px solid var(--vscode-accent-cyan)',
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem',
                color: 'var(--vscode-accent-cyan)'
              }}>
                <FileEdit size={12} />
                <span>File updated: <b>{evt.data.path}</b> (v{evt.data.version || 1})</span>
              </div>
            );
          }
          if (evt.type === 'terminal_output') {
            return (
              <div key={evt.id} style={{
                padding: '0.45rem',
                backgroundColor: '#121212',
                borderRadius: '3px',
                fontSize: '11px',
                fontFamily: 'var(--font-mono)',
                border: '1px solid var(--vscode-border)',
                color: evt.data.exit_code === 0 ? '#4ec9b0' : '#f14c4c'
              }}>
                <div style={{ color: 'var(--vscode-text-muted)', marginBottom: '0.2rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                  <Terminal size={11} /> $ {evt.data.command}
                </div>
                <pre style={{ whiteSpace: 'pre-wrap', margin: 0, maxHeight: '120px', overflowY: 'auto' }}>
                  {evt.data.output}
                </pre>
              </div>
            );
          }
          if (evt.type === 'memory_updated') {
            return (
              <div key={evt.id} style={{
                padding: '0.35rem 0.5rem',
                backgroundColor: 'rgba(197, 134, 192, 0.1)',
                borderRadius: '3px',
                fontSize: '11px',
                borderLeft: '2px solid var(--vscode-accent-purple)',
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem',
                color: 'var(--vscode-accent-purple)'
              }}>
                <Tag size={12} />
                <span>Memory saved: <b>{evt.data.key}</b></span>
              </div>
            );
          }
          if (evt.type === 'git_checkpoint') {
            return (
              <div key={evt.id} style={{
                padding: '0.35rem 0.5rem',
                backgroundColor: 'rgba(106, 153, 85, 0.1)',
                borderRadius: '3px',
                fontSize: '11px',
                borderLeft: '2px solid var(--vscode-accent-green)',
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem',
                color: 'var(--vscode-accent-green)'
              }}>
                <GitCommit size={12} />
                <span>Checkpoint: <b>{evt.data.message}</b></span>
              </div>
            );
          }
          if (evt.type === 'error') {
            return (
              <div key={evt.id} style={{
                padding: '0.35rem 0.5rem',
                backgroundColor: 'rgba(241, 76, 76, 0.15)',
                borderRadius: '3px',
                fontSize: '11px',
                borderLeft: '2px solid var(--vscode-accent-red)',
                color: 'var(--vscode-accent-red)',
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem'
              }}>
                <AlertCircle size={12} />
                <span>{evt.data.error}</span>
              </div>
            );
          }
          if (evt.type === 'user_joined' || evt.type === 'user_left') {
            return (
              <div key={evt.id} style={{ textAlign: 'center', fontSize: '10px', color: 'var(--vscode-text-muted)', fontStyle: 'italic', margin: '0.15rem 0' }}>
                {evt.data.display_name} {evt.type === 'user_joined' ? 'joined workspace' : 'left workspace'}
              </div>
            );
          }
          return null;
        })}
        <div ref={endRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} style={{
        padding: '0.5rem',
        borderTop: '1px solid var(--vscode-border)',
        display: 'flex',
        gap: '0.4rem',
        backgroundColor: '#1e1e1e'
      }}>
        <input
          type="text"
          className="input"
          style={{ flex: 1, fontSize: '12px' }}
          placeholder="Ask Summit to generate code, refactor, or run tests..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />
        <button
          type="submit"
          className="btn btn-primary"
          style={{ padding: '0.3rem 0.6rem' }}
          disabled={!prompt.trim() || status === 'EXECUTING' || status === 'THINKING'}
          title="Send Prompt (Enter)"
        >
          <Send size={13} />
        </button>
      </form>
    </div>
  );
};
