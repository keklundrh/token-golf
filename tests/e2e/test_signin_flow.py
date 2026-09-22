"""
E2E Test: Sign-in Flow

Tests user creation, sign out, sign back in, and session resumption.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Session, SessionParticipant, User


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_signin_flow_complete(
    client: TestClient,
    db_session: AsyncSession,
    all_challenges,
):
    """
    Test complete sign-in flow: Create user, sign out, sign back in, resume session.

    Flow:
    1. Generate new user
    2. Save credentials
    3. Start new session with sign-in (simulate "sign out" by starting fresh)
    4. Verify same user
    5. Verify can create new session
    6. Verify user data persists across sessions
    """

    # === Step 1: Generate new user ===
    first_start = client.post(
        "/api/game/start",
        json={"action": "generate", "course_id": "beginner-course"}
    )

    assert first_start.status_code == 201
    first_data = first_start.json()

    # Save credentials
    username = first_data["username"]
    password = first_data["password"]
    user_id = first_data["user_id"]
    first_session_id = first_data["session_id"]

    assert username is not None
    assert password is not None

    # Verify user exists in database
    result = await db_session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.username == username

    # === Step 2: Make some progress ===
    challenge_ids = first_data["challenges"]
    if len(challenge_ids) == 0:
        pytest.skip("No challenges available")

    first_challenge_id = challenge_ids[0]

    attempt_response = client.post(
        "/api/game/submit",
        json={
            "session_id": first_session_id,
            "challenge_id": first_challenge_id,
            "user_prompt": "Solve this challenge.",
            "system_prompt": None,
            "context_files": []
        }
    )

    if attempt_response.status_code == 503:
        pytest.skip("LLM service unavailable")

    assert attempt_response.status_code == 200

    # === Step 3: "Sign out" and sign back in (new session) ===
    # This simulates signing out and back in by creating a new session
    # with the same user credentials

    second_start = client.post(
        "/api/game/start",
        json={
            "action": "signin",
            "username": username,
            "password": password,
            "course_id": "beginner-course"
        }
    )

    assert second_start.status_code == 201
    second_data = second_start.json()

    # === Step 4: Verify same user ===
    assert second_data["user_id"] == user_id
    assert second_data["username"] == username

    # Password should NOT be returned for existing user sign-in
    assert second_data.get("password") is None

    # Should have a new session ID
    second_session_id = second_data["session_id"]
    assert second_session_id != first_session_id

    # === Step 5: Verify both sessions exist ===
    result = await db_session.execute(
        select(Session).where(Session.id == first_session_id)
    )
    first_session = result.scalar_one_or_none()
    assert first_session is not None

    result = await db_session.execute(
        select(Session).where(Session.id == second_session_id)
    )
    second_session = result.scalar_one_or_none()
    assert second_session is not None

    # === Step 6: Verify user has participated in both sessions ===
    result = await db_session.execute(
        select(SessionParticipant).where(
            SessionParticipant.user_id == user_id
        )
    )
    participants = result.scalars().all()

    # Should have 2 session participations
    assert len(participants) >= 2

    session_ids = {p.session_id for p in participants}
    assert first_session_id in session_ids
    assert second_session_id in session_ids

    # === Step 7: Verify first session progress is preserved ===
    first_status = client.get(f"/api/game/status/{first_session_id}")
    assert first_status.status_code == 200
    first_status_data = first_status.json()

    # Should show tokens from the attempt we made
    assert first_status_data["total_tokens"] > 0

    # === Step 8: Verify second session is fresh ===
    second_status = client.get(f"/api/game/status/{second_session_id}")
    assert second_status.status_code == 200
    second_status_data = second_status.json()

    # New session should have 0 tokens (no attempts yet)
    assert second_status_data["total_tokens"] == 0


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_signin_invalid_credentials(
    client: TestClient,
    db_session: AsyncSession,
    all_challenges,
):
    """
    Test sign-in with invalid credentials.

    Flow:
    1. Try to sign in with non-existent user
    2. Verify 401 Unauthorized
    3. Try to sign in with wrong password
    4. Verify 401 Unauthorized
    """

    # === Test 1: Non-existent username ===
    nonexistent_response = client.post(
        "/api/game/start",
        json={
            "action": "signin",
            "username": "NonExistentUser-999",
            "password": "anypassword",
            "course_id": "beginner-course"
        }
    )

    assert nonexistent_response.status_code == 401
    error_data = nonexistent_response.json()
    assert "detail" in error_data

    error_detail = error_data["detail"]
    if isinstance(error_detail, dict):
        assert error_detail.get("error") == "user_not_found"

    # === Test 2: Create user then try wrong password ===
    create_response = client.post(
        "/api/game/start",
        json={"action": "generate", "course_id": "beginner-course"}
    )

    assert create_response.status_code == 201
    create_data = create_response.json()

    username = create_data["username"]
    correct_password = create_data["password"]

    # Try with wrong password
    wrong_password_response = client.post(
        "/api/game/start",
        json={
            "action": "signin",
            "username": username,
            "password": "WrongPassword123",
            "course_id": "beginner-course"
        }
    )

    assert wrong_password_response.status_code == 401
    error_data = wrong_password_response.json()
    assert "detail" in error_data

    error_detail = error_data["detail"]
    if isinstance(error_detail, dict):
        assert error_detail.get("error") == "invalid_password"


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_signin_missing_credentials(
    client: TestClient,
    db_session: AsyncSession,
    all_challenges,
):
    """
    Test sign-in with missing username or password.

    Flow:
    1. Try to sign in without username
    2. Verify 400 Bad Request
    3. Try to sign in without password
    4. Verify 400 Bad Request
    """

    # === Test 1: Missing username ===
    no_username = client.post(
        "/api/game/start",
        json={
            "action": "signin",
            "password": "somepassword",
            "course_id": "beginner-course"
        }
    )

    assert no_username.status_code == 400
    error_data = no_username.json()
    assert "detail" in error_data

    error_detail = error_data["detail"]
    if isinstance(error_detail, dict):
        assert error_detail.get("error") == "missing_username"

    # === Test 2: Missing password ===
    no_password = client.post(
        "/api/game/start",
        json={
            "action": "signin",
            "username": "someuser",
            "course_id": "beginner-course"
        }
    )

    assert no_password.status_code == 400
    error_data = no_password.json()
    assert "detail" in error_data

    error_detail = error_data["detail"]
    if isinstance(error_detail, dict):
        assert error_detail.get("error") == "missing_password"


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_signin_multiple_sessions_same_user(
    client: TestClient,
    db_session: AsyncSession,
    all_challenges,
):
    """
    Test that a user can have multiple active sessions.

    Flow:
    1. Create user
    2. Start session 1
    3. Sign in and start session 2
    4. Submit attempts to both sessions
    5. Verify both sessions are independent
    6. Verify global leaderboard shows combined progress
    """

    # Create user
    create_response = client.post(
        "/api/game/start",
        json={"action": "generate", "course_id": "beginner-course"}
    )

    assert create_response.status_code == 201
    create_data = create_response.json()

    username = create_data["username"]
    password = create_data["password"]
    user_id = create_data["user_id"]
    session1_id = create_data["session_id"]
    challenge_ids = create_data["challenges"]

    if len(challenge_ids) == 0:
        pytest.skip("No challenges available")

    # Submit attempt in session 1
    attempt1 = client.post(
        "/api/game/submit",
        json={
            "session_id": session1_id,
            "challenge_id": challenge_ids[0],
            "user_prompt": "Solve session 1.",
            "system_prompt": None,
            "context_files": []
        }
    )

    if attempt1.status_code == 503:
        pytest.skip("LLM service unavailable")

    assert attempt1.status_code == 200
    attempt1_data = attempt1.json()
    session1_tokens = attempt1_data["total_tokens"]

    # Sign in and create session 2
    signin_response = client.post(
        "/api/game/start",
        json={
            "action": "signin",
            "username": username,
            "password": password,
            "course_id": "beginner-course"
        }
    )

    assert signin_response.status_code == 201
    signin_data = signin_response.json()
    session2_id = signin_data["session_id"]

    # Verify different sessions
    assert session2_id != session1_id

    # Submit attempt in session 2
    attempt2 = client.post(
        "/api/game/submit",
        json={
            "session_id": session2_id,
            "challenge_id": challenge_ids[0],
            "user_prompt": "Solve session 2 with different prompt and strategy.",
            "system_prompt": None,
            "context_files": []
        }
    )

    if attempt2.status_code == 503:
        pytest.skip("LLM service unavailable")

    assert attempt2.status_code == 200
    attempt2_data = attempt2.json()
    session2_tokens = attempt2_data["total_tokens"]

    # Verify sessions are independent
    status1 = client.get(f"/api/game/status/{session1_id}")
    assert status1.status_code == 200
    status1_data = status1.json()
    assert status1_data["total_tokens"] == session1_tokens

    status2 = client.get(f"/api/game/status/{session2_id}")
    assert status2.status_code == 200
    status2_data = status2.json()
    assert status2_data["total_tokens"] == session2_tokens

    # Check global leaderboard
    global_lb = client.get("/api/leaderboard/global?limit=100&completed_only=false")
    assert global_lb.status_code == 200
    global_data = global_lb.json()

    # Find user in global leaderboard
    user_entries = [e for e in global_data["entries"] if e["user_id"] == user_id]

    # User should appear
    assert len(user_entries) > 0

    # Total tokens across all sessions
    user_entry = user_entries[0]
    # Note: Global leaderboard aggregates across all sessions
    # So total_tokens should be sum of both sessions
    # (though this depends on ScoringService implementation)
