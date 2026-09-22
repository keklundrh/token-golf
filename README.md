# Token Golf ⛳

A competitive game that teaches AI token efficiency through progressively harder challenges. Players compete to complete tasks using the fewest tokens possible - just like golf, fewer strokes (tokens) wins!

## 🎯 Purpose

Token Golf is designed for conference demonstrations and educational workshops where AI users learn how different dimensions (prompts, context, system instructions, model parameters) affect token consumption and model performance.

## 🎮 Game Mechanics

- **Golf-Style Scoring**: Fewer tokens = better score
- **Progressive Difficulty**: Multiple "holes" (challenges) with increasing complexity
- **All Tokens Count**: Input, output, system prompts, failed attempts - everything counts
- **Iterate to Success**: Players can retry until they get the correct answer (all attempts count)
- **Configurable Competitions**: Choose number of holes and difficulty levels

### Task Types
- Coding challenges
- Data extraction
- Question answering
- Text generation/transformation

### Modifiable Elements (Per Challenge)
Players can add/remove:
- Context files
- System prompts
- Skills/agents
- Model parameters (if supported by backend)

## 🏆 Leaderboards

Three leaderboard views:
1. **Global**: Scores across all sessions in current deployment
2. **Per-Hole**: Best scores for individual challenges across all sessions
3. **Session**: Current session/competition rankings only

## 🎨 UI Layout

```
┌─────────────────────┬──────────────────────┐
│ Challenge Display   │                      │
│ - Problem statement │                      │
│ - Success criteria  │   Unified Stats      │
│ - Context files     │   - Token count      │
├─────────────────────┤   - Leaderboard      │
│                     │   - Your rank        │
│ Prompt Interface    │   - VS Par           │
│ - Input area        │                      │
│ - Token estimate    │                      │
└─────────────────────┴──────────────────────┘
```

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python) - async, modern, OpenAPI support
- **Frontend**: htmx + Alpine.js - server-rendered with minimal JavaScript
- **Database**: SQLite (development) → PostgreSQL (production)
- **LLM Backend**: 
  - Development: Claude API
  - Production: OpenShift AI Models as a Service
- **Deployment**: Podman containers for OpenShift (see ADR 006)

## 🚀 Quick Start

### Containerized Development (Recommended)
```bash
# Setup environment
cp .env.example .env
# Add your Claude API key to .env

# Start with Podman
podman-compose up

# Visit
# http://localhost:8000
```

### Local Python (Alternative)

**Requirements**: Python 3.12 (3.13+ not yet supported due to dependency compatibility)

```bash
# Setup virtual environment
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Add your Claude API key to .env

# Run database migrations
alembic upgrade head

# Run
uvicorn app.main:app --reload

# Visit
# http://localhost:8000
```

**Note**: Containerized development includes all dependencies (Tailwind CSS, database, etc.) pre-configured.

## 📁 Project Structure

```
token-golf/
├── app/                    # FastAPI application
│   ├── main.py            # Entry point
│   ├── api/               # API routes
│   ├── models/            # Database models
│   ├── services/          # Business logic
│   └── templates/         # HTML templates
├── challenges/            # Challenge definitions
│   ├── hole-001/
│   │   ├── challenge.yaml
│   │   └── assets/
│   └── README.md
├── docs/                  # Documentation
│   ├── ADRs/             # Architecture Decision Records
│   └── CHALLENGE_FORMAT.md
├── static/               # CSS, JS, images
├── tests/                # Test suite
└── README.md
```

## 📝 Creating Challenges

Challenges are defined in YAML files. See [Challenge Format Documentation](docs/CHALLENGE_FORMAT.md) for details.

```yaml
id: hole-001
name: "Simple Function Generation"
difficulty: easy
task_type: coding
validation:
  type: test_cases
# ... see full spec in docs/
```

## 🎯 Development Workflow

This project uses **gitflow**:
- `main` - production-ready code
- `dev` - integration branch for features
- Feature branches created from `dev`
- All decisions documented in ADRs

## 🏗️ Project Status

**Current Phase**: Phase 8 - UI Redesign & Challenge Creation (Part 1: UI ✅ COMPLETE)

**Completed**:
- ✅ Phase 0: Container Foundation (Podman)
- ✅ Phase 1: Foundation Components (FastAPI, Database, Alembic)
- ✅ Phase 2: Core Services (Challenge Loader, LLM Client, Validator, Scoring)
- ✅ Phase 3: API Endpoints (Challenge, Game, Leaderboard APIs)
- ✅ Phase 4: Frontend Templates (Tailwind CSS, htmx, Alpine.js)
- ✅ Phase 5: Frontend Interactivity + Enhancements
- ✅ Phase 6: Supporting Features
- ✅ Phase 7: Testing & Polish (213 pytest tests, 22 browser tests, 74% coverage)
- ✅ Phase 8 Part 1: UI Redesign (modern game UI, 113 UI validation tests passing)

**Next**: Phase 8 Part 2 - Challenge Creation (15-20 new challenges)

**For detailed roadmap and phase documentation**, see:
- [DEVELOPMENT_PHASES.md](docs/DEVELOPMENT_PHASES.md) - Complete 8-phase plan
- [PROJECT_STATUS.md](PROJECT_STATUS.md) - Current status and progress
- [docs/phases/](docs/phases/) - Individual phase completion records

**MVP Scope**: See [docs/MVP_SCOPE.md](docs/MVP_SCOPE.md) for included/excluded features.

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## 📄 License

[To be determined]

## 🎓 Educational Use

Token Golf is designed for:
- AI/ML workshops and conferences
- Developer training sessions
- Prompt engineering education
- Token optimization demonstrations
- Competitive learning environments

---

**Target Audience**: Conference attendees, AI practitioners, developers learning prompt engineering and token optimization strategies.
