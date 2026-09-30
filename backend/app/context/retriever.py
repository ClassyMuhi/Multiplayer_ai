import logging
from pathlib import Path
from typing import List, Dict, Any
from app.workspace.manager import workspace_manager
from app.database.repository import repository

logger = logging.getLogger("summit.context")


class ContextRetriever:
    """
    Scans repository files and constructs codebase-aware LLM context budgets
    combining project metadata, memories, recent conversation history, and relevant code files.
    """

    def __init__(self):
        self.workspace_mgr = workspace_manager

    def find_relevant_files(self, project_id: str, query: str, max_files: int = 5) -> List[str]:
        """Identifies file paths in the workspace most relevant to user prompt."""
        try:
            tree = self.workspace_mgr.list_files_tree(project_id)
        except Exception:
            return []

        all_files: List[str] = []

        def flatten(nodes):
            for n in nodes:
                if not n.is_directory:
                    all_files.append(n.path)
                elif n.children:
                    flatten(n.children)

        flatten(tree)

        if not all_files:
            return []

        query_terms = [t.lower() for t in query.split() if len(t) > 2]
        scored_files = []

        for rel_path in all_files:
            score = 0
            path_lower = rel_path.lower()

            # High priority entry files
            if any(path_lower.endswith(k) for k in ["readme.md", "main.py", "app.py", "index.ts", "package.json"]):
                score += 2

            # Match path words
            for term in query_terms:
                if term in path_lower:
                    score += 5

            scored_files.append((score, rel_path))

        scored_files.sort(key=lambda x: x[0], reverse=True)
        selected = [p for s, p in scored_files[:max_files]]
        return selected

    async def build_context(self, project_id: str, user_prompt: str) -> str:
        """Constructs full prompt context for LLM agent."""
        # 1. Project Memories
        memories = repository.get_memories(project_id)
        mem_str = "No stored project memory."
        if memories:
            mem_items = [f"- [{m['category'].upper()}] {m['key']}: {m['value']}" for m in memories]
            mem_str = "\n".join(mem_items)

        # 2. Recent Messages History
        messages = repository.get_messages(project_id, limit=10)
        hist_str = ""
        if messages:
            hist_items = [f"{m['role'].upper()} ({m.get('user_name') or 'Agent'}): {m['content']}" for m in messages[-6:]]
            hist_str = "\n".join(hist_items)

        # 3. Relevant Codebase Files
        relevant_paths = self.find_relevant_files(project_id, user_prompt, max_files=4)
        file_contents = []

        for p in relevant_paths:
            try:
                content, _, is_bin = await self.workspace_mgr.read_file(project_id, p)
                if not is_bin:
                    # Truncate very long files to fit context window
                    lines = content.splitlines()
                    if len(lines) > 200:
                        content_snippet = "\n".join(lines[:200]) + f"\n... [Truncated {len(lines)-200} lines]"
                    else:
                        content_snippet = content
                    file_contents.append(f"--- FILE: {p} ---\n{content_snippet}\n--- END FILE ---")
            except Exception as e:
                logger.warning(f"Could not read {p} for context: {e}")

        codebase_str = "\n\n".join(file_contents) if file_contents else "No code files read."

        context_prompt = f"""=== PROJECT PERSISTENT MEMORY ===
{mem_str}

=== RECENT CONVERSATION ===
{hist_str}

=== CODEBASE CONTEXT ===
{codebase_str}

=== USER CURRENT PROMPT ===
{user_prompt}
"""
        return context_prompt


context_retriever = ContextRetriever()
