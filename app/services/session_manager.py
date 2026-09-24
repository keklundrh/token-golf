"""
Token Golf - Session Manager Service

Manages session lifecycle, including timeout enforcement.
Sessions expire after a configurable timeout period (default 3 hours).
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Service for managing session lifecycle and timeout enforcement.

    Responsibilities:
        - Check if sessions have expired
        - Mark expired sessions as DNF (Did Not Finish)
        - Retrieve active sessions with timeout validation
        - Bulk mark all expired sessions (background task)

    Business Rules:
        - Sessions expire after timeout_hours (default: 3)
        - Expired sessions are marked with status='dnf'
        - Once marked DNF, no further attempts can be submitted
        - Timeout check uses expires_at timestamp vs current UTC time
    """

    def __init__(self, db_session: AsyncSession):
        """
        Initialize session manager.

        Args:
            db_session: SQLAlchemy async database session
        """
        self.db = db_session

    async def check_session_timeout(self, session_id: str) -> bool:
        """
        Check if a session has expired.

        Args:
            session_id: Session identifier

        Returns:
            True if session has expired, False otherwise

        Raises:
            ValueError: If session not found
        """
        session = await self._get_session_by_id(session_id)

        if not session:
            raise ValueError(f"Session '{session_id}' not found")

        # Use the model's is_expired method
        is_expired = session.is_expired()

        if is_expired:
            logger.info(
                f"Session {session_id} expired at {session.expires_at} "
                f"(current: {datetime.utcnow()})"
            )

        return is_expired

    async def get_active_session(self, session_id: str) -> Session:
        """
        Get a session if it exists and is active.

        Automatically marks session as DNF if expired.

        Args:
            session_id: Session identifier

        Returns:
            Session object if active

        Raises:
            HTTPException: 404 if session not found, 400 if session expired/inactive
        """
        session = await self._get_session_by_id(session_id)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session '{session_id}' not found",
            )

        # Check if expired and mark as DNF
        if session.is_expired() and session.status == "active":
            logger.warning(
                f"Session {session_id} expired - marking as DNF "
                f"(expired at {session.expires_at})"
            )
            session.status = "dnf"
            await self.db.commit()
            await self.db.refresh(session)

        # Check status
        if session.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Session timeout - marked DNF (expired at {session.expires_at.isoformat()})",
            )

        return session

    async def mark_expired_sessions(self) -> int:
        """
        Mark all expired active sessions as DNF.

        This is intended to be run as a background task or cron job.
        Finds all sessions with status='active' and expires_at < now,
        then updates them to status='dnf'.

        Returns:
            Number of sessions marked as DNF

        Raises:
            SQLAlchemyError: If database operation fails
        """
        current_time = datetime.utcnow()

        # Find all active sessions that have expired
        stmt = select(Session).where(
            Session.status == "active",
            Session.expires_at < current_time,
        )

        result = await self.db.execute(stmt)
        expired_sessions = result.scalars().all()

        marked_count = 0
        for session in expired_sessions:
            logger.info(
                f"Marking expired session {session.id} as DNF "
                f"(expired at {session.expires_at})"
            )
            session.status = "dnf"
            marked_count += 1

        if marked_count > 0:
            await self.db.commit()
            logger.info(f"Marked {marked_count} expired sessions as DNF")

        return marked_count

    async def _get_session_by_id(self, session_id: str) -> Optional[Session]:
        """
        Internal helper to get a session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session object if found, None otherwise
        """
        stmt = select(Session).where(Session.id == session_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
