import type {
  Project,
  FileNode,
  FileContent,
  MessageRecord,
  ProjectMemory,
  UserPresence,
  GitStatus,
  GitCheckpoint
} from '../types';


const API_BASE = 'http://127.0.0.1:8000/api';

export async function fetchProjects(): Promise<Project[]> {
  const res = await fetch(`${API_BASE}/projects`);
  if (!res.ok) throw new Error('Failed to fetch projects');
  const data = await res.json();
  return data.projects;
}

export async function createProject(name: string, template: string = 'blank'): Promise<Project> {
  const res = await fetch(`${API_BASE}/projects`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, template })
  });
  if (!res.ok) throw new Error('Failed to create project');
  return res.json();
}


export async function fetchFiles(projectId: string): Promise<FileNode[]> {
  const res = await fetch(`${API_BASE}/projects/${projectId}/files`);
  if (!res.ok) throw new Error('Failed to fetch files');
  return res.json();
}

export async function readFile(projectId: string, path: string): Promise<FileContent> {
  const res = await fetch(`${API_BASE}/projects/${projectId}/files/${encodeURIComponent(path)}`);
  if (!res.ok) throw new Error('Failed to read file');
  return res.json();
}

export async function updateFile(
  projectId: string,
  path: string,
  content: string,
  expectedVersion?: number,
  userId?: string
): Promise<{ success: boolean; path: string; version: number; message: string }> {
  const res = await fetch(`${API_BASE}/projects/${projectId}/files/${encodeURIComponent(path)}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, expected_version: expectedVersion, user_id: userId })
  });

  if (res.status === 409) {
    const errorData = await res.json();
    const detail = errorData.detail || errorData;
    const err = new Error(detail.message || 'File conflict detected');
    (err as any).conflictData = detail;
    throw err;
  }

  if (!res.ok) throw new Error('Failed to update file');
  return res.json();
}

export async function deleteFile(projectId: string, path: string): Promise<void> {
  const res = await fetch(`${API_BASE}/projects/${projectId}/files/${encodeURIComponent(path)}`, {
    method: 'DELETE'
  });
  if (!res.ok) throw new Error('Failed to delete file');
}

export async function fetchMessages(projectId: string): Promise<MessageRecord[]> {
  const res = await fetch(`${API_BASE}/projects/${projectId}/messages`);
  if (!res.ok) throw new Error('Failed to fetch messages');
  const data = await res.json();
  return data.messages;
}

export async function fetchMemories(projectId: string): Promise<ProjectMemory[]> {
  const res = await fetch(`${API_BASE}/projects/${projectId}/memory`);
  if (!res.ok) throw new Error('Failed to fetch memories');
  const data = await res.json();
  return data.memories;
}

export async function createMemory(
  projectId: string,
  key: string,
  value: string,
  category: string = 'general'
): Promise<ProjectMemory> {
  const res = await fetch(`${API_BASE}/projects/${projectId}/memory`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ key, value, category })
  });
  if (!res.ok) throw new Error('Failed to create memory');
  return res.json();
}

export async function deleteMemory(projectId: string, keyOrId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/projects/${projectId}/memory/${encodeURIComponent(keyOrId)}`, {
    method: 'DELETE'
  });
  if (!res.ok) throw new Error('Failed to delete memory');
}

export async function fetchUsers(projectId: string): Promise<UserPresence[]> {
  const res = await fetch(`${API_BASE}/projects/${projectId}/users`);
  if (!res.ok) throw new Error('Failed to fetch users');
  const data = await res.json();
  return data.users;
}

export async function fetchGitStatus(projectId: string): Promise<GitStatus> {
  const res = await fetch(`${API_BASE}/projects/${projectId}/git/status`);
  if (!res.ok) throw new Error('Failed to fetch git status');
  return res.json();
}

export async function fetchGitDiff(projectId: string): Promise<string> {
  const res = await fetch(`${API_BASE}/projects/${projectId}/git/diff`);
  if (!res.ok) throw new Error('Failed to fetch git diff');
  const data = await res.json();
  return data.diff;
}

export async function fetchGitRemote(projectId: string): Promise<{ remote_url: string | null; has_remote: boolean; branch?: string }> {
  const res = await fetch(`${API_BASE}/projects/${projectId}/git/remote`);
  if (!res.ok) throw new Error('Failed to fetch git remote');
  return res.json();
}

export async function setGitRemote(projectId: string, remoteUrl: string, branch: string = 'main'): Promise<{ remote_url: string; has_remote: boolean; branch: string }> {
  const res = await fetch(`${API_BASE}/projects/${projectId}/git/remote`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ remote_url: remoteUrl, branch })
  });
  if (!res.ok) throw new Error('Failed to set git remote');
  return res.json();
}

export async function commitAndPush(projectId: string, message: string, push: boolean = true): Promise<{
  commit_hash: string;
  message: string;
  created_at: string;
  pushed: boolean;
  push_output: string;
  success: boolean;
}> {
  const res = await fetch(`${API_BASE}/projects/${projectId}/git/commit-and-push`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, push })
  });
  if (!res.ok) throw new Error('Failed to commit and push');
  return res.json();
}

export async function createGitCheckpoint(projectId: string, message: string): Promise<GitCheckpoint> {
  const res = await fetch(`${API_BASE}/projects/${projectId}/git/checkpoint`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  });
  if (!res.ok) throw new Error('Failed to create checkpoint');
  return res.json();
}

export async function sendAgentMessage(
  projectId: string,
  message: string,
  userId?: string,
  displayName?: string,
  model?: string
): Promise<void> {
  const res = await fetch(`${API_BASE}/projects/${projectId}/agent/message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, user_id: userId, display_name: displayName, model })
  });
  if (!res.ok) {
    const data = await res.json();
    throw new Error(data.detail || 'Failed to send message to agent');
  }
}

export async function stopAgent(projectId: string): Promise<void> {
  await fetch(`${API_BASE}/projects/${projectId}/agent/stop`, { method: 'POST' });
}

export async function pauseAgent(projectId: string): Promise<void> {
  await fetch(`${API_BASE}/projects/${projectId}/agent/pause`, { method: 'POST' });
}

export async function resumeAgent(projectId: string): Promise<void> {
  await fetch(`${API_BASE}/projects/${projectId}/agent/resume`, { method: 'POST' });
}

export async function executeTerminalCommand(
  projectId: string,
  command: string,
  cwd?: string
): Promise<{ command: string; output: string; exit_code: number; cwd: string }> {
  const res = await fetch(`${API_BASE}/projects/${projectId}/terminal/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ command, cwd })
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || 'Terminal execution failed');
  }
  return res.json();
}
