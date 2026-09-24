from pathlib import Path
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status
from app.core.config import settings

router = APIRouter(prefix="/logs", tags=["logs"])

ALLOWED_LOG_FILES = {
    "app.log",
    "ai.log",
    "blender.log",
    "comfyui.log",
    "ffmpeg.log",
}


@router.get("/")
async def list_available_logs() -> Dict[str, Any]:
    """
    Lists the available log files and their on-disk status.
    """
    log_dir = settings.resolved_log_dir
    logs_info = []
    for filename in sorted(ALLOWED_LOG_FILES):
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
    lines: int = Query(100, ge=1, le=1000, description="Number of tail lines to read"),
) -> Dict[str, Any]:
    """
    Securely reads recent lines from an allowed log file.
    Guards against path traversal and unauthorized file reads.
    """
    # Strict allow-list validation
    if filename not in ALLOWED_LOG_FILES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid log file. Allowed: {sorted(list(ALLOWED_LOG_FILES))}",
        )

    log_path = settings.resolved_log_dir / filename

    if not log_path.exists():
        return {
            "filename": filename,
            "lines": [],
            "message": f"Log file '{filename}' has not been written to yet.",
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
            detail="Failed to read log file",
        )
