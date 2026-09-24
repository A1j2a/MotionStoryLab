from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class AssetBase(BaseModel):
    asset_type: str = Field(..., max_length=64)
    file_path: str = Field(..., max_length=512)
    status: str = Field(default="READY", max_length=32)
    metadata_json: Optional[Dict[str, Any]] = None


class AssetCreate(AssetBase):
    project_id: str


class AssetRead(AssetBase):
    id: str
    project_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
