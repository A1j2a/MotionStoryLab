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
from ai.providers import OpenRouterProvider, OpenRouterVideoProvider, OpenRouterImageProvider, get_ai_provider
from renderer.compositor import generate_high_ctr_thumbnail

logger = logging.getLogger("studio.api.settings")

router = APIRouter(prefix="/settings", tags=["settings"])

DB_PATH = BASE_DIR / "projects" / "studio.db"

AVAILABLE_MODELS = [
    {"id": "openrouter/free", "name": "OpenRouter Free Auto-Router (100% Free - Works with all Free Keys)", "is_free": True},
    {"id": "meta-llama/llama-3.3-70b-instruct:free", "name": "Meta Llama 3.3 70B Free (100% Free - SOTA SEO & Storyboards)", "is_free": True},
    {"id": "google/gemini-2.0-flash-exp:free", "name": "Google Gemini 2.0 Flash Free (100% Free - Fast & High Context)", "is_free": True},
    {"id": "deepseek/deepseek-r1:free", "name": "DeepSeek R1 Free (100% Free - Deep Reasoning)", "is_free": True},
    {"id": "liquid/lfm-2.5-2.6b:free", "name": "Liquid LFM 2.5 Free (100% Free - Fast Testing)", "is_free": True},
    {"id": "meta-llama/llama-3.3-70b-instruct", "name": "Meta Llama 3.3 70B (Paid SOTA - SEO, Storyboards & Rhymes)", "is_free": False},
    {"id": "qwen/qwen-2.5-72b-instruct", "name": "Qwen 2.5 72B (Paid SOTA - Elite Songwriting & Rhyme Cadence)", "is_free": False},
    {"id": "deepseek/deepseek-r1", "name": "DeepSeek R1 (Paid SOTA - Full Reasoning & Deep Research)", "is_free": False},
    {"id": "deepseek/deepseek-chat", "name": "DeepSeek V3 (Paid SOTA - High Speed 671B General Content)", "is_free": False},
    {"id": "openai/gpt-4o-mini", "name": "GPT-4o Mini (Paid - Fast & Cost-Efficient)", "is_free": False},
    {"id": "openai/gpt-4o", "name": "GPT-4o (Paid Flagship - Premium Metadata & Verses)", "is_free": False},
]

AVAILABLE_VIDEO_MODELS = [
    {"id": "bytedance/seedance-2.0-mini", "name": "ByteDance Seedance 2.0 Mini (Default - High Speed 3D Kids Scene Generation)", "is_free": False},
    {"id": "bytedance/seedance-2.0", "name": "ByteDance Seedance 2.0 Pro (Ultra HD 3D Dynamic Animation)", "is_free": False},
    {"id": "klingai/kling-v1.6-standard", "name": "Kling AI 1.6 Standard (Vibrant Character Physics & Movement)", "is_free": False},
    {"id": "klingai/kling-v1.6-pro", "name": "Kling AI 1.6 Pro (Cinema Quality 3D Animation)", "is_free": False},
    {"id": "luma/ray-2", "name": "Luma Ray 2 (Dynamic Camera & Photorealistic Cartoon Lighting)", "is_free": False},
    {"id": "minimax/video-01", "name": "MiniMax Video 01 (Complex Multi-character Action)", "is_free": False},
    {"id": "genmo/mochi-1", "name": "Genmo Mochi 1 (Fluid Stylized Motion)", "is_free": False},
]

AVAILABLE_THUMBNAIL_MODELS = [
    {"id": "high_ctr_graphic", "name": "High-CTR 3D Visual Graphic Engine (Local Fast, 100% Free & High CPM)", "is_free": True},
    {"id": "openai/dall-e-3", "name": "DALL-E 3 (OpenAI High-CTR Pixar Kids Cover)", "is_free": False},
    {"id": "black-forest-labs/flux-1-schnell", "name": "Flux 1 Schnell (Ultra Fast High-CTR 3D Rendering)", "is_free": False},
    {"id": "black-forest-labs/flux-1-dev", "name": "Flux 1 Dev (High Fidelity 3D Character Poster)", "is_free": False},
    {"id": "google/imagen-3", "name": "Google Imagen 3 (Vibrant Saturated YouTube Kids Style)", "is_free": False},
]


class AISettingsResponse(BaseModel):
    openrouter_enabled: bool
    openrouter_api_key: str
    openrouter_api_key_masked: str
    openrouter_model: str
    active_provider: str
    available_models: list

    # Video Settings
    openrouter_video_enabled: bool = False
    openrouter_video_model: str = "bytedance/seedance-2.0-mini"
    video_aspect_ratio: str = "16:9"
    available_video_models: list = []

    # Thumbnail Settings
    thumbnail_generator_enabled: bool = True
    thumbnail_engine: str = "high_ctr_graphic"
    thumbnail_model: str = "high_ctr_graphic"
    thumbnail_aspect_ratio: str = "16:9"
    available_thumbnail_models: list = []

    # Audio & Suno Mode Settings
    auto_song_generation_enabled: bool = True


