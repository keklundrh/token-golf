# Technical Specification: Leaderboard Ranking Fix

## Problem Statement

The current Global and Session leaderboards rank players by total tokens without considering completion status. This produces unfair rankings where users who completed 1 hole (e.g., 100 tokens) rank above users who completed 5 holes (e.g., 600 tokens). Golf scoring only makes sense when comparing players who've played the same number of holes.

## Database Schema Changes

### 1. Add Course Metadata to Sessions Table

Add a denormalized column to track the total number of holes in the course:

```sql
ALTER TABLE sessions 
ADD COLUMN course_total_holes INTEGER NOT NULL DEFAULT 5;
```

**Rationale**: While course definitions live in `courses.yaml`, denormalizing this value prevents expensive YAML parsing on every leaderboard query. This value is static per course and won't change after session creation.

**Migration Strategy**: Backfill existing sessions by parsing their `course_id` from `courses.yaml`. Default to 5 (full-tour course).

### 2. Add Completion Tracking to SessionParticipant Table

Add columns to track user progress within a session:

```sql
ALTER TABLE session_participants 
ADD COLUMN holes_completed INTEGER NOT NULL DEFAULT 0,
ADD COLUMN course_completed_at TIMESTAMP NULL;
```

**Fields**:
- `holes_completed`: Running count of challenges completed by this user in this session
- `course_completed_at`: Timestamp when user finished all holes (NULL if incomplete)

**Update Logic**: Increment `holes_completed` each time `Score.completed_at` is set for a new challenge. Set `course_completed_at` when `holes_completed = Sessions.course_total_holes`.

### 3. Add Index for Leaderboard Queries

```sql
CREATE INDEX ix_session_participants_completion 
ON session_participants(session_id, holes_completed, course_completed_at);
```

**Rationale**: Optimizes filtering for completed vs in-progress users in leaderboard queries.

## Query Logic Changes

### 1. Global Leaderboard (`get_global_leaderboard`)

**New Logic**: Show each user's best completed course performance across all sessions.

**SQL Changes**:
```python
# Step 1: Find each user's best (minimum) total_tokens for completed courses
# A course is completed when holes_completed = course_total_holes

stmt = (
    select(
        Score.user_id,
        User.username,
        Score.session_id,
        func.sum(Score.total_tokens).label("session_total_tokens"),
        SessionParticipant.course_completed_at,
    )
    .join(User, User.id == Score.user_id)
    .join(SessionParticipant, 
          (SessionParticipant.user_id == Score.user_id) & 
          (SessionParticipant.session_id == Score.session_id))
    .join(Session, Session.id == Score.session_id)
    .where(
        # Only completed courses
        SessionParticipant.course_completed_at.is_not(None),
        # Exclude DNF sessions
        Session.status != 'dnf',
    )
    .group_by(Score.user_id, User.username, Score.session_id, 
              SessionParticipant.course_completed_at)
)

# Step 2: For each user, take their minimum session_total_tokens
subq = stmt.subquery()
final_stmt = (
    select(
        subq.c.user_id,
        subq.c.username,
        func.min(subq.c.session_total_tokens).label("best_score"),
        func.min(subq.c.course_completed_at).label("first_completion"),
    )
    .group_by(subq.c.user_id, subq.c.username)
    .order_by(func.min(subq.c.session_total_tokens).asc())
    .limit(limit)
)
```

**Returns**: Only users who completed at least one full course, ranked by their best (lowest) total.

### 2. Session Leaderboard (`get_session_leaderboard`)

**Decision**: Show two separate sections - "Completed" and "In Progress".

**Option A (Recommended)**: Return completed and in-progress separately:

