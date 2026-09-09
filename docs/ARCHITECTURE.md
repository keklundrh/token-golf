# Token Golf - System Architecture

## Overview

Token Golf is a web-based educational game built with a Python backend and minimal JavaScript frontend. The architecture is designed for:
- Simple local development
- Easy deployment to OpenShift
- Future scalability to handle conference-scale concurrent users
- Clear separation of concerns

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         User Browser                         │
│                                                              │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────────────┐ │
│  │   HTML     │  │  Alpine.js  │  │      htmx            │ │
│  │ Templates  │  │  (Pills UI) │  │  (AJAX Updates)      │ │
│  └────────────┘  └─────────────┘  └──────────────────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/AJAX
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Server                          │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                     API Layer                           │ │
│  │  /api/challenges  /api/game  /api/leaderboard          │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                  Service Layer                          │ │
│  │  ┌──────────┐  ┌───────────┐  ┌─────────────────────┐ │ │
│  │  │ LLM      │  │ Validator │  │  Scoring & Token    │ │ │
│  │  │ Client   │  │ Service   │  │  Counting Service   │ │ │
│  │  └──────────┘  └───────────┘  └─────────────────────┘ │ │
│  │  ┌──────────┐  ┌───────────┐  ┌─────────────────────┐ │ │
│  │  │ Name     │  │ Challenge │  │  Session            │ │ │
│  │  │ Generator│  │ Loader    │  │  Manager            │ │ │
│  │  └──────────┘  └───────────┘  └─────────────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                   Data Layer                            │ │
│  │              SQLAlchemy ORM Models                      │ │
│  └────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     SQLite / PostgreSQL                      │
│  Tables: users, challenges, attempts, scores                │
└─────────────────────────────────────────────────────────────┘

                            │
┌─────────────────────────────────────────────────────────────┐
│                   External Services                          │
│                                                              │
│  ┌──────────────────┐         ┌──────────────────────────┐ │
│  │   Claude API     │         │   OpenShift AI           │ │
│  │  (Development)   │   OR    │  (Production)            │ │
│  └──────────────────┘         └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

                            │
┌─────────────────────────────────────────────────────────────┐
│                    Challenge Files                           │
│                 (YAML + Assets in Git)                       │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend Layer

#### HTML Templates (Jinja2)
- Server-rendered templates
- Minimal client-side logic
- Responsive design for projection screens and laptops
- Located in `app/templates/`

**Key Templates:**
- `base.html` - Base layout with common elements
- `game.html` - Main game interface (problem + interaction + metrics)
- `leaderboard.html` - Leaderboard views
- `components/` - Reusable components (pills, stat cards, etc.)

#### Alpine.js
- Lightweight JavaScript framework (15kb)
- Powers the pill UI (add/remove context files)
- Form state management
- Toggle visibility
- No build step required

#### htmx
- AJAX requests without writing JavaScript
- Partial page updates
- Real-time leaderboard updates
- WebSocket support for future real-time features

### Backend Layer

#### FastAPI Application
- Async request handling
- Automatic OpenAPI documentation
- Built-in validation with Pydantic
- WebSocket support for future features

**Main Responsibilities:**
- Serve HTML templates
- Handle API requests
- Manage game sessions
- Coordinate LLM interactions
- Calculate scores

#### API Endpoints

```
GET  /                          # Home page / game lobby
GET  /game/{session_id}         # Game interface
GET  /leaderboard               # Leaderboard views

POST /api/game/start            # Start new game session
POST /api/game/submit           # Submit prompt attempt
GET  /api/game/status/{session} # Get current game state

GET  /api/challenges            # List available challenges
GET  /api/challenges/{id}       # Get specific challenge

GET  /api/leaderboard/global    # Global leaderboard
GET  /api/leaderboard/hole/{id} # Per-hole leaderboard
GET  /api/leaderboard/session   # Current session leaderboard

GET  /api/user/stats            # Current user statistics
```

### Service Layer

#### LLM Client Service
**Purpose**: Abstract LLM provider for easy swapping

```python
class LLMClient:
    """
    Abstraction over LLM providers.
    Dev: Claude API
    Prod: OpenShift AI Models as a Service
    """
    
    async def complete(
        self,
        prompt: str,
        system_prompt: str = None,
        context_files: List[File] = None,
        **params
    ) -> LLMResponse:
        """
        Returns:
            LLMResponse with:
            - response_text
            - input_tokens
            - output_tokens
            - model_used
            - timestamp
        """
```

#### Validator Service
**Purpose**: Validate user solutions against challenge criteria

