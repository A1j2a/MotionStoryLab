from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.character import Character
from app.repositories.base import SQLAlchemyRepository


class CharacterRepository(SQLAlchemyRepository[Character]):
    def __init__(self, session: AsyncSession):
        super().__init__(Character, session)

    async def list_by_project(self, project_id: str) -> List[Character]:
        stmt = (
            select(Character)
            .where(Character.project_id == project_id)
            .order_by(Character.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def replace_characters_for_project(
        self,
        project_id: str,
        characters: List[Character],
    ) -> List[Character]:
        # Delete existing characters for this project
        await self.session.execute(
            delete(Character).where(Character.project_id == project_id)
        )
        for char in characters:
            char.project_id = project_id
            self.session.add(char)
        await self.session.commit()
        return characters
