import os
import re
import time
import shutil
import sqlite3
import logging
import subprocess
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.core.config import settings, BASE_DIR
from ai.providers import OpenRouterProvider, OpenRouterImageProvider, get_ai_provider
from renderer.compositor import generate_high_ctr_thumbnail, get_ffprobe_path, get_video_duration

logger = logging.getLogger("studio.api.settings")

router = APIRouter(prefix="/settings", tags=["settings"])

DB_PATH = BASE_DIR / "projects" / "studio.db"
ASSETS_DIR = BASE_DIR / "projects" / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

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

AVAILABLE_THUMBNAIL_MODELS = [
    {"id": "high_ctr_graphic", "name": "High-CTR 3D Visual Graphic Engine (Local Fast, 100% Free & High CPM)", "is_free": True},
    {"id": "openai/dall-e-3", "name": "DALL-E 3 (OpenAI High-CTR Pixar Kids Cover)", "is_free": False},
    {"id": "black-forest-labs/flux-1-schnell", "name": "Flux 1 Schnell (Ultra Fast High-CTR 3D Rendering)", "is_free": False},
    {"id": "black-forest-labs/flux-1-dev", "name": "Flux 1 Dev (High Fidelity 3D Character Poster)", "is_free": False},
    {"id": "google/imagen-3", "name": "Google Imagen 3 (Vibrant Saturated YouTube Kids Style)", "is_free": False},
]

AVAILABLE_VIDEO_PROVIDERS = [
    {"id": "wan", "name": "Wan Video (fal-ai/wan-flf2v - First-Frame to Last-Frame 3D)", "recommended": True},
    {"id": "local", "name": "Local 3D Engine (Pure Python & FFmpeg - No Blender Required)", "recommended": False},
]


class AISettingsResponse(BaseModel):
    openrouter_enabled: bool
    openrouter_api_key: str
    openrouter_api_key_masked: str
    openrouter_model: str
    active_provider: str
    available_models: list

    # Video Settings
    video_provider: str = "wan"
    use_wan_video: bool = True
    available_video_providers: list = AVAILABLE_VIDEO_PROVIDERS
    fal_key_configured: bool = False
    fal_key_masked: str = ""
    wan_model: str = "fal-ai/wan-flf2v"
    wan_resolution: str = "720p"
    wan_test_mode: bool = False
    video_aspect_ratio: str = "16:9"

    # AI Thumbnail & Reference Image Settings
    use_ai_thumbnail: bool = False
    use_ai_reference_images: bool = False
    ai_provider_test_mode: bool = False

    # Thumbnail Settings
    thumbnail_generator_enabled: bool = True
    thumbnail_engine: str = "high_ctr_graphic"
    thumbnail_model: str = "high_ctr_graphic"
    thumbnail_aspect_ratio: str = "16:9"
    available_thumbnail_models: list = []

    # Audio & Suno Mode Settings
    auto_song_generation_enabled: bool = True

    # Brand Logo & Compositing Settings
    channel_logo_url: Optional[str] = None
    channel_logo_enabled: bool = True
    channel_logo_position: str = "bottom_right"
    channel_logo_opacity: float = 0.95
    channel_logo_scale: int = 180
    channel_logo_bottom_spacing: int = 24

    # Intro & Outro Video Settings
    intro_clip_url: Optional[str] = None
    intro_enabled: bool = True
    intro_duration: Optional[float] = None
    outro_clip_url: Optional[str] = None
    outro_enabled: bool = True
    outro_duration: Optional[float] = None

    # Multi-track Audio Mixing Settings
    scene_audio_volume: float = 0.70
    song_audio_volume: float = 1.00
    burn_subtitles: bool = True
    subtitle_font_size: int = 24


