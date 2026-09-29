from typing import Optional, List
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.project import Project
from app.repositories.base import SQLAlchemyRepository


class ProjectRepository(SQLAlchemyRepository[Project]):
    def __init__(self, session: AsyncSession):
        super().__init__(Project, session)

    async def get_with_details(self, project_id: str) -> Optional[Project]:
        stmt = (
            select(Project)
            .where(Project.id == project_id)
            .options(
                selectinload(Project.jobs),
                selectinload(Project.characters),
                selectinload(Project.scenes),
                selectinload(Project.assets),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_topic_or_title(self, topic: str, title: Optional[str] = None) -> Optional[Project]:
        clean_topic = (topic or "").strip().lower()
        clean_title = (title or "").strip().lower()
        if not clean_topic and not clean_title:
            return None

        conditions = []
        if clean_topic:
            conditions.append(func.lower(Project.topic) == clean_topic)
            conditions.append(func.lower(Project.title) == clean_topic)
        if clean_title:
            conditions.append(func.lower(Project.title) == clean_title)
            conditions.append(func.lower(Project.topic) == clean_title)

        stmt = (
            select(Project)
            .where(or_(*conditions))
            .options(
                selectinload(Project.jobs),
                selectinload(Project.characters),
                selectinload(Project.scenes),
                selectinload(Project.assets),
            )
            .order_by(Project.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_by_status(
        self,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Project]:
        stmt = select(Project).order_by(Project.created_at.desc())
        if status:
            stmt = stmt.where(Project.status == status)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_status(self, project_id: str, status: str) -> Optional[Project]:
        project = await self.get(project_id)
        if not project:
            return None
        project.status = status
        return await self.update(project)
