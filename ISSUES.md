# Token Golf - Known Issues & Technical Debt

**Last Updated**: 2026-09-21  
**Status**: 4 issues logged (3 critical, 1 medium)

---

## Critical Issues (Must Fix Before Production)

### Issue #1: Breaking Change in POST /api/game/start Format
**Priority**: Critical  
**Status**: Open  
**Introduced**: Phase 5 (Agent 4 - API Improvements)  
**Affects**: Frontend authentication flow

**Description:**
API endpoint format changed but frontend templates not updated yet.

**Old Format:**
```json
POST /api/game/start
{
  "generate_new_user": true,
  "course_id": "beginner-course"
}
```

**New Format:**
```json
POST /api/game/start
{
  "action": "generate",  // or "signin"
  "course_id": "beginner-course"
  // For signin, also include:
  // "username": "...",
  // "password": "..."
}
```

**Files Affected:**
- `app/templates/index.html` (lines with htmx form submission)
- Potentially `app/templates/game.html` if it has start game functionality

**Resolution Steps:**
1. Read `app/templates/index.html`
2. Find all instances of form submission to `/api/game/start`
3. Update JavaScript/Alpine.js to use `action` field instead of `generate_new_user`
4. Test in browser
5. Mark issue as resolved

**Related:**
- See `app/api/game.py` lines ~500-600 for new API implementation
- See `docs/phases/PHASE_5_COMPLETE.md` for breaking change details

---

### Issue #2: Password Hashing Migration (SHA256 → Bcrypt)
**Priority**: Critical (Security)  
**Status**: Open  
**Affects**: Production deployment, security

**Description:**
MVP uses SHA256 password hashing for simplicity. This is vulnerable to rainbow table attacks and not suitable for production.

**Current Implementation:**
```python
# app/api/game.py
import hashlib
password_hash = hashlib.sha256(password.encode()).hexdigest()
```

**Required Implementation:**
```python
import bcrypt
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
```

**Resolution Steps:**
1. Add `bcrypt` to `requirements.txt`
2. Update `app/api/game.py`:
   - Replace `hash_password()` function with bcrypt
   - Replace `verify_password()` function with bcrypt
3. Decision: Invalidate existing passwords OR migrate existing hashes
   - Recommendation: Invalidate (simpler, acceptable for MVP→production)
4. Test authentication flow
5. Document in ADR or update ADR 009

**Related:**
- ADR 009: Password Authentication in MVP (documents SHA256 as temporary)
- Security best practices: OWASP Password Storage Cheat Sheet

**Estimated Effort**: 1-2 hours

---

### Issue #3: Browser Testing Not Performed
**Priority**: Critical (Quality)  
**Status**: Blocked by Issue #1  
**Affects**: MVP validation

**Description:**
Frontend templates created and enhanced but not tested in actual browser. Breaking change in API format blocks this testing.

**Test Scenarios Needed:**
1. **Authentication Flow:**
   - Generate new username/password
   - Sign in with existing credentials
   - Invalid credentials handling
   - Session creation

2. **Game Flow:**
   - Load challenge
   - Submit prompt
   - View validation results
   - Pills UI (add/remove context files)
   - System prompt editing
   - Token estimate display
   - Copy-to-clipboard functionality

3. **Leaderboard:**
   - View switching (Global/Per-Hole/Session)
   - Keyboard shortcuts (G/H/S/R)
   - Refresh functionality
   - Data loading/skeleton states

4. **Error Handling:**
   - 404 page
   - 500 error page
   - Weather delay (LLM failure)
   - Session timeout
   - Validation errors

5. **Responsive Design:**
   - Mobile view
   - Tablet view
   - Desktop view
   - Animations at 60fps

**Resolution Steps:**
1. Fix Issue #1 (breaking change)
2. Start development server:
   ```bash
   podman-compose up
   # or
   uvicorn app.main:app --reload
   ```
3. Run through all test scenarios
4. Log any bugs found
5. Fix bugs
6. Re-test
7. Document testing results

**Related:**
- Testing scenarios documented in this issue
- Manual testing checklist (create if needed)

