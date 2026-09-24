import os
import re
import time
import sqlite3
import logging
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import settings, BASE_DIR
from ai.providers import OpenRouterProvider, get_ai_provider

logger = logging.getLogger("studio.api.settings")

router = APIRouter(prefix="/settings", tags=["settings"])

DB_PATH = BASE_DIR / "projects" / "studio.db"

AVAILABLE_MODELS = [
    {"id": "meta-llama/llama-3.3-70b-instruct", "name": "Meta Llama 3.3 70B (Recommended - SOTA SEO, Storyboards & Rhymes)", "is_free": False},
    {"id": "qwen/qwen-2.5-72b-instruct", "name": "Qwen 2.5 72B (Recommended - Elite Songwriting & Rhyme Cadence)", "is_free": False},
    {"id": "deepseek/deepseek-r1", "name": "DeepSeek R1 (Full Reasoning & Deep Research)", "is_free": False},
    {"id": "deepseek/deepseek-chat", "name": "DeepSeek V3 (High Speed 671B General Content)", "is_free": False},
    {"id": "openai/gpt-4o-mini", "name": "GPT-4o Mini (Fast & Cost-Efficient)", "is_free": False},
    {"id": "openai/gpt-4o", "name": "GPT-4o (OpenAI Flagship - Premium Metadata & Verses)", "is_free": False},
    {"id": "liquid/lfm-2.5-2.6b:free", "name": "Liquid LFM 2.5 (Free Tier - Fast Testing)", "is_free": True},
]


class AISettingsResponse(BaseModel):
    openrouter_enabled: bool
    openrouter_api_key: str
    openrouter_api_key_masked: str
    openrouter_model: str
    active_provider: str
    available_models: list


class UpdateAISettingsRequest(BaseModel):
    openrouter_enabled: bool
    openrouter_api_key: Optional[str] = None
    openrouter_model: Optional[str] = "deepseek/deepseek-r1:free"


class TestOpenRouterRequest(BaseModel):
    api_key: Optional[str] = None
    model: Optional[str] = None


def init_config_db():
    try:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(DB_PATH), timeout=10)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS studio_config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f"Could not init config DB: {e}")


def get_db_config(key: str, default: str = "") -> str:
    init_config_db()
    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=10)
        c = conn.cursor()
        c.execute("SELECT value FROM studio_config WHERE key = ?", (key,))
        row = c.fetchone()
        conn.close()
        if row and row[0]:
            return row[0]
    except Exception:
        pass
    return default


def set_db_config(key: str, value: str):
    init_config_db()
    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=10)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO studio_config (key, value) VALUES (?, ?)", (key, value))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f"Failed to persist config {key} to SQLite: {e}")


def mask_key(key: str) -> str:
    if not key:
        return ""
    if len(key) <= 8:
        return "****"
    return f"{key[:6]}...{key[-4:]}"


def update_env_file(key_values: dict):
    """Updates key-values in .env file while preserving comments and structure."""
    env_path = BASE_DIR / ".env"
    lines = []
    if env_path.exists():
        lines = env_path.read_text(encoding="utf-8").splitlines()

    updated_keys = set()
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            k = stripped.split("=", 1)[0].strip()
            if k in key_values:
                new_lines.append(f"{k}={key_values[k]}")
                updated_keys.add(k)
                continue
        new_lines.append(line)

    for k, v in key_values.items():
        if k not in updated_keys:
            new_lines.append(f"{k}={v}")

    env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


@router.get("/ai", response_model=AISettingsResponse)
async def get_ai_settings():
    # 1. Check DB first, then environment
    db_key = get_db_config("OPENROUTER_API_KEY", "")
    current_key = db_key or os.environ.get("OPENROUTER_API_KEY", settings.OPENROUTER_API_KEY).strip()

    db_enabled = get_db_config("OPENROUTER_ENABLED", "")
    if db_enabled:
        enabled = db_enabled.lower() in ("true", "1", "yes")
    else:
        enabled = os.environ.get("OPENROUTER_ENABLED", str(settings.OPENROUTER_ENABLED)).lower() in ("true", "1", "yes")

    db_model = get_db_config("OPENROUTER_MODEL", "")
    model = db_model or os.environ.get("OPENROUTER_MODEL", settings.OPENROUTER_MODEL)

    provider_instance = get_ai_provider()
    active_provider_name = provider_instance.__class__.__name__

    return AISettingsResponse(
        openrouter_enabled=enabled,
        openrouter_api_key=current_key,
        openrouter_api_key_masked=mask_key(current_key),
        openrouter_model=model,
        active_provider=active_provider_name,
        available_models=AVAILABLE_MODELS,
    )


