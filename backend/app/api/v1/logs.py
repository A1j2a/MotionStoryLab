import re
from pathlib import Path
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status
from app.core.config import settings

router = APIRouter(prefix="/logs", tags=["logs"])


def get_safe_log_files() -> List[str]:
    log_dir = settings.resolved_log_dir
    if not log_dir.exists():
        return ["app.log"]
    files = []
    for f in log_dir.glob("*.log"):
        if f.is_file() and not f.name.startswith("."):
            files.append(f.name)
    default_files = ["app.log", "ai.log", "blender.log", "comfyui.log", "ffmpeg.log", "tts.log", "ollama.log", "n8n.log"]
    for df in default_files:
        if df not in files:
            files.append(df)
    return sorted(files)


@router.get("/")
async def list_available_logs() -> Dict[str, Any]:
    """
    Lists all available log files and their on-disk status.
    """
    log_dir = settings.resolved_log_dir
    safe_files = get_safe_log_files()
    logs_info = []
    for filename in safe_files:
        file_path = log_dir / filename
        exists = file_path.is_file()
        size = file_path.stat().st_size if exists else 0
        logs_info.append(
            {
                "filename": filename,
                "exists": exists,
                "size_bytes": size,
            }
        )
    return {"logs": logs_info}


@router.get("/{filename}")
async def read_log_file(
    filename: str,
    lines: int = Query(150, ge=1, le=1000, description="Number of tail lines to read"),
) -> Dict[str, Any]:
    """
    Securely reads recent lines from any active tool log file.
    """
    # Sanitize filename (letters, numbers, underscores, dashes, dots only)
    if not re.match(r"^[a-zA-Z0-9_\-]+\.log$", filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid log filename format. Must be <name>.log",
        )

    log_path = settings.resolved_log_dir / filename

    if not log_path.exists():
        return {
            "filename": filename,
            "lines": [],
            "total_lines": 0,
            "message": f"Log file '{filename}' has not recorded entries yet.",
        }

    try:
        content = log_path.read_text(encoding="utf-8", errors="replace")
        all_lines = content.splitlines()
        tail_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        return {
            "filename": filename,
            "total_lines": len(all_lines),
            "lines": tail_lines,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read log file: {str(e)}",
        )
