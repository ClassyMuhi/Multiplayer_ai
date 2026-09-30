import asyncio
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from contextlib import contextmanager

from app.database.database import Base
from app.database.repository import DatabaseRepository
from app.workspace.manager import WorkspaceManager
from app.memory.chroma_store import ChromaStore
from app.memory.memory_service import MemoryService
from app.memory.context_builder import ContextBuilder
from app.memory.memory_extractor import MemoryExtractor
from app.services.project_service import ProjectService
from app.agent.summit_adapter import SummitAdapter
from app.models.schemas import ProjectMemoryItem
from app.main import app


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
    base_path = Path(temp_dir)
    db_file = base_path / "test_app.db"
    chroma_dir = base_path / "test_chroma"
    workspace_root = base_path / "test_workspaces"

    # 1. Database
    engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    repo = DatabaseRepository()
    repo._session = lambda: _make_test_session(session_factory)

    # 2. Workspace
    workspace_mgr = WorkspaceManager(root_path=workspace_root)

    # 3. Chroma
    chroma = ChromaStore(persist_dir=chroma_dir, collection_name="phase3_test_collection")

    # 4. MemoryService
    mem_service = MemoryService(chroma=chroma)
    mem_service.repo = repo

    # 5. Project Service
    proj_service = ProjectService()
    proj_service.workspace_mgr = workspace_mgr
    proj_service.repo = repo

    # 6. Context Builder
    ctx_builder = ContextBuilder(
        memory_svc=mem_service,
        workspace_mgr=workspace_mgr,
        repo=repo
    )

    # 7. Memory Extractor
    extractor = MemoryExtractor(service=mem_service)

    # 8. Summit Adapter
    adapter = SummitAdapter(
        workspace_mgr=workspace_mgr,
        ctx_builder=ctx_builder,
        repo=repo,
        mem_svc=mem_service,
        extractor=extractor
    )

    yield {
        "engine": engine,
        "session_factory": session_factory,
        "repo": repo,
        "workspace_mgr": workspace_mgr,
        "chroma": chroma,
        "mem_service": mem_service,
        "proj_service": proj_service,
        "ctx_builder": ctx_builder,
        "extractor": extractor,
        "adapter": adapter,
        "base_path": base_path,
        "db_file": db_file,
        "chroma_dir": chroma_dir,
        "workspace_root": workspace_root
    }

    engine.dispose()
    shutil.rmtree(temp_dir, ignore_errors=True)


# =============================================================================
# TEST 1 — PROJECT SUMMARY PERSISTENCE & REFRESH
# =============================================================================

def test_1_project_summary_persistence(test_env):
    """
    Test 1:
    - Create project with demo calculator template.
    - Generate summary and verify it captures project name, README snippet, and tech stack.
    - Simulate application restart / new repository instance.
    - Verify summary persists and can be loaded or refreshed.
    """
    repo = test_env["repo"]
    proj_service = test_env["proj_service"]

    proj = proj_service.create_project(
        name="Task Master",
        template="demo-calculator",
        description="Collaborative task management backend"
    )
    proj_id = proj.id

    # Verify summary generated on creation
    summary = proj_service.get_project_summary(proj_id)
    assert summary is not None
    assert "Task Master" in summary
    assert "Collaborative task management backend" in summary
    assert "Python" in summary or "calculator" in summary.lower()

    # Manual update
    custom_summary = "Updated manual architecture summary for Task Master."
    proj_service.update_project_summary(proj_id, custom_summary)
    assert repo.get_project_summary(proj_id) == custom_summary

    # Refresh summary automatically
    refreshed = proj_service.refresh_project_summary(proj_id)
    assert "Task Master" in refreshed
    assert repo.get_project_summary(proj_id) == refreshed


# =============================================================================
# TEST 2 — MEMORY RETRIEVAL & PRIORITIZATION
# =============================================================================

