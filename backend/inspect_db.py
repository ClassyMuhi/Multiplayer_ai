"""
Summit Database Inspector Tool
Inspect SQLite data and ChromaDB vector collections in one command.
Run: python inspect_db.py
"""
import sqlite3
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SQLITE_DB_PATH = BASE_DIR / "workspaces" / "summit.db"
CHROMA_DIR = BASE_DIR / "data" / "chroma"


def inspect_sqlite():
    print("=" * 60)
    print("1. SQLITE DATABASE (Relational Storage)")
    print("=" * 60)
    print(f"Path: {SQLITE_DB_PATH}")

    if not SQLITE_DB_PATH.exists():
        print("Status: Database file not created yet.")
        return

    conn = sqlite3.connect(str(SQLITE_DB_PATH))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Tables list
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in c.fetchall()]
    print(f"Tables: {tables}\n")

    for tbl in ["projects", "project_memories", "messages", "git_checkpoints", "users"]:
        if tbl not in tables:
            continue
        c.execute(f"SELECT COUNT(*) FROM {tbl}")
        count = c.fetchone()[0]
        print(f"--- Table: {tbl} ({count} records) ---")

        c.execute(f"SELECT * FROM {tbl} ORDER BY rowid DESC LIMIT 5")
        rows = c.fetchall()
        for r in rows:
            d = dict(r)
            # Truncate large fields for display
            for k, v in d.items():
                if isinstance(v, str) and len(v) > 80:
                    d[k] = v[:77] + "..."
            print(" ", json.dumps(d, default=str))
        print()


def inspect_chromadb():
    print("=" * 60)
    print("2. CHROMADB (Vector Embedding Storage)")
    print("=" * 60)
    print(f"Path: {CHROMA_DIR}")

    try:
        import chromadb
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        collections = client.list_collections()
        print(f"Collections: {[c.name for c in collections]}")

        for col in collections:
            print(f"\n--- Collection: {col.name} ({col.count()} embeddings) ---")
            data = col.get(limit=5)
            for i in range(len(data.get("ids", []))):
                doc_id = data["ids"][i]
                doc = data["documents"][i] if data.get("documents") else ""
                meta = data["metadatas"][i] if data.get("metadatas") else {}
                print(f"  [ID]: {doc_id}")
                print(f"  [Meta]: {meta}")
                print(f"  [Doc]: {doc[:100]}...\n")
    except ImportError:
        print("Note: 'chromadb' package is optional. Install with `pip install chromadb` if you want to inspect vector tables directly.")
    except Exception as e:
        print(f"ChromaDB Status: {e}")


if __name__ == "__main__":
    inspect_sqlite()
    inspect_chromadb()