```python
class ValidatorService:
    """
    Validates responses against challenge criteria.
    Supports multiple validation types.
    """
    
    def validate(
        self,
        challenge: Challenge,
        response: str
    ) -> ValidationResult:
        """
        Returns:
            ValidationResult with:
            - is_correct: bool
            - feedback: str (optional)
            - test_results: List[TestResult] (for coding)
        """
```

**Validation Types:**
- `test_cases`: Run code against test inputs
- `exact_match`: String comparison
- `semantic_similarity`: Embeddings-based matching
- `custom_script`: Execute Python validator script

#### Scoring Service
**Purpose**: Calculate and track token usage

```python
class ScoringService:
    """
    Tracks token usage and calculates scores.
    """
    
    def record_attempt(
        self,
        user_id: int,
        challenge_id: str,
        tokens: TokenCount,
        is_correct: bool
    ) -> Attempt:
        """Record an attempt and update scores"""
    
    def get_user_score(
        self,
        user_id: int,
        challenge_id: str
    ) -> Score:
        """Get current score for user on challenge"""
```

#### Name Generator Service
**Purpose**: Generate professional, appropriate usernames

```python
class NameGeneratorService:
    """
    Generates usernames: {Color}-{Course}-{Club}
    """
    
    def generate_name(self) -> str:
        """Returns unique, appropriate username"""
    
    def validate_name(self, name: str) -> bool:
        """Validate name meets criteria"""
```

**Components:**
- Colors: 20-30 standard colors
- Courses: 50+ famous golf courses
- Clubs: 1-14
- Blacklist: Filter inappropriate combinations

#### Challenge Loader Service
**Purpose**: Load and parse YAML challenge definitions

```python
class ChallengeLoaderService:
    """
    Loads challenges from YAML files.
    Caches parsed challenges.
    """
    
    def load_challenge(self, challenge_id: str) -> Challenge:
        """Load and parse challenge YAML"""
    
    def list_challenges(
        self,
        difficulty: str = None,
        task_type: str = None
    ) -> List[Challenge]:
        """List available challenges with filters"""
```

### Data Layer

#### SQLAlchemy Models

**User Model**
```python
class User(Base):
    id: int
    username: str
    created_at: datetime
    session_id: str
    is_active: bool
    
    # Relationships
    attempts: List[Attempt]
    scores: List[Score]
```

**Challenge Model**
```python
class Challenge(Base):
    id: str  # hole-001
    name: str
    difficulty: str
    task_type: str
    config_yaml: str  # Full YAML content
    created_at: datetime
    
    # Relationships
    attempts: List[Attempt]
    scores: List[Score]
```

**Attempt Model**
```python
class Attempt(Base):
    id: int
    user_id: int
    challenge_id: str
    attempt_number: int
    prompt: str
    response: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    is_correct: bool
    created_at: datetime
    
    # Relationships
    user: User
    challenge: Challenge
```

**Score Model**
```python
class Score(Base):
    id: int
    user_id: int
    challenge_id: str
    total_attempts: int
    total_tokens: int
    completed_at: datetime
    session_id: str
    
    # Relationships
    user: User
    challenge: Challenge
```

### External Services

#### Claude API (Development)
- REST API for completions
- Token counting via API
- Response streaming (optional)

#### OpenShift AI (Production)
- Models as a Service
- Same interface abstracted via LLMClient
- May support different models/parameters

### File System

#### Challenge Repository
```
challenges/
├── hole-001/
│   ├── challenge.yaml      # Challenge definition
│   └── assets/
│       ├── context1.csv    # Context files
│       └── test_data.json  # Test data
├── hole-002/
│   └── ...
└── schema.yaml             # YAML schema definition
```

## Data Flow

### Game Session Flow

```
1. User visits homepage
   ↓
2. System generates username (Color-Course-Club)
   ↓
3. User selects holes/difficulty
   ↓
4. System creates session, loads first challenge
   ↓
5. Challenge rendered with:
   - Problem statement
   - Default context files (as pills)
   - Default system prompt
   ↓
6. User modifies context/prompt
   ↓
7. User submits prompt
   ↓
8. System:
   - Sends to LLM (via LLMClient)
   - Records tokens
   - Validates response
   - Stores attempt
   ↓
9. If incorrect:
   - Show feedback
   - User tries again (tokens accumulate)
   ↓
10. If correct:
    - Record final score
    - Update leaderboard
    - Show next challenge or completion screen
```

### Token Counting Flow

```
User Submit
    ↓
LLMClient.complete()
    ↓
    ├─> Count input tokens (prompt + system + context)
    ├─> Send to LLM
    ├─> Receive response
    └─> Count output tokens
    ↓
ScoringService.record_attempt()
    ↓
    ├─> Store in attempts table
    ├─> Update running total in scores table
    └─> Trigger leaderboard update
```

### Leaderboard Update Flow

