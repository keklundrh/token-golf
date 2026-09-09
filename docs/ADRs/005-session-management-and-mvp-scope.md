# ADR 005: Session Management and MVP Scope

## Status

Accepted

## Context

Token Golf needs a clear session management strategy to handle multiple concurrent players and competition workflows. Additionally, we need to define MVP scope boundaries to ensure focused, timely delivery while maintaining extensibility for future features.

### Key Requirements
- Support multiple concurrent users at conferences
- Track user progress through challenges
- Maintain user context (prompts, files) across attempts
- Define clear competition/game boundaries
- Handle session timeouts gracefully
- Minimize authentication friction for demos
- Store granular data for analytics and debugging

### Constraints
- Conference demo environment (3-hour events)
- No persistent user accounts initially
- Simple, understandable game flow
- Accurate token tracking required

## Decision

### Session Structure
**A session = a competition = a game on a specific course (collection of holes).**

- Sessions are created with a specific course_id (which holes to play)
- Multiple users can join the same session (compete together)
- Users can participate in multiple concurrent sessions
- Each session has a configurable timeout (default 3 hours from creation)
- Sessions that timeout are marked "DNF" (Did Not Finish)

### Storage Granularity
**All user modifications are stored per user per session per attempt.**

User modifications include:
- Prompt text
- System prompt customizations
- Context files (which are active, edits made)

This is stored in the `attempts` table with fields:
- `prompt`: The user's prompt
- `system_prompt`: User's system prompt (if modified)
- `context_files`: JSON field tracking which files were active and any edits

### Edit Persistence Within a Hole
**Changes persist across attempts within the same hole.**

If a user removes a context file on attempt 1 of hole 3:
- Attempt 2 of hole 3: File remains removed
- Attempt 1 of hole 4: File reappears (new hole, reset to defaults)

This allows users to refine their approach without re-doing modifications each attempt.

### Authentication (MVP)
**No persistent authentication for MVP.**

- Each time a user starts a session, generate a new username
- Format: `{Color}-{GolfCourse}-{ClubNumber}` (e.g., "Blue-Augusta-7")
- No passwords, no account recovery
- Future: Add optional password-based authentication for username reclaim

### MVP Feature Boundaries

**INCLUDED in MVP:**
- Test cases validation (coding challenges)
- Exact match validation (text responses)
- Auto-generated usernames (new each session)
- Haiku model only (hardcoded)
- Three leaderboard views (Global, Per-Hole, Session)
- Session timeout (3 hours, configurable)
- Context file management (add/remove/edit via pills UI)
- System prompt editing
- Token counting and scoring
- SQLite database
- Claude API backend

**EXCLUDED from MVP:**
- Skills/agents (predefined skill files)
- Model selection by users
- Time limits per hole
- Hints system
- Persistent authentication with passwords
- Semantic similarity validation
- Custom validation scripts
- Model parameters modification UI
- Offline mode
- Pill drag-to-reorder functionality
- Real-time WebSocket updates
- Max iterations per hole enforcement

### Database Schema
New tables:
- `sessions`: Track game sessions with course, timeout, status
- `session_participants`: Link users to sessions (many-to-many)
- Modified `attempts`: Add session_id, system_prompt, context_files
- Modified `scores`: Add session_id

## Consequences

### Positive Consequences

**Session Management:**
- Clear game boundaries (session = one competition)
- Supports both individual play and group competitions
- Users can try multiple sessions without interference
- Timeout prevents abandoned sessions from accumulating
- Simple to explain ("It's like one round of golf")

**Storage Granularity:**
- Complete audit trail of every attempt
- Can replay user's exact strategy
- Analytics on prompt evolution
- Debug support (see exactly what user submitted)
- Fair scoring (no hidden modifications)

