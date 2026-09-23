import os
import shutil
from pathlib import Path
from typing import List, Optional, Tuple
import aiofiles

from app.core.config import settings
from app.models.schemas import FileNode


class WorkspaceSecurityError(Exception):
    """Raised when an unsafe path or path traversal attempt is detected."""
    pass


class WorkspaceNotFoundError(Exception):
    """Raised when a project workspace directory does not exist."""
    pass


class WorkspaceManager:
    """
    Manages isolated project workspaces on the filesystem.
    Enforces path traversal safety and performs file I/O operations.
    """

    def __init__(self, root_path: Optional[Path] = None):
        self.root_path = (root_path or settings.workspace_root_path).resolve()
        self.root_path.mkdir(parents=True, exist_ok=True)

    def get_workspace_dir(self, project_id: str) -> Path:
        """
        Returns the resolved workspace directory path for a project ID.
        Validates that project_id cannot contain path traversal.
        """
        if not project_id or ".." in project_id or "/" in project_id or "\\" in project_id:
            raise WorkspaceSecurityError(f"Invalid project ID: {project_id}")

        workspace_dir = (self.root_path / project_id).resolve()
        # Verify workspace directory is within root_path
        try:
            workspace_dir.relative_to(self.root_path)
        except ValueError:
            raise WorkspaceSecurityError("Workspace path resolves outside the root workspace directory.")

        return workspace_dir

    def ensure_workspace(self, project_id: str) -> Path:
        """Ensures the workspace exists on disk and returns its path."""
        workspace_dir = self.get_workspace_dir(project_id)
        workspace_dir.mkdir(parents=True, exist_ok=True)
        return workspace_dir

    def validate_safe_path(self, project_id: str, relative_path: str) -> Path:
        """
        Validates and resolves a relative path within the project workspace.
        Raises WorkspaceSecurityError if the path escapes the workspace.
        """
        workspace_dir = self.get_workspace_dir(project_id)
        if not workspace_dir.exists():
            raise WorkspaceNotFoundError(f"Workspace for project '{project_id}' does not exist.")

        # Strip leading slashes to prevent root-relative interpretation
        clean_rel = relative_path.lstrip("/\\")
        target_path = (workspace_dir / clean_rel).resolve()

        # Strict security check: target_path must have workspace_dir as parent/ancestor
        try:
            target_path.relative_to(workspace_dir)
        except ValueError:
            raise WorkspaceSecurityError(
                f"Path traversal detected: '{relative_path}' escapes workspace '{project_id}'"
            )

        return target_path

    def list_files_tree(self, project_id: str, max_depth: int = 10) -> List[FileNode]:
        """
        Recursively lists all files and directories in the workspace as a tree of FileNode.
        Excludes hidden/virtualenv/git folders.
        """
        workspace_dir = self.get_workspace_dir(project_id)
        if not workspace_dir.exists():
            raise WorkspaceNotFoundError(f"Workspace '{project_id}' does not exist.")

        ignored_names = {
            ".git", ".venv", "venv", "__pycache__", ".pytest_cache",
            "node_modules", ".next", ".DS_Store"
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

    async def read_file(self, project_id: str, relative_path: str) -> Tuple[str, int, bool]:
        """
        Reads a file's content from the project workspace.
        Returns (content_str, size_bytes, is_binary).
        """
        file_path = self.validate_safe_path(project_id, relative_path)
        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError(f"File '{relative_path}' not found in project '{project_id}'.")

        size = file_path.stat().st_size

        # Check for binary file
        try:
            async with aiofiles.open(file_path, mode="r", encoding="utf-8") as f:
                content = await f.read()
                return content, size, False
        except UnicodeDecodeError:
            # Fallback for binary files
            return "<binary file content>", size, True

    async def write_file(self, project_id: str, relative_path: str, content: str) -> int:
        """
        Writes text content to a file in the workspace, creating parent directories if needed.
        Returns the number of bytes written.
        """
        file_path = self.validate_safe_path(project_id, relative_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(file_path, mode="w", encoding="utf-8") as f:
            await f.write(content)

        return file_path.stat().st_size

    def delete_file(self, project_id: str, relative_path: str) -> bool:
        """Deletes a file or directory within the workspace."""
        file_path = self.validate_safe_path(project_id, relative_path)
        if not file_path.exists():
            return False

        if file_path.is_dir():
            shutil.rmtree(file_path)
        else:
            file_path.unlink()
        return True

    def init_demo_calculator_workspace(self, project_id: str) -> Path:
        """Seeds a demo calculator project in the workspace."""
        workspace_dir = self.ensure_workspace(project_id)

        # 1. calculator.py
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

        # 2. tests/test_calculator.py
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

        # 3. README.md
        readme_content = '''# Demo Calculator Project

A sample Python project for testing the **Summit AI Coding Agent**.

## Features
- Basic math operations: `add`, `subtract`, `multiply`
- Pytest test suite in `tests/test_calculator.py`

## Try asking Summit:
> "Add a divide function to calculator.py with zero division error handling and write tests for it in tests/test_calculator.py, then run pytest."
'''
        (workspace_dir / "README.md").write_text(readme_content, encoding="utf-8")

        return workspace_dir


# Global workspace manager instance
workspace_manager = WorkspaceManager()
