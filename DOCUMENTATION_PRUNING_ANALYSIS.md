# Token Golf - Documentation Pruning Analysis

**Generated**: 2026-09-23  
**Current State**: 68 markdown files in docs/, 7 root-level docs  
**Recommendation**: Reduce to ~15-20 essential files

---

## Executive Summary

**CRITICAL FINDINGS:**
1. **Setup/Getting Started** information appears in 4 different files (README, QUICKSTART, RUNNING, CONTRIBUTING)
2. **Project Status** duplicated across README, PROJECT_STATUS, and CLAUDE.md
3. **MVP Scope** duplicated in CLAUDE.md and docs/MVP_SCOPE.md
4. **20 session files** in docs/sessions/ - many are redundant "final summaries" of same work
5. **5 documentation-about-documentation** files that can be deleted
6. **18 phase completion files** - most are historical and can be archived/removed

---

## 🔴 CRITICAL REDUNDANCIES (Fix First)

### 1. Setup Instructions (4 files → 1 file)
**Current duplicates:**
- `README.md` (lines 66-104) - Quick Start section
- `QUICKSTART.md` (entire file, 287 lines) - Detailed setup guide
- `RUNNING.md` (entire file, 210 lines) - "Super easy" guide
- `CONTRIBUTING.md` (lines 249-286) - Initial Setup section

**Recommendation:**
- **KEEP**: `QUICKSTART.md` (rename to `SETUP.md`)
- **DELETE**: `RUNNING.md` (completely redundant)
- **EDIT**: Remove Quick Start from README.md (replace with "See SETUP.md")
- **EDIT**: Remove Initial Setup from CONTRIBUTING.md (reference SETUP.md)

**Consolidation savings:** 3 files → 1 file

---

### 2. MVP Scope (2 comprehensive files → 1 file)
**Current duplicates:**
- `CLAUDE.md` (lines 145-230) - MVP Scope section
- `docs/MVP_SCOPE.md` (entire file, 300+ lines) - Comprehensive MVP scope

**Recommendation:**
- **KEEP**: `docs/MVP_SCOPE.md` (single source of truth)
- **EDIT**: `CLAUDE.md` - Replace MVP section with: "See docs/MVP_SCOPE.md"

**Consolidation savings:** Remove 85 lines from CLAUDE.md

---

### 3. Project Status (3 files with overlapping info)
**Current duplicates:**
- `PROJECT_STATUS.md` (389 lines) - Very detailed, includes phases
- `README.md` (lines 151-177) - Summary of status
- `CLAUDE.md` (lines 94-100) - References PROJECT_STATUS.md

**Recommendation:**
- **KEEP**: `PROJECT_STATUS.md` (single source of truth)
- **EDIT**: `README.md` - Reduce to 3-line summary: "Phase 8 in progress. See PROJECT_STATUS.md"
- **KEEP**: `CLAUDE.md` reference (already minimal)

**Consolidation savings:** Remove 20+ lines from README.md

---

### 4. Current Game Configuration (3 locations)
**Current duplicates:**
- `docs/CURRENT_GAME_CONFIG.md` (223 lines) - Comprehensive config
- `PROJECT_STATUS.md` (lines 386-389) - Current Configuration section
- `CLAUDE.md` (scattered throughout)

**Recommendation:**
- **KEEP**: `docs/CURRENT_GAME_CONFIG.md` (detailed reference)
- **EDIT**: `PROJECT_STATUS.md` - Replace section with: "See docs/CURRENT_GAME_CONFIG.md"
- **EDIT**: `CLAUDE.md` - Add reference to CURRENT_GAME_CONFIG.md

**Consolidation savings:** Remove duplicate config info

---

## 🗑️ FILES TO DELETE (33 files)

### Session Documentation (DELETE 15 files)
**Rationale:** Multiple redundant summaries of same work. Keep only unique/critical ones.

