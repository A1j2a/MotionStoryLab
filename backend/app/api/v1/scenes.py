from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.models.scene import Scene
from app.repositories.scene_repo import SceneRepository
from app.repositories.project_repo import ProjectRepository
from app.schemas.scene import SceneRead, SceneUpdate, SceneCreate

router = APIRouter(prefix="/scenes", tags=["scenes"])


@router.get("/project/{project_id}", response_model=List[SceneRead])
async def list_scenes_for_project(
    project_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    project_repo = ProjectRepository(session)
    if not await project_repo.get(project_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found",
        )
    scene_repo = SceneRepository(session)
    return await scene_repo.list_by_project(project_id)


@router.get("/{scene_id}", response_model=SceneRead)
async def get_scene(
    scene_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    scene_repo = SceneRepository(session)
    scene = await scene_repo.get(scene_id)
    if not scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scene '{scene_id}' not found",
        )
    return scene


@router.patch("/{scene_id}", response_model=SceneRead)
async def update_scene(
    scene_id: str,
    payload: SceneUpdate,
    session: AsyncSession = Depends(get_db_session),
):
    scene_repo = SceneRepository(session)
    scene = await scene_repo.get(scene_id)
    if not scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scene '{scene_id}' not found",
        )

    if payload.duration is not None:
        scene.duration = payload.duration
    if payload.environment is not None:
        scene.environment = payload.environment
    if payload.characters is not None:
        scene.characters = payload.characters
    if payload.actions is not None:
        scene.actions = payload.actions
    if payload.camera is not None:
        scene.camera = payload.camera
    if payload.lighting is not None:
        scene.lighting = payload.lighting
    if payload.dialogue is not None:
        scene.dialogue = payload.dialogue
    if payload.lyrics is not None:
        scene.lyrics = payload.lyrics
    if payload.music is not None:
        scene.music = payload.music
    if payload.sound_effects is not None:
        scene.sound_effects = payload.sound_effects
    if payload.transition is not None:
        scene.transition = payload.transition
    if payload.status is not None:
        scene.status = payload.status
    if payload.render_path is not None:
        scene.render_path = payload.render_path
    if payload.error is not None:
        scene.error = payload.error

    return await scene_repo.update(scene)


@router.post("/{scene_id}/regenerate", response_model=SceneRead)
async def regenerate_scene(
    scene_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Resets an individual scene's render state to PENDING to trigger single-scene regeneration
    without affecting already completed sibling scenes.
    """
    scene_repo = SceneRepository(session)
    scene = await scene_repo.reset_scene(scene_id)
    if not scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scene '{scene_id}' not found",
        )
    return scene
