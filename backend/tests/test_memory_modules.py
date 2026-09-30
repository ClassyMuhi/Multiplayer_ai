import tempfile
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.database.repository import repository
from app.memory.conversation_memory import conversation_memory
from app.memory.project_memory import project_memory
from app.models.schemas import MessageRecord, ProjectMemoryItem
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


@pytest.fixture(autouse=True)
def setup_test_db():
    temp_dir = tempfile.mkdtemp()
    db_file = Path(temp_dir) / "test_memory.db"
    db_url = f"sqlite:///{db_file}"

    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Wire repository to temp db
    orig_session = repository._session
    repository._session = lambda: _make_test_session(session_factory)

    # Ensure test project exists
    repository.create_project("test-mem-proj", "Test Memory Project", "/tmp/mem-proj")

    yield

    repository._session = orig_session
    engine.dispose()
    if db_file.exists():
        db_file.unlink(missing_ok=True)


def test_conversation_memory_interface():
    # Save user message
    msg1 = conversation_memory.save_message(
        project_id="test-mem-proj",
        role="user",
        content="Create a login component",
        user_id="dev-u1",
        user_name="Alice"
    )
    assert isinstance(msg1, MessageRecord)
    assert msg1.content == "Create a login component"
    assert msg1.role == "user"
    assert msg1.user_name == "Alice"

    # Save assistant response
    msg2 = conversation_memory.save_message(
        project_id="test-mem-proj",
        role="assistant",
        content="Implemented login component in src/login.py"
    )
    assert isinstance(msg2, MessageRecord)
    assert msg2.role == "assistant"

    # Fetch messages
    history = conversation_memory.get_messages("test-mem-proj")
    assert len(history) == 2
    assert history[0].content == "Create a login component"
    assert history[1].content == "Implemented login component in src/login.py"


def test_project_memory_interface():
    # Save project decision
    item1 = project_memory.save_memory(
        project_id="test-mem-proj",
        key="auth_strategy",
        value="Use JWT tokens in HTTP-only cookies",
        category="architecture_decision"
    )
    assert isinstance(item1, ProjectMemoryItem)
    assert item1.key == "auth_strategy"
    assert item1.value == "Use JWT tokens in HTTP-only cookies"

    # Retrieve all memories
    all_items = project_memory.get_memories("test-mem-proj")
    assert len(all_items) == 1
    assert all_items[0].key == "auth_strategy"

    # Retrieve by category
    filtered = project_memory.get_memories("test-mem-proj", category="architecture_decision")
    assert len(filtered) == 1
    empty = project_memory.get_memories("test-mem-proj", category="coding_convention")
    assert len(empty) == 0

    # Delete memory
    deleted = project_memory.delete_memory("test-mem-proj", "auth_strategy")
    assert deleted is True
    assert len(project_memory.get_memories("test-mem-proj")) == 0
