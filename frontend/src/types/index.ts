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
  | 'memory_saved'
  | 'presence_update'
  | 'git_checkpoint';

export interface Project {
  id: string;
  name: string;
  description?: string;
  workspace_path?: string;
  created_at?: string;
  updated_at?: string;
}

export interface FileNode {
  name: string;
  path: string;
  is_directory: boolean;
  size?: number;
  children?: FileNode[];
}

export interface OpenFile {
  path: string;
  content: string;
  originalContent?: string;
  language?: string;
  isDirty?: boolean;
  version?: number;
}

export interface ToolExecution {
  id?: string;
  tool?: string;
  name?: string;
  args?: Record<string, any>;
  arguments?: Record<string, any>;
  input?: any;
  result?: any;
  output?: string;
  status?: string;
  timestamp?: string;
}

export interface ChatMessage {
  id: string;
  sender?: 'user' | 'agent' | 'system';
  role?: string;
  text?: string;
  content?: string;
  thought?: string;
  timestamp: string;
  userName?: string;
  user_name?: string;
  toolExecutions?: ToolExecution[];
}

export interface AgentSessionStatus {
  status: string;
  currentStep?: string;
  current_action?: string;
  activeCommand?: string;
}

export interface CreateProjectPayload {
  name: string;
  description?: string;
  template?: string;
  root_path?: string;
}

export interface CreateMemoryPayload {
  key?: string;
  value?: string;
  content?: string;
  category?: string;
  importance?: string | number;
  memory_type?: string;
}

export interface ProjectListResponse {
  projects: Project[];
}

export interface ProjectSummary {
  id?: string;
  project_id?: string;
  content?: string;
  summary?: string;
  architecture_overview?: string;
  updated_at?: string;
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
  content?: string;
  importance?: string;
  created_at?: string;
  updated_at?: string;
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
