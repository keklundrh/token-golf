# Fixes Needed - Action Plan

**Created**: 2026-09-21  
**Based on**: CONSISTENCY_AUDIT.md  
**Priority**: Work through these together

---

## Quick Stats

**Issues Found**: 21  
**Documentation Bloat**: 1,940 lines (37% unnecessary)  
**Estimated Fix Time**: 2 hours  
**Expected Savings**: ~3,000 lines, accurate docs

---

## Critical Fixes (Do First - 30 min)

### Fix 1: PROJECT_STATUS.md - Update Current Phase

**File**: PROJECT_STATUS.md  
**Lines**: 2-10, 109-287

**Current** (WRONG):
```markdown
**Last Updated**: 2026-09-09
**Phase**: Phase 0 - Container Foundation
**Status**: ✅ Complete
```

**Should be**:
```markdown
**Last Updated**: 2026-09-21
**Phase**: Phase 2.4 - Scoring Service
**Status**: ✅ Complete (All Phase 2 services done)
**Next**: Phase 3.1 - Challenge API
```

**Also update**: "What's Next" section (currently says Phase 1, should say Phase 3)

---

### Fix 2: DEVELOPMENT_PHASES.md - Check Completed Boxes

**File**: DEVELOPMENT_PHASES.md  
**Lines**: 10-71 (Phase 0, 1.2-1.4, 2.1-2.4)

**Current**: All `- [ ]` unchecked ❌  
**Should be**: `- [x]` for completed items ✅

**Phases to mark complete**:
- Phase 0 (lines 10-16): All 7 items
- Phase 1.2 (lines 38-43): All 6 items
- Phase 1.3 (lines 50-57): All 8 items
- Phase 1.4 (lines 64-71): All 8 items
- Phase 2.1 (lines 80-88): All 9 items
- Phase 2.2 (lines 95-102): All 8 items (except unit tests)
- Phase 2.3 (lines 109-116): All 8 items (except unit tests)
- Phase 2.4 (lines 123-129): All 7 items (except unit tests)

**Total**: ~60 checkboxes to update

---

### Fix 3: CLAUDE.md - Add Current State Section

**File**: CLAUDE.md  
**Line**: 100 (before "### Directory Structure")

**Add**:
```markdown
### Current State (Phase 2.4 Complete)

**Implemented**:
- ✅ Container foundation (Podman/Docker)
- ✅ Database models (SQLAlchemy 2.0)
- ✅ Database migrations (Alembic)
- ✅ Configuration management (Pydantic)
- ✅ Service layer (4 services: challenge loader, LLM client, validator, scoring)

**Not Yet Implemented** (see Directory Structure below for target):
- ⏳ API endpoints (Phase 3)
- ⏳ Frontend templates (Phase 4-5)
- ⏳ Name generator (Phase 6)
- ⏳ Tests (Phase 7)

### Directory Structure (Target Architecture)
```

**Also add** at line 159 (after directory structure):
```markdown
**Note**: Directory structure above shows target architecture. See "Current State" for what's implemented.
```

---

## Documentation Cleanup (Do Second - 60 min)

### Fix 4: Remove Repetitive Test Sections

**Files to edit** (delete entire "### Unit Tests (Future Phase 7)" section):

1. `docs/phases/PHASE_2.1_COMPLETE.md` - Delete lines 450-485
2. `docs/phases/PHASE_2.2_COMPLETE.md` - Delete lines 416-450  
3. `docs/phases/PHASE_2.3_COMPLETE.md` - Delete lines 460-504
4. `docs/phases/PHASE_2.4_COMPLETE.md` - Delete lines 577-620

**Replace each with**:
```markdown
## Testing

Unit tests will be implemented in Phase 7. See `docs/TESTING_PLAN.md` for the testing strategy.
```

**Savings**: ~200 lines

---

### Fix 5: Compress Verbose Sections

**Apply to**: All PHASE_2.X_COMPLETE.md files

#### Before (example from PHASE_2.2):
```markdown
### ✅ LLMClient Class

Full-featured async client:

```python
client = LLMClient()

# Basic completion
response = await client.complete(
    prompt="Write a Python function to add two numbers",
    system_prompt="You are a helpful coding assistant."
)

# With context files
response = await client.complete_with_context(...)
```

**Features**:
- ✅ Async/await pattern (matches FastAPI)
- ✅ Uses Anthropic AsyncAnthropic client
- ✅ Configurable timeout (default 60s)
- ✅ Automatic retries (default 2 attempts)
- ✅ Multiple content block handling
- ✅ Context file support (for challenges)
- ✅ Comprehensive logging
```

#### After (compressed):
```markdown
### ✅ LLMClient Class

Async Claude API client with token counting.

```python
response = await client.complete(prompt="...", system_prompt="...")
```

Features: async/await, timeouts, retries, context files, token counting. See code docstrings.
```

