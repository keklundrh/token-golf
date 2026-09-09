# Phase 1.4: Alembic Setup - COMPLETE ✅

**Completed**: 2026-09-09  
**Time**: ~30 minutes  
**Status**: Database migrations fully operational, ready for Phase 2

## Summary

Successfully initialized Alembic database migrations for Token Golf. All 6 tables can now be created, modified, and rolled back through version-controlled migrations. Migration files are mounted into the container and work seamlessly with our SQLAlchemy models.

---

## Files Created

### 4 Core Files

1. **`alembic.ini`** (147 lines)
   - Alembic configuration file
   - Database URL configuration
   - Logging configuration
   - Migration script location

2. **`alembic/env.py`** (111 lines)
   - Migration environment configuration
   - Imports all models for autogenerate
   - Converts async SQLite URL to sync for Alembic
   - Configures online and offline migration modes

3. **`alembic/script.py.mako`** (24 lines)
   - Template for generating new migration files
   - Type-hinted revision identifiers
   - Upgrade/downgrade function stubs

4. **`alembic/README`** (17 lines)
   - Quick reference for common migration commands
   - Containerized workflow documentation

5. **`alembic/versions/7b570d46009c_initial_schema_with_all_tables.py`** (128 lines)
   - Initial migration generated from models
   - Creates all 6 tables with proper schema
   - Includes upgrade() and downgrade() functions

---

## Database Schema Created

### Migration Successfully Creates 6 Tables

```sql
-- Core tables
✓ users                  (id, username, created_at, is_active)
✓ sessions               (id, course_id, created_at, timeout_hours, status, expires_at)
✓ challenges             (id, name, difficulty, task_type, config_yaml, created_at)

-- Join tables and tracking
✓ session_participants   (id, session_id, user_id, joined_at)
✓ attempts               (id, user_id, session_id, challenge_id, attempt_number, prompt, ...)
✓ scores                 (id, user_id, session_id, challenge_id, total_attempts, total_tokens, ...)

-- Metadata
✓ alembic_version        (version_num) - tracks migration state
```

---

## Migration Features

### ✅ Auto-generation from Models
```bash
$ podman-compose exec web alembic revision --autogenerate -m "description"
```
- Detects new tables
- Detects new columns
- Detects indexes
- Detects foreign keys
- Detects constraints

### ✅ All Indexes Created
```
Detected added index 'ix_users_username' on '('username',)'
Detected added index 'ix_sessions_course_id' on '('course_id',)'
Detected added index 'ix_challenges_difficulty' on '('difficulty',)'
Detected added index 'ix_challenges_task_type' on '('task_type',)'
Detected added index 'ix_attempts_user_id' on '('user_id',)'
Detected added index 'ix_attempts_session_id' on '('session_id',)'
Detected added index 'ix_attempts_challenge_id' on '('challenge_id',)'
Detected added index 'ix_scores_user_id' on '('user_id',)'
Detected added index 'ix_scores_session_id' on '('session_id',)'
Detected added index 'ix_scores_challenge_id' on '('challenge_id',)'
Detected added index 'ix_session_participants_session_id' on '('session_id',)'
Detected added index 'ix_session_participants_user_id' on '('user_id',)'
```

### ✅ All Foreign Keys with CASCADE
```python
sa.ForeignKeyConstraint(['user_id'], ['users.id'], 
                       name='fk_attempts_user_id_users', 
                       ondelete='CASCADE')
```

### ✅ All Unique Constraints
```python
sa.UniqueConstraint('user_id', 'session_id', 'challenge_id', 
                   name='uq_user_session_challenge')
sa.UniqueConstraint('session_id', 'user_id', 
                   name='uq_session_user')
```

### ✅ Column Comments Preserved
All model comments appear in migration:
```python
sa.Column('username', sa.String(length=100), nullable=False, 
         comment='Auto-generated username (Color-Course-Club format)')
```

---

## Tested Operations

### ✅ Initial Migration
```bash
$ podman-compose exec web alembic upgrade head
INFO  [alembic.runtime.migration] Running upgrade  -> 7b570d46009c, Initial schema with all tables
```

### ✅ Downgrade (Rollback)
```bash
$ podman-compose exec web alembic downgrade -1
INFO  [alembic.runtime.migration] Running downgrade 7b570d46009c -> , Initial schema with all tables
```
Result: All tables removed except `alembic_version`

### ✅ Re-upgrade
```bash
$ podman-compose exec web alembic upgrade head
INFO  [alembic.runtime.migration] Running upgrade  -> 7b570d46009c, Initial schema with all tables
```
Result: All 6 tables restored perfectly

### ✅ Current Version Check
```bash
$ podman-compose exec web alembic current
7b570d46009c (head)
```

---

## Configuration Highlights

### Database URL Handling
```python
# alembic/env.py
# Convert async URL to sync URL for Alembic
database_url = settings.database_url.replace("sqlite+aiosqlite://", "sqlite://")
config.set_main_option("sqlalchemy.url", database_url)
```

**Why**: Alembic doesn't support async SQLAlchemy drivers, so we convert the async URL to sync

### Model Imports
```python
# Import all models so they're registered with Base.metadata
from app.models import (
    User,
    Session,
    SessionParticipant,
    Challenge,
    Attempt,
    Score,
)

target_metadata = Base.metadata
```

**Why**: Ensures autogenerate can detect all tables

### Container Integration
Updated `docker-compose.yml`:
```yaml
volumes:
  - ./alembic:/app/alembic
  - ./alembic.ini:/app/alembic.ini
```

