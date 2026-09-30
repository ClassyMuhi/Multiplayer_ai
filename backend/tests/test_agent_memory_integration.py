import tempfile
import shutil
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.database.repository import DatabaseRepository
from app.workspace.manager import WorkspaceManager
from app.memory.chroma_store import ChromaStore
from app.memory.memory_service import MemoryService
from app.memory.context_builder import ContextBuilder
from app.memory.memory_extractor import MemoryExtractor
from app.agent.summit_adapter import SummitAdapter
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
def integrated_system():
    temp_dir = tempfile.mkdtemp()
    base_path = Path(temp_dir)
    db_file = base_path / "app.db"
    chroma_dir = base_path / "chroma"
    workspace_root = base_path / "workspaces"

    # 1. Database
    engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    repo = DatabaseRepository()
    repo._session = lambda: _make_test_session(session_factory)

    # 2. Workspace
    workspace_mgr = WorkspaceManager(root_path=workspace_root)

    # 3. Chroma
    chroma = ChromaStore(persist_dir=chroma_dir, collection_name="e2e_collection")

    # 4. MemoryService
    mem_service = MemoryService(chroma=chroma)
    mem_service.repo = repo

    # 5. Extractor
    extractor = MemoryExtractor(service=mem_service)

    # 6. Adapter
    adapter = SummitAdapter()
    adapter.workspace_mgr = workspace_mgr

    # Seed demo project
    proj_id = "test-e2e-proj"
    workspace_mgr.init_demo_calculator_workspace(proj_id)
    repo.create_project(
        id=proj_id,
        name="E2E Project",
        workspace_path=str(workspace_mgr.get_workspace_dir(proj_id))
    )

    yield adapter, mem_service, repo, extractor, proj_id, base_path

    engine.dispose()
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.asyncio
async def test_end_to_end_agent_memory_lifecycle(integrated_system):
    """
    End-to-end integration lifecycle test:
    1. Seed project architectural decision.
    2. Retrieve relevant memory before agent task.
    3. Verify ContextBuilder creates clean prompt context.
    4. Execute agent task.
    5. Automatically extract new learning from task.
    6. Search and verify both initial memory and new learning exist and are retrievable.
    """
    adapter, mem_service, repo, extractor, proj_id, _ = integrated_system

    # Step 1: Pre-populate an architectural decision
    mem_service.add_memory(
        project_id=proj_id,
        content="Always check for division by zero and raise ValueError.",
        memory_type="coding_convention",
        key="zero_division_rule"
    )

    # Step 2: Developer sends a prompt
    user_prompt = "Implement divide function for calculator with zero check."

    # Step 3: Semantic retrieval
    retrieved = mem_service.search_memories(project_id=proj_id, query=user_prompt, top_k=3)
    assert len(retrieved) >= 1
    assert "division by zero" in retrieved[0].content

    # Step 4: Build context
    context = ContextBuilder.build_memory_context(retrieved)
    assert "Coding Conventions & Style" in context
    assert "division by zero" in context

    # Step 5: Execute autonomous task with context
    workspace_dir = adapter.workspace_mgr.get_workspace_dir(proj_id)
    summary = await adapter._execute_autonomous_task(
        project_id=proj_id,
        workspace_dir=workspace_dir,
        user_prompt=user_prompt,
        memory_context=context
    )
    assert "Successfully implemented" in summary

    # Step 6: Post-task Memory Extraction
    extracted = await extractor.extract_and_save(
        project_id=proj_id,
        user_prompt=user_prompt,
        outcome_summary=summary
    )
    assert extracted is not None

    # Step 7: Verify both memories exist in the project
    all_memories = mem_service.list_memories(project_id=proj_id)
    assert len(all_memories) >= 2

    # Step 8: Semantic query for newly learned capability
    search_new = mem_service.search_memories(project_id=proj_id, query="What math functions are implemented?")
    assert len(search_new) >= 1
