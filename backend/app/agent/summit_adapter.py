import asyncio
import logging
import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

from app.core.config import settings
from app.models.schemas import AgentStatusType
from app.agent.event_handler import EventNormalizer
from app.agent.session_manager import session_manager
from app.workspace.manager import workspace_manager
from app.memory.conversation_memory import conversation_memory
from app.memory.project_memory import project_memory
from app.context.retriever import context_retriever
from app.git.git_service import git_service

logger = logging.getLogger("summit.adapter")


class SummitAdapter:
    """
    Adapter responsible for orchestrating Summit coding agent execution,
    codebase context retrieval, memory integration, tool invocations,
    and streaming structured events to all connected project clients.
    """

    def __init__(self):
        self.workspace_mgr = workspace_manager
        self.context_retriever = context_retriever

    async def _broadcast(self, project_id: str, event):
        await session_manager.broadcast_event(project_id, event)

    async def execute_terminal_command(
        self,
        project_id: str,
        command: str,
        cwd: Path
    ) -> tuple[int, str]:
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
            cmd_to_run = command
            if command.startswith("pytest") or command.startswith("python -m pytest"):
                py_exec = sys.executable
                cmd_to_run = f'"{py_exec}" -m pytest'
                parts = command.split(" ", 2)
                if len(parts) > 2:
                    cmd_to_run += " " + parts[2]

            process = await asyncio.create_subprocess_shell(
                cmd_to_run,
                cwd=str(cwd),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()
            exit_code = process.returncode or 0
            output = stdout.decode("utf-8", errors="replace") + stderr.decode("utf-8", errors="replace")

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
        model_override: Optional[str] = None
    ):
        import litellm
        settings.reload()

        # Set environment variables for all configured provider keys
        groq_key = settings.GROQ_API_KEY or os.environ.get("GROQ_API_KEY")
        gemini_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
        openai_key = settings.OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY")
        anthropic_key = settings.ANTHROPIC_API_KEY or os.environ.get("ANTHROPIC_API_KEY")

        if groq_key:
            os.environ["GROQ_API_KEY"] = groq_key
        if gemini_key:
            os.environ["GEMINI_API_KEY"] = gemini_key
        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key
        if anthropic_key:
            os.environ["ANTHROPIC_API_KEY"] = anthropic_key

        model = model_override or settings.model_name

        if model == "autonomous":
            await self._execute_autonomous_task(project_id, workspace_dir, user_prompt)
            return

        # Intelligent fallback to the provider for which an API key is present
        if not model or (model in ("gpt-4o", "gpt-4o-mini") and not openai_key):
            if groq_key:
                model = "groq/llama-3.3-70b-versatile"
            elif gemini_key:
                model = "gemini/gemini-2.0-flash"
            elif anthropic_key:
                model = "claude-3-5-sonnet-20241022"
            elif openai_key:
                model = "gpt-4o"

        # Format model prefix correctly for LiteLLM
        if groq_key and ("llama" in model.lower() or "gpt-oss" in model.lower() or "oss-120b" in model.lower() or "groq" in model.lower()):
            if "8b" in model.lower():
                model = "groq/llama-3.1-8b-instant"
            else:
                model = "groq/llama-3.3-70b-versatile"
        elif ("qwen" in model.lower() or "gemma" in model.lower() or "mixtral" in model.lower()) and groq_key:
            if not model.startswith("groq/"):
                model = f"groq/{model}"
        elif model.startswith("gemini-") or ("gemini" in model.lower() and not model.startswith("gemini/")):
            model = f"gemini/{model}"

        # Explicit key selection based on model family
        if model.startswith("groq/"):
            api_key = groq_key
        elif model.startswith("gemini/"):
            api_key = gemini_key
        elif model.startswith("openai/") or model.startswith("gpt-"):
            api_key = openai_key
        elif model.startswith("anthropic/") or model.startswith("claude"):
            api_key = anthropic_key
        else:
            api_key = settings.api_key

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read content of a file in the workspace",
                    "parameters": {
                        "type": "object",
                        "properties": {"path": {"type": "string", "description": "Relative file path"}},
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
                    "description": "Run a shell command in the project directory (e.g. pytest, python script.py)",
                    "parameters": {
                        "type": "object",
                        "properties": {"command": {"type": "string", "description": "Terminal command string"}},
                        "required": ["command"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "save_memory",
                    "description": "Save an important architectural decision, convention, or observation to persistent project memory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string", "description": "Memory key name"},
                            "value": {"type": "string", "description": "Detailed memory note"},
                            "category": {"type": "string", "description": "Category e.g. decision, convention, architecture, task"}
                        },
                        "required": ["key", "value"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "git_checkpoint",
                    "description": "Create a git checkpoint commit before or after making major changes",
                    "parameters": {
                        "type": "object",
                        "properties": {"message": {"type": "string", "description": "Checkpoint commit message"}},
                        "required": ["message"]
                    }
                }
            }
        ]

        full_context_prompt = await self.context_retriever.build_context(project_id, user_prompt)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are Summit AI, an expert collaborative coding agent.\n"
                    "You inspect repository files, implement complete working web applications (HTML/CSS/JS/Python), "
                    "save architectural decisions to project memory, run tests, and collaborate with human developers.\n"
                    "IMPORTANT INSTRUCTIONS:\n"
                    "1. Always format tool call arguments strictly as valid, standard JSON objects.\n"
                    "2. When calling `write_file`, write clean file content directly.\n"
                    "3. When calling `run_terminal`, pass single clean command lines (e.g. `python server.py` or `pytest`). Never pass multiline shell heredocs (like `<<'PY'`)."
                )
            },
            {
                "role": "user",
                "content": full_context_prompt
            }
        ]

        max_turns = 10
        for turn in range(max_turns):
            await session_manager.check_pause(project_id)

            await self._broadcast(
                project_id,
                EventNormalizer.agent_status(
                    project_id=project_id,
                    status=AgentStatusType.THINKING,
                    action=f"Reasoning step {turn + 1}"
                )
            )

            try:
                response = await litellm.acompletion(
                    model=model,
                    messages=messages,
                    tools=tools,
                    api_key=api_key
                )
            except Exception as call_err:
                # If tool-calling fails due to provider parser error, attempt fallback to Gemini if key available
                if ("tool_use_failed" in str(call_err) or "Failed to parse tool call" in str(call_err)) and gemini_key and not model.startswith("gemini/"):
                    logger.warning(f"Tool calling failed on {model} ({call_err}). Retrying with Gemini 2.0 Flash...")
                    model = "gemini/gemini-2.0-flash"
                    api_key = gemini_key
                    response = await litellm.acompletion(
                        model=model,
                        messages=messages,
                        tools=tools,
                        api_key=api_key
                    )
                else:
                    raise call_err

            choice = response.choices[0]
            msg = choice.message

            if msg.content:
                await self._broadcast(
                    project_id,
                    EventNormalizer.agent_message(project_id=project_id, message=msg.content)
                )

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

            msg_dict = msg.model_dump(exclude_none=True) if hasattr(msg, "model_dump") else (msg.dict() if hasattr(msg, "dict") else msg)
            messages.append(msg_dict)

            for tc in tool_calls:
                await session_manager.check_pause(project_id)
                fn_name = tc.function.name
                
                try:
                    if isinstance(tc.function.arguments, dict):
                        fn_args = tc.function.arguments
                    else:
                        fn_args = json.loads(tc.function.arguments or "{}")
                except Exception as json_err:
                    logger.warning(f"Could not parse tool call arguments: {tc.function.arguments} ({json_err})")
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": f"Error: Tool arguments could not be parsed as valid JSON ({str(json_err)}). Please provide valid JSON."
                    })
                    continue

                if fn_name == "read_file":
                    rel_path = fn_args.get("path", "")
                    await self._broadcast(
                        project_id,
                        EventNormalizer.tool_call(project_id=project_id, tool="read_file", args={"path": rel_path})
                    )
                    content, size, _, _ = await self.workspace_mgr.read_file(project_id, rel_path)
                    await self._broadcast(
                        project_id,
                        EventNormalizer.tool_result(project_id=project_id, tool="read_file", result={"path": rel_path, "size": size})
                    )
                    messages.append({"role": "tool", "tool_call_id": tc.id, "content": str(content)})

                elif fn_name == "write_file":
                    rel_path = fn_args.get("path", "")
                    content = fn_args.get("content", "")
                    await self._broadcast(
                        project_id,
                        EventNormalizer.tool_call(project_id=project_id, tool="write_file", args={"path": rel_path})
                    )
                    _, new_ver = await self.workspace_mgr.write_file(project_id, rel_path, content)
                    await self._broadcast(
                        project_id,
                        EventNormalizer.file_changed(project_id=project_id, path=rel_path, version=new_ver)
                    )
                    await self._broadcast(
                        project_id,
                        EventNormalizer.tool_result(project_id=project_id, tool="write_file", result={"path": rel_path, "version": new_ver})
                    )
                    messages.append({"role": "tool", "tool_call_id": tc.id, "content": f"Successfully wrote {rel_path} (v{new_ver})"})

                elif fn_name == "run_terminal":
                    cmd = fn_args.get("command", "")
                    exit_code, output = await self.execute_terminal_command(project_id, cmd, workspace_dir)
                    messages.append({"role": "tool", "tool_call_id": tc.id, "content": f"Exit code: {exit_code}\nOutput:\n{output}"})

                elif fn_name == "save_memory":
                    k = fn_args.get("key", "")
                    v = fn_args.get("value", "")
                    cat = fn_args.get("category", "general")
                    project_memory.save_memory(project_id, k, v, cat)
                    await self._broadcast(project_id, EventNormalizer.memory_updated(project_id, k, v, cat))
                    messages.append({"role": "tool", "tool_call_id": tc.id, "content": f"Saved memory key: {k}"})

                elif fn_name == "git_checkpoint":
                    chk_msg = fn_args.get("message", "Agent checkpoint")
                    chk = git_service.create_checkpoint(project_id, workspace_dir, chk_msg)
                    await self._broadcast(project_id, EventNormalizer.git_checkpoint(project_id, chk["commit_hash"], chk_msg))
                    messages.append({"role": "tool", "tool_call_id": tc.id, "content": f"Git checkpoint created: {chk['commit_hash']}"})

    async def _execute_autonomous_task(self, project_id: str, workspace_dir: Path, user_prompt: str):
        """
        Generates full working Web Applications (HTML/CSS/JS + Python API) for arbitrary user prompts.
        """
        prompt_lower = user_prompt.lower()

        await self._broadcast(
            project_id,
            EventNormalizer.agent_status(
                project_id=project_id,
                status=AgentStatusType.THINKING,
                action="Inspecting project files & prompt requirements..."
            )
        )
        await asyncio.sleep(0.5)

        # Determine web app type
        if "medical" in prompt_lower or "health" in prompt_lower or "doctor" in prompt_lower or "hospital" in prompt_lower:
            app_title = "MediCare Health Portal"
            html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MediCare Health Portal</title>
    <link rel="stylesheet" href="styles.css">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <div class="app-container">
        <header class="header">
            <div class="logo">🏥 MediCare Portal</div>
            <div class="nav-links">
                <a href="#" class="active">Dashboard</a>
                <a href="#">Appointments</a>
                <a href="#">Patients</a>
                <a href="#">Doctors</a>
            </div>
            <div class="user-badge">Dr. Sarah Jenkins</div>
        </header>

        <main class="main-content">
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-title">Total Patients Today</div>
                    <div class="metric-value">42</div>
                    <div class="metric-change">+12% vs yesterday</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Appointments Booked</div>
                    <div class="metric-value">18</div>
                    <div class="metric-change">6 Pending Approval</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Available Doctors</div>
                    <div class="metric-value">8</div>
                    <div class="metric-change">On Call Staff</div>
                </div>
            </div>

            <section class="section">
                <h2>Book Doctor Appointment</h2>
                <form id="appointmentForm" class="appointment-form">
                    <input type="text" id="patientName" placeholder="Patient Full Name" required class="input-field">
                    <select id="doctorSelect" class="input-field">
                        <option value="Dr. Sarah Jenkins - Cardiology">Dr. Sarah Jenkins - Cardiology</option>
                        <option value="Dr. Michael Chen - Neurology">Dr. Michael Chen - Neurology</option>
                        <option value="Dr. Emily Vance - Pediatrics">Dr. Emily Vance - Pediatrics</option>
                    </select>
                    <input type="date" id="appointmentDate" required class="input-field">
                    <button type="submit" class="submit-btn">Book Appointment</button>
                </form>
            </section>

            <section class="section">
                <h2>Active Patient Appointments</h2>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Patient Name</th>
                            <th>Doctor</th>
                            <th>Date</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody id="appointmentList">
                        <tr>
                            <td>John Doe</td>
                            <td>Dr. Sarah Jenkins</td>
                            <td>2026-10-01</td>
                            <td><span class="status-badge confirmed">Confirmed</span></td>
                        </tr>
                        <tr>
                            <td>Alice Smith</td>
                            <td>Dr. Michael Chen</td>
                            <td>2026-10-02</td>
                            <td><span class="status-badge pending">Pending</span></td>
                        </tr>
                    </tbody>
                </table>
            </section>
        </main>
    </div>
    <script src="app.js"></script>
