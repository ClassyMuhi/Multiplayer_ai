import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Locate .env in backend directory, project root, or CWD
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # backend/
PROJECT_ROOT = BASE_DIR.parent  # Multiplayer_ai/ or workspace root

def _load_env_files():
    # Only load .env files first; only fallback to .env.example if no valid key is loaded
    for env_path in [BASE_DIR / ".env", PROJECT_ROOT / ".env", Path.cwd() / ".env", Path.cwd() / "backend" / ".env"]:
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=True)


_load_env_files()


def _clean_str(val: Optional[str]) -> Optional[str]:
    if not val or not isinstance(val, str):
        return None
    val_clean = val.strip()
    return val_clean if val_clean else None


class Settings(BaseSettings):
    # Server Settings
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = True

    # Summit Workspace Settings
    SUMMIT_WORKSPACE_ROOT: str = "./workspaces"

    # LLM / AI Provider Settings
    AI_MODEL: Optional[str] = None
    AI_API_KEY: Optional[str] = None
    SUMMIT_MODEL: str = "gpt-4o"
    GROQ_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENHANDS_API_KEY: Optional[str] = None

    # Chroma Vector DB Settings
    CHROMA_PERSIST_DIR: str = "./data/chroma"
    CHROMA_COLLECTION_NAME: str = "summit_memories"

    # App Settings
    APP_NAME: str = "Summit AI Coding Workspace"
    APP_VERSION: str = "0.1.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def reload(self):
        """Reload environment variables from .env files dynamically."""
        _load_env_files()
        self.AI_MODEL = _clean_str(os.getenv("AI_MODEL")) or self.AI_MODEL
        self.AI_API_KEY = _clean_str(os.getenv("AI_API_KEY")) or self.AI_API_KEY
        self.SUMMIT_MODEL = _clean_str(os.getenv("SUMMIT_MODEL")) or self.SUMMIT_MODEL
        self.GROQ_API_KEY = _clean_str(os.getenv("GROQ_API_KEY")) or self.GROQ_API_KEY
        self.GEMINI_API_KEY = _clean_str(os.getenv("GEMINI_API_KEY")) or self.GEMINI_API_KEY
        self.OPENAI_API_KEY = _clean_str(os.getenv("OPENAI_API_KEY")) or self.OPENAI_API_KEY
        self.ANTHROPIC_API_KEY = _clean_str(os.getenv("ANTHROPIC_API_KEY")) or self.ANTHROPIC_API_KEY
        self.OPENHANDS_API_KEY = _clean_str(os.getenv("OPENHANDS_API_KEY")) or self.OPENHANDS_API_KEY

    @property
    def api_key(self) -> Optional[str]:
        return (
            _clean_str(os.getenv("AI_API_KEY"))
            or _clean_str(self.AI_API_KEY)
            or _clean_str(os.getenv("GROQ_API_KEY"))
            or _clean_str(self.GROQ_API_KEY)
            or _clean_str(os.getenv("GEMINI_API_KEY"))
            or _clean_str(self.GEMINI_API_KEY)
            or _clean_str(os.getenv("OPENAI_API_KEY"))
            or _clean_str(self.OPENAI_API_KEY)
            or _clean_str(os.getenv("ANTHROPIC_API_KEY"))
            or _clean_str(self.ANTHROPIC_API_KEY)
            or _clean_str(os.getenv("OPENHANDS_API_KEY"))
            or _clean_str(self.OPENHANDS_API_KEY)
        )

    @property
    def model_name(self) -> str:
        return (
            _clean_str(os.getenv("AI_MODEL"))
            or _clean_str(self.AI_MODEL)
            or _clean_str(os.getenv("SUMMIT_MODEL"))
            or _clean_str(self.SUMMIT_MODEL)
            or "gpt-4o"
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
        path = Path(self.CHROMA_PERSIST_DIR)
        if not path.is_absolute():
            return Path.cwd() / path
        return path


settings = Settings()

