import os
import subprocess
from pathlib import Path

FIGURES_DIR = Path("research_paper/figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# 1. System Architecture SVG
svg_fig1 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 680" width="1100" height="680" style="background:#ffffff; font-family:'Segoe UI', Helvetica, Arial, sans-serif;">
  <defs>
    <linearGradient id="clientGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#eff6ff"/>
      <stop offset="100%" stop-color="#dbeafe"/>
    </linearGradient>
    <linearGradient id="gatewayGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#f5f3ff"/>
      <stop offset="100%" stop-color="#ede9fe"/>
    </linearGradient>
    <linearGradient id="agentGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#f0fdf4"/>
      <stop offset="100%" stop-color="#dcfce7"/>
    </linearGradient>
    <linearGradient id="memGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#fffbeb"/>
      <stop offset="100%" stop-color="#fef3c7"/>
    </linearGradient>
    <linearGradient id="wsGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#faf5ff"/>
      <stop offset="100%" stop-color="#f3e8ff"/>
    </linearGradient>
    <filter id="shadow" x="-3%" y="-3%" width="106%" height="108%" filterUnits="userSpaceOnUse">
      <feDropShadow dx="1" dy="2" stdDeviation="3" flood-opacity="0.12"/>
    </filter>
    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#334155"/>
    </marker>
    <marker id="arrowBlue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#2563eb"/>
    </marker>
  </defs>

  <!-- Title Banner -->
  <rect x="20" y="15" width="1060" height="42" rx="6" fill="#1e293b"/>
  <text x="550" y="42" fill="#ffffff" font-size="16" font-weight="bold" text-anchor="middle" letter-spacing="0.5">
    SYSTEM ARCHITECTURE: MULTIPLAYER AI CODING AGENT WITH PERSISTENT PROJECT MEMORY
  </text>

  <!-- LAYER 1: CLIENT TIER -->
  <rect x="20" y="70" width="1060" height="110" rx="8" fill="url(#clientGrad)" stroke="#93c5fd" stroke-width="1.5" filter="url(#shadow)"/>
  <text x="35" y="93" fill="#1e3a8a" font-size="13" font-weight="bold">COLLABORATIVE FRONTEND CLIENTS (React / TypeScript / Vite / Monaco Editor)</text>
  
  <!-- Client Boxes -->
  <g transform="translate(45, 105)">
    <!-- Client A -->
    <rect x="0" y="0" width="220" height="60" rx="6" fill="#ffffff" stroke="#3b82f6" stroke-width="1.5"/>
    <circle cx="20" cy="22" r="9" fill="#2563eb"/>
    <text x="20" y="26" fill="#fff" font-size="10" font-weight="bold" text-anchor="middle">A</text>
    <text x="36" y="24" fill="#1e293b" font-size="11" font-weight="bold">Developer Alice</text>
    <text x="12" y="45" fill="#64748b" font-size="9.5">Monaco Editor | Live Chat Stream</text>

    <!-- Client B -->
    <rect x="250" y="0" width="220" height="60" rx="6" fill="#ffffff" stroke="#10b981" stroke-width="1.5"/>
    <circle cx="270" cy="22" r="9" fill="#059669"/>
    <text x="270" y="26" fill="#fff" font-size="10" font-weight="bold" text-anchor="middle">B</text>
    <text x="286" y="24" fill="#1e293b" font-size="11" font-weight="bold">Developer Bob</text>
    <text x="262" y="45" fill="#64748b" font-size="9.5">OCC Conflict Modal | Git Panel</text>

    <!-- Client C -->
    <rect x="500" y="0" width="220" height="60" rx="6" fill="#ffffff" stroke="#f59e0b" stroke-width="1.5"/>
    <circle cx="520" cy="22" r="9" fill="#d97706"/>
    <text x="520" y="26" fill="#fff" font-size="10" font-weight="bold" text-anchor="middle">C</text>
    <text x="536" y="24" fill="#1e293b" font-size="11" font-weight="bold">Developer Charlie</text>
    <text x="512" y="45" fill="#64748b" font-size="9.5">Memory Panel | File Explorer</text>

    <!-- Shared Services Box -->
    <rect x="750" y="0" width="235" height="60" rx="6" fill="#ffffff" stroke="#8b5cf6" stroke-width="1.5"/>
    <text x="762" y="22" fill="#5b21b6" font-size="11" font-weight="bold">Client-Side Protocols</text>
    <text x="762" y="38" fill="#475569" font-size="9.5">• ProjectWebSocket &amp; Reconnect</text>
    <text x="762" y="52" fill="#475569" font-size="9.5">• REST Client (Axios / Fetch)</text>
  </g>

  <!-- LAYER 2: GATEWAY & SESSION MANAGEMENT -->
  <rect x="20" y="195" width="1060" height="95" rx="8" fill="url(#gatewayGrad)" stroke="#c4b5fd" stroke-width="1.5" filter="url(#shadow)"/>
  <text x="35" y="217" fill="#4c1d95" font-size="13" font-weight="bold">FASTAPI SERVER &amp; MULTIPLAYER SESSION MANAGER</text>

  <g transform="translate(45, 227)">
    <!-- WebSocket Stream Gateway -->
    <rect x="0" y="0" width="310" height="52" rx="5" fill="#ffffff" stroke="#7c3aed" stroke-width="1.2"/>
    <text x="12" y="20" fill="#6d28d9" font-size="10.5" font-weight="bold">WebSocket Room Hub (/api/projects/{id}/stream)</text>
    <text x="12" y="38" fill="#475569" font-size="9">Connection Registry | Presence Tracking (UserPresenceInfo)</text>

    <!-- Event Normalizer -->
    <rect x="330" y="0" width="320" height="52" rx="5" fill="#ffffff" stroke="#7c3aed" stroke-width="1.2"/>
    <text x="342" y="20" fill="#6d28d9" font-size="10.5" font-weight="bold">EventNormalizer &amp; Broadcast Bus</text>
    <text x="342" y="38" fill="#475569" font-size="9">AGENT_STATUS | TOOL_CALL | TERMINAL | FILE_CHANGED</text>

    <!-- REST API Endpoints -->
    <rect x="670" y="0" width="315" height="52" rx="5" fill="#ffffff" stroke="#7c3aed" stroke-width="1.2"/>
    <text x="682" y="20" fill="#6d28d9" font-size="10.5" font-weight="bold">REST Routers (Projects, Files, Git, Memory)</text>
    <text x="682" y="38" fill="#475569" font-size="9">Path Validation | Auth Tokens | Health Check (/api/health)</text>
  </g>

  <!-- LAYER 3: CORE SUBSYSTEMS (AGENT, MEMORY, WORKSPACE) -->
  
  <!-- 3A: AI CODING AGENT ORCHESTRATOR -->
  <rect x="20" y="305" width="410" height="355" rx="8" fill="url(#agentGrad)" stroke="#86efac" stroke-width="1.5" filter="url(#shadow)"/>
  <text x="35" y="328" fill="#14532d" font-size="12.5" font-weight="bold">AI AGENT ORCHESTRATOR (SummitAdapter)</text>

  <g transform="translate(35, 340)">
    <!-- Lifecycle Controller -->
    <rect x="0" y="0" width="380" height="50" rx="5" fill="#ffffff" stroke="#16a34a" stroke-width="1.2"/>
    <text x="12" y="19" fill="#15803d" font-size="10.5" font-weight="bold">Agent Execution &amp; Lifecycle Controller</text>
    <text x="12" y="36" fill="#475569" font-size="9">State Machine: IDLE, THINKING, RUNNING, PAUSED, STOPPED</text>
    <text x="290" y="36" fill="#16a34a" font-size="8.5" font-weight="bold">[asyncio.Event]</text>

    <!-- Model Dispatcher -->
    <rect x="0" y="60" width="380" height="75" rx="5" fill="#ffffff" stroke="#16a34a" stroke-width="1.2"/>
    <text x="12" y="78" fill="#15803d" font-size="10.5" font-weight="bold">Model-Agnostic LLM Dispatcher (LiteLLM)</text>
    <text x="12" y="96" fill="#334155" font-size="9">• Cloud LLMs: Groq (Llama 3.3 70B, DeepSeek R1), Gemini 2.0 Flash</text>
    <text x="12" y="111" fill="#334155" font-size="9">• Commercial APIs: OpenAI (GPT-4o), Anthropic (Claude 3.5 Sonnet)</text>
    <text x="12" y="126" fill="#15803d" font-size="9" font-weight="bold">• Offline Deterministic Fallback Engine (Zero API Key Mode)</text>

    <!-- Tool Execution Loop -->
    <rect x="0" y="145" width="380" height="80" rx="5" fill="#ffffff" stroke="#16a34a" stroke-width="1.2"/>
    <text x="12" y="163" fill="#15803d" font-size="10.5" font-weight="bold">Sandboxed Tool Invocation Engine</text>
    <text x="12" y="181" fill="#475569" font-size="9">• read_file(path) / write_file(path, content)</text>
    <text x="12" y="196" fill="#475569" font-size="9">• run_terminal(command, cwd) [Pytest, Python Execution]</text>
    <text x="12" y="211" fill="#475569" font-size="9">• save_memory(key, val) / git_checkpoint(message)</text>

    <!-- Context Injection Interface -->
    <rect x="0" y="235" width="380" height="60" rx="5" fill="#ffffff" stroke="#16a34a" stroke-width="1.2"/>
    <text x="12" y="253" fill="#15803d" font-size="10.5" font-weight="bold">Context Retrieval &amp; Prompt Budgeting</text>
    <text x="12" y="271" fill="#475569" font-size="9">ContextRetriever &amp; ContextBuilder Context Assembly</text>
    <text x="12" y="285" fill="#64748b" font-size="8.5">Memories (2.5kB) + Chat (6 turns) + Code Tree + Scored Files</text>
  </g>

  <!-- 3B: PERSISTENT MEMORY SUBSYSTEM -->
  <rect x="445" y="305" width="335" height="355" rx="8" fill="url(#memGrad)" stroke="#fcd34d" stroke-width="1.5" filter="url(#shadow)"/>
  <text x="460" y="328" fill="#78350f" font-size="12.5" font-weight="bold">DUAL-TIER PERSISTENT MEMORY SYSTEM</text>

  <g transform="translate(460, 340)">
    <!-- Relational Tier -->
    <rect x="0" y="0" width="305" height="85" rx="5" fill="#ffffff" stroke="#d97706" stroke-width="1.2"/>
    <text x="10" y="18" fill="#b45309" font-size="10" font-weight="bold">Tier 1: Relational Source-of-Truth (SQLite)</text>
    <text x="10" y="35" fill="#475569" font-size="8.5">• conversation_messages (Full Chat Transcript)</text>
    <text x="10" y="49" fill="#475569" font-size="8.5">• project_memories (Decisions, Conventions, Facts)</text>
    <text x="10" y="63" fill="#475569" font-size="8.5">• agent_runs (Prompt, Status, Timestamps)</text>
    <text x="10" y="77" fill="#475569" font-size="8.5">• file_changes &amp; file_versions (OCC Tracking)</text>

    <!-- Vector Index Tier -->
    <rect x="0" y="95" width="305" height="90" rx="5" fill="#ffffff" stroke="#d97706" stroke-width="1.2"/>
    <text x="10" y="113" fill="#b45309" font-size="10" font-weight="bold">Tier 2: Semantic Vector Store (ChromaDB)</text>
    <text x="10" y="130" fill="#475569" font-size="8.5">• LocalEmbeddingFunction: 384-d Dense Vector</text>
    <text x="10" y="144" fill="#64748b" font-size="8">(N-gram Hashing, Positional Weights, L2-norm)</text>
    <text x="10" y="158" fill="#475569" font-size="8.5">• HNSW Index with Cosine Space</text>
    <text x="10" y="172" fill="#b45309" font-size="8.5" font-weight="bold">• Deduplication Guard: Distance &lt; 0.10 Updates</text>

    <!-- Memory Extractor -->
    <rect x="0" y="195" width="305" height="100" rx="5" fill="#ffffff" stroke="#d97706" stroke-width="1.2"/>
    <text x="10" y="213" fill="#b45309" font-size="10" font-weight="bold">Automated Memory Extractor (MemoryExtractor)</text>
    <text x="10" y="230" fill="#475569" font-size="8.5">• Trivial Pattern Filter (Regex Noise Rejection)</text>
    <text x="10" y="244" fill="#475569" font-size="8.5">• Category Classifier: Architecture, Conventions,</text>
    <text x="10" y="258" fill="#475569" font-size="8.5">  Bug Solutions, Project Facts, Context</text>
    <text x="10" y="272" fill="#475569" font-size="8.5">• Dual Extraction Mode: LLM JSON / Heuristics</text>
    <text x="10" y="286" fill="#15803d" font-size="8" font-weight="bold">Verified: 100% Offline / Non-blocking</text>
  </g>

  <!-- 3C: WORKSPACE & CONCURRENCY CONTROLLER -->
  <rect x="795" y="305" width="285" height="355" rx="8" fill="url(#wsGrad)" stroke="#d8b4fe" stroke-width="1.5" filter="url(#shadow)"/>
  <text x="810" y="328" fill="#581c87" font-size="12.5" font-weight="bold">WORKSPACE &amp; VERSIONING</text>

  <g transform="translate(810, 340)">
    <!-- Path Traversal Guard -->
    <rect x="0" y="0" width="255" height="85" rx="5" fill="#ffffff" stroke="#9333ea" stroke-width="1.2"/>
    <text x="10" y="18" fill="#7e22ce" font-size="10" font-weight="bold">Workspace Isolation &amp; Security</text>
    <text x="10" y="35" fill="#475569" font-size="8.5">• Root Boundary Validation</text>
    <text x="10" y="49" fill="#dc2626" font-size="8.5">• Path Traversal Rejection (.. /)</text>
    <text x="10" y="63" fill="#475569" font-size="8.5">• WorkspaceSecurityError</text>
    <text x="10" y="77" fill="#15803d" font-size="8" font-weight="bold">Unit Tested: Zero Directory Escape</text>

    <!-- OCC Controller -->
    <rect x="0" y="95" width="255" height="100" rx="5" fill="#ffffff" stroke="#9333ea" stroke-width="1.2"/>
    <text x="10" y="113" fill="#7e22ce" font-size="10" font-weight="bold">Optimistic Concurrency Control (OCC)</text>
    <text x="10" y="130" fill="#475569" font-size="8.5">• Monotonic File Version Counter</text>
    <text x="10" y="144" fill="#475569" font-size="8.5">• Expected vs Server Version Check</text>
    <text x="10" y="158" fill="#dc2626" font-size="8.5">• Conflict Detection: HTTP 409</text>
    <text x="10" y="172" fill="#475569" font-size="8.5">• FileConflictError Payload</text>
    <text x="10" y="186" fill="#6d28d9" font-size="8" font-weight="bold">Client Resolves: Reload vs Overwrite</text>

    <!-- Git Service -->
    <rect x="0" y="205" width="255" height="90" rx="5" fill="#ffffff" stroke="#9333ea" stroke-width="1.2"/>
    <text x="10" y="223" fill="#7e22ce" font-size="10" font-weight="bold">Local Git Checkpoint Engine</text>
    <text x="10" y="240" fill="#475569" font-size="8.5">• Subprocess Git Interface</text>
    <text x="10" y="254" fill="#475569" font-size="8.5">• Porcelain Status &amp; Diff Viewer</text>
    <text x="10" y="268" fill="#475569" font-size="8.5">• Automated Agent Commit Points</text>
    <text x="10" y="282" fill="#475569" font-size="8.5">• Optional Remote Push (origin/main)</text>
  </g>

  <!-- Connectors / Arrows -->
  <line x1="550" y1="180" x2="550" y2="195" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrowBlue)"/>
  <line x1="225" y1="290" x2="225" y2="305" stroke="#334155" stroke-width="2" marker-end="url(#arrow)"/>
  <line x1="610" y1="290" x2="610" y2="305" stroke="#334155" stroke-width="2" marker-end="url(#arrow)"/>
  <line x1="935" y1="290" x2="935" y2="305" stroke="#334155" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Horizontal Inter-subsystem Arrows -->
  <line x1="430" y1="460" x2="445" y2="460" stroke="#059669" stroke-width="1.8" marker-end="url(#arrow)"/>
  <line x1="445" y1="490" x2="430" y2="490" stroke="#d97706" stroke-width="1.8" marker-end="url(#arrow)"/>
  <line x1="780" y1="470" x2="795" y2="470" stroke="#7c3aed" stroke-width="1.8" marker-end="url(#arrow)"/>
