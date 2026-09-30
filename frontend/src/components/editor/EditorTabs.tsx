import React from 'react';
import { X, FileCode, Circle } from 'lucide-react';
import { OpenFile } from '../../types';

interface EditorTabsProps {
  openFiles: OpenFile[];
  activeFilePath: string | null;
  onSelectTab: (path: string) => void;
  onCloseTab: (path: string, e: React.MouseEvent) => void;
}

export const EditorTabs: React.FC<EditorTabsProps> = ({
  openFiles,
  activeFilePath,
  onSelectTab,
  onCloseTab,
}) => {
  if (openFiles.length === 0) {
    return null;
  }

  const getFileName = (path: string) => {
    const parts = path.split('/');
    return parts[parts.length - 1];
  };

  return (
    <div className="editor-tabs-bar">
      {openFiles.map((file) => {
        const isActive = file.path === activeFilePath;
        const fileName = getFileName(file.path);

        return (
          <div
            key={file.path}
            className={`editor-tab ${isActive ? 'active' : ''}`}
            onClick={() => onSelectTab(file.path)}
            title={file.path}
          >
            <FileCode size={14} className="tab-icon" />
            <span className="tab-name">{fileName}</span>
            {file.isDirty ? (
              <span
                className="tab-dirty"
                title="Unsaved changes"
                onClick={(e) => onCloseTab(file.path, e)}
              >
                <Circle size={8} fill="currentColor" />
              </span>
            ) : (
              <button
                className="tab-close-btn"
                title="Close tab"
                onClick={(e) => onCloseTab(file.path, e)}
              >
                <X size={13} />
              </button>
            )}
          </div>
        );
      })}
    </div>
  );
};