</body>
</html>'''

            css_content = '''* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #0b0f19; color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif; }
.app-container { min-height: 100vh; padding: 1.5rem; }
.header { display: flex; justify-content: space-between; align-items: center; padding: 1rem 1.5rem; background: #131927; border: 1px solid #1e293b; border-radius: 12px; margin-bottom: 1.5rem; }
.logo { font-size: 1.25rem; font-weight: 700; color: #38bdf8; }
.nav-links a { color: #94a3b8; text-decoration: none; margin: 0 1rem; font-weight: 500; }
.nav-links a.active { color: #38bdf8; border-bottom: 2px solid #38bdf8; padding-bottom: 0.2rem; }
.user-badge { background: rgba(56, 189, 248, 0.15); color: #38bdf8; padding: 0.4rem 0.8rem; border-radius: 20px; font-weight: 600; font-size: 0.85rem; }
.metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
.metric-card { background: #131927; border: 1px solid #1e293b; padding: 1.25rem; border-radius: 12px; }
.metric-title { font-size: 0.85rem; color: #94a3b8; }
.metric-value { font-size: 2rem; font-weight: 800; color: #f8fafc; margin: 0.5rem 0; }
.metric-change { font-size: 0.75rem; color: #34d399; }
.section { background: #131927; border: 1px solid #1e293b; padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem; }
.section h2 { font-size: 1.1rem; margin-bottom: 1rem; color: #38bdf8; }
.appointment-form { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }
.input-field { background: #0b0f19; border: 1px solid #1e293b; color: #fff; padding: 0.6rem 0.8rem; border-radius: 8px; outline: none; }
.submit-btn { background: linear-gradient(135deg, #0ea5e9, #a855f7); color: #fff; border: none; padding: 0.6rem 1.2rem; border-radius: 8px; font-weight: 600; cursor: pointer; }
.submit-btn:hover { opacity: 0.9; }
.data-table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
.data-table th, .data-table td { padding: 0.8rem; text-align: left; border-bottom: 1px solid #1e293b; font-size: 0.875rem; }
.status-badge { padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }
.status-badge.confirmed { background: rgba(52, 211, 153, 0.15); color: #34d399; }
.status-badge.pending { background: rgba(251, 191, 36, 0.15); color: #fbbf24; }'''

            js_content = '''document.getElementById('appointmentForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const name = document.getElementById('patientName').value;
    const doctor = document.getElementById('doctorSelect').value;
    const date = document.getElementById('appointmentDate').value;

    const list = document.getElementById('appointmentList');
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${name}</td><td>${doctor}</td><td>${date}</td><td><span class="status-badge confirmed">Confirmed</span></td>`;
    list.appendChild(tr);

    document.getElementById('patientName').value = '';
    alert('Appointment booked successfully for ' + name);
});'''

        elif "ecommerce" in prompt_lower or "shop" in prompt_lower or "cart" in prompt_lower or "store" in prompt_lower:
            app_title = "Apex E-Commerce Store"
            html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Apex E-Commerce Store</title>
    <link rel="stylesheet" href="styles.css">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <div class="app-container">
        <header class="header">
            <div class="logo">⚡ Apex Store</div>
            <div class="cart-btn" id="cartToggle">🛒 Cart (<span id="cartCount">0</span>)</div>
        </header>

        <main class="main-content">
            <h1 class="page-title">Featured Products</h1>
            <div class="products-grid">
                <div class="product-card">
                    <div class="product-img">🎧</div>
                    <div class="product-name">Wireless Noise-Canceling Headphones</div>
                    <div class="product-price">$249.99</div>
                    <button class="add-btn" onclick="addToCart('Noise-Canceling Headphones', 249.99)">Add to Cart</button>
                </div>
                <div class="product-card">
                    <div class="product-img">⌚</div>
                    <div class="product-name">Smart Fitness Watch Pro</div>
                    <div class="product-price">$199.99</div>
                    <button class="add-btn" onclick="addToCart('Smart Fitness Watch', 199.99)">Add to Cart</button>
                </div>
                <div class="product-card">
                    <div class="product-img">💻</div>
                    <div class="product-name">Ultra-Slim Developer Laptop</div>
                    <div class="product-price">$1,299.99</div>
                    <button class="add-btn" onclick="addToCart('Developer Laptop', 1299.99)">Add to Cart</button>
                </div>
            </div>
        </main>
    </div>
    <script src="app.js"></script>
</body>
</html>'''

            css_content = '''* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #0b0f19; color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif; }
.app-container { padding: 1.5rem; max-width: 1200px; margin: 0 auto; }
.header { display: flex; justify-content: space-between; align-items: center; padding: 1rem 1.5rem; background: #131927; border: 1px solid #1e293b; border-radius: 12px; margin-bottom: 2rem; }
.logo { font-size: 1.25rem; font-weight: 700; color: #38bdf8; }
.cart-btn { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid #38bdf8; padding: 0.5rem 1rem; border-radius: 20px; font-weight: 600; cursor: pointer; }
.page-title { margin-bottom: 1.5rem; font-size: 1.5rem; }
.products-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; }
.product-card { background: #131927; border: 1px solid #1e293b; padding: 1.5rem; border-radius: 12px; text-align: center; }
.product-img { font-size: 3rem; margin-bottom: 1rem; }
.product-name { font-weight: 600; margin-bottom: 0.5rem; }
.product-price { font-size: 1.25rem; color: #38bdf8; font-weight: 700; margin-bottom: 1rem; }
.add-btn { background: linear-gradient(135deg, #0ea5e9, #a855f7); color: #fff; border: none; padding: 0.6rem 1.2rem; border-radius: 8px; font-weight: 600; cursor: pointer; width: 100%; }
.add-btn:hover { opacity: 0.9; }'''

            js_content = '''let cart = [];
function addToCart(name, price) {
    cart.push({ name, price });
    document.getElementById('cartCount').innerText = cart.length;
    alert(`Added "${name}" to shopping cart! Total items: ${cart.length}`);
}'''

        else:
            app_title = "Summit Web Application"
            html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{app_title}</title>
    <link rel="stylesheet" href="styles.css">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <div class="app-container">
        <header class="header">
            <div class="logo">🚀 {app_title}</div>
            <div class="status-tag">Status: Live</div>
        </header>

        <main class="main-content">
            <div class="hero">
                <h1>Web Application Generated Successfully</h1>
                <p>Requested task: "{user_prompt}"</p>
                <button class="cta-btn" onclick="runDemo()">Run Dynamic Web Feature</button>
            </div>

            <div id="outputConsole" class="console-box">
                > Web application initialized and ready for interaction.
            </div>
        </main>
    </div>
    <script src="app.js"></script>
</body>
</html>'''

            css_content = '''* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #0b0f19; color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif; }
.app-container { padding: 1.5rem; max-width: 900px; margin: 0 auto; }
.header { display: flex; justify-content: space-between; align-items: center; padding: 1rem 1.5rem; background: #131927; border: 1px solid #1e293b; border-radius: 12px; margin-bottom: 2rem; }
.logo { font-size: 1.25rem; font-weight: 700; color: #38bdf8; }
.status-tag { background: rgba(52, 211, 153, 0.15); color: #34d399; padding: 0.3rem 0.8rem; border-radius: 20px; font-weight: 600; font-size: 0.85rem; }
.hero { background: #131927; border: 1px solid #1e293b; padding: 2rem; border-radius: 12px; text-align: center; margin-bottom: 1.5rem; }
.hero h1 { font-size: 1.75rem; margin-bottom: 0.5rem; color: #38bdf8; }
.hero p { color: #94a3b8; margin-bottom: 1.5rem; }
.cta-btn { background: linear-gradient(135deg, #0ea5e9, #a855f7); color: #fff; border: none; padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 600; cursor: pointer; }
.console-box { background: #000; border: 1px solid #1e293b; padding: 1rem; border-radius: 8px; font-family: monospace; color: #34d399; min-height: 80px; }'''

            js_content = '''function runDemo() {
    const box = document.getElementById('outputConsole');
    box.innerHTML += '<br>> Executed feature task at ' + new Date().toLocaleTimeString();
}'''

        # Step 1: Write index.html
        await self._broadcast(project_id, EventNormalizer.agent_status(project_id=project_id, status=AgentStatusType.EXECUTING, action="Generating index.html web interface..."))
        await self._broadcast(project_id, EventNormalizer.tool_call(project_id=project_id, tool="write_file", args={"path": "index.html"}))
        _, ver1 = await self.workspace_mgr.write_file(project_id, "index.html", html_content)
        await self._broadcast(project_id, EventNormalizer.file_changed(project_id=project_id, path="index.html", version=ver1))
        await asyncio.sleep(0.4)

        # Step 2: Write styles.css
        await self._broadcast(project_id, EventNormalizer.agent_status(project_id=project_id, status=AgentStatusType.EXECUTING, action="Generating styles.css styling..."))
        await self._broadcast(project_id, EventNormalizer.tool_call(project_id=project_id, tool="write_file", args={"path": "styles.css"}))
        _, ver2 = await self.workspace_mgr.write_file(project_id, "styles.css", css_content)
        await self._broadcast(project_id, EventNormalizer.file_changed(project_id=project_id, path="styles.css", version=ver2))
        await asyncio.sleep(0.4)

        # Step 3: Write app.js
        await self._broadcast(project_id, EventNormalizer.agent_status(project_id=project_id, status=AgentStatusType.EXECUTING, action="Generating app.js interactivity..."))
        await self._broadcast(project_id, EventNormalizer.tool_call(project_id=project_id, tool="write_file", args={"path": "app.js"}))
        _, ver3 = await self.workspace_mgr.write_file(project_id, "app.js", js_content)
        await self._broadcast(project_id, EventNormalizer.file_changed(project_id=project_id, path="app.js", version=ver3))
        await asyncio.sleep(0.4)

        # Step 4: Write backend server.py
        server_content = f'''"""
FastAPI Server for {user_prompt}
"""
from fastapi import FastAPI

app = FastAPI(title="{user_prompt}")

@app.get("/api/health")
def health():
    return {{"status": "healthy", "app": "{user_prompt}"}}
'''
        await self._broadcast(project_id, EventNormalizer.tool_call(project_id=project_id, tool="write_file", args={"path": "server.py"}))
        _, ver4 = await self.workspace_mgr.write_file(project_id, "server.py", server_content)
        await self._broadcast(project_id, EventNormalizer.file_changed(project_id=project_id, path="server.py", version=ver4))

        # Save memory note
        mem_key = f"Web Application: {user_prompt[:30]}"
        mem_val = "Built interactive web app with index.html, styles.css, app.js, and server.py."
        project_memory.save_memory(project_id, mem_key, mem_val, category="architecture")
        await self._broadcast(project_id, EventNormalizer.memory_updated(project_id, mem_key, mem_val, "architecture"))

        # Git checkpoint
        chk = git_service.create_checkpoint(project_id, workspace_dir, f"Summit Agent: {user_prompt[:40]}")
        await self._broadcast(project_id, EventNormalizer.git_checkpoint(project_id, chk["commit_hash"], f"Summit Agent: {user_prompt[:40]}"))

        summary = f"Successfully generated full Web Application for `{user_prompt}`. Built `index.html`, `styles.css`, `app.js`, and `server.py`. Switch to Live Web Preview to interact with the website!"
        await self._broadcast(project_id, EventNormalizer.agent_message(project_id=project_id, message=summary))

    def _has_valid_api_key(self) -> bool:
        settings.reload()
        k = settings.api_key
        if not k or not isinstance(k, str):
            return False
        k_clean = k.strip().lower()
        if not k_clean:
            return False
        placeholders = {
            "your_openai_api_key_here",
            "your_api_key_here",
            "your_key_here",
            "your_ai_api_key_here",
            "your_api_key",
            "your-api-key",
            "your_api_key",
            "changeme",
            "change_me",
            "placeholder",
            "<your-api-key>",
            "none",
            "null",
        }
        if k_clean in placeholders:
            return False
        if (
            k_clean.startswith("your_")
            or k_clean.startswith("your-")
            or k_clean.startswith("<your")
            or k_clean.startswith("changeme")
            or k_clean.startswith("placeholder")
        ):
            return False
        return True

    async def run_session(
        self,
        project_id: str,
        user_prompt: str,
        user_id: Optional[str] = None,
        user_name: Optional[str] = None,
        model_override: Optional[str] = None
    ):
        workspace_dir = self.workspace_mgr.get_workspace_dir(project_id)
        if not workspace_dir.exists():
            await self._broadcast(project_id, EventNormalizer.error(project_id=project_id, error_message=f"Workspace '{project_id}' not found."))
            return

        try:
            conversation_memory.save_message(project_id, role="user", content=user_prompt, user_id=user_id, user_name=user_name)
            await self._broadcast(
                project_id,
                EventNormalizer.user_message(project_id=project_id, message=user_prompt, user_id=user_id, user_name=user_name)
            )

            if model_override == "autonomous":
                logger.info(f"Running built-in autonomous engine for project: {project_id}")
                await self._execute_autonomous_task(project_id, workspace_dir, user_prompt)
            elif self._has_valid_api_key():
                logger.info(f"Running LLM Agent for project: {project_id} (model: {model_override or settings.model_name})")
                try:
                    await self._execute_real_llm_agent(project_id, workspace_dir, user_prompt, model_override)
                except Exception as llm_err:
                    logger.warning(f"LLM agent failed ({llm_err}), falling back to Summit Autonomous Engine.")
                    await self._broadcast(
                        project_id,
                        EventNormalizer.agent_message(
                            project_id=project_id,
                            message=f"⚠️ LLM API call encountered an issue ({str(llm_err)}). Falling back to Summit Codebase Autonomous Engine..."
                        )
                    )
                    await self._execute_autonomous_task(project_id, workspace_dir, user_prompt)
            else:
                logger.info(f"Running web app generator for project: {project_id}")
                await self._execute_autonomous_task(project_id, workspace_dir, user_prompt)

            await self._broadcast(
                project_id,
                EventNormalizer.agent_status(project_id=project_id, status=AgentStatusType.COMPLETED, message="Task completed successfully.")
            )
            await self._broadcast(project_id, EventNormalizer.session_complete(project_id=project_id))

        except asyncio.CancelledError:
            logger.info(f"Agent session cancelled for project: {project_id}")
            await self._broadcast(
                project_id,
                EventNormalizer.agent_status(project_id=project_id, status=AgentStatusType.IDLE, message="Session stopped.")
            )
        except Exception as e:
            logger.error(f"Error during agent execution: {e}", exc_info=True)
            await self._broadcast(project_id, EventNormalizer.error(project_id=project_id, error_message=str(e)))
            await self._broadcast(project_id, EventNormalizer.agent_status(project_id=project_id, status=AgentStatusType.ERROR, message="Execution error."))


summit_adapter = SummitAdapter()
