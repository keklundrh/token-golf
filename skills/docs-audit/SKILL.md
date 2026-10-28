---
name: docs-audit
description: Verifies token-golf end-user documentation against the code and specs. Use when the user asks to "run the docs-audit", check that docs/ is accurate, or confirm documentation before reporting work done.
---

# Docs audit: end-user docs vs specs and code

Report-only pass. Never fix anything as part of the audit — findings are
follow-up work the user assigns. Docs are corrected by editing the file in
place; issues by editing the issue body. Never comments, never closing an
issue.

## Scope

`docs/` is **end-user documentation only** in this repo (see AGENTS.md
"Documentation"). One file per topic; the file-per-topic registry lives in
AGENTS.md. `docs/ARCHITECTURE.md` is a pointer to issue #7 — verify the
pointer, and that the canonical spec really lives in the issue.

## Checks

1. **Accuracy.** For every claim in `docs/`, confirm it against the current
   code and the issue specs (`gh issue view <N> --json body`). Flag:
   - behavior the docs describe that the code no longer has
   - behavior the code has that the docs omit or contradict
   - config examples that no longer match `config/`
2. **Hygiene.** Flag anything in `docs/` that violates the repo rule:
   - agent notes, AI task definitions, build prompts, implementation notes
   - content restated from another doc or an issue (must link, not restate)
   - a second file for a topic that already has one

Cite the doc path (and line where useful) plus the contradicting
`file:line` or issue number for every finding.

## Findings format

One line per finding:

```
<class> | <doc path> | <what> | <suggested correction>
```

`<class>`: `stale-doc` (docs contradict code/spec), `missing-doc`
(documented behavior absent from docs where the doc's scope requires it),
`leak` (implementation/agent notes in docs/), `dup` (restated content —
should link).

Report the list. Do not fix anything as part of the audit.