**Apply pattern**:
- Features: Bullets only, max 50 lines
- Integration: Max 30 lines, reference SERVICE_INTEGRATION.md
- Examples: 1-2 only, max 30 lines
- Remove: Performance sections (code comments handle this)
- Remove: Detailed error scenarios (code comments handle this)

**Savings**: ~400 lines per file × 4 = ~1,600 lines

---

### Fix 6: Create Consolidated Documentation

#### Create: docs/TESTING_PLAN.md

**Content**:
```markdown
# Testing Plan - Token Golf

Phase 7 will implement comprehensive testing.

## Test Structure
- Unit tests: app/tests/unit/
- Integration tests: app/tests/integration/
- Challenge validation: app/tests/challenges/

## Services to Test
- ChallengeLoaderService (Phase 2.1)
- LLMClient + MockLLMClient (Phase 2.2)
- ValidatorService (Phase 2.3)
- ScoringService (Phase 2.4)

## Coverage Target
- Services: >80% coverage
- Models: >90% coverage
- API endpoints: 100% coverage

## Test Examples
[Move all test examples from phase docs here]
```

#### Create: docs/SERVICE_INTEGRATION.md

**Content**:
```markdown
# Service Integration Guide

How Token Golf services work together.

## Complete Flow

```python
# 1. Load challenge
challenge = await challenge_loader.get_challenge("hole-001")

# 2. Get LLM response
llm_response = await llm_client.complete(prompt, system_prompt)

# 3. Validate
validation = await validator.validate(challenge, llm_response.response_text)

# 4. Record score
attempt = await scoring.record_attempt(
    user_id=user_id,
    input_tokens=llm_response.input_tokens,
    output_tokens=llm_response.output_tokens,
    is_correct=validation.is_correct
)
```

## Service Dependencies
[Diagram or list]

## Integration Points
[Details from phase docs consolidated here]
```

**Savings**: Allows removal of ~400 lines from phase docs

---

## Minor Fixes (Do Last - 20 min)

### Fix 7: Update Line Counts

**Files**:
- PHASE_2.2_COMPLETE.md: Change "370 lines" → "357 lines"
- PHASE_2.3_COMPLETE.md: Change "407 lines" → "439 lines"

### Fix 8: Add Missing Files to CLAUDE.md

**Line 117** (in services section), add:
```markdown
├── services/
│   ├── __init__.py
│   ├── challenge_loader.py  # Challenge YAML loading (Phase 2.1)
│   ├── llm_client.py        # LLM API integration (Phase 2.2)
│   ├── validator.py         # Answer validation (Phase 2.3)
│   ├── scoring.py           # Token counting & scoring (Phase 2.4)
│   └── name_generator.py    # User name generation (Phase 6 - TODO)
```

**After line 126**, add:
```markdown
├── database.py              # SQLAlchemy async session management
```

### Fix 9: Mark Unimplemented Commands in CLAUDE.md

**Lines 461-494** (Development Commands section):

Add status markers:
```markdown
## Common Development Commands

# Setup ✅ Works
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run development server ✅ Works
uvicorn app.main:app --reload --port 8000

# Run tests ⏳ Phase 7
pytest tests/

# Create new challenge ⏳ Phase 6
python scripts/new_challenge.py --id hole-042
```

---

## Summary

### Total Fixes: 9

| Fix | Time | Lines Saved | Priority |
|-----|------|-------------|----------|
| 1. Update PROJECT_STATUS | 5 min | 0 | Critical |
| 2. Check DEVELOPMENT_PHASES boxes | 10 min | 0 | Critical |
| 3. Add current state to CLAUDE | 15 min | 0 | Critical |
| 4. Remove test repetition | 15 min | 200 | High |
| 5. Compress verbose sections | 30 min | 1,600 | High |
| 6. Create consolidated docs | 15 min | 400 | High |
| 7. Update line counts | 2 min | 0 | Low |
| 8. Add missing files to CLAUDE | 3 min | 0 | Low |
| 9. Mark unimplemented commands | 5 min | 0 | Low |
| **Total** | **~100 min** | **~2,200** | - |

### Expected Results

**Before**:
- Outdated status files (says Phase 0, actually Phase 2.4)
- 5,234 lines of phase documentation
- 1,940 lines of repetition
- Confusion about what exists vs what's planned

**After**:
- Accurate status files
- ~3,000 lines of phase documentation (42% reduction)
- No repetition, consolidated reference docs
- Clear separation: current vs future state

---

## Ready to Start?

**Suggested Order**:
1. Fixes 1-3 (Critical, 30 min)
2. Fix 4 (Remove test repetition, 15 min)
3. Fix 6 (Create consolidated docs, 15 min)
4. Fix 5 (Compress verbose sections, 30 min)
5. Fixes 7-9 (Minor polish, 10 min)

**Total**: ~100 minutes working together

Let's start?
