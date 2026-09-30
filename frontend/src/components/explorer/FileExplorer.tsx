import React, { useState } from 'react';
import { RefreshCw, FolderTree, FilePlus, Plus, X } from 'lucide-react';
import { FileNode } from '../../types';
import { FileTreeNode } from './FileTreeNode';

interface FileExplorerProps {
  fileTree: FileNode[];
  activeFilePath: string | null;
  isLoading: boolean;
  onSelectFile: (filePath: string) => void;
  onRefreshTree: () => void;
  onCreateFile?: (filePath: string) => void;
  onDeleteFile?: (filePath: string) => void;
}

export const FileExplorer: React.FC<FileExplorerProps> = ({
  fileTree,
  activeFilePath,
  isLoading,
  onSelectFile,
  onRefreshTree,
  onCreateFile,
  onDeleteFile,
}) => {
  const [isCreatingFile, setIsCreatingFile] = useState(false);
  const [newFilePath, setNewFilePath] = useState('');

  const handleCreateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newFilePath.trim() || !onCreateFile) return;
    onCreateFile(newFilePath.trim());
    setNewFilePath('');
    setIsCreatingFile(false);
  };

  return (
    <div className="file-explorer-container">
      {/* Header */}
      <div className="file-explorer-header">
        <span className="file-explorer-title">
          <FolderTree size={14} color="var(--accent-primary)" />
          <span>Explorer</span>
        </span>

        <div className="file-explorer-actions">
          {onCreateFile && (
            <button
              onClick={() => setIsCreatingFile(true)}
              title="New File..."
              className="btn-icon-subtle"
            >
              <FilePlus size={13} />
            </button>
          )}

          <button
            onClick={onRefreshTree}
            title="Refresh File Explorer"
            className="btn-icon-subtle"
          >
            <RefreshCw size={13} className={isLoading ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {/* New File Input Row */}
      {isCreatingFile && (
        <form onSubmit={handleCreateSubmit} className="new-file-inline-form">
          <input
            type="text"
            className="new-file-input"
            placeholder="filename.py or path/file.ts"
            value={newFilePath}
            onChange={(e) => setNewFilePath(e.target.value)}
            autoFocus
          />
          <button type="submit" className="btn-icon-subtle" title="Create">
            <Plus size={12} />
          </button>
          <button
            type="button"
            className="btn-icon-subtle"
            onClick={() => setIsCreatingFile(false)}
            title="Cancel"
          >
            <X size={12} />
          </button>
        </form>
      )}

      {/* File Tree */}
      <div className="file-explorer-tree-view">
        {isLoading && fileTree.length === 0 ? (
          <div className="file-explorer-loading">
            <RefreshCw size={14} className="animate-spin" />
            <span>Loading workspace files...</span>
          </div>
        ) : fileTree.length === 0 ? (
          <div className="file-explorer-empty">
            <span>Workspace is empty</span>
          </div>
        ) : (
          fileTree.map((node) => (
            <FileTreeNode
              key={node.path}
              node={node}
              activeFilePath={activeFilePath}
              onSelectFile={onSelectFile}
            />
          ))
        )}
      </div>
    </div>
  );
};
