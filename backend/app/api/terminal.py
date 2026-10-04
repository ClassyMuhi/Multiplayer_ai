import asyncio
import os
import sys
import subprocess
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status

from app.workspace.manager import workspace_manager, WorkspaceNotFoundError, WorkspaceSecurityError
from app.agent.session_manager import session_manager
from app.agent.event_handler import EventNormalizer

router = APIRouter(prefix="/api/projects/{project_id}/terminal", tags=["terminal"])


class TerminalExecuteRequest(BaseModel):
    command: str
    cwd: Optional[str] = None


class TerminalExecuteResponse(BaseModel):
    command: str
    output: str
    exit_code: int
    cwd: str


def _sync_run_command(cmd: str, target_cwd: str) -> tuple[int, str]:
    """Synchronous subprocess execution safe on all OS and event loops."""
    try:
        proc = subprocess.run(
            cmd,
            shell=True,
            cwd=target_cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=30.0,
            encoding="utf-8",
            errors="replace"
        )
        return proc.returncode, proc.stdout or ""
    except subprocess.TimeoutExpired:
        return 124, "[Process timed out after 30 seconds]"
    except Exception as exc:
        return 1, f"Execution failed: {str(exc)}"


@router.post("/execute", response_model=TerminalExecuteResponse)
async def execute_terminal_command(project_id: str, request: TerminalExecuteRequest):
    """
    Executes a real shell command within the project workspace directory
    and returns its stdout, stderr, and exit status.
    """
    cmd = request.command.strip()
    if not cmd:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Command cannot be empty")

    try:
        workspace_dir = workspace_manager.ensure_workspace(project_id)
    except (WorkspaceNotFoundError, WorkspaceSecurityError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # Resolve working directory
    target_cwd = workspace_dir
    if request.cwd:
        candidate = (workspace_dir / request.cwd).resolve()
        try:
            candidate.relative_to(workspace_dir)
            if candidate.is_dir():
                target_cwd = candidate
        except ValueError:
            pass

    # Broadcast tool call event
    await session_manager.broadcast_event(
        project_id,
        EventNormalizer.tool_call(
            project_id=project_id,
            tool="terminal",
            args={"command": cmd, "cwd": str(target_cwd)},
            description=f"Terminal: {cmd}"
        )
    )

    try:
        exit_code, output = await asyncio.to_thread(_sync_run_command, cmd, str(target_cwd))

        # Broadcast terminal output
        await session_manager.broadcast_event(
            project_id,
            EventNormalizer.terminal_output(
                project_id=project_id,
                command=cmd,
                output=output,
                exit_code=exit_code
            )
        )

        return TerminalExecuteResponse(
            command=cmd,
            output=output,
            exit_code=exit_code,
            cwd=str(target_cwd)
        )

    except Exception as e:
        err_msg = f"Failed to execute command: {str(e)}"
        return TerminalExecuteResponse(
            command=cmd,
            output=err_msg,
            exit_code=1,
            cwd=str(target_cwd)
        )
