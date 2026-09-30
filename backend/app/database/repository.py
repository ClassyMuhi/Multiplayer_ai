import uuid
import sqlite3
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from app.database.connection import get_connection


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Repository:

    @staticmethod
    def _ensure_project_stub(conn: sqlite3.Connection, project_id: str):
        ts = now_iso()
        conn.execute(
            """
            INSERT INTO projects (id, name, template, workspace_path, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO NOTHING
            """,
            (project_id, project_id.replace("-", " ").title(), "blank", project_id, ts, ts)
        )

    # --- Users ---
    @staticmethod
    def get_or_create_user(user_id: str, display_name: str) -> dict:
        conn = get_connection()
        try:
            with conn:
                cur = conn.cursor()
                cur.execute("SELECT id, display_name, created_at FROM users WHERE id = ?", (user_id,))
                row = cur.fetchone()
                if row:
                    return dict(row)
                
                created = now_iso()
                cur.execute(
                    "INSERT INTO users (id, display_name, created_at) VALUES (?, ?, ?)",
                    (user_id, display_name, created)
                )
                return {"id": user_id, "display_name": display_name, "created_at": created}
        finally:
            conn.close()

    # --- Projects ---
    @staticmethod
    def save_project(project_id: str, name: str, template: str, workspace_path: str):
        conn = get_connection()
        try:
            with conn:
                cur = conn.cursor()
                created = now_iso()
                cur.execute(
                    """
                    INSERT INTO projects (id, name, template, workspace_path, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        name=excluded.name,
                        workspace_path=excluded.workspace_path,
                        updated_at=excluded.updated_at
                    """,
                    (project_id, name, template, workspace_path, created, created)
                )
        finally:
            conn.close()

    @staticmethod
    def get_project(project_id: str) -> Optional[dict]:
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
            row = cur.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    @staticmethod
    def list_projects() -> List[dict]:
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM projects ORDER BY updated_at DESC")
            return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

    # --- Messages (Conversation Memory) ---
    @staticmethod
    def save_message(
        project_id: str,
        role: str,
        content: str,
        user_id: Optional[str] = None,
        user_name: Optional[str] = None
    ) -> dict:
        msg_id = str(uuid.uuid4())
        ts = now_iso()
        conn = get_connection()
        try:
            with conn:
                Repository._ensure_project_stub(conn, project_id)
                conn.execute(
                    """
                    INSERT INTO messages (id, project_id, user_id, user_name, role, content, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (msg_id, project_id, user_id, user_name, role, content, ts)
                )
            return {
                "id": msg_id,
                "project_id": project_id,
                "user_id": user_id,
                "user_name": user_name,
                "role": role,
                "content": content,
                "timestamp": ts
            }
        finally:
            conn.close()

    @staticmethod
    def get_messages(project_id: str, limit: int = 100) -> List[dict]:
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, project_id, user_id, user_name, role, content, timestamp
                FROM messages
                WHERE project_id = ?
                ORDER BY timestamp ASC
                LIMIT ?
                """,
                (project_id, limit)
            )
            return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

    # --- Project Memory ---
    @staticmethod
    def save_memory(
        project_id: str,
        key: str,
        value: str,
        category: str = "general"
    ) -> dict:
        conn = get_connection()
        try:
            ts = now_iso()
            mem_id = str(uuid.uuid4())
            with conn:
                Repository._ensure_project_stub(conn, project_id)
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO project_memories (id, project_id, category, key, value, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(project_id, key) DO UPDATE SET
                        category=excluded.category,
                        value=excluded.value,
                        updated_at=excluded.updated_at
                    """,
                    (mem_id, project_id, category, key, value, ts, ts)
                )
            return {
                "id": mem_id,
                "project_id": project_id,
                "category": category,
                "key": key,
                "value": value,
                "updated_at": ts
            }
        finally:
            conn.close()

    @staticmethod
    def get_memories(project_id: str, category: Optional[str] = None) -> List[dict]:
        conn = get_connection()
        try:
            cur = conn.cursor()
            if category:
                cur.execute(
                    "SELECT * FROM project_memories WHERE project_id = ? AND category = ? ORDER BY updated_at DESC",
                    (project_id, category)
                )
            else:
                cur.execute(
                    "SELECT * FROM project_memories WHERE project_id = ? ORDER BY category, updated_at DESC",
                    (project_id,)
                )
            return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def delete_memory(project_id: str, key_or_id: str) -> bool:
        conn = get_connection()
        try:
            with conn:
                cur = conn.cursor()
                cur.execute(
                    "DELETE FROM project_memories WHERE project_id = ? AND (key = ? OR id = ?)",
                    (project_id, key_or_id, key_or_id)
                )
                return cur.rowcount > 0
        finally:
            conn.close()

    # --- File Versions & Conflict Detection ---
    @staticmethod
    def get_file_version(project_id: str, path: str) -> int:
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT version FROM file_versions WHERE project_id = ? AND path = ?",
                (project_id, path)
            )
            row = cur.fetchone()
            return row["version"] if row else 1
        finally:
            conn.close()

    @staticmethod
    def update_file_version(
        project_id: str,
        path: str,
        content: str,
        updated_by: Optional[str] = None
    ) -> int:
        conn = get_connection()
        try:
            ts = now_iso()
            with conn:
                Repository._ensure_project_stub(conn, project_id)
                cur = conn.cursor()
                cur.execute(
                    "SELECT version FROM file_versions WHERE project_id = ? AND path = ?",
                    (project_id, path)
                )
                row = cur.fetchone()
                new_version = (row["version"] + 1) if row else 1

                cur.execute(
                    """
                    INSERT INTO file_versions (project_id, path, version, content, updated_by, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(project_id, path) DO UPDATE SET
                        version=?,
                        content=excluded.content,
                        updated_by=excluded.updated_by,
                        updated_at=excluded.updated_at
                    """,
                    (project_id, path, new_version, content, updated_by, ts, new_version)
                )
                return new_version
        finally:
            conn.close()

    # --- Git Checkpoints ---
    @staticmethod
    def save_git_checkpoint(project_id: str, commit_hash: str, message: str) -> dict:
        conn = get_connection()
        try:
            chk_id = str(uuid.uuid4())
            ts = now_iso()
            with conn:
                Repository._ensure_project_stub(conn, project_id)
                conn.execute(
                    """
                    INSERT INTO git_checkpoints (id, project_id, commit_hash, message, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (chk_id, project_id, commit_hash, message, ts)
                )
            return {
                "id": chk_id,
                "project_id": project_id,
                "commit_hash": commit_hash,
                "message": message,
                "created_at": ts
            }
        finally:
            conn.close()

    @staticmethod
    def get_git_checkpoints(project_id: str) -> List[dict]:
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM git_checkpoints WHERE project_id = ? ORDER BY created_at DESC",
                (project_id,)
            )
            return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()


repository = Repository()
