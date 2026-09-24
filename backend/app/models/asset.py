import uuid
from typing import Optional, Dict, Any
from sqlalchemy import String, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class Asset(Base, TimestampMixin):
    __tablename__ = "assets"

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
    asset_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )  # audio, vocals, music, sfx, thumbnail, subtitles, video_shot, final_video
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="READY", nullable=False)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="assets")
