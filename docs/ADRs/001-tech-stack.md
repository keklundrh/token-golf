# ADR 001: Technology Stack Selection

## Status

Accepted

## Context

Token Golf requires a web application that can:
- Run locally on developer laptops for testing
- Deploy to OpenShift for production (conference demos)
- Handle 100+ concurrent users during conferences
- Provide real-time-ish updates for leaderboards
- Be maintained by a team comfortable with Python
- Minimize JavaScript complexity
- Support rapid development and iteration

### Key Requirements

**Functional:**
- Interactive web UI with chat-style interface
- Real-time leaderboard updates
- Token counting and scoring
- LLM integration (Claude API → OpenShift AI)
- Challenge management system
- User session management

**Non-Functional:**
- Simple local development setup
- Container-deployable (Docker/OpenShift)
- Scalable to conference workloads
- Maintainable by Python developers
- Minimal frontend complexity
- Fast iteration cycles

**Constraints:**
- Team expertise: Python (strong), JavaScript (limited)
- Deployment target: OpenShift
- No Node.js backend preferred
- Must be open source
- Modern, well-maintained technologies

## Decision

We will use the following technology stack:

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: SQLite (dev) → PostgreSQL (prod)
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic (see ADR 004)
- **Async Runtime**: uvicorn with asyncio

### Frontend
- **Rendering**: Server-side with Jinja2 templates
- **Interactivity**: htmx for AJAX
- **Minimal JS**: Alpine.js (15kb) for component state
- **Styling**: Tailwind CSS

### LLM Integration
- **Development**: Anthropic Claude API (direct HTTP client)
- **Production**: OpenShift AI (via abstraction layer)

### Deployment
- **Containerization**: Docker
- **Orchestration**: OpenShift/Kubernetes
- **Process Manager**: uvicorn workers

### Development Tools
- **Code Quality**: Black, isort, flake8, mypy
- **Testing**: pytest, pytest-asyncio, httpx
- **Pre-commit**: Automated checks

## Rationale

### FastAPI
- Native async/await for concurrent LLM requests
- Excellent performance without Node.js
- Automatic OpenAPI documentation
- Strong typing with Pydantic
- Built-in dependency injection
- Large, active community
- WebSocket support for future real-time features

### Server-Side Rendering (htmx + Jinja2)
- Minimal JavaScript complexity
- Progressive enhancement approach
- Server-controlled state (simpler debugging)
- Plays to Python team strengths
- Good enough performance for our use case
- No build step or npm dependencies

### Alpine.js
- Tiny footprint (15kb)
- Perfect for pill UI (add/remove elements)
- Declarative syntax (HTML attributes)
- No build step required
- Good documentation
- Complements htmx well

### SQLite → PostgreSQL
- Start simple with SQLite (single file, no setup)
- Well-defined migration path to PostgreSQL
- SQLAlchemy abstracts differences
- Both well-supported by FastAPI ecosystem

### Docker/OpenShift
- Standard containerization
- OpenShift is deployment target (requirement)
- Portable between environments
- Easy scaling with replicas

## Consequences

### Positive Consequences

- **Python-Centric**: Leverages team's Python expertise
- **Simple Stack**: Fewer technologies to learn and maintain
- **Fast Development**: No frontend build pipeline, rapid iteration
- **Scalable**: Async FastAPI handles concurrent LLM requests efficiently
- **Deployable**: Docker + OpenShift is well-trodden path
- **Testable**: Great testing tools in Python ecosystem
- **Type Safe**: Pydantic + mypy catch errors early
- **Observable**: Standard Python logging and monitoring

### Negative Consequences

- **Server Load**: Server-side rendering requires more server resources than SPA
- **Network Chattiness**: htmx makes frequent requests vs. batched SPA calls
- **Limited Interactivity**: Can't match rich SPA interactions (not needed for our use case)
- **State Management**: Server-side session state can complicate scaling (mitigated with Redis later)
- **Alpine.js Learning**: Small learning curve for team

### Risks

- **Risk**: htmx performance insufficient for 100+ concurrent users
  - **Mitigation**: Load test early, can add caching/Redis if needed
  - **Likelihood**: Low - htmx designed for this
  
- **Risk**: SQLite doesn't handle concurrent writes at scale
  - **Mitigation**: Migrate to PostgreSQL when scaling (planned)
  - **Likelihood**: Medium - expected and planned for
  
