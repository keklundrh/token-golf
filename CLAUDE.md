# Token Golf - AI Assistant Context

This file provides comprehensive context for AI assistants working on the Token Golf project.

## Project Overview

Token Golf is a competitive educational game that teaches AI users about token efficiency and optimization. Players compete to complete AI tasks using the fewest tokens possible, with golf-style scoring where fewer tokens = better performance.

### Target Deployment
- **Development**: Local laptop with Claude API backend
- **Production**: OpenShift with OpenShift AI Models as a Service

### Target Audience
Conference attendees at major tech conferences who need to learn how different dimensions (prompts, context, system instructions, model parameters) affect token consumption and LLM performance.

## Core Game Mechanics

### Scoring System (ADR 011: Practice Swings)
- **Practice Swings**: Players can take unlimited practice swings to test their prompts
  - Practice swings show LLM response, validation, and token count
  - Practice swings do NOT count toward leaderboard score
  - Saved to database for analytics but marked as `attempt_type='practice'`
- **Submitted Attempts**: Players submit their best attempts to record score
  - Only successful attempts can be submitted
  - Submitted attempts marked as `attempt_type='submitted'`
  - Only submitted attempts count toward leaderboard
- **Scoring Calculation**: Best (lowest tokens) submitted attempt per hole wins
- **Retry After Success**: Players can submit multiple times to improve their score
- **Winner**: Lowest total tokens across all submitted attempts on completed holes
- **Tie-breaking**: If multiple players tie for first place, they compete in an additional challenge until a single winner emerges (repeat as needed) - placeholder for tie-breaking challenge to be created later

**Historical Note**: Pre-ADR 011 (before 2026-09-23), every attempt counted ("all tokens count" golf-style scoring). This was changed to practice swings to encourage experimentation and better teach token optimization.

### Challenge Structure
- **Holes**: Individual challenges with specific tasks
- **Sessions**: A "game" on a specific course (collection of holes). Think of it as one round of golf.
- **Courses**: Predefined collections of holes (like golf courses) that define which challenges are included in a session
- **Difficulty Levels**: Configurable per hole and per course
- **Task Types**: coding, data extraction, question answering, text transformation
- Holes are ordered easy to hard within a session
- Players play independently and scores are aggregated into a common session for the course

### Session Management
- **Session Timeout**: 3 hours from session creation (configurable in config file)
- **Timeout Behavior**: Sessions that timeout are marked "DNF" (Did Not Finish)
- **Multiple Sessions**: Users can participate in multiple concurrent sessions
- **Session Resumption**: Players can pause mid-hole, close browser, and return within 3 hours to resume
- **Username**: Players can generate new credentials (auto-generated username + password) or sign in with existing username + password

### User Interaction Elements
Players can view these during gameplay:
- Pre-loaded context files (read-only display)
- System prompts (read-only display)
- **Note**: Skills/agents and model parameters are NOT in MVP (future features)
- **Phase 8 Update (2026-09-22)**: Pills UI (editable with X buttons) was replaced with clean read-only display for better UX

**Historical Note**: Earlier versions had editable pills UI where users could remove context files and modify system prompts. This was removed in Phase 8 Part 1 UI redesign as it created confusion and clutter.

### Validation
Each challenge must have clear, verifiable correct answers (MVP only includes first two):
- Test cases (for coding) - **MVP**
- Exact string matching - **MVP**
- Semantic similarity checks - **NOT in MVP**
- Custom validation scripts - **NOT in MVP**

## Technical Architecture

### Technology Stack

#### Backend
- **Framework**: FastAPI (Python)
  - Async support for scalability
- Modern, well-documented
  - OpenAPI spec generation
- **Database**: 
  - Local dev: SQLite
  - Production: PostgreSQL (migration via ADR)
- **LLM Integration**:
  - Local dev: Claude API
  - Production: OpenShift AI Models as a Service

#### Frontend
- **Rendering**: Server-side with htmx
  - Minimal JavaScript approach
  - No Node.js backend needed
- **Interactivity**: Alpine.js (15kb)
  - Pill UI (add/remove elements)
  - Local form state
  - Toggle visibility
- **Styling**: Tailwind CSS
  - Utility-first approach
  - Customizable design system
  - Production-optimized builds

#### Deployment
- Docker containers for OpenShift compatibility
- Designed for high availability and concurrency
- Multi-tenancy support for conference scenarios

### Design Principles

