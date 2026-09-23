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
    template: Optional[str] = Field("demo-calculator", description="Initial project template to seed")


class ProjectResponse(BaseModel):
    id: str
    name: str
    workspace_path: str
    created_at: datetime
    updated_at: datetime


class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]


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
