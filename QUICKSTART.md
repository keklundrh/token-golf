# Token Golf - Quick Start Guide

## Prerequisites

- **Podman** and **podman-compose** installed
  - macOS: `brew install podman podman-compose`
  - Linux: See [Podman installation guide](https://podman.io/getting-started/installation)
  - Windows: See [Podman Desktop](https://podman-desktop.io/)
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

## Next Steps

After Phase 0 is complete, we'll build:

1. **Phase 1**: Database models, config, Alembic migrations
2. **Phase 2**: Core services (LLM client, validator, scoring)
3. **Phase 3**: API endpoints
4. **Phase 4**: Frontend templates
5. **Phase 5**: Frontend interactivity

See [docs/DEVELOPMENT_PHASES.md](docs/DEVELOPMENT_PHASES.md) for the complete roadmap.

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
