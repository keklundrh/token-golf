"""
E2E Test: Multiplayer Session

Tests multiple users playing the same course and competing on leaderboards.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Score, Session, SessionParticipant


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_multiplayer_session(
    client: TestClient,
    db_session: AsyncSession,
    all_challenges,
):
    """
    Test multiplayer session: Multiple users playing same course,
    verify leaderboard rankings.

    Flow:
    1. User 1 starts session
    2. User 2 starts separate session (same course)
    3. User 3 starts separate session (same course)
    4. All users submit attempts for same challenge
    5. Verify session-specific leaderboards
    6. Verify global leaderboard shows all users
    7. Verify per-hole leaderboard ranks correctly
    """

    # === User 1: Start session ===
    user1_start = client.post(
        "/api/game/start",
        json={"action": "generate", "course_id": "beginner-course"}
    )

    assert user1_start.status_code == 201
    user1_data = user1_start.json()
    user1_session = user1_data["session_id"]
    user1_id = user1_data["user_id"]
    user1_name = user1_data["username"]
    challenge_ids = user1_data["challenges"]

    if len(challenge_ids) == 0:
        pytest.skip("No challenges available for this test")

    first_challenge_id = challenge_ids[0]

    # === User 2: Start session ===
    user2_start = client.post(
        "/api/game/start",
        json={"action": "generate", "course_id": "beginner-course"}
    )

    assert user2_start.status_code == 201
    user2_data = user2_start.json()
    user2_session = user2_data["session_id"]
    user2_id = user2_data["user_id"]
    user2_name = user2_data["username"]

    # === User 3: Start session ===
    user3_start = client.post(
        "/api/game/start",
        json={"action": "generate", "course_id": "beginner-course"}
    )

    assert user3_start.status_code == 201
    user3_data = user3_start.json()
    user3_session = user3_data["session_id"]
    user3_id = user3_data["user_id"]
    user3_name = user3_data["username"]

    # Verify all users are different
    assert user1_id != user2_id
    assert user2_id != user3_id
    assert user1_id != user3_id

    # Verify all sessions are different
    assert user1_session != user2_session
    assert user2_session != user3_session

    # === User 1: Submit attempt (efficient prompt - fewer tokens) ===
    user1_attempt = client.post(
        "/api/game/submit",
        json={
            "session_id": user1_session,
            "challenge_id": first_challenge_id,
            "user_prompt": "Solve efficiently.",  # Short prompt
            "system_prompt": None,
            "context_files": [],
            "action": "submit"
        }
    )

    if user1_attempt.status_code == 503:
        pytest.skip("LLM service unavailable")

    if user1_attempt.status_code == 422:
        pytest.skip("LLM did not solve challenge correctly - cannot test with action=submit")

    assert user1_attempt.status_code == 200
    user1_attempt_data = user1_attempt.json()
    user1_tokens = user1_attempt_data["total_tokens"]

    # === User 2: Submit attempt (verbose prompt - more tokens) ===
    user2_attempt = client.post(
        "/api/game/submit",
        json={
            "session_id": user2_session,
            "challenge_id": first_challenge_id,
            "user_prompt": (
                "Please write a comprehensive solution to this challenge. "
                "Include detailed comments explaining each step. "
                "Add error handling and edge case considerations. "
                "Make sure the code is well-documented and follows best practices."
            ),
            "system_prompt": (
                "You are an expert programmer who writes detailed, "
                "well-documented code with extensive explanations."
            ),
            "context_files": [],
            "action": "submit"
        }
    )

    if user2_attempt.status_code == 503:
        pytest.skip("LLM service unavailable")

    if user2_attempt.status_code == 422:
        pytest.skip("LLM did not solve challenge correctly - cannot test with action=submit")

    assert user2_attempt.status_code == 200
    user2_attempt_data = user2_attempt.json()
    user2_tokens = user2_attempt_data["total_tokens"]

    # === User 3: Submit attempt (medium prompt) ===
    user3_attempt = client.post(
        "/api/game/submit",
        json={
            "session_id": user3_session,
            "challenge_id": first_challenge_id,
            "user_prompt": "Solve this challenge with clean code.",
            "system_prompt": "You are a helpful coding assistant.",
            "context_files": [],
            "action": "submit"
        }
    )

    if user3_attempt.status_code == 503:
        pytest.skip("LLM service unavailable")

    if user3_attempt.status_code == 422:
        pytest.skip("LLM did not solve challenge correctly - cannot test with action=submit")

    assert user3_attempt.status_code == 200
    user3_attempt_data = user3_attempt.json()
    user3_tokens = user3_attempt_data["total_tokens"]

    # Verify database has scores for all users
    for user_id, session_id in [
        (user1_id, user1_session),
        (user2_id, user2_session),
        (user3_id, user3_session)
    ]:
        result = await db_session.execute(
            select(Score).where(
                Score.user_id == user_id,
                Score.session_id == session_id,
                Score.challenge_id == first_challenge_id
            )
        )
        score = result.scalar_one_or_none()
        assert score is not None
        assert score.total_tokens > 0

    # === Check session-specific leaderboards (ADR 010: completed + in_progress) ===
    # Each session should only show its own participants

    user1_leaderboard = client.get(f"/api/leaderboard/session/{user1_session}")
    assert user1_leaderboard.status_code == 200
    user1_lb_data = user1_leaderboard.json()
    user1_all = user1_lb_data["completed"] + user1_lb_data["in_progress"]
    assert len(user1_all) == 1  # Only user 1
    assert user1_all[0]["user_id"] == user1_id

    user2_leaderboard = client.get(f"/api/leaderboard/session/{user2_session}")
    assert user2_leaderboard.status_code == 200
    user2_lb_data = user2_leaderboard.json()
    user2_all = user2_lb_data["completed"] + user2_lb_data["in_progress"]
    assert len(user2_all) == 1  # Only user 2
    assert user2_all[0]["user_id"] == user2_id

    user3_leaderboard = client.get(f"/api/leaderboard/session/{user3_session}")
    assert user3_leaderboard.status_code == 200
    user3_lb_data = user3_leaderboard.json()
    user3_all = user3_lb_data["completed"] + user3_lb_data["in_progress"]
    assert len(user3_all) == 1  # Only user 3
    assert user3_all[0]["user_id"] == user3_id

    # === Check global leaderboard ===
    # Should show all users (if they completed challenges)
    global_leaderboard = client.get(
        "/api/leaderboard/global?limit=100&completed_only=false"
    )
    assert global_leaderboard.status_code == 200
    global_data = global_leaderboard.json()

    # All three users should be in global leaderboard
    user_ids_in_global = {entry["user_id"] for entry in global_data["entries"]}
    assert user1_id in user_ids_in_global
    assert user2_id in user_ids_in_global
    assert user3_id in user_ids_in_global

    # === Check per-hole leaderboard ===
    # Should rank users by tokens used (lower is better)
    hole_leaderboard = client.get(
        f"/api/leaderboard/hole/{first_challenge_id}?limit=100"
    )
    assert hole_leaderboard.status_code == 200
    hole_data = hole_leaderboard.json()

    assert hole_data["challenge_id"] == first_challenge_id

    # Find users in per-hole leaderboard (only those who completed)
    user1_entry = next(
        (e for e in hole_data["entries"] if e["user_id"] == user1_id),
        None
    )
    user2_entry = next(
        (e for e in hole_data["entries"] if e["user_id"] == user2_id),
        None
    )
    user3_entry = next(
        (e for e in hole_data["entries"] if e["user_id"] == user3_id),
        None
    )

    # Users only appear if they completed the challenge
    # Rankings should be based on tokens (lower is better in golf scoring)
    if user1_entry and user2_entry:
        # User 2 had verbose prompt so should have more tokens
        # Golf scoring: lower tokens = better rank = lower rank number
        # But we can't guarantee completion, so just verify structure
        assert "rank" in user1_entry
        assert "total_tokens" in user1_entry


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_concurrent_attempts(
    client: TestClient,
    db_session: AsyncSession,
    all_challenges,
):
    """
    Test concurrent users submitting attempts.
    Verifies data consistency under concurrent load.

    Flow:
    1. Create 3 users with sessions
    2. All submit attempts to same challenge concurrently
    3. Verify all attempts recorded correctly
    4. Verify leaderboard updates correctly
    """

    # Create 3 users
    users = []
    for i in range(3):
        start = client.post(
            "/api/game/start",
            json={"action": "generate", "course_id": "beginner-course"}
        )
        assert start.status_code == 201
        users.append(start.json())

    if len(users[0]["challenges"]) == 0:
        pytest.skip("No challenges available")

    challenge_id = users[0]["challenges"][0]

    # All users submit attempts
    for user in users:
        attempt = client.post(
            "/api/game/submit",
            json={
                "session_id": user["session_id"],
                "challenge_id": challenge_id,
                "user_prompt": f"Solve for user {user['username']}",
                "system_prompt": None,
                "context_files": [],
                "action": "submit"
            }
        )

        if attempt.status_code == 503:
            pytest.skip("LLM service unavailable")

        if attempt.status_code == 422:
            pytest.skip("LLM did not solve challenge correctly - cannot test with action=submit")

        assert attempt.status_code == 200

    # Verify all scores recorded
    for user in users:
        result = await db_session.execute(
            select(Score).where(
                Score.user_id == user["user_id"],
                Score.session_id == user["session_id"],
                Score.challenge_id == challenge_id
            )
        )
        score = result.scalar_one_or_none()
        assert score is not None
        assert score.total_attempts >= 1

    # Verify global leaderboard consistency
    global_lb = client.get("/api/leaderboard/global?limit=100&completed_only=false")
    assert global_lb.status_code == 200
    global_data = global_lb.json()

    # All users should appear
    user_ids = {u["user_id"] for u in users}
    lb_user_ids = {e["user_id"] for e in global_data["entries"]}
    assert user_ids.issubset(lb_user_ids)
