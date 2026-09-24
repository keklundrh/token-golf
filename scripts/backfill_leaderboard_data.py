#!/usr/bin/env python3
"""
Backfill script for leaderboard completion tracking.

This script populates the new columns added in migration 2e1ac852f393:
- sessions.course_total_holes (from courses.yaml)
- session_participants.holes_completed (from Score records)
- session_participants.course_completed_at (when all holes completed)

Run this after running: alembic upgrade head
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
import yaml

from app.database import async_session_factory
from app.models import Session, SessionParticipant, Score, Challenge


async def backfill_course_total_holes(db: AsyncSession):
    """
    Backfill sessions.course_total_holes from courses.yaml.
    """
    print("📊 Backfilling sessions.course_total_holes...")

    # Load courses.yaml
    courses_path = project_root / "challenges" / "courses.yaml"
    with open(courses_path, 'r') as f:
        courses_data = yaml.safe_load(f)

    # Build mapping: course_id -> total_holes
    course_holes = {}
    for course in courses_data.get('courses', []):
        course_id = course['id']
        hole_count = len(course['holes'])
        course_holes[course_id] = hole_count

    print(f"   Loaded {len(course_holes)} courses from courses.yaml")

    # Update sessions
    result = await db.execute(select(Session))
    sessions = result.scalars().all()

    updated = 0
    for session in sessions:
        total_holes = course_holes.get(session.course_id, 5)  # Default to 5
        if session.course_total_holes != total_holes:
            session.course_total_holes = total_holes
            updated += 1

    await db.commit()
    print(f"   ✅ Updated {updated}/{len(sessions)} sessions")


async def backfill_participant_completion(db: AsyncSession):
    """
    Backfill session_participants.holes_completed and course_completed_at.
    """
    print("\n📊 Backfilling session_participants completion tracking...")

    # Get all participants
    result = await db.execute(select(SessionParticipant))
    participants = result.scalars().all()

    print(f"   Processing {len(participants)} participants...")

    updated = 0
    for participant in participants:
        # Count completed challenges for this user in this session
        stmt = select(func.count(Score.id), func.max(Score.completed_at)).where(
            Score.user_id == participant.user_id,
            Score.session_id == participant.session_id,
            Score.completed_at.is_not(None),
        )
        result = await db.execute(stmt)
        completed_count, latest_completion = result.one()

        # Get course total holes for this session
        session_stmt = select(Session.course_total_holes).where(
            Session.id == participant.session_id
        )
        result = await db.execute(session_stmt)
        course_total = result.scalar_one()

        # Update participant
        if participant.holes_completed != completed_count:
            participant.holes_completed = completed_count
            updated += 1

        # Set course_completed_at if user finished all holes
        if completed_count == course_total and not participant.course_completed_at:
            participant.course_completed_at = latest_completion
            print(f"   ✅ User {participant.user_id} completed course in session {participant.session_id[:8]}... ({completed_count}/{course_total} holes)")
            updated += 1

    await db.commit()
    print(f"   ✅ Updated {updated}/{len(participants)} participants")


async def verify_backfill(db: AsyncSession):
    """
    Verify the backfill was successful.
    """
    print("\n🔍 Verifying backfill...")

    # Check sessions
    stmt = select(func.count(Session.id)).where(Session.course_total_holes == 5)
    result = await db.execute(stmt)
    sessions_with_5_holes = result.scalar_one()
    print(f"   Sessions with 5 holes (full-tour): {sessions_with_5_holes}")

    # Check participants with completed courses
    stmt = select(func.count(SessionParticipant.id)).where(
        SessionParticipant.course_completed_at.is_not(None)
    )
    result = await db.execute(stmt)
    completed_participants = result.scalar_one()
    print(f"   Participants who completed full course: {completed_participants}")

    # Check participants with partial completion
    stmt = select(
        SessionParticipant.holes_completed,
        func.count(SessionParticipant.id).label('count')
    ).group_by(SessionParticipant.holes_completed).order_by(SessionParticipant.holes_completed)
    result = await db.execute(stmt)

    print("\n   Holes completed distribution:")
    for holes, count in result.all():
        print(f"     {holes} holes: {count} participants")

    print("\n   ✅ Backfill verification complete!")


async def main():
    """
    Main backfill execution.
    """
    print("🚀 Starting leaderboard data backfill...\n")

    # Get database session
    async with async_session_factory() as db:
        try:
            await backfill_course_total_holes(db)
            await backfill_participant_completion(db)
            await verify_backfill(db)

            print("\n✅ Backfill complete!")

        except Exception as e:
            print(f"\n❌ Error during backfill: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
