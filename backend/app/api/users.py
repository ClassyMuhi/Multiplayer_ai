from fastapi import APIRouter, HTTPException, status
from app.models.schemas import UserPresenceListResponse
from app.agent.session_manager import session_manager
from app.services.project_service import project_service

router = APIRouter(prefix="/api/projects/{project_id}/users", tags=["users"])


@router.get("", response_model=UserPresenceListResponse)
def get_connected_users(project_id: str):
    """Retrieve list of currently online users in this project room."""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    users = session_manager.get_connected_users(project_id)
    return UserPresenceListResponse(users=users)
