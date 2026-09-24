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

### Scoring System (ADR 003: Competition Scoring and Leaderboards)
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

**Historical Note**: Pre-ADR 003 consolidation (before 2026-09-24), every attempt counted ("all tokens count" golf-style scoring). Changed to practice swings (originally ADR 011, now absorbed into ADR 003) to encourage experimentation and better teach token optimization.

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

**See [docs/CHALLENGE_FORMAT.md](docs/CHALLENGE_FORMAT.md) for complete challenge YAML specification.**

## Development Workflow

**See [CONTRIBUTING.md](CONTRIBUTING.md) for git flow, branching rules, and testing strategy.**

## Database Schema

**See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for complete database schema and system architecture.**

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

## Setup & Development Commands

**See [SETUP.md](SETUP.md) for complete setup instructions and development commands.**

## MVP Scope

**See [docs/MVP_SCOPE.md](docs/MVP_SCOPE.md) for complete MVP feature scope (included/excluded features).**

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


## Documentation Policy for AI Assistants

### CRITICAL RULES - READ FIRST

**NEVER CREATE NEW DOCUMENTATION FILES.** Always append to or edit existing files.

**File Reference Limits:**
- CLAUDE.md can link to **AT MOST ONE FILE** per topic
- If information exists in a file, reference it - don't duplicate
- When in doubt, append to existing file rather than create new

If no topic exists and the information discussed exists NO WHERE ELSE, a new documentation file can be created and linked to in CLAUDE.md 

### Documentation Structure

**Root files** (reference only):
- `README.md` - Project overview
- `CLAUDE.md` - This file (AI context)
- `PROJECT_STATUS.md` - Current status
- `SETUP.md` - Setup/commands
- `CONTRIBUTING.md` - Dev workflow
- `ISSUES.md` - Known issues

**Topic-specific docs** (detailed content):
- `docs/ARCHITECTURE.md` - System architecture, database schema
- `docs/CHALLENGE_FORMAT.md` - Challenge YAML spec
- `docs/MVP_SCOPE.md` - Feature scope
- `docs/CURRENT_GAME_CONFIG.md` - Active game config
- `docs/ADRs/` - Architecture decisions (consolidated: 000, 001, 003, 005, 007)
- `docs/phases/` - Phase completions (historical, do not edit)
- `docs/sessions/` - Session notes (dated YYYY-MM-DD format)

### Where to Document What

| Content Type | File to Edit |
|--------------|--------------|
| Implementation status | PROJECT_STATUS.md |
| Setup instructions | SETUP.md |
| Architecture changes | docs/ARCHITECTURE.md |
| Challenge format | docs/CHALLENGE_FORMAT.md |
| MVP scope changes | docs/MVP_SCOPE.md |
| Game configuration | docs/CURRENT_GAME_CONFIG.md |
| Architectural decisions | docs/ADRs/NNN-title.md (new file OK) |
| Session work notes | docs/sessions/DESCRIPTION_YYYY-MM-DD.md |
| Bug tracking | ISSUES.md |

### Session Documentation Rules

- **Format**: `docs/sessions/DESCRIPTION_YYYY-MM-DD.md`
- **When**: For detailed implementation notes, bug fixes, investigations
- **DO NOT**: Create "summary" or "final" documents - update PROJECT_STATUS.md instead
- **DO NOT**: Create duplicate summaries of same work

### Before Creating Any File

1. Check if topic covered in existing file
2. If yes: Edit existing file
3. If no: Check if it belongs in existing category (append)
4. Only if truly unique: Create new file (rare)

**Example**: Don't create "LEADERBOARD_SUMMARY.md" - update PROJECT_STATUS.md and reference docs/sessions/ for details.
