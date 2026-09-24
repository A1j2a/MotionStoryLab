from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.job import JobStatus


class JobCreate(BaseModel):
    project_id: str
    status: JobStatus = JobStatus.DRAFT
    current_step: str = "INIT"
    progress: int = Field(default=0, ge=0, le=100)


class JobUpdate(BaseModel):
    status: Optional[JobStatus] = None
    current_step: Optional[str] = None
    progress: Optional[int] = Field(default=None, ge=0, le=100)
    error: Optional[str] = None


class JobRead(BaseModel):
    id: str
    project_id: str
    status: JobStatus
    current_step: str
    progress: int
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