class UpdateAISettingsRequest(BaseModel):
    openrouter_enabled: bool
    openrouter_api_key: Optional[str] = None
    openrouter_model: Optional[str] = "deepseek/deepseek-r1:free"

    # Video Settings
    video_provider: Optional[str] = "wan"
    use_wan_video: Optional[bool] = True
    fal_key: Optional[str] = None
    wan_model: Optional[str] = "fal-ai/wan-flf2v"
    wan_resolution: Optional[str] = "720p"
    wan_test_mode: Optional[bool] = False
    video_aspect_ratio: Optional[str] = "16:9"

    # AI Thumbnail & Reference Image Settings
    use_ai_thumbnail: Optional[bool] = False
    use_ai_reference_images: Optional[bool] = False
    ai_provider_test_mode: Optional[bool] = False

    # Thumbnail Settings
    thumbnail_generator_enabled: Optional[bool] = True
    thumbnail_engine: Optional[str] = "high_ctr_graphic"
    thumbnail_model: Optional[str] = "high_ctr_graphic"
    thumbnail_aspect_ratio: Optional[str] = "16:9"
    auto_song_generation_enabled: Optional[bool] = True

    # Brand Logo & Compositing Settings
    channel_logo_enabled: Optional[bool] = True
    channel_logo_position: Optional[str] = "bottom_right"
    channel_logo_opacity: Optional[float] = 0.95
    channel_logo_scale: Optional[int] = 180
    channel_logo_bottom_spacing: Optional[int] = 24

    # Intro & Outro Video Settings
    intro_enabled: Optional[bool] = True
    outro_enabled: Optional[bool] = True

    # Audio Mixing Settings
    scene_audio_volume: Optional[float] = 0.70
    song_audio_volume: Optional[float] = 1.00
    burn_subtitles: Optional[bool] = True
    subtitle_font_size: Optional[int] = 24



