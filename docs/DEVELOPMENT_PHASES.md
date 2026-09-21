# Token Golf - Development Phases

**Approach**: Component-by-component incremental development  
**Strategy**: Build one piece at a time, containerize from the start, test as we go

## Phase 0: Container Foundation ✅ COMPLETE

**Goal**: Establish containerized development environment

- [x] Create `Dockerfile` for development
- [x] Create `docker-compose.yml` for local development
- [x] Create `.dockerignore`
- [x] Create `requirements.txt` with initial dependencies
- [x] Create `.env.example` template
- [x] Verify container builds and runs
- [x] Document how to run containerized development

**Deliverable**: Can run `docker-compose up` and access the app

---

## Phase 1: Foundation Components

### 1.1 Basic FastAPI App ✅ COMPLETE
**Goal**: Get minimal web server running in container

- [x] Create `app/` directory structure
- [x] Create `app/main.py` with basic FastAPI app
- [x] Create one health check endpoint (`/health`)
- [x] Verify endpoint works via curl/browser
- [x] Hot reload working in development

**Deliverable**: `curl http://localhost:8000/health` returns JSON

### 1.2 Configuration Management ✅ COMPLETE
**Goal**: Manage environment variables and settings

- [x] Create `app/config.py` with settings class
- [x] Use Pydantic BaseSettings for config
- [x] Load from environment variables
- [x] Configure database URL
- [x] Configure LLM API settings
- [x] Document all required env vars in `.env.example`

**Deliverable**: Settings loaded from environment, accessible throughout app

### 1.3 Database Models ✅ COMPLETE
**Goal**: Define SQLAlchemy models for all entities

- [x] Create `app/models/__init__.py`
- [x] Create `app/models/base.py` with Base class
- [x] Create `app/models/user.py` - User model
- [x] Create `app/models/challenge.py` - Challenge model
- [x] Create `app/models/attempt.py` - Attempt model
- [x] Create `app/models/score.py` - Score model
- [x] Add relationships between models
- [x] Include type hints and docstrings

**Deliverable**: All models defined, importable, type-checked

### 1.4 Alembic Setup ✅ COMPLETE
**Goal**: Initialize database migrations

- [x] Install Alembic in requirements.txt
- [x] Run `alembic init alembic`
- [x] Configure `alembic.ini` for containerized environment
- [x] Configure `alembic/env.py` to use our models
- [x] Create initial migration
- [x] Test migration: upgrade and downgrade
- [x] Document migration workflow

**Deliverable**: Database created with all tables, migration works

---

## Phase 2: Core Services

### 2.1 Challenge Loader Service ✅ COMPLETE
**Goal**: Read and parse YAML challenge files

- [x] Create `app/services/__init__.py`
- [x] Create `app/services/challenge_loader.py`
- [x] Implement YAML file reading
- [x] Implement challenge parsing and validation
- [x] Cache parsed challenges
- [x] Handle missing/invalid files gracefully
- [ ] Write unit tests (Phase 7)
- [x] Test with placeholder challenges

**Deliverable**: Can load challenges from YAML files, return Challenge objects

### 2.2 LLM Client Service ✅ COMPLETE
**Goal**: Abstract LLM provider interaction

- [x] Create `app/services/llm_client.py`
- [x] Define `LLMResponse` model
- [x] Implement Claude API client
- [x] Implement token counting
- [x] Add error handling and retries
- [x] Create mock client for testing
- [x] Add timeout configuration
- [ ] Write unit tests with mocked API (Phase 7)

**Deliverable**: Can call LLM, get response with token counts

### 2.3 Validator Service ✅ COMPLETE
**Goal**: Validate LLM responses against challenge criteria

- [x] Create `app/services/validator.py`
- [x] Define `ValidationResult` model
- [x] Implement `test_cases` validation type
- [x] Implement `exact_match` validation type
- [x] Implement `pattern_match` validation type
- [x] Add validation error handling
- [ ] Write comprehensive unit tests (Phase 7)
- [x] Test with real challenge examples

**Deliverable**: Can validate responses, return pass/fail with feedback

### 2.4 Scoring Service ✅ COMPLETE
**Goal**: Track token usage and calculate scores

- [x] Create `app/services/scoring.py`
- [x] Implement attempt recording
- [x] Implement score calculation
- [x] Implement score retrieval by user/challenge
- [x] Track cumulative tokens across attempts
- [ ] Write unit tests (Phase 7)
- [x] Test with database