```
Score Update
    ↓
Calculate Rankings:
    ├─> Per-Hole: ORDER BY total_tokens ASC WHERE challenge_id = X
    ├─> Global: SUM(total_tokens) GROUP BY user_id ORDER BY sum ASC
    └─> Session: Same as Global WHERE session_id = X
    ↓
Cache Results (future: Redis)
    ↓
Return to Client (via htmx partial update)
```

## Scalability Considerations

### Current (MVP) Implementation
- Single FastAPI process
- SQLite database
- Synchronous LLM calls
- In-memory session storage

### Future Enhancements

#### Phase 1: Multi-Process
- Uvicorn workers
- Shared PostgreSQL database
- Redis for session storage
- Connection pooling

#### Phase 2: Distributed
- Load balancer
- Multiple FastAPI instances
- PostgreSQL with read replicas
- Redis cluster
- WebSocket for real-time updates

#### Phase 3: Cloud-Native (OpenShift)
- Kubernetes pods with auto-scaling
- PostgreSQL operator
- Redis operator
- Persistent volume claims for challenge assets
- Ingress/Route configuration

## Security Considerations

### Current Scope
- No authentication (conference demo)
- Rate limiting on API endpoints
- Input validation on all user inputs
- SQL injection protection (SQLAlchemy ORM)
- XSS protection (Jinja2 auto-escaping)

### Future Considerations
- OAuth for persistent accounts
- API key management
- User data privacy
- Challenge solution privacy (prevent cheating)
- DDoS protection

## Deployment

### Local Development
```bash
# Python virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Environment configuration
cp .env.example .env
# Edit .env with Claude API key

# Run server
uvicorn app.main:app --reload

# Access at http://localhost:8000
```

### Docker Development
```bash
# Build image
docker build -t token-golf:dev .

# Run with docker-compose
docker-compose up

# Access at http://localhost:8000
```

### OpenShift Production
```bash
# Build image
oc new-build --name=token-golf --binary
oc start-build token-golf --from-dir=.

# Deploy
oc new-app token-golf
oc expose svc/token-golf

# Configure environment
oc set env deployment/token-golf \
  OPENSHIFT_AI_ENDPOINT=... \
  DATABASE_URL=...

# Scale
oc scale deployment/token-golf --replicas=3
```

## Testing Strategy

### Unit Tests
- Service layer logic
- Validation functions
- Token counting accuracy
- Name generation

### Integration Tests
- API endpoint responses
- Database operations
- LLM client mocking

### Challenge Tests
- Validate all challenges are solvable
- Test validation logic
- Verify token estimates

### Load Tests (Future)
- Simulate conference scenario (100+ concurrent users)
- Stress test leaderboard updates
- Test database under load

## Monitoring & Observability

### Metrics to Track
- Request latency
- LLM API response times
- Token usage per challenge
- Error rates
- Active sessions
- Database query performance

### Logging
- Structured logging (JSON)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Request/response logging
- LLM interaction logging (for debugging)

### Tools (Production)
- Prometheus for metrics
- Grafana for dashboards
- ELK stack for log aggregation
- OpenShift built-in monitoring

## Configuration Management

### Environment Variables
```bash
# LLM Configuration
LLM_PROVIDER=claude  # or openshift_ai
CLAUDE_API_KEY=sk-...
OPENSHIFT_AI_ENDPOINT=https://...

# Database
DATABASE_URL=sqlite:///./token_golf.db
# or postgresql://user:pass@host:5432/token_golf

# Application
DEBUG=false
LOG_LEVEL=INFO
SECRET_KEY=...

# Game Configuration
MAX_ITERATIONS_PER_HOLE=20
SESSION_TIMEOUT_MINUTES=60
```

### Config Files
- `.env` - Local environment variables (not committed)
- `.env.example` - Template for environment variables
- `app/config.py` - Configuration class with defaults
- `challenges/` - Challenge definitions (committed)

## Performance Targets

### MVP (Local)
- Page load: < 1s
- API response: < 200ms
- LLM round-trip: < 5s (dependent on LLM provider)
- Support: 10 concurrent users

### Production (Conference)
- Page load: < 2s
- API response: < 500ms
- LLM round-trip: < 5s
- Support: 100+ concurrent users
- 99% uptime during event

## Future Architecture Enhancements

### Real-Time Features
- WebSocket connections for live updates
- Server-sent events for leaderboard
- Real-time competition countdown
- Live audience view (spectator mode)

### Advanced Features
- Challenge difficulty adaptation based on user performance
- Team competitions (shared token pool)
- Replay mode (review past attempts)
- Analytics dashboard for organizers
- Export competition results (CSV, PDF)

### Multi-Region Support
- CDN for static assets
- Regional LLM endpoints
- Database read replicas
- Edge caching