class TestOpenRouterRequest(BaseModel):
    api_key: Optional[str] = None
    model: Optional[str] = None


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

    video_ratio = get_db_config("VIDEO_ASPECT_RATIO", "16:9")

    thumb_enabled_db = get_db_config("THUMBNAIL_GENERATOR_ENABLED", "true")
    thumb_enabled = thumb_enabled_db.lower() in ("true", "1", "yes")
    thumb_engine = get_db_config("THUMBNAIL_ENGINE", "high_ctr_graphic")
    thumb_model = get_db_config("THUMBNAIL_MODEL", "high_ctr_graphic")
    thumb_ratio = get_db_config("THUMBNAIL_ASPECT_RATIO", "16:9")
    auto_song_db = get_db_config("AUTO_SONG_GENERATION_ENABLED", "true")
    auto_song_enabled = auto_song_db.lower() in ("true", "1", "yes")

    # Wan & Video Provider settings
    vid_provider = get_db_config("VIDEO_PROVIDER", os.environ.get("VIDEO_PROVIDER", "wan"))
    use_wan_db = get_db_config("USE_WAN_VIDEO", os.environ.get("USE_WAN_VIDEO", "true" if vid_provider == "wan" else "false"))
    use_wan_video = use_wan_db.lower() in ("true", "1", "yes")

    use_ai_thumb_db = get_db_config("USE_AI_THUMBNAIL", os.environ.get("USE_AI_THUMBNAIL", "false"))
    use_ai_thumbnail = use_ai_thumb_db.lower() in ("true", "1", "yes")

    use_ai_ref_db = get_db_config("USE_AI_REFERENCE_IMAGES", os.environ.get("USE_AI_REFERENCE_IMAGES", "false"))
    use_ai_ref = use_ai_ref_db.lower() in ("true", "1", "yes")

    ai_test_db = get_db_config("AI_PROVIDER_TEST_MODE", os.environ.get("AI_PROVIDER_TEST_MODE", "false"))
    ai_test_mode = ai_test_db.lower() in ("true", "1", "yes")

    fal_key_raw = get_db_config("FAL_KEY", os.environ.get("FAL_KEY", ""))
    fal_configured = bool(fal_key_raw and len(fal_key_raw) > 5)
    wan_model_val = get_db_config("WAN_MODEL", os.environ.get("WAN_MODEL", "fal-ai/wan-flf2v"))
    wan_res_val = get_db_config("WAN_RESOLUTION", os.environ.get("WAN_RESOLUTION", "720p"))
    wan_test_db = get_db_config("VIDEO_GENERATION_TEST_MODE", os.environ.get("VIDEO_GENERATION_TEST_MODE", "false"))
    wan_test_mode = wan_test_db.lower() in ("true", "1", "yes") or ai_test_mode

    provider_instance = get_ai_provider()
    active_provider_name = provider_instance.__class__.__name__

    # Brand Logo & Compositing settings
    logo_file = ASSETS_DIR / "channel_logo.png"
    logo_url = "/api/v1/settings/logo" if logo_file.exists() else None
    logo_enabled = get_db_config("CHANNEL_LOGO_ENABLED", "true").lower() in ("true", "1", "yes")
    logo_pos = get_db_config("CHANNEL_LOGO_POSITION", "bottom_right")
    logo_opacity = float(get_db_config("CHANNEL_LOGO_OPACITY", "0.95"))
    logo_scale = int(get_db_config("CHANNEL_LOGO_SCALE", "180"))
    logo_bottom_spacing = int(get_db_config("CHANNEL_LOGO_BOTTOM_SPACING", "24"))

    # Intro & Outro settings
    intro_file = ASSETS_DIR / "intro_clip.mp4"
    intro_url = "/api/v1/settings/intro" if intro_file.exists() else None
    intro_enabled = get_db_config("INTRO_ENABLED", "true").lower() in ("true", "1", "yes")
    intro_dur = get_video_duration(str(intro_file)) if intro_file.exists() else None

    outro_file = ASSETS_DIR / "outro_clip.mp4"
    outro_url = "/api/v1/settings/outro" if outro_file.exists() else None
    outro_enabled = get_db_config("OUTRO_ENABLED", "true").lower() in ("true", "1", "yes")
    outro_dur = get_video_duration(str(outro_file)) if outro_file.exists() else None

    # Audio Mixing Settings
    scene_vol = float(get_db_config("SCENE_AUDIO_VOLUME", "0.70"))
    song_vol = float(get_db_config("SONG_AUDIO_VOLUME", "1.00"))
    burn_subs = get_db_config("BURN_SUBTITLES", "true").lower() in ("true", "1", "yes")
    sub_size = int(get_db_config("SUBTITLE_FONT_SIZE", "24"))

    return AISettingsResponse(
        openrouter_enabled=enabled,
        openrouter_api_key=current_key,
        openrouter_api_key_masked=mask_key(current_key),
        openrouter_model=model,
        active_provider=active_provider_name,
        available_models=AVAILABLE_MODELS,
        video_provider=vid_provider,
        use_wan_video=use_wan_video,
        available_video_providers=AVAILABLE_VIDEO_PROVIDERS,
        fal_key_configured=fal_configured,
        fal_key_masked=mask_key(fal_key_raw) if fal_configured else "",
        wan_model=wan_model_val,
        wan_resolution=wan_res_val,
        wan_test_mode=wan_test_mode,
        video_aspect_ratio=video_ratio,
        use_ai_thumbnail=use_ai_thumbnail,
        use_ai_reference_images=use_ai_ref,
        ai_provider_test_mode=ai_test_mode,
        thumbnail_generator_enabled=thumb_enabled,
        thumbnail_engine=thumb_engine,
        thumbnail_model=thumb_model,
        thumbnail_aspect_ratio=thumb_ratio,
        available_thumbnail_models=AVAILABLE_THUMBNAIL_MODELS,
        auto_song_generation_enabled=auto_song_enabled,
        channel_logo_url=logo_url,
        channel_logo_enabled=logo_enabled,
        channel_logo_position=logo_pos,
        channel_logo_opacity=logo_opacity,
        channel_logo_scale=logo_scale,
        channel_logo_bottom_spacing=logo_bottom_spacing,
        intro_clip_url=intro_url,
        intro_enabled=intro_enabled,
        intro_duration=intro_dur,
        outro_clip_url=outro_url,
        outro_enabled=outro_enabled,
        outro_duration=outro_dur,
        scene_audio_volume=scene_vol,
        song_audio_volume=song_vol,
        burn_subtitles=burn_subs,
        subtitle_font_size=sub_size,
    )