**Deliverable**: Can record attempts, calculate and retrieve scores

---

## Phase 3: API Endpoints

### 3.1 Challenge API ✅ COMPLETE
**Goal**: Endpoints for challenge operations

- [x] Create `app/api/__init__.py`
- [x] Create `app/api/challenges.py`
- [x] `GET /api/challenges` - List all challenges
- [x] `GET /api/challenges/{id}` - Get specific challenge
- [x] Add filtering by difficulty/type
- [x] Add request/response models (Pydantic)
- [ ] Write integration tests (Phase 7)
- [x] Test in container

**Deliverable**: ✅ Can list and retrieve challenges via API

### 3.2 Game API ✅ COMPLETE
**Goal**: Endpoints for game session management

- [x] Create `app/api/game.py`
- [x] `POST /api/game/start` - Start new game session
- [x] `POST /api/game/submit` - Submit prompt attempt
- [x] `GET /api/game/status/{session}` - Get game state
- [x] Integrate LLM client, validator, scoring services
- [x] Handle errors gracefully (weather delay)
- [ ] Write integration tests (Phase 7)

**Deliverable**: ✅ Can start game, submit prompts, get validation results

### 3.3 Leaderboard API ✅ COMPLETE
**Goal**: Endpoints for leaderboard views

- [x] Create `app/api/leaderboard.py`
- [x] `GET /api/leaderboard/global` - Global leaderboard
- [x] `GET /api/leaderboard/hole/{id}` - Per-hole leaderboard
- [x] `GET /api/leaderboard/session/{id}` - Session leaderboard
- [x] Implement ranking logic (golf scoring)
- [x] Add pagination (limit, offset)
- [ ] Write integration tests (Phase 7)

**Deliverable**: ✅ Can retrieve leaderboards in all three views

---

## Phase 4: Frontend - Templates ✅ COMPLETE

### 4.1 Base Template & Static Setup ✅ COMPLETE
**Goal**: Set up Tailwind CSS and base template

- [x] Add Tailwind CSS to container build
- [x] Create `static/css/input.css` with Tailwind directives
- [x] Configure Tailwind build in docker-compose
- [x] Create `app/templates/base.html` - base template
- [x] Add static file serving in FastAPI
- [x] Test Tailwind classes render correctly
- [x] Add Alpine.js CDN link

**Deliverable**: ✅ Base template with Tailwind and Alpine.js working

### 4.2 Home/Lobby Page ✅ COMPLETE
**Goal**: Landing page to start game

- [x] Create `app/templates/index.html`
- [x] Add welcome message
- [x] Add "Start Game" button (with auth options)
- [x] Style with Tailwind
- [x] Add route in main.py
- [x] Add leaderboard preview
- [ ] Test in browser (Phase 5)

**Deliverable**: ✅ Can visit home page, see styled interface

### 4.3 Game Interface Layout ✅ COMPLETE
**Goal**: Main game page with split layout

- [x] Create `app/templates/game.html`
- [x] Implement two-column layout (problem + metrics)
- [x] Add problem statement section
- [x] Add chat/interaction section with pills UI
- [x] Add metrics panel (stats, leaderboard, comparison, distribution)
- [x] Style with Tailwind
- [x] Make responsive

**Deliverable**: ✅ Game page with proper layout structure

### 4.4 Leaderboard Page ✅ COMPLETE
**Goal**: Standalone leaderboard view

- [x] Create `app/templates/leaderboard.html`
- [x] Add three view toggle (Global/Per-Hole/Session)
- [x] Display rankings with top 10
- [x] Add statistics panel
- [x] Style with Tailwind
- [x] Add route in main.py

**Deliverable**: ✅ Standalone leaderboard page with all views

---

## Phase 5: Frontend - Interactivity

### 5.1 Htmx Prompt Submission
**Goal**: Submit prompts without page reload

- [ ] Add htmx to base template
- [ ] Create prompt input form
- [ ] Add htmx attributes for AJAX submission
- [ ] Create htmx response partial templates
- [ ] Handle loading states
- [ ] Display LLM responses
- [ ] Show validation results

**Deliverable**: Can submit prompts, see results without page reload

### 5.2 Alpine.js Pills UI
**Goal**: Context file pills for add/remove

- [ ] Create Alpine.js component for pills
- [ ] Display context files as pills
- [ ] Add remove (X) functionality
- [ ] Add pill styling with Tailwind
- [ ] Include pill data in form submission
- [ ] Test add/remove interaction

