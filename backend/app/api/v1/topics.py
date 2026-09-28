import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.api.deps import get_db_session
from app.models.project import Project
from app.models.job import Job, JobStatus
from app.repositories.project_repo import ProjectRepository
from app.repositories.job_repo import JobRepository
from app.schemas.project import ProjectRead
from ai.topic_researcher import discover_kids_topics

router = APIRouter(prefix="/topics", tags=["topics"])


class TopicSelectPayload(BaseModel):
    topic: str
    title: str
    category: str
    target_age: str
    duration: Optional[str] = "2-3 Minutes"
    duration_min: Optional[int] = None
    duration_max: Optional[int] = None
    content_angle: str
    why_worth_considering: str
    opportunity_signals: str
    suggested_characters: List[str] = []
    suggested_story_concept: str = ""


@router.get("/discover", response_model=List[Dict[str, Any]])
async def get_discovered_topics(
    limit: int = Query(8, ge=2, le=20, description="Number of topic opportunities to generate"),
    target_age: Optional[str] = Query(None, description="Preschool age group filter"),
    duration: Optional[str] = Query(None, description="Duration filter"),
    language: Optional[str] = Query(None, description="Language / market filter"),
    seed: Optional[int] = Query(None, description="Random seed for fresh dynamic variations"),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Step 1: ' Find Today's Kids Topics'
    Researches current kids topic opportunities exclusively from Live AI with custom filters.
    Strictly filters out and excludes any topics that already have projects/videos in the database,
    and guarantees zero duplicate or repeat topics across discoveries.
    """
    import asyncio
    from sqlalchemy import select

    try:
        stmt = select(Project)
        res = await session.execute(stmt)
        projects = res.scalars().all()
        excluded: List[str] = []
        for p in projects:
            if p.topic:
                excluded.append(p.topic)
            if p.title:
                excluded.append(p.title)
            if p.metadata_json and isinstance(p.metadata_json, dict):
                tinfo = p.metadata_json.get("topic_info")
                if isinstance(tinfo, dict):
                    if tinfo.get("topic"):
                        excluded.append(tinfo.get("topic"))
                    if tinfo.get("suggested_title"):
                        excluded.append(tinfo.get("suggested_title"))

        return await asyncio.to_thread(
            discover_kids_topics,
            limit=limit,
            target_age=target_age,
            duration=duration,
            language=language,
            seed=seed,
            excluded_topics=excluded,
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=str(e),
        )


@router.post("/select", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def select_topic_and_create_project(
    payload: TopicSelectPayload,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Step 1 -> Step 2: Creates project from selected topic card and initializes TOPIC_SELECTED state.
    """
    project_repo = ProjectRepository(session)
    job_repo = JobRepository(session)

    d_min = payload.duration_min or 2
    d_max = payload.duration_max or 3
    if payload.duration:
        dur_str = str(payload.duration).lower()
        if "1" in dur_str and "2" in dur_str:
            d_min, d_max = 1, 2
        elif "2" in dur_str and "3" in dur_str:
            d_min, d_max = 2, 3
        elif "3" in dur_str and "5" in dur_str:
            d_min, d_max = 3, 5
        elif "short" in dur_str or "<60" in dur_str:
            d_min, d_max = 1, 1

    project = Project(
        title=payload.title,
        topic=payload.topic,
        target_age=payload.target_age,
        duration_min=d_min,
        duration_max=d_max,
        video_type="Nursery Rhyme",
        visual_style="3D Cartoon",
        status="PROCESSING",
        metadata_json={
            "topic_info": payload.model_dump(),
            "target_duration": payload.duration or f"{d_min}-{d_max} Minutes",
        },
    )
    created = await project_repo.create(project)

    # Permanently store selected topic in consumed/used storage to guarantee zero repeats
    from ai.topic_researcher import mark_topic_as_used
    mark_topic_as_used(
        title=payload.title,
        topic=payload.topic,
        category=payload.category,
    )

    # Initialize Job in TOPIC_SELECTED
    await job_repo.create(
        Job(
            project_id=created.id,
            status=JobStatus.TOPIC_SELECTED,
            current_step="TOPIC_SELECTED",
            progress=10,
        )
    )

    return created


@router.get("/ai-usage", response_model=List[Dict[str, Any]])
async def get_ai_usage_stats():
    """Returns AI provider usage stats — call count per model."""
    from ai.providers import get_ai_usage_stats
    return get_ai_usage_stats()
