from fastapi import APIRouter, HTTPException, status
from app.models.schemas import (
    GitStatusResponse,
    GitDiffResponse,
    GitCheckpointRequest,
    GitCheckpointResponse,
    GitRemoteResponse,
    GitSetRemoteRequest,
    GitCommitPushRequest,
    GitCommitPushResponse
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


@router.get("/remote", response_model=GitRemoteResponse)
def get_git_remote(project_id: str):
    """Get configured GitHub remote repository for project workspace."""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    ws_dir = workspace_manager.get_workspace_dir(project_id)
    return git_service.get_remote(ws_dir)


@router.post("/remote", response_model=GitRemoteResponse)
def set_git_remote(project_id: str, payload: GitSetRemoteRequest):
    """Connect project workspace to a GitHub remote repository."""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    ws_dir = workspace_manager.get_workspace_dir(project_id)
    return git_service.set_remote(ws_dir, payload.remote_url, payload.branch or "main")


@router.post("/commit-and-push", response_model=GitCommitPushResponse)
def commit_and_push(project_id: str, payload: GitCommitPushRequest):
    """Commit changes with a message and automatically push to GitHub."""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    ws_dir = workspace_manager.get_workspace_dir(project_id)
    result = git_service.commit_and_push(project_id, ws_dir, payload.message, payload.push)
    return GitCommitPushResponse(
        commit_hash=result["commit_hash"],
        message=result["message"],
        created_at=result["created_at"],
        pushed=result["pushed"],
        push_output=result["push_output"],
        success=result["success"]
    )


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
