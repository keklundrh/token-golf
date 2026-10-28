---
name: code-audit
description: Reviews token-golf code against the issue specs, both directions. Use when the user asks to "run the code-audit", check that code matches the specs, or find unspecced or unimplemented behavior before merging work.
---

# Code audit: code vs spec

Report-only pass. Never fix anything as part of the audit — findings are
follow-up work the user assigns. Fixes follow the normal branch/test-first
flow on a branch off `dev`; issue bodies are corrected by editing them in
place, never comments, and issues are never closed by the agent.

## Method: requirements matrix

Build a matrix of **requirement → issue number → code file → test**, one
row per behavioral requirement in the issues relevant to the work in scope.
Source issues with `gh issue view <N> --json body` — the issue body is the
specification (see AGENTS.md "Where work is defined"). Use file reads and
targeted search to map each requirement to its implementing code and its
test.

## Checks (both directions)

1. **Spec → code.** Every specced behavior exists in code. A requirement
   with no implementing code is a finding. A requirement with no covering
   test is also a finding (this repo's rule: no code without an explicit
   test).
2. **Code → spec.** No code behavior contradicts or silently extends beyond
   the spec. Unspecced behavior is a finding even when it looks right —
   cite the code, name the issue that should own it if the behavior is
   wanted, so the spec is updated by edit before the work is reported done.

## Scope rules

- Cite `file:line` for every finding; never report a finding without one.
- Tests count as behavior evidence, not proof: a test that asserts wiring
  or incidental defaults does not cover a behavioral requirement.
- Read the issue bodies before opening files; the body is the source of
  truth, code comments are not.

## Findings format

One line per finding:

```
<class> | <file:line> | <what> | <suggested correction>
```

`<class>`: `unimplemented` (specced, not in code), `code-bug` (contradicts
spec), `unspecced` (behavior with no spec owner), `untested` (specced
behavior with no test).

Report the list. Do not fix anything as part of the audit.
