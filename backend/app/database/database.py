import os
import logging
from pathlib import Path
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

from app.core.config import settings

logger = logging.getLogger("summit.database")


def _ensure_sqlite_directory(db_url: str):
    """Ensures that the directory for SQLite file exists."""
    if db_url.startswith("sqlite:///"):
        raw_path = db_url.replace("sqlite:///", "")
        # Remove query parameters if present
        if "?" in raw_path:
            raw_path = raw_path.split("?")[0]
        db_path = Path(raw_path)
        if not db_path.is_absolute():
            db_path = (Path.cwd() / db_path).resolve()
        db_path.parent.mkdir(parents=True, exist_ok=True)


_ensure_sqlite_directory(settings.DATABASE_URL)

# Configure SQLite specific engine arguments
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy models."""
    pass


def init_db():
    """
    Initializes the database schema and creates all tables if they don't exist.
    Safe to call on every application startup.
    """
    _ensure_sqlite_directory(settings.DATABASE_URL)
    # Import models so they are registered with Base metadata
    import app.database.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    logger.info("Database schema initialized successfully.")


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session and ensures proper closure.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
