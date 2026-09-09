"""
Token Golf - User Model

Represents players in the game.
Each user gets an auto-generated username (Color-Course-Club format).
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.attempt import Attempt
    from app.models.score import Score
    from app.models.session import SessionParticipant


class User(Base):
    """
    User model - represents a player in Token Golf.

    In MVP, users are anonymous with auto-generated usernames.
    Each time a player starts a session, they get a new username.

    Future: Add authentication to allow reclaiming usernames.
    """

    __tablename__ = "users"

    # Primary Key
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="Unique user identifier",
    )

    # Fields
    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Auto-generated username (Color-Course-Club format)",
    )

    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        comment="When user account was created",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether user account is active",
    )

    # Relationships
    session_participations: Mapped[list["SessionParticipant"]] = relationship(
        "SessionParticipant",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    attempts: Mapped[list["Attempt"]] = relationship(
        "Attempt",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    scores: Mapped[list["Score"]] = relationship(
        "Score",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}')>"