1. **Simplicity First**: Start simple, optimize later via ADRs
2. **Python-Centric**: Minimize JavaScript, Python for all backend logic
3. **Server-Side Rendering**: htmx for interactivity without SPA complexity
4. **Open Source**: All dependencies must be open source
5. **Modern & Common**: Use widely-adopted, well-maintained technologies
6. **Documentation-Driven**: All decisions recorded in markdown/ADRs

## Implementation Status

**For current project status, phase completion, and progress tracking, see [PROJECT_STATUS.md](PROJECT_STATUS.md)**

This file (CLAUDE.md) provides stable reference documentation for AI assistants. Implementation status changes frequently and is maintained separately.

## Target Directory Structure

```
token-golf/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Configuration management (Pydantic)
│   ├── database.py          # SQLAlchemy async session
│   ├── api/                 # REST API endpoints
│   │   ├── __init__.py
│   │   ├── challenges.py    # Challenge endpoints
│   │   ├── leaderboard.py   # Leaderboard endpoints
│   │   └── game.py          # Game session endpoints
│   ├── models/              # SQLAlchemy 2.0 models (6 files)
│   │   ├── __init__.py
│   │   ├── base.py          # Base class
│   │   ├── user.py          # User model
│   │   ├── session.py       # Session + SessionParticipant models
│   │   ├── challenge.py     # Challenge model
│   │   ├── attempt.py       # Attempt model
│   │   └── score.py         # Score model
│   ├── services/            # Business logic (4 services)
│   │   ├── __init__.py
│   │   ├── challenge_loader.py  # Challenge YAML parsing
│   │   ├── llm_client.py    # LLM API integration (Claude)
│   │   ├── validator.py     # Answer validation (test cases, exact match)
│   │   └── scoring.py       # Token counting & scoring
│   └── templates/           # Jinja2 templates
│       ├── base.html        # Base template with navigation
│       ├── index.html       # Home/lobby page
│       ├── game.html        # Game interface
│       └── leaderboard.html # Leaderboard page
├── alembic/                 # Database migrations
│   ├── env.py
│   ├── versions/
│   └── ...
├── challenges/              # Challenge content
│   ├── README.md            # Challenge authoring guide
│   ├── hole-001/
│   │   ├── challenge.yaml   # Challenge definition
│   │   └── assets/          # Context files, test data
│   └── courses.yaml         # Course definitions
├── docs/                    # Project documentation
│   ├── ADRs/                # Architecture Decision Records
│   ├── phases/              # Phase completion docs
│   ├── sessions/            # Session-specific implementation notes (dated)
│   ├── ARCHITECTURE.md
│   ├── CHALLENGE_FORMAT.md
│   └── API.md               # API documentation
├── static/                  # Frontend assets
│   └── css/
│       ├── input.css        # Tailwind directives
│       └── output.css       # Generated CSS
├── tests/                   # Test suite
│   ├── unit/
│   ├── integration/
│   └── challenges/
├── .env.example             # Environment variables template
├── .gitignore
├── alembic.ini              # Alembic configuration
├── scripts/                 # Utility scripts
│   └── rebuild-css.sh       # Rebuild Tailwind CSS
├── CLAUDE.md                # This file
├── CONTRIBUTING.md          # Developer guidelines
├── docker-compose.yml       # Local development
├── Dockerfile               # Container definition
├── package.json             # Tailwind CSS dependency
├── tailwind.config.js       # Tailwind configuration
├── PROJECT_STATUS.md        # Current status (see this for implementation progress)
├── README.md                # Project overview
└── requirements.txt         # Python dependencies
```

## User Identity System

### Name Generation & Authentication
Auto-generated usernames ensure professional, family-friendly identifiers:
- Format: `{Color}-{GolfCourse}-{ClubNumber}`
- Example: `Blue-Pebblebeach-7`, `Green-Augusta-3`
- Components:
  - Colors: Standard golf-appropriate colors
  - Courses: Famous golf course names (Augusta, Pebblebeach, StAndrews, etc.)
  - Clubs: 1-14 (standard golf club numbers)
- Validation: Filter inappropriate combinations
- **Authentication Options**:
  - **Generate New**: Auto-generate username + password
  - **Sign In**: Use existing username + password
- **Password Storage**: SHA256 hashed (MVP implementation - production should use bcrypt/argon2)

## UI Layout Specification

