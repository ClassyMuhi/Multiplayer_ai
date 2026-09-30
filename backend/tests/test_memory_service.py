import tempfile
import shutil
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.database.repository import DatabaseRepository
from app.memory.chroma_store import ChromaStore
from app.memory.memory_service import MemoryService
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


@pytest.fixture
def test_env():
    temp_dir = tempfile.mkdtemp()
    db_file = Path(temp_dir) / "test_service.db"
    chroma_dir = Path(temp_dir) / "chroma"

    # SQLite setup
    engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    repo = DatabaseRepository()
    repo._session = lambda: _make_test_session(session_factory)

    # Chroma setup
    chroma = ChromaStore(persist_dir=chroma_dir, collection_name="test_service_col")

    # MemoryService setup
    service = MemoryService(chroma=chroma)
    service.repo = repo

    # Create test projects
    repo.create_project("proj-1", "Project 1", "/tmp/p1")
    repo.create_project("proj-2", "Project 2", "/tmp/p2")

    yield service, repo, chroma, temp_dir

    engine.dispose()
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_add_and_search_memory(test_env):
    service, repo, chroma, _ = test_env

    mem = service.add_memory(
        project_id="proj-1",
        content="The authentication token is stored in HTTP-only cookies.",
        memory_type="architecture_decision"
    )
    assert mem.id is not None
    assert mem.project_id == "proj-1"
    assert "HTTP-only cookies" in mem.content

    # Semantic search
    results = service.search_memories(
        project_id="proj-1",
        query="Where do we store the auth token?",
        top_k=3
    )
    assert len(results) >= 1
    assert results[0].id == mem.id
    assert "cookies" in results[0].content


def test_memory_service_project_isolation(test_env):
    service, _, _, _ = test_env

    service.add_memory(
        project_id="proj-1",
        content="Frontend is developed with Next.js App Router.",
        memory_type="project_fact"
    )
    service.add_memory(
        project_id="proj-2",
        content="Frontend is developed with Vue.js 3.",
        memory_type="project_fact"
    )

    # Search in Project 1
    p1_res = service.search_memories(project_id="proj-1", query="What frontend framework?")
    assert len(p1_res) >= 1
    assert all(r.project_id == "proj-1" for r in p1_res)
    assert "Next.js" in p1_res[0].content
    assert "Vue" not in p1_res[0].content

    # Search in Project 2
    p2_res = service.search_memories(project_id="proj-2", query="What frontend framework?")
    assert len(p2_res) >= 1
    assert all(r.project_id == "proj-2" for r in p2_res)
    assert "Vue" in p2_res[0].content
    assert "Next.js" not in p2_res[0].content


def test_memory_update_and_delete(test_env):
    service, _, _, _ = test_env

    mem = service.add_memory(
        project_id="proj-1",
        content="Old logging format is plain text.",
        memory_type="coding_convention"
    )

    # Update
    updated = service.update_memory(
        project_id="proj-1",
        memory_id=mem.id,
        content="New logging format is structured JSON."
    )
    assert updated is not None
    assert "structured JSON" in updated.content

    # Search confirms update in semantic index
    hits = service.search_memories(project_id="proj-1", query="logging format")
    assert len(hits) >= 1
    assert "structured JSON" in hits[0].content

    # Delete
    deleted = service.delete_memory(project_id="proj-1", memory_id_or_key=mem.id)
    assert deleted is True

    # Search confirms deletion
    hits_after = service.search_memories(project_id="proj-1", query="logging format")
    assert len(hits_after) == 0


def test_rebuild_project_memory_index(test_env):
    service, repo, chroma, _ = test_env

    # Add memories via service
    service.add_memory("proj-1", "Memory item A", "project_fact")
    service.add_memory("proj-1", "Memory item B", "coding_convention")

    # Clear Chroma collection manually to simulate index corruption
    chroma.reset()
    assert chroma.count("proj-1") == 0

    # Rebuild index from SQLite source of truth
    rebuilt_count = service.rebuild_project_memory_index(project_id="proj-1")
    assert rebuilt_count == 2

    # Verify search works again
    hits = service.search_memories(project_id="proj-1", query="Memory item A")
    assert len(hits) >= 1
