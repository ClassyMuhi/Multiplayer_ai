from typing import List, Optional
from app.database.repository import repository
from app.models.schemas import ProjectMemoryItem, ProjectMemoryCreate


class ProjectMemory:
    """Manages persistent project memory (decisions, conventions, architecture notes)."""

    @staticmethod
    def save_memory(
        project_id: str,
        key: str,
        value: str,
        category: str = "general"
    ) -> ProjectMemoryItem:
        record = repository.save_memory(
            project_id=project_id,
            key=key,
            value=value,
            category=category
        )
        return ProjectMemoryItem(**record)

    @staticmethod
    def get_memories(project_id: str, category: Optional[str] = None) -> List[ProjectMemoryItem]:
        records = repository.get_memories(project_id, category=category)
        return [ProjectMemoryItem(**r) for r in records]

    @staticmethod
    def delete_memory(project_id: str, key_or_id: str) -> bool:
        return repository.delete_memory(project_id, key_or_id)


project_memory = ProjectMemory()
