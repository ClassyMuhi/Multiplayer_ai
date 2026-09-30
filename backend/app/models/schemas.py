from enum import Enum
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime, timezone


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class AgentStatusType(str, Enum):
    IDLE = "IDLE"
    THINKING = "THINKING"
    EXECUTING = "EXECUTING"
    WAITING = "WAITING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class AppEventType(str, Enum):
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    USER_MESSAGE = "user_message"
    AGENT_STATUS = "agent_status"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    FILE_CHANGED = "file_changed"
    FILE_CREATED = "file_created"
    FILE_DELETED = "file_deleted"
    FILE_CONFLICT = "file_conflict"
    TERMINAL_OUTPUT = "terminal_output"
    AGENT_MESSAGE = "agent_message"
    ERROR = "error"
    SESSION_COMPLETE = "session_complete"
    MEMORY_UPDATED = "memory_updated"
    GIT_CHECKPOINT = "git_checkpoint"


# --- Project Schemas ---
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


# --- File Schemas ---
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
    version: int = 1


class FileUpdateRequest(BaseModel):
    content: str
    expected_version: Optional[int] = None
    user_id: Optional[str] = None


class FileConflictResponse(BaseModel):
    conflict: bool = True
    path: str
    server_version: int
    expected_version: int
    server_content: str
    message: str = "File has been modified by another user or agent."


class FileOperationResponse(BaseModel):
    success: bool
    path: str
    message: Optional[str] = None
    version: Optional[int] = None


# --- User Presence Schemas ---
class UserPresenceInfo(BaseModel):
    user_id: str
    display_name: str
    connected_at: datetime = Field(default_factory=now_utc)


class UserPresenceListResponse(BaseModel):
    users: List[UserPresenceInfo]


# --- Agent & Conversation Schemas ---
class AgentMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Instruction or query for Summit agent")
    user_id: Optional[str] = None
    display_name: Optional[str] = None


class MessageRecord(BaseModel):
    id: str
    project_id: str
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    role: str
    content: str
    timestamp: datetime


class MessageListResponse(BaseModel):
    messages: List[MessageRecord]


class AgentStopResponse(BaseModel):
    success: bool
    message: str


class AgentSessionStatus(BaseModel):
    project_id: str
    status: AgentStatusType
    current_action: Optional[str] = None
    active_tools: List[str] = []
    updated_at: datetime = Field(default_factory=now_utc)


# --- Project Memory Schemas ---
class ProjectMemoryItem(BaseModel):
    id: str
    project_id: str
    category: str
    key: str
    value: str
    updated_at: datetime


class ProjectMemoryCreate(BaseModel):
    key: str = Field(..., min_length=1)
    value: str = Field(..., min_length=1)
    category: Optional[str] = Field("general", description="e.g. architecture, decision, task, convention")


class ProjectMemoryListResponse(BaseModel):
    memories: List[ProjectMemoryItem]


# --- Git Schemas ---
class GitStatusResponse(BaseModel):
    branch: str
    modified: List[str]
    staged: List[str]
    untracked: List[str]
    is_clean: bool


class GitDiffResponse(BaseModel):
    diff: str


class GitCheckpointRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Checkpoint / commit message")


class GitCheckpointResponse(BaseModel):
    commit_hash: str
    message: str
    created_at: datetime


# --- Event Stream Schema ---
class AppEvent(BaseModel):
    id: str
    project_id: str
    type: AppEventType
    timestamp: datetime = Field(default_factory=now_utc)
    data: Dict[str, Any] = Field(default_factory=dict)
