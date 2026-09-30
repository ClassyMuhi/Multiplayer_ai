# Multiplayer AI Coding Agent with Persistent Project Memory

A real-time collaborative AI coding workspace where multiple human developers connect to the **SAME project** and interact with **ONE shared AI coding agent**.

![Summit AI Workspace Demonstration](C:\Users\HP\.gemini\antigravity-ide\brain\51570f1c-23ca-41c5-8959-b3ae43bd4724\auth_py_opened_1790704156175.png)

---

## 🚀 Key Features

1. **Multiplayer Room & Presence System**
   - Multiple human developers connect to the same project room simultaneously.
   - Real-time online user presence tracking (`USER_JOINED`, `USER_LEFT`).
   - Shared WebSocket stream so all developers see live agent thoughts, tool calls, file updates, and terminal outputs.

2. **Persistent Conversation Memory**
   - Saves all developer prompts and AI agent messages to SQLite database (`messages` table).
   - Reopening a project restores full historical chat context.

3. **Persistent Project Memory**
   - Saves architectural decisions, coding conventions, technical notes, and task progress notes to SQLite database (`project_memories` table).
   - Project memory is automatically retrieved and injected into the AI agent prompt context for every task.

4. **Codebase-Aware AI Agent**
   - Context retriever scans the project workspace, identifies relevant code files, and constructs a focused context budget.
   - Supports tool calling loop: `read_file`, `write_file`, `create_file`, `delete_file`, `run_terminal`, `save_memory`, `git_checkpoint`.
   - Supports agent status controls: `START`, `STOP`, `PAUSE`, `RESUME`.

5. **File Versioning & Concurrent Editing Protection**
   - Every file modification increments its stored version (`file_versions` table).
   - When User A saves a file while User B or the Agent modified it, a `FILE_CONFLICT` (HTTP 409) is returned with a visual diff resolution modal.

6. **Local Git Checkpoints & Diff Viewer**
   - Integrates local Git version control (`git init`, `git status`, `git diff`, `git checkpoint`).
   - Create local git commit checkpoints before or after major agent tasks.

7. **Collaborative IDE Web Application**
   - Modern dark developer tool UI built with Next.js / Vite, React, TypeScript, and Monaco Editor.
   - Includes File Explorer, Code Editor, AI Agent Panel, Memory Panel, and Git Status Bar.

---

## 🏗️ Architecture Overview

```
                      PROJECT ROOM (project_id)
                                 |
           ---------------------------------------------
           |                     |                     |
      User A (Alice)       User B (Bob)          User C (Carol)
           |                     |                     |
           ---------------------------------------------
                                 |
                      WebSocket Stream (/api/projects/{id}/agent/stream)
                                 |
                        Shared AI Agent Session
                                 |
         -------------------------------------------------
         |           |           |            |          |
      Memory     Context     Workspace     Terminal    Git
     (SQLite)   Retriever  (Versioning)   (Pytest)  Checkpoints
```

---

## 🛠️ Backend Installation & Setup

### Prerequisites
- Python 3.10+
- `pip` package manager

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables (Optional for LLM Key)
Copy `.env.example` to `.env`:
```ini
SUMMIT_WORKSPACE_ROOT=./workspaces
SUMMIT_MODEL=gpt-4o
OPENAI_API_KEY=your_openai_api_key_here
HOST=127.0.0.1
PORT=8000
DEBUG=True
```
*Note: If no LLM API key is provided, Summit automatically runs its codebase-aware autonomous engine.*

### 3. Run Backend Server
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 4. Run Automated Backend Tests
```bash
cd backend
python -m pytest
```

---

## 💻 Frontend Installation & Setup

### Prerequisites
- Node.js v18+
- `npm`

### 1. Install Frontend Dependencies
```bash
cd frontend
npm install
```

### 2. Run Frontend Development Server
```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```
Open [http://127.0.0.1:5173](http://127.0.0.1:5173) in your browser.

---

## 🔌 API Endpoints Summary

### Projects & Workspace
- `GET /api/projects` - List all project workspaces
- `POST /api/projects` - Create a new project workspace
- `GET /api/projects/{id}` - Get project details
- `GET /api/projects/{id}/files` - List recursive file tree
- `GET /api/projects/{id}/files/{path}` - Read file content & version
- `PUT /api/projects/{id}/files/{path}` - Write file with expected version check
- `DELETE /api/projects/{id}/files/{path}` - Delete file/folder

### Shared Agent & WebSocket
- `WS /api/projects/{id}/agent/stream?user_id={uid}&display_name={name}` - Real-time event stream
- `POST /api/projects/{id}/agent/message` - Send instruction to shared agent
- `POST /api/projects/{id}/agent/stop` - Cancel active agent task
- `POST /api/projects/{id}/agent/pause` - Pause active agent task
- `POST /api/projects/{id}/agent/resume` - Resume paused agent task

### Persistence & Memory
- `GET /api/projects/{id}/messages` - Fetch persistent conversation history
- `GET /api/projects/{id}/memory` - Fetch persistent project memories
- `POST /api/projects/{id}/memory` - Create/update persistent project memory
- `DELETE /api/projects/{id}/memory/{key}` - Delete project memory note

### User Presence & Git
- `GET /api/projects/{id}/users` - Get online room presence
- `GET /api/projects/{id}/git/status` - Get git status
- `GET /api/projects/{id}/git/diff` - Get working directory git diff
- `POST /api/projects/{id}/git/checkpoint` - Create local git commit checkpoint

---

## 🧪 Testing Verification Results

- **Backend Pytest Suite**: 17 unit/integration tests passed (`test_api.py`, `test_event_normalizer.py`, `test_multiplayer_memory.py`, `test_workspace.py`).
- **Frontend Build**: `npm run build` compileddist bundle with 0 errors.
- **End-to-End Demonstration**: Verified live WebSocket event streaming, file creation (`auth.py`), pytest execution, persistent project memory creation, and browser UI interaction.
