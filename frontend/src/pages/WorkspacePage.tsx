import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Project,
  FileNode,
  OpenFile,
  ChatMessage,
  AgentSessionStatus,
  AppEvent,
  ProjectMemory,
  ProjectSummary,
  CreateMemoryPayload,
} from '../types';
import { apiService } from '../services/api';
import { wsService } from '../services/websocket';
import { TopBar } from '../components/layout/TopBar';
import { ActivityBar } from '../components/layout/ActivityBar';
import { StatusBar } from '../components/layout/StatusBar';
import { FileExplorer } from '../components/explorer/FileExplorer';
import { EditorTabs } from '../components/editor/EditorTabs';
import { CodeEditor } from '../components/editor/CodeEditor';
import { AIChat } from '../components/ai/AIChat';
import { BottomPanel } from '../components/terminal/BottomPanel';
import { AddMemoryModal } from '../components/memory/AddMemoryModal';
import { EditSummaryModal } from '../components/summary/EditSummaryModal';

interface WorkspacePageProps {
  project: Project;
  onBackToProjects: () => void;
}

export const WorkspacePage: React.FC<WorkspacePageProps> = ({
  project,
  onBackToProjects,
}) => {
  // Sidebar & Layout State
  const [activeSidebarView, setActiveSidebarView] = useState<'explorer' | 'memory' | 'summary'>('explorer');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isBottomPanelOpen, setIsBottomPanelOpen] = useState(true);
  const [bottomPanelTab, setBottomPanelTab] = useState<'terminal' | 'activity' | 'memory' | 'summary'>('terminal');

  // File System State
  const [fileTree, setFileTree] = useState<FileNode[]>([]);
  const [isFileTreeLoading, setIsFileTreeLoading] = useState(false);
  const [openFiles, setOpenFiles] = useState<OpenFile[]>([]);
  const [activeFilePath, setActiveFilePath] = useState<string | null>(null);

  // Agent & Chat State
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [agentStatus, setAgentStatus] = useState<AgentSessionStatus>({ status: 'idle' });
  const [agentEvents, setAgentEvents] = useState<AppEvent[]>([]);
  const [terminalOutput, setTerminalOutput] = useState<string>('');

  // Memory & Summary State
  const [memories, setMemories] = useState<ProjectMemory[]>([]);
  const [projectSummary, setProjectSummary] = useState<ProjectSummary | null>(null);
  const [isAddMemoryOpen, setIsAddMemoryOpen] = useState(false);
  const [isEditSummaryOpen, setIsEditSummaryOpen] = useState(false);

  // WebSocket & Multiplayer Presence
  const [wsConnected, setWsConnected] = useState(false);
  const [connectedUsersCount, setConnectedUsersCount] = useState(1);
  const [statusNotification, setStatusNotification] = useState<string | null>(null);

  const activeFile = openFiles.find((f) => f.path === activeFilePath) || null;

  // Show status notification in the status bar
  const notify = (msg: string) => {
    setStatusNotification(msg);
    setTimeout(() => {
      setStatusNotification(null);
    }, 4000);
  };

  // 1. Initial Load for the Workspace
  const loadWorkspaceData = useCallback(async () => {
    try {
      setIsFileTreeLoading(true);
      const [treeData, memoryData, summaryData] = await Promise.all([
        apiService.getFileTree(project.id),
        apiService.getMemories(project.id).catch(() => []),
        apiService.getProjectSummary(project.id).catch(() => null),
      ]);

      setFileTree(treeData);
      setMemories(memoryData);
      setProjectSummary(summaryData);
    } catch (err: any) {
      notify(`Error loading workspace data: ${err.message}`);
    } finally {
      setIsFileTreeLoading(false);
    }
  }, [project.id]);

  // 2. Project Isolation & WebSocket Connection
  useEffect(() => {
    // Reset state when switching projects
    setOpenFiles([]);
    setActiveFilePath(null);
    setChatMessages([]);
    setAgentEvents([]);
    setTerminalOutput('');
    setAgentStatus({ status: 'idle' });

    // Load project data
    loadWorkspaceData();

    // Connect WebSocket strictly to this project
    const userId = `dev-${Math.random().toString(36).substring(2, 7)}`;
    const userName = `Developer`;

    wsService.connect(project.id, userId, userName);

    const unsubConnection = wsService.onConnectionChange((connected) => {
      setWsConnected(connected);
    });

    const unsubEvents = wsService.onEvent((event: AppEvent) => {
      // Record in activity timeline
      setAgentEvents((prev) => [event, ...prev.slice(0, 199)]);

      switch (event.type) {
        case 'agent_status': {
          const status = event.data?.status || 'idle';
          setAgentStatus({
            status,
            currentStep: event.data?.step,
            activeCommand: event.data?.command,
          });
          break;
        }

        case 'terminal_output': {
          const out = typeof event.data === 'string' ? event.data : event.data?.output || '';
          setTerminalOutput((prev) => prev + out + '\n');
          break;
        }

        case 'file_changed': {
          // Refresh file tree
          apiService.getFileTree(project.id).then(setFileTree).catch(() => {});

          // If the changed file is open in Monaco, update or notify
          const changedPath = event.data?.file_path;
          if (changedPath) {
            notify(`Agent modified: ${changedPath}`);
            apiService.getFileContent(project.id, changedPath).then((data) => {
              setOpenFiles((prev) =>
                prev.map((f) =>
                  f.path === changedPath
                    ? { ...f, content: data.content, originalContent: data.content, isDirty: false }
                    : f
                )
              );
            }).catch(() => {});
          }
          break;
        }

        case 'tool_call': {
          const toolName = event.data?.name || 'tool';
          const toolInput = event.data?.input || {};
          
          setChatMessages((prev) => {
            if (prev.length === 0) return prev;
            const lastMsg = prev[prev.length - 1];
            if (lastMsg.role === 'assistant') {
              const updatedTools = [
                ...(lastMsg.toolExecutions || []),
                { name: toolName, input: toolInput, status: 'running' as const },
              ];
              return [...prev.slice(0, -1), { ...lastMsg, toolExecutions: updatedTools }];
            }
            return prev;
          });
          break;
        }

        case 'tool_result': {
          const toolName = event.data?.name || 'tool';
          const toolOutput = event.data?.output || '';
          const isError = event.data?.is_error || false;

          setChatMessages((prev) => {
            if (prev.length === 0) return prev;
            const lastMsg = prev[prev.length - 1];
            if (lastMsg.role === 'assistant') {
              const updatedTools = (lastMsg.toolExecutions || []).map((t) =>
                t.name === toolName && t.status === 'running'
                  ? { ...t, output: toolOutput, status: isError ? ('error' as const) : ('completed' as const) }
                  : t
              );
              return [...prev.slice(0, -1), { ...lastMsg, toolExecutions: updatedTools }];
            }
            return prev;
          });
          break;
        }

        case 'agent_message': {
          const content = event.data?.content || '';
          const thought = event.data?.thought;
          setChatMessages((prev) => {
            if (prev.length > 0 && prev[prev.length - 1].role === 'assistant') {
              const last = prev[prev.length - 1];
              return [
                ...prev.slice(0, -1),
                { ...last, content: last.content ? `${last.content}\n${content}` : content, thought: thought || last.thought },
              ];
            } else {
              return [
                ...prev,
                {
                  id: `msg-${Date.now()}`,
                  role: 'assistant',
                  content,
                  thought,
                  timestamp: event.timestamp,
                },
              ];
            }
          });
          break;
        }

        case 'session_complete': {
          setAgentStatus({ status: 'completed' });
          notify('Agent session completed successfully');
          // Reload memories as the agent may have saved new ones
          apiService.getMemories(project.id).then(setMemories).catch(() => {});
          break;
        }

        case 'memory_saved': {
          apiService.getMemories(project.id).then(setMemories).catch(() => {});
          notify('New project memory stored in persistent memory');
          break;
        }

        case 'presence_update': {
          if (event.data?.count) {
            setConnectedUsersCount(event.data.count);
          }
          break;
        }

        default:
          break;
      }
    });

    return () => {
      unsubConnection();
      unsubEvents();
      wsService.disconnect();
    };
  }, [project.id, loadWorkspaceData]);

  // 3. File Explorer Actions
  const handleOpenFile = async (filePath: string) => {
    // Check if already open
    const existing = openFiles.find((f) => f.path === filePath);
    if (existing) {
      setActiveFilePath(filePath);
      return;
    }

    try {
      const data = await apiService.getFileContent(project.id, filePath);
      const newOpenFile: OpenFile = {
        path: filePath,
        content: data.content,
        originalContent: data.content,
        isDirty: false,
      };

      setOpenFiles((prev) => [...prev, newOpenFile]);
      setActiveFilePath(filePath);
    } catch (err: any) {
      notify(`Failed to open file: ${err.message}`);
    }
  };

  const handleCloseTab = (filePath: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const file = openFiles.find((f) => f.path === filePath);
    if (file?.isDirty) {
      if (!window.confirm(`File ${filePath} has unsaved changes. Close anyway?`)) {
        return;
      }
    }

    const nextFiles = openFiles.filter((f) => f.path !== filePath);
    setOpenFiles(nextFiles);

    if (activeFilePath === filePath) {
      if (nextFiles.length > 0) {
        setActiveFilePath(nextFiles[nextFiles.length - 1].path);
      } else {
        setActiveFilePath(null);
      }
    }
  };

  const handleEditorContentChange = (path: string, newContent: string) => {
    setOpenFiles((prev) =>
      prev.map((f) =>
        f.path === path
          ? {
              ...f,
              content: newContent,
              isDirty: newContent !== f.originalContent,
            }
          : f
      )
    );
  };

  const handleSaveFile = async (filePath: string) => {
    const file = openFiles.find((f) => f.path === filePath);
    if (!file) return;

    try {
      await apiService.saveFile(project.id, filePath, file.content);
      setOpenFiles((prev) =>
        prev.map((f) =>
          f.path === filePath
            ? { ...f, originalContent: file.content, isDirty: false }
            : f
        )
      );
      notify(`Saved ${filePath}`);
    } catch (err: any) {
      notify(`Error saving file: ${err.message}`);
    }
  };

  const handleCreateFile = async (filePath: string) => {
    try {
      await apiService.createFile(project.id, filePath, '');
      const tree = await apiService.getFileTree(project.id);
      setFileTree(tree);
      await handleOpenFile(filePath);
      notify(`Created ${filePath}`);
    } catch (err: any) {
      notify(`Error creating file: ${err.message}`);
    }
  };

  const handleDeleteFile = async (filePath: string) => {
    if (!window.confirm(`Delete ${filePath}?`)) return;

    try {
      await apiService.deleteFile(project.id, filePath);
      const tree = await apiService.getFileTree(project.id);
      setFileTree(tree);
      setOpenFiles((prev) => prev.filter((f) => f.path !== filePath));
      if (activeFilePath === filePath) {
        setActiveFilePath(null);
      }
      notify(`Deleted ${filePath}`);
    } catch (err: any) {
      notify(`Error deleting file: ${err.message}`);
    }
  };

  // 4. AI Agent Chat Actions
  const handleSendMessage = async (prompt: string) => {
    const userMessage: ChatMessage = {
      id: `usr-${Date.now()}`,
      role: 'user',
      content: prompt,
      timestamp: new Date().toISOString(),
      userName: 'You',
    };

    const pendingAssistantMessage: ChatMessage = {
      id: `ai-${Date.now() + 1}`,
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
      toolExecutions: [],
    };

    setChatMessages((prev) => [...prev, userMessage, pendingAssistantMessage]);
    setAgentStatus({ status: 'thinking' });

    try {
      await apiService.sendAgentMessage(project.id, prompt);
    } catch (err: any) {
      setAgentStatus({ status: 'error' });
      notify(`Agent error: ${err.message}`);
    }
  };

  const handleStopAgent = async () => {
    try {
      await apiService.stopAgent(project.id);
      setAgentStatus({ status: 'stopped' });
      notify('Agent stopped by user');
    } catch (err: any) {
      notify(`Error stopping agent: ${err.message}`);
    }
  };

  // 5. Memory & Summary Actions
  const handleSearchMemories = async (query: string) => {
    if (!query.trim()) {
      const data = await apiService.getMemories(project.id);
      setMemories(data);
      return;
    }
    try {
      const results = await apiService.searchMemories(project.id, query);
      setMemories(results);
    } catch (err: any) {
      notify(`Error searching memories: ${err.message}`);
    }
  };

  const handleAddMemory = async (payload: CreateMemoryPayload) => {
    await apiService.createMemory(project.id, payload);
    const data = await apiService.getMemories(project.id);
    setMemories(data);
    notify('Project memory saved');
  };

  const handleDeleteMemory = async (memoryId: string) => {
    if (!window.confirm('Delete this memory?')) return;
    try {
      await apiService.deleteMemory(project.id, memoryId);
      setMemories((prev) => prev.filter((m) => m.id !== memoryId));
      notify('Memory removed');
    } catch (err: any) {
      notify(`Error deleting memory: ${err.message}`);
    }
  };

  const handleSaveSummary = async (content: string) => {
    const updated = await apiService.updateProjectSummary(project.id, content);
    setProjectSummary(updated);
    notify('Project summary updated');
  };

  return (
    <div className="workspace-container">
      {/* Top Application Bar */}
      <TopBar
        project={project}
        agentStatus={agentStatus}
        wsConnected={wsConnected}
        connectedUsersCount={connectedUsersCount}
        onOpenProjectSelector={onBackToProjects}
      />

      {/* Main 3-Pane Work Area */}
      <div className="workspace-main-row">
        {/* Activity Icon Bar */}
        <ActivityBar
          activeView={activeSidebarView}
          onSelectView={(view) => {
            if (activeSidebarView === view && isSidebarOpen) {
              setIsSidebarOpen(false);
            } else {
              setActiveSidebarView(view);
              setIsSidebarOpen(true);
            }
          }}
        />

        {/* Left Sidebar (File Explorer / Memory / Summary) */}
        {isSidebarOpen && (
          <div className="workspace-sidebar">
            {activeSidebarView === 'explorer' && (
              <FileExplorer
                fileTree={fileTree}
                activeFilePath={activeFilePath}
                isLoading={isFileTreeLoading}
                onSelectFile={handleOpenFile}
                onRefreshTree={loadWorkspaceData}
                onCreateFile={handleCreateFile}
                onDeleteFile={handleDeleteFile}
              />
            )}
            {activeSidebarView === 'memory' && (
              <div className="sidebar-static-panel">
                <div className="sidebar-static-header">
                  <span>Project Memories ({memories.length})</span>
                </div>
                <div className="sidebar-static-body">
                  <button
                    className="btn-primary-small width-100"
                    onClick={() => setIsAddMemoryOpen(true)}
                  >
                    + Add Memory
                  </button>
                  <div className="sidebar-memory-list">
                    {memories.map((m) => (
                      <div key={m.id} className="sidebar-memory-item">
                        <span className="sidebar-memory-cat">{m.category || 'general'}</span>
                        <p>{m.content}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
            {activeSidebarView === 'summary' && (
              <div className="sidebar-static-panel">
                <div className="sidebar-static-header">
                  <span>Project Summary</span>
                </div>
                <div className="sidebar-static-body">
                  <button
                    className="btn-primary-small width-100"
                    onClick={() => setIsEditSummaryOpen(true)}
                  >
                    Edit Summary
                  </button>
                  <div className="sidebar-summary-text">
                    {projectSummary?.content || 'No summary defined yet.'}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Center Code Editor & Bottom Panels Area */}
        <div className="workspace-center-column">
          <div className="workspace-editor-area">
            <EditorTabs
              openFiles={openFiles}
              activeFilePath={activeFilePath}
              onSelectTab={setActiveFilePath}
              onCloseTab={handleCloseTab}
            />
            <CodeEditor
              activeFile={activeFile}
              onContentChange={handleEditorContentChange}
              onSaveFile={handleSaveFile}
              onAskAIAboutCode={(selectedCode, filePath) => {
                handleSendMessage(
                  `Inspect this code snippet in ${filePath}:\n\`\`\`\n${selectedCode}\n\`\`\``
                );
              }}
            />
          </div>

          {/* Bottom Docking Panel (Terminal, Activity, Memory, Summary) */}
          <BottomPanel
            projectId={project.id}
            terminalOutput={terminalOutput}
            agentEvents={agentEvents}
            memories={memories}
            summary={projectSummary}
            activeTab={bottomPanelTab}
            isOpen={isBottomPanelOpen}
            onTabChange={setBottomPanelTab}
            onToggleOpen={() => setIsBottomPanelOpen(!isBottomPanelOpen)}
            onClearTerminal={() => setTerminalOutput('')}
            onSearchMemories={handleSearchMemories}
            onRefreshMemories={() => apiService.getMemories(project.id).then(setMemories)}
            onRefreshSummary={() => apiService.getProjectSummary(project.id).then(setProjectSummary)}
            onOpenAddMemoryModal={() => setIsAddMemoryOpen(true)}
            onOpenEditSummaryModal={() => setIsEditSummaryOpen(true)}
            onDeleteMemory={handleDeleteMemory}
          />
        </div>

        {/* Right AI Coding Agent Chat Panel */}
        <div className="workspace-ai-column">
          <AIChat
            projectId={project.id}
            messages={chatMessages}
            agentStatus={agentStatus}
            onSendMessage={handleSendMessage}
            onStopAgent={handleStopAgent}
            onOpenFile={handleOpenFile}
            onClearChat={() => setChatMessages([])}
          />
        </div>
      </div>

      {/* Bottom Status Bar */}
      <StatusBar
        activeFilePath={activeFilePath}
        wsConnected={wsConnected}
        agentStatus={agentStatus}
        notification={statusNotification}
      />

      {/* Modals */}
      <AddMemoryModal
        isOpen={isAddMemoryOpen}
        onClose={() => setIsAddMemoryOpen(false)}
        onAddMemory={handleAddMemory}
      />

      <EditSummaryModal
        isOpen={isEditSummaryOpen}
        currentSummary={projectSummary}
        onClose={() => setIsEditSummaryOpen(false)}
        onSaveSummary={handleSaveSummary}
      />
    </div>
  );
};
