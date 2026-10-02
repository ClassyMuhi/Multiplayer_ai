import React, { useState } from 'react';
import type { ProjectMemory } from '../types';
import { Brain, Plus, Trash2, Tag, ChevronDown, ChevronRight } from 'lucide-react';

interface MemoryPanelProps {
  memories: ProjectMemory[];
  onCreateMemory: (key: string, value: string, category: string) => void;
  onDeleteMemory: (keyOrId: string) => void;
}

export const MemoryPanel: React.FC<MemoryPanelProps> = ({
  memories,
  onCreateMemory,
  onDeleteMemory
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [showAdd, setShowAdd] = useState(false);
  const [key, setKey] = useState('');
  const [value, setValue] = useState('');
  const [category, setCategory] = useState('decision');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (key.trim() && value.trim()) {
      onCreateMemory(key.trim(), value.trim(), category);
      setKey('');
      setValue('');
      setShowAdd(false);
    }
  };

  return (
    <div style={{
      backgroundColor: 'var(--vscode-bg-sidebar)',
      borderBottom: '1px solid var(--vscode-border)',
      userSelect: 'none'
    }}>
      {/* Header Bar */}
      <div style={{
        padding: '0.35rem 0.75rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        cursor: 'pointer'
      }} onClick={() => setIsOpen(!isOpen)}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          {isOpen ? <ChevronDown size={12} color="var(--vscode-text-muted)" /> : <ChevronRight size={12} color="var(--vscode-text-muted)" />}
          <Brain size={13} color="var(--vscode-accent-purple)" />
          <span style={{ fontWeight: 600, fontSize: '11px', color: 'var(--vscode-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Project Memories
          </span>
          <span style={{ fontSize: '10px', color: 'var(--vscode-text-muted)' }}>({memories.length})</span>
        </div>

        <button
          className="btn-icon"
          style={{ padding: '2px 4px', fontSize: '11px', gap: '3px' }}
          onClick={(e) => {
            e.stopPropagation();
            setIsOpen(true);
            setShowAdd(!showAdd);
          }}
          title="Add Memory Note"
        >
          <Plus size={12} />
        </button>
      </div>

      {isOpen && (
        <div style={{ padding: '0.5rem 0.75rem', borderTop: '1px solid var(--vscode-border)', backgroundColor: '#1e1e1e' }}>
          {showAdd && (
            <form onSubmit={handleSubmit} style={{ backgroundColor: 'var(--vscode-bg-sidebar)', padding: '0.5rem', borderRadius: '3px', marginBottom: '0.5rem', border: '1px solid var(--vscode-border)' }}>
              <div style={{ display: 'flex', gap: '0.3rem', marginBottom: '0.3rem' }}>
                <input
                  type="text"
                  className="input"
                  style={{ flex: 1, fontSize: '11px', padding: '0.2rem 0.4rem' }}
                  placeholder="Memory Key (e.g. Auth Architecture)"
                  value={key}
                  onChange={(e) => setKey(e.target.value)}
                />
                <select
                  className="input"
                  style={{ fontSize: '11px', padding: '0.2rem 0.4rem' }}
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                >
                  <option value="decision">Decision</option>
                  <option value="architecture">Architecture</option>
                  <option value="convention">Convention</option>
                  <option value="task">Task</option>
                  <option value="general">General</option>
                </select>
              </div>
              <textarea
                className="input"
                style={{ width: '100%', height: '45px', fontSize: '11px', marginBottom: '0.3rem', resize: 'none', padding: '0.25rem 0.4rem' }}
                placeholder="Memory details..."
                value={value}
                onChange={(e) => setValue(e.target.value)}
              />
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.3rem' }}>
                <button type="button" className="btn btn-secondary" style={{ padding: '0.15rem 0.45rem', fontSize: '11px' }} onClick={() => setShowAdd(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" style={{ padding: '0.15rem 0.45rem', fontSize: '11px' }}>
                  Save
                </button>
              </div>
            </form>
          )}

          <div style={{ display: 'flex', gap: '0.4rem', overflowX: 'auto', paddingBottom: '0.2rem' }}>
            {memories.length === 0 ? (
              <span style={{ fontSize: '11px', color: 'var(--vscode-text-muted)' }}>
                No memories recorded yet. The agent automatically persists key decisions.
              </span>
            ) : (
              memories.map((m) => (
                <div
                  key={m.id}
                  style={{
                    minWidth: '200px',
                    maxWidth: '260px',
                    backgroundColor: 'var(--vscode-bg-sidebar)',
                    border: '1px solid var(--vscode-border)',
                    borderRadius: '3px',
                    padding: '0.45rem',
                    flexShrink: 0
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.2rem' }}>
                    <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--vscode-accent-purple)' }}>
                      {m.key}
                    </span>
                    <button
                      style={{ background: 'none', border: 'none', color: 'var(--vscode-text-muted)', cursor: 'pointer', padding: 0 }}
                      onClick={() => onDeleteMemory(m.id)}
                      title="Delete Memory"
                    >
                      <Trash2 size={10} />
                    </button>
                  </div>
                  <p style={{ fontSize: '11px', color: 'var(--vscode-text-secondary)', lineHeight: '1.3' }}>
                    {m.value}
                  </p>
                  <div style={{ marginTop: '0.25rem', fontSize: '10px', color: 'var(--vscode-text-muted)', display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
                    <Tag size={9} /> {m.category}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};
