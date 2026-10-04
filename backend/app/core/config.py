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

    # LLM / AI Provider Settings
    AI_MODEL: Optional[str] = None
    AI_API_KEY: Optional[str] = None
    SUMMIT_MODEL: str = "gpt-4o"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENHANDS_API_KEY: Optional[str] = None

    # App Settings
    APP_NAME: str = "Summit AI Coding Workspace"
    APP_VERSION: str = "0.1.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def api_key(self) -> Optional[str]:
        return self.AI_API_KEY or self.OPENAI_API_KEY or self.ANTHROPIC_API_KEY or self.OPENHANDS_API_KEY

    @property
    def model_name(self) -> str:
        return self.AI_MODEL or self.SUMMIT_MODEL or "gpt-4o"

    @property
    def workspace_root_path(self) -> Path:
        path = Path(self.SUMMIT_WORKSPACE_ROOT)
        if not path.is_absolute():
            # Resolve relative to project backend root
            return Path.cwd() / path
        return path


settings = Settings()
