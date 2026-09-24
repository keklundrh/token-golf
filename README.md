# Token Golf ⛳

A competitive game that teaches AI token efficiency through progressively harder challenges. Players compete to complete tasks using the fewest tokens possible - just like golf, fewer strokes (tokens) wins!

## 🎯 Purpose

Token Golf is designed for conference demonstrations and educational workshops where AI users learn how different dimensions (prompts, context, system instructions, model parameters) affect token consumption and model performance.

## 🎮 Game Mechanics

- **Golf-Style Scoring**: Fewer tokens = better score
- **Progressive Difficulty**: 5 "holes" (challenges) with increasing complexity
- **Practice Swings**: Unlimited practice attempts to test your prompts (don't count toward score)
- **Submit & Record**: When happy with a solution, submit it to record your score
- **Best Score Wins**: Only your best submitted attempt per hole counts toward the leaderboard
- **Retry to Improve**: Can submit multiple times to optimize your score
- **Single Course Mode**: Currently all sessions play "Full Tour" (5 holes)

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

**See [SETUP.md](SETUP.md) for complete setup instructions** (containerized or local Python).

```bash
# Quick version:
cp .env.example .env    # Add your Claude API key
podman-compose up       # Or use ./run.sh for local Python
# Visit http://localhost:8000
```

## 📁 Project Structure & Documentation

- **Architecture**: See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Creating Challenges**: See [docs/CHALLENGE_FORMAT.md](docs/CHALLENGE_FORMAT.md)
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)

## 🎯 Development Workflow

This project uses **gitflow**:
- `main` - production-ready code
- `dev` - integration branch for features
- Feature branches created from `dev`
- All decisions documented in ADRs

## 🏗️ Project Status

**Phase 8 in progress** (UI Redesign ✅, Bug Fixes ✅, Challenge Creation next).

**See [PROJECT_STATUS.md](PROJECT_STATUS.md) for detailed current status, completed phases, and roadmap.**

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
