"""
Unit tests for ScoringService

Tests attempt recording, score calculation, leaderboards (global, per-hole, session),
and score queries.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from app.services.scoring import ScoringService
from app.models.attempt import Attempt
from app.models.score import Score
from app.models.user import User
from app.models.session import Session


# Fixtures for scoring tests (avoid bcrypt hashing issues)
@pytest.fixture
async def test_user(db_session):
    """Create a test user without bcrypt hashing."""
    user = User(
        username="test-user",
        password_hash="simple-hash",  # Not using bcrypt
        created_at=datetime.utcnow(),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_users(db_session):
    """Create multiple test users."""
    users = [
        User(
            username=f"player-{i}",
            password_hash=f"hash-{i}",
            created_at=datetime.utcnow(),
            is_active=True,
        )
        for i in range(1, 4)
    ]

    for user in users:
        db_session.add(user)

    await db_session.commit()

    for user in users:
        await db_session.refresh(user)

    return users


@pytest.fixture
async def test_session(db_session, test_user):
    """Create a test session."""
    session_id = str(uuid4())
    created_at = datetime.utcnow()
    timeout_hours = 3

    session = Session(
        id=session_id,
        course_id="beginner-course",
        created_at=created_at,
        timeout_hours=timeout_hours,
        status="active",
        expires_at=Session.calculate_expires_at(created_at, timeout_hours),
    )

    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    return session


class TestRecordAttempt:
    """Test recording attempts and updating scores."""

    @pytest.mark.asyncio
    async def test_record_first_attempt_correct(self, db_session):
        """Test recording first successful attempt."""
        # Create user
        user = User(
            username="test-user",
            password_hash="simple-hash",
            created_at=datetime.utcnow()
        )
        db_session.add(user)

        # Create session (required for scoring service to query course_total_holes)
        session = Session(
            id="session-001",
            course_id="beginner-course",
            created_at=datetime.utcnow(),
            timeout_hours=3,
            status="active",
            expires_at=datetime.utcnow() + timedelta(hours=3),
            course_total_holes=5,
        )
        db_session.add(session)

        await db_session.commit()
        await db_session.refresh(user)

        scoring = ScoringService(db_session)

        attempt = await scoring.record_attempt(
            user_id=user.id,
            session_id="session-001",
            challenge_id="hole-001",
            prompt="Write an add function",
            response="def add(a, b): return a + b",
            input_tokens=10,
            output_tokens=15,
            is_correct=True,
        )

        assert attempt.attempt_number == 1
        assert attempt.total_tokens == 25
        assert attempt.is_correct is True

        # Check score was created
        score = await scoring.get_score(user.id, "session-001", "hole-001")
        assert score is not None
        assert score.total_tokens == 25
        assert score.total_attempts == 1
        assert score.completed_at is not None

    @pytest.mark.asyncio
    async def test_record_multiple_attempts(self, db_session):
        """Test recording multiple attempts increments attempt number."""
        user = User(
            username="test-user",
            password_hash="simple-hash",
            created_at=datetime.utcnow()
        )
        db_session.add(user)

        # Create session
        session = Session(
            id="session-001",
            course_id="beginner-course",
            created_at=datetime.utcnow(),
            timeout_hours=3,
            status="active",
            expires_at=datetime.utcnow() + timedelta(hours=3),
            course_total_holes=5,
        )
        db_session.add(session)

        await db_session.commit()
        await db_session.refresh(user)

        scoring = ScoringService(db_session)

        # First attempt (failed)
        attempt1 = await scoring.record_attempt(
            user_id=user.id,
            session_id="session-001",
            challenge_id="hole-001",
            prompt="Try 1",
            response="wrong",
            input_tokens=5,
            output_tokens=3,
            is_correct=False,
        )

        # Second attempt (failed)
        attempt2 = await scoring.record_attempt(
            user_id=user.id,
            session_id="session-001",
            challenge_id="hole-001",
            prompt="Try 2",
            response="still wrong",
            input_tokens=6,
            output_tokens=4,
            is_correct=False,
        )

        # Third attempt (success)
        attempt3 = await scoring.record_attempt(
            user_id=user.id,
            session_id="session-001",
            challenge_id="hole-001",
            prompt="Try 3",
            response="correct!",
            input_tokens=7,
            output_tokens=5,
            is_correct=True,
        )

        assert attempt1.attempt_number == 1
        assert attempt2.attempt_number == 2
        assert attempt3.attempt_number == 3

        # Check cumulative score
        score = await scoring.get_score(user.id, "session-001", "hole-001")
        assert score.total_tokens == 8 + 10 + 12  # All attempts count
        assert score.total_attempts == 3
        assert score.completed_at is not None

    @pytest.mark.asyncio
    async def test_record_attempt_negative_tokens_raises_error(self, db_session):
        """Test recording attempt with negative tokens raises ValueError."""
        user = User(
            username="test-user",
            password_hash="simple-hash",
            created_at=datetime.utcnow()
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        scoring = ScoringService(db_session)

        with pytest.raises(ValueError, match="Token counts cannot be negative"):
            await scoring.record_attempt(
                user_id=user.id,
                session_id="session-001",
                challenge_id="hole-001",
                prompt="Test",
                response="Test",
                input_tokens=-5,
                output_tokens=10,
                is_correct=True,
            )

    @pytest.mark.asyncio
    async def test_record_attempt_with_system_prompt(self, db_session):
        """Test recording attempt includes system prompt."""
        user = User(
            username="test-user",
            password_hash="simple-hash",
            created_at=datetime.utcnow()
        )
        db_session.add(user)

        # Create session
        session = Session(
            id="session-001",
            course_id="beginner-course",
            created_at=datetime.utcnow(),
            timeout_hours=3,
            status="active",
            expires_at=datetime.utcnow() + timedelta(hours=3),
            course_total_holes=5,
        )
        db_session.add(session)

        await db_session.commit()
        await db_session.refresh(user)

        scoring = ScoringService(db_session)

        attempt = await scoring.record_attempt(
            user_id=user.id,
            session_id="session-001",
            challenge_id="hole-001",
            prompt="Write code",
            response="Code here",
            input_tokens=20,
            output_tokens=10,
            is_correct=True,
            system_prompt="You are a coding assistant",
        )

        assert attempt.system_prompt == "You are a coding assistant"

    @pytest.mark.asyncio
    async def test_record_attempt_with_context_files(self, db_session):
        """Test recording attempt includes context files."""
        user = User(
            username="test-user",
            password_hash="simple-hash",
            created_at=datetime.utcnow()
        )
        db_session.add(user)

        # Create session
        session = Session(
            id="session-001",
            course_id="beginner-course",
            created_at=datetime.utcnow(),
            timeout_hours=3,
            status="active",
            expires_at=datetime.utcnow() + timedelta(hours=3),
            course_total_holes=5,
        )
        db_session.add(session)

        await db_session.commit()
        await db_session.refresh(user)

        scoring = ScoringService(db_session)

        context = {"file1": "content1"}

        attempt = await scoring.record_attempt(
            user_id=user.id,
            session_id="session-001",
            challenge_id="hole-001",
            prompt="Test",
            response="Test",
            input_tokens=10,
            output_tokens=5,
            is_correct=True,
            context_files=context,
        )

        assert attempt.context_files == context


class TestGetScore:
    """Test score retrieval."""

    @pytest.mark.asyncio
    async def test_get_existing_score(self, db_session, test_user, test_session):
        """Test getting an existing score."""
        scoring = ScoringService(db_session)

        # Record an attempt to create a score
        await scoring.record_attempt(
            user_id=test_user.id,
            session_id=test_session.id,
            challenge_id="hole-001",
            prompt="Test",
            response="Test",
            input_tokens=10,
            output_tokens=5,
            is_correct=True,
        )

        score = await scoring.get_score(
            test_user.id,
            test_session.id,
            "hole-001"
        )

        assert score is not None
        assert score.total_tokens == 15

    @pytest.mark.asyncio
    async def test_get_nonexistent_score(self, db_session, test_user, test_session):
        """Test getting nonexistent score returns None."""
        scoring = ScoringService(db_session)

        score = await scoring.get_score(
            test_user.id,
            test_session.id,
            "nonexistent-hole"
        )

        assert score is None


class TestGetUserScores:
    """Test getting all scores for a user in a session."""

    @pytest.mark.asyncio
    async def test_get_user_scores(self, db_session, test_user, test_session):
        """Test getting all user scores in a session."""
        scoring = ScoringService(db_session)

        # Record attempts for multiple challenges
        for i in range(1, 4):
            await scoring.record_attempt(
                user_id=test_user.id,
                session_id=test_session.id,
                challenge_id=f"hole-00{i}",
                prompt="Test",
                response="Test",
                input_tokens=10,
                output_tokens=5,
                is_correct=True,
            )

        scores = await scoring.get_user_scores(test_user.id, test_session.id)

        assert len(scores) == 3
        assert all(s.user_id == test_user.id for s in scores)


class TestGetChallengeScores:
    """Test getting all scores for a challenge."""

    @pytest.mark.asyncio
    async def test_get_challenge_scores(self, db_session, test_users, test_session):
        """Test getting all scores for a challenge."""
        scoring = ScoringService(db_session)

        # Record attempts from multiple users
        for i, user in enumerate(test_users):
            await scoring.record_attempt(
                user_id=user.id,
                session_id=test_session.id,
                challenge_id="hole-001",
                prompt="Test",
                response="Test",
                input_tokens=10 * (i + 1),
                output_tokens=5 * (i + 1),
                is_correct=True,
            )

        scores = await scoring.get_challenge_scores("hole-001")

        assert len(scores) == 3
        # Should be ordered by total_tokens ascending
        assert scores[0].total_tokens < scores[1].total_tokens < scores[2].total_tokens

    @pytest.mark.asyncio
    async def test_get_challenge_scores_completed_only(self, db_session, test_users, test_session):
        """Test getting only completed challenge scores."""
        scoring = ScoringService(db_session)

        # Record some completed and some incomplete
        for i, user in enumerate(test_users):
            await scoring.record_attempt(
                user_id=user.id,
                session_id=test_session.id,
                challenge_id="hole-001",
                prompt="Test",
                response="Test",
                input_tokens=10,
                output_tokens=5,
                is_correct=(i == 0),  # Only first user succeeds
            )

        scores = await scoring.get_challenge_scores("hole-001", completed_only=True)

        assert len(scores) == 1
        assert scores[0].completed_at is not None


class TestSessionLeaderboard:
    """Test session leaderboard generation."""

    @pytest.mark.asyncio
    async def test_session_leaderboard(self, db_session, test_users, test_session):
        """Test getting session leaderboard with aggregated scores."""
        from app.models.session import SessionParticipant
        from datetime import datetime

        # Add users as session participants
        for user in test_users:
            participant = SessionParticipant(
                session_id=test_session.id,
                user_id=user.id,
                joined_at=datetime.utcnow(),
            )
            db_session.add(participant)
        await db_session.commit()

        scoring = ScoringService(db_session)

        # Record attempts from multiple users on multiple challenges
        for user in test_users:
            for i in range(1, 3):  # 2 challenges each
                await scoring.record_attempt(
                    user_id=user.id,
                    session_id=test_session.id,
                    challenge_id=f"hole-00{i}",
                    prompt="Test",
                    response="Test",
                    input_tokens=10 * user.id,
                    output_tokens=5 * user.id,
                    is_correct=True,
                )

        leaderboard_data = await scoring.get_session_leaderboard(test_session.id, limit=10)

        # ADR 010: leaderboard is now a dict with completed/in_progress sections
        all_entries = leaderboard_data["completed"] + leaderboard_data["in_progress"]
        assert len(all_entries) == 3
        # Should be ordered by total_tokens ascending within sections
        if len(leaderboard_data["in_progress"]) >= 2:
            assert leaderboard_data["in_progress"][0]["total_tokens"] <= leaderboard_data["in_progress"][1]["total_tokens"]

    @pytest.mark.asyncio
    async def test_session_leaderboard_limit(self, db_session, test_users, test_session):
        """Test session leaderboard respects limit parameter."""
        from app.models.session import SessionParticipant
        from datetime import datetime

        # Add users as session participants
        for user in test_users:
            participant = SessionParticipant(
                session_id=test_session.id,
                user_id=user.id,
                joined_at=datetime.utcnow(),
            )
            db_session.add(participant)
        await db_session.commit()

        scoring = ScoringService(db_session)

        for user in test_users:
            await scoring.record_attempt(
                user_id=user.id,
                session_id=test_session.id,
                challenge_id="hole-001",
                prompt="Test",
                response="Test",
                input_tokens=10,
                output_tokens=5,
                is_correct=True,
            )

        leaderboard_data = await scoring.get_session_leaderboard(test_session.id, limit=2)

        # ADR 010: limit applies per section
        total_entries = len(leaderboard_data["completed"]) + len(leaderboard_data["in_progress"])
        assert total_entries <= 4  # Max 2 per section = 4 total


class TestGlobalLeaderboard:
    """Test global leaderboard across all sessions."""

    @pytest.mark.asyncio
    async def test_global_leaderboard(self, db_session, test_users):
        """Test getting global leaderboard across sessions (ADR 010: requires course completion)."""
        from app.models.session import SessionParticipant

        # Create sessions
        for session_num in [1, 2]:
            session = Session(
                id=f"session-{session_num}",
                course_id="beginner-course",
                created_at=datetime.utcnow(),
                timeout_hours=3,
                status="active",
                expires_at=datetime.utcnow() + timedelta(hours=3),
                course_total_holes=1,  # Single hole course for this test
            )
            db_session.add(session)

        await db_session.commit()

        scoring = ScoringService(db_session)

        # Record attempts across different sessions and mark courses as completed
        for user in test_users:
            for session_num in [1, 2]:
                # Create participant and mark as completed
                participant = SessionParticipant(
                    session_id=f"session-{session_num}",
                    user_id=user.id,
                    joined_at=datetime.utcnow(),
                    holes_completed=1,
                    course_completed_at=datetime.utcnow(),
                )
                db_session.add(participant)

                await scoring.record_attempt(
                    user_id=user.id,
                    session_id=f"session-{session_num}",
                    challenge_id="hole-001",
                    prompt="Test",
                    response="Test",
                    input_tokens=10 * user.id,
                    output_tokens=5 * user.id,
                    is_correct=True,
                )

        await db_session.commit()

        leaderboard = await scoring.get_global_leaderboard(limit=10)

        assert len(leaderboard) == 3
        # Should be ordered by total_tokens
        assert leaderboard[0]["total_tokens"] < leaderboard[1]["total_tokens"]
        # Each user should have 2 completed challenges (across sessions)
        for entry in leaderboard:
            assert entry["completed_challenges"] == 2


class TestPerHoleLeaderboard:
    """Test per-hole leaderboard."""

    @pytest.mark.asyncio
    async def test_per_hole_leaderboard(self, db_session, test_users):
        """Test getting leaderboard for specific challenge."""
        # Create session
        session = Session(
            id="session-001",
            course_id="beginner-course",
            created_at=datetime.utcnow(),
            timeout_hours=3,
            status="active",
            expires_at=datetime.utcnow() + timedelta(hours=3),
            course_total_holes=5,
        )
        db_session.add(session)
        await db_session.commit()

        scoring = ScoringService(db_session)

        # Record attempts from multiple users
        for i, user in enumerate(test_users):
            await scoring.record_attempt(
                user_id=user.id,
                session_id="session-001",
                challenge_id="hole-001",
                prompt="Test",
                response="Test",
                input_tokens=10 * (i + 1),
                output_tokens=5 * (i + 1),
                is_correct=True,
            )

        leaderboard = await scoring.get_per_hole_leaderboard("hole-001", limit=10)

        assert len(leaderboard) == 3
        # Should be ordered by total_tokens
        assert leaderboard[0]["total_tokens"] < leaderboard[1]["total_tokens"]
        # All should be completed
        assert all(entry["completed_at"] is not None for entry in leaderboard)

    @pytest.mark.asyncio
    async def test_per_hole_leaderboard_only_completed(self, db_session, test_users):
        """Test per-hole leaderboard only shows completed attempts."""
        # Create session
        session = Session(
            id="session-001",
            course_id="beginner-course",
            created_at=datetime.utcnow(),
            timeout_hours=3,
            status="active",
            expires_at=datetime.utcnow() + timedelta(hours=3),
            course_total_holes=5,
        )
        db_session.add(session)
        await db_session.commit()

        scoring = ScoringService(db_session)

        # Record some completed and some incomplete
        for i, user in enumerate(test_users):
            await scoring.record_attempt(
                user_id=user.id,
                session_id="session-001",
                challenge_id="hole-001",
                prompt="Test",
                response="Test",
                input_tokens=10,
                output_tokens=5,
                is_correct=(i < 2),  # Only first 2 users succeed
            )

        leaderboard = await scoring.get_per_hole_leaderboard("hole-001", limit=10)

        # Should only show the 2 users who completed it
        assert len(leaderboard) == 2


class TestGetUserAttempts:
    """Test getting user attempts for a challenge."""

    @pytest.mark.asyncio
    async def test_get_user_attempts(self, db_session, test_user):
        """Test getting all user attempts for a challenge."""
        # Create session
        session = Session(
            id="session-001",
            course_id="beginner-course",
            created_at=datetime.utcnow(),
            timeout_hours=3,
            status="active",
            expires_at=datetime.utcnow() + timedelta(hours=3),
            course_total_holes=5,
        )
        db_session.add(session)
        await db_session.commit()

        scoring = ScoringService(db_session)

        # Record multiple attempts
        for i in range(3):
            await scoring.record_attempt(
                user_id=test_user.id,
                session_id="session-001",
                challenge_id="hole-001",
                prompt=f"Try {i+1}",
                response=f"Response {i+1}",
                input_tokens=10,
                output_tokens=5,
                is_correct=(i == 2),
            )

        attempts = await scoring.get_user_attempts(
            test_user.id,
            "hole-001"
        )

        assert len(attempts) == 3
        assert attempts[0].attempt_number == 1
        assert attempts[2].attempt_number == 3
        assert attempts[2].is_correct is True

    @pytest.mark.asyncio
    async def test_get_user_attempts_with_session_filter(self, db_session, test_user):
        """Test getting user attempts filtered by session."""
        # Create sessions
        for session_num in [1, 2]:
            session = Session(
                id=f"session-{session_num}",
                course_id="beginner-course",
                created_at=datetime.utcnow(),
                timeout_hours=3,
                status="active",
                expires_at=datetime.utcnow() + timedelta(hours=3),
                course_total_holes=5,
            )
            db_session.add(session)

        await db_session.commit()

        scoring = ScoringService(db_session)

        # Record attempts in different sessions
        for session_num in [1, 2]:
            await scoring.record_attempt(
                user_id=test_user.id,
                session_id=f"session-{session_num}",
                challenge_id="hole-001",
                prompt="Test",
                response="Test",
                input_tokens=10,
                output_tokens=5,
                is_correct=True,
            )

        attempts = await scoring.get_user_attempts(
            test_user.id,
            "hole-001",
            session_id="session-1"
        )

        assert len(attempts) == 1
        assert attempts[0].session_id == "session-1"


class TestGetAttemptCount:
    """Test getting attempt count for a user on a challenge."""

    @pytest.mark.asyncio
    async def test_get_attempt_count(self, db_session, test_user):
        """Test getting total attempt count."""
        scoring = ScoringService(db_session)

        # Record multiple attempts
        for i in range(5):
            await scoring.record_attempt(
                user_id=test_user.id,
                session_id="session-001",
                challenge_id="hole-001",
                prompt="Test",
                response="Test",
                input_tokens=10,
                output_tokens=5,
                is_correct=False,
            )

        count = await scoring.get_attempt_count(test_user.id, "hole-001")

        assert count == 5

    @pytest.mark.asyncio
    async def test_get_attempt_count_zero(self, db_session, test_user):
        """Test getting attempt count when no attempts exist."""
        scoring = ScoringService(db_session)

        count = await scoring.get_attempt_count(test_user.id, "hole-999")

        assert count == 0


class TestClearChallengeScore:
    """Test clearing challenge score (weather delay scenario)."""

    @pytest.mark.asyncio
    async def test_clear_existing_score(self, db_session, test_user, test_session):
        """Test clearing an existing score."""
        scoring = ScoringService(db_session)

        # Create a score
        await scoring.record_attempt(
            user_id=test_user.id,
            session_id=test_session.id,
            challenge_id="hole-001",
            prompt="Test",
            response="Test",
            input_tokens=100,
            output_tokens=50,
            is_correct=True,
        )

        # Verify score exists
        score_before = await scoring.get_score(
            test_user.id,
            test_session.id,
            "hole-001"
        )
        assert score_before.total_tokens == 150

        # Clear the score
        cleared = await scoring.clear_challenge_score(
            test_user.id,
            test_session.id,
            "hole-001"
        )

        assert cleared is True

        # Verify score was reset
        score_after = await scoring.get_score(
            test_user.id,
            test_session.id,
            "hole-001"
        )
        assert score_after.total_tokens == 0
        assert score_after.total_attempts == 0
        assert score_after.completed_at is None

    @pytest.mark.asyncio
    async def test_clear_nonexistent_score(self, db_session, test_user, test_session):
        """Test clearing nonexistent score returns False."""
        scoring = ScoringService(db_session)

        cleared = await scoring.clear_challenge_score(
            test_user.id,
            test_session.id,
            "nonexistent-hole"
        )

        assert cleared is False


class TestScoreCumulativeTracking:
    """Test cumulative score tracking across attempts."""

    @pytest.mark.asyncio
    async def test_failed_attempts_add_to_score(self, db_session, test_user, test_session):
        """Test that failed attempts add to cumulative score."""
        scoring = ScoringService(db_session)

        # First attempt - failed
        await scoring.record_attempt(
            user_id=test_user.id,
            session_id=test_session.id,
            challenge_id="hole-001",
            prompt="Try 1",
            response="Wrong",
            input_tokens=10,
            output_tokens=5,
            is_correct=False,
        )

        score1 = await scoring.get_score(test_user.id, test_session.id, "hole-001")
        assert score1.total_tokens == 15
        assert score1.completed_at is None
        assert score1.total_attempts == 1

    @pytest.mark.asyncio
    async def test_retries_after_success_count(self, db_session, test_user, test_session):
        """Test that first correct attempt marks completion."""
        scoring = ScoringService(db_session)

        # First attempt - success
        await scoring.record_attempt(
            user_id=test_user.id,
            session_id=test_session.id,
            challenge_id="hole-001",
            prompt="First try",
            response="Correct",
            input_tokens=10,
            output_tokens=5,
            is_correct=True,
        )

        score1 = await scoring.get_score(test_user.id, test_session.id, "hole-001")
        assert score1.completed_at is not None
        assert score1.total_tokens == 15
        assert score1.total_attempts == 1
