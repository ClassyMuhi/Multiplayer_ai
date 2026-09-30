import React, { useState } from 'react';
import type { FileNode } from '../types';
import { FolderOpen, FileCode, FileText, Plus, Trash2, RefreshCw } from 'lucide-react';


interface FileExplorerProps {
  files: FileNode[];
  activePath: string | null;
  onSelectFile: (path: string) => void;
  onCreateFile: (path: string) => void;
  onDeleteFile: (path: string) => void;
  onRefresh: () => void;
}

export const FileExplorer: React.FC<FileExplorerProps> = ({
  files,
  activePath,
  onSelectFile,
  onCreateFile,
  onDeleteFile,
  onRefresh
}) => {
  const [newFilePath, setNewFilePath] = useState('');
  const [showAddInput, setShowAddInput] = useState(false);

  const handleAddSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (newFilePath.trim()) {
      onCreateFile(newFilePath.trim());
      setNewFilePath('');
      setShowAddInput(false);
    }
  };

  const renderTree = (nodes: FileNode[], depth = 0) => {
    return nodes.map((node) => {
      const isSelected = activePath === node.path;
      const isCode = node.name.endsWith('.py') || node.name.endsWith('.ts') || node.name.endsWith('.js') || node.name.endsWith('.json');

      if (node.is_directory) {
        return (
          <div key={node.path}>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                padding: '0.3rem 0.5rem',
                paddingLeft: `${depth * 0.75 + 0.5}rem`,
                color: 'var(--text-muted)',
                fontSize: '0.8rem',
                fontWeight: 600,
                userSelect: 'none'
              }}
            >
              <FolderOpen size={14} color="var(--accent-amber)" />
              <span>{node.name}</span>
            </div>
            {node.children && renderTree(node.children, depth + 1)}
          </div>
        );
      }

      return (
        <div
          key={node.path}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0.35rem 0.5rem',
            paddingLeft: `${depth * 0.75 + 0.5}rem`,
            backgroundColor: isSelected ? 'var(--bg-hover)' : 'transparent',
            borderLeft: isSelected ? '2px solid var(--accent-blue)' : '2px solid transparent',
            color: isSelected ? 'var(--accent-blue)' : 'var(--text-main)',
            fontSize: '0.825rem',
            cursor: 'pointer',
            borderRadius: '4px',
            margin: '1px 0'
          }}
          onClick={() => onSelectFile(node.path)}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', overflow: 'hidden' }}>
            {isCode ? <FileCode size={14} color="var(--accent-blue)" /> : <FileText size={14} color="var(--text-muted)" />}
            <span style={{ textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>
              {node.name}
            </span>
          </div>


          <button
            title="Delete File"
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-dim)',
              cursor: 'pointer',
              padding: '2px',
              display: 'flex'
            }}
            onClick={(e) => {
              e.stopPropagation();
              if (confirm(`Delete ${node.path}?`)) onDeleteFile(node.path);
            }}
          >
            <Trash2 size={12} />
          </button>
        </div>
      );
    });
  };

  return (
    <div style={{
      width: '240px',
      backgroundColor: 'var(--bg-panel)',
      borderRight: '1px solid var(--border-color)',
      display: 'flex',
      flexDirection: 'column',
      height: '100%'
    }}>
      {/* Explorer Header */}
      <div style={{
        padding: '0.6rem 0.8rem',
        borderBottom: '1px solid var(--border-color)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Explorer
        </span>
        <div style={{ display: 'flex', gap: '0.2rem' }}>
          <button
            className="btn btn-secondary"
            style={{ padding: '0.2rem 0.4rem' }}
            title="New File"
            onClick={() => setShowAddInput(!showAddInput)}
          >
            <Plus size={13} />
          </button>
          <button
            className="btn btn-secondary"
            style={{ padding: '0.2rem 0.4rem' }}
            title="Refresh Explorer"
            onClick={onRefresh}
          >
            <RefreshCw size={13} />
          </button>
        </div>
      </div>

      {/* Add New File Input */}
      {showAddInput && (
        <form onSubmit={handleAddSubmit} style={{ padding: '0.5rem', borderBottom: '1px solid var(--border-color)' }}>
          <input
            type="text"
            className="input"
            style={{ width: '100%', fontSize: '0.75rem' }}
            placeholder="filename.py or src/app.py"
            value={newFilePath}
            onChange={(e) => setNewFilePath(e.target.value)}
            autoFocus
          />
        </form>
      )}

      {/* Tree Content */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '0.4rem 0.25rem' }}>
        {files.length === 0 ? (
          <div style={{ padding: '1rem', fontSize: '0.8rem', color: 'var(--text-dim)', textAlign: 'center' }}>
            No files in workspace.
          </div>
        ) : (
          renderTree(files)
        )}
      </div>
    </div>
  );
};
