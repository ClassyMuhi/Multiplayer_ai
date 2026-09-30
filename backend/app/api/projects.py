from fastapi import APIRouter, HTTPException, status
from app.models.schemas import (
    ProjectCreate,
    ProjectResponse,
    ProjectListResponse,
    ProjectSummaryResponse,
    ProjectSummaryUpdate
)
from app.services.project_service import project_service
from app.workspace.manager import WorkspaceSecurityError, WorkspaceNotFoundError

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=ProjectListResponse)
def list_projects():
    """List all available workspaces/projects."""
    return project_service.list_projects()


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate):
    """Create a new project workspace."""
    try:
        return project_service.create_project(name=payload.name, template=payload.template)
    except WorkspaceSecurityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create project: {e}")


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str):
    """Retrieve details for a specific project workspace."""
    try:
        project = project_service.get_project(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")
        return project
    except WorkspaceSecurityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{project_id}/summary", response_model=ProjectSummaryResponse)
def get_project_summary(project_id: str):
    """Retrieve the high-level project summary."""
    try:
        project = project_service.get_project(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")
        summary = project_service.get_project_summary(project_id)
        return ProjectSummaryResponse(
            project_id=project_id,
            summary=summary,
            updated_at=project.updated_at
        )
    except WorkspaceSecurityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{project_id}/summary", response_model=ProjectSummaryResponse)
def update_project_summary(project_id: str, payload: ProjectSummaryUpdate):
    """Manually update the project summary."""
    try:
        project = project_service.get_project(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")
        updated_proj = project_service.update_project_summary(project_id, payload.summary)
        return ProjectSummaryResponse(
            project_id=project_id,
            summary=updated_proj.project_summary if updated_proj else payload.summary,
            updated_at=updated_proj.updated_at if updated_proj else None
        )
    except WorkspaceSecurityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{project_id}/summary/refresh", response_model=ProjectSummaryResponse)
def refresh_project_summary(project_id: str):
    """Regenerate/refresh the project summary from workspace and memory analysis."""
    try:
        project = project_service.get_project(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")
        new_summary = project_service.refresh_project_summary(project_id)
        updated_proj = project_service.get_project(project_id)
        return ProjectSummaryResponse(
            project_id=project_id,
            summary=new_summary,
            updated_at=updated_proj.updated_at if updated_proj else None
        )
    except WorkspaceSecurityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
