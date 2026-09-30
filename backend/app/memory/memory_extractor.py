import json
import logging
import re
from typing import Optional, Dict, Any, List

from app.core.config import settings
from app.memory.memory_service import memory_service, MemoryService

logger = logging.getLogger("summit.memory_extractor")


class MemoryExtractor:
    """
    Extracts durable, high-value project facts, architecture decisions,
    and coding conventions from completed agent tasks.
    Filters out transient noise, trivial chat, and tool execution logs.
    """

    def __init__(self, service: Optional[MemoryService] = None):
        self.memory_svc = service or memory_service

        # Transient / trivial phrases that should never become permanent memory
        self.trivial_patterns = [
            r"^(ok|okay|sure|done|thanks|thank you|hello|hi|yes|no)\b",
            r"^run\s+(pytest|tests|tests/\S+)",
            r"^(please\s+)?(fix|check|view|open|show|run|update|delete|modify)\s+(this|file|code|this\s+file|this\s+code)(\s+please)?$",
            r"^completed\b",
            r"^working\s+on\s+it"
        ]


    def is_trivial(self, text: str) -> bool:
        """Checks if text contains only ephemeral or low-information content."""
        clean = text.strip().lower()
        if len(clean) < 10:
            return True

        for pat in self.trivial_patterns:
            if re.search(pat, clean):
                return True
        return False

    def extract_heuristic_memory(self, prompt: str, outcome_summary: str) -> Optional[Dict[str, Any]]:
        """
        Extracts structured memory using pattern-matching heuristics on prompt and outcome.
        """
        p_lower = prompt.lower()
        s_lower = outcome_summary.lower()

        # Check for architecture/framework decisions
        if any(term in p_lower for term in ["framework", "architecture", "database", "orm", "library", "stack"]):
            return {
                "memory_type": "architecture_decision",
                "content": f"Decision: {prompt.strip()} -> {outcome_summary.strip()[:200]}",
                "importance": 0.85
            }

        # Check for conventions or patterns
        if any(term in p_lower for term in ["convention", "style", "format", "structure", "standard", "pattern"]):
            return {
                "memory_type": "coding_convention",
                "content": f"Convention: {prompt.strip()} -> {outcome_summary.strip()[:200]}",
                "importance": 0.8
            }

        # Check for bug solution / error handling
        if any(term in p_lower or term in s_lower for term in ["fix", "bug", "error", "exception", "failed", "crash"]):
            return {
                "memory_type": "bug_solution",
                "content": f"Bug Resolution: {outcome_summary.strip()[:250]}",
                "importance": 0.75
            }

        # Check for significant feature additions
        if any(term in p_lower for term in ["add", "implement", "create", "build"]):
            return {
                "memory_type": "project_fact",
                "content": f"Implemented: {outcome_summary.strip()[:200]}",
                "importance": 0.7
            }

        return None

    async def extract_llm_memory(self, prompt: str, outcome_summary: str) -> Optional[Dict[str, Any]]:
        """
        Uses LLM with LiteLLM to extract structured memory if API key is present.
        """
        api_key = settings.OPENAI_API_KEY or settings.ANTHROPIC_API_KEY or settings.OPENHANDS_API_KEY
        if not api_key:
            return None

        import litellm

        system_instruction = (
            "You are a Project Memory Extraction Engine. Analyze the developer instruction and outcome. "
            "If it contains a lasting architecture decision, coding convention, project fact, or bug solution, "
            "extract it as JSON. If it's trivial (simple question, one-off test, ephemeral chat), return should_remember=false.\n"
            "JSON Format:\n"
            "{\n"
            '  "should_remember": true/false,\n'
            '  "memory_type": "architecture_decision"|"coding_convention"|"project_fact"|"bug_solution"|"important_context",\n'
            '  "content": "concise, factual summary of the rule/decision/fact",\n'
            '  "importance": 0.0 to 1.0\n'
            "}"
        )

        user_content = f"Developer prompt: {prompt}\nAgent outcome: {outcome_summary}"

        try:
            response = await litellm.acompletion(
                model=settings.SUMMIT_MODEL,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_content}
                ],
                api_key=api_key,
                temperature=0.1
            )
            raw = response.choices[0].message.content.strip()
            # Extract JSON substring
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                if data.get("should_remember") and data.get("content"):
                    return data
        except Exception as e:
            logger.warning(f"LLM memory extraction failed ({e}), falling back to heuristics.")

        return None

    async def extract_and_save(
        self,
        project_id: str,
        user_prompt: str,
        outcome_summary: str,
        user_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Coordinates extraction and persists any extracted memory to MemoryService.
        """
        if self.is_trivial(user_prompt):
            logger.debug(f"[MEMORY EXTRACTOR] Ignored trivial prompt: '{user_prompt}'")
            return None

        # 1. Try LLM extraction if key available
        extracted = None
        has_key = bool(settings.OPENAI_API_KEY or settings.ANTHROPIC_API_KEY or settings.OPENHANDS_API_KEY)
        if has_key:
            extracted = await self.extract_llm_memory(user_prompt, outcome_summary)

        # 2. Fall back to heuristic extraction
        if not extracted:
            extracted = self.extract_heuristic_memory(user_prompt, outcome_summary)

        if not extracted or not extracted.get("content"):
            return None

        content = extracted["content"]
        mem_type = extracted.get("memory_type", "project_fact")

        try:
            saved = self.memory_svc.add_memory(
                project_id=project_id,
                content=content,
                memory_type=mem_type,
                source="agent_task_extraction",
                created_by=user_id or "agent"
            )
            logger.info(f"[MEMORY EXTRACTOR] Automatically saved memory for project={project_id}: '{content[:60]}...'")
            return saved.model_dump()
        except Exception as e:
            logger.error(f"Error persisting extracted memory: {e}")
            return None


memory_extractor = MemoryExtractor()