**Estimated Effort**: 4-6 hours (includes bug fixes)

---

## Medium Priority Issues

### Issue #4: Unit & Integration Tests Not Written
**Priority**: Medium (Quality)  
**Status**: Open  
**Affects**: Code quality, confidence in refactoring

**Description:**
Testing infrastructure complete (pytest, fixtures, test stubs) but actual tests not written yet.

**Test Coverage Targets:**
- Models: >90%
- Services: >80%
- API endpoints: 100%
- Overall: >80%

**Tests Needed:**

**Unit Tests (services/):**
- [ ] `test_challenge_loader.py` - YAML parsing, caching, validation, course loading
- [ ] `test_llm_client.py` - Mock client, token counting, error handling
- [ ] `test_validator.py` - Test cases, exact match, code execution, edge cases
- [ ] `test_scoring.py` - Attempt recording, score calculation, leaderboard queries
- [ ] `test_session_manager.py` - Timeout checks, DNF marking, background task

**Integration Tests (api/):**
- [ ] `test_api_challenges.py` - List, get, filtering, pagination
- [ ] `test_api_game.py` - Start, submit, status, auth flows, errors
- [ ] `test_api_leaderboard.py` - Global, per-hole, session views

**E2E Tests:**
- [ ] `test_complete_game_flow.py` - Full user journey (auth → play → complete)
- [ ] `test_multiplayer_session.py` - Multiple users in same session
- [ ] `test_session_timeout.py` - Session expires correctly

**Current Status:**
- ✅ pytest.ini configured
- ✅ conftest.py with comprehensive fixtures
- ✅ tests/test_integration.py with 15 placeholder tests
- ⏳ No actual test implementations yet

**Resolution Steps:**
1. Start with critical path: E2E test (complete game flow)
2. Then integration tests (API endpoints)
3. Then unit tests (services)
4. Run with coverage: `pytest --cov=app tests/`
5. Fix any failing tests
6. Ensure >80% coverage

**Related:**
- `tests/README.md` - Testing guide
- `tests/conftest.py` - Available fixtures
- `docs/TESTING_PLAN.md` - Testing strategy

**Estimated Effort**: 8-12 hours (Phase 7 work)

---

## Technical Debt (Future Considerations)

### Potential Future Issues:

1. **Name Generator Refactoring**
   - Currently inline in `app/api/game.py`
   - Could be extracted to `app/services/name_generator.py`
   - Not critical, works fine as-is
   - Estimated: 1 hour

2. **Error Logging Enhancement**
   - Add structured logging (JSON format)
   - Add request ID tracking
   - Add performance metrics
   - Estimated: 2-3 hours

3. **Rate Limiting**
   - No rate limiting currently
   - Production should have API rate limits
   - Prevents abuse, DDoS
   - Estimated: 2-3 hours

4. **WebSocket Support (Future)**
   - Real-time leaderboard updates
   - Not in MVP scope
   - Would require significant refactoring
   - Estimated: 8-12 hours

5. **Offline Mode (Future)**
   - Not in MVP scope
   - Requires service worker, IndexedDB
   - Complex feature
   - Estimated: 12-16 hours

---

## Issue Resolution Workflow

1. **Create Issue**: Document in this file with all details
2. **Prioritize**: Critical → Medium → Low
3. **Assign**: Note who's working on it (if applicable)
4. **Track**: Update status (Open → In Progress → Blocked → Resolved)
5. **Resolve**: Fix the issue, test, document
6. **Close**: Mark as Resolved, note resolution date
7. **Review**: Periodically review this file, archive old issues

---

## Issue Status Legend

- **Open**: Issue identified, not started
- **In Progress**: Actively being worked on
- **Blocked**: Cannot proceed due to dependency
- **Resolved**: Fixed and tested
- **Won't Fix**: Decided not to fix (document reason)
- **Duplicate**: Same as another issue

---

## Contact

For questions about these issues:
- See related documentation files linked in each issue
- Check ADRs in `docs/ADRs/`
- Review phase completion docs in `docs/phases/`

---

**Next Review**: After Phase 7 completion
