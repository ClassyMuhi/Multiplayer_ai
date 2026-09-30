import logging
from typing import List, Optional, Dict, Any

from app.core.config import settings
from app.database.repository import repository
from app.memory.chroma_store import chroma_store, ChromaStore
from app.models.schemas import ProjectMemoryItem

logger = logging.getLogger("summit.memory_service")


class MemoryService:
    """
    High-level orchestrator connecting SQLite (structured source of truth)
    and ChromaDB (semantic similarity index).
    Enforces project-level scoping, deduplication, updates, and reindexing.
    """

    def __init__(self, chroma: Optional[ChromaStore] = None):
        self.chroma = chroma or chroma_store
        self.repo = repository

    def add_memory(
        self,
        project_id: str,
        content: str,
        memory_type: str = "project_fact",
        key: Optional[str] = None,
        source: Optional[str] = "manual",
        created_by: Optional[str] = None,
        importance: Optional[float] = 0.5
    ) -> ProjectMemoryItem:
        """
        Adds a persistent project memory.
        1. Checks for near-duplicate memories (deduplication).
        2. Persists to SQLite (source of truth).
        3. Indexes semantic embedding in ChromaDB.
        """
        clean_content = content.strip()
        if not clean_content:
            raise ValueError("Memory content cannot be empty.")

        # Step 1: Deduplication / update check via ChromaDB semantic search
        try:
            existing_hits = self.chroma.search(
                project_id=project_id,
                query=clean_content,
                top_k=1
            )
            if existing_hits:
                top_hit = existing_hits[0]
                distance = top_hit.get("distance", 1.0)
                # If extremely similar (distance < 0.10) and same memory_type, update existing
                if distance < 0.10 and top_hit.get("metadata", {}).get("memory_type") == memory_type:
                    doc_id = top_hit["id"]
                    logger.info(f"[MEMORY] Deduplicated memory ID={doc_id} (distance={distance:.3f})")
                    updated = self.update_memory(
                        project_id=project_id,
                        memory_id=doc_id,
                        content=clean_content,
                        memory_type=memory_type,
                        importance=importance
                    )
                    if updated:
                        return updated
        except Exception as e:
            logger.warning(f"Semantic deduplication check failed ({e}), proceeding with standard insert.")

        # Step 2: Persist to SQLite
        record = self.repo.save_project_memory(
            project_id=project_id,
            content=clean_content,
            memory_type=memory_type,
            key=key,
            source=source,
            created_by=created_by,
            importance=importance,
            is_active=True
        )

        memory_id = record["id"]

        # Step 3: Index in ChromaDB
        metadata = {
            "project_id": project_id,
            "memory_type": memory_type,
            "key": key or memory_id,
            "source": source or "manual",
            "created_by": created_by or "system",
            "importance": float(importance if importance is not None else 0.5),
            "created_at": record["created_at"].isoformat() if hasattr(record["created_at"], "isoformat") else str(record["created_at"])
        }

        try:
            self.chroma.add_document(
                doc_id=memory_id,
                document=clean_content,
                metadata=metadata
            )
            logger.info(f"[MEMORY] Stored semantic memory ID={memory_id} for project={project_id} [type={memory_type}]")
        except Exception as e:
            logger.error(f"Failed to index memory ID={memory_id} in ChromaDB: {e}", exc_info=True)
            # SQLite is source of truth, return record even if indexing had non-fatal error

        return ProjectMemoryItem(**record)

    def search_memories(
        self,
        project_id: str,
        query: str,
        top_k: Optional[int] = None,
        relevance_threshold: Optional[float] = None,
        category: Optional[str] = None
    ) -> List[ProjectMemoryItem]:
        """
        Retrieves project-scoped semantic memories relevant to a query.
        Applies relevance distance threshold and hydrates with SQLite state.
        """
        k = top_k or settings.MEMORY_TOP_K
        threshold = relevance_threshold if relevance_threshold is not None else settings.MEMORY_RELEVANCE_THRESHOLD

        where_extra = {"memory_type": category} if category else None

        hits = self.chroma.search(
            project_id=project_id,
            query=query,
            top_k=k,
            where_extra=where_extra
        )

        results: List[ProjectMemoryItem] = []
        for hit in hits:
            distance = hit.get("distance", 0.0)

            # Filter out results exceeding distance threshold
            if threshold is not None and distance > threshold:
                continue

            doc_id = hit["id"]
            # Fetch structured record from SQLite
            record = self.repo.get_project_memory(project_id=project_id, memory_id=doc_id)
            if record and record.get("is_active", True):
                item = ProjectMemoryItem(**record)
                item.similarity_score = round(1.0 - distance, 4)
                results.append(item)
            elif not record:
                # Fallback from Chroma metadata if SQLite record not found
                meta = hit.get("metadata", {})
                item = ProjectMemoryItem(
                    id=doc_id,
                    project_id=project_id,
                    memory_type=meta.get("memory_type", "general"),
                    key=meta.get("key", doc_id),
                    value=hit.get("document", ""),
                    content=hit.get("document", ""),
                    category=meta.get("memory_type", "general"),
                    source=meta.get("source", "chroma"),
                    created_by=meta.get("created_by", ""),
                    is_active=True,
                    similarity_score=round(1.0 - distance, 4),
                    created_at=record["created_at"] if record else hit.get("metadata", {}).get("created_at"),  # type: ignore
                    updated_at=record["updated_at"] if record else hit.get("metadata", {}).get("created_at")   # type: ignore
                )
                results.append(item)

        logger.info(f"[MEMORY] project={project_id} query='{query[:50]}' retrieved={len(results)} hits")
        return results

    def get_memory(self, project_id: str, memory_id: str) -> Optional[ProjectMemoryItem]:
        """Retrieves a single memory by ID."""
        record = self.repo.get_project_memory(project_id=project_id, memory_id=memory_id)
        if not record:
            return None
        return ProjectMemoryItem(**record)

    def list_memories(
        self,
        project_id: str,
        category: Optional[str] = None,
        active_only: bool = True
    ) -> List[ProjectMemoryItem]:
        """Lists all structured memories for a project."""
        records = self.repo.get_project_memories(
            project_id=project_id,
            category=category,
            active_only=active_only
        )
        return [ProjectMemoryItem(**r) for r in records]

    def update_memory(
        self,
        project_id: str,
        memory_id: str,
        content: str,
        memory_type: Optional[str] = None,
        importance: Optional[float] = None,
        is_active: Optional[bool] = None
    ) -> Optional[ProjectMemoryItem]:
        """Updates a memory in both SQLite and ChromaDB."""
        clean_content = content.strip()
        record = self.repo.update_project_memory(
            memory_id=memory_id,
            content=clean_content,
            memory_type=memory_type,
            importance=importance,
            is_active=is_active
        )
        if not record:
            return None

        # Update in ChromaDB
        if record.get("is_active", True):
            metadata = {
                "project_id": project_id,
                "memory_type": record["memory_type"],
                "key": record.get("key") or memory_id,
                "source": record.get("source") or "manual",
                "created_by": record.get("created_by") or "system",
                "importance": float(record.get("importance") or 0.5),
                "created_at": str(record["created_at"])
            }
            self.chroma.update_document(
                doc_id=memory_id,
                document=clean_content,
                metadata=metadata
            )
        else:
            # If deactivated, remove from semantic search index
            self.chroma.delete_document(doc_id=memory_id)

        return ProjectMemoryItem(**record)

    def delete_memory(self, project_id: str, memory_id_or_key: str) -> bool:
        """Deletes a memory item from both SQLite and ChromaDB."""
        # Find record first to get exact ID
        record = self.repo.get_project_memory(project_id, memory_id_or_key)
        actual_id = record["id"] if record else memory_id_or_key

        # Delete from ChromaDB
        self.chroma.delete_document(doc_id=actual_id)

        # Delete from SQLite
        return self.repo.delete_memory(project_id, memory_id_or_key)

    def rebuild_project_memory_index(self, project_id: Optional[str] = None) -> int:
        """
        Rebuilds ChromaDB index from the SQLite source of truth.
        Useful for recovery or database synchronization.
        """
        if project_id:
            # Clear project docs from Chroma
            self.chroma.delete_project_documents(project_id)
            records = self.repo.get_project_memories(project_id=project_id, active_only=True)
        else:
            self.chroma.reset()
            # Fetch all projects
            projects = self.repo.list_projects()
            records = []
            for p in projects:
                records.extend(self.repo.get_project_memories(project_id=p["id"], active_only=True))

        indexed_count = 0
        for r in records:
            meta = {
                "project_id": r["project_id"],
                "memory_type": r["memory_type"],
                "key": r.get("key") or r["id"],
                "source": r.get("source") or "sqlite_sync",
                "created_by": r.get("created_by") or "system",
                "importance": float(r.get("importance") or 0.5),
                "created_at": str(r["created_at"])
            }
            content = r.get("content") or r.get("value") or ""
            if content:
                self.chroma.add_document(doc_id=r["id"], document=content, metadata=meta)
                indexed_count += 1

        logger.info(f"[MEMORY] Rebuilt ChromaDB index: {indexed_count} documents indexed.")
        return indexed_count


# Global memory service instance
memory_service = MemoryService()