### Overall Layout
```
┌─────────────────────────────┬────────────────────────────┐
│                             │                            │
│  Problem Statement          │                            │
│  (Top Left)                 │                            │
│  - Challenge description    │                            │
│  - Task requirements        │                            │
│  - Success criteria         │    Metrics & Results       │
│                             │    (Whole Right Side)      │
├─────────────────────────────┤                            │
│                             │    - Current Stats         │
│  Interaction Area           │    - Leaderboard           │
│  (Bottom Left)              │    - Comparison Data       │
│                             │    - Statistical Dist.     │
│  ┌───────────────────────┐  │                            │
│  │ Chat Interface        │  │                            │
│  │                       │  │                            │
│  ├───────────────────────┤  │                            │
│  │ Context Pills:        │  │                            │
│  │ [context.csv X]       │  │                            │
│  │ [system.txt X]        │  │                            │
│  │                       │  │                            │
│  └───────────────────────┘  │                            │
│                             │                            │
└─────────────────────────────┴────────────────────────────┘
```

### Metrics Panel Components

1. **Current User Stats**
   - Token count (current attempt)
   - Total tokens (all attempts this hole)
   - Number of attempts
   - Current rank on this hole
   - Status: In Progress / Completed

2. **Leaderboard Display**
   - Toggle: Global / Per-Hole / Session
     - **Global**: Scores across all sessions in current deployment (historically)
     - **Per-Hole**: Best scores for individual challenges across all sessions
     - **Session**: Scores for current session only
   - Top 10 players
   - Highlight current user
   - Shows current leader's name and score for each challenge/hole
   - Real-time updates (future enhancement, not MVP)

3. **Comparison Data**
   - User's last attempt vs current
   - User's score vs average
   - Improvement indicators
   - User's current place in leaderboard

4. **Statistical Distribution**
   - Displayed in top right corner alongside user's place
   - Shows current leader's name and score for each challenge/hole
   - Average tokens for this hole (across all sessions)
   - Median tokens
   - Best score
   - Number of completions
   - Histogram/distribution graph (calculated real-time or cached as needed)

### Pills UI
- Alpine.js driven
- Click X to remove element
- Click pill to edit/configure (modal or inline)
- Visual indication of active/inactive state
- **Note**: Drag-to-reorder is NOT in MVP (future enhancement)

## Challenge Format

Challenges are defined in YAML files located in `/challenges/hole-XXX/challenge.yaml`.

### Basic Structure
```yaml
id: hole-001
name: "Challenge Display Name"
difficulty: easy  # easy, medium, hard, expert
description: |
  Multi-line description of the task.
  What the player needs to accomplish.
  
task_type: coding  # coding, extraction, question_answering, generation

validation:
  type: test_cases  # MVP: test_cases, exact_match only
  criteria:
    - input: [1, 2, 3]
      expected_output: 6
    - input: [10, 20]
      expected_output: 30

context_files:
  - name: "example_data.csv"
    path: "./challenges/hole-001/assets/example_data.csv"
    description: "Sample data for testing"
    removable: true
    editable: false
    
system_prompt:
  default: "You are a helpful coding assistant."
  removable: false
  editable: true

parameters:
  max_iterations: 10          # Optional limit
  hints_available: 2          # Number of hints (future)
  time_limit_seconds: null    # Optional time limit

metadata:
  author: "Token Golf Team"
  created_date: "2026-09-09"
  tags: ["python", "basics", "functions"]
  estimated_tokens_expert: 150
  estimated_tokens_beginner: 800
```

See `docs/CHALLENGE_FORMAT.md` for complete specification.

## Development Workflow

### Git Flow
- **main**: Production-ready releases only
- **dev**: Integration branch for all features
- **feature/\***: Feature branches off dev
- **hotfix/\***: Emergency fixes off main

### Branching Rules
1. All new work starts from `dev`
2. Create feature branch: `git checkout -b feature/name dev`
3. Commit regularly with clear messages
4. Merge back to `dev` via PR
5. Tag releases on `main`

### Documentation Requirements
1. **ADRs**: All architectural decisions
2. **API Changes**: Update docs/API.md
3. **Challenge Changes**: Update schema and examples
4. **Code Comments**: Minimal - code should be self-documenting
5. **Commit Messages**: Clear, descriptive, reference issues

### Testing Strategy
1. Unit tests for all services
2. Integration tests for API endpoints
3. Challenge validation tests (ensure challenges are solvable)
4. Load testing for conference scenarios (future)

## Database Schema (Initial)

### Sessions Table
```sql
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,              -- UUID or similar
    course_id TEXT NOT NULL,          -- Which set of holes (currently: "full-tour" - 5 holes)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    timeout_hours INTEGER DEFAULT 3,  -- Configurable, default 3 hours
    status TEXT DEFAULT 'active',     -- 'active', 'completed', 'dnf'
    expires_at TIMESTAMP              -- created_at + timeout_hours
);
```

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

