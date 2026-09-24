import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.api.deps import get_db_session
from app.models.project import Project
from app.models.character import Character
from app.models.job import Job, JobStatus
from app.repositories.project_repo import ProjectRepository
from app.repositories.job_repo import JobRepository
from ai.content_package import generate_content_package
from ai.planner import generate_preschool_lyrics

router = APIRouter(prefix="/projects", tags=["content-package"])


class ContentPackageUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    chapters: Optional[List[Dict[str, Any]]] = None
    hashtags: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    story_concept: Optional[str] = None
    approved_lyrics: str
    characters: Optional[List[Dict[str, Any]]] = None
    environments: Optional[List[Dict[str, Any]]] = None
    music_style: Optional[str] = None
    voice_style: Optional[str] = None
    thumbnail_prompt: Optional[str] = None
    target_audience: Optional[str] = None
    educational_angle: Optional[str] = None
    visual_bible: Optional[Dict[str, Any]] = None


@router.post("/{project_id}/content-package/generate", response_model=Dict[str, Any])
async def generate_project_content_package(
    project_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Step 2: Generates complete Content Package (Title, Description, Chapters, Story, Lyrics, Character Bible, Music/Voice).
    """
    project_repo = ProjectRepository(session)
    job_repo = JobRepository(session)

    project = await project_repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    topic = project.topic or project.title
    import asyncio
    duration_mins = float(project.duration_min or 2.0)
    pkg = await asyncio.to_thread(
        generate_content_package,
        topic=topic,
        video_type=project.video_type,
        target_age=project.target_age,
        duration_minutes=duration_mins,
    )

    # Persist in project
    project.title = pkg.get("title", project.title)
    project.lyrics_text = pkg.get("lyrics_full", "")
    meta = dict(project.metadata_json or {})
    meta["content_package"] = pkg
    meta["approved_lyrics"] = pkg.get("lyrics_full", "")
    meta["visual_bible"] = pkg.get("visual_bible", {})
    project.metadata_json = meta
    await project_repo.update(project)

    # Sync Character Bible to database
    from sqlalchemy import delete
    await session.execute(delete(Character).where(Character.project_id == project_id))
    for c in pkg.get("characters", []):
        char_obj = Character(
            project_id=project_id,
            name=c.get("name", "Hero"),
            type=c.get("species", c.get("type", "character")),
            appearance=c.get("appearance", "Cute 3D preschool character"),
            colors=c.get("colors", ["#facc15", "#2563eb"]),
            clothing=c.get("clothing", ""),
            personality=c.get("personality", "Cheerful"),
            age=c.get("age", "Kid"),
            voice=c.get("voice", "tenor_cheerful"),
            animation_set=c.get("animation_set", ["walk", "wave", "dance"]),
        )
        session.add(char_obj)

    # Update job
    jobs = await job_repo.list_by_project(project_id)
    if jobs:
        latest = jobs[0]
        latest.status = JobStatus.CONTENT_GENERATING
        latest.current_step = "CONTENT_PACKAGE_READY"
        latest.progress = 25
        await job_repo.update(latest)

    await session.commit()
    return pkg


@router.get("/{project_id}/content-package", response_model=Dict[str, Any])
async def get_project_content_package(
    project_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    project_repo = ProjectRepository(session)
    project = await project_repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    meta = project.metadata_json or {}
    if "content_package" in meta:
        return meta["content_package"]

    # If not generated yet, generate on the fly
    return await generate_project_content_package(project_id, session)


@router.put("/{project_id}/content-package", response_model=Dict[str, Any])
async def save_approved_content_package(
    project_id: str,
    payload: ContentPackageUpdate,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Step 4: User saves edited Content Package.
    The saved lyrics become approved_lyrics (SOURCE OF TRUTH) for all downstream steps.
    """
    project_repo = ProjectRepository(session)
    job_repo = JobRepository(session)

    project = await project_repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if payload.title:
        project.title = payload.title
    project.lyrics_text = payload.approved_lyrics

    meta = dict(project.metadata_json or {})
    curr_pkg = dict(meta.get("content_package") or {})

    # Update pkg
    curr_pkg["title"] = payload.title or project.title
    if payload.description:
        curr_pkg["description"] = payload.description
    if payload.chapters:
        curr_pkg["chapters"] = payload.chapters
    if payload.hashtags:
        curr_pkg["hashtags"] = payload.hashtags
    if payload.tags:
        curr_pkg["tags"] = payload.tags
    if payload.story_concept:
        curr_pkg["story_concept"] = payload.story_concept
    curr_pkg["lyrics_full"] = payload.approved_lyrics
    curr_pkg["approved_lyrics"] = payload.approved_lyrics
    if payload.characters:
        curr_pkg["characters"] = payload.characters
    if payload.environments:
        curr_pkg["environments"] = payload.environments
    if payload.music_style:
        curr_pkg["music_style"] = payload.music_style
    if payload.voice_style:
        curr_pkg["voice_style"] = payload.voice_style
    if payload.thumbnail_prompt:
        curr_pkg["thumbnail_prompt"] = payload.thumbnail_prompt

    meta["content_package"] = curr_pkg
    meta["approved_lyrics"] = payload.approved_lyrics
    project.metadata_json = meta
    await project_repo.update(project)

    # Sync characters if passed
    if payload.characters:
        from sqlalchemy import delete
        await session.execute(delete(Character).where(Character.project_id == project_id))
        for c in payload.characters:
            char_obj = Character(
                project_id=project_id,
                name=c.get("name", "Hero"),
                type=c.get("species", c.get("type", "character")),
                appearance=c.get("appearance", "Cute 3D preschool character"),
                colors=c.get("colors", ["#facc15", "#2563eb"]),
                clothing=c.get("clothing", ""),
                personality=c.get("personality", "Cheerful"),
                age=c.get("age", "Kid"),
                voice=c.get("voice", "tenor_cheerful"),
                animation_set=c.get("animation_set", ["walk", "wave", "dance"]),
            )
            session.add(char_obj)

    # Update job status to CONTENT_APPROVED
    jobs = await job_repo.list_by_project(project_id)
    if jobs:
        latest = jobs[0]
        latest.status = JobStatus.CONTENT_APPROVED
        latest.current_step = "CONTENT_APPROVED"
        latest.progress = 30
        await job_repo.update(latest)

    await session.commit()
    return curr_pkg


@router.post("/{project_id}/lyrics/regenerate", response_model=Dict[str, Any])
async def regenerate_lyrics_only(
    project_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """Regenerates only the lyrics while preserving rest of package."""
    project_repo = ProjectRepository(session)
    project = await project_repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    topic = project.topic or project.title
    import asyncio
    lyrics_data = await asyncio.to_thread(generate_preschool_lyrics, topic)

    meta = dict(project.metadata_json or {})
    curr_pkg = dict(meta.get("content_package") or {})
    curr_pkg["lyrics_full"] = lyrics_data["lyrics_full"]
    curr_pkg["approved_lyrics"] = lyrics_data["lyrics_full"]
    curr_pkg["verses"] = lyrics_data["verses"]

    project.lyrics_text = lyrics_data["lyrics_full"]
    meta["content_package"] = curr_pkg
    meta["approved_lyrics"] = lyrics_data["lyrics_full"]
    project.metadata_json = meta
    await project_repo.update(project)

    return curr_pkg
