from enum import Enum
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class AgentStatusType(str, Enum):
    IDLE = "IDLE"
    THINKING = "THINKING"
    EXECUTING = "EXECUTING"
    WAITING = "WAITING"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class AppEventType(str, Enum):
    USER_MESSAGE = "user_message"
    AGENT_STATUS = "agent_status"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    FILE_CHANGED = "file_changed"
    TERMINAL_OUTPUT = "terminal_output"
    AGENT_MESSAGE = "agent_message"
    ERROR = "error"
    SESSION_COMPLETE = "session_complete"


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Project display name")
    description: Optional[str] = Field(None, description="Optional project description")
    template: Optional[str] = Field("demo-calculator", description="Initial project template to seed")


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    workspace_path: str
    created_at: datetime
    updated_at: datetime


class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]


class UserCreate(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=100)


class UserResponse(BaseModel):
    id: str
    display_name: str
    created_at: datetime


class ProjectMemberResponse(BaseModel):
    id: str
    project_id: str
    user_id: str
    joined_at: datetime


class MessageRecord(BaseModel):
    id: str
    project_id: str
    role: str
    content: str
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    created_at: datetime


class ProjectMemoryItem(BaseModel):
    id: str
    project_id: str
    memory_type: str = "general"
    key: Optional[str] = None
    value: str
    content: Optional[str] = None
    category: Optional[str] = "general"
    source: Optional[str] = None
    created_by: Optional[str] = None
    is_active: bool = True
    similarity_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime


class ProjectMemoryCreate(BaseModel):
    content: Optional[str] = None
    value: Optional[str] = None
    memory_type: Optional[str] = "general"
    category: Optional[str] = "general"
    key: Optional[str] = None
    source: Optional[str] = None
    created_by: Optional[str] = None


class MemorySearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Semantic search query")
    top_k: Optional[int] = Field(5, ge=1, le=20, description="Max memories to retrieve")
    relevance_threshold: Optional[float] = Field(None, description="Optional distance threshold")
    category: Optional[str] = Field(None, description="Optional category filter")



class AgentRunResponse(BaseModel):
    id: str
    project_id: str
    prompt: str
    initiated_by: Optional[str] = None
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None


class FileChangeRecord(BaseModel):
    id: str
    project_id: str
    file_path: str
    operation: str
    user_id: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime



class FileNode(BaseModel):
    name: str
    path: str  # relative path inside workspace
    is_directory: bool
    size: Optional[int] = None
    children: Optional[List["FileNode"]] = None


FileNode.model_rebuild()


class FileContentResponse(BaseModel):
    path: str
    content: str
    size: int
    is_binary: bool = False


class FileUpdateRequest(BaseModel):
    content: str


class FileOperationResponse(BaseModel):
    success: bool
    path: str
    message: Optional[str] = None


class AgentMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Instruction or query for Summit agent")


class AgentStopResponse(BaseModel):
    success: bool
    message: str


class AgentSessionStatus(BaseModel):
    project_id: str
    status: AgentStatusType
    current_action: Optional[str] = None
    active_tools: List[str] = []
    updated_at: datetime


class AppEvent(BaseModel):
    id: str
    project_id: str
    type: AppEventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = Field(default_factory=dict)
