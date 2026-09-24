import os
from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.core.config import settings
from app.models.project import Project
from app.models.job import Job, JobStatus
from app.models.scene import Scene

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    # 1. Total projects
    proj_count_res = await session.execute(select(func.count(Project.id)))
    total_projects = proj_count_res.scalar() or 0

    # 2. Projects grouped by status
    status_res = await session.execute(
        select(Project.status, func.count(Project.id)).group_by(Project.status)
    )
    projects_by_status = dict(status_res.all())

    # 3. Active jobs
    active_statuses = [
        JobStatus.PLANNING,
        JobStatus.ASSET_GENERATION,
        JobStatus.AUDIO_GENERATION,
        JobStatus.ANIMATION,
        JobStatus.RENDERING,
        JobStatus.COMPOSITING,
        JobStatus.QUALITY_CHECK,
        JobStatus.UPLOADING,
    ]
    active_jobs_res = await session.execute(
        select(func.count(Job.id)).where(Job.status.in_(active_statuses))
    )
    active_jobs = active_jobs_res.scalar() or 0

    # 4. Total and completed scenes
    total_scenes_res = await session.execute(select(func.count(Scene.id)))
    total_scenes = total_scenes_res.scalar() or 0

    completed_scenes_res = await session.execute(
        select(func.count(Scene.id)).where(Scene.status == "COMPLETED")
    )
    completed_scenes = completed_scenes_res.scalar() or 0

    # 5. Storage calculation for projects directory
    project_dir = settings.resolved_project_dir
    total_bytes = 0
    if project_dir.exists():
        for root, _, files in os.walk(project_dir):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    total_bytes += os.path.getsize(fp)
                except OSError:
                    pass

    return {
        "total_projects": total_projects,
        "projects_by_status": projects_by_status,
        "active_jobs": active_jobs,
        "total_scenes": total_scenes,
        "completed_scenes": completed_scenes,
        "storage_used_bytes": total_bytes,
        "storage_used_mb": round(total_bytes / (1024 * 1024), 2),
    }
