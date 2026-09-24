from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.asset import Asset
from app.repositories.base import SQLAlchemyRepository


class AssetRepository(SQLAlchemyRepository[Asset]):
    def __init__(self, session: AsyncSession):
        super().__init__(Asset, session)

    async def list_by_project(
        self,
        project_id: str,
        asset_type: Optional[str] = None,
    ) -> List[Asset]:
        stmt = (
            select(Asset)
            .where(Asset.project_id == project_id)
            .order_by(Asset.created_at.desc())
        )
        if asset_type:
            stmt = stmt.where(Asset.asset_type == asset_type)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def record_asset(
        self,
        project_id: str,
        asset_type: str,
        file_path: str,
        status: str = "READY",
        metadata: Optional[dict] = None,
    ) -> Asset:
        asset = Asset(
            project_id=project_id,
            asset_type=asset_type,
            file_path=file_path,
            status=status,
            metadata_json=metadata,
        )
        return await self.create(asset)
