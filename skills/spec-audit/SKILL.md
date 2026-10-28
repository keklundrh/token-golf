---
name: spec-audit
description: Audits token-golf issue specs against each other and the code. Use when the user asks to "run the spec-audit", review issue consistency, or check that code matches the specs before merging work.
---

# Spec audit: issue specs vs code

Report-only pass. Never fix anything as part of the audit — findings are
follow-up work the user assigns. Fixes follow the normal branch/test-first
flow; issue bodies and docs are corrected by editing them in place, never
comments, and issues are never closed by the agent.

## Method: requirements matrix

Build a matrix of **requirement → issue number → code file → test**, one
row per behavioral requirement, then run both checks below over the same
matrix. Source issues with `gh issue view <N> --json body` — the issue body
is the specification (see AGENTS.md "Where work is defined").

## Check 1: issue vs issue

Read the open issue bodies relevant to the work in scope. Flag:

- **Contradictions** — one issue states what another supersedes without the
  other being edited in place (e.g. #2's one-swing-per-challenge wording vs
  #5's run-history ledger which assumes multiple options run).
- **Redundancies** — the same rule owned by two issues; it will drift. Flag
  which issue should own it and what the other should link instead.
- **Stale claims** — implementation-status or test-count lines that no
  longer match reality (e.g. "Tests: 33 passing" after the suite grew).
- **Open items** — a body tracking open items that the implementation has
  resolved but the body still lists as open.

## Check 2: spec vs code

For each matrix row, confirm **both directions**:

1. Every specced behavior exists in code (unimplemented spec = finding).
2. No code behavior contradicts or silently extends beyond the spec
   (unspecced behavior = finding; cite the code, name the issue that should
   own it if the behavior is wanted).

Cite `file:line` for every finding. Tests count as behavior evidence: a
requirement with no covering test is a finding.

## Findings format

One line per finding:

```
<class> | <where> | <what> | <suggested correction>
```

`<class>`: `spec-bug` (issue body wrong/contradictory), `code-bug` (code
contradicts spec), `unspecced` (code behavior with no spec owner),
`stale-issue` (issue body out of date), `untested` (specced behavior with no
test). `<where>`: issue number or `file:line`.

Report the list. Do not fix anything as part of the audit.
