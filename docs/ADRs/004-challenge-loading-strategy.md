# ADR 007: Challenge Loading Strategy

## Status

Accepted

## Context

Token Golf needs to load challenge definitions from YAML files in the `challenges/` directory. These challenges must be available to the game engine during gameplay. We need to decide:

1. **When** to load challenges (startup vs on-demand)
2. **Where** to store them (database, memory cache, or both)
3. **How** to handle updates during development vs production

### Key Requirements

**Functional:**
- Fast challenge retrieval during gameplay (< 10ms)
- Support for 50+ challenges without performance degradation
- Validate challenge format before use
- Allow development iteration (edit YAML, see changes)

**Non-Functional:**
- Minimize database queries during gameplay
- Fail fast on invalid challenges (catch errors at startup)
- Support hot-reload in development
- Production-ready caching strategy

**Constraints:**
- Challenges stored as YAML files in git repository
- Database stores parsed challenges (Challenge model)
- Configuration option to control loading behavior

## Decision

We will implement a **hybrid loading strategy** with three-tier caching:

### Three-Tier Caching Strategy

```
1. In-Memory Cache (fastest)
   ↓ (miss)
2. Database (persistent)
   ↓ (miss)
3. YAML File (source of truth)
```

### Loading Modes

#### Mode 1: Preload on Startup (Production)
```python
# Enabled via config: PRELOAD_CHALLENGES=true
@app.on_event("startup")
async def startup_event():
    if settings.preload_challenges:
        await challenge_loader.preload_all_challenges()
```

**Behavior:**
- Scans `challenges/` directory for all `challenge.yaml` files
- Parses each YAML file
- Validates required fields
- Stores in database
- Populates in-memory cache
- **Fails startup if any challenge is invalid**

**Use case:** Production deployments, conference demos

#### Mode 2: Lazy Loading (Development)
```python
# Enabled via config: PRELOAD_CHALLENGES=false
challenge = await challenge_loader.get_challenge("hole-001")
```

**Behavior:**
- Checks in-memory cache first
- Falls back to database
- Falls back to YAML file if not found
- Caches result for future requests
- **Allows adding challenges without restart**

**Use case:** Local development, testing new challenges

### Cache Invalidation

**In-Memory Cache:**
- Cleared on application restart
- Never invalidated during runtime (challenges are immutable once loaded)

**Database:**
- Persists across restarts
- Can be cleared manually for development
- Production: Seeded on deployment

**YAML Files:**
- Source of truth
- Read-only during gameplay
- Modified by developers, committed to git

## Implementation Details

### ChallengeLoaderService

```python
class ChallengeLoaderService:
    def __init__(self, db_session, challenges_dir: Path):
        self._cache: Dict[str, Challenge] = {}
        self._db = db_session
        self._challenges_dir = challenges_dir
    
    async def get_challenge(self, challenge_id: str) -> Challenge:
        """
        Get challenge with three-tier lookup:
        1. In-memory cache
        2. Database
        3. YAML file
        """
        # Tier 1: In-memory cache
        if challenge_id in self._cache:
            return self._cache[challenge_id]
        
        # Tier 2: Database
        db_challenge = await self._get_from_database(challenge_id)
        if db_challenge:
            self._cache[challenge_id] = db_challenge
            return db_challenge
        
        # Tier 3: YAML file
        yaml_challenge = await self._load_from_yaml(challenge_id)
        await self._save_to_database(yaml_challenge)
        self._cache[challenge_id] = yaml_challenge
        return yaml_challenge
    
    async def preload_all_challenges(self) -> int:
        """
        Load all challenges at startup.
        Returns number of challenges loaded.
        Raises exception if any challenge is invalid.
        """
        # Implementation
        pass
    
    async def list_challenges(
        self, 
        difficulty: str | None = None,
        task_type: str | None = None
    ) -> List[Challenge]:
        """List challenges with optional filters"""
        pass
```

### Configuration

Added to `app/config.py`:
```python
preload_challenges: bool = Field(
    default=True,
    description="Preload challenges on startup"
)
```

Added to `.env.example`:
```bash
# Preload all challenges at startup (recommended for production)
PRELOAD_CHALLENGES=true
```

### Directory Structure

```
challenges/
├── hole-001/
│   ├── challenge.yaml    # Loaded into database
│   └── assets/           # Referenced by challenge, not loaded
├── hole-002/
│   └── challenge.yaml
└── courses.yaml          # Future: Course definitions
```

## Rationale

### Why Three-Tier Caching?