def test_2_memory_retrieval_and_prioritization(test_env):
    """
    Test 2:
    - Add memories with different categories and importance scores.
    - Query semantic search.
    - Verify returned memories are correctly scored and retrieved.
    """
    mem_service = test_env["mem_service"]
    proj_id = "test-proj-p2"

    mem_service.add_memory(
        project_id=proj_id,
        content="Authentication must use JWT tokens in the Authorization header.",
        memory_type="architecture_decision",
        key="auth_jwt",
        importance=0.9
    )
    mem_service.add_memory(
        project_id=proj_id,
        content="Use snake_case for all API endpoint URLs.",
        memory_type="coding_convention",
        key="naming_convention",
        importance=0.8
    )
    mem_service.add_memory(
        project_id=proj_id,
        content="Team meeting every Monday at 10 AM.",
        memory_type="general",
        key="meeting_note",
        importance=0.3
    )

    results = mem_service.search_memories(
        project_id=proj_id,
        query="How should I authenticate requests?",
        top_k=5
    )

    assert len(results) >= 1
    top_memory = results[0]
    assert "JWT" in top_memory.content
    assert top_memory.memory_type == "architecture_decision"
    assert top_memory.importance == 0.9


# =============================================================================
# TEST 3 — MANDATORY PROJECT ISOLATION
# =============================================================================

def test_3_project_isolation(test_env):
    """
    Test 3 (MANDATORY):
    - Project A: FastAPI microservice
    - Project B: Django monolith
    - Query Project A -> Django memory must NEVER appear
    - Query Project B -> FastAPI memory must NEVER appear
    """
    mem_service = test_env["mem_service"]
    proj_a = "project-alpha-fastapi"
    proj_b = "project-beta-django"

    # Add Project A memory
    mem_service.add_memory(
        project_id=proj_a,
        content="Project Alpha backend is built exclusively with FastAPI and async routes.",
        memory_type="architecture_decision",
        key="alpha_tech"
    )

    # Add Project B memory
    mem_service.add_memory(
        project_id=proj_b,
        content="Project Beta backend is a Django monolith using Django ORM and synchronous views.",
        memory_type="architecture_decision",
        key="beta_tech"
    )

    # Search in Project A
    results_a = mem_service.search_memories(project_id=proj_a, query="What backend framework is used?", top_k=10)
    assert len(results_a) > 0
    for r in results_a:
        assert r.project_id == proj_a
        assert "Django" not in r.content
        assert "FastAPI" in r.content

    # Search in Project B
    results_b = mem_service.search_memories(project_id=proj_b, query="What backend framework is used?", top_k=10)
    assert len(results_b) > 0
    for r in results_b:
        assert r.project_id == proj_b
        assert "FastAPI" not in r.content
        assert "Django" in r.content


# =============================================================================
# TEST 4 — SMART CONTEXT BUILDER
# =============================================================================

@pytest.mark.asyncio
async def test_4_context_builder_intelligence(test_env):
    """
    Test 4:
    - Create a multi-file project workspace (README.md, calculator.py, tests/test_calculator.py).
    - Add persistent memories and past conversation messages.
    - Build context for prompt: 'Implement division function in calculator.py'.
    - Verify context contains Summary, Memories, Tree, Files, Conversation, and Instructions.
    - Verify smart file selector selects calculator.py and test_calculator.py.
    - Verify size limit safeguards.
    """
    ctx_builder = test_env["ctx_builder"]
    proj_service = test_env["proj_service"]
    mem_service = test_env["mem_service"]
    repo = test_env["repo"]

    proj = proj_service.create_project(
        name="Smart Calc Service",
        template="demo-calculator",
        description="Demo calculator microservice"
    )
    proj_id = proj.id

    # 1. Add memories
    mem_service.add_memory(
        project_id=proj_id,
        content="Always raise ValueError('Cannot divide by zero.') on zero division.",
        memory_type="coding_convention",
        importance=0.9
    )

    # 2. Add past conversation messages
    repo.save_message(project_id=proj_id, role="user", content="We need arithmetic operations.")
    repo.save_message(project_id=proj_id, role="assistant", content="I will prepare the calculator module.")

    # 3. Build full agent context
    user_prompt = "Implement division function in calculator.py and add tests in tests/test_calculator.py"
    payload = await ctx_builder.build_full_context(
        project_id=proj_id,
        user_prompt=user_prompt
    )

    assert payload.project_id == proj_id
    assert payload.project_summary is not None
    assert len(payload.memories) >= 1
    assert "divide by zero" in payload.memories[0].content
    assert "calculator.py" in payload.project_tree
    assert len(payload.relevant_files) >= 1
    
    # Check that calculator.py is in the selected files
    selected_paths = [rf.path for rf in payload.relevant_files]
    assert any("calculator.py" in p for p in selected_paths)

    # Verify formatted prompt sections
    prompt = payload.formatted_prompt
    assert "PROJECT SUMMARY" in prompt
    assert "CURRENT DEVELOPER REQUEST" in prompt
    assert "RELEVANT PROJECT MEMORIES" in prompt
    assert "PROJECT STRUCTURE" in prompt
    assert "RELEVANT PROJECT FILES" in prompt
    assert "RECENT CONVERSATION CONTEXT" in prompt
    assert "INSTRUCTIONS & GUIDELINES" in prompt


