import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
import uuid

from app.core.config import settings
from app.models.schemas import ProjectResponse, ProjectListResponse
from app.workspace.manager import workspace_manager
from app.database.repository import repository


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_dt(ts_str: str) -> datetime:
    dt = datetime.fromisoformat(ts_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


class ProjectService:
    """
    Manages project lifecycle, directory structure, metadata, and DB persistence.
    """

    def __init__(self):
        self.workspace_mgr = workspace_manager

    def _get_project_meta_path(self, project_id: str) -> Path:
        workspace_dir = self.workspace_mgr.ensure_workspace(project_id)
        meta_dir = workspace_dir / ".summit"
        meta_dir.mkdir(exist_ok=True)
        return meta_dir / "project.json"

    def _save_project_metadata(self, project_id: str, name: str, template: str = "demo-calculator", created_at: Optional[str] = None):
        meta_file = self._get_project_meta_path(project_id)
        ts = now_utc_iso()
        data = {
            "id": project_id,
            "name": name,
            "template": template,
            "created_at": created_at or ts,
            "updated_at": ts
        }
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        workspace_dir = self.workspace_mgr.get_workspace_dir(project_id)
        repository.save_project(
            project_id=project_id,
            name=name,
            template=template,
            workspace_path=str(workspace_dir.resolve())
        )

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
        root = self.workspace_mgr.root_path
        if not root.exists():
            root.mkdir(parents=True, exist_ok=True)

        projects: List[ProjectResponse] = []
        for entry in root.iterdir():
            if entry.is_dir() and not entry.name.startswith("."):
                project_id = entry.name
                meta = self._read_project_metadata(project_id)

                now = datetime.now(timezone.utc)
                if meta:
                    name = meta.get("name", project_id)
                    created_at = parse_dt(meta.get("created_at", now.isoformat()))
                    updated_at = parse_dt(meta.get("updated_at", now.isoformat()))
                else:
                    name = project_id.replace("-", " ").title()
                    created_at = datetime.fromtimestamp(entry.stat().st_ctime, tz=timezone.utc)
                    updated_at = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc)

                projects.append(ProjectResponse(
                    id=project_id,
                    name=name,
                    workspace_path=str(entry.resolve()),
                    created_at=created_at,
                    updated_at=updated_at
                ))

        projects.sort(key=lambda p: p.updated_at, reverse=True)
        return ProjectListResponse(projects=projects)

    def get_project(self, project_id: str) -> Optional[ProjectResponse]:
        try:
            workspace_dir = self.workspace_mgr.get_workspace_dir(project_id)
        except Exception:
            return None

        if not workspace_dir.exists():
            return None

        meta = self._read_project_metadata(project_id)
        now = datetime.now(timezone.utc)
        if meta:
            name = meta.get("name", project_id)
            created_at = parse_dt(meta.get("created_at", now.isoformat()))
            updated_at = parse_dt(meta.get("updated_at", now.isoformat()))
        else:
            name = project_id.replace("-", " ").title()
            created_at = datetime.fromtimestamp(workspace_dir.stat().st_ctime, tz=timezone.utc)
            updated_at = datetime.fromtimestamp(workspace_dir.stat().st_mtime, tz=timezone.utc)

        return ProjectResponse(
            id=project_id,
            name=name,
            workspace_path=str(workspace_dir.resolve()),
            created_at=created_at,
            updated_at=updated_at
        )

    def create_project(self, name: str, template: Optional[str] = "demo-calculator") -> ProjectResponse:
        slug = "".join(c if c.isalnum() else "-" for c in name.lower()).strip("-")
        if not slug:
            slug = "project"
        project_id = f"{slug}-{uuid.uuid4().hex[:6]}"

        if template == "demo-calculator":
            self.workspace_mgr.init_demo_calculator_workspace(project_id)
        else:
            self.workspace_mgr.ensure_workspace(project_id)

        self._save_project_metadata(project_id, name, template=template or "blank")
        return self.get_project(project_id)  # type: ignore

    def ensure_default_demo_project(self) -> str:
        demo_id = "demo-calculator"
        demo_path = self.workspace_mgr.root_path / demo_id
        if not demo_path.exists():
            self.workspace_mgr.init_demo_calculator_workspace(demo_id)
            self._save_project_metadata(demo_id, "Demo Calculator Project", template="demo-calculator")
        return demo_id


project_service = ProjectService()
