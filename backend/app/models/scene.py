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
    music: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    sound_effects: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    transition: Mapped[Optional[str]] = mapped_column(String(64), default="cut", nullable=True)

    status: Mapped[str] = mapped_column(String(32), default="PENDING", nullable=False)
    render_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="scenes")