**In-Memory Cache:**
- Sub-millisecond lookups during gameplay
- No database queries for frequently accessed challenges
- Acceptable memory footprint (50 challenges ≈ 50KB)

**Database Storage:**
- Survives application restarts
- Provides query capabilities (filter by difficulty, task_type)
- Atomic transactions for consistency
- Migration-friendly (Alembic can version challenges)

**YAML Files:**
- Version controlled (git)
- Human-editable
- Easy to review in PRs
- Portable across environments

### Why Hybrid Loading?

**Production Benefits:**
- Fail-fast: Invalid challenges caught at startup
- Consistent state: All challenges validated before accepting traffic
- Performance: Zero YAML reads during gameplay
- Predictable: No surprise "challenge not found" errors

**Development Benefits:**
- Fast iteration: Edit YAML, restart app (no migration needed)
- Selective loading: Test one challenge without loading all
- Flexibility: Disable preload for faster startup during development

### Why Not Alternatives?

**Alternative 1: YAML-only (no database)**
- ❌ Slow: Parse YAML on every request
- ❌ No query capabilities
- ❌ Harder to filter/search

**Alternative 2: Database-only (migrate challenges)**
- ❌ Poor developer experience (migrations for content changes)
- ❌ Harder to review challenge changes in PRs
- ❌ Not version-controlled naturally

**Alternative 3: Always preload (no lazy loading)**
- ❌ Slow development iteration
- ❌ Can't add challenges without restart
- ❌ Less flexible for testing

## Consequences

### Positive Consequences

- **Fast Gameplay**: In-memory cache ensures < 1ms challenge lookups
- **Fail-Fast**: Preload catches invalid challenges before production traffic
- **Flexible Development**: Lazy loading allows rapid iteration
- **Scalable**: Caching strategy supports 100+ challenges
- **Version Controlled**: YAML files in git, reviewable in PRs
- **Query-Friendly**: Database enables filtering by difficulty/type
- **Testable**: Can mock service, test with fixture challenges

### Negative Consequences

- **Memory Usage**: In-memory cache grows with challenge count (acceptable)
- **Complexity**: Three-tier system is more complex than single-tier
- **Consistency**: Database and YAML can drift in development (mitigated by preload in production)
- **Restart Required**: Production deployments need restart to pick up challenge changes (acceptable)

### Risks

**Risk: Database and YAML drift in development**
- **Mitigation**: Clear database before testing, or always preload
- **Likelihood**: Medium
- **Impact**: Low (dev-only issue)

**Risk: Invalid challenge passes lazy loading but fails preload**
- **Mitigation**: Same validation logic for both paths
- **Likelihood**: Low
- **Impact**: Low (caught in testing)

**Risk: Memory usage with 1000+ challenges**
- **Mitigation**: Monitor memory, add cache size limit if needed
- **Likelihood**: Low (not planning 1000+ challenges)
- **Impact**: Low

## Alternatives Considered

### Alternative 1: Redis Cache
- **Description**: Use Redis instead of in-memory cache
- **Pros**: Shared cache across multiple app instances, survives restarts
- **Cons**: Adds dependency, network latency, overkill for MVP
- **Why not chosen**: In-memory is sufficient for single-instance MVP

### Alternative 2: File Watcher (Hot Reload)
- **Description**: Watch YAML files, reload on changes
- **Pros**: No restart needed in development
- **Cons**: Complex, error-prone, not useful in production
- **Why not chosen**: Restart is acceptable for development workflow

### Alternative 3: Separate Challenge Service
- **Description**: Microservice for challenge management
- **Pros**: Independent scaling, clear separation
- **Cons**: Over-engineered for MVP, adds deployment complexity
- **Why not chosen**: Monolith is simpler for MVP scale

## Implementation Checklist

- [ ] Create `app/services/challenge_loader.py`
- [ ] Implement three-tier caching logic
- [ ] Add `preload_challenges` config option
- [ ] Add startup event handler for preload
- [ ] Implement YAML parsing with validation
- [ ] Add error handling for missing/invalid files
- [ ] Write unit tests for loader service
- [ ] Write integration tests with real YAML files
- [ ] Document usage in DEVELOPMENT_PHASES.md
- [ ] Update PROJECT_STATUS.md when complete

## References

- **Challenge Format**: `/docs/CHALLENGE_FORMAT.md`
- **Database Models**: `/app/models/challenge.py`
- **Configuration**: `/app/config.py`
- **Development Phases**: `/docs/DEVELOPMENT_PHASES.md`

---

**Date**: 2026-09-21  
**Author**: Token Golf Team  
**Status**: Accepted - Ready for implementation
