import os
import shutil
import subprocess
from contextlib import asynccontextmanager
from typing import Dict, Any
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure system tool paths (/opt/homebrew/bin, /usr/local/bin) are in PATH
for p in ["/opt/homebrew/bin", "/usr/local/bin"]:
    if p not in os.environ.get("PATH", ""):
        os.environ["PATH"] = f"{p}:{os.environ.get('PATH', '')}"

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.db.init_db import init_db

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB tables
    await init_db()
    yield
    # Shutdown


app = FastAPI(
    title="AI Kids Video Studio API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS restricted to local origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"http://127.0.0.1:{settings.FRONTEND_PORT}",
        f"http://localhost:{settings.FRONTEND_PORT}",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Mount API v1 router
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Exposes service health status for Backend, Ollama, n8n, ComfyUI, TTS, and FFmpeg.
    """
    results: Dict[str, Any] = {
        "status": "healthy",
        "backend": {"status": "connected", "port": settings.BACKEND_PORT},
    }

    # Helper async check
    async def check_url(url: str) -> bool:
        try:
            async with httpx.AsyncClient(timeout=1.5) as client:
                res = await client.get(url)
                return res.status_code < 500
        except Exception:
            return False

    # Check Ollama AI Engine (Port 11434)
    ollama_ok = await check_url(f"{settings.OLLAMA_URL}/api/version") or await check_url(f"{settings.OLLAMA_URL}/")
    results["ollama"] = {"status": "connected" if ollama_ok else "offline", "url": settings.OLLAMA_URL, "model": settings.OLLAMA_MODEL}

    # Check n8n
    n8n_ok = await check_url(f"{settings.N8N_URL}/healthz")
    results["n8n"] = {"status": "connected" if n8n_ok else "offline", "url": settings.N8N_URL}

    # Check ComfyUI
    comfy_ok = await check_url(f"{settings.COMFYUI_URL}/system_stats")
    results["comfyui"] = {"status": "connected" if comfy_ok else "offline", "url": settings.COMFYUI_URL}

    # Check TTS
    tts_ok = await check_url(f"{settings.KOKORO_TTS_URL}/health")
    results["tts"] = {"status": "connected" if tts_ok else "offline", "url": settings.KOKORO_TTS_URL}

    # Check FFmpeg binary
    ffmpeg_bin = shutil.which("ffmpeg")
    results["ffmpeg"] = {
        "status": "connected" if ffmpeg_bin else "offline",
        "path": ffmpeg_bin,
    }

    return results
