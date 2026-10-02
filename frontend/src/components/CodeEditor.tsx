import React, { useEffect, useState } from 'react';
import Editor from '@monaco-editor/react';
import type { FileContent } from '../types';
import {
  Save,
  Code2,
  Globe,
  RefreshCw,
  FileCode,
  FileText,
  FileJson,
  X,
  ChevronRight,
  ExternalLink
} from 'lucide-react';

interface CodeEditorProps {
  projectId: string;
  activeFile: FileContent | null;
  onSave: (path: string, content: string, expectedVersion: number) => Promise<void>;
  isSaving: boolean;
  hasIndexHtml?: boolean;
}

export const CodeEditor: React.FC<CodeEditorProps> = ({
  projectId,
  activeFile,
  onSave,
  isSaving,
  hasIndexHtml = false
}) => {
  const [content, setContent] = useState('');
  const [isDirty, setIsDirty] = useState(false);
  const [viewMode, setViewMode] = useState<'editor' | 'preview'>('editor');
  const [iframeKey, setIframeKey] = useState(Date.now());

  useEffect(() => {
    if (activeFile) {
      setContent(activeFile.content);
      setIsDirty(false);
    }
  }, [activeFile?.path, activeFile?.version, activeFile?.content]);

  // Handle Ctrl+S / Cmd+S shortcut inside editor
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        if (activeFile) {
          onSave(activeFile.path, content, activeFile.version);
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [activeFile, content, onSave]);

  const getLanguage = (path: string) => {
    if (path.endsWith('.py')) return 'python';
    if (path.endsWith('.ts') || path.endsWith('.tsx')) return 'typescript';
    if (path.endsWith('.js') || path.endsWith('.jsx')) return 'javascript';
    if (path.endsWith('.json')) return 'json';
    if (path.endsWith('.md')) return 'markdown';
    if (path.endsWith('.css')) return 'css';
    if (path.endsWith('.html')) return 'html';
    return 'plaintext';
  };

  const getFileIcon = (path: string) => {
    if (path.endsWith('.py')) return <FileCode size={13} color="#3776ab" />;
    if (path.endsWith('.ts') || path.endsWith('.tsx')) return <FileCode size={13} color="#3178c6" />;
    if (path.endsWith('.js') || path.endsWith('.jsx')) return <FileCode size={13} color="#f7df1e" />;
    if (path.endsWith('.html')) return <FileCode size={13} color="#e34f26" />;
    if (path.endsWith('.css')) return <FileCode size={13} color="#42a5f5" />;
    if (path.endsWith('.json')) return <FileJson size={13} color="#cbcb41" />;
    return <FileText size={13} color="var(--vscode-text-muted)" />;
  };

  const handleSave = () => {
    if (activeFile) {
      onSave(activeFile.path, content, activeFile.version);
    }
  };

  const previewUrl = `http://127.0.0.1:8000/api/projects/${projectId}/preview/index.html`;

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', backgroundColor: 'var(--vscode-bg-editor)' }}>
      {/* VSCodium Editor Tab Bar */}
      <div style={{
        height: '35px',
        backgroundColor: 'var(--vscode-bg-tab-inactive)',
        borderBottom: '1px solid var(--vscode-border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        userSelect: 'none'
      }}>
        {/* Left: Open Tabs */}
        <div style={{ display: 'flex', alignItems: 'center', height: '100%', overflowX: 'auto' }}>
          {activeFile && (
            <div
              style={{
                height: '100%',
                display: 'flex',
                alignItems: 'center',
                gap: '0.45rem',
                padding: '0 0.8rem',
                backgroundColor: viewMode === 'editor' ? 'var(--vscode-bg-tab-active)' : 'var(--vscode-bg-tab-inactive)',
                borderTop: viewMode === 'editor' ? '2px solid var(--vscode-accent)' : '2px solid transparent',
                borderRight: '1px solid var(--vscode-border)',
                color: viewMode === 'editor' ? 'var(--vscode-text-white)' : 'var(--vscode-text-muted)',
                fontSize: '12px',
                cursor: 'pointer'
              }}
              onClick={() => setViewMode('editor')}
            >
              {getFileIcon(activeFile.path)}
              <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 500 }}>{activeFile.path}</span>
              {isDirty ? (
                <span style={{ color: 'var(--vscode-accent-yellow)', fontSize: '10px' }}>●</span>
              ) : (
                <span style={{
                  fontSize: '10px',
                  color: 'var(--vscode-text-muted)',
                  backgroundColor: 'rgba(255,255,255,0.05)',
                  padding: '1px 4px',
                  borderRadius: '2px'
                }}>
                  v{activeFile.version}
                </span>
              )}
            </div>
          )}

          {(hasIndexHtml || activeFile?.path === 'index.html') && (
            <div
              style={{
                height: '100%',
                display: 'flex',
                alignItems: 'center',
                gap: '0.45rem',
                padding: '0 0.8rem',
                backgroundColor: viewMode === 'preview' ? 'var(--vscode-bg-tab-active)' : 'var(--vscode-bg-tab-inactive)',
                borderTop: viewMode === 'preview' ? '2px solid var(--vscode-accent-cyan)' : '2px solid transparent',
                borderRight: '1px solid var(--vscode-border)',
                color: viewMode === 'preview' ? 'var(--vscode-accent-cyan)' : 'var(--vscode-text-muted)',
                fontSize: '12px',
                cursor: 'pointer'
              }}
              onClick={() => {
                setViewMode('preview');
                setIframeKey(Date.now());
              }}
            >
              <Globe size={13} color="var(--vscode-accent-cyan)" />
              <span style={{ fontWeight: 500 }}>Web Preview</span>
            </div>
          )}
        </div>

        {/* Right: Actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', paddingRight: '0.6rem' }}>
          {viewMode === 'preview' ? (
            <>
              <button
                className="btn-icon"
                style={{ fontSize: '11px', padding: '3px 6px', gap: '4px' }}
                onClick={() => setIframeKey(Date.now())}
                title="Reload Web Preview"
              >
                <RefreshCw size={12} />
                <span>Reload</span>
              </button>
              <a
                href={previewUrl}
                target="_blank"
                rel="noreferrer"
                className="btn-icon"
                style={{ fontSize: '11px', padding: '3px 6px', textDecoration: 'none', gap: '4px' }}
                title="Open in New Tab"
              >
                <ExternalLink size={12} />
                <span>Popout</span>
              </a>
            </>
          ) : activeFile ? (
            <>
              <span style={{ fontSize: '11px', color: 'var(--vscode-text-muted)', marginRight: '0.4rem' }}>
                {activeFile.size} B
              </span>
              <button
                className="btn btn-primary"
                style={{ padding: '0.2rem 0.6rem', fontSize: '11px', height: '24px' }}
                onClick={handleSave}
                disabled={isSaving}
                title="Save File (Ctrl+S)"
              >
                <Save size={12} />
                <span>{isSaving ? 'Saving...' : 'Save'}</span>
              </button>
            </>
          ) : null}
        </div>
      </div>

      {/* Breadcrumbs Bar */}
      {activeFile && viewMode === 'editor' && (
        <div style={{
          height: '24px',
          backgroundColor: 'var(--vscode-bg-editor)',
          borderBottom: '1px solid var(--vscode-border)',
          display: 'flex',
          alignItems: 'center',
          padding: '0 0.8rem',
          fontSize: '11px',
          color: 'var(--vscode-text-muted)',
          gap: '0.35rem'
        }}>
          <span>workspace</span>
          <ChevronRight size={11} />
          <span style={{ color: 'var(--vscode-text-primary)' }}>{activeFile.path}</span>
        </div>
      )}

      {/* Main Workspace Body */}
      <div style={{ flex: 1, position: 'relative', overflow: 'hidden' }}>
        {viewMode === 'preview' ? (
          <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            {/* Embedded Browser Navigation Bar */}
            <div style={{
              height: '32px',
              backgroundColor: 'var(--vscode-bg-sidebar)',
              borderBottom: '1px solid var(--vscode-border)',
              display: 'flex',
              alignItems: 'center',
              padding: '0 0.6rem',
              gap: '0.5rem'
            }}>
              <button
                className="btn-icon"
                onClick={() => setIframeKey(Date.now())}
                title="Refresh Preview"
              >
                <RefreshCw size={12} />
              </button>
              <div style={{
                flex: 1,
                backgroundColor: 'var(--vscode-bg-input)',
                borderRadius: '3px',
                padding: '0.15rem 0.5rem',
                fontSize: '11px',
                color: 'var(--vscode-text-secondary)',
                fontFamily: 'var(--font-mono)',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap'
              }}>
                {previewUrl}
              </div>
            </div>

            <iframe
              key={iframeKey}
              src={previewUrl}
              title="Live Web Application Preview"
              style={{
                flex: 1,
                width: '100%',
                border: 'none',
                backgroundColor: '#ffffff'
              }}
            />
          </div>
        ) : activeFile ? (
          <Editor
            height="100%"
            language={getLanguage(activeFile.path)}
            theme="vs-dark"
            value={content}
            onChange={(val) => {
              setContent(val || '');
              setIsDirty(true);
            }}
            options={{
              fontSize: 13,
              fontFamily: 'JetBrains Mono, Consolas, Courier New, monospace',
              minimap: { enabled: true, maxColumn: 80 },
              scrollBeyondLastLine: false,
              automaticLayout: true,
              tabSize: 4,
              renderLineHighlight: 'all',
              cursorBlinking: 'smooth',
              cursorSmoothCaretAnimation: 'on',
              lineNumbers: 'on',
              padding: { top: 8 }
            }}
          />
        ) : (
          <div style={{
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--vscode-text-muted)',
            gap: '0.6rem',
            userSelect: 'none'
          }}>
            <Code2 size={40} color="var(--vscode-border-light)" />
            <p style={{ fontSize: '12px' }}>Select a file from the explorer or prompt the AI agent.</p>
          </div>
        )}
      </div>
    </div>
  );
};
