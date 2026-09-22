"""
Token Golf - Leaderboard API Endpoints

Provides three leaderboard views:
- Global: Rankings across all sessions
- Per-Hole: Best scores for individual challenges
- Session: Rankings within a specific session
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Session, User
from app.services import ScoringService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])


# ============================================================================
# Pydantic Models
# ============================================================================


class LeaderboardEntry(BaseModel):
    """Single entry in a leaderboard."""

    rank: int = Field(..., description="Ranking position (1-based)")
    user_id: int = Field(..., description="User identifier")
    username: str = Field(..., description="Username")
    total_tokens: int = Field(..., description="Total tokens used")
    completed_challenges: int = Field(..., description="Number of challenges completed")
    total_attempts: int = Field(..., description="Total number of attempts")
    session_id: Optional[str] = Field(
        None, description="Session ID (for session leaderboard)"
    )
    completed_at: Optional[str] = Field(
        None, description="Completion timestamp (ISO format)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "rank": 1,
                "user_id": 42,
                "username": "Blue-Pebblebeach-7",
                "total_tokens": 1250,
                "completed_challenges": 5,
                "total_attempts": 12,
                "session_id": "session-abc123",
                "completed_at": "2026-09-21T15:30:00",
            }
        }


class LeaderboardResponse(BaseModel):
    """Leaderboard response with entries and metadata."""

    leaderboard_type: str = Field(
        ..., description="Type of leaderboard (global, per_hole, session)"
    )
    entries: List[LeaderboardEntry] = Field(..., description="Leaderboard entries")
    total_entries: int = Field(..., description="Total number of entries")
    limit: int = Field(..., description="Maximum entries returned")
    offset: int = Field(..., description="Offset for pagination")
    current_page: int = Field(..., description="Current page number (1-based)")
    has_more: bool = Field(..., description="Whether there are more entries to load")
    user_rank: Optional[int] = Field(
        None, description="Current user's rank (if applicable)"
    )
    challenge_id: Optional[str] = Field(
        None, description="Challenge ID (for per-hole leaderboard)"
    )
    session_id: Optional[str] = Field(
        None, description="Session ID (for session leaderboard)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "leaderboard_type": "global",
                "entries": [
                    {
                        "rank": 1,
                        "user_id": 42,
                        "username": "Blue-Pebblebeach-7",
                        "total_tokens": 1250,
                        "completed_challenges": 5,
                        "total_attempts": 12,
                    }
                ],
                "total_entries": 50,
                "limit": 10,
                "offset": 0,
                "current_page": 1,
                "has_more": True,
                "user_rank": None,
            }
        }


# ============================================================================
# Endpoints
# ============================================================================


@router.get("/global", response_model=LeaderboardResponse)
async def get_global_leaderboard(
    limit: int = Query(10, ge=1, le=100, description="Maximum entries to return"),
    offset: int = Query(0, ge=0, description="Number of entries to skip"),
    completed_only: bool = Query(
        True, description="Only show users who completed at least one challenge"
    ),
    db: AsyncSession = Depends(get_db),
) -> LeaderboardResponse:
    """
    Get global leaderboard across all sessions.

    Rankings are based on total tokens used across all completed challenges.
    Lower tokens = better rank (golf scoring).

    Args:
        limit: Maximum entries to return (1-100, default 10)
        offset: Number of entries to skip for pagination (default 0)
        completed_only: Only show users with at least one completed challenge
        db: Database session

    Returns:
        LeaderboardResponse with global rankings
    """
    logger.info(
        f"Getting global leaderboard: limit={limit}, offset={offset}, "
        f"completed_only={completed_only}"
    )

    scoring_service = ScoringService(db)
    leaderboard = await scoring_service.get_global_leaderboard(
        limit=limit + offset  # Get more to handle offset
    )

    # Filter completed only if requested
    if completed_only:
        leaderboard = [entry for entry in leaderboard if entry.get("completed_challenges", 0) > 0]

    # Apply offset and limit
    total_entries = len(leaderboard)
    leaderboard = leaderboard[offset : offset + limit]

    # Get usernames for leaderboard entries
    user_ids = [entry["user_id"] for entry in leaderboard]
    if user_ids:
        result = await db.execute(select(User).where(User.id.in_(user_ids)))
        users = {user.id: user.username for user in result.scalars().all()}
    else:
        users = {}

    # Build response entries
    entries = [
        LeaderboardEntry(
            rank=offset + idx + 1,
            user_id=entry["user_id"],
            username=users.get(entry["user_id"], f"User-{entry['user_id']}"),
            total_tokens=entry["total_tokens"],
            completed_challenges=entry.get("completed_challenges", 0),
            total_attempts=entry.get("total_attempts", 0),
        )
        for idx, entry in enumerate(leaderboard)
    ]

    logger.info(f"Returning {len(entries)} global leaderboard entries")

    # Calculate pagination metadata
    current_page = (offset // limit) + 1 if limit > 0 else 1
    has_more = (offset + len(entries)) < total_entries

    return LeaderboardResponse(
        leaderboard_type="global",
        entries=entries,
        total_entries=total_entries,
        limit=limit,
        offset=offset,
        current_page=current_page,
        has_more=has_more,
        user_rank=None,  # Would need user_id parameter to determine
    )


@router.get("/hole/{challenge_id}", response_model=LeaderboardResponse)
async def get_per_hole_leaderboard(
    challenge_id: str,
    limit: int = Query(10, ge=1, le=100, description="Maximum entries to return"),
    offset: int = Query(0, ge=0, description="Number of entries to skip"),
    db: AsyncSession = Depends(get_db),
) -> LeaderboardResponse:
    """
    Get leaderboard for a specific challenge (hole).

    Rankings show best scores for this challenge across all sessions.
    Only users who completed the challenge are included.

    Args:
        challenge_id: Challenge identifier (e.g., "hole-001")
        limit: Maximum entries to return (1-100, default 10)
        offset: Number of entries to skip for pagination (default 0)
        db: Database session

    Returns:
        LeaderboardResponse with per-hole rankings
    """
    logger.info(
        f"Getting per-hole leaderboard for {challenge_id}: "
        f"limit={limit}, offset={offset}"
    )

    scoring_service = ScoringService(db)
    leaderboard = await scoring_service.get_per_hole_leaderboard(
        challenge_id=challenge_id,
        limit=limit + offset,
    )

    # Apply offset and limit
    total_entries = len(leaderboard)
    leaderboard = leaderboard[offset : offset + limit]

    # Build response entries (per-hole returns username directly)
    entries = [
        LeaderboardEntry(
            rank=offset + idx + 1,
            user_id=entry["user_id"],
            username=entry.get("username", f"User-{entry['user_id']}"),
            total_tokens=entry["total_tokens"],
            completed_challenges=1,  # Always 1 for per-hole
            total_attempts=entry.get("total_attempts", 0),
            session_id=entry.get("session_id"),
            completed_at=entry.get("completed_at").isoformat()
            if entry.get("completed_at")
            else None,
        )
        for idx, entry in enumerate(leaderboard)
    ]

    logger.info(
        f"Returning {len(entries)} per-hole leaderboard entries for {challenge_id}"
    )

    # Calculate pagination metadata
    current_page = (offset // limit) + 1 if limit > 0 else 1
    has_more = (offset + len(entries)) < total_entries

    return LeaderboardResponse(
        leaderboard_type="per_hole",
        entries=entries,
        total_entries=total_entries,
        limit=limit,
        offset=offset,
        current_page=current_page,
        has_more=has_more,
        user_rank=None,  # Would need user_id parameter to determine
        challenge_id=challenge_id,
    )


@router.get("/session/{session_id}", response_model=LeaderboardResponse)
async def get_session_leaderboard(
    session_id: str,
    limit: int = Query(100, ge=1, le=1000, description="Maximum entries to return"),
    offset: int = Query(0, ge=0, description="Number of entries to skip"),
    db: AsyncSession = Depends(get_db),
) -> LeaderboardResponse:
    """
    Get leaderboard for a specific session.

    Rankings show participants in this session only.
    Useful for current competition view.

    Args:
        session_id: Session identifier
        limit: Maximum entries to return (1-1000, default 100)
        offset: Number of entries to skip for pagination (default 0)
        db: Database session

    Returns:
        LeaderboardResponse with session rankings
    """
    logger.info(
        f"Getting session leaderboard for {session_id}: "
        f"limit={limit}, offset={offset}"
    )

    # Verify session exists
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "session_not_found",
                "message": f"Session '{session_id}' not found.",
                "details": {"session_id": session_id},
                "suggestions": [
                    "Check that the session ID is correct",
                    "Start a new game session with POST /api/game/start",
                ],
            },
        )

    scoring_service = ScoringService(db)
    leaderboard = await scoring_service.get_session_leaderboard(
        session_id=session_id,
        limit=limit + offset,
    )

    # Apply offset and limit
    total_entries = len(leaderboard)
    leaderboard = leaderboard[offset : offset + limit]

    # Get usernames for leaderboard entries
    user_ids = [entry["user_id"] for entry in leaderboard]
    if user_ids:
        result = await db.execute(select(User).where(User.id.in_(user_ids)))
        users = {user.id: user.username for user in result.scalars().all()}
    else:
        users = {}

    # Build response entries
    entries = [
        LeaderboardEntry(
            rank=offset + idx + 1,
            user_id=entry["user_id"],
            username=users.get(entry["user_id"], f"User-{entry['user_id']}"),
            total_tokens=entry["total_tokens"],
            completed_challenges=entry.get("completed_challenges", 0),
            total_attempts=entry.get("total_attempts", 0),
            session_id=session_id,
        )
        for idx, entry in enumerate(leaderboard)
    ]

    logger.info(
        f"Returning {len(entries)} session leaderboard entries for {session_id}"
    )

    # Calculate pagination metadata
    current_page = (offset // limit) + 1 if limit > 0 else 1
    has_more = (offset + len(entries)) < total_entries

    return LeaderboardResponse(
        leaderboard_type="session",
        entries=entries,
        total_entries=total_entries,
        limit=limit,
        offset=offset,
        current_page=current_page,
        has_more=has_more,
        user_rank=None,  # Would need user_id parameter to determine
        session_id=session_id,
    )
