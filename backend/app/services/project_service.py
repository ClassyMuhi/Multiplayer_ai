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
                project_summary=p.get("project_summary"),
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
            project_summary=p.get("project_summary"),
            workspace_path=p["workspace_path"],
            created_at=p["created_at"],
            updated_at=p["updated_at"]
        )

    def generate_project_summary(self, project_id: str) -> str:
        """
        Generates a concise, structured project summary from real workspace assets:
        - README file
        - Workspace file structure
        - Dependencies / tech stack configuration
        - High-importance architecture decisions and project facts
        """
        project = self.repo.get_project(project_id)
        proj_name = project.get("name", project_id) if project else project_id
        proj_desc = (project.get("description") or "").strip() if project else ""

        summary_parts = []
        summary_parts.append(f"Project: {proj_name}")
        if proj_desc:
            summary_parts.append(f"Description: {proj_desc}")

        workspace_dir = self.workspace_mgr.ensure_workspace(project_id)

        # 1. Inspect README
        readme_candidates = ["README.md", "readme.md", "README.txt", "README"]
        for r_name in readme_candidates:
            r_file = workspace_dir / r_name
            if r_file.exists() and r_file.is_file():
                try:
                    content = r_file.read_text(encoding="utf-8", errors="ignore").strip()
                    if content:
                        # Extract first few non-empty paragraphs
                        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
                        readme_snippet = "\n".join(paragraphs[:3])
                        if len(readme_snippet) > 600:
                            readme_snippet = readme_snippet[:597] + "..."
                        summary_parts.append(f"Overview (from README):\n{readme_snippet}")
                        break
                except Exception:
                    pass

        # 2. Inspect Tech Stack & Config Files
        tech_stack = []
        if (workspace_dir / "requirements.txt").exists():
            tech_stack.append("Python (requirements.txt)")
        if (workspace_dir / "pyproject.toml").exists():
            tech_stack.append("Python (pyproject.toml)")
        if (workspace_dir / "package.json").exists():
            tech_stack.append("Node.js / JavaScript (package.json)")
        if (workspace_dir / "tsconfig.json").exists():
            tech_stack.append("TypeScript (tsconfig.json)")
        if (workspace_dir / "Dockerfile").exists():
            tech_stack.append("Docker containerization")

        # Check for pytest or tests dir
        if (workspace_dir / "tests").is_dir() or (workspace_dir / "pytest.ini").exists():
            tech_stack.append("Pytest test suite")

        if tech_stack:
            summary_parts.append("Technology & Tooling: " + ", ".join(tech_stack))

        # 3. Structure Summary
        try:
            tree_nodes = self.workspace_mgr.list_files_tree(project_id, max_depth=2)
            top_entries = [node.name + ("/" if node.is_directory else "") for node in tree_nodes[:12]]
            if top_entries:
                summary_parts.append("Key Structure: " + ", ".join(top_entries))
        except Exception:
            pass

        # 4. Include Key Architecture Memories from Database
        try:
            key_mems = self.repo.get_project_memories(project_id=project_id, active_only=True)
            arch_mems = [m for m in key_mems if m.get("memory_type") in ("architecture_decision", "project_fact", "coding_convention")]
            if arch_mems:
                mem_lines = [f"- {m['content'][:150]}" for m in arch_mems[:4]]
                summary_parts.append("Established Architecture & Rules:\n" + "\n".join(mem_lines))
        except Exception:
            pass

        full_summary = "\n\n".join(summary_parts)
        max_chars = settings.PROJECT_SUMMARY_MAX_CHARS
        if len(full_summary) > max_chars:
            full_summary = full_summary[:max_chars - 3] + "..."

        # Persist to SQLite
        self.repo.update_project_summary(project_id=project_id, summary=full_summary)
        return full_summary

    def get_project_summary(self, project_id: str) -> Optional[str]:
        """Retrieves or lazily generates project summary for a given project."""
        summary = self.repo.get_project_summary(project_id)
        if not summary:
            # Generate summary if project exists
            p = self.repo.get_project(project_id)
            if p:
                summary = self.generate_project_summary(project_id)
        return summary

    def update_project_summary(self, project_id: str, summary: str) -> Optional[ProjectResponse]:
        """Manually updates the project summary."""
        clean_summary = summary.strip()
        self.repo.update_project_summary(project_id=project_id, summary=clean_summary)
        return self.get_project(project_id)

    def refresh_project_summary(self, project_id: str) -> str:
        """Forces regeneration of the project summary from workspace and memories."""
        return self.generate_project_summary(project_id)

    def create_project(
        self,
        name: str,
        template: Optional[str] = "demo-calculator",
        description: Optional[str] = None
    ) -> ProjectResponse:
        """Creates a new project record in DB, sets up workspace, and generates summary."""
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
        # Generate initial summary
        self.generate_project_summary(project_id)
        return self.get_project(project_id)  # type: ignore

    def ensure_default_demo_project(self) -> str:
        """Ensures the demo calculator project exists in both database and filesystem with summary."""
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
        # Ensure summary exists
        if not self.repo.get_project_summary(demo_id):
            self.generate_project_summary(demo_id)
        return demo_id


project_service = ProjectService()