- **Risk**: Team struggles with Alpine.js
  - **Mitigation**: Limited scope (just pill UI), good docs
  - **Likelihood**: Low - simpler than React/Vue
  
- **Risk**: OpenShift AI integration differs significantly from Claude API
  - **Mitigation**: Abstraction layer (LLMClient) from day one
  - **Likelihood**: Medium - mitigated by design

## Alternatives Considered

### Alternative 1: Node.js + Express + React

- **Description**: Full JavaScript stack with React SPA
- **Pros**: 
  - Rich client-side interactivity
  - Huge ecosystem
  - Team could learn modern JS
  - Standard SPA patterns
- **Cons**: 
  - Team not strong in JavaScript
  - Two language environments (JS + Python for LLM?)
  - Build pipeline complexity
  - More moving parts
  - Doesn't leverage team strengths
- **Why not chosen**: Against team expertise, adds complexity

### Alternative 2: Django + HTMX

- **Description**: Django instead of FastAPI
- **Pros**: 
  - Batteries-included framework
  - Excellent admin interface
  - Large ecosystem
  - Similar rendering approach
- **Cons**: 
  - Heavier framework (we don't need most features)
  - Less async-friendly than FastAPI
  - Slower for API-heavy workloads
  - More opinionated (good and bad)
- **Why not chosen**: FastAPI better fit for async LLM calls, modern patterns

### Alternative 3: Flask + Vanilla JavaScript

- **Description**: Lighter Python framework, no htmx/Alpine
- **Pros**: 
  - Maximum simplicity
  - Fewer dependencies
  - Team knows Flask
- **Cons**: 
  - No async support (Flask 3.0 has it but immature)
  - Manual AJAX code gets messy
  - Reinventing patterns htmx provides
  - Less structure
- **Why not chosen**: htmx provides better UX without complexity tax

### Alternative 4: Full SPA (React/Vue) + FastAPI

- **Description**: FastAPI for API only, separate React/Vue frontend
- **Pros**: 
  - Modern SPA experience
  - Clear API/UI separation
  - Could be more responsive
- **Cons**: 
  - Two separate deployment artifacts
  - Complex frontend build pipeline
  - State management complexity (Redux/Vuex)
  - Team learning curve
  - CORS complications
  - Overkill for our interactivity needs
- **Why not chosen**: Complexity not justified by requirements

### Alternative 5: Phoenix LiveView (Elixir)

- **Description**: Elixir framework with server-rendered real-time updates
- **Pros**: 
  - Excellent real-time performance
  - Server-rendered like our approach
  - Great concurrency model
- **Cons**: 
  - Team has zero Elixir experience
  - Smaller ecosystem
  - Harder to hire for
  - Not Python (can't reuse existing code/skills)
- **Why not chosen**: Too far from team expertise

## Implementation Notes

### Project Structure
```
app/
├── main.py          # FastAPI app entry point
├── api/             # API route handlers
├── services/        # Business logic
├── models/          # SQLAlchemy models
├── templates/       # Jinja2 templates
└── config.py        # Configuration

static/
├── css/
├── js/              # Minimal Alpine.js components
└── images/

tests/
├── unit/
├── integration/
└── challenges/
```

### Development Workflow
1. Backend: `uvicorn app.main:app --reload`
2. No build step for frontend (pure htmx/Alpine)
3. Templates auto-reload in dev mode
4. Hot reload for Python changes

### Testing Strategy
- Backend: pytest with httpx TestClient
- Frontend: Playwright for E2E
- LLM: Mock responses in tests

## Migration Path

If we need to scale beyond this stack:

1. **Add Redis**: For session/cache management
2. **Add PostgreSQL**: Replace SQLite in production
3. **WebSockets**: For true real-time leaderboard
4. **CDN**: For static assets at scale
5. **If SPA needed**: Keep FastAPI backend, add React frontend (separate decision)

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [htmx Documentation](https://htmx.org/)
- [Alpine.js Documentation](https://alpinejs.dev/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/)
- [OpenShift Python Guide](https://docs.openshift.com/container-platform/latest/openshift_images/using_images/using-s21-images.html)

---

**Date**: 2026-09-09  
**Author**: Token Golf Team  
**Reviewers**: N/A (Initial decision)