class UpdateAISettingsRequest(BaseModel):
    openrouter_enabled: bool
    openrouter_api_key: Optional[str] = None
    openrouter_model: Optional[str] = "deepseek/deepseek-r1:free"

    # Video Settings
    openrouter_video_enabled: Optional[bool] = False
    openrouter_video_model: Optional[str] = "bytedance/seedance-2.0-mini"
    video_aspect_ratio: Optional[str] = "16:9"

    # Thumbnail Settings
    thumbnail_generator_enabled: Optional[bool] = True
    thumbnail_engine: Optional[str] = "high_ctr_graphic"
    thumbnail_model: Optional[str] = "high_ctr_graphic"
    thumbnail_aspect_ratio: Optional[str] = "16:9"
    auto_song_generation_enabled: Optional[bool] = True


class TestOpenRouterRequest(BaseModel):
    api_key: Optional[str] = None
    model: Optional[str] = None


class TestVideoRequest(BaseModel):
    api_key: Optional[str] = None
    model: Optional[str] = "bytedance/seedance-2.0-mini"
    aspect_ratio: Optional[str] = "16:9"
    prompt: Optional[str] = "Cute 3D preschool character dancing on a colorful playground, 8k vibrant cartoon animation"


class TestThumbnailRequest(BaseModel):
    title: Optional[str] = "Numbers Farm: 1 to 10 Fun!"
    topic: Optional[str] = "Preschool Rhyme"
    model: Optional[str] = "high_ctr_graphic"
    aspect_ratio: Optional[str] = "16:9"


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

    env_path.write_text(chr(10).join(new_lines) + chr(10), encoding="utf-8")




@router.get("/ai", response_model=AISettingsResponse)
async def get_ai_settings():
    db_key = get_db_config("OPENROUTER_API_KEY", "")
    current_key = db_key or os.environ.get("OPENROUTER_API_KEY", settings.OPENROUTER_API_KEY).strip()

    db_enabled = get_db_config("OPENROUTER_ENABLED", "")
    if db_enabled:
        enabled = db_enabled.lower() in ("true", "1", "yes")
    else:
        enabled = os.environ.get("OPENROUTER_ENABLED", str(settings.OPENROUTER_ENABLED)).lower() in ("true", "1", "yes")

    db_model = get_db_config("OPENROUTER_MODEL", "")
    model = db_model or os.environ.get("OPENROUTER_MODEL", settings.OPENROUTER_MODEL)

    video_enabled_db = get_db_config("OPENROUTER_VIDEO_ENABLED", "false")
    video_enabled = video_enabled_db.lower() in ("true", "1", "yes")
    video_model = get_db_config("OPENROUTER_VIDEO_MODEL", "bytedance/seedance-2.0-mini")
    video_ratio = get_db_config("VIDEO_ASPECT_RATIO", "16:9")

    thumb_enabled_db = get_db_config("THUMBNAIL_GENERATOR_ENABLED", "true")
    thumb_enabled = thumb_enabled_db.lower() in ("true", "1", "yes")
    thumb_engine = get_db_config("THUMBNAIL_ENGINE", "high_ctr_graphic")
    thumb_model = get_db_config("THUMBNAIL_MODEL", "high_ctr_graphic")
    thumb_ratio = get_db_config("THUMBNAIL_ASPECT_RATIO", "16:9")
    auto_song_db = get_db_config("AUTO_SONG_GENERATION_ENABLED", "true")
    auto_song_enabled = auto_song_db.lower() in ("true", "1", "yes")

    provider_instance = get_ai_provider()
    active_provider_name = provider_instance.__class__.__name__

    return AISettingsResponse(
        openrouter_enabled=enabled,
        openrouter_api_key=current_key,
        openrouter_api_key_masked=mask_key(current_key),
        openrouter_model=model,
        active_provider=active_provider_name,
        available_models=AVAILABLE_MODELS,
        openrouter_video_enabled=video_enabled,
        openrouter_video_model=video_model,
        video_aspect_ratio=video_ratio,
        available_video_models=AVAILABLE_VIDEO_MODELS,
        thumbnail_generator_enabled=thumb_enabled,
        thumbnail_engine=thumb_engine,
        thumbnail_model=thumb_model,
        thumbnail_aspect_ratio=thumb_ratio,
        available_thumbnail_models=AVAILABLE_THUMBNAIL_MODELS,
        auto_song_generation_enabled=auto_song_enabled,
    )


