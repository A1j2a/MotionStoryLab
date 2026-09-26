import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    APP_ENV: str = "local"
    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 3000

    DATABASE_URL: str = "sqlite+aiosqlite:///./projects/studio.db"

    @property
    def resolved_database_url(self) -> str:
        prefix = "sqlite+aiosqlite:///"
        if self.DATABASE_URL.startswith(prefix):
            raw_path = self.DATABASE_URL[len(prefix) :]
            if not Path(raw_path).is_absolute():
                clean_rel = raw_path.lstrip("./")
                return f"{prefix}{BASE_DIR / clean_rel}"
        return self.DATABASE_URL

    # AI Provider Settings
    AI_PROVIDER: str = "ollama"  # openrouter, claude, omniroute, ollama, fallback

    # OpenRouter Integration (Deep Research & Lyrics)
    OPENROUTER_ENABLED: bool = False
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "deepseek/deepseek-r1:free"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    OMNIROUTE_URL: str = "http://127.0.0.1:20128"
    OMNIROUTE_API_KEY: str = ""
    OMNIROUTE_MODEL: str = "omniroute-default"

    OLLAMA_URL: str = "http://127.0.0.1:11434"
    OLLAMA_MODEL: str = "llama3.2"
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"
    SUNO_API_KEY: str = ""
    SUNO_API_URL: str = "http://127.0.0.1:8000/api/v1/mock-suno"
    N8N_URL: str = "http://127.0.0.1:5678"
    COMFYUI_URL: str = "http://127.0.0.1:8188"
    KOKORO_TTS_URL: str = "http://127.0.0.1:8880"

    MAX_RENDER_JOBS: int = 1
    MAX_AI_JOBS: int = 1

    FAL_KEY: str = ""
    WAN_MODEL: str = "fal-ai/wan-flf2v"
    WAN_RESOLUTION: str = "720p"

    YOUTUBE_CLIENT_ID: str = ""
    YOUTUBE_CLIENT_SECRET: str = ""
    YOUTUBE_REFRESH_TOKEN: str = ""

    PROJECT_DIR: str = "./projects"
    LOG_DIR: str = "./logs"

    @property
    def resolved_project_dir(self) -> Path:
        if self.PROJECT_DIR.startswith("./") or not Path(self.PROJECT_DIR).is_absolute():
            clean_rel = self.PROJECT_DIR.lstrip("./")
            return BASE_DIR / clean_rel
        return Path(self.PROJECT_DIR)

    @property
    def resolved_log_dir(self) -> Path:
        if self.LOG_DIR.startswith("./") or not Path(self.LOG_DIR).is_absolute():
            clean_rel = self.LOG_DIR.lstrip("./")
            return BASE_DIR / clean_rel
        return Path(self.LOG_DIR)

    DEFAULT_LANGUAGE: str = "en"
    DEFAULT_DURATION_MIN: int = 5
    DEFAULT_DURATION_MAX: int = 7
    DEFAULT_VIDEO_TYPE: str = "Nursery Rhyme"
    DEFAULT_VISUAL_STYLE: str = "3D Cartoon"
    DEFAULT_TARGET_AGE: str = "Kids"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

# Ensure directories exist
settings.resolved_project_dir.mkdir(parents=True, exist_ok=True)
settings.resolved_log_dir.mkdir(parents=True, exist_ok=True)
