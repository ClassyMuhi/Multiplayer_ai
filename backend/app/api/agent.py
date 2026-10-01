import asyncio
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import (
    AgentMessageRequest,
    AgentSessionStatus,
    AgentStopResponse,
    AgentStatusType
)
from app.services.project_service import project_service
from app.agent.session_manager import session_manager
from app.agent.summit_adapter import summit_adapter

router = APIRouter(prefix="/api/projects/{project_id}/agent", tags=["agent"])


@router.get("/status", response_model=AgentSessionStatus)
def get_agent_status(project_id: str):
    """Get current status of the Summit agent for this project."""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return session_manager.get_status(project_id)


@router.post("/message")
async def send_agent_message(
    project_id: str,
    payload: AgentMessageRequest
):
    """
    Send a prompt/instruction to the shared Summit AI Agent.
    Launches agent reasoning & execution loop, streaming events to all room users.
    """
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if session_manager.is_running(project_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Agent is currently busy processing another task. Please wait or stop the session."
        )

    task = asyncio.create_task(
        summit_adapter.run_session(
            project_id=project_id,
            user_prompt=payload.message,
            user_id=payload.user_id,
            user_name=payload.display_name,
            model_override=payload.model
        )
    )
    session_manager.set_running_task(project_id, task)

    return {
        "status": "started",
        "project_id": project_id,
        "message": payload.message
    }


@router.post("/stop", response_model=AgentStopResponse)
def stop_agent_session(project_id: str):
    """Stops/cancels active Summit agent execution."""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    stopped = session_manager.stop_session(project_id)
    if stopped:
        return AgentStopResponse(success=True, message="Agent session stopped successfully.")
    return AgentStopResponse(success=False, message="No active agent session was running.")


@router.post("/pause", response_model=AgentStopResponse)
def pause_agent_session(project_id: str):
    """Pauses active Summit agent execution."""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    paused = session_manager.pause_session(project_id)
    if paused:
        return AgentStopResponse(success=True, message="Agent session paused.")
    return AgentStopResponse(success=False, message="Could not pause (session not running or already paused).")


@router.post("/resume", response_model=AgentStopResponse)
def resume_agent_session(project_id: str):
    """Resumes paused Summit agent execution."""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    resumed = session_manager.resume_session(project_id)
    if resumed:
        return AgentStopResponse(success=True, message="Agent session resumed.")
    return AgentStopResponse(success=False, message="Could not resume (session not paused).")