@router.post("/ai", response_model=AISettingsResponse)
async def update_ai_settings(payload: UpdateAISettingsRequest):
    env_updates = {
        "OPENROUTER_ENABLED": "true" if payload.openrouter_enabled else "false",
        "OPENROUTER_MODEL": payload.openrouter_model or "deepseek/deepseek-r1:free",
        "OPENROUTER_VIDEO_ENABLED": "true" if payload.openrouter_video_enabled else "false",
        "OPENROUTER_VIDEO_MODEL": payload.openrouter_video_model or "bytedance/seedance-2.0-mini",
        "VIDEO_ASPECT_RATIO": payload.video_aspect_ratio or "16:9",
        "THUMBNAIL_GENERATOR_ENABLED": "true" if payload.thumbnail_generator_enabled else "false",
        "THUMBNAIL_ENGINE": payload.thumbnail_engine or "high_ctr_graphic",
        "THUMBNAIL_MODEL": payload.thumbnail_model or "high_ctr_graphic",
        "THUMBNAIL_ASPECT_RATIO": payload.thumbnail_aspect_ratio or "16:9",
        "AUTO_SONG_GENERATION_ENABLED": "true" if payload.auto_song_generation_enabled is not False else "false",
    }

    for k, v in env_updates.items():
        set_db_config(k, v)
        os.environ[k] = v

    if payload.openrouter_api_key and not payload.openrouter_api_key.startswith("***"):
        clean_key = payload.openrouter_api_key.strip()
        env_updates["OPENROUTER_API_KEY"] = clean_key
        os.environ["OPENROUTER_API_KEY"] = clean_key
        settings.OPENROUTER_API_KEY = clean_key
        set_db_config("OPENROUTER_API_KEY", clean_key)

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
        openrouter_video_enabled=payload.openrouter_video_enabled or False,
        openrouter_video_model=payload.openrouter_video_model or "bytedance/seedance-2.0-mini",
        video_aspect_ratio=payload.video_aspect_ratio or "16:9",
        available_video_models=AVAILABLE_VIDEO_MODELS,
        thumbnail_generator_enabled=payload.thumbnail_generator_enabled if payload.thumbnail_generator_enabled is not None else True,
        thumbnail_engine=payload.thumbnail_engine or "high_ctr_graphic",
        thumbnail_model=payload.thumbnail_model or "high_ctr_graphic",
        thumbnail_aspect_ratio=payload.thumbnail_aspect_ratio or "16:9",
        available_thumbnail_models=AVAILABLE_THUMBNAIL_MODELS,
        auto_song_generation_enabled=payload.auto_song_generation_enabled if payload.auto_song_generation_enabled is not None else True,
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


@router.post("/video/test")
async def test_video_generation(payload: TestVideoRequest):
    api_key = payload.api_key or get_db_config("OPENROUTER_API_KEY", "") or os.environ.get("OPENROUTER_API_KEY", settings.OPENROUTER_API_KEY)
    model = payload.model or get_db_config("OPENROUTER_VIDEO_MODEL", "bytedance/seedance-2.0-mini")
    aspect_ratio = payload.aspect_ratio or get_db_config("VIDEO_ASPECT_RATIO", "16:9")

    if not api_key or api_key.startswith("***"):
        api_key = get_db_config("OPENROUTER_API_KEY", "") or os.environ.get("OPENROUTER_API_KEY", settings.OPENROUTER_API_KEY)

    if not api_key:
        raise HTTPException(status_code=400, detail="OpenRouter API Key is required to test video generation.")

    provider = OpenRouterVideoProvider(api_key=api_key, model=model, aspect_ratio=aspect_ratio)
    start_time = time.time()
    job = provider.submit_video_job(payload.prompt or "A cute 3D preschool character dancing", model=model, aspect_ratio=aspect_ratio)
    latency_ms = int((time.time() - start_time) * 1000)

    if not job:
        raise HTTPException(status_code=502, detail=f"OpenRouter Video submission failed: {provider.last_error}")

    return {
        "success": True,
        "job_id": job.get("id"),
        "polling_url": job.get("polling_url"),
        "model": model,
        "aspect_ratio": aspect_ratio,
        "latency_ms": latency_ms,
        "message": f"Video generation job submitted successfully to {model}!",
    }


@router.post("/thumbnail/test")
async def test_thumbnail_generation(payload: TestThumbnailRequest):
    test_out = BASE_DIR / "projects" / "test_thumbnail.jpg"
    try:
        generate_high_ctr_thumbnail(
            title=payload.title or "Numbers Farm: 1 to 10 Fun!",
            topic=payload.topic or "Preschool Rhyme",
            output_thumbnail_path=str(test_out),
            aspect_ratio=payload.aspect_ratio or "16:9",
        )
        return {
            "success": True,
            "model": payload.model,
            "aspect_ratio": payload.aspect_ratio,
            "message": "High-CTR YouTube Kids Thumbnail generated successfully!",
            "file_size": test_out.stat().st_size if test_out.exists() else 0,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Thumbnail generation failed: {e}")