```python
async def get_session_leaderboard(
    self,
    session_id: str,
    limit: int = 10,
) -> dict:
    """
    Returns:
        {
            "completed": [...],  # Users who finished all holes
            "in_progress": [...] # Users still playing
        }
    """
    
    # Get course_total_holes for this session
    session_stmt = select(Session.course_total_holes).where(Session.id == session_id)
    result = await self.db.execute(session_stmt)
    course_total_holes = result.scalar_one()
    
    # Completed users
    completed_stmt = (
        select(
            Score.user_id,
            User.username,
            func.sum(Score.total_tokens).label("total_tokens"),
            SessionParticipant.holes_completed,
            SessionParticipant.course_completed_at,
        )
        .join(User, User.id == Score.user_id)
        .join(SessionParticipant, 
              (SessionParticipant.user_id == Score.user_id) & 
              (SessionParticipant.session_id == session_id))
        .where(
            Score.session_id == session_id,
            SessionParticipant.holes_completed == course_total_holes,
        )
        .group_by(Score.user_id, User.username, SessionParticipant.holes_completed,
                  SessionParticipant.course_completed_at)
        .order_by(func.sum(Score.total_tokens).asc())
        .limit(limit)
    )
    
    # In-progress users
    in_progress_stmt = (
        select(
            Score.user_id,
            User.username,
            func.sum(Score.total_tokens).label("total_tokens"),
            SessionParticipant.holes_completed,
        )
        .join(User, User.id == Score.user_id)
        .join(SessionParticipant, 
              (SessionParticipant.user_id == Score.user_id) & 
              (SessionParticipant.session_id == session_id))
        .where(
            Score.session_id == session_id,
            SessionParticipant.holes_completed < course_total_holes,
        )
        .group_by(Score.user_id, User.username, SessionParticipant.holes_completed)
        .order_by(SessionParticipant.holes_completed.desc(), 
                  func.sum(Score.total_tokens).asc())
        .limit(limit)
    )
    
    return {
        "completed": [...],
        "in_progress": [...]
    }
```

**Option B (Alternative)**: Show only completed, with separate endpoint for in-progress.

**Recommendation**: Option A - Users want to see both their ranking among finishers and their progress vs other in-progress players.

### 3. Per-Hole Leaderboard (`get_per_hole_leaderboard`)

**No changes needed**. Already filters to `Score.completed_at IS NOT NULL`, which correctly shows only users who completed that specific hole.

## Handling DNF Sessions

**Global Leaderboard**: Exclude sessions with `status = 'dnf'` (already specified in query above).

**Session Leaderboard**: 
- If viewing a DNF session, show a "DNF" status banner in UI
- Still show rankings (users may want to see their progress before timeout)
- Optionally exclude DNF sessions from global history

## Service Layer Changes

Update `ScoringService` in `/Users/keklund/projects/token-golf/app/services/scoring.py`:

1. **`_update_score` method**: After setting `Score.completed_at`, check if this completes the course and update `SessionParticipant`:

```python
# After line 243 in _update_score
if is_correct and score.completed_at is not None:
    # Check if this completes the course
    await self._check_course_completion(user_id, session_id)
```

2. **Add new method `_check_course_completion`**:

```python
async def _check_course_completion(
    self,
    user_id: int,
    session_id: str,
) -> bool:
    """
    Check if user completed all holes in session's course.
    Updates SessionParticipant.holes_completed and course_completed_at.
    """
    # Count completed challenges for this user in this session
    stmt = select(func.count(Score.id)).where(
        Score.user_id == user_id,
        Score.session_id == session_id,
        Score.completed_at.is_not(None),
    )
    result = await self.db.execute(stmt)
    completed_count = result.scalar_one()
    
    # Get course total holes
    session_stmt = select(Session.course_total_holes).where(Session.id == session_id)
    result = await self.db.execute(session_stmt)
    course_total = result.scalar_one()
    
    # Update SessionParticipant
    participant_stmt = select(SessionParticipant).where(
        SessionParticipant.user_id == user_id,
        SessionParticipant.session_id == session_id,
    )
    result = await self.db.execute(participant_stmt)
    participant = result.scalar_one_or_none()
    
    if participant:
        participant.holes_completed = completed_count
        if completed_count == course_total and not participant.course_completed_at:
            participant.course_completed_at = datetime.utcnow()
            logger.info(
                f"User {user_id} completed course in session {session_id} "
                f"with {completed_count}/{course_total} holes"
            )
        await self.db.commit()
        return completed_count == course_total
    
    return False
```

## Migration Checklist

1. **Alembic Migration**: Create migration adding new columns
2. **Backfill Sessions**: Parse `courses.yaml` to set `course_total_holes` for existing sessions
3. **Backfill Participants**: Calculate `holes_completed` and `course_completed_at` from existing `Score` records
4. **Update Service**: Add `_check_course_completion` logic
5. **Update Queries**: Modify `get_global_leaderboard` and `get_session_leaderboard`
6. **Update Templates**: Adjust UI to handle two-section session leaderboard
7. **Testing**: Verify rankings with partial vs complete players

## Impact Summary

- **Global Leaderboard**: Only shows users who completed at least one full course
- **Session Leaderboard**: Separates completed finishers from in-progress players
- **Per-Hole Leaderboard**: No change (already correct)
- **DNF Sessions**: Excluded from global rankings but still viewable per-session
- **Database**: Two new columns on existing tables, one new index
- **Performance**: Minimal impact - denormalization reduces query complexity
