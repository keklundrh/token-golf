# Current Game Configuration

**Last Updated**: 2026-09-22 (Phase 8 Part 1.5)

## Course Configuration

### Active Mode
**Single Course Mode** - All game sessions use one predefined course.

### Current Course
**ID**: `full-tour`  
**Name**: "Complete Championship"  
**Description**: "All holes in sequence. The ultimate test of token efficiency across all challenge types."  
**Difficulty**: Expert  
**Estimated Duration**: 150 minutes  
**Par Total**: 750 tokens

### Holes (Challenges)

| Order | Challenge ID | Name | Difficulty | Par | Task Type | Validation |
|-------|-------------|------|------------|-----|-----------|------------|
| 1 | hole-001 | Hello World | Easy | 50 | Generation | Exact Match |
| 2 | hole-002 | Addition Function | Easy | 100 | Coding | Test Cases |
| 3 | hole-003 | String Reversal | Medium | 150 | Coding | Test Cases |
| 4 | hole-004 | Email Extraction | Medium | 150 | Extraction | Exact Match |
| 5 | hole-005 | FizzBuzz | Hard | 300 | Coding | Test Cases |

**Total Holes**: 5  
**Total Par**: 750 tokens

## Course Selection

### Implementation
Hardcoded in `app/templates/index.html`:
- **Line 92**: New game flow - `"course_id": "full-tour"`
- **Line 194**: Sign-in flow - `"course_id": "full-tour"`

### Previous Configuration
- **Before Phase 8 Part 1.5**: Hardcoded to `"beginner-course"` (2 holes)
- **Beginner Course Holes**: hole-001, hole-002
- **Beginner Course Par**: 150 tokens (50 + 100)

### Available Courses (Defined but Not Used)

The following courses are defined in `challenges/courses.yaml` but not currently selectable:

1. **beginner-course** - "Beginner's Green" (2 holes, par 300)
2. **intermediate-course** - "Challenge Valley" (3 holes, par 450)
3. **advanced-course** - "Expert's Peak" (3 holes, par 600)
4. **full-tour** - "Complete Championship" (5 holes, par 750) ← **ACTIVE**

### Future Plans
Course selection UI will be re-enabled when:
- Additional challenges are created (Phase 8 Part 2)
- Each course has at least 5-10 unique challenges
- Multiple difficulty tiers are well-represented

## Scoring Configuration

### Rank Calculation
**Method**: Compare player against others with **same number of completed holes**

**Format**: "X/Y" where:
- X = Player's rank (1 = best)
- Y = Total players at same progress level

**Sorting**: By total_tokens ascending (lower is better)

**Display**: Shows "-" until at least 1 hole completed

### Par Comparison
**Terms Used**:
- Eagle: -2 or better
- Birdie: -1
- Par: Exactly 0 (at par)
- Bogey: +1
- Double Bogey: +2
- "+X Over Par": More than +2

**Display Location**: 
- Individual hole: In validation success banner
- Cumulative: "vs Par (All Holes)" in Player Stats (blue box)

### Success Messages
**Varies by attempt number**:
1. Attempt 1: "⛳ Hole in One!"
2. Attempt 2: "⛳ Nice Shot!"
3. Attempt 3: "⛳ Well Done!"
4. Attempt 4+: "⛳ Success!"

## UI Configuration

### Navigation
- **Home Button**: Always visible in top navigation bar
- **Prev/Next**: Navigate between holes
- **Progress Bar**: Shows "Hole X of Y" with % complete

### Stats Panels

#### Player Stats (Blue Gradient Box)
**Shows**: Cumulative session data
- Rank (among same-progress players)
- Attempts (total across all holes)
- Total Tokens (sum across all holes)
- vs Par (All Holes) - only shows after completing 1+ holes

#### Challenge Stats (White Box)
**Shows**: Current challenge data (all players)
- Best Score (lowest tokens for this challenge)
- Average (mean tokens across all completions)
- Total Attempts (all attempts by all users)

#### Top 5 Leaderboard
**Shows**: Top 5 scores for current challenge
- Sorted by total_tokens ascending
- Highlights current user with ⭐
- Medal indicators for top 3

### Completion Modal
**On Last Hole**:
- Left button: "View Leaderboard"
- Right button: "New Course" (green, navigates to home)

**On Other Holes**:
- Left button: "Leaderboard"
- Right button: "Next Hole" (gold)

## API Configuration

### Session Creation
**Endpoint**: `POST /api/game/start`

**Payload**:
```json
{
  "action": "generate",  // or "signin"
  "course_id": "full-tour"
}
```

**Response** (201):
```json
{
  "session_id": "uuid",
  "username": "Color-Course-Number",
  "password": "generated-password",
  "course_id": "full-tour",
  "message": "Welcome! Your course has 5 holes."
}
```

### Game Status
**Endpoint**: `GET /api/game/status/{session_id}`

**Response**:
```json
{
  "session_id": "uuid",
  "user_id": 123,
  "username": "Pink-Merion-13",
  "course_id": "full-tour",
  "session_status": "active",
  "challenges": [
    {
      "id": "hole-001",
      "name": "Hello World",
      "completed": true,
      "attempts": 2,
      "tokens": 85
    }
  ],
  "current_challenge_id": "hole-002",
  "total_tokens": 85,
  "completed_challenges": 1,
  "rank": "1/3"
}
```

## Database Configuration

### Session Record
```sql
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    course_id TEXT NOT NULL,  -- Always "full-tour" currently
    created_at TIMESTAMP,
    timeout_hours INTEGER DEFAULT 3,
    status TEXT DEFAULT 'active',
    expires_at TIMESTAMP
)
```

## Environment Configuration

### Log Level
**Setting**: `LOG_LEVEL=warning` in `.env`

**Rationale**: Reduce console spam from SQLAlchemy query logging

### Database
**Development**: SQLite (`sqlite+aiosqlite:///./data/token_golf.db`)  
**Production**: PostgreSQL (not yet configured)

## Testing Configuration

### Test Suite
- **Pytest Tests**: 213 tests
- **Browser Tests**: 22 tests
- **UI Validation**: 113 tests
- **Total**: 348 automated tests

### Coverage
- **Overall**: 74%
- **Services**: 91%
- **APIs**: 57%

## See Also

- `challenges/courses.yaml` - Course definitions
- `app/templates/index.html` - Course selection (hardcoded)
- `app/templates/game.html` - Game UI and stats
- `docs/phases/PHASE_8_PART_1.5_BUG_FIXES_AND_ENHANCEMENTS.md` - Recent changes
