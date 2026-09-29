from typing import List, Optional
from app.database.repository import repository
from app.models.schemas import MessageRecord


class ConversationMemory:
    """Manages persistent chat conversation history per project."""

    @staticmethod
    def save_message(
        project_id: str,
        role: str,
        content: str,
        user_id: Optional[str] = None,
        user_name: Optional[str] = None
    ) -> MessageRecord:
        record = repository.save_message(
            project_id=project_id,
            role=role,
            content=content,
            user_id=user_id,
            user_name=user_name
        )
        return MessageRecord(**record)

    @staticmethod
    def get_messages(project_id: str, limit: int = 100) -> List[MessageRecord]:
        records = repository.get_messages(project_id, limit=limit)
        return [MessageRecord(**r) for r in records]


conversation_memory = ConversationMemory()
