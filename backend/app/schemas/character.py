from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class CharacterBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    type: str = Field(..., max_length=64)
    appearance: str = Field(...)
    colors: Optional[List[str]] = None
    clothing: Optional[str] = None
    personality: Optional[str] = None
    age: Optional[str] = None
    voice: Optional[str] = None
    animation_set: Optional[List[str]] = None
    reference_images: Optional[List[str]] = None


class CharacterCreate(CharacterBase):
    id: Optional[str] = None
    project_id: Optional[str] = None


class CharacterRead(CharacterBase):
    id: str
    project_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
