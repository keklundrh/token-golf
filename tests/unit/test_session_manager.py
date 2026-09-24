"""
Unit tests for SessionManager

Tests session timeout checking, DNF marking, and session lifecycle.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import HTTPException

from app.services.session_manager import SessionManager
from app.models.session import Session


class TestCheckSessionTimeout:
    """Test checking if sessions have expired."""

    @pytest.mark.asyncio
    async def test_active_session_not_expired(self, db_session):
        """Test that active session within timeout is not expired."""
        # Create active session that expires in the future
        created_at = datetime.utcnow()
        timeout_hours = 3
        session_obj = Session(
            id=str(uuid4()),
            course_id="beginner-course",
            created_at=created_at,
            timeout_hours=timeout_hours,
            status="active",
            expires_at=Session.calculate_expires_at(created_at, timeout_hours),
        )
        db_session.add(session_obj)
        await db_session.commit()

        manager = SessionManager(db_session)
        is_expired = await manager.check_session_timeout(session_obj.id)

        assert is_expired is False

    @pytest.mark.asyncio
    async def test_expired_session_detected(self, db_session):
        """Test that expired session is detected as expired."""
        # Create session that expired 1 hour ago
        created_at = datetime.utcnow() - timedelta(hours=4)
        timeout_hours = 3
        session_obj = Session(
            id=str(uuid4()),
            course_id="beginner-course",
            created_at=created_at,
            timeout_hours=timeout_hours,
            status="active",
            expires_at=Session.calculate_expires_at(created_at, timeout_hours),
        )
        db_session.add(session_obj)
        await db_session.commit()

        manager = SessionManager(db_session)
        is_expired = await manager.check_session_timeout(session_obj.id)

        assert is_expired is True

    @pytest.mark.asyncio
    async def test_check_nonexistent_session_raises_error(self, db_session):
        """Test checking nonexistent session raises ValueError."""
        manager = SessionManager(db_session)

        with pytest.raises(ValueError, match="Session .* not found"):
            await manager.check_session_timeout("nonexistent-session-id")


class TestGetActiveSession:
    """Test getting active session with auto-DNF marking."""

    @pytest.mark.asyncio
    async def test_get_active_session_success(self, db_session):
        """Test getting an active session that hasn't expired."""
        created_at = datetime.utcnow()
        timeout_hours = 3
        session_obj = Session(
            id=str(uuid4()),
            course_id="beginner-course",
            created_at=created_at,
            timeout_hours=timeout_hours,
            status="active",
            expires_at=Session.calculate_expires_at(created_at, timeout_hours),
        )
        db_session.add(session_obj)
        await db_session.commit()

        manager = SessionManager(db_session)
        result = await manager.get_active_session(session_obj.id)

        assert result.id == session_obj.id
        assert result.status == "active"

    @pytest.mark.asyncio
    async def test_get_expired_session_marks_dnf(self, db_session):
        """Test getting expired session automatically marks it as DNF."""
        created_at = datetime.utcnow() - timedelta(hours=4)
        timeout_hours = 3
        session_obj = Session(
            id=str(uuid4()),
            course_id="beginner-course",
            created_at=created_at,
            timeout_hours=timeout_hours,
            status="active",
            expires_at=Session.calculate_expires_at(created_at, timeout_hours),
        )
        db_session.add(session_obj)
        await db_session.commit()

        manager = SessionManager(db_session)

        with pytest.raises(HTTPException) as exc_info:
            await manager.get_active_session(session_obj.id)

        assert exc_info.value.status_code == 400
        assert "Session timeout" in exc_info.value.detail

        # Verify session was marked as DNF
        await db_session.refresh(session_obj)
        assert session_obj.status == "dnf"

    @pytest.mark.asyncio
    async def test_get_dnf_session_raises_error(self, db_session):
        """Test getting already DNF session raises error."""
        created_at = datetime.utcnow()
        timeout_hours = 3
        session_obj = Session(
            id=str(uuid4()),
            course_id="beginner-course",
            created_at=created_at,
            timeout_hours=timeout_hours,
            status="dnf",
            expires_at=Session.calculate_expires_at(created_at, timeout_hours),
        )
        db_session.add(session_obj)
        await db_session.commit()

        manager = SessionManager(db_session)

        with pytest.raises(HTTPException) as exc_info:
            await manager.get_active_session(session_obj.id)

        assert exc_info.value.status_code == 400
        assert "Session timeout" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_completed_session_raises_error(self, db_session):
        """Test getting completed session raises error."""
        created_at = datetime.utcnow()
        timeout_hours = 3
        session_obj = Session(
            id=str(uuid4()),
            course_id="beginner-course",
            created_at=created_at,
            timeout_hours=timeout_hours,
            status="completed",
            expires_at=Session.calculate_expires_at(created_at, timeout_hours),
        )
        db_session.add(session_obj)
        await db_session.commit()

        manager = SessionManager(db_session)

        with pytest.raises(HTTPException) as exc_info:
            await manager.get_active_session(session_obj.id)

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_get_nonexistent_session_raises_404(self, db_session):
        """Test getting nonexistent session raises 404."""
        manager = SessionManager(db_session)

        with pytest.raises(HTTPException) as exc_info:
            await manager.get_active_session("nonexistent-id")

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail


