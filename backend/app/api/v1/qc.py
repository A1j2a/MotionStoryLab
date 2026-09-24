import os
import sys
from pathlib import Path
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.api.deps import get_db_session
from app.core.config import settings
from app.models.project import Project
from app.models.scene import Scene
from app.models.character import Character
from app.repositories.project_repo import ProjectRepository
from services.qc_service import run_quality_control

router = APIRouter(prefix="/projects", tags=["qc"])


@router.post("/{project_id}/qc/run", response_model=Dict[str, Any])
async def execute_project_qc(
    project_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Step 21 (Quality Control): Automatically validates Video, Audio, Scenes, Lyrics, Characters, and Subtitles.
    """
    project_repo = ProjectRepository(session)
    project = await project_repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    sc_res = await session.execute(select(Scene).where(Scene.project_id == project_id))
    scenes = sc_res.scalars().all()

    ch_res = await session.execute(select(Character).where(Character.project_id == project_id))
    chars = ch_res.scalars().all()
    char_list = [{"name": c.name, "id": c.name.lower().replace(" ", "_")} for c in chars]

    meta = project.metadata_json or {}
    approved_lyrics = meta.get("approved_lyrics") or project.lyrics_text or ""
    project_dir = os.path.join(str(settings.resolved_project_dir), project_id)

    qc_res = run_quality_control(
        project_dir=project_dir,
        project_title=project.title,
        num_scenes=len(scenes),
        approved_lyrics=approved_lyrics,
        characters=char_list,
    )

    # Persist in project metadata
    meta_copy = dict(meta)
    meta_copy["qc_result"] = qc_res
    project.metadata_json = meta_copy
    await project_repo.update(project)
    await session.commit()

    return qc_res


@router.get("/{project_id}/qc", response_model=Dict[str, Any])
async def get_project_qc_status(
    project_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    project_repo = ProjectRepository(session)
    project = await project_repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    meta = project.metadata_json or {}
    if "qc_result" in meta:
        return meta["qc_result"]

    return await execute_project_qc(project_id, session)
