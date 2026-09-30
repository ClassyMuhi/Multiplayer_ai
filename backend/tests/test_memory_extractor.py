import pytest
from app.memory.memory_extractor import MemoryExtractor


def test_memory_extractor_filters_trivial():
    extractor = MemoryExtractor()
    assert extractor.is_trivial("ok") is True
    assert extractor.is_trivial("thanks") is True
    assert extractor.is_trivial("run pytest") is True
    assert extractor.is_trivial("done") is True
    assert extractor.is_trivial("Please fix this file") is True

    # Meaningful text should NOT be trivial
    assert extractor.is_trivial("We decided to use Redis for session caching.") is False


def test_memory_extractor_heuristic_extraction():
    extractor = MemoryExtractor()

    # Architecture extraction
    arch_res = extractor.extract_heuristic_memory(
        prompt="Let's use PostgreSQL for our database architecture.",
        outcome_summary="Configured PostgreSQL connection in database.py"
    )
    assert arch_res is not None
    assert arch_res["memory_type"] == "architecture_decision"
    assert "PostgreSQL" in arch_res["content"]

    # Coding convention extraction
    conv_res = extractor.extract_heuristic_memory(
        prompt="Ensure all API responses follow snake_case JSON convention.",
        outcome_summary="Updated Pydantic aliases to snake_case."
    )
    assert conv_res is not None
    assert conv_res["memory_type"] == "coding_convention"

    # Bug solution extraction
    bug_res = extractor.extract_heuristic_memory(
        prompt="Fix the crash on divide by zero.",
        outcome_summary="Handled ZeroDivisionError in math_service.py"
    )
    assert bug_res is not None
    assert bug_res["memory_type"] == "bug_solution"
