from fastapi import APIRouter, HTTPException, status
from app.models.schemas import ProjectCreate, ProjectResponse, ProjectListResponse
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
