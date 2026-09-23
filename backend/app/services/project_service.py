import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import uuid

from app.core.config import settings
from app.models.schemas import ProjectResponse, ProjectListResponse
from app.workspace.manager import workspace_manager


class ProjectService:
    """
    Manages project lifecycle, directory structure, and metadata.
    """

    def __init__(self):
        self.workspace_mgr = workspace_manager

    def _get_project_meta_path(self, project_id: str) -> Path:
        workspace_dir = self.workspace_mgr.ensure_workspace(project_id)
        meta_dir = workspace_dir / ".summit"
        meta_dir.mkdir(exist_ok=True)
        return meta_dir / "project.json"

    def _save_project_metadata(self, project_id: str, name: str, created_at: Optional[str] = None):
        meta_file = self._get_project_meta_path(project_id)
        now_iso = datetime.utcnow().isoformat()
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
        """Discovers all projects in the workspace root."""
        root = self.workspace_mgr.root_path
        if not root.exists():
            root.mkdir(parents=True, exist_ok=True)

        projects: List[ProjectResponse] = []
        for entry in root.iterdir():
            if entry.is_dir() and not entry.name.startswith("."):
                project_id = entry.name
                meta = self._read_project_metadata(project_id)

                if meta:
                    name = meta.get("name", project_id)
                    created_at = datetime.fromisoformat(meta.get("created_at", datetime.utcnow().isoformat()))
                    updated_at = datetime.fromisoformat(meta.get("updated_at", datetime.utcnow().isoformat()))
                else:
                    name = project_id.replace("-", " ").title()
                    created_at = datetime.fromtimestamp(entry.stat().st_ctime)
                    updated_at = datetime.fromtimestamp(entry.stat().st_mtime)

                projects.append(ProjectResponse(
                    id=project_id,
                    name=name,
                    workspace_path=str(entry.resolve()),
                    created_at=created_at,
                    updated_at=updated_at
                ))

        # Sort by updated_at descending
        projects.sort(key=lambda p: p.updated_at, reverse=True)
        return ProjectListResponse(projects=projects)

    def get_project(self, project_id: str) -> Optional[ProjectResponse]:
        """Gets project details by ID."""
        try:
            workspace_dir = self.workspace_mgr.get_workspace_dir(project_id)
        except Exception:
            return None

        if not workspace_dir.exists():
            return None

        meta = self._read_project_metadata(project_id)
        if meta:
            name = meta.get("name", project_id)
            created_at = datetime.fromisoformat(meta.get("created_at", datetime.utcnow().isoformat()))
            updated_at = datetime.fromisoformat(meta.get("updated_at", datetime.utcnow().isoformat()))
        else:
            name = project_id.replace("-", " ").title()
            created_at = datetime.fromtimestamp(workspace_dir.stat().st_ctime)
            updated_at = datetime.fromtimestamp(workspace_dir.stat().st_mtime)

        return ProjectResponse(
            id=project_id,
            name=name,
            workspace_path=str(workspace_dir.resolve()),
            created_at=created_at,
            updated_at=updated_at
        )

    def create_project(self, name: str, template: Optional[str] = "demo-calculator") -> ProjectResponse:
        """Creates a new project and seeds it."""
        # Generate safe slug-based project ID
        slug = "".join(c if c.isalnum() else "-" for c in name.lower()).strip("-")
        if not slug:
            slug = "project"
        project_id = f"{slug}-{uuid.uuid4().hex[:6]}"

        if template == "demo-calculator":
            self.workspace_mgr.init_demo_calculator_workspace(project_id)
        else:
            self.workspace_mgr.ensure_workspace(project_id)

        self._save_project_metadata(project_id, name)
        return self.get_project(project_id)  # type: ignore

    def ensure_default_demo_project(self) -> str:
        """Ensures the demo calculator project exists at startup."""
        demo_id = "demo-calculator"
        demo_path = self.workspace_mgr.root_path / demo_id
        if not demo_path.exists():
            self.workspace_mgr.init_demo_calculator_workspace(demo_id)
            self._save_project_metadata(demo_id, "Demo Calculator Project")
        return demo_id


project_service = ProjectService()
