# ADR 000: Documentation Standards and Organization

## Status

Accepted (absorbs former ADR 008: Documentation Organization, 2026-09-21)

## Context

Token Golf generates multiple documentation types — architecture decisions, phase completion summaries, session notes, and guides. Two problems needed solving:

1. Decisions were scattered across chat threads and code comments; "why" questions got re-asked and decisions re-litigated.
2. Early files landed in inconsistent locations (a phase doc in the repo root, phase docs mixed with planning docs in `docs/`), making documentation hard to find and navigate.

## Decision

### Part 1: Architecture Decision Records

We use ADRs for all significant architectural and technical decisions.

**Qualifies for an ADR**: technology choices, architectural patterns and system design, API/data model designs, deployment and infrastructure strategy, breaking changes, major refactoring approaches, security and privacy decisions.

**Does not**: minor bug fixes, code style preferences, routine dependency updates, implementation details within existing patterns.

**Process**:
1. Copy `docs/ADRs/template.md`
2. Number sequentially: `NNN-kebab-case-title.md`
3. Fill out Context, Decision, Consequences, Alternatives
4. Commit with related code changes
5. Reference the ADR number in code comments where relevant
6. Related decisions MAY be consolidated into an existing ADR when topics overlap; superseded decisions are absorbed with an "absorbs" note, not left as stub files (see the 2026-09-24 consolidation)

### Part 2: Repository Documentation Layout

```
docs/
├── ADRs/           # Architecture decisions (NNN-kebab-case-title.md) + template.md
├── phases/         # Phase completion docs: PHASE_X.Y_TYPE.md (COMPLETE | CONSISTENCY_CHECK | FIXES)
├── sessions/       # Dated session notes: DESCRIPTION_YYYY-MM-DD.md
├── ARCHITECTURE.md
├── CHALLENGE_FORMAT.md
└── API.md
```

The repo root stays clean: only stable reference files (`README.md`, `CLAUDE.md`, `PROJECT_STATUS.md`, `CONTRIBUTING.md`, `SETUP.md`, `ISSUES.md`).

**Rules**:
- Phase documents are permanent historical records — never delete or move them
- Naming conventions: `PHASE_X.Y_TYPE.md` for phases, `NNN-kebab-case-title.md` for ADRs, `DESCRIPTION_YYYY-MM-DD.md` for session notes
- Update `docs/phases/README.md` (index) when adding phase docs
- Session work notes go in `docs/sessions/`, never the repo root

## Consequences

### Positive
- Decisions and their rationale survive team turnover and context loss
- Documentation locations are predictable; onboarding is self-serve
- Git history doubles as a searchable decision log
- Root directory stays clean

### Negative
- Writing ADRs takes time
- Consolidations leave historical documents pointing at absorbed ADR numbers (mitigated by "absorbs" notes in each consolidated ADR)

### Risks
- *ADRs not written consistently* → required for significant changes
- *ADRs go stale* → supersede/absorb explicitly rather than silently editing

## Alternatives Considered

- **No formal documentation** — knowledge loss, scattered context
- **Wiki/shared docs** — not version-controlled with code, drifts from codebase
- **Inline code comments only** — too granular, lost in refactors, no alternatives captured
- **Flat `docs/` (no subdirectories)** — cluttered at 50+ phase docs
- **One directory per phase** — over-nested for the doc volume
- **By document type (`docs/complete/`, `docs/fixes/`)** — breaks phase cohesion
- **Git tags instead of completion docs** — no detailed context or analysis

## References

- [Michael Nygard's ADR article](http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions)
- `docs/ADRs/template.md`
- `docs/phases/README.md`

---

**Date**: 2026-09-09 (consolidated 2026-09-24; absorbs former ADR 008, 2026-09-21)
**Author**: Token Golf Team
