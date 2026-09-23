"""
Token Golf - Score Model

Aggregated scores per user, per session, per challenge.
Tracks submitted attempts and best (minimum) token count (ADR 011).
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.challenge import Challenge
    from app.models.session import Session
    from app.models.user import User


class Score(Base):
    """
    Score model - aggregated scoring per user/session/challenge.

    Represents a user's score for one challenge within one session.
    Updated after each submitted attempt (ADR 011):
    - total_attempts: count of submitted attempts
    - total_tokens: best (minimum) tokens from all submitted attempts
    """

    __tablename__ = "scores"

    # Primary Key
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="Unique score record identifier",
    )

    # Foreign Keys
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User this score belongs to",
    )

    session_id: Mapped[str] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Session this score belongs to",
    )

    challenge_id: Mapped[str] = mapped_column(
        ForeignKey("challenges.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Challenge this score is for",
    )

    # Score tracking (ADR 011: only submitted attempts)
    total_attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Count of submitted attempts (practice attempts not included)",
    )

    total_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Best (minimum) tokens from all submitted attempts (ADR 011)",
    )

    # Completion tracking
    completed_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
        comment="When user first submitted a correct attempt for this challenge",
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="scores",
    )

    session: Mapped["Session"] = relationship(
        "Session",
        back_populates="scores",
    )

    challenge: Mapped["Challenge"] = relationship(
        "Challenge",
        back_populates="scores",
    )

    # Constraints (one score record per user/session/challenge combination)
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "session_id",
            "challenge_id",
            name="uq_user_session_challenge",
        ),
    )

    def __repr__(self) -> str:
        status = "completed" if self.completed_at else "in_progress"
        return (
            f"<Score(user_id={self.user_id}, session_id='{self.session_id}', "
            f"challenge_id='{self.challenge_id}', attempts={self.total_attempts}, "
            f"tokens={self.total_tokens}, status={status})>"
        )

    def is_completed(self) -> bool:
        """Check if challenge has been completed"""
        return self.completed_at is not None
