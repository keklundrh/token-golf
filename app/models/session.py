"""
Token Golf - Session Models

Session: A game on a specific course (collection of holes)
SessionParticipant: Join table linking users to sessions
"""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.attempt import Attempt
    from app.models.score import Score
    from app.models.user import User


class Session(Base):
    """
    Session model - represents one game on a specific course.

    A session is a competition where multiple players compete on the same
    course (collection of holes). Sessions timeout after a configurable
    number of hours (default: 3).
    """

    __tablename__ = "sessions"

    # Indexes for efficient timeout queries
    __table_args__ = (
        Index("ix_sessions_status_expires", "status", "expires_at"),
    )

    # Primary Key (using string UUID)
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        comment="Session UUID",
    )

    # Fields
    course_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Which course this session uses (e.g., 'beginner-course')",
    )

    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        comment="When session was created",
    )

    timeout_hours: Mapped[int] = mapped_column(
        Integer,
        default=3,
        nullable=False,
        comment="Session timeout in hours",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        nullable=False,
        comment="Session status: 'active', 'completed', 'dnf'",
    )

    expires_at: Mapped[datetime] = mapped_column(
        nullable=False,
        comment="When session expires (created_at + timeout_hours)",
    )

    course_total_holes: Mapped[int] = mapped_column(
        Integer,
        default=5,
        nullable=False,
        comment="Total number of holes in this course (denormalized from courses.yaml)",
    )

    # Relationships
    participants: Mapped[list["SessionParticipant"]] = relationship(
        "SessionParticipant",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    attempts: Mapped[list["Attempt"]] = relationship(
        "Attempt",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    scores: Mapped[list["Score"]] = relationship(
        "Score",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Session(id='{self.id}', course='{self.course_id}', status='{self.status}')>"

    def is_expired(self) -> bool:
        """Check if session has expired"""
        return datetime.utcnow() > self.expires_at

    def is_active(self) -> bool:
        """Check if session is active and not expired"""
        return self.status == "active" and not self.is_expired()

    @classmethod
    def calculate_expires_at(cls, created_at: datetime, timeout_hours: int) -> datetime:
        """Calculate expiration timestamp"""
        return created_at + timedelta(hours=timeout_hours)


class SessionParticipant(Base):
    """
    SessionParticipant model - join table for users and sessions.

    Tracks which users are participating in which sessions.
    A user can participate in multiple concurrent sessions.
    """

    __tablename__ = "session_participants"

    # Primary Key
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="Unique participant record identifier",
    )

    # Foreign Keys
    session_id: Mapped[str] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Session this participation belongs to",
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User participating in session",
    )

    # Fields
    joined_at: Mapped[datetime] = mapped_column(
        nullable=False,
        comment="When user joined this session",
    )

    holes_completed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of challenges completed by this user in this session",
    )

    course_completed_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
        comment="Timestamp when user completed all holes in the course (NULL if incomplete)",
    )

    # Relationships
    session: Mapped["Session"] = relationship(
        "Session",
        back_populates="participants",
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="session_participations",
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint("session_id", "user_id", name="uq_session_user"),
    )

    def __repr__(self) -> str:
        return f"<SessionParticipant(session_id='{self.session_id}', user_id={self.user_id})>"
