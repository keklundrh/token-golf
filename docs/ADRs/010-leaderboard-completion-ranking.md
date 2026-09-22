# ADR 010: Leaderboard Completion-Based Ranking

**Date**: 2026-09-22  
**Status**: ✅ Implemented  
**Deciders**: Development Team  
**Context**: Leaderboard ranking fix based on professional golf conventions

---

## Context and Problem Statement

The original leaderboard implementation ranked all players by total tokens ascending, regardless of completion status. This created an unfair ranking where users who abandoned the game after 1-2 holes appeared at the top of the leaderboard simply because they had fewer total tokens.

**Problem Example**:
```
Rank  Player              Tokens  Holes Completed
1.    Green-Oakmont-7        15        1  ← ABANDONED!
2.    Pink-Augusta-2         26        1  ← ABANDONED!
8.    Pink-Merion-13         85        2  ← Actually played more!
```

This violated the fundamental golf principle: **you can't win by quitting early**.

---

## Research & Analysis

### Professional Golf Conventions

Research into [PGA scoring](https://primetopgolf.com/pga-golf-scoring/), [golf leaderboards](https://www.livetourney.com/blog/golf-scoreboard-explained), and [tournament scoring](https://www.livetourney.com/blog/golf-tournament-scoring) revealed:

1. **Completion-First Ranking**: Players are ranked by holes completed, THEN by score
2. **WD/DNF Status**: Withdrawn/Did Not Finish players shown separately with status markers, NOT ranked
3. **"Thru" Column**: Shows progress (e.g., "14" = completed 14 holes, "F" = finished)
4. **Ties Display**: "T" prefix for ties (e.g., "T3" for tied 3rd)
5. **Par Display**: Score relative to par (-8, +3, E)

---

## Decision

Implement **completion-first ranking** across all three leaderboard types, following golf conventions while keeping the system accessible to non-golfers.

### Core Ranking Logic

**Sort Order**:
1. **Holes completed** (descending) - more holes = higher rank
2. **Total tokens** (ascending) - fewer tokens = better
3. **Completion time** (ascending) - tiebreaker

### Three Leaderboard Types

#### 1. Global Leaderboard (Hall of Fame)
- **Show**: ONLY users who completed ALL holes (full course)
- **Sort**: By total tokens ascending (lowest wins)
- **Purpose**: Best complete performances ever
- **DNF Handling**: Exclude entirely

#### 2. Session Leaderboard (Live Competition)
**Two-Section Display**:
- **Top Section - "Completed"** (finished all holes)
  - Ranked 1, 2, 3... by total tokens
  - Status badge: **F** (Finished)
- **Divider Line** - Clear visual separator
- **Bottom Section - "In Progress"** OR "DNF"
  - Ranked by holes completed, then tokens
  - Display as "--" rank (not numbered)
  - Status badges: **IP** (In Progress), **DNF** (Did Not Finish)

#### 3. Per-Hole Leaderboard
- **No changes** - already filters to `completed_at IS NOT NULL`
- Shows only players who completed that specific hole

### Visual Elements

**Display Format**:
```
Rank | Player              | Status | Holes | Progress | Tokens
-----|---------------------|--------|-------|----------|-------
1    | Blue-Augusta-7      | F      | 5/5   | ●●●●●    | 1,245
T2   | Red-Pebble-3        | F      | 5/5   | ●●●●●    | 1,389
T2   | Green-StAndrews-9   | F      | 5/5   | ●●●●●    | 1,389
4    | Yellow-Oakmont-2    | IP     | 4/5   | ●●●●○    | 1,102
---- | ------------------- | ------ | ----- | -------- | ------
--   | Orange-Cypress-1    | DNF    | 2/5   | ●●○○○    |   543
```

**Status Codes**:
- **F** = Finished (all holes)
- **IP** = In Progress (session active)
- **DNF** = Did Not Finish (timed out)

---

## Implementation

### Database Changes (Migration 2e1ac852f393)

**Added to `sessions` table**:
```sql
ALTER TABLE sessions ADD COLUMN course_total_holes INTEGER NOT NULL DEFAULT 5;
```

**Added to `session_participants` table**:
```sql
ALTER TABLE session_participants 
ADD COLUMN holes_completed INTEGER NOT NULL DEFAULT 0,
ADD COLUMN course_completed_at TIMESTAMP NULL;
```

**Added index**:
```sql
CREATE INDEX ix_session_participants_completion 
ON session_participants(session_id, holes_completed, course_completed_at);
```

### Service Layer Changes

**ScoringService** (`app/services/scoring.py`):
- Added `_check_course_completion()` method
- Called from `_update_score()` after setting `Score.completed_at`
- Updates `SessionParticipant.holes_completed` and `course_completed_at`

**Updated Queries**:

1. **Global Leaderboard**:
   - Join with `SessionParticipant`
   - Filter: `course_completed_at IS NOT NULL`
   - Exclude DNF sessions: `Session.status != 'dnf'`
   - Show each user's best (minimum) total across all completed courses

2. **Session Leaderboard**:
   - Returns `dict` with `"completed"` and `"in_progress"` arrays
   - Completed: `holes_completed == course_total_holes`, sorted by tokens
   - In Progress: `holes_completed < course_total_holes`, sorted by holes desc, tokens asc

3. **Per-Hole Leaderboard**: No changes (already correct)

### Frontend Changes

**New Templates**:
- `app/templates/partials/leaderboard_global.html`
- `app/templates/partials/leaderboard_session.html`

**New Routes** (`app/main.py`):
- `/htmx/leaderboard/global` - HTML partial for htmx
- `/htmx/leaderboard/session/{session_id}` - HTML partial for htmx

**Updated**:
- `app/templates/leaderboard.html` - Points to new htmx routes
- `app/templates/game.html` - Shows holes completed (X/5 format)

---

## Consequences

### Positive

✅ **Fair Competition**: Can't win by quitting early  
✅ **Golf Authentic**: Matches professional golf conventions  
✅ **Clear Progress**: Visual indicators (●●●○○) show completion  
✅ **Accessible**: No golf knowledge required to understand  
✅ **Motivating**: Encourages players to complete all holes  
✅ **Transparent**: Incomplete players still visible, just not ranked  

### Neutral

🔄 **Two-Section Leaderboard**: Session view more complex but clearer  
🔄 **Database Denormalization**: `course_total_holes` stored in sessions for performance  

### Negative

⚠️ **Breaking Change**: Global leaderboard may show fewer players (only completers)  
⚠️ **Empty Global**: If no one completed full course, global leaderboard is empty  

---

## Migration Notes

**Backfill Script**: `scripts/backfill_leaderboard_data.py`
- Populated `sessions.course_total_holes` from `courses.yaml`
- Calculated `session_participants.holes_completed` from `Score` records
- Set `course_completed_at` for users who finished all holes

**Existing Data**: 38 sessions on "beginner-course" (2 holes) were correctly backfilled.

---

## Alternatives Considered

### Option A: Show All Players, Sort by Completion
**Rejected**: Creates confusing single list where partial players are mixed with completers

### Option B: Only Show Completers Everywhere
**Rejected**: Too harsh - hides in-progress players from session view

### Option C: Use Weighted Scoring (tokens/holes)
**Rejected**: Unfairly penalizes longer courses, not golf-authentic

---

## References

- [PGA Golf Scoring](https://primetopgolf.com/pga-golf-scoring/)
- [Golf Leaderboard Explained](https://www.livetourney.com/blog/golf-scoreboard-explained)
- [Golf Tournament Scoring Guide](https://www.livetourney.com/blog/golf-tournament-scoring)
- [What Does WD Mean in Golf?](https://www.livetourney.com/blog/what-does-wd-mean-in-golf)
- Research agents: `leaderboard_fix_spec.md` (technical spec)

---

## Related ADRs

- ADR 003: Tie-Breaking Mechanism (still applies for final standings)
- ADR 005: Session Management and MVP Scope (timeout behavior)

---

## Follow-Up Actions

- [ ] User acceptance testing with browser
- [ ] Update user-facing help text to explain status codes
- [ ] Consider adding "Resume" button for abandoned sessions
- [ ] Analytics on completion rates