### Session Participants Table
```sql
CREATE TABLE session_participants (
    id INTEGER PRIMARY KEY,
    session_id TEXT REFERENCES sessions(id),
    user_id INTEGER REFERENCES users(id),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, user_id)
);
```

### Challenges Table
```sql
CREATE TABLE challenges (
    id TEXT PRIMARY KEY,  -- hole-001, etc.
    name TEXT NOT NULL,
    difficulty TEXT,
    task_type TEXT,
    config_yaml TEXT,  -- Full YAML content
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Attempts Table
```sql
CREATE TABLE attempts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    session_id TEXT REFERENCES sessions(id),
    challenge_id TEXT REFERENCES challenges(id),
    attempt_number INTEGER,
    prompt TEXT,
    system_prompt TEXT,               -- User's system prompt for this attempt
    context_files JSON,                -- Which context files were active
    response TEXT,
    input_tokens INTEGER,
    output_tokens INTEGER,
    total_tokens INTEGER,
    is_correct BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Note on storage granularity**: System prompts, context files, and other user modifications are stored per user per session per attempt in the attempts table.

### Scores Table
```sql
CREATE TABLE scores (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    session_id TEXT REFERENCES sessions(id),
    challenge_id TEXT REFERENCES challenges(id),
    total_attempts INTEGER,
    total_tokens INTEGER,              -- Running total for this hole
    completed_at TIMESTAMP,
    UNIQUE(user_id, session_id, challenge_id)
);
```

## LLM Integration

### Token Counting
- Use LLM provider's token counting API (for MVP, may use MLFlow for production)
- Track separately: input tokens, output tokens
- System tokens are treated as input tokens
- Store all token counts in database for analysis
- Tokens accumulate: running counter per hole and per session

### Model Selection
- **MVP**: Haiku only (hardcoded, no user choice)
- **Future**: Challenge files will have a flag to indicate which models are allowed
- **After MVP**: Players can choose models based on challenge configuration

### Error Handling
- **LLM API Errors**: Treated as "weather delay"
  - Only the user who encountered the error is affected
  - Clear the token count for that specific hole for that user
  - User starts the hole over
  - Completed holes remain untouched
  - Other users' progress is not affected

### API Abstraction
Create service layer to abstract LLM provider:
```python
class LLMClient:
    def __init__(self, provider: str, api_key: str):
        pass
    
    def complete(self, prompt: str, system: str, **kwargs) -> LLMResponse:
        """Send completion request, return response with token counts"""
        pass
```

This allows swapping Claude API → OpenShift AI with minimal code changes.

## Future Considerations

### Scalability
- WebSocket support for real-time updates
- Redis for session management
- Horizontal scaling with load balancer
- Database connection pooling

### Features
- Hints system (costs tokens)
- Team competitions
- Challenge difficulty adaptation
- Replay/review mode
- Export competition results

### Analytics
- Token usage patterns
- Common mistakes per challenge
- Difficulty calibration data
- User learning curves

## Common Development Commands

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8000

# Run tests
pytest tests/

# Format code
black app/ tests/
isort app/ tests/

# Lint
flake8 app/ tests/
mypy app/

# Database migrations (future)
alembic upgrade head

# Create new challenge
python scripts/new_challenge.py --id hole-042 --name "Challenge Name"

