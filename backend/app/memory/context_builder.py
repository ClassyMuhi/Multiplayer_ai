import logging
from typing import List, Optional
from app.models.schemas import ProjectMemoryItem

logger = logging.getLogger("summit.context_builder")


class ContextBuilder:
    """
    Builds clean, structured prompt context from retrieved semantic project memories.
    Provides context to the AI agent while protecting prompt token limits.
    """

    @staticmethod
    def build_memory_context(memories: List[ProjectMemoryItem], max_total_chars: int = 2500) -> str:
        """
        Converts a list of retrieved ProjectMemoryItems into a markdown context block.
        Returns an empty string if no memories are provided.
        """
        if not memories:
            return ""

        # Filter active memories
        active_memories = [m for m in memories if m.is_active]
        if not active_memories:
            return ""

        # Group by category / memory_type
        category_labels = {
            "architecture_decision": "Architecture & Design Decisions",
            "coding_convention": "Coding Conventions & Style",
            "project_fact": "Key Project Facts & Tech Stack",
            "bug_solution": "Known Issues & Bug Solutions",
            "important_context": "Important Project Context",
            "dependency_information": "Dependencies & Modules",
            "conversation_summary": "Previous Decisions Summary",
            "general": "General Project Notes"
        }

        grouped = {}
        for mem in active_memories:
            cat = mem.memory_type or mem.category or "general"
            grouped.setdefault(cat, []).append(mem)

        lines = [
            "---",
            "### PERSISTENT PROJECT MEMORY & ARCHITECTURE CONTEXT",
            "The following verified project memories have been retrieved from previous team interactions.",
            "Incorporate these established conventions, architecture rules, and facts into your solution:",
            ""
        ]

        total_chars = sum(len(l) for l in lines)

        for cat, items in grouped.items():
            label = category_labels.get(cat, cat.replace("_", " ").title())
            lines.append(f"#### {label}")

            for item in items:
                content = item.content or item.value or ""
                # Clean up single-line or multi-line content
                clean_content = content.strip()
                if len(clean_content) > 300:
                    clean_content = clean_content[:297] + "..."

                item_line = f"• {clean_content}"
                if item.similarity_score is not None:
                    # Optional relevance indicator (internal)
                    item_line = f"• {clean_content}"

                if total_chars + len(item_line) > max_total_chars:
                    lines.append("• [Additional context truncated to fit prompt budget]")
                    break

                lines.append(item_line)
                total_chars += len(item_line) + 1

            lines.append("")

        lines.append("---")
        return "\n".join(lines)


context_builder = ContextBuilder()