</svg>
"""

# 2. Sequence Diagram SVG
svg_fig2 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 600" width="1000" height="600" style="background:#ffffff; font-family:'Segoe UI', Helvetica, Arial, sans-serif;">
  <defs>
    <marker id="sqArrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#1e293b"/>
    </marker>
    <marker id="sqArrowRed" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#dc2626"/>
    </marker>
    <marker id="sqArrowGreen" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#16a34a"/>
    </marker>
  </defs>

  <!-- Title -->
  <rect x="20" y="10" width="960" height="36" rx="5" fill="#1e293b"/>
  <text x="500" y="34" fill="#ffffff" font-size="14" font-weight="bold" text-anchor="middle">
    SEQUENCE: MULTIPLAYER AGENT EXECUTION, REAL-TIME STREAMING &amp; CONCURRENT EDIT RESOLUTION
  </text>

  <!-- Lifeline Headers -->
  <!-- Alice -->
  <rect x="40" y="60" width="130" height="35" rx="5" fill="#dbeafe" stroke="#2563eb" stroke-width="1.5"/>
  <text x="105" y="82" fill="#1e3a8a" font-size="11.5" font-weight="bold" text-anchor="middle">Dev Alice (A)</text>
  <line x1="105" y1="95" x2="105" y2="570" stroke="#94a3b8" stroke-dasharray="4,4"/>

  <!-- Bob -->
  <rect x="230" y="60" width="130" height="35" rx="5" fill="#d1fae5" stroke="#059669" stroke-width="1.5"/>
  <text x="295" y="82" fill="#065f46" font-size="11.5" font-weight="bold" text-anchor="middle">Dev Bob (B)</text>
  <line x1="295" y1="95" x2="295" y2="570" stroke="#94a3b8" stroke-dasharray="4,4"/>

  <!-- WebSocket & SessionManager -->
  <rect x="420" y="60" width="160" height="35" rx="5" fill="#ede9fe" stroke="#7c3aed" stroke-width="1.5"/>
  <text x="500" y="82" fill="#5b21b6" font-size="11.5" font-weight="bold" text-anchor="middle">Session / WS Hub</text>
  <line x1="500" y1="95" x2="500" y2="570" stroke="#94a3b8" stroke-dasharray="4,4"/>

  <!-- Summit Agent -->
  <rect x="640" y="60" width="150" height="35" rx="5" fill="#dcfce7" stroke="#16a34a" stroke-width="1.5"/>
  <text x="715" y="82" fill="#14532d" font-size="11.5" font-weight="bold" text-anchor="middle">Summit AI Agent</text>
  <line x1="715" y1="95" x2="715" y2="570" stroke="#94a3b8" stroke-dasharray="4,4"/>

  <!-- Workspace & DB -->
  <rect x="830" y="60" width="140" height="35" rx="5" fill="#fef3c7" stroke="#d97706" stroke-width="1.5"/>
  <text x="900" y="82" fill="#78350f" font-size="11.5" font-weight="bold" text-anchor="middle">Workspace / DB</text>
  <line x1="900" y1="95" x2="900" y2="570" stroke="#94a3b8" stroke-dasharray="4,4"/>

  <!-- STEP 1: Connect -->
  <line x1="105" y1="120" x2="500" y2="120" stroke="#1e293b" stroke-width="1.5" marker-end="url(#sqArrow)"/>
  <text x="280" y="114" fill="#334155" font-size="9.5">1. WS Connect (user_id="alice")</text>

  <line x1="295" y1="140" x2="500" y2="140" stroke="#1e293b" stroke-width="1.5" marker-end="url(#sqArrow)"/>
  <text x="375" y="134" fill="#334155" font-size="9.5">2. WS Connect (user_id="bob")</text>

  <line x1="500" y1="160" x2="105" y2="160" stroke="#2563eb" stroke-width="1.2" stroke-dasharray="3,3" marker-end="url(#sqArrow)"/>
  <line x1="500" y1="160" x2="295" y2="160" stroke="#2563eb" stroke-width="1.2" stroke-dasharray="3,3" marker-end="url(#sqArrow)"/>
  <text x="210" y="174" fill="#2563eb" font-size="9">Broadcast: USER_JOINED (Presence List: [Alice, Bob])</text>

  <!-- STEP 2: Instruction -->
  <line x1="105" y1="195" x2="500" y2="195" stroke="#1e293b" stroke-width="1.5" marker-end="url(#sqArrow)"/>
  <text x="250" y="190" fill="#0f172a" font-size="9.5" font-weight="bold">3. POST /agent/message ("Implement JWT auth in auth.py")</text>

  <line x1="500" y1="215" x2="715" y2="215" stroke="#1e293b" stroke-width="1.5" marker-end="url(#sqArrow)"/>
  <text x="575" y="210" fill="#334155" font-size="9">4. Dispatch Task to Shared Agent</text>

  <!-- STEP 3: Context Retrieval -->
  <line x1="715" y1="235" x2="900" y2="235" stroke="#d97706" stroke-width="1.5" marker-end="url(#sqArrow)"/>
  <text x="750" y="230" fill="#78350f" font-size="9">5. Retrieve Memories &amp; Files</text>

  <line x1="900" y1="250" x2="715" y2="250" stroke="#d97706" stroke-width="1.2" stroke-dasharray="3,3" marker-end="url(#sqArrow)"/>
  <text x="760" y="263" fill="#78350f" font-size="8.5">Return Memories + Scored File Buffers</text>

  <!-- STEP 4: Streaming Tool Call -->
  <line x1="715" y1="280" x2="500" y2="280" stroke="#16a34a" stroke-width="1.5" marker-end="url(#sqArrowGreen)"/>
  <text x="535" y="275" fill="#15803d" font-size="9">6. Tool: write_file("auth.py", content)</text>

  <line x1="715" y1="298" x2="900" y2="298" stroke="#16a34a" stroke-width="1.5" marker-end="url(#sqArrowGreen)"/>
  <text x="740" y="294" fill="#15803d" font-size="9">7. Write Disk &amp; Increment Version (v1 -&gt; v2)</text>

  <line x1="500" y1="320" x2="105" y2="320" stroke="#16a34a" stroke-width="1.2" stroke-dasharray="3,3" marker-end="url(#sqArrowGreen)"/>
  <line x1="500" y1="320" x2="295" y2="320" stroke="#16a34a" stroke-width="1.2" stroke-dasharray="3,3" marker-end="url(#sqArrowGreen)"/>
  <text x="140" y="334" fill="#15803d" font-size="9">Broadcast: FILE_CHANGED ("auth.py", version=2) to Alice and Bob</text>

  <!-- STEP 5: Terminal Pytest -->
  <line x1="715" y1="355" x2="500" y2="355" stroke="#16a34a" stroke-width="1.5" marker-end="url(#sqArrowGreen)"/>
  <text x="540" y="350" fill="#15803d" font-size="9">8. Tool: run_terminal("pytest tests/test_auth.py")</text>

  <line x1="500" y1="375" x2="105" y2="375" stroke="#7c3aed" stroke-width="1.2" stroke-dasharray="3,3" marker-end="url(#sqArrow)"/>
  <line x1="500" y1="375" x2="295" y2="375" stroke="#7c3aed" stroke-width="1.2" stroke-dasharray="3,3" marker-end="url(#sqArrow)"/>
  <text x="150" y="388" fill="#6d28d9" font-size="9">Broadcast: TERMINAL_OUTPUT ("4 passed in 0.42s") to Alice and Bob</text>

  <!-- STEP 6: Concurrent Edit Conflict -->
  <line x1="295" y1="415" x2="900" y2="415" stroke="#dc2626" stroke-width="1.5" marker-end="url(#sqArrowRed)"/>
  <text x="360" y="410" fill="#dc2626" font-size="9.5" font-weight="bold">9. PUT /files/auth.py (Bob saves local buffer with expected_version=1)</text>

  <rect x="880" y="425" width="40" height="25" fill="#fee2e2" stroke="#dc2626"/>
  <text x="900" y="440" fill="#b91c1c" font-size="8" font-weight="bold" text-anchor="middle">OCC</text>

  <line x1="900" y1="460" x2="295" y2="460" stroke="#dc2626" stroke-width="1.5" stroke-dasharray="4,2" marker-end="url(#sqArrowRed)"/>
  <text x="380" y="455" fill="#b91c1c" font-size="9.5" font-weight="bold">10. HTTP 409 Conflict: server_version=2 != expected_version=1</text>

  <!-- STEP 7: Resolution Modal -->
  <rect x="235" y="475" width="120" height="35" rx="4" fill="#fee2e2" stroke="#dc2626" stroke-width="1"/>
  <text x="295" y="490" fill="#991b1b" font-size="8.5" font-weight="bold" text-anchor="middle">Bob's Conflict Modal</text>
  <text x="295" y="502" fill="#7f1d1d" font-size="7.5" text-anchor="middle">Inspect Server v2 Diff</text>

  <line x1="295" y1="525" x2="900" y2="525" stroke="#16a34a" stroke-width="1.5" marker-end="url(#sqArrowGreen)"/>
  <text x="440" y="520" fill="#15803d" font-size="9">11. Bob accepts server version (Reloads v2) OR Force Overwrites (v3)</text>

  <!-- STEP 8: Memory Extraction -->
  <line x1="715" y1="550" x2="900" y2="550" stroke="#d97706" stroke-width="1.5" marker-end="url(#sqArrow)"/>
  <text x="730" y="545" fill="#78350f" font-size="8.5">12. Memory Extractor indexes JWT decision in SQLite &amp; ChromaDB</text>
</svg>
"""

