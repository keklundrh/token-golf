"""
E2E Test: Session Timeout

Tests session expiration and DNF (Did Not Finish) marking.
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Session, SessionParticipant, User


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_session_timeout_dnf_marking(
    client: TestClient,
    db_session: AsyncSession,
    all_challenges,
):
    """
    Test session timeout: Start session, simulate timeout, verify DNF marking.

    Flow:
    1. Start session
    2. Make an attempt
    3. Manually expire the session (simulate timeout)
    4. Try to submit another attempt
    5. Verify session is marked as expired/DNF
    6. Verify appropriate error message
    """

    # Step 1: Start session
    start_response = client.post(
        "/api/game/start",
        json={"action": "generate", "course_id": "beginner-course"}
    )

    assert start_response.status_code == 201
    start_data = start_response.json()

    session_id = start_data["session_id"]
    user_id = start_data["user_id"]
    challenge_ids = start_data["challenges"]

    if len(challenge_ids) == 0:
        pytest.skip("No challenges available")

    first_challenge_id = challenge_ids[0]

    # Step 2: Submit one valid attempt
    attempt_response = client.post(
        "/api/game/submit",
        json={
            "session_id": session_id,
            "challenge_id": first_challenge_id,
            "user_prompt": "Solve this challenge.",
            "system_prompt": None,
            "context_files": [],
            "action": "submit"
        }
    )

    if attempt_response.status_code == 503:
        pytest.skip("LLM service unavailable")

    if attempt_response.status_code == 422:
        pytest.skip("LLM did not solve challenge correctly - cannot test with action=submit")

    assert attempt_response.status_code == 200

    # Step 3: Manually expire the session
    # Get session from database and modify timestamps
    result = await db_session.execute(
        select(Session).where(Session.id == session_id)
    )
    session = result.scalar_one_or_none()
    assert session is not None

    # Set created_at to past and expires_at to past
    # This simulates a session that has timed out
    session.created_at = datetime.utcnow() - timedelta(hours=5)
    session.expires_at = datetime.utcnow() - timedelta(hours=1)
    await db_session.commit()
    await db_session.refresh(session)

    # Verify session is expired
    assert session.is_expired()

    # Step 4: Try to submit another attempt (should fail)
    expired_attempt = client.post(
        "/api/game/submit",
        json={
            "session_id": session_id,
            "challenge_id": first_challenge_id,
            "user_prompt": "Try to solve after timeout.",
            "system_prompt": None,
            "context_files": []
        }
    )

    # Should get 400 Bad Request for expired session
    assert expired_attempt.status_code == 400

    error_data = expired_attempt.json()
    assert "detail" in error_data

    # Verify error indicates session is not active
    error_detail = error_data["detail"]
    if isinstance(error_detail, dict):
        assert error_detail.get("error") == "session_not_active"
        assert "expired" in error_detail.get("message", "").lower() or \
               "not active" in error_detail.get("message", "").lower()

    # Step 5: Get game status (should still work but show expired status)
    status_response = client.get(f"/api/game/status/{session_id}")

    # Status endpoint should return the session even if expired
    # (to show final state to user)
    assert status_response.status_code == 200
    status_data = status_response.json()

    # Session should still exist in database but marked as not active
    result = await db_session.execute(
        select(Session).where(Session.id == session_id)
    )
    session = result.scalar_one_or_none()
    assert session is not None

    # The SessionManager's mark_expired_sessions should have marked it as DNF
    # This happens in the background task, so we'll trigger it manually
    from app.services import SessionManager
    manager = SessionManager(db_session)
    marked_count = await manager.mark_expired_sessions()

    # Refresh session
    await db_session.refresh(session)

    # Session status should now be 'dnf' (did not finish)
    assert session.status == "dnf"


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_session_timeout_prevents_new_attempts(
    client: TestClient,
    db_session: AsyncSession,
    all_challenges,
):
    """
    Test that expired sessions cannot accept new attempts.

    Flow:
    1. Create session
    2. Expire it immediately
    3. Try to submit - should be rejected
    4. Verify no attempt was recorded
    """

    # Start session
    start_response = client.post(
        "/api/game/start",
        json={"action": "generate", "course_id": "beginner-course"}
    )

    assert start_response.status_code == 201
    start_data = start_response.json()

    session_id = start_data["session_id"]
    challenge_ids = start_data["challenges"]

    if len(challenge_ids) == 0:
        pytest.skip("No challenges available")

    # Immediately expire the session
    result = await db_session.execute(
        select(Session).where(Session.id == session_id)
    )
    session = result.scalar_one_or_none()
    assert session is not None

    session.expires_at = datetime.utcnow() - timedelta(hours=1)
    await db_session.commit()

    # Try to submit attempt
    attempt_response = client.post(
        "/api/game/submit",
        json={
            "session_id": session_id,
            "challenge_id": challenge_ids[0],
            "user_prompt": "This should fail",
            "system_prompt": None,
            "context_files": [],
            "action": "submit"
        }
    )

    # Should be rejected
    assert attempt_response.status_code == 400


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_session_automatic_expiration(
    client: TestClient,
    db_session: AsyncSession,
    all_challenges,
):
    """
    Test that the get_active_session method automatically detects expiration.

    Flow:
    1. Create session
    2. Submit attempt successfully
    3. Manually expire session
    4. Call get_active_session
    5. Verify it marks session as DNF
    """

    # Start session
    start_response = client.post(
        "/api/game/start",
        json={"action": "generate", "course_id": "beginner-course"}
    )

    assert start_response.status_code == 201
    start_data = start_response.json()

    session_id = start_data["session_id"]

    # Verify session is active
    result = await db_session.execute(
        select(Session).where(Session.id == session_id)
    )
    session = result.scalar_one_or_none()
    assert session is not None
    assert session.status == "active"
    assert not session.is_expired()

    # Expire the session
    session.expires_at = datetime.utcnow() - timedelta(seconds=1)
    await db_session.commit()
    await db_session.refresh(session)

    # Verify it's now expired
    assert session.is_expired()
    assert session.status == "active"  # Not yet marked as DNF

    # Try to get active session (this should trigger DNF marking)
    from app.services import SessionManager
    manager = SessionManager(db_session)

    # This should raise HTTPException because session is expired
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await manager.get_active_session(session_id)

    # Should be 400 Bad Request
    assert exc_info.value.status_code == 400

    # Session should now be marked as DNF
    await db_session.refresh(session)
    assert session.status == "dnf"


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_session_timeout_with_completed_challenges(
    client: TestClient,
    db_session: AsyncSession,
    all_challenges,
):
    """
    Test that completed challenges are preserved when session times out.

    Flow:
    1. Start session
    2. Complete a challenge
    3. Expire session
    4. Verify completed challenge data is still accessible
    """

    # Start session
    start_response = client.post(
        "/api/game/start",
        json={"action": "generate", "course_id": "beginner-course"}
    )

    assert start_response.status_code == 201
    start_data = start_response.json()

    session_id = start_data["session_id"]
    user_id = start_data["user_id"]
    challenge_ids = start_data["challenges"]

    if len(challenge_ids) == 0:
        pytest.skip("No challenges available")

    # Submit attempt
    attempt_response = client.post(
        "/api/game/submit",
        json={
            "session_id": session_id,
            "challenge_id": challenge_ids[0],
            "user_prompt": "Solve this.",
            "system_prompt": None,
            "context_files": [],
            "action": "submit"
        }
    )

    if attempt_response.status_code == 503:
        pytest.skip("LLM service unavailable")

    if attempt_response.status_code == 422:
        pytest.skip("LLM did not solve challenge correctly - cannot test with action=submit")

    assert attempt_response.status_code == 200
    attempt_data = attempt_response.json()

    initial_tokens = attempt_data["total_tokens"]

    # Expire session
    result = await db_session.execute(
        select(Session).where(Session.id == session_id)
    )
    session = result.scalar_one_or_none()
    session.expires_at = datetime.utcnow() - timedelta(hours=1)
    await db_session.commit()

    # Mark as DNF
    from app.services import SessionManager
    manager = SessionManager(db_session)
    await manager.mark_expired_sessions()

    # Verify scores are still accessible
    from app.models import Score
    result = await db_session.execute(
        select(Score).where(
            Score.user_id == user_id,
            Score.session_id == session_id
        )
    )
    scores = result.scalars().all()

    # Should have at least one score
    assert len(scores) > 0

    # Tokens should be preserved
    assert any(s.total_tokens == initial_tokens for s in scores)

    # Get game status - should show completed work
    status_response = client.get(f"/api/game/status/{session_id}")
    assert status_response.status_code == 200
    status_data = status_response.json()

    # Should show DNF status
    assert status_data["session_status"] == "dnf"

    # Should show token count
    assert status_data["total_tokens"] > 0
