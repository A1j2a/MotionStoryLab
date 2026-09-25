import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Integer, Float, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class Scene(Base, TimestampMixin):
    __tablename__ = "scenes"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scene_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    duration: Mapped[float] = mapped_column(Float, default=5.0, nullable=False)
    environment: Mapped[str] = mapped_column(String(128), nullable=False)

    characters: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    actions: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    camera: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    lighting: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    dialogue: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lyrics: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    video_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    music: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    sound_effects: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    transition: Mapped[Optional[str]] = mapped_column(String(64), default="cut", nullable=True)

    status: Mapped[str] = mapped_column(String(32), default="PENDING", nullable=False)
    render_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Continuity & Video Provider Tracking (Wan FLF2V / Blender)
    start_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    end_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    negative_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_frame: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    end_frame: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    reference_image: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    previous_scene_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    next_scene_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    generation_status: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    generation_attempt: Mapped[Optional[int]] = mapped_column(Integer, default=0, nullable=True)
    provider: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    provider_request_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    video_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    local_video_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Manual External Generation Workflow fields (no-AI-video-gen workflow)
    prompt_status: Mapped[Optional[str]] = mapped_column(String(32), default="NOT_COPIED", nullable=True)  # NOT_COPIED | PROMPT_COPIED | VIDEO_UPLOADED | ORDER_CONFIRMED | FAILED
    prompt_copied_at: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    uploaded_file: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    uploaded_duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    scene_order: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="scenes")
