import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.models.schemas import AppEvent, AppEventType, AgentStatusType


class EventNormalizer:
    """
    Normalizes agent actions, presence updates, file change events, and status transitions
    into clean, structured AppEvent payloads consumed by the WebSocket stream.
    """

    @staticmethod
    def create_event(
        project_id: str,
        event_type: AppEventType,
        data: Dict[str, Any],
        event_id: Optional[str] = None
    ) -> AppEvent:
        return AppEvent(
            id=event_id or str(uuid.uuid4()),
            project_id=project_id,
            type=event_type,
            timestamp=datetime.now(timezone.utc),
            data=data
        )

    @staticmethod
    def user_joined(project_id: str, user_id: str, display_name: str, connected_users: list) -> AppEvent:
        return EventNormalizer.create_event(
            project_id=project_id,
            event_type=AppEventType.USER_JOINED,
            data={
                "user_id": user_id,
                "display_name": display_name,
                "connected_users": connected_users
            }
        )

    @staticmethod
    def user_left(project_id: str, user_id: str, display_name: str, connected_users: list) -> AppEvent:
        return EventNormalizer.create_event(
            project_id=project_id,
            event_type=AppEventType.USER_LEFT,
            data={
                "user_id": user_id,
                "display_name": display_name,
                "connected_users": connected_users
            }
        )

    @staticmethod
    def user_message(project_id: str, message: str, user_id: Optional[str] = None, user_name: Optional[str] = None) -> AppEvent:
        return EventNormalizer.create_event(
            project_id=project_id,
            event_type=AppEventType.USER_MESSAGE,
            data={
                "message": message,
                "user_id": user_id,
                "user_name": user_name or "Developer"
            }
        )

    @staticmethod
    def agent_status(
        project_id: str,
        status: AgentStatusType,
        message: Optional[str] = None,
        action: Optional[str] = None
    ) -> AppEvent:
        return EventNormalizer.create_event(
            project_id=project_id,
            event_type=AppEventType.AGENT_STATUS,
            data={
                "status": status.value,
                "message": message,
                "action": action
            }
        )

    @staticmethod
    def tool_call(
        project_id: str,
        tool: str,
        args: Dict[str, Any],
        description: Optional[str] = None
    ) -> AppEvent:
        return EventNormalizer.create_event(
            project_id=project_id,
            event_type=AppEventType.TOOL_CALL,
            data={
                "tool": tool,
                "args": args,
                "description": description or f"Running {tool}"
            }
        )

    @staticmethod
    def tool_result(
        project_id: str,
        tool: str,
        result: Any,
        success: bool = True
    ) -> AppEvent:
        return EventNormalizer.create_event(
            project_id=project_id,
            event_type=AppEventType.TOOL_RESULT,
            data={
                "tool": tool,
                "result": result,
                "success": success
            }
        )

    @staticmethod
    def terminal_output(
        project_id: str,
        command: str,
        output: str,
        exit_code: int = 0
    ) -> AppEvent:
        return EventNormalizer.create_event(
            project_id=project_id,
            event_type=AppEventType.TERMINAL_OUTPUT,
            data={
                "command": command,
                "output": output,
                "exit_code": exit_code
            }
        )

    @staticmethod
    def file_changed(
        project_id: str,
        path: str,
        change_type: str = "modified",
        version: Optional[int] = None
    ) -> AppEvent:
        return EventNormalizer.create_event(
            project_id=project_id,
            event_type=AppEventType.FILE_CHANGED,
            data={
                "path": path.replace("\\", "/"),
                "change_type": change_type,
                "version": version
            }
        )

    @staticmethod
    def file_created(project_id: str, path: str) -> AppEvent:
        return EventNormalizer.create_event(
            project_id=project_id,
            event_type=AppEventType.FILE_CREATED,
            data={"path": path.replace("\\", "/")}
        )

    @staticmethod
    def file_deleted(project_id: str, path: str) -> AppEvent:
        return EventNormalizer.create_event(
            project_id=project_id,
            event_type=AppEventType.FILE_DELETED,
            data={"path": path.replace("\\", "/")}
        )

    @staticmethod
    def file_conflict(project_id: str, path: str, server_version: int, expected_version: int, server_content: str) -> AppEvent:
        return EventNormalizer.create_event(
            project_id=project_id,
            event_type=AppEventType.FILE_CONFLICT,
            data={
                "path": path.replace("\\", "/"),
                "server_version": server_version,
                "expected_version": expected_version,
                "server_content": server_content,
                "message": f"Conflict detected in {path}"
            }
        )

    @staticmethod
    def agent_message(
        project_id: str,
        message: str,
        thought: Optional[str] = None
    ) -> AppEvent:
        return EventNormalizer.create_event(
            project_id=project_id,
            event_type=AppEventType.AGENT_MESSAGE,
            data={
                "message": message,
                "thought": thought
            }
        )

    @staticmethod
    def memory_updated(project_id: str, key: str, value: str, category: str) -> AppEvent:
        return EventNormalizer.create_event(
            project_id=project_id,
            event_type=AppEventType.MEMORY_UPDATED,
            data={
                "key": key,
                "value": value,
                "category": category
            }
        )

    @staticmethod
    def git_checkpoint(project_id: str, commit_hash: str, message: str) -> AppEvent:
        return EventNormalizer.create_event(
            project_id=project_id,
            event_type=AppEventType.GIT_CHECKPOINT,
            data={
                "commit_hash": commit_hash,
                "message": message
            }
        )

    @staticmethod
    def error(
        project_id: str,
        error_message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> AppEvent:
        return EventNormalizer.create_event(
            project_id=project_id,
            event_type=AppEventType.ERROR,
            data={
                "error": error_message,
                "details": details or {}
            }
        )

    @staticmethod
    def session_complete(
        project_id: str,
        summary: Optional[str] = None
    ) -> AppEvent:
        return EventNormalizer.create_event(
            project_id=project_id,
            event_type=AppEventType.SESSION_COMPLETE,
            data={"summary": summary or "Summit Agent completed the session."}
        )
