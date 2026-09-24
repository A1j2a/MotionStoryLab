from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.models.character import Character
from app.repositories.character_repo import CharacterRepository
from app.repositories.project_repo import ProjectRepository
from app.schemas.character import CharacterRead, CharacterCreate

router = APIRouter(prefix="/characters", tags=["characters"])


@router.get("/project/{project_id}", response_model=List[CharacterRead])
async def get_character_bible(
    project_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    project_repo = ProjectRepository(session)
    if not await project_repo.get(project_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found",
        )
    char_repo = CharacterRepository(session)
    return await char_repo.list_by_project(project_id)


@router.post("/project/{project_id}", response_model=List[CharacterRead], status_code=status.HTTP_201_CREATED)
async def update_character_bible(
    project_id: str,
    characters: List[CharacterCreate],
    session: AsyncSession = Depends(get_db_session),
):
    project_repo = ProjectRepository(session)
    if not await project_repo.get(project_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found",
        )
    char_repo = CharacterRepository(session)
    entities = [
        Character(
            name=c.name,
            type=c.type,
            appearance=c.appearance,
            colors=c.colors,
            clothing=c.clothing,
            personality=c.personality,
            age=c.age,
            voice=c.voice,
            animation_set=c.animation_set,
            reference_images=c.reference_images,
        )
        for c in characters
    ]
    return await char_repo.replace_characters_for_project(project_id, entities)