**DELETE (Redundant summaries from 2026-09-23):**
1. `docs/sessions/DOCUMENTATION_COMPLETE_2026-09-23.md` - Redundant
2. `docs/sessions/DOCUMENTATION_ORGANIZATION_2026-09-23.md` - Meta-doc
3. `docs/sessions/FINAL_STATUS_2026-09-23.md` - Duplicate of FINAL_SUMMARY
4. `docs/sessions/FINAL_SUMMARY_2026-09-23.md` - Duplicate info in PROJECT_STATUS
5. `docs/sessions/FIXES_2026-09-23.md` - Covered in IMPLEMENTATION_SUMMARY
6. `docs/sessions/GLOBAL_LEADERBOARD_IN_PROGRESS_2026-09-23.md` - Outdated WIP
7. `docs/sessions/IMPLEMENTATION_SUMMARY_2026-09-23.md` - Covered in phase docs
8. `docs/sessions/LEADERBOARD_FINAL_SUMMARY_2026-09-23.md` - Duplicate
9. `docs/sessions/LEADERBOARD_FIX_2026-09-23.md` - Small fix, not worth keeping
10. `docs/sessions/SESSION_SUMMARY_2026-09-23.md` - Generic summary

**DELETE (Meta-documentation files):**
11. `docs/DOCUMENTATION_CONSISTENCY_AUDIT.md` (24KB) - Audit complete, delete
12. `docs/DOCUMENTATION_FIXES_2026-09-22.md` - Fixes applied, delete
13. `docs/DOCUMENTATION_UPDATE_2026-09-22.md` - Updates done, delete

**DELETE (Redundant UI/testing docs):**
14. `docs/UI_AUDIT_2026-09-22.md` (17KB) - Audit complete, delete
15. `docs/UI_REDESIGN_PROPOSAL.md` (43KB) - Proposal implemented, delete
16. `docs/UI_REDESIGN_TEST_REPORT.md` (20KB) - Tests passed, delete

**DELETE (Redundant summaries):**
17. `docs/BUG_FIXES_SUMMARY.md` - Info in phase docs
18. `docs/CODE_AUDIT_2026-09-22.md` (16KB) - Audit complete, delete
19. `docs/PHASE_7_SUMMARY.md` - Duplicate of phase completion doc
20. `docs/TEST_SUITE_SUMMARY.md` - Info in PROJECT_STATUS.md

**DELETE (Root-level redundant file):**
21. `RUNNING.md` - Completely redundant with QUICKSTART.md

### Historical Phase Docs (OPTIONAL - Archive or DELETE 12 files)
**Rationale:** Historical records. Useful for reference but not critical for AI or developers.

**OPTIONS:**
- Option A: **DELETE** all sub-phase docs, keep only major phase completions
- Option B: **ARCHIVE** to `docs/archive/phases/` (keep out of main docs)
- Option C: **KEEP** but accept they're historical

**Sub-phase files (12):**
- `PHASE_1.2_COMPLETE.md`
- `PHASE_1.3_COMPLETE.md`
- `PHASE_1.4_COMPLETE.md`
- `PHASE_2.1_COMPLETE.md`
- `PHASE_2.2_COMPLETE.md`
- `PHASE_2.3_COMPLETE.md`
- `PHASE_2.4_COMPLETE.md`
- `PHASE_3.1_COMPLETE.md`
- `PHASE_3.2_COMPLETE.md`
- `PHASE_3.3_COMPLETE.md`
- `phase-4.1-part1-tailwind-setup.md`
- `PHASE_8_UI_REDESIGN_AND_CHALLENGES.md`

**KEEP (Major milestones):**
- `PHASE_0_COMPLETE.md`
- `PHASE_4_COMPLETE.md`
- `PHASE_5_COMPLETE.md`
- `PHASE_7_COMPLETE.md`
- `PHASE_8_PART_1_UI_REDESIGN_COMPLETE.md`
- `PHASE_8_PART_1.5_BUG_FIXES_AND_ENHANCEMENTS.md`

