from typing import Optional
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import (
    ProjectMemoryCreate,
    ProjectMemoryItem,
    ProjectMemoryListResponse
)
from app.memory.project_memory import project_memory
from app.services.project_service import project_service

router = APIRouter(prefix="/api/projects/{project_id}/memory", tags=["memory"])


@router.get("", response_model=ProjectMemoryListResponse)
def get_memories(project_id: str, category: Optional[str] = None):
    """Retrieve persistent project memories (decisions, architecture, conventions)."""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    items = project_memory.get_memories(project_id, category=category)
    return ProjectMemoryListResponse(memories=items)


@router.post("", response_model=ProjectMemoryItem, status_code=status.HTTP_201_CREATED)
def create_memory(project_id: str, payload: ProjectMemoryCreate):
    """Create or update a persistent project memory item."""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    item = project_memory.save_memory(
        project_id=project_id,
        key=payload.key,
        value=payload.value,
        category=payload.category or "general"
    )
    return item


@router.delete("/{key_or_id}")
def delete_memory(project_id: str, key_or_id: str):
    """Delete a persistent project memory item by key or ID."""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    deleted = project_memory.delete_memory(project_id, key_or_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory item not found")

    return {"success": True, "message": "Memory item deleted successfully"}
