# ADR 004: Database Migrations with Alembic

## Status

Accepted

## Context

Token Golf uses SQLAlchemy as its ORM for database operations. As development progresses, the database schema will evolve:
- Adding new tables
- Modifying existing columns
- Creating indexes
- Changing relationships

We need a way to manage these schema changes that:
- Preserves data during schema updates
- Allows rollback if something goes wrong
- Keeps dev and production databases in sync
- Version controls schema changes
- Works with both SQLite (dev) and PostgreSQL (prod)

### Options for Schema Management

1. **Manual SQL scripts** - Write and run SQL by hand
2. **Recreate database** - Drop and recreate on every change (lose data)
3. **Migration tool** - Use a tool like Alembic or Django migrations

## Decision

We will use **Alembic** for database migrations from the start of development.

### Implementation Approach
- Initialize Alembic during project setup
- Auto-generate migrations from model changes
- Review and test all migrations before committing
- Store migrations in version control
- Apply migrations as part of deployment process

## Rationale

### Why Alembic?

1. **Official SQLAlchemy Tool**: Maintained by the SQLAlchemy team
2. **Auto-generation**: Can generate migrations from model changes
3. **Bidirectional**: Supports upgrade and downgrade
4. **Well-Documented**: Extensive documentation and examples
5. **FastAPI Ecosystem**: Commonly used with FastAPI projects
6. **Production Ready**: Battle-tested in production systems

### Why From the Start?

1. **Better Habits**: Learn proper migration workflow early
2. **Avoid Pain Later**: Adding migrations to existing DB is harder
3. **Team Learning**: Team learns the tool while stakes are low
4. **Production Path**: Smooth path from dev to production
5. **Data Preservation**: Even dev data can be valuable to keep

## Consequences

### Positive Consequences

- **Data Safety**: Schema changes don't lose data
- **Reversible**: Can rollback bad migrations
- **Auditable**: Migration history shows all schema changes
- **Team Coordination**: All developers apply same migrations
- **CI/CD Ready**: Migrations integrate into deployment pipeline
- **Cross-Database**: Works with SQLite → PostgreSQL migration
- **Professional**: Industry-standard approach

### Negative Consequences

- **Initial Setup**: Requires Alembic configuration upfront
- **Learning Curve**: Team needs to learn Alembic commands
- **Extra Step**: Must create migration for every model change
- **Conflicts**: Merge conflicts in migrations (rare but annoying)
- **Testing Overhead**: Should test both upgrade and downgrade paths

### Risks

- **Risk**: Team forgets to create migrations
  - **Mitigation**: Pre-commit hooks to detect model changes without migrations
  - **Likelihood**: Medium - will happen occasionally

- **Risk**: Auto-generated migrations miss edge cases
  - **Mitigation**: Always review auto-generated migrations, test before committing
  - **Likelihood**: Medium - expected with auto-generation

- **Risk**: Migration conflicts in multi-developer scenario
  - **Mitigation**: Clear workflow, communicate DB changes, resolve conflicts early
  - **Likelihood**: Low - small team, good communication

## Alternatives Considered

### Alternative 1: No Migrations (Recreate Database)

- **Description**: Drop and recreate database on every schema change
- **Pros**:
  - No tool to learn
  - Simplest approach
  - No migration files to manage
  - Fast for early development
- **Cons**:
  - Lose all data on every change
  - Can't preserve test data
  - No production migration path
  - Have to recreate from scratch
- **Why not chosen**: Pain increases over time, bad production story

### Alternative 2: Manual SQL Scripts

- **Description**: Write SQL migration scripts by hand
- **Pros**:
  - Full control
  - No tool dependency
  - Simple to understand
- **Cons**:
  - Error-prone (human writes SQL)
  - No auto-generation
  - Tedious for large schemas
  - Hard to rollback
  - Must maintain SQLite and PostgreSQL versions
- **Why not chosen**: Too error-prone, doesn't leverage ORM

### Alternative 3: Add Alembic Later

- **Description**: Start without migrations, add Alembic before production
- **Pros**:
  - Faster initial setup
  - Simpler early development
  - Learn tool when needed
- **Cons**:
  - Must recreate migration history later (painful)
  - Harder to retrofit to existing database
  - Team learns tool under pressure (pre-production)
  - Lose data during transition
- **Why not chosen**: Retrofitting is more painful than starting correctly

## Implementation Notes

### Initial Setup

```bash
# Install Alembic
pip install alembic

# Initialize in project
cd /path/to/project
alembic init alembic

# Configure alembic.ini
# Set sqlalchemy.url or use env variable
```

### Configuration

**alembic.ini**:
```ini
[alembic]
script_location = alembic
sqlalchemy.url = driver://user:pass@localhost/dbname

# Can use env var instead:
# sqlalchemy.url = ${DATABASE_URL}
```

**alembic/env.py**:
```python
from app.models import Base
from app.config import settings

# Set target metadata to your Base
target_metadata = Base.metadata

# Use config from settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
```

### Workflow

**Creating a migration:**
```bash
# Auto-generate from model changes
alembic revision --autogenerate -m "Add user table"

# Review the generated migration in alembic/versions/xxx_add_user_table.py
# Edit if needed

# Apply migration
alembic upgrade head
```

**Rolling back:**
```bash
# Downgrade one revision
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade <revision_id>
```

**Checking status:**
```bash
# Show current revision
alembic current

# Show migration history
alembic history
```

### Development Process

1. **Modify models** in `app/models/`
2. **Generate migration**: `alembic revision --autogenerate -m "description"`
3. **Review migration**: Check generated file in `alembic/versions/`
4. **Test migration**: 
   - `alembic upgrade head` (apply)
   - Test application
   - `alembic downgrade -1` (test rollback)
   - `alembic upgrade head` (reapply)
5. **Commit**: Add migration file to git
6. **Team**: Other developers run `alembic upgrade head`

### Project Structure

```
project/
├── alembic/
│   ├── versions/          # Migration scripts
│   │   ├── 001_initial.py
│   │   ├── 002_add_scores.py
│   │   └── ...
│   ├── env.py            # Alembic environment
│   └── script.py.mako    # Migration template
├── alembic.ini           # Alembic config
├── app/
│   └── models/           # SQLAlchemy models
└── ...
```

### Best Practices

1. **Always review auto-generated migrations** - They can miss things
2. **Test both upgrade and downgrade** - Ensure reversibility
3. **One logical change per migration** - Keep migrations focused
4. **Descriptive names** - "add_user_table" not "migration_1"
5. **Don't modify committed migrations** - Create new ones instead
6. **Backup before production migrations** - Safety first

### SQLite → PostgreSQL Migration

Alembic helps with this transition:
1. Generate migrations using SQLite in dev
2. Test migrations work on both SQLite and PostgreSQL
3. In production, run same migrations against PostgreSQL
4. Most migrations are database-agnostic via SQLAlchemy

## References

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [FastAPI + Alembic Guide](https://fastapi.tiangolo.com/tutorial/sql-databases/#alembic-note)
- [SQLAlchemy Migrations Best Practices](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html)

## Future Considerations

- **Pre-commit hooks**: Detect model changes without migrations
- **CI/CD**: Automated migration testing
- **Production process**: Blue-green deployments with schema changes
- **Data migrations**: Not just schema, but data transformations

---

**Date**: 2026-09-09  
**Author**: Token Golf Team  
**Reviewers**: Karl Eklund
