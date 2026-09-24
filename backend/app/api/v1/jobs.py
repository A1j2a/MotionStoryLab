from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.models.job import JobStatus
from app.repositories.job_repo import JobRepository
from app.repositories.project_repo import ProjectRepository
from app.schemas.job import JobRead, JobUpdate

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/project/{project_id}", response_model=List[JobRead])
async def list_jobs_for_project(
    project_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    project_repo = ProjectRepository(session)
    if not await project_repo.get(project_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found",
        )
    job_repo = JobRepository(session)
    return await job_repo.list_by_project(project_id)


@router.get("/{job_id}", response_model=JobRead)
async def get_job(
    job_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    job_repo = JobRepository(session)
    job = await job_repo.get(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found",
        )
    return job


@router.patch("/{job_id}", response_model=JobRead)
async def update_job(
    job_id: str,
    payload: JobUpdate,
    session: AsyncSession = Depends(get_db_session),
):
    job_repo = JobRepository(session)
    job = await job_repo.get(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found",
        )

    if payload.status is not None:
        job.status = payload.status
    if payload.current_step is not None:
        job.current_step = payload.current_step
    if payload.progress is not None:
        job.progress = payload.progress
    if payload.error is not None:
        job.error = payload.error

    return await job_repo.update(job)


@router.post("/{job_id}/retry", response_model=JobRead)
async def retry_job(
    job_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    job_repo = JobRepository(session)
    job = await job_repo.get(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found",
        )

    # Resume from current step, reset error and set status to PLANNING or RENDERING
    job.status = JobStatus.PLANNING if job.progress < 20 else JobStatus.RENDERING
    job.error = None
    return await job_repo.update(job)
