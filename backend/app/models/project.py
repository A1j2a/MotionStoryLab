import uuid
from typing import List, Optional
from sqlalchemy import String, Integer, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    topic: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(32), default="en", nullable=False)
    duration_min: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    duration_max: Mapped[int] = mapped_column(Integer, default=7, nullable=False)
    video_type: Mapped[str] = mapped_column(String(64), default="Nursery Rhyme", nullable=False)
    visual_style: Mapped[str] = mapped_column(String(64), default="3D Cartoon", nullable=False)
    target_age: Mapped[str] = mapped_column(String(64), default="Kids", nullable=False)

    character_style: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    music_style: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    voice_style: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    status: Mapped[str] = mapped_column(String(64), default="DRAFT", nullable=False)
    lyrics_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationships
    jobs: Mapped[List["Job"]] = relationship(
        "Job",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="Job.created_at.desc()",
    )
    characters: Mapped[List["Character"]] = relationship(
        "Character",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    scenes: Mapped[List["Scene"]] = relationship(
        "Scene",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="Scene.scene_number.asc()",
    )
    assets: Mapped[List["Asset"]] = relationship(
        "Asset",
        back_populates="project",
        cascade="all, delete-orphan",
    )