**Deliverable**: Can add/remove context files via pill UI

### 5.3 Metrics Panel
**Goal**: Display real-time stats and leaderboard

- [ ] Create metrics panel template component
- [ ] Display current token count
- [ ] Display attempt count
- [ ] Display user rank
- [ ] Add leaderboard view (top 10)
- [ ] Use htmx for auto-refresh
- [ ] Style with Tailwind

**Deliverable**: Metrics update in real-time as game progresses

---

## Phase 6: Supporting Features

### 6.1 Name Generator Service
**Goal**: Auto-generate user names

- [ ] Create `app/services/name_generator.py`
- [ ] Create lists: colors, courses, club numbers
- [ ] Implement name generation algorithm
- [ ] Ensure uniqueness (check database)
- [ ] Add inappropriate name filtering
- [ ] Write unit tests
- [ ] Integrate into game start

**Deliverable**: New users get auto-generated names

### 6.2 Session Management
**Goal**: Track user sessions

- [ ] Add session middleware to FastAPI
- [ ] Store session data (in-memory for MVP)
- [ ] Associate users with sessions
- [ ] Handle session expiration
- [ ] Add session cleanup
- [ ] Test session lifecycle

**Deliverable**: Sessions persist across requests

### 6.3 Leaderboard Page
**Goal**: Standalone leaderboard view

- [ ] Create `app/templates/leaderboard.html`
- [ ] Add toggle for three leaderboard types
- [ ] Display rankings with styling
- [ ] Highlight current user
- [ ] Add route in main.py
- [ ] Style with Tailwind

**Deliverable**: Can view leaderboards in standalone page

---

## Phase 7: Polish & Testing

### 7.1 Error Handling
**Goal**: Graceful error handling throughout

- [ ] Add global exception handlers
- [ ] Create error templates (404, 500, etc.)
- [ ] Add validation error messages
- [ ] Handle LLM API failures gracefully
- [ ] Add user-friendly error messages
- [ ] Log errors appropriately

**Deliverable**: Errors don't crash app, users see helpful messages

### 7.2 Testing Suite
**Goal**: Comprehensive test coverage

- [ ] Organize tests: unit, integration, e2e
- [ ] Achieve >80% coverage on services
- [ ] Test all API endpoints
- [ ] Test validation logic thoroughly
- [ ] Create test fixtures and factories
- [ ] Document how to run tests in container

**Deliverable**: Full test suite passing, good coverage

### 7.3 Documentation
**Goal**: Complete developer and user documentation

- [ ] Update README with setup instructions
- [ ] Document API endpoints (auto-generated + examples)
- [ ] Create local development guide
- [ ] Document environment variables
- [ ] Create troubleshooting guide
- [ ] Add architecture diagrams

**Deliverable**: New developers can get started easily

---

## Phase 8: Production Preparation

### 8.1 Production Dockerfile
**Goal**: Optimized container for production

- [ ] Create multi-stage Dockerfile
- [ ] Minimize image size
- [ ] Run as non-root user
- [ ] Health check endpoint
- [ ] Production-ready uvicorn config
- [ ] Document deployment

**Deliverable**: Production-ready container image

### 8.2 PostgreSQL Migration
**Goal**: Switch from SQLite to PostgreSQL

- [ ] Add PostgreSQL to docker-compose
- [ ] Test Alembic migrations on PostgreSQL
- [ ] Update connection pooling
- [ ] Verify all queries work
- [ ] Document PostgreSQL setup

**Deliverable**: App works with PostgreSQL

### 8.3 OpenShift Preparation
**Goal**: Ready for OpenShift deployment

- [ ] Create OpenShift manifests
- [ ] Configure routes/ingress
- [ ] Set up environment variables
- [ ] Configure persistent volumes
- [ ] Test deployment process
- [ ] Document OpenShift deployment

**Deliverable**: Can deploy to OpenShift

---

## Notes

- **Flexibility**: Phases can be reordered based on priorities
- **Testing**: Test each component before moving to next
- **Documentation**: Update docs as we go
- **Git**: Commit after each completed sub-task
- **Containerization**: Always test in Docker, not just local Python
- **ADRs**: Create ADR for any significant decisions made during development

---

**For current project status and phase tracking, see [PROJECT_STATUS.md](../PROJECT_STATUS.md)**
