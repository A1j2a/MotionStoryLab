import enum
import uuid
from typing import Optional
from sqlalchemy import String, Integer, Text, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class JobStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    TOPIC_DISCOVERY = "TOPIC_DISCOVERY"
    TOPIC_SELECTED = "TOPIC_SELECTED"
    PLANNING = "PLANNING"
    CONTENT_GENERATING = "CONTENT_GENERATING"
    CONTENT_APPROVED = "CONTENT_APPROVED"
    ASSET_GENERATION = "ASSET_GENERATION"
    SONG_GENERATING = "SONG_GENERATING"
    SONG_READY = "SONG_READY"
    AUDIO_ANALYZING = "AUDIO_ANALYZING"
    AUDIO_GENERATION = "AUDIO_GENERATION"
    STORYBOARD_GENERATING = "STORYBOARD_GENERATING"
    STORYBOARD_READY = "STORYBOARD_READY"
    SCENE_GENERATING = "SCENE_GENERATING"
    SCENE_RENDERING = "SCENE_RENDERING"
    ANIMATION = "ANIMATION"
    RENDERING = "RENDERING"
    ASSEMBLING = "ASSEMBLING"
    COMPOSITING = "COMPOSITING"
    QC = "QC"
    QUALITY_CHECK = "QUALITY_CHECK"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    READY = "READY"
    APPROVED = "APPROVED"
    UPLOADING = "UPLOADING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Job(Base, TimestampMixin):
    __tablename__ = "jobs"

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
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status_enum", native_enum=False),
        default=JobStatus.DRAFT,
        nullable=False,
        index=True,
    )
    current_step: Mapped[str] = mapped_column(String(128), default="INIT", nullable=False)
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="jobs")
