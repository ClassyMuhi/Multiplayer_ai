import sqlite3
import logging
from pathlib import Path
from typing import Optional
from app.core.config import settings

logger = logging.getLogger("summit.database")

DB_PATH: Optional[Path] = None


def get_db_path() -> Path:
    global DB_PATH
    if DB_PATH is None:
        root = settings.workspace_root_path
        root.mkdir(parents=True, exist_ok=True)
        DB_PATH = root / "summit.db"
    return DB_PATH


def get_connection() -> sqlite3.Connection:
    db_file = get_db_path()
    conn = sqlite3.connect(str(db_file), timeout=10.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """Initializes SQLite database tables if they do not exist."""
    conn = get_connection()
    try:
        with conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    template TEXT,
                    workspace_path TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    user_id TEXT,
                    user_name TEXT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS project_memories (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    category TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
                    UNIQUE(project_id, key)
                );

                CREATE TABLE IF NOT EXISTS file_versions (
                    project_id TEXT NOT NULL,
                    path TEXT NOT NULL,
                    version INTEGER NOT NULL DEFAULT 1,
                    content TEXT,
                    updated_by TEXT,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (project_id, path),
                    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS git_checkpoints (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    commit_hash TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
                );
            """)
        logger.info(f"Database initialized at: {get_db_path()}")
    finally:
        conn.close()
