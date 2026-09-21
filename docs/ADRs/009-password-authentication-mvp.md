# ADR 009: Password Authentication in MVP

## Status

Accepted (supersedes ADR 005 authentication section)

## Context

ADR 005 originally specified "No persistent authentication for MVP" with auto-generated usernames only. During Phase 3.2 implementation (2026-09-21), we added password authentication to support both:
- New users generating credentials
- Returning users signing in with username/password

This decision was made pragmatically during implementation but was not documented in an ADR, creating inconsistency between ADR 005 and the actual codebase.

### Requirements Driving Change
1. **Conference demos need repeatability** - Presenters want to resume the same user across browser restarts
2. **User request** - Players want to continue their session after a break
3. **Low friction still required** - Can't require email, verification, or password recovery for MVP
4. **Implementation simplicity** - Must work with SQLite, no external auth service

### Technical Implementation (as built in Phase 3.2)
- Username format: `{Color}-{GolfCourse}-{ClubNumber}` (e.g., "Blue-Pebblebeach-7")
- Password storage: SHA256 hashing (MVP only - see security note)
- Two authentication flows:
  1. **Generate New**: Auto-generate username + random password, display to user
  2. **Sign In**: Username + password form validation
- No password recovery, no email, no account management
- Username uniqueness enforced at database level

## Decision

**Include password authentication in MVP with these constraints:**

1. **Authentication flows**:
   - Users can generate new credentials (username + password auto-generated)
   - Users can sign in with existing username + password
   - No password reset/recovery (users must generate new account)
   - No email addresses required

2. **Password storage**:
   - **MVP**: SHA256 hashing (simple, sufficient for demo environment)
   - **Post-MVP**: Migrate to bcrypt or argon2 before production deployment
   - Database field: `users.password_hash` (nullable for backward compatibility)

3. **Username generation**:
   - Format: `{Color}-{GolfCourse}-{ClubNumber}`
   - Examples: "Blue-Pebblebeach-7", "Green-Augusta-3", "Red-Standrews-14"
   - Uniqueness enforced by database constraint
   - Filter inappropriate combinations
   - Implemented in `app.api.game.generate_username()`

4. **UI/UX**:
   - Home page shows two options: "Generate New" and "Sign In"
   - Generated credentials displayed in copy-able boxes
   - Clear messaging: "Save these credentials - no password recovery available"
   - Session storage for session_id persistence

5. **Session management**:
   - POST /api/game/start handles both auth flows
   - Returns session_id + user info
   - Browser stores session_id in sessionStorage
   - 3-hour session timeout (existing ADR 005 decision)

## Consequences

### Positive Consequences

**Better UX for conferences:**
- Presenters can prepare demos with known credentials
- Players can take breaks without losing progress
- Reduces friction of "lost my random username"
- Still simple (no email, verification, recovery complexity)

**Sufficient security for MVP:**
- SHA256 prevents plaintext password leaks
- Good enough for conference demos (low-stakes environment)
- Clear migration path to production-grade hashing

**Backward compatible:**
- password_hash field is nullable
- Existing usernames without passwords still work
- Can add passwords to existing users later

**Implementation simplicity:**
- No external dependencies (email service, auth provider)
- Works entirely with SQLite
- Fast to implement (~50 lines of code)

### Negative Consequences

**Security limitations:**
- SHA256 is not ideal for password hashing (vulnerable to rainbow tables)
- No rate limiting on login attempts (MVP acceptable)
- No password strength requirements (auto-generated are strong)
- No multi-factor authentication

**User experience limitations:**
- No password recovery (must create new account)
- No account management UI
- No email notifications
- Can't link multiple sessions to one identity

**Technical debt:**
- Must migrate to bcrypt/argon2 before production
- Password hashing migration needs planning
- May need to invalidate existing passwords on migration

### Risks

**Risk: Password database leak**
- Likelihood: Low (MVP deployment, conference environment only)
- Impact: Medium (SHA256 hashed, but not ideal)
- Mitigation: Clear migration to bcrypt before production, use HTTPS, limit deployment scope
- Acceptance: Acceptable for MVP, must fix for production

**Risk: Users forget passwords with no recovery**
- Likelihood: High
- Impact: Low (just generate new account, low stakes)
- Mitigation: Clear UI messaging, copy-to-clipboard for credentials
- Acceptance: Acceptable for MVP - if this becomes pain point, add recovery