# 3. Memory Lifecycle SVG
svg_fig3 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 950 560" width="950" height="560" style="background:#ffffff; font-family:'Segoe UI', Helvetica, Arial, sans-serif;">
  <defs>
    <linearGradient id="mlBoxGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="100%" stop-color="#f8fafc"/>
    </linearGradient>
    <marker id="mArrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#1e293b"/>
    </marker>
    <marker id="mGreen" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#16a34a"/>
    </marker>
    <marker id="mRed" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#dc2626"/>
    </marker>
  </defs>

  <!-- Title Banner -->
  <rect x="20" y="12" width="910" height="38" rx="6" fill="#1e293b"/>
  <text x="475" y="37" fill="#ffffff" font-size="14" font-weight="bold" text-anchor="middle">
    DUAL-TIER PERSISTENT MEMORY LIFECYCLE &amp; CONTEXT INJECTION PIPELINE
  </text>

  <!-- PHASE 1: EXTRACTION & FILTERING -->
  <rect x="20" y="65" width="280" height="470" rx="7" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
  <text x="35" y="90" fill="#0f172a" font-size="12" font-weight="bold">PHASE 1: MEMORY EXTRACTION</text>

  <!-- Completed Task Event -->
  <rect x="35" y="105" width="250" height="55" rx="5" fill="#ffffff" stroke="#3b82f6" stroke-width="1.2"/>
  <text x="45" y="125" fill="#1e3a8a" font-size="10.5" font-weight="bold">Completed Agent Task Event</text>
  <text x="45" y="142" fill="#64748b" font-size="9">Prompt, Outcome Summary, Modified Files</text>

  <!-- Arrow -->
  <line x1="160" y1="160" x2="160" y2="180" stroke="#1e293b" stroke-width="1.5" marker-end="url(#mArrow)"/>

  <!-- Trivial Noise Filter -->
  <rect x="35" y="180" width="250" height="75" rx="5" fill="#ffffff" stroke="#ef4444" stroke-width="1.2"/>
  <text x="45" y="200" fill="#991b1b" font-size="10.5" font-weight="bold">Trivial Filter (is_trivial)</text>
  <text x="45" y="217" fill="#475569" font-size="8.5">Regex Rejection: Length &lt; 10 chars,</text>
  <text x="45" y="230" fill="#475569" font-size="8.5">"ok", "sure", "thanks", "fix this file", "run pytest"</text>
  <text x="45" y="244" fill="#dc2626" font-size="8" font-weight="bold">Discards 100% of Ephemeral Noise</text>

  <!-- Arrow -->
  <line x1="160" y1="255" x2="160" y2="280" stroke="#16a34a" stroke-width="1.5" marker-end="url(#mGreen)"/>

  <!-- Structured Classifier -->
  <rect x="35" y="280" width="250" height="110" rx="5" fill="#ffffff" stroke="#16a34a" stroke-width="1.2"/>
  <text x="45" y="300" fill="#166534" font-size="10.5" font-weight="bold">Classification Engine</text>
  <text x="45" y="318" fill="#334155" font-size="8.5">• Architecture Decision (prio=1, imp=0.85)</text>
  <text x="45" y="332" fill="#334155" font-size="8.5">• Coding Convention (prio=2, imp=0.80)</text>
  <text x="45" y="346" fill="#334155" font-size="8.5">• Bug Solution (prio=4, imp=0.75)</text>
  <text x="45" y="360" fill="#334155" font-size="8.5">• Project Fact (prio=5, imp=0.70)</text>
  <text x="45" y="376" fill="#15803d" font-size="8" font-weight="bold">Hybrid: Cloud LLM JSON / Local Heuristic</text>

  <!-- Arrow -->
  <line x1="160" y1="390" x2="160" y2="415" stroke="#1e293b" stroke-width="1.5" marker-end="url(#mArrow)"/>

  <!-- Candidate Payload -->
  <rect x="35" y="415" width="250" height="55" rx="5" fill="#ffffff" stroke="#8b5cf6" stroke-width="1.2"/>
  <text x="45" y="435" fill="#5b21b6" font-size="10" font-weight="bold">Structured Memory Candidate</text>
  <text x="45" y="452" fill="#64748b" font-size="8.5">Content, Category, Importance, ProjectID</text>

  <!-- PHASE 2: PERSISTENCE & DEDUPLICATION -->
  <rect x="325" y="65" width="300" height="470" rx="7" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
  <text x="340" y="90" fill="#0f172a" font-size="12" font-weight="bold">PHASE 2: DEDUPLICATION &amp; STORAGE</text>

  <!-- Deduplication Decision -->
  <rect x="340" y="110" width="270" height="90" rx="5" fill="#ffffff" stroke="#f59e0b" stroke-width="1.2"/>
  <text x="350" y="130" fill="#b45309" font-size="10" font-weight="bold">Semantic Deduplication Check</text>
  <text x="350" y="147" fill="#475569" font-size="8.5">ChromaDB Top-1 Cosine Distance Search:</text>
  <text x="350" y="162" fill="#d97706" font-size="9" font-weight="bold">d &lt; 0.10 ?</text>
  <text x="350" y="177" fill="#15803d" font-size="8.5">YES: Update existing SQLite record &amp; vector</text>
  <text x="350" y="191" fill="#2563eb" font-size="8.5">NO: Proceed to Dual Insert</text>

  <!-- Connect candidate to dedup -->
  <path d="M 285 442 L 310 442 L 310 155 L 340 155" fill="none" stroke="#1e293b" stroke-width="1.5" marker-end="url(#mArrow)"/>

  <!-- Arrow down to storage -->
  <line x1="475" y1="200" x2="475" y2="230" stroke="#1e293b" stroke-width="1.5" marker-end="url(#mArrow)"/>

  <!-- Tier 1 SQLite Box -->
  <rect x="340" y="230" width="270" height="110" rx="5" fill="#ffffff" stroke="#2563eb" stroke-width="1.2"/>
  <text x="350" y="250" fill="#1e3a8a" font-size="10" font-weight="bold">Tier 1: SQLite Relational Store</text>
  <text x="350" y="267" fill="#475569" font-size="8.5">Primary Key: UUID (id)</text>
  <text x="350" y="281" fill="#475569" font-size="8.5">project_id, memory_type, content, importance</text>
  <text x="350" y="295" fill="#475569" font-size="8.5">created_by, is_active, created_at, updated_at</text>
  <text x="350" y="310" fill="#1e40af" font-size="8" font-weight="bold">Authoritative Ground Truth Storage</text>
  <text x="350" y="324" fill="#64748b" font-size="8">Full ACID transaction integrity</text>

  <!-- Arrow to Tier 2 ChromaDB -->
  <line x1="475" y1="340" x2="475" y2="365" stroke="#1e293b" stroke-width="1.5" marker-end="url(#mArrow)"/>

  <!-- Tier 2 ChromaDB Box -->
  <rect x="340" y="365" width="270" height="115" rx="5" fill="#ffffff" stroke="#7c3aed" stroke-width="1.2"/>
  <text x="350" y="385" fill="#5b21b6" font-size="10" font-weight="bold">Tier 2: ChromaDB Vector Index</text>
  <text x="350" y="402" fill="#475569" font-size="8.5">LocalEmbeddingFunction (dim=384)</text>
  <text x="350" y="416" fill="#475569" font-size="8.5">Trigram hashing + subword projection</text>
  <text x="350" y="430" fill="#475569" font-size="8.5">HNSW Cosine Space Graph Indexing</text>
  <text x="350" y="445" fill="#7c3aed" font-size="8" font-weight="bold">Project-Level Collection Scoping</text>
  <text x="350" y="460" fill="#16a34a" font-size="8" font-weight="bold">Zero External API / 100% Offline</text>

  <!-- PHASE 3: CONTEXT INJECTION -->
  <rect x="650" y="65" width="280" height="470" rx="7" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
  <text x="665" y="90" fill="#0f172a" font-size="12" font-weight="bold">PHASE 3: CONTEXT INJECTION</text>

  <!-- Downstream User Prompt -->
  <rect x="665" y="110" width="250" height="60" rx="5" fill="#ffffff" stroke="#3b82f6" stroke-width="1.2"/>
  <text x="675" y="130" fill="#1e3a8a" font-size="10" font-weight="bold">New Incoming Developer Prompt</text>
  <text x="675" y="147" fill="#64748b" font-size="8.5">Prompt: "Update token expiration logic"</text>
  <text x="675" y="160" fill="#64748b" font-size="8">Keywords: [token, expiration, logic]</text>

  <!-- Query ChromaDB -->
  <path d="M 665 140 L 635 140 L 635 410 L 610 410" fill="none" stroke="#7c3aed" stroke-width="1.2" stroke-dasharray="3,3" marker-end="url(#mArrow)"/>
  <path d="M 610 435 L 635 435 L 635 210 L 665 210" fill="none" stroke="#7c3aed" stroke-width="1.2" stroke-dasharray="3,3" marker-end="url(#mArrow)"/>

  <!-- Context Prioritizer -->
  <rect x="665" y="190" width="250" height="105" rx="5" fill="#ffffff" stroke="#10b981" stroke-width="1.2"/>
  <text x="675" y="210" fill="#065f46" font-size="10" font-weight="bold">ContextBuilder Prioritization</text>
  <text x="675" y="227" fill="#475569" font-size="8.5">1. Filter is_active == True</text>
  <text x="675" y="241" fill="#475569" font-size="8.5">2. Sort Key: (CategoryPrio, -Importance)</text>
  <text x="675" y="255" fill="#475569" font-size="8.5">3. Markdown Formatting by Category</text>
  <text x="675" y="269" fill="#047857" font-size="8" font-weight="bold">Strict Budget Cap: Max 2500 Characters</text>
  <text x="675" y="283" fill="#64748b" font-size="7.5">(Truncates low-priority items if over limit)</text>

  <!-- Arrow -->
  <line x1="790" y1="295" x2="790" y2="320" stroke="#1e293b" stroke-width="1.5" marker-end="url(#mArrow)"/>

  <!-- Codebase Scorer -->
  <rect x="665" y="320" width="250" height="85" rx="5" fill="#ffffff" stroke="#3b82f6" stroke-width="1.2"/>
  <text x="675" y="338" fill="#1e3a8a" font-size="10" font-weight="bold">Workspace File Scoring</text>
  <text x="675" y="355" fill="#475569" font-size="8.5">• Exact match in path: +15 pts</text>
  <text x="675" y="369" fill="#475569" font-size="8.5">• Keyword hit in filename: +4 pts</text>
  <text x="675" y="383" fill="#475569" font-size="8.5">• Topic match (auth, test, api): +5 pts</text>
  <text x="675" y="397" fill="#1e40af" font-size="8" font-weight="bold">Top 4 Files Selected (Max 6kB each)</text>

  <!-- Arrow -->
  <line x1="790" y1="405" x2="790" y2="430" stroke="#1e293b" stroke-width="1.5" marker-end="url(#mArrow)"/>

  <!-- Final Prompt -->
  <rect x="665" y="430" width="250" height="90" rx="5" fill="#eff6ff" stroke="#2563eb" stroke-width="1.5"/>
  <text x="675" y="450" fill="#1e3a8a" font-size="10" font-weight="bold">Consolidated Agent Prompt</text>
  <text x="675" y="467" fill="#334155" font-size="8.5">[1] Project Persistent Memory (Markdown)</text>
  <text x="675" y="481" fill="#334155" font-size="8.5">[2] Recent Multi-User Conversation (10 msgs)</text>
  <text x="675" y="495" fill="#334155" font-size="8.5">[3] Directory Structure &amp; Scored Files</text>
  <text x="675" y="509" fill="#2563eb" font-size="8" font-weight="bold">Passed to LiteLLM / Autonomous Engine</text>
