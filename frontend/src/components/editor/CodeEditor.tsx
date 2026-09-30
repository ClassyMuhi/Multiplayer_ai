import React, { useRef, useEffect, useCallback } from 'react';
import Editor, { Monaco, OnMount } from '@monaco-editor/react';
import { FileCode, Save, Sparkles } from 'lucide-react';
import { OpenFile } from '../../types';

interface CodeEditorProps {
  activeFile: OpenFile | null;
  onContentChange: (path: string, content: string) => void;
  onSaveFile: (path: string) => void;
  onAskAIAboutCode?: (selectedCode: string, filePath: string) => void;
}

export const CodeEditor: React.FC<CodeEditorProps> = ({
  activeFile,
  onContentChange,
  onSaveFile,
  onAskAIAboutCode,
}) => {
  const editorRef = useRef<any>(null);
  const monacoRef = useRef<Monaco | null>(null);

  // Auto-detect language by file extension
  const getLanguage = (filePath: string): string => {
    const ext = filePath.split('.').pop()?.toLowerCase();
    switch (ext) {
      case 'py':
        return 'python';
      case 'ts':
        return 'typescript';
      case 'tsx':
        return 'typescript';
      case 'js':
        return 'javascript';
      case 'jsx':
        return 'javascript';
      case 'json':
        return 'json';
      case 'html':
        return 'html';
      case 'css':
        return 'css';
      case 'md':
        return 'markdown';
      case 'sql':
        return 'sql';
      case 'yaml':
      case 'yml':
        return 'yaml';
      case 'sh':
      case 'bash':
        return 'shell';
      case 'dockerfile':
        return 'dockerfile';
      default:
        return 'plaintext';
    }
  };

  const handleEditorMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;
    monacoRef.current = monaco;

    // Define custom dark theme matching IDE palette
    monaco.editor.defineTheme('agentic-dark', {
      base: 'vs-dark',
      inherit: true,
      rules: [
        { token: 'comment', foreground: '6272a4', fontStyle: 'italic' },
        { token: 'keyword', foreground: 'ff79c6' },
        { token: 'string', foreground: 'f1fa8c' },
        { token: 'number', foreground: 'bd93f9' },
        { token: 'type', foreground: '8be9fd' },
        { token: 'function', foreground: '50fa7b' },
      ],
      colors: {
        'editor.background': '#0f111a',
        'editor.foreground': '#e6edf3',
        'editor.lineHighlightBackground': '#181b29',
        'editorCursor.foreground': '#58a6ff',
        'editorWhitespace.foreground': '#21262d',
        'editorIndentGuide.background': '#1f2430',
        'editorIndentGuide.activeBackground': '#388bfd',
        'editorLineNumber.foreground': '#484f58',
        'editorLineNumber.activeForeground': '#c9d1d9',
        'editorGutter.background': '#0f111a',
      },
    });

    monaco.editor.setTheme('agentic-dark');

    // Add Ctrl+S / Cmd+S save command directly to Monaco
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      if (activeFile) {
        onSaveFile(activeFile.path);
      }
    });

    // Add Context Menu Action for "Ask AI about this code"
    if (onAskAIAboutCode) {
      editor.addAction({
        id: 'ask-ai-selection',
        label: 'Ask AI Agent About Selection',
        contextMenuGroupId: 'navigation',
        contextMenuOrder: 1.5,
        run: (ed) => {
          const selection = ed.getSelection();
          if (selection && activeFile) {
            const selectedText = ed.getModel()?.getValueInRange(selection);
            if (selectedText) {
              onAskAIAboutCode(selectedText, activeFile.path);
            }
          }
        },
      });
    }
  };

  // Keyboard shortcut listener on window for save
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        if (activeFile) {
          onSaveFile(activeFile.path);
        }
      }
    },
    [activeFile, onSaveFile]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  if (!activeFile) {
    return (
      <div className="editor-empty-state">
        <div className="editor-empty-content">
          <div className="empty-icon-wrapper">
            <FileCode size={48} className="empty-icon" />
          </div>
          <h3>No File Open</h3>
          <p>Select a file from the explorer on the left to start editing, or ask the AI agent to create or modify code.</p>
          <div className="empty-shortcuts">
            <div className="shortcut-item">
              <span className="key-badge">Ctrl</span> + <span className="key-badge">S</span>
              <span className="shortcut-desc">Save active file</span>
            </div>
            <div className="shortcut-item">
              <span className="key-badge">Ctrl</span> + <span className="key-badge">Enter</span>
              <span className="shortcut-desc">Send AI prompt</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="code-editor-container">
      <div className="editor-header">
        <div className="editor-file-info">
          <span className="editor-file-path">{activeFile.path}</span>
          {activeFile.isDirty && <span className="dirty-badge">● Unsaved</span>}
        </div>
        <div className="editor-actions">
          <button
            className={`editor-save-btn ${activeFile.isDirty ? 'btn-highlight' : ''}`}
            onClick={() => onSaveFile(activeFile.path)}
            title="Save File (Ctrl+S)"
          >
            <Save size={13} />
            <span>Save</span>
          </button>
        </div>
      </div>
      <div className="editor-monaco-wrapper">
        <Editor
          height="100%"
          language={getLanguage(activeFile.path)}
          value={activeFile.content}
          onChange={(value) => onContentChange(activeFile.path, value || '')}
          onMount={handleEditorMount}
          theme="agentic-dark"
          options={{
            fontFamily: "'JetBrains Mono', 'Fira Code', 'Courier New', monospace",
            fontSize: 13,
            lineHeight: 20,
            minimap: { enabled: true, maxColumn: 80, scale: 0.8 },
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 2,
            wordWrap: 'on',
            renderWhitespace: 'selection',
            smoothScrolling: true,
            cursorBlinking: 'smooth',
            cursorSmoothCaretAnimation: 'on',
            bracketPairColorization: { enabled: true },
          }}
        />
      </div>
    </div>
  );
};
