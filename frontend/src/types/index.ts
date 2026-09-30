export type AgentStatusType =
  | 'IDLE'
  | 'THINKING'
  | 'EXECUTING'
  | 'WAITING'
  | 'COMPLETED'
  | 'ERROR'
  | 'STOPPED'
  | 'idle'
  | 'thinking'
  | 'working'
  | 'running_command'
  | 'completed'
  | 'stopped'
  | 'error';

export type AppEventType =
  | 'user_message'
  | 'agent_status'
  | 'tool_call'
  | 'tool_result'
  | 'file_changed'
  | 'terminal_output'
  | 'agent_message'
  | 'error'
  | 'agent_error'
  | 'session_complete'
  | 'memory_saved'
  | 'presence_update';

export interface Project {
  id: string;
  name: string;
  description?: string | null;
  project_summary?: string | null;
  workspace_path: string;
  created_at: string;
  updated_at: string;
}

export interface CreateProjectPayload {
  name: string;
  description?: string;
  template?: string;
  root_path?: string;
}

export interface ProjectListResponse {
  projects: Project[];
}

export interface ProjectSummary {
  project_id: string;
  summary?: string | null;
  content?: string | null;
  updated_at?: string | null;
}

export interface FileNode {
  name: string;
  path: string; // relative path inside workspace
  is_directory: boolean;
  size?: number | null;
  children?: FileNode[] | null;
}

export interface FileContent {
  path: string;
  content: string;
  size: number;
  is_binary: boolean;
}

export interface OpenFile {
  path: string;
  content: string;
  originalContent: string;
  isDirty: boolean;
}

export interface ProjectMemory {
  id: string;
  project_id: string;
  memory_type?: string;
  key?: string | null;
  value?: string;
  content?: string | null;
  category?: string | null;
  source?: string | null;
  created_by?: string | null;
  importance?: number | null;
  similarity_score?: number | null;
  is_active?: boolean;
  created_at: string;
  updated_at?: string;
}

export interface CreateMemoryPayload {
  content: string;
  category?: string;
  importance?: number;
  memory_type?: string;
  key?: string;
}

export interface ToolExecution {
  name: string;
  input?: any;
  output?: string;
  status: 'running' | 'completed' | 'error';
}

export interface AgentSessionStatus {
  status: AgentStatusType;
  current_action?: string | null;
  currentStep?: string | null;
  activeCommand?: string | null;
  active_tools?: string[];
  updated_at?: string;
}

export interface AppEvent {
  id?: string;
  project_id?: string;
  type: AppEventType;
  timestamp: string;
  data: any;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  userName?: string;
  thought?: string;
  toolExecutions?: ToolExecution[];
}

export interface DeveloperSession {
  user_id: string;
  user_name: string;
  is_current_user?: boolean;
  joined_at: string;
}
