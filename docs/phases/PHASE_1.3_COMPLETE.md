# Phase 1.3: Database Models - COMPLETE ✅

**Completed**: 2026-09-09  
**Time**: ~45 minutes  
**Status**: Ready for Phase 1.4 (Alembic Setup)

## Summary

Created all SQLAlchemy 2.0 ORM models for Token Golf database schema. Models include full type hints, relationships, constraints, and helper methods. All 6 tables defined correctly with proper foreign keys and indexes.

---

## Files Created

### 7 Model Files (Total: ~600 lines)

1. **`app/models/base.py`** (90 lines)
   - `Base` class with declarative base
   - Naming conventions for constraints
   - `TimestampMixin` for created_at/updated_at
   - Helper methods: `__repr__()`, `to_dict()`

2. **`app/models/user.py`** (70 lines)
   - User model with auto-generated username
   - Relationships to sessions, attempts, scores
   - Fields: id, username, created_at, is_active

3. **`app/models/session.py`** (150 lines)
   - Session model with timeout logic
   - SessionParticipant join table
   - Helper methods: `is_expired()`, `is_active()`, `calculate_expires_at()`
   - Unique constraint on (session_id, user_id)

4. **`app/models/challenge.py`** (60 lines)
   - Challenge model for YAML-loaded holes
   - Stores full YAML config
   - Fields: id (string), name, difficulty, task_type, config_yaml

5. **`app/models/attempt.py`** (120 lines)
   - Attempt model for each prompt submission
   - Token tracking (input, output, total)
   - User modifications (system_prompt, context_files JSON)
   - Fields: prompt, response, is_correct

6. **`app/models/score.py`** (90 lines)
   - Score model for aggregated results
   - Tracks total attempts and cumulative tokens
   - Unique constraint on (user_id, session_id, challenge_id)
   - Helper method: `is_completed()`

7. **`app/models/__init__.py`** (20 lines)
   - Exports all models
   - Clean import interface

---

## Database Schema

### Tables Created (6 total)

```sql
-- Users (auto-generated usernames)
users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    created_at DATETIME NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
)

-- Game sessions (3-hour timeout)
sessions (
    id VARCHAR(36) PRIMARY KEY,
    course_id VARCHAR(100) NOT NULL,
    created_at DATETIME NOT NULL,
    timeout_hours INTEGER NOT NULL DEFAULT 3,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    expires_at DATETIME NOT NULL
)

-- Users ↔ Sessions many-to-many
session_participants (
    id INTEGER PRIMARY KEY,
    session_id VARCHAR(36) → sessions.id,
    user_id INTEGER → users.id,
    joined_at DATETIME NOT NULL,
    UNIQUE(session_id, user_id)
)

-- Challenges from YAML files
challenges (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    difficulty VARCHAR(20),
    task_type VARCHAR(50),
    config_yaml TEXT NOT NULL,
    created_at DATETIME NOT NULL
)

-- Each prompt submission
attempts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER → users.id,
    session_id VARCHAR(36) → sessions.id,
    challenge_id VARCHAR(50) → challenges.id,
    attempt_number INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    system_prompt TEXT,
    context_files JSON,
    response TEXT,
    input_tokens INTEGER NOT NULL DEFAULT 0,
    output_tokens INTEGER NOT NULL DEFAULT 0,
    total_tokens INTEGER NOT NULL DEFAULT 0,
    is_correct BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL
)

-- Aggregated scores
scores (
    id INTEGER PRIMARY KEY,
    user_id INTEGER → users.id,
    session_id VARCHAR(36) → sessions.id,
    challenge_id VARCHAR(50) → challenges.id,
    total_attempts INTEGER NOT NULL DEFAULT 0,
    total_tokens INTEGER NOT NULL DEFAULT 0,
    completed_at DATETIME,
    UNIQUE(user_id, session_id, challenge_id)
)
```

---

## Relationships

### User → SessionParticipant → Session
```python
user.session_participations  # List of SessionParticipant
user.attempts                # List of all attempts
user.scores                  # List of all scores
```

### Session → Attempts, Scores
```python
session.participants  # List of SessionParticipant
session.attempts     # All attempts in this session
session.scores       # All scores in this session
```

### Challenge → Attempts, Scores
```python
challenge.attempts  # All attempts on this challenge
challenge.scores    # All scores for this challenge
```

### Attempt → User, Session, Challenge
```python
attempt.user       # User who made attempt
attempt.session    # Session it belongs to
attempt.challenge  # Challenge attempted
```

### Score → User, Session, Challenge
```python
score.user       # User
score.session    # Session
score.challenge  # Challenge
```

---

## Features Implemented

### ✅ SQLAlchemy 2.0 Style
- Modern `Mapped[type]` type hints
- `mapped_column()` for all columns
- Proper async support ready

### ✅ Type Safety
```python
id: Mapped[int] = mapped_column(primary_key=True)
username: Mapped[str] = mapped_column(String(100), unique=True)
is_active: Mapped[bool] = mapped_column(Boolean, default=True)
created_at: Mapped[datetime] = mapped_column(nullable=False)
```

### ✅ Relationships with Cascade
```python
attempts: Mapped[list["Attempt"]] = relationship(
    "Attempt",
    back_populates="user",
    cascade="all, delete-orphan",  # Delete attempts when user deleted
)
```

