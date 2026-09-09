# ADR 000: Use Architecture Decision Records

## Status

Accepted

## Context

Token Golf is a project designed for conference demonstrations with potential to scale. As the project evolves, we need to:

- Document important architectural and technical decisions
- Provide context for future contributors and maintainers
- Track the evolution of the system over time
- Enable informed decision-making by understanding past choices

Without structured documentation of decisions:
- New team members struggle to understand "why" things are done certain ways
- Important context gets lost in chat/email threads
- Similar questions get asked repeatedly
- Decisions get revisited unnecessarily

## Decision

We will use **Architecture Decision Records (ADRs)** to document all significant architectural and technical decisions.

### What qualifies as "significant"?

Decisions that should be documented:
- Technology choices (frameworks, libraries, databases)
- Architectural patterns and system design
- API designs and data models
- Deployment and infrastructure strategies
- Breaking changes to existing systems
- Major refactoring approaches
- Security and privacy decisions

Decisions that don't need ADRs:
- Minor bug fixes
- Code style preferences (covered by linters)
- Routine dependency updates
- Implementation details within existing patterns

### ADR Process

1. Copy the template from `docs/ADRs/template.md`
2. Number sequentially: `NNN-title.md`
3. Fill out all sections thoroughly
4. Commit with related code changes or separately
5. Reference ADR number in code comments when relevant

### ADR Format

Each ADR includes:
- **Status**: Proposed, Accepted, Deprecated, or Superseded
- **Context**: The issue motivating the decision
- **Decision**: What we're doing and why
- **Consequences**: Positive, negative, and risks
- **Alternatives Considered**: Other options and why not chosen
- **References**: Links to related resources

## Consequences

### Positive Consequences

- **Knowledge preservation**: Critical decisions and their rationale are documented
- **Onboarding efficiency**: New contributors can understand the "why" behind the system
- **Decision quality**: Writing forces thorough consideration of alternatives
- **Reduced bike-shedding**: Decided issues don't get re-litigated repeatedly
- **Historical record**: We can trace how and why the system evolved
- **Searchability**: Git history provides searchable decision log

### Negative Consequences

- **Additional work**: Writing ADRs takes time
- **Maintenance**: ADRs may need updates if decisions change
- **Discipline required**: Team must commit to the practice
- **Potential bloat**: Not every decision needs an ADR

### Risks

- **Risk**: Team doesn't consistently write ADRs
  - **Mitigation**: Make ADRs required for PR approval on significant changes
  
- **Risk**: ADRs become outdated but not marked as superseded
  - **Mitigation**: Periodic review of ADRs, mark deprecated ones clearly
  
- **Risk**: Too much documentation, analysis paralysis
  - **Mitigation**: Clear guidelines on what needs an ADR, keep them concise

## Alternatives Considered

### Alternative 1: No Formal Documentation

- **Description**: Rely on code comments, commit messages, and tribal knowledge
- **Pros**: 
  - No additional process overhead
  - Faster in short term
- **Cons**: 
  - Knowledge loss when team members leave
  - Context scattered across many sources
  - Difficult to understand big-picture decisions
- **Why not chosen**: Doesn't scale, poor long-term maintainability

### Alternative 2: Wiki or Shared Docs

- **Description**: Document decisions in a separate wiki or Google Docs
- **Pros**: 
  - Easy to edit and collaborate
  - Rich formatting options
- **Cons**: 
  - Not version controlled with code
  - Becomes out of sync with codebase
  - Additional tool to maintain
  - Harder to discover
- **Why not chosen**: Separation from code reduces utility and discoverability

### Alternative 3: Inline Code Comments Only

- **Description**: Document architectural decisions in code comments
- **Pros**: 
  - Right next to relevant code
  - Always in sync
- **Cons**: 
  - Doesn't capture alternatives considered
  - Hard to find cross-cutting decisions
  - Not suitable for high-level architecture
  - Gets lost in refactoring
- **Why not chosen**: Too granular, doesn't capture strategic thinking

## References

- [Michael Nygard's ADR article](http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions)
- [ADR GitHub organization](https://adr.github.io/)
- [When to write an ADR](https://github.com/joelparkerhenderson/architecture-decision-record#when-to-write-an-adr)

---

**Date**: 2026-09-09  
**Author**: Token Golf Team  
**Reviewers**: N/A (Initial ADR)
