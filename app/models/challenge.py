"""
Token Golf - Challenge Model

Represents individual challenges (holes) loaded from YAML files.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.attempt import Attempt
    from app.models.score import Score


class Challenge(Base):
    """
    Challenge model - represents a single hole/challenge.

    Challenges are loaded from YAML files in the challenges/ directory.
    The full YAML content is stored in config_yaml for reference.
    """

    __tablename__ = "challenges"

    # Primary Key (using challenge ID from YAML, e.g., "hole-001")
    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        comment="Challenge identifier (e.g., 'hole-001')",
    )

    # Fields
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Display name of the challenge",
    )

    difficulty: Mapped[str] = mapped_column(
        String(20),
        nullable=True,
        index=True,
        comment="Difficulty level: 'easy', 'medium', 'hard', 'expert'",
    )

    task_type: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        comment="Type of task: 'coding', 'extraction', 'question_answering', 'generation'",
    )

    config_yaml: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Full YAML configuration for this challenge",
    )

    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        comment="When challenge was loaded into database",
    )

    # Relationships
    attempts: Mapped[list["Attempt"]] = relationship(
        "Attempt",
        back_populates="challenge",
        cascade="all, delete-orphan",
    )

    scores: Mapped[list["Score"]] = relationship(
        "Score",
        back_populates="challenge",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Challenge(id='{self.id}', name='{self.name}', difficulty='{self.difficulty}')>"