</svg>
"""

# 4. OCC Workflow SVG
svg_fig4 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 500" width="900" height="500" style="background:#ffffff; font-family:'Segoe UI', Helvetica, Arial, sans-serif;">
  <defs>
    <marker id="occArrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#1e293b"/>
    </marker>
    <marker id="occGreen" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#16a34a"/>
    </marker>
    <marker id="occRed" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#dc2626"/>
    </marker>
  </defs>

  <!-- Title -->
  <rect x="20" y="10" width="860" height="36" rx="5" fill="#1e293b"/>
  <text x="450" y="34" fill="#ffffff" font-size="14" font-weight="bold" text-anchor="middle">
    OPTIMISTIC CONCURRENCY CONTROL (OCC) &amp; CONFLICT RESOLUTION WORKFLOW
  </text>

  <!-- Step 1: Read File -->
  <rect x="50" y="70" width="220" height="70" rx="5" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.2"/>
  <text x="60" y="93" fill="#1e3a8a" font-size="11" font-weight="bold">1. File Read Request</text>
  <text x="60" y="110" fill="#475569" font-size="9">GET /api/projects/{id}/files/{path}</text>
  <text x="60" y="125" fill="#2563eb" font-size="8.5">Returns: content, size, version=V_0</text>

  <!-- Arrow -->
  <line x1="270" y1="105" x2="330" y2="105" stroke="#1e293b" stroke-width="1.5" marker-end="url(#occArrow)"/>

  <!-- Step 2: Edit & Write -->
  <rect x="330" y="70" width="240" height="70" rx="5" fill="#f8fafc" stroke="#64748b" stroke-width="1.2"/>
  <text x="340" y="93" fill="#0f172a" font-size="11" font-weight="bold">2. Local Buffer Modification</text>
  <text x="340" y="110" fill="#475569" font-size="9">PUT /api/projects/{id}/files/{path}</text>
  <text x="340" y="125" fill="#0f172a" font-size="8.5">Payload: content, expected_version=V_0</text>

  <!-- Arrow -->
  <line x1="450" y1="140" x2="450" y2="180" stroke="#1e293b" stroke-width="1.5" marker-end="url(#occArrow)"/>

  <!-- Step 3: Server Version Check -->
  <polygon points="450,180 570,230 450,280 330,230" fill="#fffbeb" stroke="#d97706" stroke-width="1.5"/>
  <text x="450" y="225" fill="#92400e" font-size="10.5" font-weight="bold" text-anchor="middle">Version Check</text>
  <text x="450" y="240" fill="#92400e" font-size="9" text-anchor="middle">current_version == expected_version ?</text>

  <!-- Branch YES (Right) -->
  <line x1="570" y1="230" x2="650" y2="230" stroke="#16a34a" stroke-width="2" marker-end="url(#occGreen)"/>
  <text x="600" y="220" fill="#16a34a" font-size="10" font-weight="bold">YES (Match)</text>

  <rect x="650" y="180" width="220" height="100" rx="5" fill="#f0fdf4" stroke="#16a34a" stroke-width="1.5"/>
  <text x="660" y="203" fill="#14532d" font-size="10.5" font-weight="bold">Atomic Write &amp; Version Bump</text>
  <text x="660" y="220" fill="#334155" font-size="9">• Validate Path Traversal Sandbox</text>
  <text x="660" y="235" fill="#334155" font-size="9">• Write buffer via aiofiles</text>
  <text x="660" y="250" fill="#334155" font-size="9">• DB version increment: V_new = V_0 + 1</text>
  <text x="660" y="265" fill="#15803d" font-size="8.5" font-weight="bold">• WS Broadcast: FILE_CHANGED (v_new)</text>

  <!-- Branch NO (Down) -->
  <line x1="450" y1="280" x2="450" y2="330" stroke="#dc2626" stroke-width="2" marker-end="url(#occRed)"/>
  <text x="460" y="305" fill="#dc2626" font-size="10" font-weight="bold">NO (Conflict: v_server &gt; v_expected)</text>

  <rect x="310" y="330" width="280" height="75" rx="5" fill="#fef2f2" stroke="#dc2626" stroke-width="1.5"/>
  <text x="320" y="353" fill="#991b1b" font-size="10.5" font-weight="bold">FileConflictError (HTTP 409)</text>
  <text x="320" y="370" fill="#475569" font-size="9">• Aborts disk overwrite</text>
  <text x="320" y="385" fill="#b91c1c" font-size="8.5">Returns: server_version, server_content buffer</text>

  <!-- Arrow to Client Modal -->
  <line x1="310" y1="367" x2="220" y2="367" stroke="#1e293b" stroke-width="1.5" marker-end="url(#occArrow)"/>

  <!-- Client Resolution Modal -->
  <rect x="30" y="325" width="190" height="145" rx="5" fill="#ffffff" stroke="#7c3aed" stroke-width="1.5"/>
  <text x="40" y="348" fill="#5b21b6" font-size="10.5" font-weight="bold">Conflict Resolution Modal</text>
  <text x="40" y="365" fill="#475569" font-size="8.5">Visual Diff Presentation</text>
  
  <rect x="40" y="375" width="170" height="35" rx="3" fill="#eff6ff" stroke="#3b82f6"/>
  <text x="45" y="390" fill="#1e40af" font-size="8" font-weight="bold">Option A: Reload Server Version</text>
  <text x="45" y="402" fill="#64748b" font-size="7.5">Accept v_server, discards stale edit</text>

  <rect x="40" y="415" width="170" height="35" rx="3" fill="#fef2f2" stroke="#ef4444"/>
  <text x="45" y="430" fill="#991b1b" font-size="8" font-weight="bold">Option B: Force Overwrite</text>
  <text x="45" y="442" fill="#64748b" font-size="7.5">Overwrites server buffer with v_new</text>
</svg>
"""

