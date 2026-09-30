from datetime import datetime, timezone
import pytest

from app.memory.context_builder import ContextBuilder
from app.models.schemas import ProjectMemoryItem


def test_context_builder_empty():
    cb = ContextBuilder()
    assert cb.build_memory_context([]) == ""


def test_context_builder_formatting():
    cb = ContextBuilder()
    now = datetime.now(timezone.utc)

    memories = [
        ProjectMemoryItem(
            id="m1",
            project_id="p1",
            memory_type="architecture_decision",
            key="db",
            value="Backend uses SQLite with SQLAlchemy.",
            content="Backend uses SQLite with SQLAlchemy.",
            category="architecture_decision",
            created_at=now,
            updated_at=now
        ),
        ProjectMemoryItem(
            id="m2",
            project_id="p1",
            memory_type="coding_convention",
            key="routes",
            value="API routes must be organized by domain feature.",
            content="API routes must be organized by domain feature.",
            category="coding_convention",
            created_at=now,
            updated_at=now
        )
    ]

    context = cb.build_memory_context(memories)
    assert "PERSISTENT PROJECT MEMORY & ARCHITECTURE CONTEXT" in context
    assert "Architecture & Design Decisions" in context
    assert "Backend uses SQLite with SQLAlchemy." in context
    assert "Coding Conventions & Style" in context
    assert "API routes must be organized by domain feature." in context


def test_context_builder_skips_inactive():
    cb = ContextBuilder()
    now = datetime.now(timezone.utc)

    memories = [
        ProjectMemoryItem(
            id="m1",
            project_id="p1",
            memory_type="architecture_decision",
            value="Old deprecated framework",
            content="Old deprecated framework",
            is_active=False,
            created_at=now,
            updated_at=now
        )
    ]

    context = cb.build_memory_context(memories)
    assert context == ""
