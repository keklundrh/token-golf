"""
Token Golf - Attempt Model

Represents each prompt submission by a user for a challenge.
Stores all tokens, prompts, responses, and user modifications.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.challenge import Challenge
    from app.models.session import Session
    from app.models.user import User


class Attempt(Base):
    """
    Attempt model - each prompt submission for a challenge.

    Storage granularity: per user, per session, per attempt.

    Attempt Types:
    - 'practice': Practice swing - saved for history but doesn't count toward score
    - 'submitted': Recorded attempt - counts toward leaderboard score

    Scoring: Only 'submitted' attempts count. Best (lowest tokens) submitted
    attempt per hole is used for leaderboard ranking.

    User modifications (context files, system prompts) are stored per attempt.
    """

    __tablename__ = "attempts"

    # Primary Key
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="Unique attempt identifier",
    )

    # Foreign Keys
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who made this attempt",
    )

    session_id: Mapped[str] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Session this attempt belongs to",
    )

    challenge_id: Mapped[str] = mapped_column(
        ForeignKey("challenges.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Challenge this attempt is for",
    )

    # Attempt tracking
    attempt_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Attempt number for this user on this challenge (1, 2, 3, ...)",
    )

    attempt_type: Mapped[str] = mapped_column(
        String(20),
        default="practice",
        nullable=False,
        index=True,
        comment="Type of attempt: 'practice' (swing) or 'submitted' (recorded score)",
    )

    # User input
    prompt: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="User's prompt submitted to LLM",
    )

    system_prompt: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="User's system prompt for this attempt (may be modified from default)",
    )

    context_files: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Which context files were active for this attempt (JSON array)",
    )

    # LLM response
    response: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="LLM response text",
    )

    # Token counting (all tokens count)
    input_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Input tokens (includes system prompt tokens)",
    )

    output_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Output tokens",
    )

    total_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Total tokens (input + output)",
    )

    # Validation result
    is_correct: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether this attempt passed validation",
    )

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        comment="When attempt was made",
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="attempts",
    )

    session: Mapped["Session"] = relationship(
        "Session",
        back_populates="attempts",
    )

    challenge: Mapped["Challenge"] = relationship(
        "Challenge",
        back_populates="attempts",
    )

    def __repr__(self) -> str:
        return (
            f"<Attempt(id={self.id}, user_id={self.user_id}, "
            f"challenge_id='{self.challenge_id}', attempt={self.attempt_number}, "
            f"tokens={self.total_tokens}, correct={self.is_correct})>"
        )