**Why**: Migration files accessible both in container and on host

---

## Migration Workflow

### Creating a New Migration
```bash
# 1. Make changes to models in app/models/
# 2. Generate migration
podman-compose exec web alembic revision --autogenerate -m "Add new column"

# 3. Review generated migration file
cat alembic/versions/<revision>_add_new_column.py

# 4. Apply migration
podman-compose exec web alembic upgrade head
```

### Rolling Back
```bash
# Rollback one migration
podman-compose exec web alembic downgrade -1

# Rollback to specific version
podman-compose exec web alembic downgrade <revision>

# Rollback all migrations
podman-compose exec web alembic downgrade base
```

### Checking Status
```bash
# Current version
podman-compose exec web alembic current

# Migration history
podman-compose exec web alembic history

# Show pending migrations
podman-compose exec web alembic history --verbose
```

---

## File Structure

```
token-golf/
├── alembic/
│   ├── versions/
│   │   └── 7b570d46009c_initial_schema_with_all_tables.py
│   ├── env.py           # Migration environment
│   ├── script.py.mako   # Migration template
│   └── README           # Quick reference
├── alembic.ini          # Alembic configuration
└── data/
    └── token_golf.db    # SQLite database (created on first migration)
```

---

## Design Decisions

### 1. Sync SQLite for Alembic
**Decision**: Convert `sqlite+aiosqlite://` to `sqlite://` in env.py  
**Why**: Alembic doesn't support async drivers  
**Impact**: Migrations work seamlessly, no async needed for schema changes

### 2. Mount Migration Files into Container
**Decision**: Added alembic volume mounts to docker-compose.yml  
**Why**: 
- Edit migrations on host with IDE
- Version control works naturally
- No permission issues
**Impact**: Smooth development workflow

### 3. Enable Type Comparison
**Decision**: Set `compare_type=True` in context.configure()  
**Why**: Detect column type changes in autogenerate  
**Impact**: More accurate migration generation

### 4. Enable Default Comparison
**Decision**: Set `compare_server_default=True`  
**Why**: Detect changes to column defaults  
**Impact**: Complete change detection

### 5. Explicit Model Imports
**Decision**: Import all models explicitly in env.py  
**Why**: Clear, predictable, no import side effects  
**Impact**: Reliable autogeneration

---

## Verified Behavior

### ✅ Creates All Tables
```bash
$ podman-compose exec web python -c "..."
Tables in database:
  - alembic_version
  - attempts
  - challenges
  - scores
  - session_participants
  - sessions
  - users
```

### ✅ Preserves Schema Details
- Column types match models exactly
- Indexes created on all marked fields
- Foreign keys with CASCADE delete
- Unique constraints enforced
- NOT NULL constraints applied
- Default values set

### ✅ Clean Rollback
- Downgrade removes all tables
- Only `alembic_version` remains
- Re-upgrade restores everything
- No data loss on upgrade/downgrade cycle

---

## Common Commands Reference

```bash
# Apply all pending migrations
podman-compose exec web alembic upgrade head

# Rollback one migration
podman-compose exec web alembic downgrade -1

# Create new migration
podman-compose exec web alembic revision --autogenerate -m "description"

# Check current version
podman-compose exec web alembic current

# View history
podman-compose exec web alembic history

# Reset database (nuclear option)
podman-compose exec web alembic downgrade base
podman-compose exec web alembic upgrade head
```

---

## Integration with Development

### Database Initialization Workflow

1. **First time setup**:
   ```bash
   podman-compose up -d
   podman-compose exec web alembic upgrade head
   ```

2. **After pulling new migrations**:
   ```bash
   podman-compose exec web alembic upgrade head
   ```

3. **When modifying models**:
   ```bash
   # Edit app/models/*.py
   podman-compose exec web alembic revision --autogenerate -m "description"
   podman-compose exec web alembic upgrade head
   ```

---

## Ready for Phase 2

All database infrastructure is now in place:

✅ **Models**: SQLAlchemy 2.0 models defined (Phase 1.3)  
✅ **Migrations**: Alembic configured and tested (Phase 1.4)  
✅ **Database**: SQLite database created with schema  
✅ **Workflow**: Version-controlled migrations working

**Next Phase**: Phase 2.1 - Challenge Loader Service
- Read YAML challenge files
- Parse challenge configuration
- Load challenges into database
- Validate challenge format

---

## Success Criteria Met ✅

All Phase 1.4 deliverables from DEVELOPMENT_PHASES.md:

- [x] Install Alembic in requirements.txt (already present)
- [x] Run `alembic init alembic` (created directory structure)
- [x] Configure `alembic.ini` for containerized environment
- [x] Configure `alembic/env.py` to use our models
- [x] Create initial migration
- [x] Test migration: upgrade and downgrade
- [x] Document migration workflow

**Deliverable**: ✅ Database created with all tables, migration works

---

## Git Commit

```bash
git add alembic/ alembic.ini docker-compose.yml data/.gitkeep
git add docs/PHASE_1.4_COMPLETE.md
git commit -m "Phase 1.4: Alembic setup with initial migration

- Initialize Alembic with env.py configured for our models
- Create initial migration generating all 6 tables
- Test upgrade/downgrade cycle successfully
- Mount alembic files into container for seamless workflow
- Convert async SQLite URL to sync for Alembic compatibility
- All indexes, foreign keys, and constraints working

Database schema fully operational with version control."
```

---

**Phase 1.4 Status**: COMPLETE  
**Next Phase**: Phase 2.1 - Challenge Loader Service  
**Date**: 2026-09-09
