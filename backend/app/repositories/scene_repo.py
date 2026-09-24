from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.scene import Scene
from app.repositories.base import SQLAlchemyRepository


class SceneRepository(SQLAlchemyRepository[Scene]):
    def __init__(self, session: AsyncSession):
        super().__init__(Scene, session)

    async def list_by_project(self, project_id: str) -> List[Scene]:
        stmt = (
            select(Scene)
            .where(Scene.project_id == project_id)
            .order_by(Scene.scene_number.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_number(self, project_id: str, scene_number: int) -> Optional[Scene]:
        stmt = select(Scene).where(
            Scene.project_id == project_id,
            Scene.scene_number == scene_number,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_pending_scenes(self, project_id: str) -> List[Scene]:
        stmt = (
            select(Scene)
            .where(
                Scene.project_id == project_id,
                Scene.status.in_(["PENDING", "FAILED"]),
            )
            .order_by(Scene.scene_number.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_scene_render(
        self,
        scene_id: str,
        status: str,
        render_path: Optional[str] = None,
        error: Optional[str] = None,
    ) -> Optional[Scene]:
        scene = await self.get(scene_id)
        if not scene:
            return None
        scene.status = status
        if render_path:
            scene.render_path = render_path
        scene.error = error
        return await self.update(scene)

    async def reset_scene(self, scene_id: str) -> Optional[Scene]:
        scene = await self.get(scene_id)
        if not scene:
            return None
        scene.status = "PENDING"
        scene.render_path = None
        scene.error = None
        return await self.update(scene)

    async def replace_scenes_for_project(
        self,
        project_id: str,
        scenes: List[Scene],
    ) -> List[Scene]:
        await self.session.execute(
            delete(Scene).where(Scene.project_id == project_id)
        )
        for idx, scn in enumerate(scenes, start=1):
            scn.project_id = project_id
            scn.scene_number = idx
            self.session.add(scn)
        await self.session.commit()
        return scenes
