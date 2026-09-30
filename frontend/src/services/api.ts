import {
  Project,
  ProjectListResponse,
  ProjectSummary,
  FileNode,
  FileContent,
  ProjectMemory,
  AgentSessionStatus,
  CreateProjectPayload,
  CreateMemoryPayload,
} from '../types';

const API_BASE = '/api';

class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options?.headers || {}),
    },
  });

  if (!response.ok) {
    let errorDetail = `Request failed with status ${response.status}`;
    try {
      const errData = await response.json();
      errorDetail = errData.detail || errData.message || errorDetail;
    } catch {
      // Non-JSON response
    }
    throw new ApiError(errorDetail, response.status);
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

export const apiService = {
  // --------------------------------------------------------------------------
  // PROJECTS
  // --------------------------------------------------------------------------
  async getProjects(): Promise<Project[]> {
    const data = await request<ProjectListResponse | Project[]>(`${API_BASE}/projects`);
    if (Array.isArray(data)) return data;
    return (data as ProjectListResponse).projects || [];
  },

  async getProject(projectId: string): Promise<Project> {
    return request<Project>(`${API_BASE}/projects/${encodeURIComponent(projectId)}`);
  },

  async createProject(payload: CreateProjectPayload | string, template?: string, description?: string): Promise<Project> {
    const body = typeof payload === 'string'
      ? { name: payload, template: template || 'demo-calculator', description }
      : {
          name: payload.name,
          template: payload.template || 'demo-calculator',
          description: payload.description,
          root_path: payload.root_path,
        };

    return request<Project>(`${API_BASE}/projects`, {
      method: 'POST',
      body: JSON.stringify(body),
    });
  },

  async getProjectSummary(projectId: string): Promise<ProjectSummary> {
    const data = await request<any>(`${API_BASE}/projects/${encodeURIComponent(projectId)}/summary`);
    return {
      project_id: projectId,
      summary: data.summary || data.content || '',
      content: data.summary || data.content || '',
      updated_at: data.updated_at,
    };
  },

  async updateProjectSummary(projectId: string, summary: string): Promise<ProjectSummary> {
    const data = await request<any>(`${API_BASE}/projects/${encodeURIComponent(projectId)}/summary`, {
      method: 'PUT',
      body: JSON.stringify({ summary }),
    });
    return {
      project_id: projectId,
      summary: data.summary || data.content || summary,
      content: data.summary || data.content || summary,
      updated_at: data.updated_at,
    };
  },

  async refreshProjectSummary(projectId: string): Promise<ProjectSummary> {
    const data = await request<any>(`${API_BASE}/projects/${encodeURIComponent(projectId)}/summary/refresh`, {
      method: 'POST',
    });
    return {
      project_id: projectId,
      summary: data.summary || data.content || '',
      content: data.summary || data.content || '',
      updated_at: data.updated_at,
    };
  },

  // --------------------------------------------------------------------------
  // FILES & WORKSPACE
  // --------------------------------------------------------------------------
  async getFileTree(projectId: string): Promise<FileNode[]> {
    return request<FileNode[]>(`${API_BASE}/projects/${encodeURIComponent(projectId)}/files`);
  },

  async getFileContent(projectId: string, filePath: string): Promise<FileContent> {
    return request<FileContent>(`${API_BASE}/projects/${encodeURIComponent(projectId)}/files/${filePath}`);
  },

  async saveFile(projectId: string, filePath: string, content: string): Promise<{ success: boolean; path: string }> {
    return request<{ success: boolean; path: string }>(
      `${API_BASE}/projects/${encodeURIComponent(projectId)}/files/${filePath}`,
      {
        method: 'PUT',
        body: JSON.stringify({ content }),
      }
    );
  },

  async createFile(projectId: string, filePath: string, content: string = ''): Promise<{ success: boolean; path: string }> {
    return request<{ success: boolean; path: string }>(
      `${API_BASE}/projects/${encodeURIComponent(projectId)}/files/${filePath}`,
      {
        method: 'POST',
        body: JSON.stringify({ content }),
      }
    );
  },

  async deleteFile(projectId: string, filePath: string): Promise<{ success: boolean }> {
    return request<{ success: boolean }>(
      `${API_BASE}/projects/${encodeURIComponent(projectId)}/files/${filePath}`,
      {
        method: 'DELETE',
      }
    );
  },

  // --------------------------------------------------------------------------
  // AGENT
  // --------------------------------------------------------------------------
  async getAgentStatus(projectId: string): Promise<AgentSessionStatus> {
    return request<AgentSessionStatus>(`${API_BASE}/projects/${encodeURIComponent(projectId)}/agent/status`);
  },

  async sendAgentMessage(projectId: string, message: string): Promise<{ status: string; message: string }> {
    return request<{ status: string; message: string }>(
      `${API_BASE}/projects/${encodeURIComponent(projectId)}/agent/message`,
      {
        method: 'POST',
        body: JSON.stringify({ message }),
      }
    );
  },

  async stopAgent(projectId: string): Promise<{ success: boolean; message: string }> {
    return request<{ success: boolean; message: string }>(
      `${API_BASE}/projects/${encodeURIComponent(projectId)}/agent/stop`,
      {
        method: 'POST',
      }
    );
  },

  // --------------------------------------------------------------------------
  // PERSISTENT PROJECT MEMORY
  // --------------------------------------------------------------------------
  async getMemories(projectId: string, category?: string): Promise<ProjectMemory[]> {
    const query = category ? `?category=${encodeURIComponent(category)}` : '';
    const data = await request<any[]>(`${API_BASE}/projects/${encodeURIComponent(projectId)}/memory${query}`);
    return data.map((item) => ({
      ...item,
      content: item.content || item.value || '',
    }));
  },

  async searchMemories(projectId: string, query: string, topK: number = 5): Promise<ProjectMemory[]> {
    const data = await request<any[]>(
      `${API_BASE}/projects/${encodeURIComponent(projectId)}/memory/search`,
      {
        method: 'POST',
        body: JSON.stringify({ query, top_k: topK }),
      }
    );
    return data.map((item) => ({
      ...item,
      content: item.content || item.value || '',
    }));
  },

  async createMemory(projectId: string, payload: CreateMemoryPayload): Promise<ProjectMemory> {
    return request<ProjectMemory>(`${API_BASE}/projects/${encodeURIComponent(projectId)}/memory`, {
      method: 'POST',
      body: JSON.stringify({
        content: payload.content,
        category: payload.category || 'architecture',
        importance: payload.importance ?? 3,
        memory_type: payload.memory_type || 'architecture_decision',
        key: payload.key,
      }),
    });
  },

  async deleteMemory(projectId: string, memoryId: string): Promise<{ success: boolean }> {
    return request<{ success: boolean }>(
      `${API_BASE}/projects/${encodeURIComponent(projectId)}/memory/${encodeURIComponent(memoryId)}`,
      {
        method: 'DELETE',
      }
    );
  },
};

export const api = apiService;
