import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.models.schemas import AppEvent, AppEventType, AgentStatusType


class EventNormalizer:
    """
    Normalizes internal Summit / OpenHands agent actions, observations,
    and status transitions into clean, structured AppEvent payloads
    consumed by the frontend WebSocket stream.
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
    def user_message(project_id: str, message: str) -> AppEvent:
        return EventNormalizer.create_event(
            project_id=project_id,
            event_type=AppEventType.USER_MESSAGE,
            data={"message": message}
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
        change_type: str = "modified"
    ) -> AppEvent:
        return EventNormalizer.create_event(
            project_id=project_id,
            event_type=AppEventType.FILE_CHANGED,
            data={
                "path": path.replace("\\", "/"),
                "change_type": change_type
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