**Edit Persistence:**
- Better UX (don't lose your work between attempts)
- Encourages iterative refinement
- Reduces friction in gameplay
- Teaches optimization through iteration

**MVP Boundaries:**
- Clear scope prevents feature creep
- Faster time to first demo
- Validate core concept before investing in advanced features
- Simple codebase for initial implementation
- Foundation for future enhancements

### Negative Consequences

**Session Management:**
- More complex database schema
- Need cleanup job for expired sessions
- Can't prevent same person from joining same session multiple times (future: check IP or browser fingerprint)

**Storage Granularity:**
- Larger database (storing full context each attempt)
- More complex queries for analytics
- JSON field for context_files (less structured)

**Edit Persistence:**
- Potential confusion if user expects fresh start
- Need clear UI indication of what's currently active
- Can't easily "reset to defaults" mid-hole without manual re-adding

**MVP Limitations:**
- Some requested features deferred
- May need refactoring for post-MVP features
- Limited validation types in first version

### Risks

**Risk: Database size growth with per-attempt storage**
- Mitigation: Context files stored by reference (path), not duplicated. Archive old sessions after event.
- Likelihood: Low - conferences are time-limited events

**Risk: Users confused by edit persistence**
- Mitigation: Clear visual indicators of active pills, "reset" button for hole
- Likelihood: Medium - needs good UX design

**Risk: Session timeout too short/long**
- Mitigation: Make configurable, monitor actual usage patterns, adjust
- Likelihood: Medium - 3 hours is estimate, may need tuning

**Risk: MVP excludes features users want**
- Mitigation: Fast iteration after MVP, user feedback drives roadmap
- Likelihood: High - but acceptable for MVP validation

## Alternatives Considered

### Alternative 1: User-Scoped Sessions (No Multi-Player)
- **Description**: Each user has their own independent session, no shared leaderboards
- **Pros**: Simpler database, no need for session_participants table
- **Cons**: No competition aspect, defeats "conference competition" use case
- **Why not chosen**: Core use case is competitive conference events

### Alternative 2: Hole-Scoped Storage (Not Attempt-Scoped)
- **Description**: Store latest state per hole, not every attempt
- **Pros**: Smaller database, simpler queries
- **Cons**: Lose audit trail, can't analyze prompt evolution, harder to debug
- **Why not chosen**: Analytics value of per-attempt data is high

### Alternative 3: Fresh Start Each Attempt
- **Description**: Reset all pills/prompts to defaults on each attempt
- **Pros**: Simpler, no hidden state
- **Cons**: Frustrating UX, users re-do same modifications repeatedly
- **Why not chosen**: Poor user experience for iterative gameplay

### Alternative 4: Persistent Authentication from Start
- **Description**: Require login, persistent accounts
- **Pros**: Can track users across sessions, prevent duplicate entries
- **Cons**: Friction for demos, need password reset, email verification, etc.
- **Why not chosen**: Adds complexity that's unnecessary for MVP conference demos

### Alternative 5: Include All Validation Types in MVP
- **Description**: Build semantic similarity, custom scripts, pattern match immediately
- **Pros**: Full featured from day one
- **Cons**: Delays MVP, added complexity, semantic similarity needs embedding service
- **Why not chosen**: Test cases + exact match sufficient to validate concept

## Implementation Notes

### Database Migration
- Add `sessions` table
- Add `session_participants` table
- Modify `attempts` to include session_id, system_prompt, context_files
- Modify `scores` to include session_id
- Modify `users` to remove session_id (now in session_participants)

### Session Lifecycle
```python
def create_session(course_id: str, timeout_hours: int = 3) -> Session:
    """Create a new game session."""
    session = Session(
        id=generate_uuid(),
        course_id=course_id,
        timeout_hours=timeout_hours,
        status='active',
        expires_at=now() + timedelta(hours=timeout_hours)
    )
    return session

def check_session_timeout():
    """Background job: mark expired sessions as DNF."""
    expired = Session.query.filter(
        Session.expires_at < now(),
        Session.status == 'active'
    ).all()
    for session in expired:
        session.status = 'dnf'
```

### Configuration File
Create `config.yaml`:
```yaml
game:
  session_timeout_hours: 3
  model: haiku
  
llm:
  provider: claude  # or openshift_ai
  api_key: ${CLAUDE_API_KEY}
  
database:
  url: sqlite:///./token_golf.db
```

## References

- ADR 003: Tie-Breaking Mechanism (related to session competition flow)
- ADR 004: Database Migrations with Alembic (migration strategy)
- Conference demo requirements discussion (internal notes)

---

**Date**: 2026-09-09  
**Author**: Token Golf Team  
**Reviewers**: Karl Eklund
