import uuid
from typing import Optional, List, Dict
from sqlalchemy import String, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class Character(Base, TimestampMixin):
    __tablename__ = "characters"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    type: Mapped[str] = mapped_column(String(64), nullable=False)  # animal, human, vehicle, fantasy
    appearance: Mapped[str] = mapped_column(Text, nullable=False)
    colors: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    clothing: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    personality: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    age: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    voice: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    animation_set: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    reference_images: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="characters")
