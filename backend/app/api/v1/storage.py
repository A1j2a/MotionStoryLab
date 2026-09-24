import os
import shutil
from pathlib import Path
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status
from app.core.config import settings

router = APIRouter(prefix="/storage", tags=["Storage Management"])


def get_dir_size_bytes(path: Path) -> int:
    total = 0
    if not path.exists():
        return 0
    for root, _, files in os.walk(str(path)):
        for f in files:
            fp = os.path.join(root, f)
            try:
                total += os.path.getsize(fp)
            except OSError:
                pass
    return total


def format_bytes(bytes_count: int) -> str:
    if bytes_count < 1024:
        return f"{bytes_count} B"
    elif bytes_count < 1024 * 1024:
        return f"{bytes_count / 1024:.1f} KB"
    elif bytes_count < 1024 * 1024 * 1024:
        return f"{bytes_count / (1024 * 1024):.1f} MB"
    else:
        return f"{bytes_count / (1024 * 1024 * 1024):.2f} GB"


@router.get("/status")
async def get_storage_status() -> Dict[str, Any]:
    project_dir = settings.resolved_project_dir
    log_dir = settings.resolved_log_dir

    project_size = get_dir_size_bytes(project_dir)
    log_size = get_dir_size_bytes(log_dir)
    total_size = project_size + log_size

    # Count project folders
    project_count = 0
    if project_dir.exists():
        project_count = len([d for d in project_dir.iterdir() if d.is_dir()])

    return {
        "status": "healthy",
        "total_bytes": total_size,
        "total_formatted": format_bytes(total_size),
        "projects_bytes": project_size,
        "projects_formatted": format_bytes(project_size),
        "logs_bytes": log_size,
        "logs_formatted": format_bytes(log_size),
        "project_count": project_count,
        "project_dir": str(project_dir),
    }


@router.post("/clear")
async def clear_storage(purge_all: bool = False) -> Dict[str, Any]:
    """
    Cleans up storage:
    - If purge_all is False: removes temporary frame sequences, intermediate clips, and scratch files, keeping final.mp4 and master audio.
    - If purge_all is True: removes all projects and resets studio database storage.
    """
    project_dir = settings.resolved_project_dir
    cleaned_bytes = 0

    if not project_dir.exists():
        return {"cleared": True, "cleaned_bytes": 0, "cleaned_formatted": "0 B"}

    for item in project_dir.iterdir():
        if item.is_dir():
            if purge_all:
                cleaned_bytes += get_dir_size_bytes(item)
                shutil.rmtree(str(item), ignore_errors=True)
            else:
                # Clean scene frame directories and temp configs
                scenes_dir = item / "scenes"
                if scenes_dir.exists():
                    for sub in scenes_dir.iterdir():
                        if sub.is_dir() and "frames" in sub.name:
                            cleaned_bytes += get_dir_size_bytes(sub)
                            shutil.rmtree(str(sub), ignore_errors=True)

    return {
        "cleared": True,
        "cleaned_bytes": cleaned_bytes,
        "cleaned_formatted": format_bytes(cleaned_bytes),
        "message": "Storage cache successfully cleaned!" if not purge_all else "All projects and storage reset successfully!",
    }
