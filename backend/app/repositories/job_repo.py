from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.job import Job, JobStatus
from app.repositories.base import SQLAlchemyRepository


class JobRepository(SQLAlchemyRepository[Job]):
    def __init__(self, session: AsyncSession):
        super().__init__(Job, session)

    async def list_by_project(self, project_id: str) -> List[Job]:
        stmt = (
            select(Job)
            .where(Job.project_id == project_id)
            .order_by(Job.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_active_job_for_project(self, project_id: str) -> Optional[Job]:
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
        stmt = (
            select(Job)
            .where(Job.project_id == project_id, Job.status.in_(active_statuses))
            .order_by(Job.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_progress(
        self,
        job_id: str,
        status: JobStatus,
        current_step: str,
        progress: int,
        error: Optional[str] = None,
    ) -> Optional[Job]:
        job = await self.get(job_id)
        if not job:
            return None
        job.status = status
        job.current_step = current_step
        job.progress = max(0, min(100, progress))
        job.error = error
        return await self.update(job)
