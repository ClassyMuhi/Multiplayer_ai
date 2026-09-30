import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from app.core.config import settings
from app.models.schemas import AgentStatusType, AgentContextPayload
from app.agent.event_handler import EventNormalizer
from app.agent.session_manager import session_manager
from app.workspace.manager import workspace_manager, WorkspaceManager
from app.memory.memory_service import memory_service, MemoryService
from app.memory.context_builder import context_builder, ContextBuilder
from app.memory.memory_extractor import memory_extractor, MemoryExtractor
from app.memory.conversation_memory import conversation_memory
from app.database.repository import repository, DatabaseRepository


logger = logging.getLogger("summit.adapter")


class SummitAdapter:
    """
    Summit Coding Agent Adapter (Phase 3).
    Orchestrates:
    1. Context Builder integration (Project Summary, Memories, Files, Tree, Conversation).
    2. Autonomous LLM or simulated tool calling loop (read_file, write_file, run_terminal).
    3. FileChange recording in SQLite repository.
    4. Real-time WebSocket event normalization and broadcasting.
    5. Post-task memory extraction with modified files context.
    6. Robust failure resilience and graceful degradation.
    """

    def __init__(
        self,
        workspace_mgr: Optional[WorkspaceManager] = None,
        ctx_builder: Optional[ContextBuilder] = None,
        repo: Optional[DatabaseRepository] = None,
        mem_svc: Optional[MemoryService] = None,
        extractor: Optional[MemoryExtractor] = None
    ):
        self.workspace_mgr = workspace_mgr or workspace_manager
        self.ctx_builder = ctx_builder or context_builder
        self.repo = repo or repository
        self.mem_svc = mem_svc or memory_service
        self.extractor = extractor or memory_extractor

    async def _broadcast(self, project_id: str, event):
        await session_manager.broadcast_event(project_id, event)

    async def execute_terminal_command(
        self,
        project_id: str,
        command: str,
        cwd: Path
    ) -> tuple[int, str]:
        """
        Executes a real terminal command inside the project workspace directory
        and captures stdout/stderr.
        """
        await self._broadcast(
            project_id,
            EventNormalizer.tool_call(
                project_id=project_id,
                tool="terminal",
                args={"command": command, "cwd": str(cwd)},
                description=f"Executing: {command}"
            )
        )

        try:
            # Use current python executable for python/pytest commands
            cmd_to_run = command
            if command.startswith("pytest") or command.startswith("python -m pytest"):
                py_exec = sys.executable
                cmd_to_run = f'"{py_exec}" -m pytest'
                if len(command.split(" ", 2)) > 2:
                    cmd_to_run += " " + command.split(" ", 2)[2]

            process = await asyncio.create_subprocess_shell(
                cmd_to_run,
                cwd=str(cwd),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()
            exit_code = process.returncode or 0
            output = stdout.decode("utf-8", errors="replace") + stderr.decode("utf-8", errors="replace")

            # Stream terminal output event
            await self._broadcast(
                project_id,
                EventNormalizer.terminal_output(
                    project_id=project_id,
                    command=command,
                    output=output,
                    exit_code=exit_code
                )
            )

            await self._broadcast(
                project_id,
                EventNormalizer.tool_result(
                    project_id=project_id,
                    tool="terminal",
                    result={"exit_code": exit_code, "output": output},
                    success=(exit_code == 0)
                )
            )

            return exit_code, output
        except Exception as e:
            err_msg = f"Error executing command '{command}': {str(e)}"
            logger.error(err_msg)
            await self._broadcast(
                project_id,
                EventNormalizer.error(project_id=project_id, error_message=err_msg)
            )
            return -1, err_msg

    async def _execute_real_llm_agent(
        self,
        project_id: str,
        workspace_dir: Path,
        user_prompt: str,
        memory_context: str = "",
        user_id: Optional[str] = None,
        context_payload: Optional[AgentContextPayload] = None
    ) -> Tuple[str, List[str]]:
        """
        Integrates with LLM API (OpenAI/Anthropic/LiteLLM) to perform tool calling loop
        augmented with intelligent project context (Phase 3).
        Returns (outcome_summary, files_modified_list).
        """
        import litellm
        import json

        api_key = settings.OPENAI_API_KEY or settings.ANTHROPIC_API_KEY or settings.OPENHANDS_API_KEY
        model = settings.SUMMIT_MODEL

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read content of a file in the workspace",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Relative file path"}
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Write/overwrite a file with full content in the workspace",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Relative file path"},
                            "content": {"type": "string", "description": "Full file content"}
                        },
                        "required": ["path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "run_terminal",
                    "description": "Run a shell/terminal command in the workspace directory (e.g. pytest)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "description": "Terminal command to run"}
                        },
                        "required": ["command"]
                    }
                }
            }
        ]

        system_instruction = (
            "You are Summit AI, an autonomous expert coding agent.\n"
            "You inspect project context and files, implement requested changes, "
            "create or update tests, run pytest in terminal, and verify your changes before completing."
        )

        if context_payload and context_payload.formatted_prompt:
            prompt_content = context_payload.formatted_prompt
        elif memory_context:
            prompt_content = f"{memory_context}\n\nUser Request: {user_prompt}"
        else:
            prompt_content = user_prompt

        messages = [
            {
                "role": "system",
                "content": system_instruction
            },
            {
                "role": "user",
                "content": prompt_content
            }
        ]

        files_modified: List[str] = []
        last_agent_message = "Task completed."
        max_turns = 10

        for turn in range(max_turns):
            await self._broadcast(
                project_id,
                EventNormalizer.agent_status(
                    project_id=project_id,
                    status=AgentStatusType.THINKING,
                    action=f"Reasoning step {turn + 1}"
                )
            )

            response = await litellm.acompletion(
                model=model,
                messages=messages,
                tools=tools,
                api_key=api_key
            )

            choice = response.choices[0]
            msg = choice.message

            if msg.content:
                last_agent_message = msg.content
                await self._broadcast(
                    project_id,
                    EventNormalizer.agent_message(project_id=project_id, message=msg.content)
                )

            # Check for tool calls
            tool_calls = getattr(msg, "tool_calls", None)
            if not tool_calls:
                break

            await self._broadcast(
                project_id,
                EventNormalizer.agent_status(
                    project_id=project_id,
                    status=AgentStatusType.EXECUTING,
                    action="Executing tools"
                )
            )

            messages.append(msg)

            for tc in tool_calls:
                fn_name = tc.function.name
                fn_args = json.loads(tc.function.arguments)

                if fn_name == "read_file":
                    rel_path = fn_args.get("path", "")
                    await self._broadcast(
                        project_id,
                        EventNormalizer.tool_call(
                            project_id=project_id,
                            tool="read_file",
                            args={"path": rel_path},
                            description=f"Reading file: {rel_path}"
                        )
                    )
                    content, size, _ = await self.workspace_mgr.read_file(project_id, rel_path)
                    await self._broadcast(
                        project_id,
                        EventNormalizer.tool_result(
                            project_id=project_id,
                            tool="read_file",
                            result={"path": rel_path, "size": size},
                            success=True
                        )
                    )
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "name": fn_name,
                        "content": content
                    })

                elif fn_name == "write_file":
                    rel_path = fn_args.get("path", "")
                    content = fn_args.get("content", "")
                    await self._broadcast(
                        project_id,
                        EventNormalizer.tool_call(
                            project_id=project_id,
                            tool="write_file",
                            args={"path": rel_path},
                            description=f"Writing file: {rel_path}"
                        )
                    )
                    await self.workspace_mgr.write_file(project_id, rel_path, content)
                    
                    # Record FileChange in SQLite
                    try:
                        self.repo.record_file_change(
                            project_id=project_id,
                            file_path=rel_path,
                            operation="modify",
                            user_id=user_id,
                            description=f"Modified by Summit AI Agent: {rel_path}"
                        )
                    except Exception as e:
                        logger.warning(f"Could not record FileChange for {rel_path}: {e}")

                    if rel_path not in files_modified:
                        files_modified.append(rel_path)

                    await self._broadcast(
                        project_id,
                        EventNormalizer.file_changed(project_id=project_id, path=rel_path)
                    )
                    await self._broadcast(
                        project_id,
                        EventNormalizer.tool_result(
                            project_id=project_id,
                            tool="write_file",
                            result={"path": rel_path, "status": "written"},
                            success=True
                        )
                    )
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "name": fn_name,
                        "content": f"Successfully wrote {len(content)} characters to {rel_path}"
                    })

                elif fn_name == "run_terminal":
                    cmd = fn_args.get("command", "")
                    exit_code, output = await self.execute_terminal_command(
                        project_id=project_id,
                        command=cmd,
                        cwd=workspace_dir
                    )
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "name": fn_name,
                        "content": f"Exit code: {exit_code}\nOutput:\n{output}"
                    })

        return last_agent_message, files_modified

    async def _execute_autonomous_task(
        self,
        project_id: str,
        workspace_dir: Path,
        user_prompt: str,
        memory_context: str = "",
        user_id: Optional[str] = None,
        context_payload: Optional[AgentContextPayload] = None
    ) -> str:
        """
        Autonomous execution engine that performs real file operations, test runs,
        and records FileChanges in SQLite.
        """
        prompt_lower = user_prompt.lower()
        files_modified: List[str] = []

        # Step 1: Inspect Workspace & Read Files
        await self._broadcast(
            project_id,
            EventNormalizer.agent_status(
                project_id=project_id,
                status=AgentStatusType.THINKING,
                action="Inspecting project files..."
            )
        )
        await asyncio.sleep(0.3)

        # Inspect calculator.py if relevant
        calc_path = "calculator.py"
        if (workspace_dir / calc_path).exists():
            await self._broadcast(
                project_id,
                EventNormalizer.tool_call(
                    project_id=project_id,
                    tool="read_file",
                    args={"path": calc_path},
                    description=f"Reading: {calc_path}"
                )
            )
            content, size, _ = await self.workspace_mgr.read_file(project_id, calc_path)
            await self._broadcast(
                project_id,
                EventNormalizer.tool_result(
                    project_id=project_id,
                    tool="read_file",
                    result={"path": calc_path, "bytes": size},
                    success=True
                )
            )
            await asyncio.sleep(0.3)

        # Step 2: Code Modification
        if "divide" in prompt_lower or "division" in prompt_lower:
            await self._broadcast(
                project_id,
                EventNormalizer.agent_status(
                    project_id=project_id,
                    status=AgentStatusType.EXECUTING,
                    action="Implementing divide function..."
                )
            )

            # Updated calculator.py content
            updated_calculator = '''"""
Calculator Module for Summit AI Coding Agent Demo
"""

def add(a: float, b: float) -> float:
    """Returns the sum of a and b."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Returns the difference of a and b."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Returns the product of a and b."""
    return a * b


def divide(a: float, b: float) -> float:
    """Returns the quotient of a and b. Raises ValueError on division by zero."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b
'''
            await self._broadcast(
                project_id,
                EventNormalizer.tool_call(
                    project_id=project_id,
                    tool="write_file",
                    args={"path": "calculator.py"},
                    description="Updating calculator.py with divide function"
                )
            )
            await self.workspace_mgr.write_file(project_id, "calculator.py", updated_calculator)
            
            # Record FileChange
            self.repo.record_file_change(
                project_id=project_id,
                file_path="calculator.py",
                operation="modify",
                user_id=user_id,
                description="Implemented divide function with zero division error handling"
            )
            files_modified.append("calculator.py")

            await self._broadcast(
                project_id,
                EventNormalizer.file_changed(project_id=project_id, path="calculator.py")
            )
            await asyncio.sleep(0.3)

            # Step 3: Update Tests
            await self._broadcast(
                project_id,
                EventNormalizer.agent_status(
                    project_id=project_id,
                    status=AgentStatusType.EXECUTING,
                    action="Adding unit tests for divide function..."
                )
            )

            updated_tests = '''"""
Unit tests for Calculator Module
"""
import pytest
from calculator import add, subtract, multiply, divide


def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0


def test_subtract():
    assert subtract(10, 4) == 6
    assert subtract(0, 5) == -5


def test_multiply():
    assert multiply(3, 7) == 21
    assert multiply(-2, 4) == -8


def test_divide():
    assert divide(10, 2) == 5
    assert divide(7, 2) == 3.5
    assert divide(-9, 3) == -3


def test_divide_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero."):
        divide(5, 0)
'''
            test_file_path = "tests/test_calculator.py"
            await self._broadcast(
                project_id,
                EventNormalizer.tool_call(
                    project_id=project_id,
                    tool="write_file",
                    args={"path": test_file_path},
                    description="Adding test_divide and test_divide_by_zero to tests"
                )
            )
            await self.workspace_mgr.write_file(project_id, test_file_path, updated_tests)
            
            # Record FileChange
            self.repo.record_file_change(
                project_id=project_id,
                file_path=test_file_path,
                operation="modify",
                user_id=user_id,
                description="Added unit tests for divide and divide_by_zero"
            )
            files_modified.append(test_file_path)

            await self._broadcast(
                project_id,
                EventNormalizer.file_changed(project_id=project_id, path=test_file_path)
            )
            await asyncio.sleep(0.3)

        # Step 4: Run Real Pytest in Terminal
        await self._broadcast(
            project_id,
            EventNormalizer.agent_status(
                project_id=project_id,
                status=AgentStatusType.EXECUTING,
                action="Running pytest test suite..."
            )
        )

        exit_code, output = await self.execute_terminal_command(
            project_id=project_id,
            command="pytest",
            cwd=workspace_dir
        )

        # Step 5: Final Agent Explanation
        if exit_code == 0:
            summary = (
                "Successfully implemented `divide(a, b)` in `calculator.py` with zero-division validation. "
                "Added unit tests in `tests/test_calculator.py` and verified that all tests pass."
            )
        else:
            summary = f"Completed modifications, but tests returned exit code {exit_code}.\nOutput: {output}"

        await self._broadcast(
            project_id,
            EventNormalizer.agent_message(
                project_id=project_id,
                message=summary
            )
        )
        return summary

    async def run_session(self, project_id: str, user_prompt: str, user_id: Optional[str] = None):
        """
        Main execution coordinator for a Summit agent session.
        Implements the complete Phase 3 pipeline:
        1. Persist user message.
        2. Create AgentRun in SQLite.
        3. Build comprehensive project context (Summary, Memories, Tree, Files, Conversation).
        4. Broadcast agent status and context intelligence.
        5. Execute Agent with tool-calling loop (read/write/terminal).
        6. Record FileChanges in SQLite.
        7. Persist outcome to conversation history.
        8. Extract long-term memory & architecture decisions (SQLite + ChromaDB).
        9. Complete session and notify subscribers.
        """
        workspace_dir = self.workspace_mgr.get_workspace_dir(project_id)
        if not workspace_dir.exists():
            await self._broadcast(
                project_id,
                EventNormalizer.error(project_id=project_id, error_message=f"Workspace '{project_id}' not found.")
            )
            return

        run_record = None
        files_modified_list: List[str] = []

        try:
            # 1. Save user message to persistent conversation history
            self.repo.save_message(
                project_id=project_id,
                role="user",
                content=user_prompt,
                user_id=user_id
            )

            # 2. Record agent run in SQLite
            run_record = self.repo.create_agent_run(
                project_id=project_id,
                prompt=user_prompt,
                initiated_by=user_id,
                status="running"
            )

            # 3. Emit user message to WebSocket subscribers
            await self._broadcast(
                project_id,
                EventNormalizer.user_message(project_id=project_id, message=user_prompt)
            )

            # 4. Phase 3: Intelligent Project Context Building with Graceful Degradation
            context_payload: Optional[AgentContextPayload] = None
            memory_context = ""
            try:
                context_payload = await self.ctx_builder.build_full_context(
                    project_id=project_id,
                    user_prompt=user_prompt,
                    user_id=user_id
                )
                memory_context = self.ctx_builder.build_memory_context(context_payload.memories)
                if context_payload.memories:
                    logger.info(
                        f"[AGENT] project={project_id} retrieved={len(context_payload.memories)} memories, "
                        f"files={len(context_payload.relevant_files)}"
                    )
            except Exception as e:
                logger.error(f"[CONTEXT] Context building failed gracefully ({e}), proceeding with raw prompt.")

            # 5. Check LLM API availability and execute
            has_api_key = bool(settings.OPENAI_API_KEY or settings.ANTHROPIC_API_KEY or settings.OPENHANDS_API_KEY)

            if has_api_key:
                logger.info(f"Running LLM Agent for project: {project_id}")
                outcome_summary, files_modified_list = await self._execute_real_llm_agent(
                    project_id=project_id,
                    workspace_dir=workspace_dir,
                    user_prompt=user_prompt,
                    memory_context=memory_context,
                    user_id=user_id,
                    context_payload=context_payload
                )
            else:
                logger.info(f"Running autonomous workspace engine for project: {project_id}")
                outcome_summary = await self._execute_autonomous_task(
                    project_id=project_id,
                    workspace_dir=workspace_dir,
                    user_prompt=user_prompt,
                    memory_context=memory_context,
                    user_id=user_id,
                    context_payload=context_payload
                )
                # Query recent file changes produced in this run
                recent_changes = self.repo.get_project_file_changes(project_id=project_id, limit=5)
                files_modified_list = [c["file_path"] for c in recent_changes]

            # 6. Save assistant outcome to persistent conversation history
            self.repo.save_message(
                project_id=project_id,
                role="assistant",
                content=outcome_summary
            )

            # 7. Update agent run status in SQLite
            if run_record:
                self.repo.update_agent_run(run_id=run_record["id"], status="completed")

            # 8. Post-task Memory Extraction (Autonomous learning)
            try:
                await self.extractor.extract_and_save(
                    project_id=project_id,
                    user_prompt=user_prompt,
                    outcome_summary=outcome_summary,
                    user_id=user_id,
                    files_changed=files_modified_list
                )
            except Exception as e:
                logger.warning(f"Memory extraction failed non-fatally: {e}")

            # 9. Mark session complete
            await self._broadcast(
                project_id,
                EventNormalizer.agent_status(
                    project_id=project_id,
                    status=AgentStatusType.COMPLETED,
                    message="Task completed."
                )
            )
            await self._broadcast(
                project_id,
                EventNormalizer.session_complete(project_id=project_id)
            )

        except asyncio.CancelledError:
            logger.info(f"Agent session cancelled for project: {project_id}")
            if run_record:
                self.repo.update_agent_run(run_id=run_record["id"], status="stopped")
            await self._broadcast(
                project_id,
                EventNormalizer.agent_status(
                    project_id=project_id,
                    status=AgentStatusType.IDLE,
                    message="Session was stopped by user."
                )
            )
        except Exception as e:
            logger.error(f"Error during agent session execution: {e}", exc_info=True)
            if run_record:
                self.repo.update_agent_run(run_id=run_record["id"], status="failed")
            await self._broadcast(
                project_id,
                EventNormalizer.error(project_id=project_id, error_message=str(e))
            )
            await self._broadcast(
                project_id,
                EventNormalizer.agent_status(
                    project_id=project_id,
                    status=AgentStatusType.ERROR,
                    message="An error occurred during execution."
                )
            )


summit_adapter = SummitAdapter()
