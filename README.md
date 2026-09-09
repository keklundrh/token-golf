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
│ Problem Statement   │                      │
│                     │                      │
│                     │   Metrics & Results  │
├─────────────────────┤                      │
│                     │   - Leaderboards     │
│ Chat Interface      │   - User Stats       │
│ - Prompt input      │   - Comparisons      │
│ - Context pills     │   - Distribution     │
│ - System settings   │                      │
└─────────────────────┴──────────────────────┘
```

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python) - async, modern, OpenAPI support
- **Frontend**: htmx + Alpine.js - server-rendered with minimal JavaScript
- **Database**: SQLite (development) → PostgreSQL (production)
- **LLM Backend**: 
  - Development: Claude API
  - Production: OpenShift AI Models as a Service
- **Deployment**: Docker containers for OpenShift

## 🚀 Quick Start (Local Development)

```bash
# Setup (coming soon)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Add your Claude API key to .env

# Run
uvicorn app.main:app --reload

# Visit
# http://localhost:8000
```

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

## 🏗️ Roadmap

### Phase 1: MVP (Current)
**Included:**
- [x] Session management (sessions = games on courses)
- [ ] 3-5 basic challenges (test cases + exact match validation)
- [ ] Three leaderboard views (Global, Per-Hole, Session)
- [ ] Local SQLite storage
- [ ] Claude API backend (Haiku model)
- [ ] Auto-generated usernames (new each session)
- [ ] Context file & system prompt editing (pills UI)
- [ ] Session timeout (3 hours, configurable)
- [ ] Edit persistence within holes

**Excluded from MVP:**
- Skills/agents
- Model selection
- Time limits per hole
- Hints system
- Persistent authentication
- Semantic similarity validation
- Custom validation scripts
- Offline mode
- Real-time WebSocket updates

### Phase 2: Advanced Features
- [ ] Skills/agents system
- [ ] Additional validation types (semantic, custom scripts)
- [ ] Model selection per challenge
- [ ] Hints system (costs tokens)
- [ ] Persistent authentication (password-based)
- [ ] Real-time WebSocket updates
- [ ] Time limits and max iterations

### Phase 3: Production
- [ ] OpenShift deployment
- [ ] OpenShift AI integration
- [ ] PostgreSQL migration
- [ ] MLFlow integration (token counting)
- [ ] High availability
- [ ] Advanced metrics and analytics
- [ ] Multi-region support

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