**Total deletion potential:** 33 files (or 21 if keeping historical phase docs)

---

## 📝 FILES TO CONSOLIDATE

### 1. CLAUDE.md - Aggressive Consolidation
**Current size:** 661 lines, 26KB

**Sections to REMOVE/REPLACE with references:**
- Lines 145-230: MVP Scope → "See docs/MVP_SCOPE.md"
- Lines 231-275: Database Schema → "See docs/ARCHITECTURE.md"
- Lines 355-370: Development Commands → "See SETUP.md"
- Lines 430-500: Documentation Organization → Simplify dramatically

**Target size:** ~350 lines (reduce by 50%)

---

### 2. README.md - Streamline
**Current size:** 200 lines

**Sections to REMOVE:**
- Lines 66-104: Quick Start → "See SETUP.md for setup instructions"
- Lines 151-177: Detailed status → "See PROJECT_STATUS.md"
- Lines 106-127: Project Structure → Move to ARCHITECTURE.md or delete

**Target size:** ~100 lines (one-page overview)

---

### 3. PROJECT_STATUS.md - Remove Redundancies
**Current size:** 389 lines

**Sections to REMOVE/SIMPLIFY:**
- Lines 186-211: Duplicate Phase 1.5 section (appears twice!)
- Lines 386-389: Current Configuration → "See docs/CURRENT_GAME_CONFIG.md"
- Simplify phase summaries (keep only completion status, link to phase docs)

**Target size:** ~250 lines

---

## ✅ FILES TO KEEP (Core Documentation)

### Root Level (6 files)
1. **README.md** - Project overview (streamlined to ~100 lines)
2. **CLAUDE.md** - AI assistant context (streamlined to ~350 lines)
3. **PROJECT_STATUS.md** - Current status (streamlined to ~250 lines)
4. **SETUP.md** (renamed from QUICKSTART.md) - Single setup guide
5. **CONTRIBUTING.md** - Developer guidelines (with setup section removed)
6. **ISSUES.md** - Known issues tracker

