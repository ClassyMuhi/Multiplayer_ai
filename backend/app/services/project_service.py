import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
import uuid


from app.core.config import settings
from app.models.schemas import ProjectResponse, ProjectListResponse
from app.workspace.manager import workspace_manager
from app.database.repository import repository


class ProjectService:
    """
    Manages project lifecycle, directory structure, and metadata using SQLite database
    and isolated workspaces.
    """

    def __init__(self):
        self.workspace_mgr = workspace_manager
        self.repo = repository

    def _get_project_meta_path(self, project_id: str) -> Path:
        workspace_dir = self.workspace_mgr.ensure_workspace(project_id)
        meta_dir = workspace_dir / ".summit"
        meta_dir.mkdir(exist_ok=True)
        return meta_dir / "project.json"

    def _save_project_metadata(self, project_id: str, name: str, created_at: Optional[str] = None):
        meta_file = self._get_project_meta_path(project_id)
        now_iso = datetime.now(timezone.utc).isoformat()

        data = {
            "id": project_id,
            "name": name,
            "created_at": created_at or now_iso,
            "updated_at": now_iso
        }
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _read_project_metadata(self, project_id: str) -> Optional[dict]:
        meta_file = self._get_project_meta_path(project_id)
        if not meta_file.exists():
            return None
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def list_projects(self) -> ProjectListResponse:
        """Lists all projects from database, discovering and syncing any workspace directories."""
        root = self.workspace_mgr.root_path
        if not root.exists():
            root.mkdir(parents=True, exist_ok=True)

        # Sync disk directories to DB if any exist on disk but not in DB
        for entry in root.iterdir():
            if entry.is_dir() and not entry.name.startswith("."):
                project_id = entry.name
                db_proj = self.repo.get_project(project_id)
                if not db_proj:
                    meta = self._read_project_metadata(project_id)
                    name = meta.get("name", project_id.replace("-", " ").title()) if meta else project_id.replace("-", " ").title()
                    self.repo.create_project(
                        id=project_id,
                        name=name,
                        workspace_path=str(entry.resolve())
                    )

        db_projects = self.repo.list_projects()
        projects = [
            ProjectResponse(
                id=p["id"],
                name=p["name"],
                description=p.get("description"),
                workspace_path=p["workspace_path"],
                created_at=p["created_at"],
                updated_at=p["updated_at"]
            )
            for p in db_projects
        ]
        return ProjectListResponse(projects=projects)

    def get_project(self, project_id: str) -> Optional[ProjectResponse]:
        """Gets project details by ID from database repository."""
        try:
            workspace_dir = self.workspace_mgr.get_workspace_dir(project_id)
        except Exception:
            return None

        if not workspace_dir.exists():
            return None

        p = self.repo.get_project(project_id)
        if not p:
            meta = self._read_project_metadata(project_id)
            name = meta.get("name", project_id.replace("-", " ").title()) if meta else project_id.replace("-", " ").title()
            p = self.repo.create_project(
                id=project_id,
                name=name,
                workspace_path=str(workspace_dir.resolve())
            )

        return ProjectResponse(
            id=p["id"],
            name=p["name"],
            description=p.get("description"),
            workspace_path=p["workspace_path"],
            created_at=p["created_at"],
            updated_at=p["updated_at"]
        )

    def create_project(
        self,
        name: str,
        template: Optional[str] = "demo-calculator",
        description: Optional[str] = None
    ) -> ProjectResponse:
        """Creates a new project record in DB and sets up the workspace."""
        slug = "".join(c if c.isalnum() else "-" for c in name.lower()).strip("-")
        if not slug:
            slug = "project"
        project_id = f"{slug}-{uuid.uuid4().hex[:6]}"

        if template == "demo-calculator":
            workspace_dir = self.workspace_mgr.init_demo_calculator_workspace(project_id)
        else:
            workspace_dir = self.workspace_mgr.ensure_workspace(project_id)

        # Save metadata to SQLite
        self.repo.create_project(
            id=project_id,
            name=name,
            description=description,
            workspace_path=str(workspace_dir.resolve())
        )
        self._save_project_metadata(project_id, name)
        return self.get_project(project_id)  # type: ignore

    def ensure_default_demo_project(self) -> str:
        """Ensures the demo calculator project exists in both database and filesystem."""
        demo_id = "demo-calculator"
        demo_path = self.workspace_mgr.root_path / demo_id
        if not demo_path.exists():
            self.workspace_mgr.init_demo_calculator_workspace(demo_id)
            self._save_project_metadata(demo_id, "Demo Calculator Project")

        self.repo.create_project(
            id=demo_id,
            name="Demo Calculator Project",
            description="Default demo project for Summit AI",
            workspace_path=str(demo_path.resolve())
        )
        return demo_id



project_service = ProjectService()
