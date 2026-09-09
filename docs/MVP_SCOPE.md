# Token Golf - MVP Scope & Clarifications

**Last Updated**: 2026-09-09

This document provides quick reference for all MVP scope decisions and clarifications.

## Quick Reference

### Core Concepts

| Concept | Definition |
|---------|------------|
| **Hole** | Individual challenge with specific task |
| **Course** | Collection of holes (predefined) |
| **Session** | A game on a specific course = competition = one round |
| **Score** | Total tokens used across all attempts for a hole |

### Sessions

- **Definition**: Session = Competition = Game on a course
- **Timeout**: 3 hours from creation (configurable in config file)
- **Timeout Behavior**: Marked as "DNF" (Did Not Finish)
- **Multiple Sessions**: Users can join multiple concurrent sessions
- **Resumption**: Players can pause and return within 3 hours
- **Timer**: Based on session creation time (not last activity)

### User Identity

- **MVP**: New auto-generated username each session
- **Format**: `{Color}-{GolfCourse}-{ClubNumber}` (e.g., "Blue-Augusta-7")
- **Authentication**: None for MVP (no passwords)
- **Future**: Optional password-based authentication to reclaim usernames

### Token Counting

- **What Counts**: Input + output tokens
- **System Tokens**: Treated as input tokens
- **Accumulation**: Running counter per hole AND per session
- **Failed Attempts**: All attempts count toward total
- **Retries**: No limit on retries (all count as additional strokes)

### LLM Integration

- **MVP Model**: Haiku only (hardcoded, no user choice)
- **Future**: Model selection based on challenge configuration flag
- **Backend**: Claude API (dev), OpenShift AI (production)
- **Token Counting**: Via LLM provider API (future: MLFlow for production)

### Error Handling

- **LLM API Errors**: Treated as "weather delay"
  - Only affected user's tokens cleared for that hole
  - User starts that specific hole over
  - Completed holes remain untouched
  - Other users unaffected

### User Modifications

- **Storage Granularity**: Per user per session per attempt
- **What's Stored**:
  - Prompt text
  - System prompt (if modified)
  - Context files (which active, any edits)
- **Edit Persistence**: Changes persist across attempts within same hole
- **Reset Behavior**: New hole = reset to challenge defaults

### Validation Types

| Type | MVP Status | Description |
|------|-----------|-------------|
| `test_cases` | ✅ **Included** | Run code against test inputs |
| `exact_match` | ✅ **Included** | String comparison (case-insensitive, trim whitespace) |
| `semantic_similarity` | ❌ **Excluded** | Embeddings-based matching |
| `pattern_match` | ❌ **Excluded** | Regex validation |
| `multiple_choice` | ❌ **Excluded** | Predefined options |
| `custom_script` | ❌ **Excluded** | Python validator scripts |

### Leaderboards

Three toggleable views:

| View | Scope | Description |
|------|-------|-------------|
| **Global** | All sessions | Scores across all sessions in current deployment |
| **Per-Hole** | All sessions | Best scores for individual challenges |
| **Session** | Current only | Scores for current session/competition |

**Display**: Top 10 players, current user highlighted, current leader shown per hole

### UI Elements

#### Pills UI
- **Technology**: Alpine.js
- **Actions**:
  - Click X to remove
  - Click pill to edit (modal or inline)
- **Visual**: Active/inactive state indication
- **NOT in MVP**: Drag-to-reorder

#### Metrics Panel (Right Side)
1. **Current User Stats**
   - Token count (current attempt)
   - Total tokens (all attempts this hole)
   - Number of attempts
   - Current rank
   - Status (In Progress / Completed)

2. **Leaderboard** (toggleable views)

3. **Statistical Distribution** (top right)
   - Current leader's name and score per hole
   - User's current place
   - Average tokens (all sessions)
   - Median tokens
   - Best score
   - Number of completions

### Challenge Files

- **Location**: `challenges/hole-XXX/challenge.yaml`
- **Assets**: `challenges/hole-XXX/assets/`
- **Course Definitions**: `challenges/courses.yaml`
- **Schema Validation**: Not in MVP (programmatic validation only)