### docs/ Directory (9-12 files)
1. **docs/ARCHITECTURE.md** - System architecture
2. **docs/CHALLENGE_FORMAT.md** - Challenge YAML spec
3. **docs/DEVELOPMENT_PHASES.md** - Phase roadmap
4. **docs/MVP_SCOPE.md** - MVP scope reference
5. **docs/CURRENT_GAME_CONFIG.md** - Active game config
6. **docs/TESTING_PLAN.md** - Testing strategy
7. **docs/ADRs/** (directory) - Keep all 12 ADRs
8. **docs/phases/** (directory) - Keep 6 major phase completions
9. **docs/sessions/** (directory) - Keep 5 unique session files

### Session Files to KEEP (5 files)
1. `BROWSER_TESTING_REPORT_2026-09-22.md` - Unique testing insights
2. `BUTTON_STATE_GUIDE.md` - Technical reference
3. `LEADERBOARD_FIX_SUMMARY.md` - Significant fix documentation
4. `LEADERBOARD_SIMPLIFICATION_2026-09-23.md` - Recent important work
5. `PRACTICE_SWINGS_IMPLEMENTATION.md` - Core game mechanic change
6. `SESSION_2026-09-22_FIXES.md` - Critical bug fixes
7. `leaderboard_fix_spec.md` - Technical spec

---

## 📊 BEFORE & AFTER

### Before Pruning
- **Total files**: 75 markdown files
- **Root docs**: 7 files (~70KB)
- **docs/ files**: 68 files (~300KB+)
- **Redundancy level**: HIGH (same info 2-4 places)

### After Pruning
- **Total files**: ~30 markdown files (-60%)
- **Root docs**: 6 files (~40KB, -43%)
- **docs/ files**: ~24 files (-65%)
- **Redundancy level**: LOW (single source of truth)

---

## 🎯 RECOMMENDED ACTION PLAN

### Phase 1: Quick Wins (30 minutes)
1. **DELETE** 15 session files (redundant summaries)
2. **DELETE** 6 meta-documentation files (audits, proposals)
3. **DELETE** `RUNNING.md` (redundant setup guide)
4. **RENAME** `QUICKSTART.md` → `SETUP.md`

**Result:** -22 files immediately

### Phase 2: Consolidation (1 hour)
5. **EDIT** `README.md` - Remove Quick Start, Status details
6. **EDIT** `CLAUDE.md` - Replace sections with references
7. **EDIT** `PROJECT_STATUS.md` - Remove duplicate Phase 1.5, config
8. **EDIT** `CONTRIBUTING.md` - Remove setup section

**Result:** -300+ lines of duplicate content

### Phase 3: Optional Archive (30 minutes)
9. **MOVE** 12 sub-phase files to `docs/archive/phases/`
10. **CREATE** `docs/archive/README.md` explaining archive purpose

**Result:** -12 files from main docs (or delete if preferred)

---

## 🚨 WARNINGS

### DO NOT DELETE:
- **ADRs** - All architectural decisions should be preserved
- **Major phase completion docs** - Important milestones
- **Unique session files** - Files with unique technical insights
- **ARCHITECTURE.md** - Core system documentation
- **CHALLENGE_FORMAT.md** - Challenge authoring spec

### REVIEW BEFORE DELETING:
- Session files marked for deletion (verify no unique info)
- Phase sub-completion files (may have unique details)

---

## 📋 SPECIFIC EDITS NEEDED

### CLAUDE.md
```markdown
# Before (lines 145-230, 85 lines)
## MVP Scope
[... detailed MVP scope content ...]

# After (5 lines)
## MVP Scope
See `docs/MVP_SCOPE.md` for complete MVP scope documentation including features included/excluded, validation types, and UI elements.
```

### README.md
```markdown
# Before (lines 66-104, 38 lines)
## 🚀 Quick Start
### Containerized Development...
[... detailed setup instructions ...]

# After (3 lines)
## 🚀 Quick Start
See [SETUP.md](SETUP.md) for complete setup instructions (containerized or local Python).
```

### PROJECT_STATUS.md
```markdown
# Before (lines 186-211, duplicate!)
### Phase 8 Part 1.5: Bug Fixes...
[entire duplicate section]

# After
[DELETE - it's already at lines 160-185]
```

---

## ✅ SUCCESS CRITERIA

After pruning, documentation should be:
1. **Single source of truth** - Each piece of info in ONE place
2. **Easy to navigate** - Clear hierarchy, no hunting
3. **Up to date** - Remove outdated/completed audits
4. **Minimal** - Only essential information kept
5. **Cross-referenced** - Clear links between related docs

**Target:** New AI assistant or developer can understand project from 3-4 core files (README, CLAUDE, PROJECT_STATUS, SETUP).

---

## 🔗 CROSS-REFERENCE MAP (Post-Pruning)

```
README.md
  ├→ SETUP.md (getting started)
  ├→ PROJECT_STATUS.md (current state)
  ├→ CONTRIBUTING.md (how to contribute)
  └→ docs/ARCHITECTURE.md (system design)

CLAUDE.md (AI context)
  ├→ PROJECT_STATUS.md (implementation status)
  ├→ docs/MVP_SCOPE.md (feature scope)
  ├→ docs/CURRENT_GAME_CONFIG.md (active config)
  ├→ docs/CHALLENGE_FORMAT.md (challenge spec)
  └→ docs/ADRs/ (decisions)

PROJECT_STATUS.md
  ├→ docs/phases/ (phase completion details)
  ├→ docs/CURRENT_GAME_CONFIG.md (config)
  └→ ISSUES.md (known issues)

SETUP.md
  ├→ .env.example (config template)
  ├→ CONTRIBUTING.md (dev workflow)
  └→ ISSUES.md (troubleshooting)
```

---

**END OF ANALYSIS**
