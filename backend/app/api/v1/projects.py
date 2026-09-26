import os
import asyncio
from typing import List, Optional, Dict, Any
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db_session
from app.models.project import Project
from app.models.job import Job, JobStatus
from app.repositories.project_repo import ProjectRepository
from app.repositories.job_repo import JobRepository
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectRead
from app.schemas.character import CharacterRead
from app.schemas.scene import SceneRead
from app.schemas.job import JobRead
from app.schemas.asset import AssetRead
from app.core.config import settings
from app.core.pipeline import run_project_pipeline
from ai.planner import generate_seo_metadata

router = APIRouter(prefix="/projects", tags=["projects"])


class ProjectDetailRead(ProjectRead):
    characters: List[CharacterRead] = []
    scenes: List[SceneRead] = []
    jobs: List[JobRead] = []
    assets: List[AssetRead] = []


@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
):
    project_repo = ProjectRepository(session)
    job_repo = JobRepository(session)

    # 1. Create project
    project = Project(
        title=payload.title,
        topic=payload.topic,
        language=payload.language,
        duration_min=payload.duration_min,
        duration_max=payload.duration_max,
        video_type=payload.video_type,
        visual_style=payload.visual_style,
        target_age=payload.target_age,
        character_style=payload.character_style,
        music_style=payload.music_style,
        voice_style=payload.voice_style,
        status="DRAFT",
    )
    created = await project_repo.create(project)

    # 2. Automatically initialize initial DRAFT job
    await job_repo.create(
        Job(
            project_id=created.id,
            status=JobStatus.PLANNING,
            current_step="PROJECT_CREATED",
            progress=5,
        )
    )

    # 3. Launch the video generation pipeline safely in the background
    asyncio.create_task(run_project_pipeline(created.id))

    return created


@router.post("/{project_id}/generate", status_code=status.HTTP_202_ACCEPTED)
async def trigger_generation(
    project_id: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
):
    repo = ProjectRepository(session)
    project = await repo.get(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found",
        )

    # Launch pipeline
    background_tasks.add_task(run_project_pipeline, project_id)
    return {
        "status": "started",
        "project_id": project_id,
        "message": "Automated video generation pipeline initiated",
    }


