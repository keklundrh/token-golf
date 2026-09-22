"""
E2E Test: Multiple Challenges

Tests completing multiple challenges and token accumulation across a course.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Score, Attempt


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_multiple_challenges_navigation(
    client: TestClient,
    db_session: AsyncSession,
    all_challenges,
):
    """
    Test completing hole-001, navigating to hole-002, verifying token accumulation.

    Flow:
    1. Start session
    2. Complete hole-001
    3. Get status (should show hole-001 complete)
    4. Navigate to hole-002
    5. Complete hole-002
    6. Verify cumulative token tracking
    7. Verify individual challenge scores
    8. Verify session totals
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
    username = start_data["username"]
    challenge_ids = start_data["challenges"]

    # Need at least 2 challenges for this test
    if len(challenge_ids) < 2:
        pytest.skip("Need at least 2 challenges for this test")

    hole_001 = challenge_ids[0]
    hole_002 = challenge_ids[1]

    # Verify challenge IDs
    # They should be sorted, so first should be hole-001 or similar
    assert hole_001 is not None
    assert hole_002 is not None
    assert hole_001 != hole_002

    # === Step 2: Complete hole-001 ===
    hole_001_attempt = client.post(
        "/api/game/submit",
        json={
            "session_id": session_id,
            "challenge_id": hole_001,
            "user_prompt": "Solve the first challenge efficiently.",
            "system_prompt": None,
            "context_files": []
        }
    )

    if hole_001_attempt.status_code == 503:
        pytest.skip("LLM service unavailable")

    assert hole_001_attempt.status_code == 200
    hole_001_data = hole_001_attempt.json()

    hole_001_tokens = hole_001_data["total_tokens"]
    hole_001_cumulative = hole_001_data["cumulative_tokens"]

    # First attempt on first challenge: total should equal cumulative
    assert hole_001_tokens == hole_001_cumulative
    assert hole_001_data["attempt_number"] == 1

    # === Step 3: Get status after hole-001 ===
    status_after_1 = client.get(f"/api/game/status/{session_id}")
    assert status_after_1.status_code == 200
    status_1_data = status_after_1.json()

    # Verify hole-001 is in challenges
    challenge_statuses = {c["id"]: c for c in status_1_data["challenges"]}
    assert hole_001 in challenge_statuses

    hole_001_status = challenge_statuses[hole_001]
    assert hole_001_status["attempts"] >= 1
    assert hole_001_status["tokens"] == hole_001_cumulative

    # If the attempt was correct, hole should be marked complete
    # (depends on validation, so we don't assert this)

    # Total session tokens should equal hole-001 tokens so far
    assert status_1_data["total_tokens"] == hole_001_cumulative

    # === Step 4: Load hole-002 details ===
    hole_002_details = client.get(f"/api/challenges/{hole_002}")
    assert hole_002_details.status_code == 200
    hole_002_data = hole_002_details.json()

    assert hole_002_data["id"] == hole_002
    assert "description" in hole_002_data

    # === Step 5: Submit attempt for hole-002 ===
    hole_002_attempt = client.post(
        "/api/game/submit",
        json={
            "session_id": session_id,
            "challenge_id": hole_002,
            "user_prompt": "Solve the second challenge.",
            "system_prompt": None,
            "context_files": []
        }
    )

    if hole_002_attempt.status_code == 503:
        pytest.skip("LLM service unavailable")

    assert hole_002_attempt.status_code == 200
    hole_002_attempt_data = hole_002_attempt.json()

    hole_002_tokens = hole_002_attempt_data["total_tokens"]
    hole_002_cumulative = hole_002_attempt_data["cumulative_tokens"]

    # For hole-002, cumulative should equal total (first attempt on this hole)
    assert hole_002_tokens == hole_002_cumulative
    assert hole_002_attempt_data["attempt_number"] == 1

    # === Step 6: Verify token accumulation ===
    # Get final status
    final_status = client.get(f"/api/game/status/{session_id}")
    assert final_status.status_code == 200
    final_data = final_status.json()

    # Total tokens should be sum of both challenges
    expected_total = hole_001_cumulative + hole_002_cumulative
    assert final_data["total_tokens"] == expected_total

    # Verify individual challenge statuses
    final_challenges = {c["id"]: c for c in final_data["challenges"]}

    assert hole_001 in final_challenges
    assert hole_002 in final_challenges

    assert final_challenges[hole_001]["tokens"] == hole_001_cumulative
    assert final_challenges[hole_002]["tokens"] == hole_002_cumulative

    # === Step 7: Verify database scores ===
    # Check hole-001 score
    result = await db_session.execute(
        select(Score).where(
            Score.user_id == user_id,
            Score.session_id == session_id,
            Score.challenge_id == hole_001
        )
    )
    score_001 = result.scalar_one_or_none()
    assert score_001 is not None
    assert score_001.total_tokens == hole_001_cumulative
    assert score_001.total_attempts >= 1

    # Check hole-002 score
    result = await db_session.execute(
        select(Score).where(
            Score.user_id == user_id,
            Score.session_id == session_id,
            Score.challenge_id == hole_002
        )
    )
    score_002 = result.scalar_one_or_none()
    assert score_002 is not None
    assert score_002.total_tokens == hole_002_cumulative
    assert score_002.total_attempts >= 1

    # === Step 8: Verify attempts are recorded ===
    result = await db_session.execute(
        select(Attempt).where(
            Attempt.user_id == user_id,
            Attempt.session_id == session_id
        )
    )
    all_attempts = result.scalars().all()

    # Should have at least 2 attempts (one per challenge)
    assert len(all_attempts) >= 2

    # Verify attempts for each challenge
    hole_001_attempts = [a for a in all_attempts if a.challenge_id == hole_001]
    hole_002_attempts = [a for a in all_attempts if a.challenge_id == hole_002]

    assert len(hole_001_attempts) >= 1
    assert len(hole_002_attempts) >= 1


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_multiple_attempts_per_challenge(
    client: TestClient,
    db_session: AsyncSession,
    all_challenges,
):
    """
    Test submitting multiple attempts to the same challenge.

    Flow:
    1. Start session
    2. Submit attempt 1 to hole-001
    3. Submit attempt 2 to hole-001
    4. Submit attempt 3 to hole-001
    5. Verify cumulative tokens increase
    6. Verify attempt numbers increment
    7. Verify score tracking
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

    challenge_id = challenge_ids[0]

    # Track cumulative tokens
    cumulative_tokens = 0
    attempt_tokens = []

    # === Submit 3 attempts ===
    for attempt_num in range(1, 4):
        attempt_response = client.post(
            "/api/game/submit",
            json={
                "session_id": session_id,
                "challenge_id": challenge_id,
                "user_prompt": f"Attempt {attempt_num}: Solve this challenge.",
                "system_prompt": None,
                "context_files": []
            }
        )

        if attempt_response.status_code == 503:
            pytest.skip("LLM service unavailable")

        assert attempt_response.status_code == 200
        attempt_data = attempt_response.json()

        # Verify attempt number increments
        assert attempt_data["attempt_number"] == attempt_num

        # Track tokens
        tokens = attempt_data["total_tokens"]
        cumulative_tokens += tokens
        attempt_tokens.append(tokens)

        # Cumulative should match our running total
        assert attempt_data["cumulative_tokens"] == cumulative_tokens

    # === Verify final score ===
    result = await db_session.execute(
        select(Score).where(
            Score.user_id == user_id,
            Score.session_id == session_id,
            Score.challenge_id == challenge_id
        )
    )
    score = result.scalar_one_or_none()
    assert score is not None

    # Should have 3 attempts
    assert score.total_attempts == 3

    # Total tokens should match cumulative
    assert score.total_tokens == cumulative_tokens

    # === Verify attempts in database ===
    result = await db_session.execute(
        select(Attempt).where(
            Attempt.user_id == user_id,
            Attempt.session_id == session_id,
            Attempt.challenge_id == challenge_id
        ).order_by(Attempt.attempt_number)
    )
    attempts = result.scalars().all()

    assert len(attempts) == 3

    # Verify attempt numbers
    for i, attempt in enumerate(attempts, start=1):
        assert attempt.attempt_number == i


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_challenge_switching(
    client: TestClient,
    db_session: AsyncSession,
    all_challenges,
):
    """
    Test switching between challenges (not completing them in order).

    Flow:
    1. Start session
    2. Attempt hole-001
    3. Switch to hole-002 (without completing hole-001)
    4. Attempt hole-002
    5. Switch back to hole-001
    6. Verify tokens tracked independently
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

    if len(challenge_ids) < 2:
        pytest.skip("Need at least 2 challenges")

    hole_001 = challenge_ids[0]
    hole_002 = challenge_ids[1]

    # === Attempt hole-001 ===
    attempt_001_v1 = client.post(
        "/api/game/submit",
        json={
            "session_id": session_id,
            "challenge_id": hole_001,
            "user_prompt": "First attempt at hole 1.",
            "system_prompt": None,
            "context_files": []
        }
    )

    if attempt_001_v1.status_code == 503:
        pytest.skip("LLM service unavailable")

    assert attempt_001_v1.status_code == 200
    data_001_v1 = attempt_001_v1.json()
    tokens_001_v1 = data_001_v1["total_tokens"]

    # === Switch to hole-002 ===
    attempt_002_v1 = client.post(
        "/api/game/submit",
        json={
            "session_id": session_id,
            "challenge_id": hole_002,
            "user_prompt": "First attempt at hole 2.",
            "system_prompt": None,
            "context_files": []
        }
    )

    if attempt_002_v1.status_code == 503:
        pytest.skip("LLM service unavailable")

    assert attempt_002_v1.status_code == 200
    data_002_v1 = attempt_002_v1.json()
    tokens_002_v1 = data_002_v1["total_tokens"]

    # Should be attempt #1 for hole-002
    assert data_002_v1["attempt_number"] == 1

    # === Switch back to hole-001 ===
    attempt_001_v2 = client.post(
        "/api/game/submit",
        json={
            "session_id": session_id,
            "challenge_id": hole_001,
            "user_prompt": "Second attempt at hole 1.",
            "system_prompt": None,
            "context_files": []
        }
    )

    if attempt_001_v2.status_code == 503:
        pytest.skip("LLM service unavailable")

    assert attempt_001_v2.status_code == 200
    data_001_v2 = attempt_001_v2.json()
    tokens_001_v2 = data_001_v2["total_tokens"]

    # Should be attempt #2 for hole-001
    assert data_001_v2["attempt_number"] == 2

    # Cumulative for hole-001 should be sum of both attempts
    assert data_001_v2["cumulative_tokens"] == tokens_001_v1 + tokens_001_v2

    # === Verify final scores ===
    result = await db_session.execute(
        select(Score).where(
            Score.user_id == user_id,
            Score.session_id == session_id,
            Score.challenge_id == hole_001
        )
    )
    score_001 = result.scalar_one_or_none()
    assert score_001 is not None
    assert score_001.total_attempts == 2
    assert score_001.total_tokens == tokens_001_v1 + tokens_001_v2

    result = await db_session.execute(
        select(Score).where(
            Score.user_id == user_id,
            Score.session_id == session_id,
            Score.challenge_id == hole_002
        )
    )
    score_002 = result.scalar_one_or_none()
    assert score_002 is not None
    assert score_002.total_attempts == 1
    assert score_002.total_tokens == tokens_002_v1

    # === Verify game status ===
    status = client.get(f"/api/game/status/{session_id}")
    assert status.status_code == 200
    status_data = status.json()

    # Total should be sum of all challenges
    expected_total = (tokens_001_v1 + tokens_001_v2) + tokens_002_v1
    assert status_data["total_tokens"] == expected_total


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_all_challenges_completion(
    client: TestClient,
    db_session: AsyncSession,
    all_challenges,
):
    """
    Test completing all challenges in a course.

    Flow:
    1. Start session
    2. Complete all challenges in order
    3. Verify final status shows all complete
    4. Verify total token accumulation
    5. Verify appears on leaderboards
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

    # Track total tokens
    total_tokens = 0

    # === Attempt each challenge ===
    for challenge_id in challenge_ids:
        # Load challenge
        challenge_response = client.get(f"/api/challenges/{challenge_id}")
        assert challenge_response.status_code == 200

        # Submit attempt
        attempt_response = client.post(
            "/api/game/submit",
            json={
                "session_id": session_id,
                "challenge_id": challenge_id,
                "user_prompt": f"Solve {challenge_id}.",
                "system_prompt": None,
                "context_files": []
            }
        )

        if attempt_response.status_code == 503:
            pytest.skip("LLM service unavailable")

        assert attempt_response.status_code == 200
        attempt_data = attempt_response.json()

        total_tokens += attempt_data["total_tokens"]

    # === Verify final status ===
    final_status = client.get(f"/api/game/status/{session_id}")
    assert final_status.status_code == 200
    final_data = final_status.json()

    # All challenges should have attempts
    assert len(final_data["challenges"]) == len(challenge_ids)

    for challenge in final_data["challenges"]:
        assert challenge["attempts"] >= 1
        assert challenge["tokens"] > 0

    # Total tokens should match
    assert final_data["total_tokens"] == total_tokens

    # === Verify global leaderboard ===
    global_lb = client.get("/api/leaderboard/global?limit=100&completed_only=false")
    assert global_lb.status_code == 200
    global_data = global_lb.json()

    # User should appear
    user_in_leaderboard = any(
        entry["user_id"] == user_id for entry in global_data["entries"]
    )
    assert user_in_leaderboard