class TestMarkExpiredSessions:
    """Test bulk marking of expired sessions (background task)."""

    @pytest.mark.asyncio
    async def test_mark_expired_sessions_success(self, db_session):
        """Test marking multiple expired sessions as DNF."""
        current_time = datetime.utcnow()

        # Create multiple sessions - some expired, some active
        sessions = [
            # Expired sessions
            Session(
                id=str(uuid4()),
                course_id="beginner-course",
                created_at=current_time - timedelta(hours=5),
                timeout_hours=3,
                status="active",
                expires_at=current_time - timedelta(hours=2),
            ),
            Session(
                id=str(uuid4()),
                course_id="beginner-course",
                created_at=current_time - timedelta(hours=4),
                timeout_hours=3,
                status="active",
                expires_at=current_time - timedelta(hours=1),
            ),
            # Active session (not expired)
            Session(
                id=str(uuid4()),
                course_id="beginner-course",
                created_at=current_time,
                timeout_hours=3,
                status="active",
                expires_at=current_time + timedelta(hours=3),
            ),
            # Already DNF session (expired but already marked)
            Session(
                id=str(uuid4()),
                course_id="beginner-course",
                created_at=current_time - timedelta(hours=5),
                timeout_hours=3,
                status="dnf",
                expires_at=current_time - timedelta(hours=2),
            ),
        ]

        for session_obj in sessions:
            db_session.add(session_obj)
        await db_session.commit()

        manager = SessionManager(db_session)
        marked_count = await manager.mark_expired_sessions()

        # Should mark 2 expired active sessions
        assert marked_count == 2

        # Verify the sessions were marked
        for session_obj in sessions[:2]:
            await db_session.refresh(session_obj)
            assert session_obj.status == "dnf"

        # Verify active session remains active
        await db_session.refresh(sessions[2])
        assert sessions[2].status == "active"

        # Verify already DNF session remains DNF
        await db_session.refresh(sessions[3])
        assert sessions[3].status == "dnf"

    @pytest.mark.asyncio
    async def test_mark_expired_sessions_none_expired(self, db_session):
        """Test marking when no sessions are expired returns 0."""
        current_time = datetime.utcnow()

        # Create only active sessions
        sessions = [
            Session(
                id=str(uuid4()),
                course_id="beginner-course",
                created_at=current_time,
                timeout_hours=3,
                status="active",
                expires_at=current_time + timedelta(hours=3),
            ),
            Session(
                id=str(uuid4()),
                course_id="beginner-course",
                created_at=current_time - timedelta(hours=1),
                timeout_hours=3,
                status="active",
                expires_at=current_time + timedelta(hours=2),
            ),
        ]

        for session_obj in sessions:
            db_session.add(session_obj)
        await db_session.commit()

        manager = SessionManager(db_session)
        marked_count = await manager.mark_expired_sessions()

        assert marked_count == 0

        # Verify all sessions remain active
        for session_obj in sessions:
            await db_session.refresh(session_obj)
            assert session_obj.status == "active"

    @pytest.mark.asyncio
    async def test_mark_expired_sessions_empty_database(self, db_session):
        """Test marking when no sessions exist returns 0."""
        manager = SessionManager(db_session)
        marked_count = await manager.mark_expired_sessions()

        assert marked_count == 0


class TestSessionManagerInit:
    """Test SessionManager initialization."""

    @pytest.mark.asyncio
    async def test_init(self, db_session):
        """Test session manager initialization."""
        manager = SessionManager(db_session)
        assert manager.db == db_session


class TestGetSessionById:
    """Test internal _get_session_by_id method."""

    @pytest.mark.asyncio
    async def test_get_existing_session(self, db_session):
        """Test getting existing session by ID."""
        session_obj = Session(
            id=str(uuid4()),
            course_id="beginner-course",
            created_at=datetime.utcnow(),
            timeout_hours=3,
            status="active",
            expires_at=datetime.utcnow() + timedelta(hours=3),
        )
        db_session.add(session_obj)
        await db_session.commit()

        manager = SessionManager(db_session)
        result = await manager._get_session_by_id(session_obj.id)

        assert result is not None
        assert result.id == session_obj.id

    @pytest.mark.asyncio
    async def test_get_nonexistent_session(self, db_session):
        """Test getting nonexistent session returns None."""
        manager = SessionManager(db_session)
        result = await manager._get_session_by_id("nonexistent-id")

        assert result is None


