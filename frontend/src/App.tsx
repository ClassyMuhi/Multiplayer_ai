import React, { useState, useEffect, useRef } from 'react';
import type {
  Project,
  FileNode,
  FileContent,
  UserPresence,
  MessageRecord,
  ProjectMemory,
  AgentStatusType,
  AppEvent,
  GitStatus,
  FileConflictData
} from './types';

import * as api from './api/client';
import { ProjectHeader } from './components/ProjectHeader';
import { FileExplorer } from './components/FileExplorer';
import { CodeEditor } from './components/CodeEditor';
import { AgentPanel } from './components/AgentPanel';
import { MemoryPanel } from './components/MemoryPanel';
import { GitPanel } from './components/GitPanel';
import { ConflictModal } from './components/ConflictModal';

export const App: React.FC = () => {

  const [projects, setProjects] = useState<Project[]>([]);
  const [currentProject, setCurrentProject] = useState<Project | null>(null);
  const [files, setFiles] = useState<FileNode[]>([]);
  const [activeFile, setActiveFile] = useState<FileContent | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  const [currentUser, setCurrentUser] = useState({
    userId: 'user_a',
    displayName: 'Alice (Dev A)'
  });
  const [connectedUsers, setConnectedUsers] = useState<UserPresence[]>([]);

  const [messages, setMessages] = useState<MessageRecord[]>([]);
  const [memories, setMemories] = useState<ProjectMemory[]>([]);
  const [agentStatus, setAgentStatus] = useState<AgentStatusType>('IDLE');
  const [events, setEvents] = useState<AppEvent[]>([]);

  const [gitStatus, setGitStatus] = useState<GitStatus | null>(null);
  const [gitDiff, setGitDiff] = useState<string | null>(null);
  const [conflictData, setConflictData] = useState<FileConflictData | null>(null);

  const wsRef = useRef<WebSocket | null>(null);

  // Initial load projects
  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const list = await api.fetchProjects();
      setProjects(list);
      if (list.length > 0 && !currentProject) {
        selectProject(list[0]);
      }
    } catch (e) {
      console.error('Error loading projects:', e);
    }
  };

  const selectProject = async (project: Project) => {
    setCurrentProject(project);
    setActiveFile(null);
    setEvents([]);

    try {
      const [fileTree, msgs, mems, users, git] = await Promise.all([
        api.fetchFiles(project.id),
        api.fetchMessages(project.id),
        api.fetchMemories(project.id),
        api.fetchUsers(project.id),
        api.fetchGitStatus(project.id)
      ]);

      setFiles(fileTree);
      setMessages(msgs);
      setMemories(mems);
      setConnectedUsers(users);
      setGitStatus(git);

      // Select calculator.py or main file if exists
      if (fileTree.length > 0) {
        const defaultFile = fileTree.find((f) => !f.is_directory);
        if (defaultFile) {
          openFile(project.id, defaultFile.path);
        }
      }
    } catch (e) {
      console.error('Error loading project details:', e);
    }
  };

  // WebSocket Connection Lifecycle
  useEffect(() => {
    if (!currentProject) return;

    if (wsRef.current) {
      wsRef.current.close();
    }

    const wsUrl = `ws://127.0.0.1:8000/api/projects/${currentProject.id}/agent/stream?user_id=${currentUser.userId}&display_name=${encodeURIComponent(currentUser.displayName)}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('Connected to Summit WebSocket room:', currentProject.id);
    };

    ws.onmessage = (event) => {
      try {
        const appEvent: AppEvent = JSON.parse(event.data);
        handleAppEvent(appEvent);
      } catch (err) {
        console.error('Failed to parse WS message:', err);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed.');
    };

    return () => {
      ws.close();
    };
  }, [currentProject?.id, currentUser.userId]);

  const handleAppEvent = (evt: AppEvent) => {
    setEvents((prev) => [...prev, evt]);

    switch (evt.type) {
      case 'agent_status':
        if (evt.data.status) {
          setAgentStatus(evt.data.status);
        }
        break;

      case 'user_joined':
      case 'user_left':
        if (evt.data.connected_users) {
          setConnectedUsers(evt.data.connected_users);
        }
        break;

      case 'user_message':
        setMessages((prev) => [
          ...prev,
          {
            id: evt.id,
            project_id: evt.project_id,
            user_id: evt.data.user_id,
            user_name: evt.data.user_name,
            role: 'user',
            content: evt.data.message,
            timestamp: evt.timestamp
          }
        ]);
        break;

      case 'agent_message':
        setMessages((prev) => [
          ...prev,
          {
            id: evt.id,
            project_id: evt.project_id,
            role: 'assistant',
            content: evt.data.message,
            timestamp: evt.timestamp
          }
        ]);
        break;

      case 'file_changed':
      case 'file_created':
      case 'file_deleted':
        if (currentProject) {
          api.fetchFiles(currentProject.id).then(setFiles);
          api.fetchGitStatus(currentProject.id).then(setGitStatus);

          // Refresh currently open active file if changed by someone else or agent
          if (activeFile && evt.data.path === activeFile.path) {
            openFile(currentProject.id, activeFile.path);
          }
        }
        break;

      case 'file_conflict':
        setConflictData(evt.data as FileConflictData);
        break;

      case 'memory_updated':
        if (currentProject) {
          api.fetchMemories(currentProject.id).then(setMemories);
        }
        break;

      case 'git_checkpoint':
        if (currentProject) {
          api.fetchGitStatus(currentProject.id).then(setGitStatus);
        }
        break;

      default:
        break;
    }
  };

  const openFile = async (projectId: string, path: string) => {
    try {
      const fileData = await api.readFile(projectId, path);
      setActiveFile(fileData);
    } catch (e) {
      console.error(`Error opening ${path}:`, e);
    }
  };

  const handleSaveFile = async (path: string, content: string, expectedVersion: number) => {
    if (!currentProject) return;
    setIsSaving(true);
    try {
      const result = await api.updateFile(currentProject.id, path, content, expectedVersion, currentUser.userId);
      setActiveFile((prev) => (prev ? { ...prev, content, version: result.version, size: content.length } : null));
    } catch (e: any) {
      if (e.conflictData) {
        setConflictData(e.conflictData);
      } else {
        alert(e.message || 'Failed to save file');
      }
    } finally {
      setIsSaving(false);
    }
  };

  const handleCreateFile = async (path: string) => {
    if (!currentProject) return;
    try {
      await api.updateFile(currentProject.id, path, '# New File\n');
      const updatedFiles = await api.fetchFiles(currentProject.id);
      setFiles(updatedFiles);
      openFile(currentProject.id, path);
    } catch (e) {
      alert('Failed to create file');
    }
  };

  const handleDeleteFile = async (path: string) => {
    if (!currentProject) return;
    try {
      await api.deleteFile(currentProject.id, path);
      const updatedFiles = await api.fetchFiles(currentProject.id);
      setFiles(updatedFiles);
      if (activeFile?.path === path) setActiveFile(null);
    } catch (e) {
      alert('Failed to delete file');
    }
  };

  const handleSendMessage = async (msg: string) => {
    if (!currentProject) return;
    try {
      await api.sendAgentMessage(currentProject.id, msg, currentUser.userId, currentUser.displayName);
    } catch (e: any) {
      alert(e.message);
    }
  };

  const handleCreateProject = async (name: string, template: string = 'blank') => {
    try {
      const newProj = await api.createProject(name, template);
      await loadProjects();
      selectProject(newProj);
    } catch (e) {
      alert('Failed to create project');
    }
  };


  const handleCreateMemory = async (key: string, value: string, category: string) => {
    if (!currentProject) return;
    try {
      await api.createMemory(currentProject.id, key, value, category);
      const mems = await api.fetchMemories(currentProject.id);
      setMemories(mems);
    } catch (e) {
      alert('Failed to create memory note');
    }
  };

  const handleDeleteMemory = async (keyOrId: string) => {
    if (!currentProject) return;
    try {
      await api.deleteMemory(currentProject.id, keyOrId);
      const mems = await api.fetchMemories(currentProject.id);
      setMemories(mems);
    } catch (e) {
      alert('Failed to delete memory');
    }
  };

  const handleFetchGitDiff = async () => {
    if (!currentProject) return;
    try {
      const diff = await api.fetchGitDiff(currentProject.id);
      setGitDiff(diff);
    } catch (e) {
      setGitDiff('Error loading diff');
    }
  };

  const handleCreateCheckpoint = async (msg: string) => {
    if (!currentProject) return;
    try {
      await api.createGitCheckpoint(currentProject.id, msg);
      const git = await api.fetchGitStatus(currentProject.id);
      setGitStatus(git);
    } catch (e) {
      alert('Failed to create git checkpoint');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', backgroundColor: 'var(--bg-dark)' }}>
      {/* Top Header */}
      <ProjectHeader
        projects={projects}
        currentProject={currentProject}
        onSelectProject={(id) => {
          const p = projects.find((x) => x.id === id);
          if (p) selectProject(p);
        }}
        onCreateProject={handleCreateProject}
        connectedUsers={connectedUsers}
        currentUser={currentUser}
        onSwitchUser={(userId, displayName) => setCurrentUser({ userId, displayName })}
      />

      {/* Main Workspace Layout */}
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {/* Left: File Explorer */}
        <FileExplorer
          files={files}
          activePath={activeFile?.path || null}
          onSelectFile={(p) => currentProject && openFile(currentProject.id, p)}
          onCreateFile={handleCreateFile}
          onDeleteFile={handleDeleteFile}
          onRefresh={() => currentProject && api.fetchFiles(currentProject.id).then(setFiles)}
        />

        {/* Center: Editor + Memory Drawer + Git Panel */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%' }}>
          {/* Memory Notes Drawer */}
          <MemoryPanel
            memories={memories}
            onCreateMemory={handleCreateMemory}
            onDeleteMemory={handleDeleteMemory}
          />

          {/* Monaco Code Editor & Live Web Preview */}
          <CodeEditor
            projectId={currentProject?.id || ''}
            activeFile={activeFile}
            onSave={handleSaveFile}
            isSaving={isSaving}
            hasIndexHtml={files.some((f) => f.name === 'index.html' || f.path.endsWith('index.html'))}
          />


          {/* Bottom Git Status Bar */}
          <GitPanel
            status={gitStatus}
            onFetchDiff={handleFetchGitDiff}
            diffContent={gitDiff}
            onCreateCheckpoint={handleCreateCheckpoint}
          />
        </div>

        {/* Right: Multiplayer AI Chat & Event Stream Panel */}
        <AgentPanel
          status={agentStatus}
          events={events}
          messages={messages}
          onSendMessage={handleSendMessage}
          onStop={() => currentProject && api.stopAgent(currentProject.id)}
          onPause={() => currentProject && api.pauseAgent(currentProject.id)}
          onResume={() => currentProject && api.resumeAgent(currentProject.id)}
        />
      </div>

      {/* Concurrent Editing Conflict Resolution Modal */}
      <ConflictModal
        conflict={conflictData}
        onAcceptServer={(_path, serverContent, serverVersion) => {

          setActiveFile((prev) => (prev ? { ...prev, content: serverContent, version: serverVersion } : null));
          setConflictData(null);
        }}
        onForceSave={async (path) => {
          if (activeFile && currentProject) {
            await api.updateFile(currentProject.id, path, activeFile.content, undefined, currentUser.userId);
            setConflictData(null);
            openFile(currentProject.id, path);
          }
        }}
        onDismiss={() => setConflictData(null)}
      />
    </div>
  );
};

export default App;

