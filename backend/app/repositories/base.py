from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Type
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class AbstractRepository(ABC, Generic[ModelType]):
    @abstractmethod
    async def get(self, id: str) -> Optional[ModelType]:
        pass

    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        pass

    @abstractmethod
    async def create(self, entity: ModelType) -> ModelType:
        pass

    @abstractmethod
    async def update(self, entity: ModelType) -> ModelType:
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        pass


class SQLAlchemyRepository(AbstractRepository[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, id: str) -> Optional[ModelType]:
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, entity: ModelType) -> ModelType:
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: ModelType) -> ModelType:
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def delete(self, id: str) -> bool:
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