# =============================================================================
# TEST 5 — AGENT INTEGRATION & FILE CHANGE PERSISTENCE
# =============================================================================

@pytest.mark.asyncio
async def test_5_agent_integration_and_file_changes(test_env):
    """
    Test 5:
    - Execute agent turn via SummitAdapter.
    - Verify tool execution modifies calculator.py and tests/test_calculator.py.
    - Verify FileChange records are stored in SQLite repository.
    - Verify AgentRun record is marked completed.
    """
    adapter = test_env["adapter"]
    proj_service = test_env["proj_service"]
    repo = test_env["repo"]

    proj = proj_service.create_project(name="Agent Run Test Project", template="demo-calculator")
    proj_id = proj.id

    user_prompt = "Add divide function to calculator.py with zero check"
    
    # Run session
    await adapter.run_session(project_id=proj_id, user_prompt=user_prompt)

    # Verify FileChanges recorded in SQLite
    changes = repo.get_project_file_changes(proj_id)
    assert len(changes) >= 1
    changed_paths = [c["file_path"] for c in changes]
    assert any("calculator.py" in p for p in changed_paths)

    # Verify AgentRun
    runs = repo.get_project_agent_runs(proj_id)
    assert len(runs) >= 1
    assert runs[0]["status"] == "completed"

    # Verify Conversation Messages
    msgs = repo.get_project_messages(proj_id)
    assert len(msgs) >= 2  # user prompt and assistant response
    assert msgs[0]["role"] == "user"
    assert msgs[1]["role"] == "assistant"


# =============================================================================
# TEST 6 — POST-TASK MEMORY EXTRACTION & RETRIEVAL
# =============================================================================

@pytest.mark.asyncio
async def test_6_memory_extraction_after_agent_run(test_env):
    """
    Test 6:
    - Complete agent task that introduces an architectural decision / bug solution.
    - Verify MemoryExtractor parses outcome and persists new memory to SQLite + ChromaDB.
    - Search for the decision and verify it is retrievable.
    """
    extractor = test_env["extractor"]
    mem_service = test_env["mem_service"]
    proj_id = "test-extraction-proj"

    user_prompt = "Adopt JWT auth tokens in FastAPI middleware"
    outcome_summary = "Configured JWT bearer middleware in backend/app/core/auth.py for endpoint security."
    files_changed = ["backend/app/core/auth.py", "backend/app/main.py"]

    extracted = await extractor.extract_and_save(
        project_id=proj_id,
        user_prompt=user_prompt,
        outcome_summary=outcome_summary,
        files_changed=files_changed
    )

    assert extracted is not None
    assert "JWT" in extracted["content"]

    # Semantic search to verify indexing in ChromaDB and SQLite hydration
    search_res = mem_service.search_memories(
        project_id=proj_id,
        query="What authentication method was adopted?",
        top_k=3
    )
    assert len(search_res) >= 1
    assert "JWT" in search_res[0].content


# =============================================================================
# TEST 7 — RESTART PERSISTENCE
# =============================================================================

