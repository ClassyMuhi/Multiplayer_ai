import logging
import re
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

from app.core.config import settings
from app.models.schemas import (
    ProjectMemoryItem,
    FileNode,
    RelevantFileContext,
    MessageRecord,
    AgentContextPayload
)
from app.workspace.manager import workspace_manager, WorkspaceManager
from app.database.repository import repository, DatabaseRepository
from app.memory.memory_service import memory_service, MemoryService

logger = logging.getLogger("summit.context_builder")

STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than",
    "that", "that's", "the", "their", "theirs", "them", "themselves", "then",
    "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've",
    "this", "those", "through", "to", "too", "under", "until", "up", "very", "was",
    "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what",
    "what's", "when", "when's", "where", "where's", "which", "while", "who",
    "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you",
    "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves",
    "please", "can", "help", "want", "need", "make", "create", "add", "fix", "update"
}


class ContextBuilder:
    """
    Intelligent Project Context Builder (Phase 3).
    Assembles comprehensive, prioritized project intelligence before an agent run:
    1. Persistent Project Summary
    2. Current Developer Request
    3. Semantic Project Memories (Prioritized by category & importance)
    4. Project Directory Structure Tree
    5. Smart Relevant File Context
    6. Recent Conversation History
    7. Standard Autonomous Agent Instructions
    """

    def __init__(
        self,
        memory_svc: Optional[MemoryService] = None,
        workspace_mgr: Optional[WorkspaceManager] = None,
        repo: Optional[DatabaseRepository] = None
    ):
        self.memory_svc = memory_svc or memory_service
        self.workspace_mgr = workspace_mgr or workspace_manager
        self.repo = repo or repository

    @staticmethod
    def build_memory_context(memories: List[ProjectMemoryItem], max_total_chars: int = 2500) -> str:
        """
        Converts a list of retrieved ProjectMemoryItems into a markdown context block.
        Returns an empty string if no memories are provided.
        Maintains full backwards compatibility with Phase 2.
        """
        if not memories:
            return ""

        # Filter active memories
        active_memories = [m for m in memories if m.is_active]
        if not active_memories:
            return ""

        # Priority weights for sorting memories
        category_priority = {
            "architecture_decision": 1,
            "coding_convention": 2,
            "important_context": 3,
            "bug_solution": 4,
            "project_fact": 5,
            "dependency_information": 6,
            "conversation_summary": 7,
            "general": 8
        }

        # Sort memories by importance and category priority
        def memory_sort_key(m: ProjectMemoryItem):
            cat = m.memory_type or m.category or "general"
            prio = category_priority.get(cat, 9)
            imp = getattr(m, "importance", 0.5) or 0.5
            sim = getattr(m, "similarity_score", 0.5) or 0.5
            return (prio, -imp, -sim)

        sorted_memories = sorted(active_memories, key=memory_sort_key)

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

        grouped: Dict[str, List[ProjectMemoryItem]] = {}
        for mem in sorted_memories:
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
                clean_content = content.strip()
                if len(clean_content) > 300:
                    clean_content = clean_content[:297] + "..."

                item_line = f"• {clean_content}"
                if total_chars + len(item_line) > max_total_chars:
                    lines.append("• [Additional context truncated to fit prompt budget]")
                    break

                lines.append(item_line)
                total_chars += len(item_line) + 1

            lines.append("")

        lines.append("---")
        return "\n".join(lines)

    def extract_keywords(self, prompt: str) -> List[str]:
        """Extracts meaningful search keywords from the user prompt."""
        # Find explicit file names (e.g. calculator.py, auth.js)
        tokens = re.findall(r"[a-zA-Z0-9_\-\.]+", prompt.lower())
        keywords = []
        for t in tokens:
            # Strip trailing punctuation
            clean = t.strip(".")
            if len(clean) >= 2 and clean not in STOP_WORDS:
                keywords.append(clean)
        return keywords

    def flatten_file_tree(self, nodes: List[FileNode]) -> List[FileNode]:
        """Flattens a recursive FileNode tree into a list of file nodes."""
        result = []
        for node in nodes:
            if not node.is_directory:
                result.append(node)
            elif node.children:
                result.extend(self.flatten_file_tree(node.children))
        return result

    async def select_relevant_files(
        self,
        project_id: str,
        prompt: str,
        max_files: Optional[int] = None,
        max_file_size: Optional[int] = None
    ) -> List[RelevantFileContext]:
        """
        Smart lightweight file discovery:
        1. Analyzes user prompt for file mentions, keywords, and topics.
        2. Scores workspace files based on relevance.
        3. Reads top candidate files within configured budget limits.
        """
        limit_files = max_files or settings.MAX_CONTEXT_FILES
        limit_size = max_file_size or settings.MAX_FILE_SIZE

        try:
            tree_nodes = self.workspace_mgr.list_files_tree(project_id, max_depth=10)
        except Exception as e:
            logger.warning(f"Could not list file tree for project {project_id}: {e}")
            return []

        all_files = self.flatten_file_tree(tree_nodes)
        if not all_files:
            return []

        prompt_lower = prompt.lower()
        keywords = self.extract_keywords(prompt)

        scored_files: List[Tuple[float, FileNode]] = []
        for f in all_files:
            path_lower = f.path.lower()
            name_lower = f.name.lower()
            stem_lower = Path(f.name).stem.lower()
            score = 0.0

            # 1. Exact path or exact filename mentioned in prompt
            if path_lower in prompt_lower:
                score += 15.0
            elif name_lower in prompt_lower:
                score += 10.0
            elif len(stem_lower) > 2 and stem_lower in prompt_lower:
                score += 6.0

            # 2. Keyword hits in filename or parent path
            for kw in keywords:
                if kw in name_lower:
                    score += 4.0
                elif kw in path_lower:
                    score += 2.0

            # 3. Topic associations
            if ("test" in prompt_lower or "pytest" in prompt_lower) and ("test" in path_lower or "test" in name_lower):
                score += 5.0
            if ("calc" in prompt_lower or "math" in prompt_lower) and "calc" in path_lower:
                score += 4.0
            if ("auth" in prompt_lower or "login" in prompt_lower or "jwt" in prompt_lower) and ("auth" in path_lower or "user" in path_lower):
                score += 5.0
            if ("model" in prompt_lower or "schema" in prompt_lower or "database" in prompt_lower) and ("model" in path_lower or "db" in path_lower):
                score += 4.0
            if ("api" in prompt_lower or "endpoint" in prompt_lower or "route" in prompt_lower) and ("api" in path_lower or "route" in path_lower):
                score += 4.0

            # 4. Standard entrypoints if no specific hits
            if name_lower in ("readme.md", "main.py", "app.py", "calculator.py"):
                score += 0.5

            if score > 0.0:
                scored_files.append((score, f))

        # Sort by score descending
        scored_files.sort(key=lambda x: x[0], reverse=True)
        top_candidates = scored_files[:limit_files]

        # If no files scored above 0, include main source or README if available
        if not top_candidates and all_files:
            for f in all_files:
                if f.name.lower() in ("calculator.py", "main.py", "app.py", "readme.md"):
                    top_candidates.append((1.0, f))
                    if len(top_candidates) >= 2:
                        break

        relevant_contexts: List[RelevantFileContext] = []
        for score, f in top_candidates:
            try:
                content, size, is_binary = await self.workspace_mgr.read_file(project_id, f.path)
                if is_binary:
                    continue

                clean_content = content
                if len(clean_content) > limit_size:
                    clean_content = clean_content[:limit_size] + f"\n... [File truncated at {limit_size} characters]"

                relevant_contexts.append(RelevantFileContext(
                    path=f.path,
                    content=clean_content,
                    size=size,
                    score=round(score, 2)
                ))
            except Exception as e:
                logger.warning(f"Failed to read candidate file '{f.path}': {e}")

        return relevant_contexts

    def format_project_tree(self, nodes: List[FileNode], max_lines: int = 40) -> str:
        """Formats the file node tree into a clean, human-readable hierarchy."""
        lines = []

        def recurse(node_list: List[FileNode], prefix: str = ""):
            for idx, node in enumerate(node_list):
                if len(lines) >= max_lines:
                    lines.append(f"{prefix}... [Additional files omitted]")
                    return

                is_last = (idx == len(node_list) - 1)
                connector = "└── " if is_last else "├── "
                sub_prefix = prefix + ("    " if is_last else "│   ")

                if node.is_directory:
                    lines.append(f"{prefix}{connector}{node.name}/")
                    if node.children:
                        recurse(node.children, sub_prefix)
                else:
                    size_str = f" ({node.size} B)" if node.size is not None else ""
                    lines.append(f"{prefix}{connector}{node.name}{size_str}")

        recurse(nodes)
        return "\n".join(lines) if lines else "[Empty Workspace]"

    def format_conversation_history(
        self,
        project_id: str,
        limit: int = 10,
        max_chars: int = 4000
    ) -> Tuple[str, List[MessageRecord]]:
        """Retrieves and formats recent conversation messages."""
        try:
            raw_msgs = self.repo.get_project_messages(project_id=project_id, limit=limit)
        except Exception as e:
            logger.warning(f"Could not retrieve conversation messages for project {project_id}: {e}")
            return "", []

        if not raw_msgs:
            return "", []

        # Take last `limit` messages
        recent_raw = raw_msgs[-limit:]
        records = [MessageRecord(**m) for m in recent_raw]

        lines = []
        total_len = 0
        for m in records:
            speaker = "Developer" if m.role == "user" else ("Assistant" if m.role == "assistant" else "System")
            if m.user_name and m.role == "user":
                speaker = f"Developer ({m.user_name})"
            clean_text = m.content.strip()
            if len(clean_text) > 300:
                clean_text = clean_text[:297] + "..."
            line = f"**{speaker}**: {clean_text}"
            if total_len + len(line) > max_chars:
                lines.append("... [Older conversation context truncated]")
                break
            lines.append(line)
            total_len += len(line) + 1

        return "\n".join(lines), records

    async def build_full_context(
        self,
        project_id: str,
        user_prompt: str,
        user_id: Optional[str] = None
    ) -> AgentContextPayload:
        """
        Assembles full project-aware context according to Phase 3 specifications:
        1. Project Summary
        2. Current Request
        3. Relevant Memories
        4. Project Structure Tree
        5. Relevant Files
        6. Recent Conversation
        7. Operating Instructions
        """
        # 1. Project Summary
        summary = ""
        try:
            summary = self.repo.get_project_summary(project_id) or ""
        except Exception as e:
            logger.warning(f"Failed to load project summary for {project_id}: {e}")

        # 2. Semantic Memories
        memories: List[ProjectMemoryItem] = []
        try:
            memories = self.memory_svc.search_memories(
                project_id=project_id,
                query=user_prompt,
                top_k=settings.MEMORY_TOP_K
            )
        except Exception as e:
            logger.warning(f"Failed to retrieve semantic memories for {project_id}: {e}")

        memory_context_block = self.build_memory_context(memories, max_total_chars=3000)

        # 3. Project Structure Tree
        tree_text = ""
        try:
            tree_nodes = self.workspace_mgr.list_files_tree(project_id, max_depth=6)
            tree_text = self.format_project_tree(tree_nodes)
        except Exception as e:
            logger.warning(f"Failed to load project tree for {project_id}: {e}")
            tree_text = "[Workspace tree unavailable]"

        # 4. Smart Relevant Files
        relevant_files: List[RelevantFileContext] = []
        try:
            relevant_files = await self.select_relevant_files(
                project_id=project_id,
                prompt=user_prompt,
                max_files=settings.MAX_CONTEXT_FILES,
                max_file_size=settings.MAX_FILE_SIZE
            )
        except Exception as e:
            logger.warning(f"Failed to select relevant files for {project_id}: {e}")

        # 5. Recent Conversation
        conv_text, message_records = self.format_conversation_history(
            project_id=project_id,
            limit=settings.CONVERSATION_CONTEXT_LIMIT
        )

        # 6. Compose Structured Prompt
        sections = []

        sections.append("================ PROJECT CONTEXT ================")

        if summary:
            sections.append(f"### PROJECT SUMMARY\n{summary}")

        sections.append(f"### CURRENT DEVELOPER REQUEST\n{user_prompt}")

        if memory_context_block:
            sections.append(f"### RELEVANT PROJECT MEMORIES\n{memory_context_block}")

        if tree_text:
            sections.append(f"### PROJECT STRUCTURE\n```\n{tree_text}\n```")

        if relevant_files:
            file_blocks = []
            for rf in relevant_files:
                file_blocks.append(f"#### File: `{rf.path}`\n```\n{rf.content}\n```")
            sections.append("### RELEVANT PROJECT FILES\n" + "\n\n".join(file_blocks))

        if conv_text:
            sections.append(f"### RECENT CONVERSATION CONTEXT\n{conv_text}")

        sections.append(
            "### INSTRUCTIONS & GUIDELINES\n"
            "- Work strictly within the current isolated project workspace.\n"
            "- Use the available tools (`read_file`, `write_file`, `run_terminal`) to inspect and modify files.\n"
            "- Respect established architecture decisions, coding conventions, and existing patterns.\n"
            "- Do not invent nonexistent files or APIs when existing files can be inspected.\n"
            "- Verify your changes by running tests using `run_terminal` before completing."
        )

        sections.append("=================================================")

        full_prompt = "\n\n".join(sections)

        # Enforce total context budget limit
        max_budget = settings.MAX_CONTEXT_CHARS
        if len(full_prompt) > max_budget:
            logger.warning(f"[CONTEXT] Context exceeded budget ({len(full_prompt)} > {max_budget}), truncating.")
            full_prompt = full_prompt[:max_budget - 100] + "\n\n[Context truncated to fit budget limit]"

        logger.info(
            f"[CONTEXT] project={project_id} memories={len(memories)} files={len(relevant_files)} chars={len(full_prompt)}"
        )

        return AgentContextPayload(
            project_id=project_id,
            project_summary=summary,
            current_request=user_prompt,
            memories=memories,
            project_tree=tree_text,
            relevant_files=relevant_files,
            recent_messages=message_records,
            formatted_prompt=full_prompt
        )


context_builder = ContextBuilder()
