import React, { useState, useRef, useEffect } from 'react';
import type { AgentStatusType, AppEvent, MessageRecord } from '../types';
import { Bot, Send, Pause, Play, Square, Terminal, Wrench, FileEdit, AlertCircle, Cpu } from 'lucide-react';

export const AVAILABLE_MODELS = [
  { id: 'groq/openai/gpt-oss-120b', label: '⚡ Groq: GPT-OSS 120B (Active on your account)' },
  { id: 'groq/openai/gpt-oss-20b', label: '⚡ Groq: GPT-OSS 20B (Fast)' },
  { id: 'groq/qwen/qwen3.8-27b', label: '⚡ Groq: Qwen 3.8 27B' },
  { id: 'gemini/gemini-2.0-flash', label: '🌟 Gemini: 2.0 Flash' },
  { id: 'gemini/gemini-1.5-flash', label: '🌟 Gemini: 1.5 Flash' },
  { id: 'gpt-4o', label: '🧠 OpenAI: GPT-4o' },
  { id: 'autonomous', label: '🤖 Built-in Autonomous Engine' },
  { id: 'custom', label: '⚙️ Custom Model ID...' }
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
        return <span className="badge badge-thinking">● THINKING</span>;
      case 'EXECUTING':
        return <span className="badge badge-executing">● EXECUTING</span>;
      case 'PAUSED':
        return <span className="badge badge-paused">❚❚ PAUSED</span>;
      case 'COMPLETED':
        return <span className="badge badge-completed">✓ COMPLETED</span>;
      case 'ERROR':
        return <span className="badge badge-error">⚠ ERROR</span>;
      default:
        return <span className="badge badge-idle">● IDLE</span>;
    }
  };

  return (
    <div style={{
      width: '380px',
      minWidth: '320px',
      flexShrink: 0,
      backgroundColor: 'var(--bg-panel)',
      borderLeft: '1px solid var(--border-color)',
      display: 'flex',
      flexDirection: 'column',
      height: '100%'
    }}>
      {/* Header & Controls */}
      <div style={{
        padding: '0.6rem 0.8rem',
        borderBottom: '1px solid var(--border-color)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Bot size={18} color="var(--accent-blue)" />
          <span style={{ fontWeight: 700, fontSize: '0.85rem' }}>Shared AI Agent</span>
          {getStatusBadge()}
        </div>

        <div style={{ display: 'flex', gap: '0.3rem' }}>
          {status === 'EXECUTING' || status === 'THINKING' ? (
            <button className="btn btn-secondary" style={{ padding: '0.2rem 0.4rem' }} onClick={onPause} title="Pause Agent">
              <Pause size={12} />
            </button>
          ) : status === 'PAUSED' ? (
            <button className="btn btn-secondary" style={{ padding: '0.2rem 0.4rem' }} onClick={onResume} title="Resume Agent">
              <Play size={12} />
            </button>
          ) : null}

          {(status === 'EXECUTING' || status === 'THINKING' || status === 'PAUSED') && (
            <button className="btn btn-danger" style={{ padding: '0.2rem 0.4rem' }} onClick={onStop} title="Stop Agent">
              <Square size={12} />
            </button>
          )}
        </div>
      </div>

      {/* Model Selector Bar */}
      <div style={{
        padding: '0.45rem 0.8rem',
        borderBottom: '1px solid var(--border-color)',
        backgroundColor: 'rgba(15, 23, 42, 0.4)',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.35rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
          <Cpu size={13} color="var(--accent-blue)" style={{ flexShrink: 0 }} />
          <select
            value={selectedModel}
            onChange={handleModelChange}
            style={{
              flex: 1,
              backgroundColor: 'var(--bg-card)',
              color: 'var(--text-main)',
              border: '1px solid var(--border-color)',
              borderRadius: '5px',
              fontSize: '0.75rem',
              padding: '0.25rem 0.4rem',
              outline: 'none',
              cursor: 'pointer'
            }}
            title="Choose AI Model Provider"
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
            style={{ fontSize: '0.725rem', padding: '0.2rem 0.4rem' }}
            placeholder="e.g. groq/openai/gpt-oss-120b"
            value={customModel}
            onChange={handleCustomModelChange}
          />
        )}
      </div>

      {/* Stream & History */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '0.8rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {/* Past Messages */}
        {messages.map((m) => (
          <div
            key={m.id}
            style={{
              padding: '0.6rem 0.75rem',
              borderRadius: '8px',
              backgroundColor: m.role === 'user' ? 'rgba(56, 189, 248, 0.08)' : 'var(--bg-card)',
              border: m.role === 'user' ? '1px solid rgba(56, 189, 248, 0.2)' : '1px solid var(--border-color)'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem', fontSize: '0.725rem', color: 'var(--text-muted)' }}>
              <span style={{ fontWeight: 600, color: m.role === 'user' ? 'var(--accent-blue)' : 'var(--accent-purple)' }}>
                {m.role === 'user' ? (m.user_name || 'User') : 'Summit AI'}
              </span>
              <span>{new Date(m.timestamp).toLocaleTimeString()}</span>
            </div>
            <div style={{ fontSize: '0.825rem', whiteSpace: 'pre-wrap', lineHeight: '1.4' }}>
              {m.content}
            </div>
          </div>
        ))}

        {/* Real-Time Live Events Stream */}
        {events.map((evt) => {
          if (evt.type === 'tool_call') {
            return (
              <div key={evt.id} style={{ padding: '0.4rem 0.6rem', backgroundColor: 'var(--bg-card)', borderRadius: '6px', fontSize: '0.775rem', borderLeft: '3px solid var(--accent-amber)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <Wrench size={13} color="var(--accent-amber)" />
                <span>Tool: <b>{evt.data.tool}</b> {JSON.stringify(evt.data.args)}</span>
              </div>
            );
          }
          if (evt.type === 'file_changed' || evt.type === 'file_created') {
            return (
              <div key={evt.id} style={{ padding: '0.4rem 0.6rem', backgroundColor: 'rgba(52, 211, 153, 0.08)', borderRadius: '6px', fontSize: '0.775rem', borderLeft: '3px solid var(--accent-green)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <FileEdit size={13} color="var(--accent-green)" />
                <span>File updated: <b>{evt.data.path}</b> (v{evt.data.version || 1})</span>
              </div>
            );
          }
          if (evt.type === 'terminal_output') {
            return (
              <div key={evt.id} style={{ padding: '0.5rem', backgroundColor: '#000', borderRadius: '6px', fontSize: '0.725rem', fontFamily: 'var(--font-mono)', border: '1px solid var(--border-color)', color: evt.data.exit_code === 0 ? '#4ade80' : '#f87171' }}>
                <div style={{ color: 'var(--text-muted)', marginBottom: '0.2rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                  <Terminal size={11} /> $ {evt.data.command}
                </div>
                <pre style={{ whiteSpace: 'pre-wrap', margin: 0, maxHeight: '120px', overflowY: 'auto' }}>
                  {evt.data.output}
                </pre>
              </div>
            );
          }
          if (evt.type === 'error') {
            return (
              <div key={evt.id} style={{ padding: '0.4rem 0.6rem', backgroundColor: 'rgba(248, 113, 113, 0.1)', borderRadius: '6px', fontSize: '0.775rem', borderLeft: '3px solid var(--accent-red)', color: 'var(--accent-red)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <AlertCircle size={13} />
                <span>{evt.data.error}</span>
              </div>
            );
          }
          if (evt.type === 'user_joined' || evt.type === 'user_left') {
            return (
              <div key={evt.id} style={{ textAlign: 'center', fontSize: '0.725rem', color: 'var(--text-dim)', fontStyle: 'italic', margin: '0.2rem 0' }}>
                ● {evt.data.display_name} {evt.type === 'user_joined' ? 'joined' : 'left'} the project room
              </div>
            );
          }
          return null;
        })}
        <div ref={endRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} style={{ padding: '0.75rem', borderTop: '1px solid var(--border-color)', display: 'flex', gap: '0.5rem' }}>
        <input
          type="text"
          className="input"
          style={{ flex: 1 }}
          placeholder="Ask Summit to code, write tests, refactor..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />
        <button type="submit" className="btn btn-primary" disabled={!prompt.trim() || status === 'EXECUTING' || status === 'THINKING'}>
          <Send size={14} />
        </button>
      </form>
    </div>
  );
};
