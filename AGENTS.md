# AGENTS.md

Guidance for AI agents working in this repo.

## Where work is defined

- **AI tasks and build prompts are defined in GitHub issues.** The issue body
  is the specification. Read the relevant issue(s) before starting work.
- **All development work happens on a branch off `dev`, determined by the
  relevant issue.** For "let's work on issue #N": branch from `dev` as
  `<topic>-<issue-number>` (e.g. `gameplay-2`), do the work there, and when
  complete report it — the user reviews and decides whether to merge into
  `dev`. NEVER commit development work directly to `dev` or the default
  branch, and NEVER merge to `dev` yourself.
  **Bootstrap:** if `dev` doesn't exist, create it from the default branch
  (`main`) before first use, then branch from it.
- **AI agents MUST NOT close GitHub issues.** Closing is the user's call;
  report completion and let the user close.
- **Source of truth is updated by EDITS, never comments.** Issue bodies and
  docs are edited in place (`gh issue edit --body-file`, file edits).
  NEVER append a comment to record a change, status, or decision — edit the
  body/file instead. Comments are not part of the record.
- **`docs/` is for end-user documentation ONLY.** Never create AI task
  definitions, build prompts, agent instructions, or implementation notes in
  `docs/`.

## Verification & Testing

- **No code is written without an explicit test.** Every behavior change
  lands with a test that covers it. Write the test first or alongside the
  code — never after as an afterthought. A change without a test is
  incomplete; do not report it done.
- Tests must be deterministic and isolated: no network, no real LLM calls
  (mock the provider), no shared state, no flakiness.
- **Check, double check, and test your work.** Never yield unverified:
  run the changed code path and observe the result before reporting done.
  Reproduce bugs before fixing; confirm after with the failing-before/
  passing-after test. Run the full suite before reporting done.
- Test tooling (once the scaffold exists): Vitest for units/API routes,
  Playwright for UI flows. Until then, throwaway scripts are for smoke
  checks only — they never substitute for the explicit test that ships.

## Documentation

- **All work must be documented.** Work documentation lives in the GitHub
  issue body of the task that produced it — the issue is the record. Do NOT
  put implementation notes, AI task definitions, or build prompts in `docs/`.
- **One file per topic, and as few files as possible.** Only create a
  documentation file when a topic genuinely needs a persistent doc outside
  the issue (e.g. a canonical spec or user-facing guide). Each such topic
  gets exactly ONE file; update that file in place. NEVER create a second
  file for a topic that already has one, and NEVER restate information that
  already exists in another doc, an issue, or this file — link to it instead.
- File-per-topic registry (create an entry only when a new file is truly
  warranted):
  - `docs/ARCHITECTURE.md` — pointer to issue #7 (canonical spec lives there)

## Key issues

- #1 — epic: token golf education app (open items tracked in its body)
- #2 — gameplay and flow
- #3 — UI style, color scheme, and currency units (Masters palette, µ$ in UI,
  `config/homepage.yaml`, `config/challenges/hole-NNN/challenge.yaml`)
- #4 — challenge creation logic
- #5 — challenge experience
- #6 — leaderboard (scoring/storage semantics: best-per-hole)
- #7 — architecture (canonical spec; `docs/ARCHITECTURE.md` points to it)
- #8 — model cost display (pre-swing price line per option)
- #9 — tips / "explain what just happened after the run" (open idea)
- #10 — cache read/write tokens in pricing and display (open idea; follow-up
  to #8's cache deferral)

## Stack

Stack details live in issue #7 (canonical architecture spec). Summary:
Next.js + TypeScript + Tailwind, better-sqlite3 + Drizzle, Vercel AI SDK
(Anthropic + OpenAI now; open-weight via `@ai-sdk/openai-compatible`
later), SSE streaming, Docker deploy with persistent filesystem (SQLite
requirement).