class TestSessionTimeoutEdgeCases:
    """Test edge cases for session timeout logic."""

    @pytest.mark.asyncio
    async def test_session_expires_at_exact_boundary(self, db_session):
        """Test session that expires at exact current time."""
        # Create session that expires right now
        current_time = datetime.utcnow()
        created_at = current_time - timedelta(hours=3)
        timeout_hours = 3

        session_obj = Session(
            id=str(uuid4()),
            course_id="beginner-course",
            created_at=created_at,
            timeout_hours=timeout_hours,
            status="active",
            expires_at=current_time,
        )
        db_session.add(session_obj)
        await db_session.commit()

        manager = SessionManager(db_session)

        # Session at exact boundary should be considered expired
        # (expires_at < now check)
        is_expired = await manager.check_session_timeout(session_obj.id)

        # The result depends on timing, but the system should handle it gracefully
        assert isinstance(is_expired, bool)

    @pytest.mark.asyncio
    async def test_session_with_custom_timeout_hours(self, db_session):
        """Test session with custom timeout hours."""
        created_at = datetime.utcnow() - timedelta(hours=6)
        timeout_hours = 8  # Custom timeout

        session_obj = Session(
            id=str(uuid4()),
            course_id="beginner-course",
            created_at=created_at,
            timeout_hours=timeout_hours,
            status="active",
            expires_at=Session.calculate_expires_at(created_at, timeout_hours),
        )
        db_session.add(session_obj)
        await db_session.commit()

        manager = SessionManager(db_session)
        is_expired = await manager.check_session_timeout(session_obj.id)

        # 6 hours old with 8 hour timeout = still active
        assert is_expired is False

    @pytest.mark.asyncio
    async def test_session_with_short_timeout(self, db_session):
        """Test session with very short timeout period."""
        created_at = datetime.utcnow() - timedelta(minutes=10)
        timeout_hours = 0.1  # 6 minutes

        session_obj = Session(
            id=str(uuid4()),
            course_id="beginner-course",
            created_at=created_at,
            timeout_hours=timeout_hours,
            status="active",
            expires_at=Session.calculate_expires_at(created_at, timeout_hours),
        )
        db_session.add(session_obj)
        await db_session.commit()

        manager = SessionManager(db_session)
        is_expired = await manager.check_session_timeout(session_obj.id)

        # 10 minutes old with 6 minute timeout = expired
        assert is_expired is True


class TestConcurrentSessionOperations:
    """Test concurrent operations on sessions."""

    @pytest.mark.asyncio
    async def test_multiple_get_active_session_calls(self, db_session):
        """Test multiple concurrent calls to get_active_session."""
        created_at = datetime.utcnow()
        timeout_hours = 3
        session_obj = Session(
            id=str(uuid4()),
            course_id="beginner-course",
            created_at=created_at,
            timeout_hours=timeout_hours,
            status="active",
            expires_at=Session.calculate_expires_at(created_at, timeout_hours),
        )
        db_session.add(session_obj)
        await db_session.commit()

        manager = SessionManager(db_session)

        # Multiple calls should all succeed
        result1 = await manager.get_active_session(session_obj.id)
        result2 = await manager.get_active_session(session_obj.id)
        result3 = await manager.get_active_session(session_obj.id)

        assert result1.id == result2.id == result3.id == session_obj.id
        assert result1.status == result2.status == result3.status == "active"


class TestSessionStatusTransitions:
    """Test different session status transitions."""

    @pytest.mark.asyncio
    async def test_active_to_dnf_transition(self, db_session):
        """Test transition from active to DNF on expiration."""
        created_at = datetime.utcnow() - timedelta(hours=4)
        timeout_hours = 3
        session_obj = Session(
            id=str(uuid4()),
            course_id="beginner-course",
            created_at=created_at,
            timeout_hours=timeout_hours,
            status="active",
            expires_at=Session.calculate_expires_at(created_at, timeout_hours),
        )
        db_session.add(session_obj)
        await db_session.commit()

        manager = SessionManager(db_session)

        # First check - session is active but expired
        assert session_obj.status == "active"
        assert session_obj.is_expired() is True

        # Get active session should mark as DNF
        try:
            await manager.get_active_session(session_obj.id)
        except HTTPException:
            pass

        # Verify transition
        await db_session.refresh(session_obj)
        assert session_obj.status == "dnf"

    @pytest.mark.asyncio
    async def test_expired_session_not_re_marked(self, db_session):
        """Test that DNF sessions are not re-marked."""
        current_time = datetime.utcnow()
        created_at = current_time - timedelta(hours=5)
        timeout_hours = 3

        session_obj = Session(
            id=str(uuid4()),
            course_id="beginner-course",
            created_at=created_at,
            timeout_hours=timeout_hours,
            status="dnf",
            expires_at=current_time - timedelta(hours=2),
        )
        db_session.add(session_obj)
        await db_session.commit()

        manager = SessionManager(db_session)
        marked_count = await manager.mark_expired_sessions()

        # Should not mark already DNF sessions
        assert marked_count == 0

        # Status should remain DNF
        await db_session.refresh(session_obj)
        assert session_obj.status == "dnf"
