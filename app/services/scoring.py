"""
Token Golf - Scoring Service

Records attempts, calculates cumulative scores, and retrieves leaderboard data.
All tokens count: input + output + system prompts (treated as input).
"""

import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, desc, func, select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attempt import Attempt
from app.models.score import Score
from app.models.user import User

logger = logging.getLogger(__name__)


class ScoringService:
    """
    Service for managing scores and attempts.

    Responsibilities:
        - Record individual attempts with token counts
        - Calculate and update cumulative scores
        - Mark challenge completion
        - Retrieve scores for leaderboards

    Business Rules:
        - All tokens count (input + output)
        - System prompts count as input tokens
        - Failed attempts add to score
        - Users can retry after success (counts as additional strokes)
        - First correct attempt marks completion time
    """

    def __init__(self, db_session: AsyncSession):
        """
        Initialize scoring service.

        Args:
            db_session: SQLAlchemy async database session
        """
        self.db = db_session
        # Tracks (user, session, challenge) -> completed status within this
        # service instance, so completion logging fires only on transition.
        self._was_completed: dict[tuple, bool] = {}

    async def record_attempt(
        self,
        user_id: int,
        session_id: str,
        challenge_id: str,
        prompt: str,
        response: str,
        input_tokens: int,
        output_tokens: int,
        is_correct: bool,
        system_prompt: Optional[str] = None,
        context_files: Optional[dict] = None,
    ) -> Attempt:
        """
        Record a new attempt and update cumulative score.

        This method:
        1. Determines the attempt number for this user/challenge
        2. Creates an Attempt record
        3. Updates or creates the Score record
        4. Marks completion if this is the first correct attempt

        Args:
            user_id: User making the attempt
            session_id: Session the attempt belongs to
            challenge_id: Challenge being attempted
            prompt: User's prompt text
            response: LLM's response text
            input_tokens: Input token count (includes system prompt)
            output_tokens: Output token count
            is_correct: Whether validation passed
            system_prompt: User's system prompt (optional)
            context_files: Active context files (optional, JSON)

        Returns:
            Created Attempt object

        Raises:
            ValueError: If token counts are negative
            SQLAlchemyError: If database operation fails
        """
        # Validate inputs
        if input_tokens < 0 or output_tokens < 0:
            raise ValueError("Token counts cannot be negative")

        total_tokens = input_tokens + output_tokens

        # Get next attempt number for this user/challenge
        attempt_number = await self._get_next_attempt_number(
            user_id=user_id,
            challenge_id=challenge_id,
        )

        # Create attempt record
        attempt = Attempt(
            user_id=user_id,
            session_id=session_id,
            challenge_id=challenge_id,
            attempt_number=attempt_number,
            prompt=prompt,
            system_prompt=system_prompt,
            context_files=context_files,
            response=response,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            is_correct=is_correct,
            created_at=datetime.utcnow(),
        )

        self.db.add(attempt)

        # Update score
        await self._update_score(
            user_id=user_id,
            session_id=session_id,
            challenge_id=challenge_id,
            tokens_to_add=total_tokens,
            is_correct=is_correct,
        )

        await self.db.commit()
        await self.db.refresh(attempt)

        logger.info(
            f"Recorded attempt #{attempt_number} for user {user_id} "
            f"on challenge {challenge_id}: {total_tokens} tokens, "
            f"correct={is_correct}"
        )

        return attempt

    async def _get_next_attempt_number(
        self,
        user_id: int,
        challenge_id: str,
    ) -> int:
        """
        Get the next attempt number for a user on a challenge.

        Attempt numbers are per user per challenge (not per session).
        If user has made 3 attempts across all sessions, next is 4.

        Args:
            user_id: User ID
            challenge_id: Challenge ID

        Returns:
            Next attempt number (1-indexed)
        """
        # Get max attempt number for this user/challenge
        stmt = select(func.max(Attempt.attempt_number)).where(
            Attempt.user_id == user_id,
            Attempt.challenge_id == challenge_id,
        )
        result = await self.db.execute(stmt)
        max_attempt = result.scalar_one_or_none()

        # If no attempts yet, start at 1
        return (max_attempt or 0) + 1

    async def _update_score(
        self,
        user_id: int,
        session_id: str,
        challenge_id: str,
        tokens_to_add: int,
        is_correct: bool,
    ) -> Score:
        """
        Update or create score record for user/session/challenge.

        Updates:
            - Increments total_attempts
            - Adds tokens_to_add to total_tokens
            - Sets completed_at if is_correct and not already completed

        Args:
            user_id: User ID
            session_id: Session ID
            challenge_id: Challenge ID
            tokens_to_add: Tokens to add to total
            is_correct: Whether this attempt was correct

            Updated or created Score object
        """
        # Atomic increment (no read-modify-write race); insert row if missing.
        values = {
            "total_attempts": Score.total_attempts + 1,
            "total_tokens": Score.total_tokens + tokens_to_add,
        }
        if is_correct:
            values["completed_at"] = func.coalesce(
                Score.completed_at, datetime.utcnow()
            )
        stmt = (
            sqlite_insert(Score)
            .values(
                user_id=user_id,
                session_id=session_id,
                challenge_id=challenge_id,
                total_attempts=1,
                total_tokens=tokens_to_add,
                completed_at=datetime.utcnow() if is_correct else None,
            )
            .on_conflict_do_update(
                index_elements=["user_id", "session_id", "challenge_id"],
                set_=values,
            )
        )
        await self.db.execute(stmt)

        # Re-fetch the upserted row to return it
        stmt = select(Score).where(
            Score.user_id == user_id,
            Score.session_id == session_id,
            Score.challenge_id == challenge_id,
        )
        result = await self.db.execute(stmt)
        score = result.scalar_one()

        if is_correct and score.completed_at is not None and not self._was_completed.get(
            (user_id, session_id, challenge_id)
        ):
            logger.info(
                f"User {user_id} completed challenge {challenge_id} "
                f"in session {session_id} with {score.total_tokens} tokens"
            )
        self._was_completed[(user_id, session_id, challenge_id)] = (
            score.completed_at is not None
        )

        return score

    async def get_score(
        self,
        user_id: int,
        session_id: str,
        challenge_id: str,
    ) -> Optional[Score]:
        """
        Get score for specific user/session/challenge.

        Args:
            user_id: User ID
            session_id: Session ID
            challenge_id: Challenge ID

        Returns:
            Score object if found, None otherwise
        """
        stmt = select(Score).where(
            Score.user_id == user_id,
            Score.session_id == session_id,
            Score.challenge_id == challenge_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_scores(
        self,
        user_id: int,
        session_id: str,
    ) -> list[Score]:
        """
        Get all scores for a user in a session.

        Useful for showing user's progress across all challenges.

        Args:
            user_id: User ID
            session_id: Session ID

        Returns:
            List of Score objects, ordered by challenge_id
        """
        stmt = (
            select(Score)
            .where(
                Score.user_id == user_id,
                Score.session_id == session_id,
            )
            .order_by(Score.challenge_id)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_challenge_scores(
        self,
        challenge_id: str,
        session_id: Optional[str] = None,
        completed_only: bool = False,
    ) -> list[Score]:
        """
        Get all scores for a challenge.

        Used for per-hole leaderboards.

        Args:
            challenge_id: Challenge ID
            session_id: Optional session filter
            completed_only: If True, only return completed challenges

        Returns:
            List of Score objects, ordered by tokens (ascending, lower is better)
        """
        stmt = select(Score).where(Score.challenge_id == challenge_id)

        if session_id:
            stmt = stmt.where(Score.session_id == session_id)

        if completed_only:
            stmt = stmt.where(Score.completed_at.is_not(None))

        # Order by tokens (lower is better, like golf)
        stmt = stmt.order_by(Score.total_tokens.asc())

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_session_leaderboard(
        self,
        session_id: str,
        limit: int = 10,
    ) -> list[dict]:
        """
        Get leaderboard for a session.

        Aggregates all challenges in the session to create overall standings.

        Args:
            session_id: Session ID
            limit: Max number of entries to return

        Returns:
            List of dicts with user_id, username, total_tokens,
            completed_challenges, total_attempts.
            Ordered by total_tokens (ascending)
        """
        # Aggregate scores per user in session, joined to usernames
        stmt = (
            select(
                Score.user_id,
                User.username,
                func.sum(Score.total_tokens).label("total_tokens"),
                func.count(Score.id).label("total_attempts"),
                func.sum(
                    func.cast(Score.completed_at.is_not(None), Integer)
                ).label("completed_challenges"),
            )
            .join(User, User.id == Score.user_id)
            .where(Score.session_id == session_id)
            .group_by(Score.user_id, User.username)
            .order_by(func.sum(Score.total_tokens).asc())
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        return [
            {
                "user_id": row.user_id,
                "username": row.username,
                "total_tokens": row.total_tokens or 0,
                "total_attempts": row.total_attempts or 0,
                "completed_challenges": row.completed_challenges or 0,
            }
            for row in rows
        ]

    async def get_global_leaderboard(
        self,
        limit: int = 10,
    ) -> list[dict]:
        """
        Get global leaderboard across all sessions.

        Shows best performers historically.

        Args:
            limit: Max number of entries to return

        Returns:
            List of dicts with user_id, username, total_tokens,
            completed_challenges, total_attempts.
            Ordered by total_tokens (ascending)
        """
        # Aggregate all scores per user, joined to usernames
        stmt = (
            select(
                Score.user_id,
                User.username,
                func.sum(Score.total_tokens).label("total_tokens"),
                func.count(Score.id).label("total_attempts"),
                func.sum(
                    func.cast(Score.completed_at.is_not(None), Integer)
                ).label("completed_challenges"),
            )
            .join(User, User.id == Score.user_id)
            .group_by(Score.user_id, User.username)
            .order_by(func.sum(Score.total_tokens).asc())
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        return [
            {
                "user_id": row.user_id,
                "username": row.username,
                "total_tokens": row.total_tokens or 0,
                "total_attempts": row.total_attempts or 0,
                "completed_challenges": row.completed_challenges or 0,
            }
            for row in rows
        ]

    async def get_per_hole_leaderboard(
        self,
        challenge_id: str,
        limit: int = 10,
    ) -> list[dict]:
        """
        Get leaderboard for a specific challenge across all sessions.

        Only users who completed the challenge are ranked; best score
        (lowest total_tokens) per user is used.

        Args:
            challenge_id: Challenge ID (e.g., "hole-001")
            limit: Max number of entries to return

        Returns:
            List of dicts with user_id, username, session_id, total_tokens,
            total_attempts, completed_at. Ordered by total_tokens (ascending).
        """
        stmt = (
            select(
                Score.user_id,
                User.username,
                Score.session_id,
                Score.total_tokens,
                Score.total_attempts,
                Score.completed_at,
            )
            .join(User, User.id == Score.user_id)
            .where(
                Score.challenge_id == challenge_id,
                Score.completed_at.is_not(None),
            )
            .order_by(Score.total_tokens.asc(), Score.completed_at.asc())
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        return [
            {
                "user_id": row.user_id,
                "username": row.username,
                "session_id": row.session_id,
                "total_tokens": row.total_tokens or 0,
                "total_attempts": row.total_attempts or 0,
                "completed_at": row.completed_at,
            }
            for row in rows
        ]

    async def get_user_attempts(
        self,
        user_id: int,
        challenge_id: str,
        session_id: Optional[str] = None,
    ) -> list[Attempt]:
        """
        Get all attempts for a user on a challenge.

        Useful for showing attempt history and progress.

        Args:
            user_id: User ID
            challenge_id: Challenge ID
            session_id: Optional session filter

        Returns:
            List of Attempt objects, ordered by attempt_number
        """
        stmt = (
            select(Attempt)
            .where(
                Attempt.user_id == user_id,
                Attempt.challenge_id == challenge_id,
            )
            .order_by(Attempt.attempt_number.asc())
        )

        if session_id:
            stmt = stmt.where(Attempt.session_id == session_id)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_attempt_count(
        self,
        user_id: int,
        challenge_id: str,
    ) -> int:
        """
        Get total number of attempts for a user on a challenge.

        Args:
            user_id: User ID
            challenge_id: Challenge ID

        Returns:
            Number of attempts made
        """
        stmt = select(func.count(Attempt.id)).where(
            Attempt.user_id == user_id,
            Attempt.challenge_id == challenge_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one() or 0

    async def clear_challenge_score(
        self,
        user_id: int,
        session_id: str,
        challenge_id: str,
    ) -> bool:
        """
        Clear tokens for a specific challenge (weather delay scenario).

        Used when LLM API errors occur - resets that hole for affected user.
        Only clears the score, does not delete attempt history.

        Args:
            user_id: User ID
            session_id: Session ID
            challenge_id: Challenge ID to clear

        Returns:
            True if score was cleared, False if no score existed
        """
        score = await self.get_score(user_id, session_id, challenge_id)

        if score:
            score.total_attempts = 0
            score.total_tokens = 0
            score.completed_at = None
            await self.db.commit()

            logger.warning(
                f"Cleared score for user {user_id} on challenge {challenge_id} "
                f"in session {session_id} (weather delay)"
            )
            return True

        return False
