# Token Golf - Quick Start Guide

## Prerequisites

- **Podman** and **podman-compose** installed (for containerized setup)
  - macOS: `brew install podman podman-compose`
  - Linux: See [Podman installation guide](https://podman.io/getting-started/installation)
  - Windows: See [Podman Desktop](https://podman-desktop.io/)
- **Python 3.12** (for local development - 3.13+ not yet supported)
  - macOS: `brew install python@3.12`
- Claude API key (get from: https://console.anthropic.com/)

> **Note**: This project uses Podman instead of Docker. See [ADR 006](docs/ADRs/006-use-podman-for-containerization.md) for rationale. If you prefer Docker, most commands work with `alias docker=podman`.

## Setup

### 1. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Claude API key
# Replace 'your-api-key-here-replace-me' with your actual key
nano .env  # or use your preferred editor
```

### 2. Build and Run with Podman

```bash
# Build and start the container
podman-compose up --build

# Or run in detached mode (background)
podman-compose up -d --build
```

### 3. Verify It's Running

Open your browser to:
- **Home**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs

Or use curl:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "token-golf",
  "version": "0.1.0"
}
```

## Development Workflow

### Hot Reload

The container is configured with hot reload - any changes to Python files in `app/` will automatically restart the server.

### View Logs

```bash
# Follow logs in real-time
podman-compose logs -f web

# View last 100 lines
podman-compose logs --tail=100 web
```

### Stop the Container

```bash
# Stop and remove containers
podman-compose down

# Stop, remove containers, and remove volumes
podman-compose down -v
```

### Access the Container Shell

```bash
# Get a shell inside the running container
podman-compose exec web bash

# Run commands inside the container
podman-compose exec web python -c "print('Hello from container')"
```

### Run Tests (Once Implemented)

```bash
# Run all tests
podman-compose exec web pytest

# Run with coverage
podman-compose exec web pytest --cov=app --cov-report=html

# Run specific test file
podman-compose exec web pytest tests/unit/test_example.py
```

### Database Migrations (Once Alembic is Set Up)

```bash
# Create a new migration
podman-compose exec web alembic revision --autogenerate -m "description"

# Apply migrations
podman-compose exec web alembic upgrade head

# Rollback one migration
podman-compose exec web alembic downgrade -1
```

## PostgreSQL (Optional)

For production-like testing with PostgreSQL:

```bash
# Start with PostgreSQL enabled
podman-compose --profile postgres up -d

# Update .env to use PostgreSQL
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/token_golf
```

## Troubleshooting

### Port Already in Use

If port 8000 is already in use:

```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process or change port in docker-compose.yml
```

### Container Won't Start

```bash
# Check container logs
podman-compose logs web

# Rebuild from scratch
podman-compose down -v
podman-compose build --no-cache
podman-compose up
```

### Database Issues

```bash
# Remove database and start fresh
rm -f data/token_golf.db
podman-compose restart web
```

### Can't Connect to Claude API

1. Verify your API key in `.env`
2. Check network connectivity
3. View logs for detailed error messages

## File Structure

```
token-golf/
├── app/                    # Application code (hot-reloaded)
│   ├── main.py            # FastAPI entry point
│   ├── api/               # API endpoints (Phase 3)
│   ├── models/            # Database models (Phase 1)
│   └── services/          # Business logic (Phase 2)
├── data/                   # SQLite database (gitignored)
├── challenges/             # YAML challenge definitions
├── static/                 # CSS, JS, images
├── tests/                  # Test suite
├── docker-compose.yml      # Container orchestration
├── Dockerfile              # Container definition
├── requirements.txt        # Python dependencies
└── .env                    # Environment config (gitignored)
```

## ✅ Recent Updates (2026-09-22)

All critical issues from the 2026-09-21 build have been resolved:
- ✅ Issue #1: API Breaking Change (htmx JSON encoding) - FIXED
- ✅ Issue #3: Browser Testing Complete (22/22 passing) - DONE
- ✅ Phase 8 Part 1: Complete UI redesign (modern game UI) - DONE

### What Works Right Now:
- ✅ Backend API (all endpoints functional)
- ✅ Database and migrations  
- ✅ 5 sample challenges (hole-001 to hole-005)
- ✅ 4 courses (Beginner's Green, Challenge Valley, etc.)
- ✅ Error handling and session management
- ✅ Modern game UI (redesigned in Phase 8)
- ✅ 213 pytest tests + 22 browser tests (all passing)

See `ISSUES.md` for current issue tracking.

## What You'll See

After starting the server, you can visit:

### Home Page (`http://localhost:8000`)
- Auto-generated username + password option
- Sign-in for existing users
- Leaderboard preview (top 3 players)

### Game Interface (`/game/{session_id}`)
- **Left**: Challenge description + prompt input area
- **Right**: Metrics panel (tokens, rank, leaderboard)
- **Pills UI**: Manage context files and system prompts
- **Animations**: Golf-themed loading states

### Leaderboard (`/leaderboard`)
- **Three views**: Global / Per-Hole / Session
- **Keyboard shortcuts**: G, H, S, R
- **Auto-refresh**: Toggle 30-second updates

### API Documentation (`/docs`)
- Interactive OpenAPI/Swagger docs
- Test all endpoints directly
- See request/response schemas

## Available Challenges

1. **hole-001**: Hello World (easy, exact_match)
2. **hole-002**: Addition Function (easy, test_cases)
3. **hole-003**: String Reversal (medium, test_cases)
4. **hole-004**: Email Extraction (medium, exact_match)
5. **hole-005**: FizzBuzz (hard, test_cases)

## Project Status

**Completed Phases:**
- ✅ Phase 0: Container Foundation
- ✅ Phase 1: Foundation Components
- ✅ Phase 2: Core Services
- ✅ Phase 3: API Endpoints
- ✅ Phase 4: Frontend Templates
- ✅ Phase 5: Frontend Interactivity
- ✅ Phase 6: Supporting Features (~95%)

**MVP Progress:** ~95% complete

**Next:** Phase 7 - Testing & Polish

See [PROJECT_STATUS.md](PROJECT_STATUS.md) for detailed status and [docs/DEVELOPMENT_PHASES.md](docs/DEVELOPMENT_PHASES.md) for the complete roadmap.

## Getting Help

- Check the logs: `podman-compose logs -f`
- Read the docs in `/docs`
- Review ADRs in `/docs/ADRs` (especially ADR 006 for Podman rationale)
- See CONTRIBUTING.md for development guidelines

## Docker Users

If you prefer Docker, you can use it instead - our configuration is compatible:

```bash
# Create aliases
alias podman=docker
alias podman-compose=docker-compose

# Or just use docker/docker-compose directly
docker-compose up --build
```
