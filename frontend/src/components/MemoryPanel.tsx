import React, { useState } from 'react';
import type { ProjectMemory } from '../types';
import { Brain, Plus, Trash2, Tag } from 'lucide-react';


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
    <div style={{ padding: '0.8rem', backgroundColor: 'var(--bg-panel)', borderBottom: '1px solid var(--border-color)' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.6rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <Brain size={16} color="var(--accent-purple)" />
          <span style={{ fontWeight: 700, fontSize: '0.8rem', color: 'var(--text-main)' }}>
            Persistent Project Memory
          </span>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>({memories.length} notes)</span>
        </div>
        <button className="btn btn-secondary" style={{ padding: '0.15rem 0.4rem', fontSize: '0.75rem' }} onClick={() => setShowAdd(!showAdd)}>
          <Plus size={12} /> Add Memory
        </button>
      </div>

      {showAdd && (
        <form onSubmit={handleSubmit} style={{ backgroundColor: 'var(--bg-card)', padding: '0.6rem', borderRadius: '6px', marginBottom: '0.6rem', border: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', gap: '0.4rem', marginBottom: '0.4rem' }}>
            <input
              type="text"
              className="input"
              style={{ flex: 1, fontSize: '0.775rem' }}
              placeholder="Memory Key (e.g. Auth Architecture)"
              value={key}
              onChange={(e) => setKey(e.target.value)}
            />
            <select
              className="input"
              style={{ fontSize: '0.775rem' }}
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
            style={{ width: '100%', height: '50px', fontSize: '0.775rem', marginBottom: '0.4rem', resize: 'none' }}
            placeholder="Detailed instruction or decision note..."
            value={value}
            onChange={(e) => setValue(e.target.value)}
          />
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.4rem' }}>
            <button type="button" className="btn btn-secondary" style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }} onClick={() => setShowAdd(false)}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }}>
              Save Note
            </button>
          </div>
        </form>
      )}

      <div style={{ display: 'flex', gap: '0.5rem', overflowX: 'auto', paddingBottom: '0.2rem' }}>
        {memories.length === 0 ? (
          <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontStyle: 'italic' }}>
            No project memories stored yet. Agent will automatically persist key decisions here.
          </span>
        ) : (
          memories.map((m) => (
            <div
              key={m.id}
              style={{
                minWidth: '220px',
                maxWidth: '280px',
                backgroundColor: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: '6px',
                padding: '0.5rem',
                flexShrink: 0
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                <span style={{ fontSize: '0.725rem', fontWeight: 600, color: 'var(--accent-purple)' }}>
                  {m.key}
                </span>
                <button
                  style={{ background: 'none', border: 'none', color: 'var(--text-dim)', cursor: 'pointer' }}
                  onClick={() => onDeleteMemory(m.id)}
                  title="Delete Memory"
                >
                  <Trash2 size={11} />
                </button>
              </div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: '1.3' }}>
                {m.value}
              </p>
              <div style={{ marginTop: '0.3rem', fontSize: '0.65rem', color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
                <Tag size={9} /> {m.category}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
