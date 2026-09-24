import sys
from pathlib import Path
from typing import List, Dict, Any
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
    content_angle: str
    why_worth_considering: str
    opportunity_signals: str
    suggested_characters: List[str] = []
    suggested_story_concept: str = ""


@router.get("/discover", response_model=List[Dict[str, Any]])
async def get_discovered_topics(
    limit: int = Query(8, ge=3, le=20, description="Number of topic opportunities to generate"),
):
    """
    Step 1: '🔥 Find Today's Kids Topics'
    Researches current kids topic opportunities exclusively from Live AI.
    """
    import asyncio
    try:
        return await asyncio.to_thread(discover_kids_topics, limit)
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

    project = Project(
        title=payload.title,
        topic=payload.topic,
        target_age=payload.target_age,
        video_type="Nursery Rhyme",
        visual_style="3D Cartoon",
        status="PROCESSING",
        metadata_json={
            "topic_info": payload.model_dump(),
        },
    )
    created = await project_repo.create(project)

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
