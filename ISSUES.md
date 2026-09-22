# Token Golf - Known Issues & Technical Debt

**Last Updated**: 2026-09-22  
**Status**: 3 issues logged (2 critical, 1 medium)  
**Recently Resolved**: 1 critical (Issue #1)

---

## Critical Issues (Must Fix Before Production)

### Issue #1: Breaking Change in POST /api/game/start Format
**Priority**: Critical  
**Status**: ✅ **RESOLVED** (2026-09-22)  
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

**Resolution** (2026-09-22):
Fixed in browser testing session. Root cause was htmx sending form-encoded data instead of JSON.

**Changes Made:**
1. Added htmx JSON encoding extension to `base.html`
2. Added `hx-ext="json-enc"` to Generate Username button (line 101)
3. Added `hx-ext="json-enc"` to Sign In form (line 218)
4. Both forms now properly send JSON with `{"action": "generate"}` or `{"action": "signin"}`

**Files Modified:**
- `app/templates/base.html:16` - Added json-enc.js script
- `app/templates/index.html:101, 218` - Added hx-ext attribute

**Verified**: User creation and sign-in now working in browser.

**Related:**
- See `docs/sessions/SESSION_2026-09-22_FIXES.md` for full testing session details
- See Bug #3 in that document for technical details

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
**Status**: ✅ **PARTIALLY RESOLVED** (2026-09-22)  
**Progress**: Core flow tested and working, comprehensive testing remains  
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

**Progress Update** (2026-09-22):
✅ **Tested and Working:**
- Authentication flow (generate username, sign in)
- Session creation
- Challenge loading (hole-001)
- Prompt submission
- LLM integration
- Validation (exact_match type)
- Score recording
- Global leaderboard display

🔧 **Found and Fixed 7 Bugs:**
1. Python 3.13/3.14 incompatibility
2. Invalid Claude model name
3. Generate username button broken (htmx JSON)
4. Missing template variables
5. Template using wrong data source
6. Exact match validation always failing
7. Empty leaderboard (field name mismatch)

⏳ **Still Need to Test:**
- Test cases validation type
- Pills UI (context files, system prompts)
- Error pages (404, 500, weather delay)
- Session timeout
- Keyboard shortcuts
- Mobile responsive design
- Challenge navigation
- All leaderboard views (per-hole, session)

**Next Steps:**
1. Test remaining scenarios above
2. Fix any new bugs found
3. Complete comprehensive browser testing per original list

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
