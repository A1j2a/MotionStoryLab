from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


class ProjectBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    topic: str = Field(..., min_length=1)
    language: str = Field(default="en", max_length=32)
    duration_min: int = Field(default=5, ge=1, le=60)
    duration_max: int = Field(default=7, ge=1, le=60)
    video_type: str = Field(default="Nursery Rhyme", max_length=64)
    visual_style: str = Field(default="3D Cartoon", max_length=64)
    target_age: str = Field(default="Kids", max_length=64)
    character_style: Optional[str] = Field(default=None, max_length=128)
    music_style: Optional[str] = Field(default=None, max_length=128)
    voice_style: Optional[str] = Field(default=None, max_length=128)


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    status: Optional[str] = None
    lyrics_text: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None


class ProjectRead(ProjectBase):
    id: str
    status: str
    lyrics_text: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
