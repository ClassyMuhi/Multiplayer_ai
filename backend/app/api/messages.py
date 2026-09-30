from fastapi import APIRouter, HTTPException, status
from app.models.schemas import MessageListResponse
from app.memory.conversation_memory import conversation_memory
from app.services.project_service import project_service

router = APIRouter(prefix="/api/projects/{project_id}/messages", tags=["messages"])


@router.get("", response_model=MessageListResponse)
def get_messages(project_id: str, limit: int = 100):
    """Retrieve persistent conversation history for a project."""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    messages = conversation_memory.get_messages(project_id, limit=limit)
    return MessageListResponse(messages=messages)