@router.post("/ai", response_model=AISettingsResponse)
async def update_ai_settings(payload: UpdateAISettingsRequest):
    use_wan_val = payload.use_wan_video if payload.use_wan_video is not None else ((payload.video_provider or "wan").lower() == "wan")
    chosen_provider = "wan" if use_wan_val else "local"

    env_updates = {
        "OPENROUTER_ENABLED": "true" if payload.openrouter_enabled else "false",
        "OPENROUTER_MODEL": payload.openrouter_model or "deepseek/deepseek-r1:free",
        "VIDEO_PROVIDER": chosen_provider,
        "USE_WAN_VIDEO": "true" if use_wan_val else "false",
        "WAN_MODEL": payload.wan_model or "fal-ai/wan-flf2v",
        "WAN_RESOLUTION": payload.wan_resolution or "720p",
        "VIDEO_GENERATION_TEST_MODE": "true" if (payload.wan_test_mode or payload.ai_provider_test_mode) else "false",
        "AI_PROVIDER_TEST_MODE": "true" if payload.ai_provider_test_mode else "false",
        "USE_AI_THUMBNAIL": "true" if payload.use_ai_thumbnail else "false",
        "USE_AI_REFERENCE_IMAGES": "true" if payload.use_ai_reference_images else "false",
        "VIDEO_ASPECT_RATIO": payload.video_aspect_ratio or "16:9",
        "THUMBNAIL_GENERATOR_ENABLED": "true" if payload.thumbnail_generator_enabled else "false",
        "THUMBNAIL_ENGINE": payload.thumbnail_engine or "high_ctr_graphic",
        "THUMBNAIL_MODEL": payload.thumbnail_model or "high_ctr_graphic",
        "THUMBNAIL_ASPECT_RATIO": payload.thumbnail_aspect_ratio or "16:9",
        "AUTO_SONG_GENERATION_ENABLED": "true" if payload.auto_song_generation_enabled is not False else "false",
        "CHANNEL_LOGO_ENABLED": "true" if payload.channel_logo_enabled is not False else "false",
        "CHANNEL_LOGO_POSITION": payload.channel_logo_position or "bottom_right",
        "CHANNEL_LOGO_OPACITY": str(payload.channel_logo_opacity if payload.channel_logo_opacity is not None else 0.95),
        "CHANNEL_LOGO_SCALE": str(payload.channel_logo_scale if payload.channel_logo_scale is not None else 180),
        "CHANNEL_LOGO_BOTTOM_SPACING": str(payload.channel_logo_bottom_spacing if payload.channel_logo_bottom_spacing is not None else 24),
        "INTRO_ENABLED": "true" if payload.intro_enabled is not False else "false",
        "OUTRO_ENABLED": "true" if payload.outro_enabled is not False else "false",
        "SCENE_AUDIO_VOLUME": str(payload.scene_audio_volume if payload.scene_audio_volume is not None else 0.70),
        "SONG_AUDIO_VOLUME": str(payload.song_audio_volume if payload.song_audio_volume is not None else 1.00),
        "BURN_SUBTITLES": "true" if payload.burn_subtitles is not False else "false",
        "SUBTITLE_FONT_SIZE": str(payload.subtitle_font_size if payload.subtitle_font_size is not None else 24),
    }

    if payload.fal_key and not payload.fal_key.startswith("***"):
        clean_fal_key = payload.fal_key.strip()
        env_updates["FAL_KEY"] = clean_fal_key
        set_db_config("FAL_KEY", clean_fal_key)
        os.environ["FAL_KEY"] = clean_fal_key

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
    current_fal_key = get_db_config("FAL_KEY", os.environ.get("FAL_KEY", ""))
    provider_instance = get_ai_provider()

    logo_file = ASSETS_DIR / "channel_logo.png"
    intro_file = ASSETS_DIR / "intro_clip.mp4"
    outro_file = ASSETS_DIR / "outro_clip.mp4"

    return AISettingsResponse(
        openrouter_enabled=payload.openrouter_enabled,
        openrouter_api_key=current_key,
        openrouter_api_key_masked=mask_key(current_key),
        openrouter_model=settings.OPENROUTER_MODEL,
        active_provider=provider_instance.__class__.__name__,
        available_models=AVAILABLE_MODELS,
        video_provider=chosen_provider,
        use_wan_video=use_wan_val,
        available_video_providers=AVAILABLE_VIDEO_PROVIDERS,
        fal_key_configured=bool(current_fal_key and len(current_fal_key) > 5),
        fal_key_masked=mask_key(current_fal_key) if current_fal_key else "",
        wan_model=payload.wan_model or "fal-ai/wan-flf2v",
        wan_resolution=payload.wan_resolution or "720p",
        wan_test_mode=payload.wan_test_mode or False,
        video_aspect_ratio=payload.video_aspect_ratio or "16:9",
        use_ai_thumbnail=bool(payload.use_ai_thumbnail),
        use_ai_reference_images=bool(payload.use_ai_reference_images),
        ai_provider_test_mode=bool(payload.ai_provider_test_mode),
        thumbnail_generator_enabled=payload.thumbnail_generator_enabled if payload.thumbnail_generator_enabled is not None else True,
        thumbnail_engine=payload.thumbnail_engine or "high_ctr_graphic",
        thumbnail_model=payload.thumbnail_model or "high_ctr_graphic",
        thumbnail_aspect_ratio=payload.thumbnail_aspect_ratio or "16:9",
        available_thumbnail_models=AVAILABLE_THUMBNAIL_MODELS,
        auto_song_generation_enabled=payload.auto_song_generation_enabled if payload.auto_song_generation_enabled is not None else True,
        channel_logo_url="/api/v1/settings/logo" if logo_file.exists() else None,
        channel_logo_enabled=payload.channel_logo_enabled if payload.channel_logo_enabled is not None else True,
        channel_logo_position=payload.channel_logo_position or "bottom_right",
        channel_logo_opacity=payload.channel_logo_opacity if payload.channel_logo_opacity is not None else 0.95,
        channel_logo_scale=payload.channel_logo_scale if payload.channel_logo_scale is not None else 180,
        channel_logo_bottom_spacing=payload.channel_logo_bottom_spacing if payload.channel_logo_bottom_spacing is not None else 24,
        intro_clip_url="/api/v1/settings/intro" if intro_file.exists() else None,
        intro_enabled=payload.intro_enabled if payload.intro_enabled is not None else True,
        intro_duration=get_video_duration(str(intro_file)) if intro_file.exists() else None,
        outro_clip_url="/api/v1/settings/outro" if outro_file.exists() else None,
        outro_enabled=payload.outro_enabled if payload.outro_enabled is not None else True,
        outro_duration=get_video_duration(str(outro_file)) if outro_file.exists() else None,
        scene_audio_volume=payload.scene_audio_volume if payload.scene_audio_volume is not None else 0.70,
        song_audio_volume=payload.song_audio_volume if payload.song_audio_volume is not None else 1.00,
        burn_subtitles=payload.burn_subtitles if payload.burn_subtitles is not False else False,
        subtitle_font_size=payload.subtitle_font_size or 24,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Channel Logo & Intro/Outro Asset Management
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/logo/upload")
async def upload_channel_logo(file: UploadFile = File(...)):
    """Upload channel watermark logo (PNG / WEBP / JPG) to be overlaid on videos."""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in [".png", ".webp", ".jpg", ".jpeg"]:
        raise HTTPException(status_code=400, detail="Invalid image format. Please upload PNG, WEBP, or JPG.")

    dest = ASSETS_DIR / "channel_logo.png"
    content = await file.read()
    dest.write_bytes(content)

    set_db_config("CHANNEL_LOGO_PATH", str(dest))
    set_db_config("CHANNEL_LOGO_ENABLED", "true")

    return {
        "status": "success",
        "message": "Channel watermark logo uploaded successfully!",
        "logo_url": "/api/v1/settings/logo",
        "file_size": len(content),
    }


@router.get("/logo")
async def get_channel_logo():
    """Serve the active channel watermark logo."""
    dest = ASSETS_DIR / "channel_logo.png"
    if not dest.exists():
        raise HTTPException(status_code=404, detail="No channel logo uploaded yet")
    return FileResponse(str(dest), media_type="image/png", filename="channel_logo.png")


@router.delete("/logo")
async def delete_channel_logo():
    """Delete the channel watermark logo."""
    dest = ASSETS_DIR / "channel_logo.png"
    if dest.exists():
        dest.unlink()
    set_db_config("CHANNEL_LOGO_PATH", "")
    set_db_config("CHANNEL_LOGO_ENABLED", "false")
    return {"status": "success", "message": "Channel logo removed"}


@router.post("/intro/upload")
async def upload_intro_clip(file: UploadFile = File(...)):
    """Upload default channel intro video clip (MP4 / MOV). Plays before scenes with its own audio."""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in [".mp4", ".mov", ".webm"]:
        raise HTTPException(status_code=400, detail="Invalid video format. Please upload MP4, MOV, or WEBM.")

    dest = ASSETS_DIR / f"intro_clip{ext}"
    dest_final = ASSETS_DIR / "intro_clip.mp4"
    content = await file.read()
    dest.write_bytes(content)

    if ext != ".mp4":
        ffmpeg_bin = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg" or "ffmpeg"
        subprocess.run([ffmpeg_bin, "-y", "-i", str(dest), "-c:v", "libx264", "-c:a", "aac", str(dest_final)], check=True)
    else:
        dest_final = dest

    duration = get_video_duration(str(dest_final))
    set_db_config("INTRO_CLIP_PATH", str(dest_final))
    set_db_config("INTRO_ENABLED", "true")

    return {
        "status": "success",
        "message": "Intro clip uploaded successfully!",
        "intro_url": "/api/v1/settings/intro",
        "duration": duration,
    }


@router.get("/intro")
async def get_intro_clip():
    """Serve the active channel intro clip."""
    dest = ASSETS_DIR / "intro_clip.mp4"
    if not dest.exists():
        raise HTTPException(status_code=404, detail="No intro clip uploaded yet")
    return FileResponse(str(dest), media_type="video/mp4", filename="intro_clip.mp4")


@router.delete("/intro")
async def delete_intro_clip():
    """Delete the channel intro clip."""
    dest = ASSETS_DIR / "intro_clip.mp4"
    if dest.exists():
        dest.unlink()
    set_db_config("INTRO_CLIP_PATH", "")
    set_db_config("INTRO_ENABLED", "false")
    return {"status": "success", "message": "Intro clip removed"}


@router.post("/outro/upload")
async def upload_outro_clip(file: UploadFile = File(...)):
    """Upload default channel outro / end-screen video clip (MP4 / MOV). Plays after scenes with its own audio."""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in [".mp4", ".mov", ".webm"]:
        raise HTTPException(status_code=400, detail="Invalid video format. Please upload MP4, MOV, or WEBM.")

    dest = ASSETS_DIR / f"outro_clip{ext}"
    dest_final = ASSETS_DIR / "outro_clip.mp4"
    content = await file.read()
    dest.write_bytes(content)

    if ext != ".mp4":
        ffmpeg_bin = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg" or "ffmpeg"
        subprocess.run([ffmpeg_bin, "-y", "-i", str(dest), "-c:v", "libx264", "-c:a", "aac", str(dest_final)], check=True)
    else:
        dest_final = dest

    duration = get_video_duration(str(dest_final))
    set_db_config("OUTRO_CLIP_PATH", str(dest_final))
    set_db_config("OUTRO_ENABLED", "true")

    return {
        "status": "success",
        "message": "Outro clip uploaded successfully!",
        "outro_url": "/api/v1/settings/outro",
        "duration": duration,
    }


@router.get("/outro")
async def get_outro_clip():
    """Serve the active channel outro clip."""
    dest = ASSETS_DIR / "outro_clip.mp4"
    if not dest.exists():
        raise HTTPException(status_code=404, detail="No outro clip uploaded yet")
    return FileResponse(str(dest), media_type="video/mp4", filename="outro_clip.mp4")


@router.delete("/outro")
async def delete_outro_clip():
    """Delete the channel outro clip."""
    dest = ASSETS_DIR / "outro_clip.mp4"
    if dest.exists():
        dest.unlink()
    set_db_config("OUTRO_CLIP_PATH", "")
    set_db_config("OUTRO_ENABLED", "false")
    return {"status": "success", "message": "Outro clip removed"}


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