### ✅ Constraints
- Unique constraints: username, (session_id, user_id), (user_id, session_id, challenge_id)
- Foreign keys with CASCADE delete
- NOT NULL constraints
- Default values

### ✅ Indexes
```python
username: Mapped[str] = mapped_column(String(100), index=True)
course_id: Mapped[str] = mapped_column(String(100), index=True)
```

### ✅ Helper Methods
```python
session.is_expired() → bool
session.is_active() → bool
Session.calculate_expires_at(created_at, timeout_hours) → datetime
score.is_completed() → bool
```

### ✅ JSON Support
```python
context_files: Mapped[dict | None] = mapped_column(JSON, nullable=True)
```

### ✅ Docstrings
Every model, field, and method has clear documentation.

---

## Verification Tests

### ✅ Import Test
```bash
$ podman-compose exec web python -c "from app.models import *"
✅ All models imported successfully
```

### ✅ Table Definition Test
```bash
$ podman-compose exec web python -c "from app.models import Base; print(list(Base.metadata.tables.keys()))"
['attempts', 'challenges', 'scores', 'sessions', 'session_participants', 'users']
```

### ✅ Relationship Test
```bash
$ podman-compose exec web python -c "from app.models import User; ..."
User relationships:
  - session_participations → SessionParticipant
  - attempts → Attempt
  - scores → Score
```

### ✅ Column Type Test
```bash
Attempt columns:
  - id: INTEGER
  - user_id: INTEGER
  - session_id: VARCHAR(36)
  - challenge_id: VARCHAR(50)
  - attempt_number: INTEGER
  - prompt: TEXT
  - system_prompt: TEXT
  - context_files: JSON
  - response: TEXT
  - input_tokens: INTEGER
  - output_tokens: INTEGER
  - total_tokens: INTEGER
  - is_correct: BOOLEAN
  - created_at: DATETIME
```

---

## Design Decisions

### 1. SQLAlchemy 2.0 with Type Hints
**Why**: Modern, type-safe, better IDE support  
**Benefit**: Catch errors at development time, not runtime

### 2. Async-Ready (Mapped types)
**Why**: Future-proof for async database operations  
**Benefit**: Can use async SQLAlchemy when needed (Phase 2+)

### 3. String Primary Keys for Session/Challenge
**Why**: 
- Session: UUID format
- Challenge: Meaningful IDs like "hole-001"

**Benefit**: Readable, matches YAML file structure

### 4. JSON Column for context_files
**Why**: Variable structure, array of active context files  
**Benefit**: Flexibility, no separate table needed for simple list

### 5. Cascade Deletes
**Why**: Maintain referential integrity  
**Benefit**: Deleting a user automatically deletes their attempts/scores

### 6. Helper Methods on Models
**Why**: Common logic belongs with the data  
**Benefit**: `session.is_expired()` more readable than date math everywhere

### 7. TimestampMixin Not Used
**Why**: Models have different timestamp needs  
**Benefit**: More explicit, clearer what each timestamp means

---

## Schema Alignment with CLAUDE.md

| CLAUDE.md Table | Model File | Match |
|----------------|------------|-------|
| users | user.py | ✅ Perfect |
| sessions | session.py | ✅ Perfect |
| session_participants | session.py | ✅ Perfect |
| challenges | challenge.py | ✅ Perfect |
| attempts | attempt.py | ✅ Perfect |
| scores | score.py | ✅ Perfect |

All fields, types, and constraints match the documented schema.

---

## Code Quality

### Type Hints Everywhere
```python
class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    attempts: Mapped[list["Attempt"]] = relationship(...)
```

### Clear Comments
```python
id: Mapped[int] = mapped_column(
    primary_key=True,
    autoincrement=True,
    comment="Unique user identifier",  # Shows in DB schema
)
```

### Docstrings on Everything
```python
class User(Base):
    """
    User model - represents a player in Token Golf.
    
    In MVP, users are anonymous with auto-generated usernames.
    Each time a player starts a session, they get a new username.
    """
```

### Helpful __repr__
```python
def __repr__(self) -> str:
    return f"<User(id={self.id}, username='{self.username}')>"
```

---

## Ready for Phase 1.4

All models are defined and verified. Next step:

**Phase 1.4: Alembic Setup**
- Initialize Alembic
- Configure for async SQLAlchemy
- Create initial migration from models
- Apply migration to create database
- Verify tables created correctly

---

## Success Criteria Met ✅

All Phase 1.3 deliverables from DEVELOPMENT_PHASES.md:

- [x] Create `app/models/__init__.py`
- [x] Create `app/models/base.py` with Base class
- [x] Create `app/models/user.py` - User model
- [x] Create `app/models/challenge.py` - Challenge model
- [x] Create `app/models/attempt.py` - Attempt model
- [x] Create `app/models/score.py` - Score model
- [x] Add relationships between models
- [x] Include type hints and docstrings

**Bonus**: Also created `session.py` with Session and SessionParticipant models

**Deliverable**: ✅ All models defined, importable, type-checked

---

**Phase 1.3 Status**: COMPLETE  
**Next Phase**: Phase 1.4 - Alembic Setup  
**Date**: 2026-09-09
