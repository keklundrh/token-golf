# ADR 005: Session Management, Authentication, and MVP Scope

## Status

Accepted (consolidated 2026-09-24; absorbs former ADR 009: Password Authentication in MVP, 2026-09-21, which superseded this ADR's original "no authentication" decision)

## Context

Token Golf needs a session management strategy for multiple concurrent conference players, and an authentication approach that survives demo-day realities: presenters resume the same user across browser restarts, players take breaks without losing progress, and friction must stay low (no email, verification, or recovery flows). MVP scope must stay bounded for timely delivery.

## Decision

### Session Structure
**A session = a competition = a game on a specific course (collection of holes).**

- Sessions are created with a course_id; multiple users join the same session; users may hold multiple concurrent sessions
- Configurable timeout (default 3 hours from creation); expired sessions are marked **DNF** (Did Not Finish)
- Background job enforces timeouts every 5 minutes

### Storage Granularity
**All user modifications are stored per user per session per attempt** in the `attempts` table: `prompt`, `system_prompt`, `context_files` (JSON tracking active files and edits). This preserves a complete audit trail and enables prompt-evolution analytics and debugging.

### Edit Persistence Within a Hole
Modifications persist across attempts within the same hole; a new hole resets to defaults. Users refine an approach without re-doing modifications each attempt.

### Authentication (former ADR 009)
**Username + password authentication is in MVP:**

- **Flows**: "Generate New" (auto-generated username + random password, displayed in copy-able boxes with a "no password recovery" warning) and "Sign In" (username + password validation)
- **Username format**: `{Color}-{GolfCourse}-{ClubNumber}` (e.g., `Blue-Pebblebeach-7`); uniqueness enforced at the database level; inappropriate combinations filtered; implemented in `app/api/game.py`
- **Password storage**: SHA256 hashing for MVP; **must migrate to bcrypt/argon2 before production deployment** (invalidating all passwords and forcing re-registration is acceptable for the demo→prod transition); field `users.password_hash` is nullable for backward compatibility
- **No**: password recovery, email addresses, OAuth, account management UI, rate limiting (MVP)
- `POST /api/game/start` handles both flows; browser stores session_id in sessionStorage

**Security posture**: SHA256 is acceptable for MVP because deployments are short-lived, low-stakes (game scores), HTTPS-only, and not internet-exposed. **Required before production**: bcrypt/argon2, login rate limiting, password strength policy, auth audit logging, account lockout.

### MVP Feature Boundaries

**Included**: test-cases + exact-match validation, auto-generated usernames **and passwords**, sign-in, Haiku only (hardcoded), three leaderboard views, 3-hour session timeout, context file management, system prompt editing, token counting and scoring (practice swings per ADR 003), SQLite database, Claude API backend.

**Excluded**: skills/agents, user model selection, per-hole time limits, hints system, semantic similarity validation, custom validation scripts, model-parameter modification UI, offline mode, pill drag-to-reorder, WebSockets, max-iterations enforcement, password recovery/OAuth.

### Database Schema
- `sessions` (course, timeout, status, expires_at), `session_participants` (many-to-many users↔sessions)
- `attempts` gains session_id, system_prompt, context_files; `scores` gains session_id; `users` gains nullable `password_hash` (migration `002_add_password_hash.py`)

## Consequences

### Positive
- Clear competition boundaries; supports individual and group play
- Complete audit trail of every attempt; fair scoring (no hidden modifications)
- Iterative refinement without friction
- Presenters prepare known credentials; players keep progress across breaks
- Scope discipline prevents feature creep

### Negative
- Larger database (full context stored per attempt); cleanup job needed
- SHA256 is not password-grade (accepted debt with a production gate)
- No recovery path — forgotten password means generating a new account
- Same person can join a session multiple times (future: IP/fingerprint check)

### Risks
- Database growth → context files stored by reference; archive old sessions after events
- Edit-persistence confusion → clear UI indication of active state
- Timeout mis-tuned → configurable; monitor actual usage
- SHA256 weakness → production gate before any internet exposure

## Alternatives Considered

- **User-scoped sessions (no multi-player)** — kills the conference competition use case
- **Hole-scoped storage (latest state only)** — loses audit trail and prompt-evolution analytics
- **Fresh state each attempt** — frustrating; users re-do identical modifications
- **No authentication (original decision)** — presenters explicitly needed session resumption; replaced by password auth
- **OAuth (GitHub/Google) or email-based auth** — external dependencies and flows too heavy for MVP conference demos
- **Session tokens / magic links** — token loss = identity loss, awkward to type/share
- **Bcrypt from day one** — premature for the MVP threat model; tracked as a production gate
- **All validation types in MVP** — semantic similarity needs an embedding service; defers MVP

## References

- ADR 003: Competition Scoring and Leaderboards (scoring within sessions)
- ADR 001: Technology Stack (Alembic migration strategy)
- `app/api/game.py` (implementation), [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)

---

**Date**: 2026-09-09 (consolidated 2026-09-24; absorbs former ADR 009, 2026-09-21)
**Author**: Token Golf Team
