from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.repositories.asset_repo import AssetRepository
from app.repositories.project_repo import ProjectRepository
from app.schemas.asset import AssetRead, AssetCreate

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("/project/{project_id}", response_model=List[AssetRead])
async def list_assets_for_project(
    project_id: str,
    asset_type: Optional[str] = Query(None, description="Filter by asset type: music, vocals, thumbnail, subtitles, etc."),
    session: AsyncSession = Depends(get_db_session),
):
    project_repo = ProjectRepository(session)
    if not await project_repo.get(project_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found",
        )
    asset_repo = AssetRepository(session)
    return await asset_repo.list_by_project(project_id, asset_type=asset_type)


@router.post("/project/{project_id}", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
async def create_asset(
    project_id: str,
    payload: AssetCreate,
    session: AsyncSession = Depends(get_db_session),
):
    project_repo = ProjectRepository(session)
    if not await project_repo.get(project_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found",
        )
    asset_repo = AssetRepository(session)
    return await asset_repo.record_asset(
        project_id=project_id,
        asset_type=payload.asset_type,
        file_path=payload.file_path,
        status=payload.status,
        metadata=payload.metadata_json,
    )