**Risk: Implementation doesn't match ADR 005**
- Likelihood: Already occurred
- Impact: Medium (documentation confusion)
- Mitigation: This ADR supersedes ADR 005 authentication section
- Acceptance: Resolved by this ADR

## Alternatives Considered

### Alternative 1: No Authentication (Original ADR 005)
- **Description**: Auto-generated usernames only, new username each session
- **Pros**: Simplest implementation, zero auth complexity
- **Cons**: Can't resume sessions, frustrating for demos, users lose progress
- **Why not chosen**: Conference presenter feedback requested resumability

### Alternative 2: External OAuth (GitHub, Google)
- **Description**: Use third-party OAuth for authentication
- **Pros**: Production-grade security, password reset handled externally
- **Cons**: Requires internet, external dependency, complex setup, user friction
- **Why not chosen**: Too heavy for MVP, adds deployment complexity

### Alternative 3: Email-Based Authentication
- **Description**: Email + password, send verification emails
- **Pros**: Standard auth pattern, password recovery possible
- **Cons**: Requires email service, verification flow, password reset flow, more UI
- **Why not chosen**: Too much complexity for MVP conference demos

### Alternative 4: Session Tokens Only (Magic Links)
- **Description**: Generate long-lived tokens, bookmark to return
- **Pros**: No passwords, simple
- **Cons**: Token loss = account loss, hard to type/share, awkward UX
- **Why not chosen**: Worse UX than username/password for humans

### Alternative 5: Bcrypt from Start
- **Description**: Use bcrypt for password hashing in MVP
- **Pros**: Production-ready from day one
- **Cons**: Slower (noticeable in SQLite), requires additional Python dependency
- **Why not chosen**: Premature optimization, SHA256 sufficient for MVP scope

## Implementation Notes

### Database Migration
Alembic migration `002_add_password_hash.py`:
```python
def upgrade():
    op.add_column('users', sa.Column('password_hash', sa.String(), nullable=True))

def downgrade():
    op.drop_column('users', 'password_hash')
```

### Password Hashing (MVP)
```python
import hashlib

def hash_password(password: str) -> str:
    """SHA256 hash for MVP. TODO: Migrate to bcrypt before production."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against SHA256 hash."""
    return hash_password(password) == password_hash
```

### Migration Path to Production
Before production deployment:
1. Install bcrypt: `pip install bcrypt`
2. Replace hash_password() and verify_password() with bcrypt
3. Add migration to rehash existing passwords (requires plaintext - warn users)
4. OR: Invalidate all passwords, force users to reset (simpler, acceptable for demo→prod)

### API Endpoints
```python
POST /api/game/start
{
  "action": "generate",  # or "signin"
  "course_id": "beginner-course",
  
  # For signin only:
  "username": "Blue-Pebblebeach-7",
  "password": "generated-or-user-provided"
}

Response:
{
  "session_id": "uuid",
  "user_id": 123,
  "username": "Blue-Pebblebeach-7",
  "password": "auto-generated-xyz"  # Only on generate
}
```

## Security Considerations

### Acceptable for MVP
- Conference environment (known users, temporary)
- Low-stakes data (game scores, not financial/personal)
- Short-lived deployments (event duration only)
- HTTPS required (prevents plaintext interception)
- No internet exposure (local network only)

### Required for Production
- Bcrypt or argon2 password hashing
- Rate limiting on login attempts (prevent brute force)
- Password strength requirements
- HTTPS enforced
- Consider password recovery mechanism
- Audit logging for auth events
- Account lockout after failed attempts

## References

- ADR 005: Session Management and MVP Scope (superseded in part)
- ADR 004: Database Migrations with Alembic (migration strategy)
- Phase 3.2 Implementation: `app/api/game.py` (actual implementation)
- OWASP Password Storage Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html

## Update to ADR 005

**This ADR supersedes the authentication section of ADR 005.** 

ADR 005 line 59-65 specified "No persistent authentication for MVP". This is now changed to:
- **Authentication IS in MVP** with username + password
- **SHA256 hashing for MVP** (migrate to bcrypt for production)
- **Both generate and sign-in flows** supported
- All other ADR 005 decisions remain valid (session structure, storage granularity, edit persistence)

---

**Date**: 2026-09-21  
**Author**: Token Golf Team  
**Status**: Accepted (supersedes ADR 005 authentication section)  
**Implementation**: Phase 3.2 (already built)
