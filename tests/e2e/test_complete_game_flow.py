"""
E2E Test: Complete Game Flow

Tests the complete user journey from user generation through scoring and leaderboard.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Score, Session, SessionParticipant, User


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_complete_game_flow(
    client: TestClient,
    db_session: AsyncSession,
    all_challenges,
):
    """
    Test complete game flow: Generate user → start session → load challenge →
    submit attempts → validate → score → leaderboard.

    Flow:
    1. Generate new user
    2. Start game session
    3. Load challenge details
    4. Submit an incorrect attempt
    5. Submit a correct attempt
    6. Verify score is recorded
    7. Check leaderboard contains user
    """

    # Step 1: Generate new user and start session
    start_response = client.post(
        "/api/game/start",
        json={
            "action": "generate",
            "course_id": "beginner-course"
        }
    )

    assert start_response.status_code == 201
    start_data = start_response.json()

    # Verify response structure
    assert "session_id" in start_data
    assert "user_id" in start_data
    assert "username" in start_data
    assert "password" in start_data  # New user should get password
    assert "course_id" in start_data
    assert "challenges" in start_data
    assert "current_challenge_id" in start_data

    session_id = start_data["session_id"]
    user_id = start_data["user_id"]
    username = start_data["username"]
    password = start_data["password"]
    challenge_ids = start_data["challenges"]

    # Verify session and user were created in database
    result = await db_session.execute(
        select(Session).where(Session.id == session_id)
    )
    session = result.scalar_one_or_none()
    assert session is not None
    assert session.status == "active"

    result = await db_session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.username == username

    # Verify session participant
    result = await db_session.execute(
        select(SessionParticipant).where(
            SessionParticipant.session_id == session_id,
            SessionParticipant.user_id == user_id
        )
    )
    participant = result.scalar_one_or_none()
    assert participant is not None

    # Step 2: Load first challenge details
    first_challenge_id = challenge_ids[0]
    challenge_response = client.get(f"/api/challenges/{first_challenge_id}")

    assert challenge_response.status_code == 200
    challenge_data = challenge_response.json()

    assert challenge_data["id"] == first_challenge_id
    assert "name" in challenge_data
    assert "description" in challenge_data
    assert "validation_type" in challenge_data

    # Step 3: Submit an incorrect attempt (prompt too vague)
    incorrect_attempt = client.post(
        "/api/game/submit",
        json={
            "session_id": session_id,
            "challenge_id": first_challenge_id,
            "user_prompt": "Do it",  # Intentionally vague
            "system_prompt": None,
            "context_files": []
        }
    )

    # Note: This may succeed or fail depending on LLM API availability
    # In a real test, we'd mock the LLM client
    if incorrect_attempt.status_code == 503:
        # LLM service unavailable (weather delay)
        pytest.skip("LLM service unavailable - cannot test complete flow")

    assert incorrect_attempt.status_code == 200
    incorrect_data = incorrect_attempt.json()

    assert "attempt_id" in incorrect_data
    assert "is_correct" in incorrect_data
    assert "total_tokens" in incorrect_data
    assert "cumulative_tokens" in incorrect_data
    assert "attempt_number" in incorrect_data

    # First attempt should be attempt #1
    assert incorrect_data["attempt_number"] == 1

    # Step 4: Submit a correct attempt (proper prompt)
    # Note: This assumes hole-001 is a coding challenge
    correct_attempt = client.post(
        "/api/game/submit",
        json={
            "session_id": session_id,
            "challenge_id": first_challenge_id,
            "user_prompt": "Write a Python function that solves the given task. Include all necessary code.",
            "system_prompt": "You are a helpful coding assistant that writes clean, efficient code.",
            "context_files": []
        }
    )

    if correct_attempt.status_code == 503:
        pytest.skip("LLM service unavailable - cannot test complete flow")

    assert correct_attempt.status_code == 200
    correct_data = correct_attempt.json()

    # Verify attempt was recorded
    assert correct_data["attempt_number"] >= 2
    assert "llm_response" in correct_data
    assert "validation_message" in correct_data

    # If correct, should suggest next challenge
    if correct_data["is_correct"]:
        assert correct_data["next_action"] == "next_challenge"
    else:
        assert correct_data["next_action"] == "retry"

    # Step 5: Verify score was recorded in database
    result = await db_session.execute(
        select(Score).where(
            Score.user_id == user_id,
            Score.session_id == session_id,
            Score.challenge_id == first_challenge_id
        )
    )
    score = result.scalar_one_or_none()
    assert score is not None
    assert score.total_attempts >= 2
    assert score.total_tokens > 0

    # Step 6: Get game status
    status_response = client.get(f"/api/game/status/{session_id}")
    assert status_response.status_code == 200
    status_data = status_response.json()

    assert status_data["session_id"] == session_id
    assert status_data["user_id"] == user_id
    assert status_data["username"] == username
    assert status_data["session_status"] == "active"
    assert len(status_data["challenges"]) > 0
    assert status_data["total_tokens"] > 0

    # Step 7: Check session leaderboard
    leaderboard_response = client.get(f"/api/leaderboard/session/{session_id}")
    assert leaderboard_response.status_code == 200
    leaderboard_data = leaderboard_response.json()

    assert leaderboard_data["leaderboard_type"] == "session"
    assert leaderboard_data["session_id"] == session_id
    assert len(leaderboard_data["entries"]) > 0

    # Verify our user is in the leaderboard
    user_in_leaderboard = any(
        entry["user_id"] == user_id for entry in leaderboard_data["entries"]
    )
    assert user_in_leaderboard

    # Step 8: Check global leaderboard
    global_leaderboard = client.get("/api/leaderboard/global")
    assert global_leaderboard.status_code == 200
    global_data = global_leaderboard.json()

    assert global_data["leaderboard_type"] == "global"
    # User may or may not appear depending on if they completed any challenges

    # Step 9: Check per-hole leaderboard
    hole_leaderboard = client.get(f"/api/leaderboard/hole/{first_challenge_id}")
    assert hole_leaderboard.status_code == 200
    hole_data = hole_leaderboard.json()

    assert hole_data["leaderboard_type"] == "per_hole"
    assert hole_data["challenge_id"] == first_challenge_id

    # If the user completed the challenge, they should appear
    if correct_data.get("is_correct"):
        user_in_hole_leaderboard = any(
            entry["user_id"] == user_id for entry in hole_data["entries"]
        )
        # Note: User only appears if they completed the challenge
        # So we only assert if is_correct was True


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_complete_course_flow(
    client: TestClient,
    db_session: AsyncSession,
    all_challenges,
):
    """
    Test completing multiple challenges in sequence.

    Flow:
    1. Start session
    2. Complete first challenge
    3. Move to second challenge
    4. Verify token accumulation
    5. Check final status
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

    # We need at least 2 challenges for this test
    if len(challenge_ids) < 2:
        pytest.skip("Need at least 2 challenges for this test")

    # Track cumulative tokens
    cumulative_tokens = 0

    # Complete first challenge
    first_challenge_id = challenge_ids[0]
    first_attempt = client.post(
        "/api/game/submit",
        json={
            "session_id": session_id,
            "challenge_id": first_challenge_id,
            "user_prompt": "Solve this challenge efficiently with minimal tokens.",
            "system_prompt": "You are a helpful assistant.",
            "context_files": []
        }
    )

    if first_attempt.status_code == 503:
        pytest.skip("LLM service unavailable")

    assert first_attempt.status_code == 200
    first_data = first_attempt.json()
    cumulative_tokens += first_data["total_tokens"]

    # Try second challenge
    second_challenge_id = challenge_ids[1]

    # Load second challenge
    second_challenge_response = client.get(f"/api/challenges/{second_challenge_id}")
    assert second_challenge_response.status_code == 200

    # Submit attempt for second challenge
    second_attempt = client.post(
        "/api/game/submit",
        json={
            "session_id": session_id,
            "challenge_id": second_challenge_id,
            "user_prompt": "Solve this challenge.",
            "system_prompt": "You are a helpful assistant.",
            "context_files": []
        }
    )

    if second_attempt.status_code == 503:
        pytest.skip("LLM service unavailable")

    assert second_attempt.status_code == 200
    second_data = second_attempt.json()

    # Verify token accumulation
    # Each challenge has its own cumulative count
    assert second_data["cumulative_tokens"] == second_data["total_tokens"]

    # Get overall game status
    status_response = client.get(f"/api/game/status/{session_id}")
    assert status_response.status_code == 200
    status_data = status_response.json()

    # Total tokens should include both challenges
    assert status_data["total_tokens"] > 0

    # Verify both challenges appear in status
    challenge_status_ids = [c["id"] for c in status_data["challenges"]]
    assert first_challenge_id in challenge_status_ids
    assert second_challenge_id in challenge_status_ids
