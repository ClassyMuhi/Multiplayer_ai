export type AgentStatusType = 'IDLE' | 'THINKING' | 'EXECUTING' | 'WAITING' | 'PAUSED' | 'COMPLETED' | 'ERROR';

export type AppEventType =
  | 'user_joined'
  | 'user_left'
  | 'user_message'
  | 'agent_status'
  | 'tool_call'
  | 'tool_result'
  | 'file_changed'
  | 'file_created'
  | 'file_deleted'
  | 'file_conflict'
  | 'terminal_output'
  | 'agent_message'
  | 'error'
  | 'session_complete'
  | 'memory_updated'
  | 'git_checkpoint';

export interface Project {
  id: string;
  name: string;
  workspace_path: string;
  created_at: string;
  updated_at: string;
}

export interface FileNode {
  name: string;
  path: string;
  is_directory: boolean;
  size?: number;
  children?: FileNode[];
}


export interface FileContent {
  path: string;
  content: string;
  size: number;
  is_binary: boolean;
  version: number;
}

export interface UserPresence {
  user_id: string;
  display_name: string;
  connected_at: string;
}

export interface MessageRecord {
  id: string;
  project_id: string;
  user_id?: string;
  user_name?: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
}

export interface ProjectMemory {
  id: string;
  project_id: string;
  category: string;
  key: string;
  value: string;
  updated_at: string;
}

export interface GitStatus {
  branch: string;
  modified: string[];
  staged: string[];
  untracked: string[];
  is_clean: boolean;
}

export interface GitCheckpoint {
  id: string;
  commit_hash: string;
  message: string;
  created_at: string;
}

export interface AppEvent {
  id: string;
  project_id: string;
  type: AppEventType;
  timestamp: string;
  data: Record<string, any>;
}

export interface FileConflictData {
  path: string;
  server_version: number;
  expected_version: number;
  server_content: string;
  message: string;
}
