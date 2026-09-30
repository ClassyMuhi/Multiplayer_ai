import tempfile
from pathlib import Path
import pytest
import shutil

from app.memory.chroma_store import ChromaStore


@pytest.fixture
def temp_chroma_store():
    """Provides an isolated ChromaStore in a temporary directory."""
    temp_dir = tempfile.mkdtemp()
    store = ChromaStore(persist_dir=Path(temp_dir), collection_name="test_collection")
    yield store
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_chroma_add_and_get(temp_chroma_store):
    store = temp_chroma_store

    added = store.add_document(
        doc_id="mem-1",
        document="We use PostgreSQL as our primary database.",
        metadata={"project_id": "proj-a", "memory_type": "architecture_decision"}
    )
    assert added is True

    doc = store.get_document("mem-1")
    assert doc is not None
    assert doc["id"] == "mem-1"
    assert "PostgreSQL" in doc["document"]
    assert doc["metadata"]["project_id"] == "proj-a"


def test_chroma_project_isolation(temp_chroma_store):
    """
    Critical Project Isolation Test:
    Project A (FastAPI) and Project B (Django) must NEVER leak into each other's searches.
    """
    store = temp_chroma_store

    store.add_document(
        doc_id="mem-a",
        document="The backend uses FastAPI framework.",
        metadata={"project_id": "proj-alpha", "memory_type": "architecture_decision"}
    )
    store.add_document(
        doc_id="mem-b",
        document="The backend uses Django framework.",
        metadata={"project_id": "proj-beta", "memory_type": "architecture_decision"}
    )

    # Search in Project Alpha
    alpha_hits = store.search(project_id="proj-alpha", query="Which backend framework is used?")
    assert len(alpha_hits) >= 1
    assert all(h["metadata"]["project_id"] == "proj-alpha" for h in alpha_hits)
    assert "FastAPI" in alpha_hits[0]["document"]
    assert "Django" not in alpha_hits[0]["document"]

    # Search in Project Beta
    beta_hits = store.search(project_id="proj-beta", query="Which backend framework is used?")
    assert len(beta_hits) >= 1
    assert all(h["metadata"]["project_id"] == "proj-beta" for h in beta_hits)
    assert "Django" in beta_hits[0]["document"]
    assert "FastAPI" not in beta_hits[0]["document"]


def test_chroma_update_and_delete(temp_chroma_store):
    store = temp_chroma_store

    store.add_document(
        doc_id="mem-up",
        document="Initial rule: Use tabs for indentation.",
        metadata={"project_id": "proj-test", "memory_type": "coding_convention"}
    )

    # Update document
    store.update_document(
        doc_id="mem-up",
        document="Updated rule: Use 4 spaces for indentation.",
        metadata={"project_id": "proj-test", "memory_type": "coding_convention"}
    )

    doc = store.get_document("mem-up")
    assert doc is not None
    assert "4 spaces" in doc["document"]

    # Delete document
    deleted = store.delete_document("mem-up")
    assert deleted is True
    assert store.get_document("mem-up") is None


def test_chroma_persistence_across_instances():
    """
    Persistence Test:
    1. Write document to persistent directory.
    2. Close client.
    3. Open new ChromaStore pointing to same directory.
    4. Verify document is present and searchable.
    """
    temp_dir = tempfile.mkdtemp()
    persist_path = Path(temp_dir)

    # Instance 1: write memory
    store1 = ChromaStore(persist_dir=persist_path, collection_name="persist_col")
    store1.add_document(
        doc_id="p-mem-1",
        document="Critical persistent architectural rule: Always use HTTPS.",
        metadata={"project_id": "proj-p", "memory_type": "architecture_decision"}
    )

    # Instance 2: read from same disk directory
    store2 = ChromaStore(persist_dir=persist_path, collection_name="persist_col")
    hits = store2.search(project_id="proj-p", query="security and protocols")
    assert len(hits) >= 1
    assert hits[0]["id"] == "p-mem-1"
    assert "HTTPS" in hits[0]["document"]

    shutil.rmtree(temp_dir, ignore_errors=True)
