import React, { useState } from 'react';
import {
  Folder,
  FolderOpen,
  FileCode,
  FileText,
  FileJson,
  FileCog,
  FileSpreadsheet,
  ChevronRight,
  ChevronDown
} from 'lucide-react';
import { FileNode } from '../../types';

interface FileTreeNodeProps {
  node: FileNode;
  activeFilePath: string | null;
  onSelectFile: (filePath: string) => void;
  depth?: number;
}

export const FileTreeNode: React.FC<FileTreeNodeProps> = ({
  node,
  activeFilePath,
  onSelectFile,
  depth = 0
}) => {
  const [isOpen, setIsOpen] = useState(true);

  const isDirectory = node.is_directory;
  const isSelected = !isDirectory && activeFilePath === node.path;

  const getFileIcon = (fileName: string) => {
    const ext = fileName.split('.').pop()?.toLowerCase();
    switch (ext) {
      case 'py':
        return <FileCode size={14} color="#38bdf8" />;
      case 'ts':
      case 'tsx':
        return <FileCode size={14} color="#3b82f6" />;
      case 'js':
      case 'jsx':
        return <FileCode size={14} color="#facc15" />;
      case 'json':
        return <FileJson size={14} color="#fb923c" />;
      case 'md':
      case 'txt':
        return <FileText size={14} color="#94a3b8" />;
      case 'ini':
      case 'env':
      case 'toml':
        return <FileCog size={14} color="#a855f7" />;
      default:
        return <FileText size={14} color="#64748b" />;
    }
  };

  const handleClick = () => {
    if (isDirectory) {
      setIsOpen(!isOpen);
    } else {
      onSelectFile(node.path);
    }
  };

  return (
    <div>
      <div
        onClick={handleClick}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          padding: '4px 8px',
          paddingLeft: `${depth * 14 + 10}px`,
          cursor: 'pointer',
          borderRadius: '3px',
          backgroundColor: isSelected ? 'rgba(99, 102, 241, 0.15)' : 'transparent',
          color: isSelected ? 'var(--text-primary)' : 'var(--text-secondary)',
          borderLeft: isSelected ? '2px solid var(--accent-primary)' : '2px solid transparent',
          userSelect: 'none',
          fontSize: '12px',
          transition: 'background-color 0.1s ease'
        }}
        onMouseEnter={(e) => {
          if (!isSelected) e.currentTarget.style.backgroundColor = 'var(--bg-tab-hover)';
        }}
        onMouseLeave={(e) => {
          if (!isSelected) e.currentTarget.style.backgroundColor = 'transparent';
        }}
      >
        {/* Expand / Collapse Icon for Directories */}
        {isDirectory ? (
          <>
            <span style={{ color: 'var(--text-muted)', display: 'flex' }}>
              {isOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
            </span>
            <span style={{ color: '#eab308', display: 'flex' }}>
              {isOpen ? <FolderOpen size={14} /> : <Folder size={14} />}
            </span>
          </>
        ) : (
          <>
            <span style={{ width: '14px' }} />
            <span style={{ display: 'flex' }}>{getFileIcon(node.name)}</span>
          </>
        )}

        <span
          className="font-mono"
          style={{
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
            fontWeight: isSelected ? 500 : 400
          }}
        >
          {node.name}
        </span>
      </div>

      {/* Children */}
      {isDirectory && isOpen && node.children && (
        <div>
          {node.children.map((child) => (
            <FileTreeNode
              key={child.path}
              node={child}
              activeFilePath={activeFilePath}
              onSelectFile={onSelectFile}
              depth={depth + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
};
