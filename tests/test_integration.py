"""
Token Golf - Integration Tests

Integration tests covering complete user flows and system interactions.
Tests the full stack: API -> Services -> Database.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.challenge import Challenge
from app.models.session import Session
from app.models.user import User
from app.services.challenge_loader import ChallengeLoaderService


# ============================================================================
# Authentication Flow Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_auth_flow_new_user(client: TestClient, db_session: AsyncSession):
    """
    Test complete authentication flow for new user.

    Flow:
    1. Generate new username/password
    2. Create user account
    3. Sign in with credentials
    4. Receive auth token
    5. Access protected endpoint

    TODO: Implement when auth API is complete
    """
    # TODO: POST /api/auth/register
    # TODO: POST /api/auth/login
    # TODO: GET /api/auth/me with token
    pytest.skip("Auth API not yet implemented")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_auth_flow_existing_user(
    client: TestClient,
    db_session: AsyncSession,
    sample_user: User,
):
    """
    Test authentication flow for existing user.

    Flow:
    1. Sign in with existing credentials
    2. Receive auth token
    3. Access protected endpoint

    TODO: Implement when auth API is complete
    """
    # TODO: POST /api/auth/login with sample_user credentials
    # TODO: Verify token returned
    # TODO: Use token to access protected resource
    pytest.skip("Auth API not yet implemented")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_auth_flow_invalid_credentials(client: TestClient):
    """
    Test authentication with invalid credentials.

    Flow:
    1. Attempt login with wrong password
    2. Verify 401 Unauthorized response

    TODO: Implement when auth API is complete
    """
    # TODO: POST /api/auth/login with invalid credentials
    # TODO: Assert 401 status code
    pytest.skip("Auth API not yet implemented")


# ============================================================================
# Challenge Flow Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_challenge_listing_flow(
    client: TestClient,
    all_challenges: list[Challenge],
):
    """
    Test challenge listing and filtering.

    Flow:
    1. List all challenges
    2. Filter by difficulty
    3. Filter by task type

    TODO: Implement when challenge API is complete
    """
    # TODO: GET /api/challenges
    # TODO: GET /api/challenges?difficulty=easy
    # TODO: GET /api/challenges?task_type=coding
    pytest.skip("Challenge listing API not yet implemented")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_challenge_retrieval_flow(
    client: TestClient,
    sample_challenge: Challenge,
):
    """
    Test retrieving individual challenge details.

    Flow:
    1. Get challenge by ID
    2. Verify challenge content
    3. Check context files included

    TODO: Implement when challenge API is complete
    """
    # TODO: GET /api/challenges/hole-001
    # TODO: Verify response includes all required fields
    # TODO: Check context_files if present
    pytest.skip("Challenge retrieval API not yet implemented")


# ============================================================================
# Course Flow Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_course_listing_flow(
    client: TestClient,
    challenge_loader: ChallengeLoaderService,
):
    """
    Test course listing and details.

    Flow:
    1. Load courses
    2. List all courses
    3. Get course details
    4. Verify course challenges exist

    TODO: Implement when course API is complete
    """
    # Load courses to validate they exist
    courses = await challenge_loader.list_courses()
    assert len(courses) > 0

    # TODO: GET /api/courses
    # TODO: GET /api/courses/beginner-course
    # TODO: Verify challenges in course are valid
    pytest.skip("Course API not yet implemented")


# ============================================================================
# Complete Game Flow Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_complete_game_flow(
    client: TestClient,
    db_session: AsyncSession,
    sample_user: User,
    sample_session: Session,
    sample_challenge: Challenge,
):
    """
    Test complete game flow from start to finish.

    Flow:
    1. User authenticates
    2. Create/join session on a course
    3. Get first challenge
    4. Submit attempt
    5. Receive score and feedback
    6. Move to next challenge
    7. Complete session
    8. View final leaderboard

    TODO: Implement full flow when all APIs are ready
    """
    # TODO: Implement authentication
    # TODO: POST /api/sessions (create new session)
    # TODO: GET /api/sessions/{session_id}/challenges (get challenges)
    # TODO: POST /api/attempts (submit attempt)
    # TODO: GET /api/attempts/{attempt_id} (check validation result)
    # TODO: POST /api/sessions/{session_id}/complete
    # TODO: GET /api/leaderboard/sessions/{session_id}

    # Verify test data is set up correctly
    assert sample_user is not None
    assert sample_session is not None
    assert sample_challenge is not None

    pytest.skip("Complete game flow API not yet implemented")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_multiplayer_session_flow(
    client: TestClient,
    db_session: AsyncSession,
    multiple_users: list[User],
):
    """
    Test multiplayer session with multiple participants.

    Flow:
    1. User 1 creates session
    2. Users 2 and 3 join session
    3. All users submit attempts
    4. Verify leaderboard updates
    5. Complete session
    6. Verify final rankings

    TODO: Implement when session API is complete
    """
    assert len(multiple_users) >= 3

    # TODO: POST /api/sessions (user 1 creates)
    # TODO: POST /api/sessions/{session_id}/join (users 2 & 3)
    # TODO: Each user submits attempts
    # TODO: GET /api/leaderboard/sessions/{session_id}
    # TODO: Verify rankings are correct
    pytest.skip("Multiplayer session API not yet implemented")


# ============================================================================
# Leaderboard Flow Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_leaderboard_global_flow(
    client: TestClient,
    db_session: AsyncSession,
    multiple_users: list[User],
):
    """
    Test global leaderboard functionality.

    Flow:
    1. Create multiple sessions with scores
    2. Query global leaderboard
    3. Filter by challenge
    4. Filter by time period

    TODO: Implement when leaderboard API is complete
    """
    # TODO: Create sample scores for users
    # TODO: GET /api/leaderboard/global
    # TODO: GET /api/leaderboard/global?challenge_id=hole-001
    # TODO: GET /api/leaderboard/global?period=week
    pytest.skip("Leaderboard API not yet implemented")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_leaderboard_session_flow(
    client: TestClient,
    db_session: AsyncSession,
    sample_session: Session,
    multiple_users: list[User],
):
    """
    Test session-specific leaderboard.

    Flow:
    1. Multiple users play same session
    2. Each submits attempts
    3. Query session leaderboard
    4. Verify rankings

    TODO: Implement when leaderboard API is complete
    """
    # TODO: Create attempts for multiple users in same session
    # TODO: GET /api/leaderboard/sessions/{session_id}
    # TODO: Verify user rankings based on scores
    pytest.skip("Session leaderboard API not yet implemented")


# ============================================================================
# Error Handling Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_session_timeout_flow(
    client: TestClient,
    db_session: AsyncSession,
    expired_session: Session,
):
    """
    Test handling of expired sessions.

    Flow:
    1. Attempt to submit to expired session
    2. Verify appropriate error response
    3. Check session marked as expired

    TODO: Implement when session timeout handling is ready
    """
    assert expired_session.is_expired()

    # TODO: POST /api/attempts for expired session
    # TODO: Verify 400/403 error response
    # TODO: Check error message indicates timeout
    pytest.skip("Session timeout handling not yet implemented")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_invalid_challenge_flow(client: TestClient):
    """
    Test handling of invalid challenge requests.

    Flow:
    1. Request non-existent challenge
    2. Verify 404 response

    TODO: Implement when challenge API is complete
    """
    # TODO: GET /api/challenges/invalid-challenge-id
    # TODO: Assert 404 status code
    pytest.skip("Challenge error handling not yet implemented")


# ============================================================================
# Data Validation Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_attempt_validation_flow(
    client: TestClient,
    db_session: AsyncSession,
    sample_session: Session,
    sample_challenge: Challenge,
):
    """
    Test attempt validation and scoring.

    Flow:
    1. Submit valid attempt
    2. Verify validation runs
    3. Check score calculated
    4. Verify feedback returned

    TODO: Implement when attempt validation is ready
    """
    # TODO: POST /api/attempts with valid solution
    # TODO: Wait for validation to complete
    # TODO: GET /api/attempts/{attempt_id}
    # TODO: Verify score and feedback present
    pytest.skip("Attempt validation not yet implemented")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_course_challenge_validation(
    db_session: AsyncSession,
    challenge_loader: ChallengeLoaderService,
):
    """
    Test that all courses reference valid challenges.

    Flow:
    1. Load all courses
    2. For each course, verify all challenges exist
    3. Ensure no broken references

    This test validates the data integrity of courses.yaml.
    """
    courses = await challenge_loader.list_courses()

    for course in courses:
        course_id = course["id"]

        # This should not raise if all challenges are valid
        challenges = await challenge_loader.get_course_challenges(course_id)

        # Verify we got challenges back
        assert len(challenges) > 0, f"Course {course_id} has no challenges"

        # Verify challenge count matches course definition
        expected_count = len(course["holes"])
        assert len(challenges) == expected_count, (
            f"Course {course_id} expected {expected_count} challenges, "
            f"got {len(challenges)}"
        )