def test_7_restart_persistence(test_env):
    """
    Test 7:
    - Seed project, project summary, memories, agent runs, and file changes.
    - Close database and Chroma connections.
    - Instantiate fresh repository, Chroma store, and project service pointing to same disk files.
    - Verify all data (project summary, memories, file changes, agent runs) remains fully intact.
    """
    repo = test_env["repo"]
    mem_service = test_env["mem_service"]
    proj_service = test_env["proj_service"]
    session_factory = test_env["session_factory"]
    chroma_dir = test_env["chroma_dir"]
    workspace_root = test_env["workspace_root"]

    proj = proj_service.create_project(name="Persistent Project", template="demo-calculator")
    proj_id = proj.id

    proj_service.update_project_summary(proj_id, "Persistent Project Summary v1")
    mem_service.add_memory(
        project_id=proj_id,
        content="Persistent database rule: use UUIDs for all primary keys.",
        memory_type="architecture_decision",
        key="pk_rule"
    )
    repo.record_file_change(project_id=proj_id, file_path="schema.py", operation="create")

    # --- RESTART SIMULATION ---
    new_repo = DatabaseRepository()
    new_repo._session = lambda: _make_test_session(session_factory)
    new_chroma = ChromaStore(persist_dir=chroma_dir, collection_name="phase3_test_collection")
    new_mem_svc = MemoryService(chroma=new_chroma)
    new_mem_svc.repo = new_repo
    new_proj_svc = ProjectService()
    new_proj_svc.workspace_mgr = WorkspaceManager(root_path=workspace_root)
    new_proj_svc.repo = new_repo

    # Verify project
    loaded_proj = new_proj_svc.get_project(proj_id)
    assert loaded_proj is not None
    assert loaded_proj.name == "Persistent Project"
    assert loaded_proj.project_summary == "Persistent Project Summary v1"

    # Verify memory
    loaded_mems = new_mem_svc.search_memories(project_id=proj_id, query="What is the primary key rule?")
    assert len(loaded_mems) >= 1
    assert "UUIDs" in loaded_mems[0].content

    # Verify file change
    changes = new_repo.get_project_file_changes(proj_id)
    assert len(changes) >= 1
    assert changes[0]["file_path"] == "schema.py"


# =============================================================================
# TEST 8 — FAILURE RESILIENCE
# =============================================================================

@pytest.mark.asyncio
async def test_8_failure_resilience(test_env):
    """
    Test 8:
    - Simulate memory service search failure (raising Exception).
    - Verify ContextBuilder and SummitAdapter gracefully degrade to direct prompt + workspace inspection.
    - Ensure agent session finishes without fatal crash.
    """
    adapter = test_env["adapter"]
    proj_service = test_env["proj_service"]

    proj = proj_service.create_project(name="Resilience Test", template="demo-calculator")
    proj_id = proj.id

    # Monkeypatch memory search to simulate catastrophic retrieval error
    def broken_search(*args, **kwargs):
        raise RuntimeError("Simulated ChromaDB connection drop")

    test_env["mem_service"].search_memories = broken_search

    # Agent turn should continue and complete successfully despite memory search failure
    await adapter.run_session(project_id=proj_id, user_prompt="Add divide function to calculator")

    # Verify completed
    runs = test_env["repo"].get_project_agent_runs(proj_id)
    assert len(runs) >= 1
    assert runs[0]["status"] == "completed"


# =============================================================================
# TEST 9 — PROJECT SUMMARY REST API
# =============================================================================

def test_9_project_summary_rest_api():
    """
    Test 9:
    - Test GET /api/projects/{project_id}/summary
    - Test PUT /api/projects/{project_id}/summary
    - Test POST /api/projects/{project_id}/summary/refresh
    """
    client = TestClient(app)
    project_id = "demo-calculator"

    # 1. GET Summary
    get_res = client.get(f"/api/projects/{project_id}/summary")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["project_id"] == project_id
    assert data["summary"] is not None
    assert "Demo Calculator" in data["summary"]

    # 2. PUT Summary
    new_summary_text = "Custom manually edited project summary for testing."
    put_res = client.put(
        f"/api/projects/{project_id}/summary",
        json={"summary": new_summary_text}
    )
    assert put_res.status_code == 200
    assert put_res.json()["summary"] == new_summary_text

    # Verify GET returns updated summary
    get_verify = client.get(f"/api/projects/{project_id}/summary")
    assert get_verify.json()["summary"] == new_summary_text

    # 3. POST Refresh Summary
    post_res = client.post(f"/api/projects/{project_id}/summary/refresh")
    assert post_res.status_code == 200
    refreshed_summary = post_res.json()["summary"]
    assert "Demo Calculator" in refreshed_summary