@router.post("/ai", response_model=AISettingsResponse)
async def update_ai_settings(payload: UpdateAISettingsRequest):
    env_updates = {
        "OPENROUTER_ENABLED": "true" if payload.openrouter_enabled else "false",
        "OPENROUTER_MODEL": payload.openrouter_model or "deepseek/deepseek-r1:free",
    }

    # Save to SQLite DB permanently
    set_db_config("OPENROUTER_ENABLED", env_updates["OPENROUTER_ENABLED"])
    set_db_config("OPENROUTER_MODEL", env_updates["OPENROUTER_MODEL"])

    clean_key = None
    if payload.openrouter_api_key and not payload.openrouter_api_key.startswith("***"):
        clean_key = payload.openrouter_api_key.strip()
        env_updates["OPENROUTER_API_KEY"] = clean_key
        os.environ["OPENROUTER_API_KEY"] = clean_key
        settings.OPENROUTER_API_KEY = clean_key
        set_db_config("OPENROUTER_API_KEY", clean_key)

    os.environ["OPENROUTER_ENABLED"] = env_updates["OPENROUTER_ENABLED"]
    os.environ["OPENROUTER_MODEL"] = env_updates["OPENROUTER_MODEL"]
    settings.OPENROUTER_ENABLED = payload.openrouter_enabled
    settings.OPENROUTER_MODEL = payload.openrouter_model or "deepseek/deepseek-r1:free"

    try:
        update_env_file(env_updates)
    except Exception as e:
        logger.warning(f"Could not persist to .env: {e}")

    current_key = get_db_config("OPENROUTER_API_KEY", os.environ.get("OPENROUTER_API_KEY", settings.OPENROUTER_API_KEY))
    provider_instance = get_ai_provider()

    return AISettingsResponse(
        openrouter_enabled=payload.openrouter_enabled,
        openrouter_api_key=current_key,
        openrouter_api_key_masked=mask_key(current_key),
        openrouter_model=settings.OPENROUTER_MODEL,
        active_provider=provider_instance.__class__.__name__,
        available_models=AVAILABLE_MODELS,
    )


@router.post("/ai/test")
async def test_openrouter_connection(payload: TestOpenRouterRequest):
    api_key = payload.api_key or get_db_config("OPENROUTER_API_KEY", "") or os.environ.get("OPENROUTER_API_KEY", settings.OPENROUTER_API_KEY)
    model = payload.model or get_db_config("OPENROUTER_MODEL", "") or os.environ.get("OPENROUTER_MODEL", settings.OPENROUTER_MODEL) or "deepseek/deepseek-r1:free"

    if not api_key or api_key.startswith("***"):
        api_key = get_db_config("OPENROUTER_API_KEY", "") or os.environ.get("OPENROUTER_API_KEY", settings.OPENROUTER_API_KEY)

    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="OpenRouter API Key is missing. Please enter your API key first.",
        )

    provider = OpenRouterProvider(api_key=api_key, model=model)
    start_time = time.time()

    prompt = "Respond with exactly one short cheerful sentence: 'OpenRouter connection verified successfully for MotionStoryLab!'"
    system_prompt = "You are a helpful AI diagnostic assistant. Output plain text only."

    response_text = provider.generate_text(prompt, system_prompt, max_tokens=150)
    latency_ms = int((time.time() - start_time) * 1000)

    if not response_text:
        last_err = getattr(provider, "last_error", "")
        detail_msg = f"OpenRouter error for model '{model}': {last_err}" if last_err else f"OpenRouter call failed for model '{model}'. Please check model slug or credits."
        raise HTTPException(
            status_code=502,
            detail=detail_msg,
        )

    return {
        "success": True,
        "latency_ms": latency_ms,
        "model": model,
        "response": response_text.strip(),
    }
