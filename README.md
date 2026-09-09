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
1. **Global**: Total score across all completed holes
2. **Per-Hole**: Best scores for individual challenges
3. **Session**: Current competition/event rankings

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
- [ ] Single-player mode
- [ ] 3-5 basic challenges
- [ ] Simple leaderboard
- [ ] Local SQLite storage
- [ ] Claude API backend

### Phase 2: Multi-Player
- [ ] Real-time competition mode
- [ ] Session management
- [ ] WebSocket updates
- [ ] Name generation system

### Phase 3: Production
- [ ] OpenShift deployment
- [ ] OpenShift AI integration
- [ ] PostgreSQL migration
- [ ] High availability
- [ ] Concurrency handling
- [ ] Advanced metrics

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
