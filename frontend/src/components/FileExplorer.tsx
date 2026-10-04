import React, { useState } from 'react';
import type { FileNode } from '../types';
import {
  FolderOpen,
  FileCode,
  FileText,
  FileJson,
  FileCheck,
  Plus,
  Trash2,
  RefreshCw,
  ChevronDown,
  ChevronRight
} from 'lucide-react';

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
  const [isSectionOpen, setIsSectionOpen] = useState(true);

  const handleAddSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (newFilePath.trim()) {
      onCreateFile(newFilePath.trim());
      setNewFilePath('');
      setShowAddInput(false);
    }
  };

  const getFileIcon = (name: string) => {
    if (name.endsWith('.py')) return <FileCode size={14} color="#38bdf8" />;
    if (name.endsWith('.ts') || name.endsWith('.tsx')) return <FileCode size={14} color="#3178c6" />;
    if (name.endsWith('.js') || name.endsWith('.jsx')) return <FileCode size={14} color="#facc15" />;
    if (name.endsWith('.html')) return <FileCode size={14} color="#f97316" />;
    if (name.endsWith('.css')) return <FileCode size={14} color="#38bdf8" />;
    if (name.endsWith('.json')) return <FileJson size={14} color="#fbbf24" />;
    if (name.endsWith('.md')) return <FileText size={14} color="#60a5fa" />;
    if (name.endsWith('.ini') || name.endsWith('.env')) return <FileCheck size={14} color="#a855f7" />;
    return <FileText size={14} color="#94a3b8" />;
  };

  const renderTree = (nodes: FileNode[], depth = 0) => {
    return nodes.map((node) => {
      const isSelected = activePath === node.path;

      if (node.is_directory) {
        return (
          <div key={node.path}>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem',
                padding: '0.25rem 0.5rem',
                paddingLeft: `${depth * 0.75 + 0.5}rem`,
                color: 'var(--vscode-text-secondary)',
                fontSize: '12px',
                fontWeight: 500,
                userSelect: 'none',
                cursor: 'pointer'
              }}
            >
              <FolderOpen size={13} color="#f59e0b" />
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
            padding: '0.28rem 0.5rem',
            paddingLeft: `${depth * 0.75 + 0.6}rem`,
            backgroundColor: isSelected ? 'rgba(255, 255, 255, 0.08)' : 'transparent',
            borderLeft: isSelected ? '2px solid #f4f4f5' : '2px solid transparent',
            color: isSelected ? '#ffffff' : 'var(--vscode-text-primary)',
            fontSize: '12px',
            cursor: 'pointer',
            transition: 'background-color 0.1s ease'
          }}
          onMouseEnter={(e) => {
            if (!isSelected) e.currentTarget.style.backgroundColor = 'var(--vscode-bg-card-hover)';
          }}
          onMouseLeave={(e) => {
            if (!isSelected) e.currentTarget.style.backgroundColor = 'transparent';
          }}
          onClick={() => onSelectFile(node.path)}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', overflow: 'hidden' }}>
            {getFileIcon(node.name)}
            <span style={{ textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>
              {node.name}
            </span>
          </div>

          <button
            title="Delete File"
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--vscode-text-muted)',
              cursor: 'pointer',
              padding: '2px',
              display: 'flex',
              opacity: isSelected ? 1 : 0.6
            }}
            onClick={(e) => {
              e.stopPropagation();
              if (confirm(`Delete ${node.path}?`)) onDeleteFile(node.path);
            }}
            onMouseEnter={(e) => e.currentTarget.style.color = 'var(--vscode-accent-red)'}
            onMouseLeave={(e) => e.currentTarget.style.color = 'var(--vscode-text-muted)'}
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
      minWidth: '220px',
      flexShrink: 0,
      backgroundColor: 'var(--vscode-bg-sidebar)',
      borderRight: '1px solid var(--vscode-border)',
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      userSelect: 'none'
    }}>
      {/* Explorer Sidebar Header */}
      <div style={{
        padding: '0.5rem 0.75rem',
        borderBottom: '1px solid var(--vscode-border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: '35px'
      }}>
        <div
          onClick={() => setIsSectionOpen(!isSectionOpen)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.3rem',
            cursor: 'pointer',
            fontSize: '11px',
            fontWeight: 700,
            color: 'var(--vscode-text-secondary)',
            textTransform: 'uppercase',
            letterSpacing: '0.04em'
          }}
        >
          {isSectionOpen ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
          <span>Explorer</span>
        </div>

        <div style={{ display: 'flex', gap: '0.2rem' }}>
          <button
            className="btn-icon"
            style={{ padding: '2px 4px' }}
            title="New File"
            onClick={() => setShowAddInput(!showAddInput)}
          >
            <Plus size={13} />
          </button>
          <button
            className="btn-icon"
            style={{ padding: '2px 4px' }}
            title="Refresh Files"
            onClick={onRefresh}
          >
            <RefreshCw size={12} />
          </button>
        </div>
      </div>

      {/* Add New File Input */}
      {showAddInput && (
        <form onSubmit={handleAddSubmit} style={{ padding: '0.4rem 0.5rem', borderBottom: '1px solid var(--vscode-border)', backgroundColor: '#1e1e1e' }}>
          <input
            type="text"
            className="input"
            style={{ width: '100%', fontSize: '11px', padding: '0.25rem 0.4rem' }}
            placeholder="filename.py, app.js, index.html"
            value={newFilePath}
            onChange={(e) => setNewFilePath(e.target.value)}
            autoFocus
          />
        </form>
      )}

      {/* Tree Content */}
      {isSectionOpen && (
        <div style={{ flex: 1, overflowY: 'auto', padding: '0.2rem 0' }}>
          {files.length === 0 ? (
            <div style={{ padding: '1rem', fontSize: '11px', color: 'var(--vscode-text-muted)', textAlign: 'center' }}>
              No files in workspace.
            </div>
          ) : (
            renderTree(files)
          )}
        </div>
      )}
    </div>
  );
};
