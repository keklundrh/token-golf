# ADR 003: Competition Scoring and Leaderboards

## Status

Accepted (consolidated 2026-09-24; absorbs former ADR 010: Leaderboard Completion-Based Ranking, 2026-09-22, and former ADR 011: Practice Swings and Submitted Attempts, 2026-09-23. Supersedes the original "every attempt counts" scoring)

## Context

Three mechanics define fair competition:

1. **Scoring model** — the original "every stroke counts" rule punished experimentation: users feared trying different approaches, early failures polluted final scores, and the game taught "guess right quickly" instead of "find the optimal prompt."
2. **Ranking** — ranking purely by ascending total tokens let players who quit after 1-2 holes appear above players who completed the course. This violates the golf principle: *you can't win by quitting early*.
3. **Ties** — identical token counts are likely (easy holes, shared strategies, large conference fields), so a single-winner mechanism is needed.

## Decision

### 1. Scoring Model: Practice Swings (former ADR 011)

Two distinct actions:

| Action | Behavior | Database | Scored? |
|---|---|---|---|
| **Practice Swing** | Runs prompt against LLM, shows response, validation, token count | `attempt_type='practice'` | Never; unlimited |
| **Submit & Record Score** | Records attempt for leaderboard | `attempt_type='submitted'` | Yes; only if `is_correct=True` (else HTTP 422) |

- Best (lowest-token) **submitted** attempt per hole wins; players may resubmit to improve
- Next hole unlocks after the first successful submission on the current hole (navigation guard)
- Terminology keeps the golf theme: "Practice Swing" / "Submit & Record Score"

**Database**: `attempts.attempt_type VARCHAR(20)` (default `practice`), indexed; backfill marks pre-existing correct attempts as `submitted`. **Scoring queries** filter `WHERE attempt_type='submitted'`; per-hole score is `MIN(total_tokens)` over submitted attempts; cumulative tokens sum submitted attempts only.

### 2. Ranking: Completion-First (former ADR 010)

Following professional golf conventions:

- **Global leaderboard (Hall of Fame)**: only players who completed *all* holes of a course; sorted by best total tokens ascending; DNF sessions excluded entirely
- **Session leaderboard (Live Competition)**: two sections — "Completed" (ranked 1, 2, 3… by tokens, badge **F**) above a divider, then "In Progress"/DNF (unranked `--`, sorted by holes completed desc then tokens asc, badges **IP** / **DNF**)
- **Per-hole leaderboard**: unchanged — already filters to completed attempts

Sort keys everywhere: holes completed (desc) → total tokens (asc) → completion time (asc). Progress shown as `X/5` holes and `●●●○○` indicators.

**Database**: `sessions.course_total_holes`, `session_participants.holes_completed`, `session_participants.course_completed_at`, composite index on `(session_id, holes_completed, course_completed_at)`. `ScoringService._check_course_completion()` maintains them. htmx partials: `/htmx/leaderboard/global`, `/htmx/leaderboard/session/{id}`. Backfill: `scripts/backfill_leaderboard_data.py`.

### 3. Tie-Breaking: Sudden-Death Playoff (original ADR 003)

Ties for **first place only** are broken by an additional challenge selected from the pool, repeated until one winner emerges.

- Tiebreaker tokens are tracked separately, never added to original scores
- All other rankings remain unchanged during the tiebreaker
- Cap tiebreaker rounds (e.g., 3) with a secondary metric as fallback, and include tiebreaker time in event scheduling

## Consequences

### Positive
- Experimentation is free; learning is rewarded; the optimization goal is explicit
- Leaderboards are golf-authentic and fair — no winning by quitting early
- Ties resolve dramatically and deterministically
- Every attempt is still stored, preserving analytics and audit trails

### Negative
- Departs from pure "every stroke counts" golf
- Two-button UI instead of one
- Extra denormalized completion columns and a two-section session view
- Tiebreaker duration is unpredictable

### Risks
- Practice-attempt database growth → conferences are time-limited; archive old sessions
- Empty global leaderboard before anyone completes a course → acceptable; session view stays active
- Tiebreakers run long → event planning, hard cutoffs
- Submit gating confusion → UI enables Submit only on valid attempts; navigation guard blocks advancing

## Alternatives Considered

- **All attempts count** (original scoring) — punished learning; replaced by practice swings
- **Limited practice swings / half-cost swings / first-attempt bonus** — arbitrary limits or partial penalties don't fix the core disincentive
- **No practice, multiple submits only** — loses the "pick your best" mechanic
- **Rank everyone by tokens** (original ranking) — quitters outrank finishers; replaced
- **Only show completers everywhere** — hides in-progress players from the session view
- **Weighted score (tokens/holes)** — penalizes longer courses, not golf-authentic
- **First-to-complete wins ties** — penalizes careful optimization
- **Shared victory / random selection / fewest attempts / dollar-cost tiebreakers** — anticlimactic, unskillful, punish iteration, or provider-dependent

## References

- `app/services/scoring.py`, `app/api/game.py`, `app/models/attempt.py`, `app/models/score.py`, `app/templates/game.html`
- Migrations: `87efb90c8ffb_add_attempt_type_for_practice_swings.py`, `2e1ac852f393` (completion tracking)
- [PGA playoff formats](https://www.pga.com/rules/playoff-formats), [golf leaderboard conventions](https://www.livetourney.com/blog/golf-scoreboard-explained)

---

**Date**: 2026-09-09 (original tie-breaking), consolidated 2026-09-24; absorbs former ADR 010 (2026-09-22) and ADR 011 (2026-09-23)
**Author**: Token Golf Team