### Configuration

Required config file fields:
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

## Database Schema Summary

### Tables (MVP)
1. `sessions` - Game sessions on courses
2. `users` - Player profiles
3. `session_participants` - Links users to sessions (many-to-many)
4. `challenges` - Challenge definitions
5. `attempts` - Every prompt attempt (includes session_id, system_prompt, context_files)
6. `scores` - Final scores per user per hole per session

### Key Relationships
- User can participate in multiple sessions (many-to-many)
- Session has multiple participants
- Each attempt belongs to one user, one session, one challenge
- Scores track total for user+session+challenge combination

## Features Excluded from MVP

**Will be added in future phases:**

1. **Skills/Agents**
   - Predefined skill files in `challenges/hole-XXX/assets/`
   - Loaded and included in prompt when active
   - Future: `.md` files with LLM-relevant content

2. **Model Selection**
   - Challenge files will have flag indicating allowed models
   - Users choose from allowed models
   - Different models for different challenge types

3. **Time Limits**
   - Per-hole time limits
   - Countdown timer in UI
   - Timeout = failure

4. **Hints System**
   - Progressive hints that cost tokens
   - "Spend 50 tokens for a hint?"
   - Tracked in scoring

5. **Persistent Authentication**
   - Username + password
   - Reclaim username across sessions
   - Profile/history tracking

6. **Advanced Validation**
   - Semantic similarity (embeddings)
   - Custom Python validator scripts
   - Pattern matching (regex)
   - Multiple choice

7. **Model Parameters UI**
   - Temperature, max tokens, top-p
   - If backend supports it
   - Per-attempt or per-challenge

8. **Offline Mode**
   - Download challenges
   - Play locally
   - Sync when online

9. **Pill Drag-to-Reorder**
   - Reorder context files
   - Visual priority indication

10. **Real-Time WebSockets**
    - Live leaderboard updates
    - Other players' progress
    - Spectator mode

11. **Max Iterations Enforcement**
    - Limit attempts per hole
    - Defined in challenge YAML
    - Not enforced in MVP

## Questions Resolved

| Question | Answer |
|----------|--------|
| Edit persistence within hole? | Yes, persist across attempts |
| Session timeout duration? | 3 hours (configurable) |
| Multiple concurrent sessions? | Yes, allowed |
| Authentication? | New username each session (MVP) |
| Model selection? | Haiku only, hardcoded (MVP) |
| Leaderboard scopes? | Global, Per-Hole, Session |
| LLM error handling? | "Weather delay" - affected user only |
| Validation types? | Test cases + exact match (MVP) |
| Storage granularity? | Per user per session per attempt |
| Tie-breaking? | Additional challenge (repeat as needed) |
| Schema.yaml needed? | No, not for MVP |
| System token counting? | Treat as input tokens |
| Retry limit? | No limit |

## Tie-Breaking

- **Applies to**: First place ties only
- **Process**: Tied players compete in additional challenge
- **Repeat**: Continue until single winner emerges
- **Challenge Source**: Placeholder to be created later
- **Other Ranks**: Remain unchanged during tie-breaker

See: `docs/ADRs/003-tie-breaking-mechanism.md`

## Development Priorities

### Must Have (MVP)
1. Session management system
2. Test cases validation
3. Exact match validation
4. Auto-generated usernames
5. Three leaderboard views
6. Context file pills UI
7. System prompt editing
8. Token counting & scoring
9. Session timeout handling
10. SQLite database with Alembic migrations

### Nice to Have (Post-MVP)
1. Skills/agents system
2. Additional validation types
3. Model selection
4. Persistent authentication
5. Real-time updates

### Future Enhancements
1. Offline mode
2. Advanced analytics
3. Team competitions
4. Replay mode
5. Export results

## References

- **Full Documentation**: `/docs/ARCHITECTURE.md`
- **Challenge Format**: `/docs/CHALLENGE_FORMAT.md`
- **ADRs**: `/docs/ADRs/`
- **Project Status**: `/PROJECT_STATUS.md`
- **Session Management ADR**: `/docs/ADRs/005-session-management-and-mvp-scope.md`
