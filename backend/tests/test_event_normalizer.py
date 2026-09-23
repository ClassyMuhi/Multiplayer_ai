import pytest
from app.models.schemas import AppEventType, AgentStatusType
from app.agent.event_handler import EventNormalizer


def test_user_message_event():
    event = EventNormalizer.user_message(project_id="p1", message="Hello agent")
    assert event.project_id == "p1"
    assert event.type == AppEventType.USER_MESSAGE
    assert event.data["message"] == "Hello agent"


def test_agent_status_event():
    event = EventNormalizer.agent_status(
        project_id="p1",
        status=AgentStatusType.THINKING,
        action="Analyzing codebase"
    )
    assert event.type == AppEventType.AGENT_STATUS
    assert event.data["status"] == "THINKING"
    assert event.data["action"] == "Analyzing codebase"


def test_tool_call_and_result_events():
    call_evt = EventNormalizer.tool_call(
        project_id="p1",
        tool="read_file",
        args={"path": "calculator.py"}
    )
    assert call_evt.type == AppEventType.TOOL_CALL
    assert call_evt.data["tool"] == "read_file"

    res_evt = EventNormalizer.tool_result(
        project_id="p1",
        tool="read_file",
        result={"bytes": 100},
        success=True
    )
    assert res_evt.type == AppEventType.TOOL_RESULT
    assert res_evt.data["success"] is True


def test_file_changed_and_terminal_output_events():
    fc_evt = EventNormalizer.file_changed(project_id="p1", path="src/main.py")
    assert fc_evt.type == AppEventType.FILE_CHANGED
    assert fc_evt.data["path"] == "src/main.py"

    term_evt = EventNormalizer.terminal_output(
        project_id="p1",
        command="pytest",
        output="3 passed",
        exit_code=0
    )
    assert term_evt.type == AppEventType.TERMINAL_OUTPUT
    assert term_evt.data["exit_code"] == 0
    assert "3 passed" in term_evt.data["output"]
