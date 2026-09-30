import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query

from app.models.schemas import (
    ProjectMemoryItem,
    ProjectMemoryCreate,
    MemorySearchRequest
)
from app.services.project_service import project_service
from app.memory.memory_service import memory_service

router = APIRouter(prefix="/api/projects/{project_id}/memory", tags=["memory"])
logger = logging.getLogger("summit.api.memory")


@router.get("", response_model=List[ProjectMemoryItem])
def list_project_memories(
    project_id: str,
    category: Optional[str] = None,
    active_only: bool = True
):
    """Lists all stored memories for a project."""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")

    return memory_service.list_memories(project_id=project_id, category=category, active_only=active_only)


@router.post("", response_model=ProjectMemoryItem, status_code=status.HTTP_201_CREATED)
def create_project_memory(project_id: str, payload: ProjectMemoryCreate):
    """Adds a new persistent project memory."""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")

    content = payload.content or payload.value
    if not content:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Memory content is required.")

    memory_type = payload.memory_type or payload.category or "general"

    return memory_service.add_memory(
        project_id=project_id,
        content=content,
        memory_type=memory_type,
        key=payload.key,
        source=payload.source or "api",
        created_by=payload.created_by
    )


@router.post("/search", response_model=List[ProjectMemoryItem])
def search_project_memories(project_id: str, payload: MemorySearchRequest):
    """Searches project memories using ChromaDB semantic similarity search."""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")

    return memory_service.search_memories(
        project_id=project_id,
        query=payload.query,
        top_k=payload.top_k,
        relevance_threshold=payload.relevance_threshold,
        category=payload.category
    )


@router.delete("/{memory_id}")
def delete_project_memory(project_id: str, memory_id: str):
    """Deletes a project memory by ID from both SQLite and ChromaDB."""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")

    deleted = memory_service.delete_memory(project_id=project_id, memory_id_or_key=memory_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Memory '{memory_id}' not found.")

    return {"success": True, "message": f"Memory '{memory_id}' deleted successfully."}


@router.post("/reindex")
def reindex_project_memories(project_id: str):
    """Rebuilds the ChromaDB semantic index from the SQLite source of truth for this project."""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")

    count = memory_service.rebuild_project_memory_index(project_id=project_id)
    return {"success": True, "project_id": project_id, "reindexed_count": count}
