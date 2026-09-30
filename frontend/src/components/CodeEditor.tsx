import React, { useEffect, useState } from 'react';
import Editor from '@monaco-editor/react';
import type { FileContent } from '../types';
import { Save, Code2, Globe, RefreshCw } from 'lucide-react';

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

  const handleSave = () => {
    if (activeFile) {
      onSave(activeFile.path, content, activeFile.version);
    }
  };

  const previewUrl = `http://127.0.0.1:8000/api/projects/${projectId}/preview/index.html`;


  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', backgroundColor: 'var(--bg-dark)' }}>
      {/* View Mode & Tab Header */}
      <div style={{
        height: '38px',
        backgroundColor: 'var(--bg-panel)',
        borderBottom: '1px solid var(--border-color)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 0.8rem'
      }}>
        {/* Left: Editor vs Preview Toggle */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <button
            className={`btn ${viewMode === 'editor' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '0.15rem 0.5rem', fontSize: '0.75rem' }}
            onClick={() => setViewMode('editor')}
          >
            <Code2 size={13} /> Code Editor
          </button>

          {(hasIndexHtml || activeFile?.path === 'index.html') && (
            <button
              className={`btn ${viewMode === 'preview' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ padding: '0.15rem 0.5rem', fontSize: '0.75rem', backgroundColor: viewMode === 'preview' ? 'var(--accent-emerald)' : undefined }}
              onClick={() => {
                setViewMode('preview');
                setIframeKey(Date.now());
              }}
            >
              <Globe size={13} /> Live Web Preview
            </button>
          )}

          {activeFile && viewMode === 'editor' && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginLeft: '0.5rem' }}>
              <span style={{ fontSize: '0.825rem', fontWeight: 600, color: 'var(--text-main)', fontFamily: 'var(--font-mono)' }}>
                {activeFile.path}
              </span>
              {isDirty && <span style={{ color: 'var(--accent-amber)', fontSize: '0.8rem' }}>●</span>}
              <span style={{
                fontSize: '0.675rem',
                padding: '0.1rem 0.35rem',
                borderRadius: '4px',
                backgroundColor: 'var(--bg-card)',
                color: 'var(--accent-blue)',
                border: '1px solid var(--border-color)'
              }}>
                v{activeFile.version}
              </span>
            </div>
          )}
        </div>

        {/* Right: Actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {viewMode === 'preview' ? (
            <button
              className="btn btn-secondary"
              style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }}
              onClick={() => setIframeKey(Date.now())}
            >
              <RefreshCw size={12} /> Reload Web App
            </button>
          ) : activeFile ? (
            <>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                {activeFile.size} bytes
              </span>
              <button
                className="btn btn-primary"
                style={{ padding: '0.25rem 0.6rem', fontSize: '0.775rem' }}
                onClick={handleSave}
                disabled={isSaving}
              >
                <Save size={13} />
                {isSaving ? 'Saving...' : 'Save'}
              </button>
            </>
          ) : null}
        </div>
      </div>

      {/* Main Content Area */}
      <div style={{ flex: 1, position: 'relative' }}>
        {viewMode === 'preview' ? (
          <iframe
            key={iframeKey}
            src={previewUrl}
            title="Live Web Application Preview"
            style={{
              width: '100%',
              height: '100%',
              border: 'none',
              backgroundColor: '#fff'
            }}
          />
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
              fontFamily: 'Fira Code, monospace',
              minimap: { enabled: false },
              scrollBeyondLastLine: false,
              automaticLayout: true,
              tabSize: 4
            }}
          />
        ) : (
          <div style={{
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--text-dim)',
            gap: '0.75rem'
          }}>
            <Code2 size={48} color="var(--border-bright)" />
            <p style={{ fontSize: '0.9rem' }}>Select a file from the explorer or ask Summit AI to generate your web app.</p>
          </div>
        )}
      </div>
    </div>
  );
};
