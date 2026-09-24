# ADR 001: Technology Stack

## Status

Accepted (consolidated 2026-09-24; absorbs former ADR 002: Tailwind CSS, ADR 004: Alembic, ADR 006: Podman. Containerization updated from Docker to Podman per former ADR 006)

## Context

Token Golf must run on developer laptops, deploy to OpenShift for conference production, handle 100+ concurrent users, and be maintained by a Python-strong / JavaScript-limited team. Constraints: open-source dependencies, no Node.js backend preferred, OpenShift deployment target, rapid iteration ahead of conference demos.

## Decision

### Backend
- **Framework**: FastAPI (Python 3.11+) — native async for concurrent LLM requests, automatic OpenAPI docs, Pydantic typing, dependency injection
- **Database**: SQLite (dev) → PostgreSQL (prod)
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic from day one (former ADR 004)
- **Runtime**: uvicorn with asyncio

### Frontend
- **Rendering**: server-side Jinja2 templates
- **Interactivity**: htmx for AJAX; Alpine.js (15kb) for local component state
- **Styling**: Tailwind CSS (former ADR 002) — JIT mode, custom golf-themed palette, purged production builds

### LLM Integration
- **Development**: Anthropic Claude API behind an `LLMClient` abstraction from day one
- **Production**: OpenShift AI Models as a Service via the same abstraction

### Containerization (former ADR 006)
- **Podman + podman-compose** for all local container operations; OpenShift's native runtime (CRI-O) in production
- Rootless by default; OCI-compliant Dockerfiles (Docker-compatible via `alias docker=podman`)
- Will not: require Docker, maintain separate Docker/Podman configs, use non-OCI features, run containers as root

### Development Tooling
- Quality: Black, isort, flake8, mypy; pre-commit hooks
- Testing: pytest, pytest-asyncio, httpx; mock LLM responses in tests

**Scaling path if needed**: Redis (sessions/cache) → PostgreSQL → WebSockets → CDN.

## Rationale

- **FastAPI over Django/Flask**: best async fit for LLM-heavy API work; Django heavier than needed, Flask async immature
- **htmx + Alpine over SPA**: minimal JavaScript, server-controlled state, plays to team strengths; React/Vue SPAs add build pipelines, CORS, and state complexity not justified by our interactivity needs
- **Tailwind over Pico/Bootstrap/custom/CSS-in-JS**: utility classes enable fast iteration with a consistent design system and tiny purged builds; Pico too restrictive for conference-grade UI, Bootstrap heavier with a recognizable look, CSS-in-JS conflicts with server-side rendering, custom CSS too slow
- **Alembic from the start**: retrofitting migrations onto an existing database is painful; manual SQL is error-prone; recreate-on-change loses data; team learns the tool while stakes are low
- **SQLite → PostgreSQL**: start simple; SQLAlchemy abstracts the switch
- **Podman over Docker**: OpenShift runs Podman/CRI-O so local runtime matches production; rootless is better security; avoids Docker Desktop licensing; no daemon overhead. Kind/Minikube rejected as overkill for single-service development; no-containers rejected for environment parity
- **Phoenix LiveView rejected**: zero Elixir experience, smaller ecosystem

## Consequences

### Positive
- Python-centric stack with few moving parts
- No frontend build pipeline beyond Tailwind
- Local/production container parity ("works on my machine" minimized)
- Reversible, auditable schema changes
- Fast iteration cycles

### Negative
- Server-side rendering uses more server resources; htmx is chatty vs batched SPAs
- podman-compose less mature than docker-compose; most tutorials assume Docker
- Alembic adds a step per model change; merge conflicts in migrations possible
- Small learning curves for Tailwind, Alpine, Alembic, Podman

### Risks
- htmx at 100+ concurrent users → load test early, add caching/Redis if needed
- SQLite concurrent writes at scale → planned PostgreSQL migration
- OpenShift AI differs from Claude API → abstraction layer from day one
- podman-compose feature gaps → compose file sticks to well-supported basics; `podman play kube` fallback

## Alternatives Considered

| Alternative | Why not chosen |
|---|---|
| Node.js + Express + React | Against team expertise, two language environments, build complexity |
| Django + htmx | Heavier than needed, less async-friendly for API workloads |
| Flask + vanilla JS | Immature async, manual AJAX code gets messy |
| FastAPI + separate SPA | Two deployment artifacts, CORS, state complexity, overkill |
| Phoenix LiveView (Elixir) | Zero team experience |
| Pico.css | Too little styling control |
| Bootstrap | Heavier, jQuery-adjacent, recognizable look |
| CSS-in-JS / CSS Modules | Requires JS runtime, conflicts with SSR |
| Custom CSS | Too slow, no design system |
| Manual SQL migration scripts | Error-prone, no rollback story |
| Add Alembic later | Retrofit pain, team learns under pressure |
| Docker + Docker Compose | Root daemon, runtime mismatch with OpenShift, licensing |
| Kind/Minikube locally | Overkill for single-service MVP |
| No containers in development | Environment drift, dependency inconsistency |

## Implementation Notes

- **Tailwind**: `npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch` (dev) / `--minify` (prod); `tailwind.config.js` scans `app/templates/**/*.html` and `static/js/**/*.js`; golf palette (e.g. `golf-green: #2D5F3F`)
- **Alembic**: `alembic revision --autogenerate -m "..."` → review generated file → `alembic upgrade head`; rollback `alembic downgrade -1`; `alembic/env.py` targets `app.models.Base.metadata` with `settings.DATABASE_URL`. Best practices: always review auto-generated migrations, test upgrade AND downgrade, one logical change per migration, never modify committed migrations, backup before production migrations
- **Podman**: `podman build`, `podman-compose up`; Docker users add `alias docker=podman` and `alias docker-compose=podman-compose`

## References

- [FastAPI](https://fastapi.tiangolo.com/), [htmx](https://htmx.org/), [Alpine.js](https://alpinejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/docs), [SQLAlchemy 2.0](https://docs.sqlalchemy.org/), [Alembic](https://alembic.sqlalchemy.org/)
- [Podman](https://docs.podman.io/), [OpenShift Container Platform](https://docs.openshift.com/container-platform/)

---

**Date**: 2026-09-09 (consolidated 2026-09-24; absorbs former ADR 002, ADR 004, ADR 006 — all 2026-09-09)
**Author**: Token Golf Team
