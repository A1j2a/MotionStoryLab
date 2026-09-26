from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class SceneBase(BaseModel):
    scene_number: int = Field(..., ge=1)
    duration: float = Field(default=5.0, ge=0.5, le=60.0)
    environment: str = Field(..., min_length=1, max_length=128)
    characters: List[str] = Field(default_factory=list)
    actions: List[str] = Field(default_factory=list)
    camera: Optional[Dict[str, Any]] = None
    lighting: Optional[Dict[str, Any]] = None
    dialogue: Optional[str] = None
    lyrics: Optional[str] = None
    video_prompt: Optional[str] = None
    music: Optional[str] = None
    sound_effects: List[str] = Field(default_factory=list)
    transition: Optional[str] = "cut"


class SceneCreate(SceneBase):
    project_id: str


class SceneUpdate(BaseModel):
    duration: Optional[float] = None
    environment: Optional[str] = None
    characters: Optional[List[str]] = None
    actions: Optional[List[str]] = None
    camera: Optional[Dict[str, Any]] = None
    lighting: Optional[Dict[str, Any]] = None
    dialogue: Optional[str] = None
    lyrics: Optional[str] = None
    video_prompt: Optional[str] = None
    music: Optional[str] = None
    sound_effects: Optional[List[str]] = None
    transition: Optional[str] = None
    status: Optional[str] = None
    render_path: Optional[str] = None
    error: Optional[str] = None
    prompt_status: Optional[str] = None
    prompt_copied_at: Optional[str] = None
    uploaded_file: Optional[str] = None
    uploaded_duration: Optional[float] = None
    scene_order: Optional[int] = None
    video_url: Optional[str] = None
    local_video_path: Optional[str] = None


class SceneRead(SceneBase):
    id: str
    project_id: str
    status: str
    render_path: Optional[str] = None
    error: Optional[str] = None
    prompt_status: Optional[str] = None
    prompt_copied_at: Optional[str] = None
    uploaded_file: Optional[str] = None
    uploaded_duration: Optional[float] = None
    scene_order: Optional[int] = None
    video_url: Optional[str] = None
    local_video_path: Optional[str] = None
    start_frame: Optional[str] = None
    end_frame: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
