import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  Terminal as TerminalIcon,
  Plus,
  X,
  ChevronUp,
  ChevronDown,
  Trash2,
  Maximize2,
  Minimize2,
  Play,
  RotateCcw,
  Square,
  Sparkles
} from 'lucide-react';
import * as api from '../../api/client';

interface TerminalTab {
  id: string;
  name: string;
  history: string[];
  currentDir: string;
}

interface IntegratedTerminalProps {
  projectId: string;
}

const QUICK_COMMANDS = [
  'npm run dev',
  'git status',
  'python -V',
  'node -v',
  'ls',
  'dir',
  'help'
];

export const IntegratedTerminal: React.FC<IntegratedTerminalProps> = ({ projectId }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMaximized, setIsMaximized] = useState(false);
  const [height, setHeight] = useState(250);
  const [tabs, setTabs] = useState<TerminalTab[]>([
    {
      id: 'term-1',
      name: 'zsh — Workspace',
      history: [
        '\x1b[38;2;96;165;250m┌──(summit㉿studio)-[~/workspace]\x1b[0m',
        '\x1b[38;2;52;211;153m└─❯\x1b[0m \x1b[1mTerminal Ready.\x1b[0m Type real shell commands or select quick actions below.',
        '\x1b[38;2;148;163;184m  Supported: python, node, npm, git, ls, dir, cat, cd, pip, curl, etc.\x1b[0m',
        ''
      ],
      currentDir: ''
    }
  ]);
  const [activeTabId, setActiveTabId] = useState('term-1');
  const [command, setCommand] = useState('');
  const [commandHistory, setCommandHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [isRunning, setIsRunning] = useState(false);
  const [currentRunningCmd, setCurrentRunningCmd] = useState<string | null>(null);

  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const resizeRef = useRef<{ startY: number; startHeight: number } | null>(null);

  const activeTab = tabs.find(t => t.id === activeTabId) || tabs[0];

  // Auto-scroll on new output
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [activeTab?.history, isRunning]);

  // Focus input when terminal opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen, activeTabId]);

  const addOutput = useCallback((tabId: string, lines: string[]) => {
    setTabs(prev => prev.map(t =>
      t.id === tabId
        ? { ...t, history: [...t.history, ...lines] }
        : t
    ));
  }, []);

  const runCommandDirectly = async (cmdToRun: string) => {
    const cmd = cmdToRun.trim();
    if (!cmd) return;

    setCommandHistory(prev => [cmd, ...prev.filter(c => c !== cmd)]);
    setHistoryIndex(-1);
    setCommand('');

    const displayPath = activeTab.currentDir ? `~/workspace/${activeTab.currentDir}` : '~/workspace';

    // Print command invocation prompt
    addOutput(activeTabId, [
      `\x1b[38;2;96;165;250m┌──(summit㉿studio)-[${displayPath}]\x1b[0m`,
      `\x1b[38;2;52;211;153m└─❯\x1b[0m ${cmd}`
    ]);

    // Handle Client-Side / Built-in helper commands
    if (cmd === 'clear' || cmd === 'cls') {
      setTabs(prev => prev.map(t =>
        t.id === activeTabId ? { ...t, history: [] } : t
      ));
      return;
    }

    if (cmd === 'help') {
      addOutput(activeTabId, [
        '',
        '\x1b[38;2;168;85;247m  ✦ Summit Integrated Terminal\x1b[0m',
        '  \x1b[38;2;96;165;250m• Real Execution:\x1b[0m Direct shell commands executed inside your project workspace directory.',
        '  \x1b[38;2;96;165;250m• Navigation:\x1b[0m cd <folder>, cd .., cd /',
        '  \x1b[38;2;96;165;250m• Builtins:\x1b[0m clear, cls, help, whoami, version, date',
        '  \x1b[38;2;96;165;250m• Shortcuts:\x1b[0m ↑/↓ for history, Ctrl+L to clear, Ctrl+C to cancel',
        ''
      ]);
      return;
    }

    if (cmd === 'version') {
      addOutput(activeTabId, [
        `  \x1b[38;2;168;85;247mSummit AI Studio Terminal\x1b[0m v1.2.0`,
        `  \x1b[38;2;148;163;184mProject Workspace: ${projectId}\x1b[0m`,
        ''
      ]);
      return;
    }

    if (cmd === 'whoami') {
      const session = localStorage.getItem('summit_auth_session');
      let name = 'Developer';
      try {
        if (session) name = JSON.parse(session).displayName || name;
      } catch {}
      addOutput(activeTabId, [`  ${name} (Summit Workspace Contributor)`, '']);
      return;
    }

    if (cmd === 'date') {
      addOutput(activeTabId, [`  ${new Date().toLocaleString()}`, '']);
      return;
    }

    // Handle `cd` directory tracking
    if (cmd === 'cd' || cmd === 'cd ~' || cmd === 'cd /') {
      setTabs(prev => prev.map(t => t.id === activeTabId ? { ...t, currentDir: '' } : t));
      addOutput(activeTabId, ['']);
      return;
    }

    if (cmd.startsWith('cd ')) {
      const target = cmd.slice(3).trim();
      if (target === '..') {
        const parts = activeTab.currentDir.split('/').filter(Boolean);
        parts.pop();
        const newDir = parts.join('/');
        setTabs(prev => prev.map(t => t.id === activeTabId ? { ...t, currentDir: newDir } : t));
      } else {
        const newDir = activeTab.currentDir ? `${activeTab.currentDir}/${target}` : target;
        setTabs(prev => prev.map(t => t.id === activeTabId ? { ...t, currentDir: newDir.replace(/^[\/\\]+|[\/\\]+$/g, '') } : t));
      }
      addOutput(activeTabId, ['']);
      return;
    }

    // Execute real backend command
    setIsRunning(true);
    setCurrentRunningCmd(cmd);
    const startTime = performance.now();

    try {
      const res = await api.executeTerminalCommand(
        projectId,
        cmd,
        activeTab.currentDir || undefined
      );

      const duration = ((performance.now() - startTime) / 1000).toFixed(2);
      const output = res.output ? res.output.trimEnd() : '';

      if (output) {
        addOutput(activeTabId, output.split('\n'));
      }

      if (res.exit_code === 0) {
        addOutput(activeTabId, [
          `\x1b[38;2;52;211;153m✔ Process finished in ${duration}s (exit code 0)\x1b[0m`,
          ''
        ]);
      } else {
        addOutput(activeTabId, [
          `\x1b[38;2;248;113;113m✖ Process exited with code ${res.exit_code} (${duration}s)\x1b[0m`,
          ''
        ]);
      }
    } catch (err: any) {
      addOutput(activeTabId, [
        `\x1b[38;2;248;113;113mError executing command:\x1b[0m ${err.message || err}`,
        ''
      ]);
    } finally {
      setIsRunning(false);
      setCurrentRunningCmd(null);
    }
  };

  const handleCommandSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    runCommandDirectly(command);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (commandHistory.length > 0) {
        const newIndex = Math.min(historyIndex + 1, commandHistory.length - 1);
        setHistoryIndex(newIndex);
        setCommand(commandHistory[newIndex]);
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historyIndex > 0) {
        const newIndex = historyIndex - 1;
        setHistoryIndex(newIndex);
        setCommand(commandHistory[newIndex]);
      } else {
        setHistoryIndex(-1);
        setCommand('');
      }
    } else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'l') {
      e.preventDefault();
      setTabs(prev => prev.map(t => t.id === activeTabId ? { ...t, history: [] } : t));
    } else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'c') {
      if (isRunning) {
        setIsRunning(false);
        setCurrentRunningCmd(null);
        addOutput(activeTabId, ['^C', '']);
      }
    }
  };

  const addTab = () => {
    const id = `term-${Date.now()}`;
    const newTab: TerminalTab = {
      id,
      name: `zsh (${tabs.length + 1})`,
      history: [
        `\x1b[38;2;96;165;250m┌──(summit㉿studio)-[~/workspace]\x1b[0m`,
        `\x1b[38;2;52;211;153m└─❯\x1b[0m Session started`,
        ''
      ],
      currentDir: ''
    };
    setTabs(prev => [...prev, newTab]);
    setActiveTabId(id);
  };

  const closeTab = (id: string) => {
    if (tabs.length <= 1) return;
    setTabs(prev => prev.filter(t => t.id !== id));
    if (activeTabId === id) {
      setActiveTabId(tabs.find(t => t.id !== id)?.id || tabs[0].id);
    }
  };

  const clearTerminal = () => {
    setTabs(prev => prev.map(t =>
      t.id === activeTabId ? { ...t, history: [] } : t
    ));
  };

  // Resize handling
  const handleResizeStart = (e: React.MouseEvent) => {
    e.preventDefault();
    resizeRef.current = { startY: e.clientY, startHeight: height };

    const handleMouseMove = (ev: MouseEvent) => {
      if (!resizeRef.current) return;
      const diff = resizeRef.current.startY - ev.clientY;
      const newHeight = Math.max(140, Math.min(window.innerHeight - 100, resizeRef.current.startHeight + diff));
      setHeight(newHeight);
    };

    const handleMouseUp = () => {
      resizeRef.current = null;
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  // Enhanced ANSI color parser (16 standard colors + 24-bit RGB + bold)
  const renderLine = (line: string, idx: number) => {
    const parts: React.ReactNode[] = [];
    let remaining = line;
    let key = 0;

    while (remaining.length > 0) {
      // Check RGB ANSI: \x1b[38;2;R;G;Bm
      const rgbMatch = remaining.match(/\x1b\[38;2;(\d+);(\d+);(\d+)m/);
      // Check standard ANSI: \x1b[1m, \x1b[31m, etc.
      const stdMatch = remaining.match(/\x1b\[(\d+)(?:;(\d+))?m/);

      let firstMatch: { index: number; length: number; color?: string; bold?: boolean } | null = null;

      if (rgbMatch && rgbMatch.index !== undefined) {
        firstMatch = {
          index: rgbMatch.index,
          length: rgbMatch[0].length,
          color: `rgb(${rgbMatch[1]}, ${rgbMatch[2]}, ${rgbMatch[3]})`
        };
      }

      if (stdMatch && stdMatch.index !== undefined) {
        if (!firstMatch || stdMatch.index < firstMatch.index) {
          const code = parseInt(stdMatch[1], 10);
          let color: string | undefined;
          let bold = false;

          if (code === 1) bold = true;
          else if (code === 31 || code === 91) color = '#f87171'; // red
          else if (code === 32 || code === 92) color = '#4ade80'; // green
          else if (code === 33 || code === 93) color = '#fbbf24'; // yellow
          else if (code === 34 || code === 94) color = '#60a5fa'; // blue
          else if (code === 35 || code === 95) color = '#c084fc'; // magenta
          else if (code === 36 || code === 96) color = '#22d3ee'; // cyan
          else if (code === 37 || code === 97) color = '#f4f4f5'; // white
          else if (code === 90) color = '#94a3b8'; // grey

          firstMatch = {
            index: stdMatch.index,
            length: stdMatch[0].length,
            color,
            bold
          };
        }
      }

      if (firstMatch) {
        if (firstMatch.index > 0) {
          parts.push(<span key={key++}>{remaining.slice(0, firstMatch.index)}</span>);
        }

        const afterMatch = remaining.slice(firstMatch.index + firstMatch.length);
        const resetIdx = afterMatch.indexOf('\x1b[0m');

        if (resetIdx !== -1) {
          const text = afterMatch.slice(0, resetIdx);
          parts.push(
            <span
              key={key++}
              style={{
                color: firstMatch.color,
                fontWeight: firstMatch.bold ? 600 : undefined
              }}
            >
              {text}
            </span>
          );
          remaining = afterMatch.slice(resetIdx + 4);
        } else {
          parts.push(
            <span
              key={key++}
              style={{
                color: firstMatch.color,
                fontWeight: firstMatch.bold ? 600 : undefined
              }}
            >
              {afterMatch}
            </span>
          );
          remaining = '';
        }
      } else {
        parts.push(<span key={key++}>{remaining}</span>);
        remaining = '';
      }
    }

    return (
      <div key={idx} style={{ minHeight: '18px', lineHeight: '19px', wordBreak: 'break-word' }}>
        {parts.length > 0 ? parts : '\u00A0'}
      </div>
    );
  };

  // Collapsed bottom dock bar
  if (!isOpen) {
    return (
      <div
        onClick={() => setIsOpen(true)}
        style={{
          height: '32px',
          minHeight: '32px',
          background: '#121215',
          borderTop: '1px solid var(--vscode-border)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 12px',
          cursor: 'pointer',
          userSelect: 'none',
          transition: 'background 0.15s ease'
        }}
        onMouseEnter={e => e.currentTarget.style.background = '#18181b'}
        onMouseLeave={e => e.currentTarget.style.background = '#121215'}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <TerminalIcon size={14} color="#a855f7" />
            <span style={{
              fontSize: '11px',
              fontWeight: 600,
              color: 'var(--vscode-text-white)',
              textTransform: 'uppercase',
              letterSpacing: '0.04em'
            }}>
              Terminal
            </span>
          </div>

          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
            fontSize: '10px',
            color: '#4ade80',
            backgroundColor: 'rgba(74, 222, 128, 0.12)',
            padding: '1px 6px',
            borderRadius: '10px',
            fontWeight: 500
          }}>
            <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#4ade80', display: 'inline-block' }} />
            Ready
          </div>

          {activeTab.currentDir && (
            <span style={{ fontSize: '11px', color: 'var(--vscode-text-muted)', fontFamily: 'var(--font-mono)' }}>
              ({activeTab.currentDir})
            </span>
          )}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--vscode-text-muted)', fontSize: '11px' }}>
          <span>Click to open</span>
          <ChevronUp size={14} />
        </div>
      </div>
    );
  }

  const terminalHeight = isMaximized ? 'calc(100vh - 44px - 26px)' : `${height}px`;
  const currentPathDisplay = activeTab.currentDir ? `~/workspace/${activeTab.currentDir}` : '~/workspace';

  return (
    <div
      style={{
        height: terminalHeight,
        display: 'flex',
        flexDirection: 'column',
        background: '#09090b',
        borderTop: '1px solid var(--vscode-border)',
        overflow: 'hidden',
        transition: isMaximized ? 'height 0.25s cubic-bezier(0.4, 0, 0.2, 1)' : 'none',
        zIndex: 8
      }}
    >
      {/* Draggable Resize Handle */}
      {!isMaximized && (
        <div
          onMouseDown={handleResizeStart}
          style={{
            height: '4px',
            background: 'transparent',
            cursor: 'ns-resize',
            transition: 'background 0.15s ease',
            flexShrink: 0
          }}
          onMouseEnter={e => e.currentTarget.style.background = '#60a5fa'}
          onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
          title="Drag to resize terminal height"
        />
      )}

      {/* Terminal Titlebar & Tabs */}
      <div style={{
        height: '36px',
        minHeight: '36px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 10px',
        background: '#121215',
        borderBottom: '1px solid var(--vscode-border)',
        userSelect: 'none'
      }}>
        {/* Left: Terminal Tabs */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', overflow: 'hidden' }}>
          {tabs.map(tab => (
            <div
              key={tab.id}
              onClick={() => setActiveTabId(tab.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '4px 10px',
                borderRadius: '6px',
                color: activeTabId === tab.id ? 'var(--vscode-text-white)' : 'var(--vscode-text-muted)',
                background: activeTabId === tab.id ? '#18181b' : 'transparent',
                border: activeTabId === tab.id ? '1px solid var(--vscode-border)' : '1px solid transparent',
                fontSize: '12px',
                cursor: 'pointer',
                fontWeight: activeTabId === tab.id ? 600 : 400,
                transition: 'all 0.15s ease',
                whiteSpace: 'nowrap'
              }}
            >
              <TerminalIcon size={13} color={activeTabId === tab.id ? '#a855f7' : '#94a3b8'} />
              <span>{tab.name}</span>
              {tabs.length > 1 && (
                <button
                  onClick={(e) => { e.stopPropagation(); closeTab(tab.id); }}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: 'var(--vscode-text-muted)',
                    padding: '2px',
                    cursor: 'pointer',
                    display: 'flex',
                    borderRadius: '3px',
                    transition: 'color 0.15s ease'
                  }}
                  onMouseEnter={e => e.currentTarget.style.color = '#f87171'}
                  onMouseLeave={e => e.currentTarget.style.color = 'var(--vscode-text-muted)'}
                >
                  <X size={11} />
                </button>
              )}
            </div>
          ))}

          <button
            onClick={addTab}
            title="New Terminal Tab"
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--vscode-text-muted)',
              padding: '4px 6px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              borderRadius: '4px',
              transition: 'all 0.15s ease'
            }}
            onMouseEnter={e => { e.currentTarget.style.color = '#ffffff'; e.currentTarget.style.background = 'rgba(255,255,255,0.08)'; }}
            onMouseLeave={e => { e.currentTarget.style.color = 'var(--vscode-text-muted)'; e.currentTarget.style.background = 'none'; }}
          >
            <Plus size={14} />
          </button>
        </div>

        {/* Right: Quick Command Palette & Window Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          {/* Running status badge */}
          {isRunning && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
              fontSize: '11px',
              color: '#38bdf8',
              backgroundColor: 'rgba(56, 189, 248, 0.12)',
              padding: '2px 8px',
              borderRadius: '9999px',
              fontWeight: 500
            }}>
              <span style={{ animation: 'spin 1s linear infinite', display: 'inline-block' }}>⟳</span>
              <span>Running: {currentRunningCmd}</span>
            </div>
          )}

          <button
            onClick={clearTerminal}
            title="Clear Terminal Output (Ctrl+L)"
            className="btn-icon"
            style={{ padding: '4px' }}
          >
            <Trash2 size={13} />
          </button>

          <button
            onClick={() => setIsMaximized(!isMaximized)}
            title={isMaximized ? 'Restore Terminal' : 'Maximize Terminal'}
            className="btn-icon"
            style={{ padding: '4px' }}
          >
            {isMaximized ? <Minimize2 size={13} /> : <Maximize2 size={13} />}
          </button>

          <button
            onClick={() => { setIsOpen(false); setIsMaximized(false); }}
            title="Hide Terminal"
            className="btn-icon"
            style={{ padding: '4px' }}
          >
            <ChevronDown size={14} />
          </button>
        </div>
      </div>

      {/* Quick Actions Bar */}
      <div style={{
        padding: '4px 12px',
        backgroundColor: '#0c0c0e',
        borderBottom: '1px solid var(--vscode-border)',
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
        overflowX: 'auto',
        userSelect: 'none'
      }}>
        <span style={{ fontSize: '10px', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--vscode-text-muted)', fontWeight: 600, flexShrink: 0 }}>
          Quick Run:
        </span>
        {QUICK_COMMANDS.map((q) => (
          <button
            key={q}
            onClick={() => runCommandDirectly(q)}
            disabled={isRunning}
            style={{
              padding: '2px 8px',
              fontSize: '11px',
              fontFamily: 'var(--font-mono)',
              backgroundColor: '#18181b',
              color: 'var(--vscode-text-primary)',
              border: '1px solid var(--vscode-border)',
              borderRadius: '4px',
              cursor: isRunning ? 'not-allowed' : 'pointer',
              whiteSpace: 'nowrap',
              transition: 'all 0.15s ease'
            }}
            onMouseEnter={e => { if (!isRunning) { e.currentTarget.style.backgroundColor = '#27272a'; e.currentTarget.style.color = '#ffffff'; } }}
            onMouseLeave={e => { if (!isRunning) { e.currentTarget.style.backgroundColor = '#18181b'; e.currentTarget.style.color = 'var(--vscode-text-primary)'; } }}
          >
            {q}
          </button>
        ))}
      </div>

      {/* Terminal Log Output Window */}
      <div
        ref={scrollRef}
        onClick={() => inputRef.current?.focus()}
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '10px 14px',
          fontFamily: 'var(--font-mono)',
          fontSize: '12px',
          lineHeight: '19px',
          color: '#f4f4f5',
          cursor: 'text',
          userSelect: 'text',
          backgroundColor: '#09090b'
        }}
      >
        {activeTab?.history.map((line, i) => renderLine(line, i))}
        {isRunning && (
          <div style={{ color: '#38bdf8', display: 'flex', alignItems: 'center', gap: '6px', marginTop: '4px' }}>
            <span style={{ animation: 'spin 1s linear infinite', display: 'inline-block' }}>⟳</span>
            <span>Executing... (Press Ctrl+C to cancel)</span>
          </div>
        )}
      </div>

      {/* Interactive Command Input Form */}
      <form
        onSubmit={handleCommandSubmit}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '6px 14px',
          background: '#121215',
          borderTop: '1px solid var(--vscode-border)'
        }}
      >
        <span style={{
          color: '#38bdf8',
          fontFamily: 'var(--font-mono)',
          fontSize: '12px',
          fontWeight: 600,
          userSelect: 'none'
        }}>
          {currentPathDisplay}
        </span>
        <span style={{
          color: '#4ade80',
          fontFamily: 'var(--font-mono)',
          fontSize: '13px',
          fontWeight: 700,
          userSelect: 'none'
        }}>
          ❯
        </span>
        <input
          ref={inputRef}
          type="text"
          value={command}
          onChange={e => setCommand(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isRunning}
          placeholder={isRunning ? "Command is executing..." : "Type command here (e.g. ls, npm run dev, python)..."}
          style={{
            flex: 1,
            background: 'transparent',
            border: 'none',
            color: '#f4f4f5',
            fontFamily: 'var(--font-mono)',
            fontSize: '12px',
            outline: 'none',
            padding: '4px 0',
            caretColor: '#60a5fa'
          }}
        />
        {command.trim() && (
          <button
            type="submit"
            disabled={isRunning}
            className="btn btn-primary"
            style={{ padding: '2px 8px', fontSize: '11px', display: 'flex', alignItems: 'center', gap: '4px' }}
          >
            <Play size={10} /> Run
          </button>
        )}
      </form>
    </div>
  );
};
