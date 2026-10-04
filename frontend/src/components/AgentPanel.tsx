import React, { useState, useRef, useEffect } from 'react';
import type { AgentStatusType, AppEvent, MessageRecord } from '../types';
import {
  Bot,
  User,
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

const USER_COLOR_PALETTES = [
  {
    id: 'user_a',
    bg: 'linear-gradient(135deg, rgba(37, 99, 235, 0.16) 0%, rgba(30, 58, 138, 0.18) 100%)',
    border: '1px solid rgba(96, 165, 250, 0.45)',
    headerColor: '#93c5fd',
    avatarBg: 'linear-gradient(135deg, #2563eb, #1d4ed8)',
    tagBg: 'rgba(37, 99, 235, 0.25)',
    tagColor: '#bfdbfe',
    defaultName: 'Alice (Dev A)'
  },
  {
    id: 'user_b',
    bg: 'linear-gradient(135deg, rgba(16, 185, 129, 0.16) 0%, rgba(6, 95, 70, 0.18) 100%)',
    border: '1px solid rgba(52, 211, 153, 0.45)',
    headerColor: '#6ee7b7',
    avatarBg: 'linear-gradient(135deg, #059669, #047857)',
    tagBg: 'rgba(16, 185, 129, 0.25)',
    tagColor: '#a7f3d0',
    defaultName: 'Bob (Dev B)'
  },
  {
    id: 'user_c',
    bg: 'linear-gradient(135deg, rgba(245, 158, 11, 0.16) 0%, rgba(146, 64, 14, 0.18) 100%)',
    border: '1px solid rgba(251, 191, 36, 0.45)',
    headerColor: '#fde68a',
    avatarBg: 'linear-gradient(135deg, #d97706, #b45309)',
    tagBg: 'rgba(245, 158, 11, 0.25)',
    tagColor: '#fef3c7',
    defaultName: 'Charlie (Dev C)'
  },
  {
    id: 'user_d',
    bg: 'linear-gradient(135deg, rgba(236, 72, 153, 0.16) 0%, rgba(157, 23, 77, 0.18) 100%)',
    border: '1px solid rgba(244, 114, 182, 0.45)',
    headerColor: '#fbcfe8',
    avatarBg: 'linear-gradient(135deg, #db2777, #be185d)',
    tagBg: 'rgba(236, 72, 153, 0.25)',
    tagColor: '#fce7f3',
    defaultName: 'Diana (Dev D)'
  },
  {
    id: 'user_e',
    bg: 'linear-gradient(135deg, rgba(6, 182, 212, 0.16) 0%, rgba(21, 94, 117, 0.18) 100%)',
    border: '1px solid rgba(34, 211, 238, 0.45)',
    headerColor: '#a5f3fc',
    avatarBg: 'linear-gradient(135deg, #0891b2, #0e7490)',
    tagBg: 'rgba(6, 182, 212, 0.25)',
    tagColor: '#cffafe',
    defaultName: 'Evan (Dev E)'
  }
];

const AI_THEME = {
  bg: 'linear-gradient(135deg, rgba(24, 24, 27, 0.95) 0%, rgba(30, 27, 46, 0.8) 100%)',
  border: '1px solid rgba(168, 85, 247, 0.4)',
  headerColor: '#d8b4fe',
  avatarBg: 'linear-gradient(135deg, #9333ea, #7e22ce)',
  tagBg: 'rgba(168, 85, 247, 0.25)',
  tagColor: '#e9d5ff'
};

function getUserTheme(userId?: string, userName?: string) {
  const str = (userId || userName || 'user_a').toLowerCase();
  if (str.includes('user_a') || str.includes('alice')) return USER_COLOR_PALETTES[0];
  if (str.includes('user_b') || str.includes('bob')) return USER_COLOR_PALETTES[1];
  if (str.includes('user_c') || str.includes('charlie')) return USER_COLOR_PALETTES[2];
  if (str.includes('user_d') || str.includes('diana')) return USER_COLOR_PALETTES[3];

  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  const idx = Math.abs(hash) % USER_COLOR_PALETTES.length;
  return USER_COLOR_PALETTES[idx];
}

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
        padding: '0.45rem 0.65rem',
        borderBottom: '1px solid var(--vscode-border)',
        background: 'linear-gradient(180deg, rgba(30, 58, 138, 0.15) 0%, rgba(18, 18, 21, 0.95) 100%)',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.35rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
          <Cpu size={14} color="#60a5fa" style={{ flexShrink: 0 }} />
          <select
            value={selectedModel}
            onChange={handleModelChange}
            style={{
              flex: 1,
              background: 'linear-gradient(135deg, rgba(37, 99, 235, 0.22) 0%, rgba(30, 58, 138, 0.3) 100%)',
              color: '#e0f2fe',
              border: '1px solid rgba(96, 165, 250, 0.45)',
              borderRadius: '6px',
              fontSize: '11px',
              fontWeight: 500,
              padding: '0.28rem 0.5rem',
              outline: 'none',
              cursor: 'pointer',
              boxShadow: '0 1px 4px rgba(37, 99, 235, 0.2)',
              transition: 'all 0.15s ease'
            }}
            title="Choose Active AI Model"
          >
            {AVAILABLE_MODELS.map((m) => (
              <option key={m.id} value={m.id} style={{ backgroundColor: '#18181b', color: '#f4f4f5' }}>
                {m.label}
              </option>
            ))}
          </select>
        </div>

        {selectedModel === 'custom' && (
          <input
            type="text"
            className="input"
            style={{
              fontSize: '11px',
              padding: '0.25rem 0.5rem',
              backgroundColor: 'rgba(37, 99, 235, 0.1)',
              border: '1px solid rgba(96, 165, 250, 0.4)',
              color: '#e0f2fe',
              borderRadius: '6px'
            }}
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
        {/* Past Messages with Contrasting User-Specific Themes */}
        {messages.map((m) => {
          const isAI = m.role !== 'user';
          const theme = isAI ? AI_THEME : getUserTheme(m.user_id, m.user_name);
          const displayName = isAI ? 'Summit Agent' : (m.user_name || 'Developer');
          const initial = displayName.charAt(0).toUpperCase();

          return (
            <div
              key={m.id}
              style={{
                padding: '0.65rem 0.8rem',
                borderRadius: '8px',
                background: theme.bg,
                border: theme.border,
                boxShadow: '0 2px 8px rgba(0, 0, 0, 0.35)',
                transition: 'transform 0.15s ease'
              }}
            >
              {/* Header: User Avatar, Name, Role Tag, Time */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
                  {/* Avatar Circle */}
                  <div style={{
                    width: '20px',
                    height: '20px',
                    borderRadius: '50%',
                    background: theme.avatarBg,
                    color: '#ffffff',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '10px',
                    fontWeight: 700,
                    boxShadow: '0 1px 4px rgba(0,0,0,0.3)',
                    flexShrink: 0
                  }}>
                    {isAI ? <Bot size={12} /> : initial}
                  </div>

                  {/* Display Name */}
                  <span style={{ fontWeight: 600, fontSize: '12px', color: theme.headerColor }}>
                    {displayName}
                  </span>

                  {/* Role / User Tag Badge */}
                  <span style={{
                    fontSize: '9px',
                    fontWeight: 600,
                    padding: '1px 5px',
                    borderRadius: '4px',
                    backgroundColor: theme.tagBg,
                    color: theme.tagColor,
                    textTransform: 'uppercase',
                    letterSpacing: '0.04em'
                  }}>
                    {isAI ? 'AI' : (theme as any).tag || 'User'}
                  </span>
                </div>

                <span style={{ fontSize: '10px', color: 'var(--vscode-text-muted)' }}>
                  {new Date(m.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>

              {/* Message Body Content */}
              <div style={{
                fontSize: '12px',
                whiteSpace: 'pre-wrap',
                lineHeight: '1.45',
                color: '#f4f4f5',
                paddingLeft: '2px'
              }}>
                {m.content}
              </div>
            </div>
          );
        })}

        {/* Live Events Stream */}
        {events.map((evt) => {
          if (evt.type === 'tool_call') {
            return (
              <div key={evt.id} style={{
                padding: '0.35rem 0.5rem',
                backgroundColor: '#18181b',
                borderRadius: '4px',
                fontSize: '11px',
                borderLeft: '2px solid #a1a1aa',
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem',
                color: 'var(--vscode-text-secondary)'
              }}>
                <Wrench size={12} color="#a1a1aa" />
                <span>Tool: <b>{evt.data.tool}</b> {JSON.stringify(evt.data.args)}</span>
              </div>
            );
          }
          if (evt.type === 'file_changed' || evt.type === 'file_created') {
            return (
              <div key={evt.id} style={{
                padding: '0.35rem 0.5rem',
                backgroundColor: '#18181b',
                borderRadius: '4px',
                fontSize: '11px',
                borderLeft: '2px solid #d4d4d8',
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem',
                color: 'var(--vscode-text-primary)'
              }}>
                <FileEdit size={12} color="#d4d4d8" />
                <span>File updated: <b>{evt.data.path}</b> (v{evt.data.version || 1})</span>
              </div>
            );
          }
          if (evt.type === 'terminal_output') {
            return (
              <div key={evt.id} style={{
                padding: '0.45rem',
                backgroundColor: '#09090b',
                borderRadius: '4px',
                fontSize: '11px',
                fontFamily: 'var(--font-mono)',
                border: '1px solid var(--vscode-border)',
                color: evt.data.exit_code === 0 ? '#e4e4e7' : '#a1a1aa'
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
                backgroundColor: '#18181b',
                borderRadius: '4px',
                fontSize: '11px',
                borderLeft: '2px solid #71717a',
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem',
                color: 'var(--vscode-text-secondary)'
              }}>
                <Tag size={12} color="#71717a" />
                <span>Memory saved: <b>{evt.data.key}</b></span>
              </div>
            );
          }
          if (evt.type === 'git_checkpoint') {
            return (
              <div key={evt.id} style={{
                padding: '0.35rem 0.5rem',
                backgroundColor: '#18181b',
                borderRadius: '4px',
                fontSize: '11px',
                borderLeft: '2px solid #a1a1aa',
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem',
                color: 'var(--vscode-text-secondary)'
              }}>
                <GitCommit size={12} color="#a1a1aa" />
                <span>Checkpoint: <b>{evt.data.message}</b></span>
              </div>
            );
          }
          if (evt.type === 'error') {
            return (
              <div key={evt.id} style={{
                padding: '0.35rem 0.5rem',
                backgroundColor: '#18181b',
                borderRadius: '4px',
                fontSize: '11px',
                borderLeft: '2px solid #71717a',
                color: 'var(--vscode-text-primary)',
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem'
              }}>
                <AlertCircle size={12} color="#a1a1aa" />
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
        backgroundColor: '#121215'
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