@router.get("/{project_id}/video")
async def get_project_video(
    project_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    repo = ProjectRepository(session)
    project = await repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_dir = Path(str(settings.resolved_project_dir)) / project_id
    video_path = project_dir / "output" / "final_video.mp4"
    if not video_path.exists():
        video_path = project_dir / "final.mp4"
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video rendering or assembly not yet complete")

    return FileResponse(str(video_path), media_type="video/mp4", filename=f"{project.title}.mp4")


@router.get("/{project_id}/thumbnail")
async def get_project_thumbnail(
    project_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    repo = ProjectRepository(session)
    project = await repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_dir = Path(str(settings.resolved_project_dir)) / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    thumb_path = project_dir / "thumbnail.jpg"

    if not thumb_path.exists():
        from renderer.compositor import generate_high_ctr_thumbnail
        from app.models.character import Character
        from app.models.asset import Asset
        import asyncio

        meta = project.metadata_json or {}
        seo = meta.get("manual_seo") or {}
        title = seo.get("title") or project.title or project.topic or "Preschool Kids Song"
        topic = project.topic or project.title or "Nursery Rhymes"

        char_res = await session.execute(select(Character).where(Character.project_id == project_id))
        chars = char_res.scalars().all()
        char_name = chars[0].name if chars else "Preschool Hero"

        sample_video = None
        for cand in [project_dir / "output" / "final_video.mp4", project_dir / "final.mp4"]:
            if cand.exists():
                sample_video = str(cand)
                break
        if not sample_video:
            uploaded_clips = list((project_dir / "uploaded_scenes").glob("scene_*.mp4"))
            if uploaded_clips:
                sample_video = str(uploaded_clips[0])

        try:
            await asyncio.to_thread(
                generate_high_ctr_thumbnail,
                title=title,
                topic=topic,
                output_thumbnail_path=str(thumb_path),
                video_path=sample_video,
                aspect_ratio="16:9",
                character_name=char_name,
            )
            asset_res = await session.execute(select(Asset).where(Asset.project_id == project_id, Asset.asset_type == "thumbnail"))
            existing_asset = asset_res.scalars().first()
            if not existing_asset:
                session.add(Asset(project_id=project_id, asset_type="thumbnail", file_path=str(thumb_path)))
            else:
                existing_asset.file_path = str(thumb_path)
            await session.commit()
        except Exception as e:
            logger.warning(f"On-demand thumbnail generation failed: {e}")

    if not thumb_path.exists():
        raise HTTPException(status_code=404, detail="Thumbnail not yet generated")

    return FileResponse(str(thumb_path), media_type="image/jpeg", filename="thumbnail.jpg")


@router.get("/{project_id}/seo")
async def get_project_seo(
    project_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    repo = ProjectRepository(session)
    project = await repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    meta = project.metadata_json or {}
    if "seo" in meta and meta["seo"]:
        return meta["seo"]

    seo = generate_seo_metadata(project.topic or project.title, project.title)
    meta_copy = dict(meta)
    meta_copy["seo"] = seo
    project.metadata_json = meta_copy
    await repo.update(project)
    return seo


@router.post("/{project_id}/seo")
async def regenerate_project_seo(
    project_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    repo = ProjectRepository(session)
    project = await repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    seo = generate_seo_metadata(project.topic or project.title, project.title)
    meta_copy = dict(project.metadata_json or {})
    meta_copy["seo"] = seo
    project.metadata_json = meta_copy
    await repo.update(project)
    return seo


@router.get("/", response_model=List[ProjectRead])
async def list_projects(
    status: Optional[str] = Query(None, description="Filter by project status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    repo = ProjectRepository(session)
    return await repo.list_by_status(status=status, skip=skip, limit=limit)


@router.get("/{project_id}", response_model=ProjectDetailRead)
async def get_project(
    project_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    repo = ProjectRepository(session)
    project = await repo.get_with_details(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found",
        )
    return project


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: str,
    payload: ProjectUpdate,
    session: AsyncSession = Depends(get_db_session),
):
    repo = ProjectRepository(session)
    project = await repo.get(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found",
        )

    if payload.title is not None:
        project.title = payload.title
    if payload.status is not None:
        project.status = payload.status
    if payload.lyrics_text is not None:
        project.lyrics_text = payload.lyrics_text
    if payload.metadata_json is not None:
        project.metadata_json = payload.metadata_json

    return await repo.update(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    repo = ProjectRepository(session)
    deleted = await repo.delete(project_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found",
        )
    return None

from pydantic import BaseModel

class GenerateThumbnailRequest(BaseModel):
    aspect_ratio: Optional[str] = "16:9"
    prompt_override: Optional[str] = None


@router.post("/{project_id}/thumbnail/generate")
async def generate_project_thumbnail_endpoint(
    project_id: str,
    payload: Optional[GenerateThumbnailRequest] = None,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Generates an ultra-high CTR, high-CPM YouTube Kids thumbnail for the project.
    """
    from renderer.compositor import generate_high_ctr_thumbnail
    from app.models.asset import Asset
    from app.models.character import Character
    import asyncio

    repo = ProjectRepository(session)
    project = await repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    char_res = await session.execute(select(Character).where(Character.project_id == project_id))
    char_objs = char_res.scalars().all()
    char_name = char_objs[0].name if char_objs else "Preschool Hero"

    project_dir = os.path.join(str(settings.resolved_project_dir), project_id)
    os.makedirs(project_dir, exist_ok=True)
    thumb_path = os.path.join(project_dir, "thumbnail.jpg")
    final_video_path = os.path.join(project_dir, "final.mp4")

    ratio = payload.aspect_ratio if (payload and payload.aspect_ratio) else "16:9"

    await asyncio.to_thread(
        generate_high_ctr_thumbnail,
        title=project.title,
        topic=project.topic or project.title,
        output_thumbnail_path=thumb_path,
        video_path=final_video_path if os.path.exists(final_video_path) else None,
        aspect_ratio=ratio,
        character_name=char_name,
    )

    # Save to Asset
    asset_res = await session.execute(select(Asset).where(Asset.project_id == project_id, Asset.asset_type == "thumbnail"))
    existing_asset = asset_res.scalars().first()
    if not existing_asset:
        session.add(Asset(project_id=project_id, asset_type="thumbnail", file_path=thumb_path))
    else:
        existing_asset.file_path = thumb_path
    await session.commit()

    return {
        "status": "success",
        "thumbnail_url": f"/api/v1/projects/{project_id}/thumbnail",
        "aspect_ratio": ratio,
        "message": "High-CTR YouTube Kids Thumbnail generated successfully!",
    }
