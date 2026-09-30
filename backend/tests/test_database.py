import os
import tempfile
import pytest
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.database.repository import DatabaseRepository
from app.database.models import (
    Project,
    User,
    ProjectMember,
    ConversationMessage,
    AgentRun,
    FileChange,
    ProjectMemory
)


@pytest.fixture
def temp_db():
    """Creates a temporary SQLite database file and repository for testing."""
    temp_dir = tempfile.mkdtemp()
    db_file = Path(temp_dir) / "test_app.db"
    db_url = f"sqlite:///{db_file}"

    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    repo = DatabaseRepository()
    # Override session factory
    repo._session = lambda: _make_test_session(session_factory)

    yield repo, db_url, engine

    engine.dispose()
    if db_file.exists():
        db_file.unlink(missing_ok=True)


from contextlib import contextmanager


def _make_test_session(session_factory):
    @contextmanager
    def session_scope():
        session = session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    return session_scope()


# -------------------------------------------------------------------------
# Test Projects & Isolation
# -------------------------------------------------------------------------

def test_project_persistence(temp_db):
    repo, _, _ = temp_db

    # Create project
    proj = repo.create_project(
        id="proj-alpha",
        name="Project Alpha",
        workspace_path="/tmp/alpha",
        description="Alpha Description"
    )
    assert proj["id"] == "proj-alpha"
    assert proj["name"] == "Project Alpha"
    assert proj["description"] == "Alpha Description"

    # Retrieve project
    fetched = repo.get_project("proj-alpha")
    assert fetched is not None
    assert fetched["id"] == "proj-alpha"
    assert fetched["name"] == "Project Alpha"

    # Update project
    updated = repo.update_project("proj-alpha", name="Project Alpha v2", description="Updated desc")
    assert updated["name"] == "Project Alpha v2"
    assert updated["description"] == "Updated desc"

    # List projects
    projs = repo.list_projects()
    assert len(projs) == 1
    assert projs[0]["id"] == "proj-alpha"


def test_multiple_projects_isolation(temp_db):
    repo, _, _ = temp_db

    repo.create_project("proj-1", "Project 1", "/tmp/p1")
    repo.create_project("proj-2", "Project 2", "/tmp/p2")

    # Add messages to both
    repo.save_message("proj-1", role="user", content="Msg for P1")
    repo.save_message("proj-2", role="user", content="Msg for P2")

    # Add memories to both
    repo.save_project_memory("proj-1", key="framework", content="FastAPI")
    repo.save_project_memory("proj-2", key="framework", content="NextJS")

    # Verify isolation
    p1_msgs = repo.get_project_messages("proj-1")
    p2_msgs = repo.get_project_messages("proj-2")
    assert len(p1_msgs) == 1
    assert p1_msgs[0]["content"] == "Msg for P1"
    assert len(p2_msgs) == 1
    assert p2_msgs[0]["content"] == "Msg for P2"

    p1_mems = repo.get_project_memories("proj-1")
    p2_mems = repo.get_project_memories("proj-2")
    assert len(p1_mems) == 1
    assert p1_mems[0]["value"] == "FastAPI"
    assert len(p2_mems) == 1
    assert p2_mems[0]["value"] == "NextJS"


# -------------------------------------------------------------------------
# Test Users & Membership
# -------------------------------------------------------------------------

def test_user_and_membership(temp_db):
    repo, _, _ = temp_db

    repo.create_project("proj-team", "Team Project", "/tmp/team")
    user = repo.create_user(id="dev-1", display_name="Alice")
    assert user["id"] == "dev-1"
    assert user["display_name"] == "Alice"

    # Add member
    member = repo.add_project_member("proj-team", "dev-1")
    assert member["project_id"] == "proj-team"
    assert member["user_id"] == "dev-1"

    # List members
    members = repo.get_project_members("proj-team")
    assert len(members) == 1
    assert members[0]["user_id"] == "dev-1"

    # Remove member
    removed = repo.remove_project_member("proj-team", "dev-1")
    assert removed is True
    assert len(repo.get_project_members("proj-team")) == 0


# -------------------------------------------------------------------------
# Test Conversation Messages
# -------------------------------------------------------------------------

def test_conversation_messages_pagination(temp_db):
    repo, _, _ = temp_db

    repo.create_project("proj-chat", "Chat Project", "/tmp/chat")

    for i in range(5):
        repo.save_message("proj-chat", role="user" if i % 2 == 0 else "assistant", content=f"Message {i}")

    # Limit 3
    msgs = repo.get_project_messages("proj-chat", limit=3, offset=0)
    assert len(msgs) == 3
    assert msgs[0]["content"] == "Message 0"
    assert msgs[2]["content"] == "Message 2"

    # Offset 3
    msgs_next = repo.get_project_messages("proj-chat", limit=3, offset=3)
    assert len(msgs_next) == 2
    assert msgs_next[0]["content"] == "Message 3"


# -------------------------------------------------------------------------
# Test Agent Runs
# -------------------------------------------------------------------------

