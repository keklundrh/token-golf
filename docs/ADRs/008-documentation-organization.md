# ADR 008: Documentation Organization

## Status

Accepted

## Context

As the Token Golf project progresses through development phases, we're generating multiple types of documentation:
- Phase completion summaries
- Consistency validation reports
- Fix documentation
- Architecture decisions (ADRs)
- Development guides
- API documentation

Without clear organization, documentation becomes:
- Hard to find
- Scattered across repository
- Inconsistently named
- Difficult to navigate for new team members

### Current State (Before This ADR)

```
token-golf/
├── README.md
├── CLAUDE.md
├── CONTRIBUTING.md
├── PROJECT_STATUS.md
├── PHASE_2.1_CONSISTENCY_CHECK.md  ← Root directory (wrong!)
├── docs/
│   ├── PHASE_0_COMPLETE.md         ← Mixed with other docs
│   ├── PHASE_1.2_COMPLETE.md
│   ├── PHASE_1.3_COMPLETE.md
│   ├── PHASE_1.4_COMPLETE.md
│   ├── PHASE_2.1_COMPLETE.md
│   ├── PHASE_2.1_FIXES.md
│   ├── ARCHITECTURE.md
│   ├── CHALLENGE_FORMAT.md
│   ├── DEVELOPMENT_PHASES.md
│   ├── MVP_SCOPE.md
│   └── ADRs/
│       ├── 000-use-adrs.md
│       ├── 001-tech-stack.md
│       └── ...
```

**Problems**:
- Phase docs mixed with planning/architecture docs
- One phase doc in root directory
- No clear organization within `docs/`
- Hard to find phase-specific documentation
- Unclear where new phase docs should go

## Decision

We will organize documentation into logical subdirectories under `docs/`:

```
docs/
├── phases/           ← NEW: Phase-specific documentation
│   ├── README.md     ← Index and guide
│   ├── PHASE_0_COMPLETE.md
│   ├── PHASE_1.2_COMPLETE.md
│   ├── PHASE_1.3_COMPLETE.md
│   ├── PHASE_1.4_COMPLETE.md
│   ├── PHASE_2.1_COMPLETE.md
│   ├── PHASE_2.1_CONSISTENCY_CHECK.md
│   └── PHASE_2.1_FIXES.md
├── ADRs/             ← Architecture Decision Records
│   ├── template.md
│   ├── 000-use-adrs.md
│   └── ...
├── ARCHITECTURE.md   ← Top-level architecture
├── CHALLENGE_FORMAT.md
├── DEVELOPMENT_PHASES.md
└── MVP_SCOPE.md
```

### File Naming Convention

**Phase Documents**:
```
PHASE_X.Y_TYPE.md
```

Where:
- `X.Y` = Phase number (e.g., 0, 1.2, 2.1)
- `TYPE` = Document type (COMPLETE, CONSISTENCY_CHECK, FIXES)

**ADRs**:
```
NNN-kebab-case-title.md
```

Where:
- `NNN` = Three-digit number (000, 001, 002)
- `kebab-case-title` = Descriptive title

### Document Types

**Phase Documentation**:
- `PHASE_X.Y_COMPLETE.md` - What was built, how it works
- `PHASE_X.Y_CONSISTENCY_CHECK.md` - Validation against docs/requirements
- `PHASE_X.Y_FIXES.md` - Resolution of inconsistencies found

**Architecture Documentation**:
- `ADRs/NNN-title.md` - Architecture decisions
- `ARCHITECTURE.md` - System architecture overview
- `DEVELOPMENT_PHASES.md` - Development plan
- `CHALLENGE_FORMAT.md` - Specifications
- `MVP_SCOPE.md` - Scope decisions

**Root Documentation**:
- `README.md` - Project overview and quick start
- `CLAUDE.md` - AI assistant context
- `CONTRIBUTING.md` - Contribution guidelines
- `PROJECT_STATUS.md` - Current project state

## Rationale

### Why Separate `docs/phases/`?

1. **Clear Separation**: Phase docs are temporal/historical, different from planning docs
2. **Easy Navigation**: All phase documentation in one place
3. **Scalable**: Can handle 50+ phases without cluttering main docs/
4. **Self-Documenting**: Directory name makes purpose clear
5. **Index-able**: README.md provides phase overview and links

### Why This Naming Convention?

1. **Sortable**: Files sort chronologically (PHASE_0, PHASE_1.2, PHASE_2.1)
2. **Searchable**: Grep for "PHASE_2.1" finds all related docs
3. **Consistent**: Pattern easy to follow for new docs
4. **Clear Type**: TYPE suffix makes document purpose obvious
5. **No Conflicts**: Unique naming prevents overwrites

### Why ADRs Stay Separate?

1. **Different Purpose**: ADRs are design decisions, not phase work
2. **Cross-Phase**: One ADR may affect multiple phases
3. **Standard Practice**: ADRs are typically separate in industry
4. **Existing Structure**: Already well-organized with numbering

## Consequences

### Positive Consequences

