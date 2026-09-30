import os
import shutil
from pathlib import Path
from typing import List, Optional, Tuple
import aiofiles

from app.core.config import settings
from app.models.schemas import FileNode
from app.database.repository import repository


class WorkspaceSecurityError(Exception):
    """Raised when an unsafe path or path traversal attempt is detected."""
    pass


class WorkspaceNotFoundError(Exception):
    """Raised when a project workspace directory does not exist."""
    pass


class FileConflictError(Exception):
    """Raised when concurrent editing conflict is detected."""
    def __init__(self, path: str, server_version: int, expected_version: int, server_content: str):
        clean_path = path.replace("\\", "/")
        super().__init__(
            f"Conflict in '{clean_path}': server version is {server_version}, expected {expected_version}."
        )
        self.path = clean_path
        self.server_version = server_version
        self.expected_version = expected_version
        self.server_content = server_content


class WorkspaceManager:
    """
    Manages isolated project workspaces on the filesystem.
    Enforces path traversal safety, performs file I/O, file versioning, and conflict detection.
    """

    def __init__(self, root_path: Optional[Path] = None):
        self.root_path = (root_path or settings.workspace_root_path).resolve()
        self.root_path.mkdir(parents=True, exist_ok=True)

    def get_workspace_dir(self, project_id: str) -> Path:
        if not project_id or ".." in project_id or "/" in project_id or "\\" in project_id:
            raise WorkspaceSecurityError(f"Invalid project ID: {project_id}")

        workspace_dir = (self.root_path / project_id).resolve()
        try:
            workspace_dir.relative_to(self.root_path)
        except ValueError:
            raise WorkspaceSecurityError("Workspace path resolves outside the root workspace directory.")

        return workspace_dir

    def ensure_workspace(self, project_id: str) -> Path:
        workspace_dir = self.get_workspace_dir(project_id)
        workspace_dir.mkdir(parents=True, exist_ok=True)
        return workspace_dir

    def validate_safe_path(self, project_id: str, relative_path: str) -> Path:
        workspace_dir = self.get_workspace_dir(project_id)
        if not workspace_dir.exists():
            raise WorkspaceNotFoundError(f"Workspace for project '{project_id}' does not exist.")

        clean_rel = relative_path.lstrip("/\\")
        target_path = (workspace_dir / clean_rel).resolve()

        try:
            target_path.relative_to(workspace_dir)
        except ValueError:
            raise WorkspaceSecurityError(
                f"Path traversal detected: '{relative_path}' escapes workspace '{project_id}'"
            )

        return target_path

    def list_files_tree(self, project_id: str, max_depth: int = 10) -> List[FileNode]:
        workspace_dir = self.get_workspace_dir(project_id)
        if not workspace_dir.exists():
            raise WorkspaceNotFoundError(f"Workspace '{project_id}' does not exist.")

        ignored_names = {
            ".git", ".venv", "venv", "__pycache__", ".pytest_cache",
            "node_modules", ".next", ".DS_Store", ".summit"
        }

        def build_tree(current_dir: Path, current_depth: int) -> List[FileNode]:
            if current_depth > max_depth:
                return []

            nodes: List[FileNode] = []
            try:
                entries = sorted(list(current_dir.iterdir()), key=lambda e: (not e.is_dir(), e.name.lower()))
            except (PermissionError, FileNotFoundError):
                return []

            for entry in entries:
                if entry.name in ignored_names:
                    continue

                rel_path = str(entry.relative_to(workspace_dir)).replace("\\", "/")

                if entry.is_dir():
                    children = build_tree(entry, current_depth + 1)
                    nodes.append(FileNode(
                        name=entry.name,
                        path=rel_path,
                        is_directory=True,
                        children=children
                    ))
                else:
                    try:
                        size = entry.stat().st_size
                    except (OSError, PermissionError):
                        size = 0

                    nodes.append(FileNode(
                        name=entry.name,
                        path=rel_path,
                        is_directory=False,
                        size=size
                    ))

            return nodes

        return build_tree(workspace_dir, 1)

    def get_file_version(self, project_id: str, relative_path: str) -> int:
        clean_rel = relative_path.replace("\\", "/").lstrip("/")
        return repository.get_file_version(project_id, clean_rel)

    async def read_file(self, project_id: str, relative_path: str) -> Tuple[str, int, bool, int]:
        """Reads a file and returns (content_str, size_bytes, is_binary, version)."""
        file_path = self.validate_safe_path(project_id, relative_path)
        clean_rel = relative_path.replace("\\", "/").lstrip("/")

        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError(f"File '{relative_path}' not found in project '{project_id}'.")

        size = file_path.stat().st_size
        version = repository.get_file_version(project_id, clean_rel)

        try:
            async with aiofiles.open(file_path, mode="r", encoding="utf-8") as f:
                content = await f.read()
                return content, size, False, version
        except UnicodeDecodeError:
            return "<binary file content>", size, True, version

    async def write_file(
        self,
        project_id: str,
        relative_path: str,
        content: str,
        expected_version: Optional[int] = None,
        user_id: Optional[str] = None
    ) -> Tuple[int, int]:
        """
        Writes text content to a file. Checks for version conflict if expected_version provided.
        Returns (bytes_written, new_version).
        """
        clean_rel = relative_path.replace("\\", "/").lstrip("/")
        file_path = self.validate_safe_path(project_id, relative_path)

        # Conflict check if expected_version is provided and file exists
        if expected_version is not None and file_path.exists():
            current_version = repository.get_file_version(project_id, clean_rel)
            if current_version != expected_version:
                server_content, _, _, _ = await self.read_file(project_id, clean_rel)
                raise FileConflictError(
                    path=clean_rel,
                    server_version=current_version,
                    expected_version=expected_version,
                    server_content=server_content
                )

        file_path.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(file_path, mode="w", encoding="utf-8") as f:
            await f.write(content)

        new_version = repository.update_file_version(project_id, clean_rel, content, updated_by=user_id)
        bytes_written = file_path.stat().st_size
        return bytes_written, new_version

    def delete_file(self, project_id: str, relative_path: str) -> bool:
        file_path = self.validate_safe_path(project_id, relative_path)
        if not file_path.exists():
            return False

        if file_path.is_dir():
            shutil.rmtree(file_path)
        else:
            file_path.unlink()
        return True

    def init_demo_calculator_workspace(self, project_id: str) -> Path:
        workspace_dir = self.ensure_workspace(project_id)

        calc_content = '''"""
Calculator Module for Summit AI Coding Agent Demo
"""

def add(a: float, b: float) -> float:
    """Returns the sum of a and b."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Returns the difference of a and b."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Returns the product of a and b."""
    return a * b
'''
        (workspace_dir / "calculator.py").write_text(calc_content, encoding="utf-8")
        repository.update_file_version(project_id, "calculator.py", calc_content)

        tests_dir = workspace_dir / "tests"
        tests_dir.mkdir(exist_ok=True)
        test_content = '''"""
Unit tests for Calculator Module
"""
import pytest
from calculator import add, subtract, multiply


def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0


def test_subtract():
    assert subtract(10, 4) == 6
    assert subtract(0, 5) == -5


def test_multiply():
    assert multiply(3, 7) == 21
    assert multiply(-2, 4) == -8
'''
        (tests_dir / "test_calculator.py").write_text(test_content, encoding="utf-8")
        repository.update_file_version(project_id, "tests/test_calculator.py", test_content)

        readme_content = '''# Demo Calculator Project

A sample Python project for testing the **Summit AI Coding Agent**.

## Features
- Basic math operations: `add`, `subtract`, `multiply`
- Pytest test suite in `tests/test_calculator.py`
'''
        (workspace_dir / "README.md").write_text(readme_content, encoding="utf-8")
        repository.update_file_version(project_id, "README.md", readme_content)

        return workspace_dir


workspace_manager = WorkspaceManager()
