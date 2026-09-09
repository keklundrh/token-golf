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

### Scoring System
- **All tokens count**: input + output + system prompts + failed attempts
- Players iterate on their prompts until they achieve the correct answer
- Each iteration adds to their total token count
- Players can retry after success (counts as additional strokes)
- Winner has the lowest total token count across completed holes

### Challenge Structure
- **Holes**: Individual challenges with specific tasks
- **Rounds**: Competitions with N holes
- **Difficulty Levels**: Configurable per hole and per competition
- **Task Types**: coding, data extraction, question answering, text transformation

### User Interaction Elements
Players can modify these during gameplay (pill UI with X buttons):
- Pre-loaded context files (can be included/excluded/edited)
- System prompts (modifiable)
- Skills/agents (generic LLM concepts/files)
- Model parameters (if OpenShift AI supports it)

### Validation
Each challenge must have clear, verifiable correct answers:
- Test cases (for coding)
- Exact string matching
- Semantic similarity checks
- Custom validation scripts

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
- **Styling**: [TBD - modern CSS framework]

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

### Directory Structure

```
token-golf/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── challenges.py    # Challenge endpoints
│   │   ├── leaderboard.py   # Leaderboard endpoints
│   │   └── game.py          # Game session endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          # User/session models
│   │   ├── challenge.py     # Challenge models
│   │   └── attempt.py       # Attempt/score models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_client.py    # LLM API integration
│   │   ├── validator.py     # Answer validation
│   │   ├── scoring.py       # Token counting & scoring
│   │   └── name_generator.py # User name generation
│   ├── templates/           # Jinja2 templates
│   │   ├── base.html
│   │   ├── game.html
│   │   └── leaderboard.html
│   └── config.py            # Configuration management
├── challenges/
│   ├── README.md            # Challenge authoring guide
│   ├── hole-001/
│   │   ├── challenge.yaml   # Challenge definition
│   │   └── assets/          # Context files, test data
│   └── schema.yaml          # YAML schema definition
├── docs/
│   ├── ADRs/                # Architecture Decision Records
│   │   ├── 000-use-adrs.md
│   │   ├── 001-tech-stack.md
│   │   └── template.md
│   ├── ARCHITECTURE.md      # System architecture
│   ├── CHALLENGE_FORMAT.md  # Challenge YAML specification
│   └── API.md               # API documentation
├── static/
│   ├── css/
│   ├── js/                  # Minimal JS only
│   └── images/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── challenges/          # Challenge validation tests
├── .env.example             # Environment variables template
├── .gitignore
├── CLAUDE.md                # This file
├── CONTRIBUTING.md          # Development guidelines
├── docker-compose.yml       # Local development setup
├── Dockerfile               # Production container
├── README.md                # Project overview
└── requirements.txt         # Python dependencies
```

## User Identity System

### Name Generation
Auto-generated usernames ensure professional, family-friendly identifiers:
- Format: `{Color}-{GolfCourse}-{ClubNumber}`
- Example: `Blue-Pebblebeach-7`, `Green-Augusta-3`
- Components:
  - Colors: Standard golf-appropriate colors
  - Courses: Famous golf course names (Augusta, Pebblebeach, StAndrews, etc.)
  - Clubs: 1-14 (standard golf club numbers)
- Validation: Filter inappropriate combinations
- Persistence: Names tied to sessions, stored in database

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
│  │ [skill-1 X]          │  │                            │
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
   - Top 10 players
   - Highlight current user
   - Real-time updates (in competition mode)

3. **Comparison Data**
   - User's last attempt vs current
   - User's score vs average
   - Improvement indicators

4. **Statistical Distribution**
   - Average tokens for this hole
   - Median tokens
   - Best score
   - Number of completions
   - Histogram/distribution graph

### Pills UI
- Alpine.js driven
- Click X to remove element
- Click pill to edit/configure (modal or inline)
- Visual indication of active/inactive state
- Drag to reorder (future enhancement)

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
  type: test_cases  # test_cases, exact_match, semantic_similarity, custom_script
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

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id TEXT,
    is_active BOOLEAN DEFAULT TRUE
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
    challenge_id TEXT REFERENCES challenges(id),
    attempt_number INTEGER,
    prompt TEXT,
    response TEXT,
    input_tokens INTEGER,
    output_tokens INTEGER,
    total_tokens INTEGER,
    is_correct BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Scores Table
```sql
CREATE TABLE scores (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    challenge_id TEXT REFERENCES challenges(id),
    total_attempts INTEGER,
    total_tokens INTEGER,
    completed_at TIMESTAMP,
    session_id TEXT
);
```

## LLM Integration

### Token Counting
- Use LLM provider's token counting API
- Track separately: input tokens, output tokens, system tokens
- Store all token counts in database for analysis

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

## Key Design Decisions

1. **Server-Side Rendering**: Chosen for simplicity, reduced JS complexity, better SEO
2. **SQLite First**: Start simple, migrate to PostgreSQL via ADR when scaling needs are clear
3. **YAML Challenges**: Version-controlled, human-readable, easy to edit
4. **All Tokens Count**: Most realistic measure of efficiency, teaches true optimization
5. **Auto-Generated Names**: Removes authentication friction for demos, ensures appropriate names
6. **Pill UI**: Clear visual for which context elements are active
7. **Three Leaderboards**: Different competitive contexts (global achievement vs current competition)

## Important Notes for AI Assistants

- **No Java**: Project is Python-based, avoid Java suggestions
- **Minimal JavaScript**: Only use JS when absolutely necessary (Alpine.js for pills, htmx for AJAX)
- **Document Everything**: All decisions → ADRs, all changes → clear commits
- **Challenge Files**: Don't create actual challenges yet, just the infrastructure
- **Scalability**: Design with future concurrency in mind, but implement simply first
- **Token Accuracy**: Token counting must be exact - this is the core metric
- **Validation Reliability**: Answer validation must be deterministic and fair
- **Conference Ready**: UI/UX must work well for live demos with large audiences

## Questions to Address

When implementing features, consider:
1. How does this scale to 100 concurrent users?
2. Is the token counting accurate and auditable?
3. Can this be easily modified via YAML/config?
4. Does this work offline (for conference WiFi issues)?
5. Is the validation fair and deterministic?
6. How do we handle ties in scoring?
7. What happens if the LLM API is down?
8. Can challenge authors test their challenges easily?