- ✅ **Easy to Find**: All phase docs in `docs/phases/`
- ✅ **Clean Root**: No documentation in root directory
- ✅ **Scalable**: Can add 100+ phase docs without clutter
- ✅ **Onboarding**: New developers read `docs/phases/README.md` for history
- ✅ **Clear Purpose**: Directory and file names are self-explanatory
- ✅ **Searchable**: `grep "PHASE_2.1" docs/phases/` finds everything
- ✅ **IDE-Friendly**: Directory structure works well with IDEs
- ✅ **Git-Friendly**: Clear commit organization (phase docs together)

### Negative Consequences

- ⚠️ **Migration Needed**: Existing docs moved (one-time cost)
- ⚠️ **Link Updates**: References to old paths need updating (minimal)
- ⚠️ **Learning Curve**: Team needs to learn new structure (minor)

### Risks

**Risk: Broken links after move**
- **Mitigation**: Search for references before moving, update as needed
- **Likelihood**: Low - most phase docs self-contained
- **Impact**: Low - easy to fix

**Risk: Confusion about where to put new docs**
- **Mitigation**: Clear README.md in docs/phases/ with guidelines
- **Likelihood**: Low - naming convention is clear
- **Impact**: Low - easy to move if placed wrong

## Implementation

### Migration Steps

1. ✅ Create `docs/phases/` directory
2. ✅ Move all `PHASE_*.md` from `docs/` to `docs/phases/`
3. ✅ Move `PHASE_2.1_CONSISTENCY_CHECK.md` from root to `docs/phases/`
4. ✅ Create `docs/phases/README.md` with index
5. ✅ Document decision in this ADR
6. ✅ Verify no broken links
7. ✅ Commit changes

### Future Process

**When completing a phase**:
1. Create `docs/phases/PHASE_X.Y_COMPLETE.md`
2. Create `docs/phases/PHASE_X.Y_CONSISTENCY_CHECK.md`
3. If issues found, create `docs/phases/PHASE_X.Y_FIXES.md`
4. Update `docs/phases/README.md` with links
5. Commit all together

**When creating ADRs**:
1. Create `docs/ADRs/NNN-title.md` (use next number)
2. Follow template in `docs/ADRs/template.md`
3. Reference from relevant phase docs or architecture docs

## Alternatives Considered

### Alternative 1: Keep Everything in docs/ (Flat Structure)

**Description**: No subdirectories, all docs in `docs/`

**Pros**:
- Simpler structure
- Fewer directories
- No migration needed

**Cons**:
- Cluttered with 50+ phase docs
- Hard to find specific doc types
- Poor scalability
- Mixes temporal and permanent docs

**Why not chosen**: Doesn't scale, hard to navigate

### Alternative 2: One Directory per Phase

**Description**: `docs/phases/phase-0/`, `docs/phases/phase-1.2/`, etc.

**Pros**:
- Clear isolation per phase
- Can add phase-specific assets

**Cons**:
- Overly nested (3 levels deep)
- Harder to search across phases
- More navigation required
- Overkill for small number of docs per phase

**Why not chosen**: Too much nesting for current needs

### Alternative 3: By Document Type

**Description**: `docs/complete/`, `docs/checks/`, `docs/fixes/`

**Pros**:
- Groups by document purpose
- Easy to find all COMPLETE docs

**Cons**:
- Breaks chronological flow
- Hard to see full phase picture
- Phase 2.1 docs split across 3 dirs
- Doesn't match mental model

**Why not chosen**: Breaks phase cohesion

### Alternative 4: Git Tags Instead of Docs

**Description**: Tag commits instead of writing completion docs

**Pros**:
- No extra files
- Git native

**Cons**:
- No detailed context
- Can't include analysis
- Hard to review later
- Doesn't capture decisions

**Why not chosen**: Insufficient documentation

## Maintenance

### Keeping Organized

- ✅ Update `docs/phases/README.md` with each new phase
- ✅ Follow naming convention strictly
- ✅ Keep docs/phases/ clean (only PHASE_*.md files)
- ✅ Use subdirectories only if needed for assets

### Archival

Phase documents are **permanent historical records**:
- ❌ Do not delete completed phase docs
- ❌ Do not move to "archive" directories
- ✅ Keep in docs/phases/ indefinitely
- ✅ They document what was done and when

## References

- **Phase Documentation**: `docs/phases/README.md`
- **ADR Template**: `docs/ADRs/template.md`
- **Development Plan**: `docs/DEVELOPMENT_PHASES.md`
- **Project Status**: `PROJECT_STATUS.md`

## Examples

### Good Phase Documentation

```
docs/phases/
├── PHASE_2.1_COMPLETE.md           ✅ Follows convention
├── PHASE_2.1_CONSISTENCY_CHECK.md  ✅ Clear type
├── PHASE_2.1_FIXES.md              ✅ Related docs together
```

### Bad Phase Documentation

```
docs/
├── phase-2-point-1-done.md         ❌ Wrong name format
├── fixes-for-challenge-loader.md   ❌ Not clear which phase
└── consistency-check-2.md          ❌ No phase number
```

---

**Date**: 2026-09-21  
**Author**: Token Golf Team  
**Status**: Accepted and Implemented
