import pytest
from pathlib import Path
import tempfile
import shutil

from app.workspace.manager import (
    WorkspaceManager,
    WorkspaceSecurityError,
    WorkspaceNotFoundError
)


@pytest.fixture
def temp_workspace_mgr():
    temp_dir = tempfile.mkdtemp()
    mgr = WorkspaceManager(root_path=Path(temp_dir))
    yield mgr
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_init_demo_calculator(temp_workspace_mgr):
    project_id = "test-calc"
    workspace_dir = temp_workspace_mgr.init_demo_calculator_workspace(project_id)
    assert workspace_dir.exists()
    assert (workspace_dir / "calculator.py").exists()
    assert (workspace_dir / "tests" / "test_calculator.py").exists()
    assert (workspace_dir / "README.md").exists()


def test_path_traversal_prevention(temp_workspace_mgr):
    project_id = "test-sec"
    temp_workspace_mgr.ensure_workspace(project_id)

    # Attacks attempting to break out with ../
    with pytest.raises(WorkspaceSecurityError):
        temp_workspace_mgr.validate_safe_path(project_id, "../../etc/passwd")

    with pytest.raises(WorkspaceSecurityError):
        temp_workspace_mgr.validate_safe_path(project_id, "../outside.txt")

    # Invalid project IDs
    with pytest.raises(WorkspaceSecurityError):
        temp_workspace_mgr.get_workspace_dir("../evil")


def test_file_tree_listing(temp_workspace_mgr):
    project_id = "test-tree"
    temp_workspace_mgr.init_demo_calculator_workspace(project_id)

    tree = temp_workspace_mgr.list_files_tree(project_id)
    names = [node.name for node in tree]
    assert "calculator.py" in names
    assert "README.md" in names
    assert "tests" in names

    # Check tests folder children
    tests_folder = next(n for n in tree if n.name == "tests")
    assert tests_folder.is_directory
    assert any(child.name == "test_calculator.py" for child in tests_folder.children)


@pytest.mark.asyncio
async def test_read_and_write_file(temp_workspace_mgr):
    project_id = "test-io"
    temp_workspace_mgr.ensure_workspace(project_id)

    file_path = "src/hello.py"
    test_content = "print('hello from test')"

    bytes_written, new_ver = await temp_workspace_mgr.write_file(project_id, file_path, test_content)
    assert bytes_written > 0
    assert new_ver >= 1

    content, size, is_binary, version = await temp_workspace_mgr.read_file(project_id, file_path)
    assert content == test_content
    assert size == bytes_written
    assert not is_binary
    assert version == new_ver