# Validate all challenges
python scripts/validate_challenges.py
```

## MVP Scope

### Features INCLUDED in MVP
- Test cases validation (for coding challenges)
- Exact match validation (for text responses)
- Auto-generated usernames + passwords
- Sign-in with username + password
- Password authentication (SHA256 hashing)
- Haiku model only (hardcoded)
- Three leaderboard views (Global, Per-Hole, Session)
- Session timeout (3 hours, configurable)
- Context file management (add/remove/edit via pills UI)
- System prompt editing
- Token counting and scoring
- SQLite database
- Claude API backend

### Features EXCLUDED from MVP
- Skills/agents (predefined skill files)
- Schema validation file (challenges/schema.yaml - not needed)
- Model selection by users (Haiku only)
- Time limits per hole
- Hints system
- Semantic similarity validation
- Custom validation scripts
- Model parameters modification UI
- Offline mode
- Pill drag-to-reorder functionality
- Real-time WebSocket updates
- Advanced password hashing (bcrypt/argon2 - using SHA256 for MVP)

### Config File Requirements
- Session timeout duration (default 3 hours)
- Backend LLM provider configuration
- Database connection settings

## Key Design Decisions

1. **Server-Side Rendering**: Chosen for simplicity, reduced JS complexity, better SEO
2. **SQLite First**: Start simple, migrate to PostgreSQL via ADR when scaling needs are clear
3. **YAML Challenges**: Version-controlled, human-readable, easy to edit
4. **All Tokens Count**: Most realistic measure of efficiency, teaches true optimization
5. **Username + Password**: Auto-generated or user-provided, with password authentication (SHA256 for MVP)
6. **Pill UI**: Clear visual for which context elements are active
7. **Three Leaderboards**: Different competitive contexts:
   - **Global**: All sessions in current deployment
   - **Per-Hole**: Individual challenge scores across all sessions
   - **Session**: Current session only
8. **Edit Persistence**: User modifications persist across attempts within same hole
9. **Storage Granularity**: Per user per session per attempt
10. **Session = Competition = Game**: A session is a game on a specific course (collection of holes)
11. **LLM Error Handling**: Treat as "weather delay" - affected user clears tokens for that hole only
12. **No Offline Mode**: Requires internet connection for MVP

## Important Notes for AI Assistants

- **No Java**: Project is Python-based, avoid Java suggestions
- **Minimal JavaScript**: Only use JS when absolutely necessary (Alpine.js for pills, htmx for AJAX)
- **Document Everything**: All decisions → ADRs, all changes → clear commits
- **Challenge Files**: Don't create actual challenges yet, just the infrastructure
- **Scalability**: Design with future concurrency in mind, but implement simply first
- **Token Accuracy**: Token counting must be exact - this is the core metric
- **Validation Reliability**: Answer validation must be deterministic and fair
- **Conference Ready**: UI/UX must work well for live demos with large audiences

## Clarified Design Questions (Resolved)

1. **How does this scale to 100 concurrent users?** - Design with future scalability in mind, start simple with SQLite
2. **Is the token counting accurate and auditable?** - Yes, all tokens stored per attempt in database (both practice and submitted)
3. **Can this be easily modified via YAML/config?** - Yes, challenges in YAML, session timeout in config file
4. **Does this work offline?** - No, not for MVP (requires LLM API connection)
5. **Is the validation fair and deterministic?** - Yes, test cases and exact match only for MVP
6. **How do we handle ties in scoring?** - Tied players compete in additional challenge (see ADR 003)
7. **What happens if the LLM API is down?** - "Weather delay" - affected user clears tokens for that hole
8. **Can challenge authors test their challenges easily?** - Yes, validation scripts planned
9. **Edit persistence within a hole?** - Yes, edits persist across attempts within same hole
10. **Session timeout?** - 3 hours from creation (configurable), then marked DNF
11. **Multiple concurrent sessions?** - Yes, users can join multiple sessions
12. **Authentication?** - Username + password (generate new or sign in)
13. **Model selection?** - Haiku only for MVP, hardcoded
14. **Leaderboard views?** - Three: Global (all sessions), Per-Hole (all sessions), Session (current only)

## Documentation Organization

**Root Directory** (keep clean - only stable reference files):
- `CLAUDE.md` - AI assistant context (this file)
- `PROJECT_STATUS.md` - Current implementation status
- `README.md` - Project overview and quickstart
- `CONTRIBUTING.md` - Developer guide
- `QUICKSTART.md` - Getting started guide
- `RUNNING.md` - How to run the application
- `ISSUES.md` - Known issues and workarounds

**Organized Documentation Directories**:
- `docs/ADRs/` - Architecture Decision Records (numbered, e.g., `001-description.md`)
- `docs/phases/` - Phase completion documents (historical records)
- `docs/sessions/` - Session-specific implementation notes (dated YYYY-MM-DD)
  - Bug fixes, feature implementation details, working documents
  - Format: `DESCRIPTION_YYYY-MM-DD.md`
  - See `docs/sessions/README.md` for index
- `docs/ARCHITECTURE.md` - System architecture overview
- `docs/CHALLENGE_FORMAT.md` - Challenge YAML specification
- `docs/API.md` - API documentation
- `tests/README.md` - Testing guide

**Session Documentation Policy for AI Assistants**:
- ⛔ **DO NOT** create documentation files in root directory
- ✅ **DO** create session notes in `docs/sessions/`
- ✅ **DO** use dated format: `FEATURE_NAME_YYYY-MM-DD.md`
- ✅ **DO** update `PROJECT_STATUS.md` for status changes
- ✅ **DO** create ADRs in `docs/ADRs/` for architectural decisions
- ✅ **DO** keep root clean and organized

Example session doc: `docs/sessions/LEADERBOARD_SIMPLIFICATION_2026-09-23.md`
