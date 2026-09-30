from fastapi import APIRouter, HTTPException, status
from app.models.schemas import (
    GitStatusResponse,
    GitDiffResponse,
    GitCheckpointRequest,
    GitCheckpointResponse
)
from app.git.git_service import git_service
from app.workspace.manager import workspace_manager
from app.services.project_service import project_service

router = APIRouter(prefix="/api/projects/{project_id}/git", tags=["git"])


@router.get("/status", response_model=GitStatusResponse)
def get_git_status(project_id: str):
    """Get local git repository status for project workspace."""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    ws_dir = workspace_manager.get_workspace_dir(project_id)
    return git_service.get_status(ws_dir)


@router.get("/diff", response_model=GitDiffResponse)
def get_git_diff(project_id: str):
    """Get working directory git diff for project workspace."""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    ws_dir = workspace_manager.get_workspace_dir(project_id)
    diff = git_service.get_diff(ws_dir)
    return GitDiffResponse(diff=diff)


@router.post("/checkpoint", response_model=GitCheckpointResponse)
def create_checkpoint(project_id: str, payload: GitCheckpointRequest):
    """Create a local git checkpoint commit."""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    ws_dir = workspace_manager.get_workspace_dir(project_id)
    chk = git_service.create_checkpoint(project_id, ws_dir, payload.message)
    return GitCheckpointResponse(
        commit_hash=chk["commit_hash"],
        message=chk["message"],
        created_at=chk["created_at"]
    )
