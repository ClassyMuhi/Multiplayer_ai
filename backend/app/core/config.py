from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Server Settings
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = True

    # Summit Workspace Settings
    SUMMIT_WORKSPACE_ROOT: str = "./workspaces"

    # LLM Settings
    SUMMIT_MODEL: str = "gpt-4o"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENHANDS_API_KEY: Optional[str] = None

    # Database Settings
    DATABASE_URL: str = "sqlite:///./data/app.db"

    # ChromaDB & Semantic Memory Settings
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma"
    EMBEDDING_PROVIDER: str = "default"  # "default", "onnx", "local"
    MEMORY_TOP_K: int = 5
    MEMORY_RELEVANCE_THRESHOLD: float = 1.2
    CHROMA_COLLECTION_NAME: str = "summit_project_memory"

    # App Settings
    APP_NAME: str = "Summit AI Coding Workspace"
    APP_VERSION: str = "0.1.0"

    # Context Builder & Project Intelligence Settings (Phase 3)
    MAX_CONTEXT_FILES: int = 5
    MAX_FILE_SIZE: int = 20000  # Max characters per file read into context
    MAX_CONTEXT_CHARS: int = 50000  # Total prompt context budget
    CONVERSATION_CONTEXT_LIMIT: int = 10  # Recent messages limit
    PROJECT_SUMMARY_MAX_CHARS: int = 2500



    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def workspace_root_path(self) -> Path:
        path = Path(self.SUMMIT_WORKSPACE_ROOT)
        if not path.is_absolute():
            # Resolve relative to project backend root
            return Path.cwd() / path
        return path

    @property
    def chroma_persist_path(self) -> Path:
        path = Path(self.CHROMA_PERSIST_DIRECTORY)
        if not path.is_absolute():
            return Path.cwd() / path
        return path



settings = Settings()