# Save SVGs
figs = [
    ("fig1_system_architecture", svg_fig1, 1100, 680),
    ("fig2_multiplayer_sequence", svg_fig2, 1000, 600),
    ("fig3_memory_lifecycle", svg_fig3, 950, 560),
    ("fig4_occ_workflow", svg_fig4, 900, 500),
]

for name, svg_content, w, h in figs:
    svg_path = FIGURES_DIR / f"{name}.svg"
    html_path = FIGURES_DIR / f"{name}.html"
    png_path = FIGURES_DIR / f"{name}.png"
    
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    
    html_wrapper = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  html, body {{ margin:0; padding:0; background:#ffffff; overflow:hidden; }}
</style>
</head>
<body>
{svg_content}
</body>
</html>"""
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_wrapper)
    
    # Render PNG using headless Chrome
    chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
    browser = chrome_path if os.path.exists(chrome_path) else edge_path
    
    cmd = [
        browser,
        "--headless",
        "--disable-gpu",
        f"--screenshot={png_path.resolve()}",
        f"--window-size={w},{h}",
        f"file:///{html_path.resolve()}".replace("\\", "/")
    ]
    subprocess.run(cmd, capture_output=True)
    print(f"Generated {png_path}: {png_path.exists()} (size: {png_path.stat().st_size if png_path.exists() else 0} bytes)")

print("All figures successfully created.")
