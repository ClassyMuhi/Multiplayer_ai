import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

from sqlalchemy import select, delete, update, and_, or_
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.database.models import (
    Project,
    User,
    ProjectMember,
    ConversationMessage,
    AgentRun,
    FileChange,
    ProjectMemory
)

logger = logging.getLogger("summit.repository")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)



class DatabaseRepository:
    """
    Independent repository layer managing persistence for projects,
    users, members, conversation messages, agent runs, file changes, and project memories.
    """

    @contextmanager
    def _session(self):
        """Context manager for obtaining a database session."""
        session: Session = SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database transaction rollback due to: {e}", exc_info=True)
            raise
        finally:
            session.close()

    # -------------------------------------------------------------------------
    # PROJECTS
    # -------------------------------------------------------------------------

    def create_project(
        self,
        id: str,
        name: str,
        workspace_path: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Creates or updates a project record in the database."""
        with self._session() as session:
            existing = session.get(Project, id)
            if existing:
                existing.name = name
                existing.workspace_path = workspace_path
                if description is not None:
                    existing.description = description
                existing.updated_at = utc_now()
                project = existing
            else:
                project = Project(
                    id=id,
                    name=name,
                    description=description,
                    workspace_path=workspace_path,
                    created_at=utc_now(),
                    updated_at=utc_now()
                )
                session.add(project)
            session.flush()
            return {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "workspace_path": project.workspace_path,
                "created_at": project.created_at,
                "updated_at": project.updated_at
            }

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single project record by ID."""
        with self._session() as session:
            project = session.get(Project, project_id)
            if not project:
                return None
            return {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "workspace_path": project.workspace_path,
                "created_at": project.created_at,
                "updated_at": project.updated_at
            }

    def list_projects(self) -> List[Dict[str, Any]]:
        """Lists all projects ordered by most recently updated."""
        with self._session() as session:
            stmt = select(Project).order_by(Project.updated_at.desc())
            results = session.scalars(stmt).all()
            return [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "workspace_path": p.workspace_path,
                    "created_at": p.created_at,
                    "updated_at": p.updated_at
                }
                for p in results
            ]

    def update_project(
        self,
        project_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        workspace_path: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Updates fields of an existing project."""
        with self._session() as session:
            project = session.get(Project, project_id)
            if not project:
                return None
            if name is not None:
                project.name = name
            if description is not None:
                project.description = description
            if workspace_path is not None:
                project.workspace_path = workspace_path
            project.updated_at = utc_now()
            session.flush()
            return {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "workspace_path": project.workspace_path,
                "created_at": project.created_at,
                "updated_at": project.updated_at
            }

    def delete_project(self, project_id: str) -> bool:
        """Deletes a project and all cascaded child records."""
        with self._session() as session:
            project = session.get(Project, project_id)
            if not project:
                return False
            session.delete(project)
            return True

    # -------------------------------------------------------------------------
    # USERS
    # -------------------------------------------------------------------------

    def create_user(
        self,
        display_name: str,
        id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Creates a new user record."""
        with self._session() as session:
            user = User(
                id=id or User.generate_uuid(),
                display_name=display_name,
                created_at=utc_now()
            ) if id else User(
                display_name=display_name,
                created_at=utc_now()
            )
            session.add(user)
            session.flush()
            return {
                "id": user.id,
                "display_name": user.display_name,
                "created_at": user.created_at
            }

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a user by ID."""
        with self._session() as session:
            user = session.get(User, user_id)
            if not user:
                return None
            return {
                "id": user.id,
                "display_name": user.display_name,
                "created_at": user.created_at
            }

    def get_or_create_user(self, user_id: str, display_name: str = "Developer") -> Dict[str, Any]:
        """Gets an existing user or creates a new one if not found."""
        with self._session() as session:
            user = session.get(User, user_id)
            if not user:
                user = User(
                    id=user_id,
                    display_name=display_name,
                    created_at=utc_now()
                )
                session.add(user)
                session.flush()
            return {
                "id": user.id,
                "display_name": user.display_name,
                "created_at": user.created_at
            }

    # -------------------------------------------------------------------------
    # PROJECT MEMBERSHIP
    # -------------------------------------------------------------------------

    def add_project_member(self, project_id: str, user_id: str) -> Dict[str, Any]:
        """Adds a user as a member of a project."""
        with self._session() as session:
            # Ensure project exists
            project = session.get(Project, project_id)
            if not project:
                raise ValueError(f"Project '{project_id}' not found.")

            # Check if membership already exists
            stmt = select(ProjectMember).where(
                and_(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)
            )
            existing = session.scalars(stmt).first()
            if existing:
                return {
                    "id": existing.id,
                    "project_id": existing.project_id,
                    "user_id": existing.user_id,
                    "joined_at": existing.joined_at
                }

            member = ProjectMember(
                project_id=project_id,
                user_id=user_id,
                joined_at=utc_now()
            )
            session.add(member)
            session.flush()
            return {
                "id": member.id,
                "project_id": member.project_id,
                "user_id": member.user_id,
                "joined_at": member.joined_at
            }

    def get_project_members(self, project_id: str) -> List[Dict[str, Any]]:
        """Lists all members of a project."""
        with self._session() as session:
            stmt = select(ProjectMember).where(ProjectMember.project_id == project_id)
            members = session.scalars(stmt).all()
            return [
                {
                    "id": m.id,
                    "project_id": m.project_id,
                    "user_id": m.user_id,
                    "joined_at": m.joined_at
                }
                for m in members
            ]

    def remove_project_member(self, project_id: str, user_id: str) -> bool:
        """Removes a user membership from a project."""
        with self._session() as session:
            stmt = delete(ProjectMember).where(
                and_(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)
            )
            result = session.execute(stmt)
            return (result.rowcount or 0) > 0

    # -------------------------------------------------------------------------
    # CONVERSATION MESSAGES
    # -------------------------------------------------------------------------

    def save_message(
        self,
        project_id: str,
        role: str,
        content: str,
        user_id: Optional[str] = None,
        user_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Saves a conversation message under a project."""
        with self._session() as session:
            # If user_id provided but doesn't exist, create simple user entry
            if user_id:
                user = session.get(User, user_id)
                if not user:
                    user = User(
                        id=user_id,
                        display_name=user_name or f"User-{user_id[:6]}",
                        created_at=utc_now()
                    )
                    session.add(user)
                    session.flush()

            msg = ConversationMessage(
                project_id=project_id,
                user_id=user_id,
                user_name=user_name,
                role=role,
                content=content,
                created_at=utc_now()
            )
            session.add(msg)
            session.flush()
            return {
                "id": msg.id,
                "project_id": msg.project_id,
                "user_id": msg.user_id,
                "user_name": msg.user_name,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at
            }

    def get_project_messages(
        self,
        project_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Retrieves messages for a project chronologically."""
        with self._session() as session:
            stmt = (
                select(ConversationMessage)
                .where(ConversationMessage.project_id == project_id)
                .order_by(ConversationMessage.created_at.asc())
                .offset(offset)
                .limit(limit)
            )
            messages = session.scalars(stmt).all()
            return [
                {
                    "id": m.id,
                    "project_id": m.project_id,
                    "user_id": m.user_id,
                    "user_name": m.user_name,
                    "role": m.role,
                    "content": m.content,
                    "created_at": m.created_at
                }
                for m in messages
            ]

    def get_messages(self, project_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Compatibility alias for get_project_messages."""
        return self.get_project_messages(project_id=project_id, limit=limit)

    # -------------------------------------------------------------------------
    # AGENT RUNS
    # -------------------------------------------------------------------------

    def create_agent_run(
        self,
        project_id: str,
        prompt: str,
        initiated_by: Optional[str] = None,
        status: str = "pending"
    ) -> Dict[str, Any]:
        """Records an agent run session."""
        with self._session() as session:
            run = AgentRun(
                project_id=project_id,
                prompt=prompt,
                initiated_by=initiated_by,
                status=status,
                started_at=utc_now()
            )
            session.add(run)
            session.flush()
            return {
                "id": run.id,
                "project_id": run.project_id,
                "prompt": run.prompt,
                "initiated_by": run.initiated_by,
                "status": run.status,
                "started_at": run.started_at,
                "completed_at": run.completed_at
            }

    def update_agent_run(
        self,
        run_id: str,
        status: str,
        completed_at: Optional[datetime] = None
    ) -> Optional[Dict[str, Any]]:
        """Updates the status and completion time of an agent run."""
        with self._session() as session:
            run = session.get(AgentRun, run_id)
            if not run:
                return None
            run.status = status
            if completed_at:
                run.completed_at = completed_at
            elif status in ("completed", "failed", "stopped") and not run.completed_at:
                run.completed_at = utc_now()
            session.flush()
            return {
                "id": run.id,
                "project_id": run.project_id,
                "prompt": run.prompt,
                "initiated_by": run.initiated_by,
                "status": run.status,
                "started_at": run.started_at,
                "completed_at": run.completed_at
            }

    def get_agent_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves an agent run by ID."""
        with self._session() as session:
            run = session.get(AgentRun, run_id)
            if not run:
                return None
            return {
                "id": run.id,
                "project_id": run.project_id,
                "prompt": run.prompt,
                "initiated_by": run.initiated_by,
                "status": run.status,
                "started_at": run.started_at,
                "completed_at": run.completed_at
            }

    def get_project_agent_runs(self, project_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves agent runs for a project."""
        with self._session() as session:
            stmt = (
                select(AgentRun)
                .where(AgentRun.project_id == project_id)
                .order_by(AgentRun.started_at.desc())
                .limit(limit)
            )
            runs = session.scalars(stmt).all()
            return [
                {
                    "id": r.id,
                    "project_id": r.project_id,
                    "prompt": r.prompt,
                    "initiated_by": r.initiated_by,
                    "status": r.status,
                    "started_at": r.started_at,
                    "completed_at": r.completed_at
                }
                for r in runs
            ]

    # -------------------------------------------------------------------------
    # FILE CHANGES
    # -------------------------------------------------------------------------

    def record_file_change(
        self,
        project_id: str,
        file_path: str,
        operation: str,
        user_id: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Records a file operation (create, modify, delete) within a project."""
        with self._session() as session:
            fc = FileChange(
                project_id=project_id,
                user_id=user_id,
                file_path=file_path,
                operation=operation,
                description=description,
                created_at=utc_now()
            )
            session.add(fc)
            session.flush()
            return {
                "id": fc.id,
                "project_id": fc.project_id,
                "user_id": fc.user_id,
                "file_path": fc.file_path,
                "operation": fc.operation,
                "description": fc.description,
                "created_at": fc.created_at
            }

    def get_project_file_changes(self, project_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves file modification history for a project."""
        with self._session() as session:
            stmt = (
                select(FileChange)
                .where(FileChange.project_id == project_id)
                .order_by(FileChange.created_at.desc())
                .limit(limit)
            )
            changes = session.scalars(stmt).all()
            return [
                {
                    "id": c.id,
                    "project_id": c.project_id,
                    "user_id": c.user_id,
                    "file_path": c.file_path,
                    "operation": c.operation,
                    "description": c.description,
                    "created_at": c.created_at
                }
                for c in changes
            ]

    # -------------------------------------------------------------------------
    # PROJECT MEMORIES
    # -------------------------------------------------------------------------

    def save_project_memory(
        self,
        project_id: str,
        content: str,
        memory_type: str = "general",
        key: Optional[str] = None,
        source: Optional[str] = None,
        created_by: Optional[str] = None,
        is_active: bool = True
    ) -> Dict[str, Any]:
        """
        Saves or updates a project memory item.
        If key is provided and already exists for this project, it updates the existing entry.
        """
        with self._session() as session:
            existing = None
            if key:
                stmt = select(ProjectMemory).where(
                    and_(ProjectMemory.project_id == project_id, ProjectMemory.key == key)
                )
                existing = session.scalars(stmt).first()

            if existing:
                existing.content = content
                existing.memory_type = memory_type
                existing.is_active = is_active
                if source:
                    existing.source = source
                if created_by:
                    existing.created_by = created_by
                existing.updated_at = utc_now()
                mem = existing
            else:
                mem = ProjectMemory(
                    project_id=project_id,
                    memory_type=memory_type,
                    key=key,
                    content=content,
                    source=source,
                    created_by=created_by,
                    is_active=is_active,
                    created_at=utc_now(),
                    updated_at=utc_now()
                )
                session.add(mem)

            session.flush()
            return {
                "id": mem.id,
                "project_id": mem.project_id,
                "memory_type": mem.memory_type,
                "key": mem.key or mem.id,
                "value": mem.content,
                "content": mem.content,
                "category": mem.memory_type,
                "source": mem.source,
                "created_by": mem.created_by,
                "is_active": mem.is_active,
                "created_at": mem.created_at,
                "updated_at": mem.updated_at
            }

    def get_project_memory(self, project_id: str, memory_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single project memory by ID."""
        with self._session() as session:
            mem = session.get(ProjectMemory, memory_id)
            if not mem or mem.project_id != project_id:
                return None
            return {
                "id": mem.id,
                "project_id": mem.project_id,
                "memory_type": mem.memory_type,
                "key": mem.key or mem.id,
                "value": mem.content,
                "content": mem.content,
                "category": mem.memory_type,
                "source": mem.source,
                "created_by": mem.created_by,
                "is_active": mem.is_active,
                "created_at": mem.created_at,
                "updated_at": mem.updated_at
            }

    def save_memory(
        self,
        project_id: str,
        key: str,
        value: str,
        category: str = "general"
    ) -> Dict[str, Any]:
        """Compatibility wrapper for ProjectMemory interface."""
        return self.save_project_memory(
            project_id=project_id,
            key=key,
            content=value,
            memory_type=category
        )

    def get_project_memories(
        self,
        project_id: str,
        category: Optional[str] = None,
        memory_type: Optional[str] = None,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Retrieves all memory records for a project, optionally filtered by type/activity."""
        filter_type = memory_type or category
        with self._session() as session:
            stmt = select(ProjectMemory).where(ProjectMemory.project_id == project_id)
            if active_only:
                stmt = stmt.where(ProjectMemory.is_active == True)
            if filter_type:
                stmt = stmt.where(ProjectMemory.memory_type == filter_type)
            stmt = stmt.order_by(ProjectMemory.updated_at.desc())

            memories = session.scalars(stmt).all()
            return [
                {
                    "id": m.id,
                    "project_id": m.project_id,
                    "memory_type": m.memory_type,
                    "key": m.key or m.id,
                    "value": m.content,
                    "content": m.content,
                    "category": m.memory_type,
                    "source": m.source,
                    "created_by": m.created_by,
                    "is_active": m.is_active,
                    "created_at": m.created_at,
                    "updated_at": m.updated_at
                }
                for m in memories
            ]

    def get_memories(self, project_id: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Compatibility wrapper for ProjectMemory interface."""
        return self.get_project_memories(project_id=project_id, category=category)

    def update_project_memory(
        self,
        memory_id: str,
        content: Optional[str] = None,
        value: Optional[str] = None,
        memory_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Optional[Dict[str, Any]]:
        """Updates content, type, or active state of an existing memory item."""
        new_content = content or value
        with self._session() as session:
            mem = session.get(ProjectMemory, memory_id)
            if not mem:
                return None
            if new_content is not None:
                mem.content = new_content
            if memory_type is not None:
                mem.memory_type = memory_type
            if is_active is not None:
                mem.is_active = is_active
            mem.updated_at = utc_now()
            session.flush()
            return {
                "id": mem.id,
                "project_id": mem.project_id,
                "memory_type": mem.memory_type,
                "key": mem.key or mem.id,
                "value": mem.content,
                "content": mem.content,
                "category": mem.memory_type,
                "source": mem.source,
                "created_by": mem.created_by,
                "is_active": mem.is_active,
                "created_at": mem.created_at,
                "updated_at": mem.updated_at
            }

    def delete_memory(self, project_id: str, key_or_id: str) -> bool:
        """Deletes a memory item matching key or id within a project."""
        with self._session() as session:
            stmt = delete(ProjectMemory).where(
                and_(
                    ProjectMemory.project_id == project_id,
                    or_(ProjectMemory.id == key_or_id, ProjectMemory.key == key_or_id)
                )
            )
            res = session.execute(stmt)
            return (res.rowcount or 0) > 0

    def delete_project_memory(self, project_id: str, memory_id: str) -> bool:
        """Deletes a project memory by ID."""
        return self.delete_memory(project_id=project_id, key_or_id=memory_id)



repository = DatabaseRepository()