def test_agent_runs_lifecycle(temp_db):
    repo, _, _ = temp_db

    repo.create_project("proj-agent", "Agent Project", "/tmp/agent")

    run = repo.create_agent_run(
        project_id="proj-agent",
        prompt="Add login page",
        status="running"
    )
    assert run["id"] is not None
    assert run["status"] == "running"
    assert run["completed_at"] is None

    # Update run to completed
    updated_run = repo.update_agent_run(run["id"], status="completed")
    assert updated_run["status"] == "completed"
    assert updated_run["completed_at"] is not None

    # Retrieve run
    fetched = repo.get_agent_run(run["id"])
    assert fetched["status"] == "completed"

    # Project runs
    runs = repo.get_project_agent_runs("proj-agent")
    assert len(runs) == 1
    assert runs[0]["id"] == run["id"]


# -------------------------------------------------------------------------
# Test File Changes
# -------------------------------------------------------------------------

def test_file_changes_recording(temp_db):
    repo, _, _ = temp_db

    repo.create_project("proj-files", "Files Project", "/tmp/files")

    fc = repo.record_file_change(
        project_id="proj-files",
        file_path="src/app.py",
        operation="modify",
        description="Refactored database logic"
    )
    assert fc["file_path"] == "src/app.py"
    assert fc["operation"] == "modify"

    changes = repo.get_project_file_changes("proj-files")
    assert len(changes) == 1
    assert changes[0]["file_path"] == "src/app.py"


# -------------------------------------------------------------------------
# Test Project Memories CRUD
# -------------------------------------------------------------------------

def test_project_memory_crud(temp_db):
    repo, _, _ = temp_db

    repo.create_project("proj-mem", "Mem Project", "/tmp/mem")

    # Create memory
    mem = repo.save_project_memory(
        project_id="proj-mem",
        key="db_type",
        content="SQLite for Phase 1",
        memory_type="architecture_decision"
    )
    assert mem["key"] == "db_type"
    assert mem["value"] == "SQLite for Phase 1"
    assert mem["memory_type"] == "architecture_decision"

    # Update memory by saving with same key
    mem_updated = repo.save_project_memory(
        project_id="proj-mem",
        key="db_type",
        content="SQLite with SQLAlchemy 2.0",
        memory_type="architecture_decision"
    )
    assert mem_updated["value"] == "SQLite with SQLAlchemy 2.0"

    # Retrieve memories
    all_mems = repo.get_project_memories("proj-mem")
    assert len(all_mems) == 1
    assert all_mems[0]["value"] == "SQLite with SQLAlchemy 2.0"

    # Filter by category/type
    arch_mems = repo.get_project_memories("proj-mem", category="architecture_decision")
    assert len(arch_mems) == 1
    other_mems = repo.get_project_memories("proj-mem", category="coding_convention")
    assert len(other_mems) == 0

    # Delete memory
    deleted = repo.delete_memory("proj-mem", "db_type")
    assert deleted is True
    assert len(repo.get_project_memories("proj-mem")) == 0


# -------------------------------------------------------------------------
# Test Physical SQLite File Persistence Across Sessions
# -------------------------------------------------------------------------

def test_sqlite_file_persistence_across_sessions():
    """
    Critical verification:
    1. Create data in SQLite file.
    2. Close database connection completely.
    3. Reopen new database connection to same file.
    4. Verify all records exist intact.
    """
    temp_dir = tempfile.mkdtemp()
    db_file = Path(temp_dir) / "persistent_test.db"
    db_url = f"sqlite:///{db_file}"

    # Session 1: Create schema and data
    engine1 = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine1)
    session_factory1 = sessionmaker(autocommit=False, autoflush=False, bind=engine1)

    repo1 = DatabaseRepository()
    repo1._session = lambda: _make_test_session(session_factory1)

    repo1.create_project(id="p-persist", name="Persistent Project", workspace_path="/tmp/persist")
    repo1.save_message("p-persist", role="user", content="Will I survive restart?")
    repo1.save_project_memory("p-persist", key="test_key", content="Saved state")

    # Close Session 1 engine completely
    engine1.dispose()

    # Session 2: Connect to the same SQLite file
    engine2 = create_engine(db_url, connect_args={"check_same_thread": False})
    session_factory2 = sessionmaker(autocommit=False, autoflush=False, bind=engine2)

    repo2 = DatabaseRepository()
    repo2._session = lambda: _make_test_session(session_factory2)

    # Verify project exists
    proj = repo2.get_project("p-persist")
    assert proj is not None
    assert proj["name"] == "Persistent Project"

    # Verify message survived
    msgs = repo2.get_project_messages("p-persist")
    assert len(msgs) == 1
    assert msgs[0]["content"] == "Will I survive restart?"

    # Verify memory survived
    mems = repo2.get_project_memories("p-persist")
    assert len(mems) == 1
    assert mems[0]["value"] == "Saved state"

    engine2.dispose()
    if db_file.exists():
        db_file.unlink(missing_ok=True)
