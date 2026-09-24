# Testing Plan - Token Golf

**Phase**: 7 (Post-MVP)  
**Status**: Not yet implemented  
**Coverage Target**: >80% for services, >90% for models, 100% for APIs

---

## Test Structure

```
tests/
├── unit/
│   ├── services/
│   │   ├── test_challenge_loader.py
│   │   ├── test_llm_client.py
│   │   ├── test_validator.py
│   │   └── test_scoring.py
│   └── models/
│       ├── test_user.py
│       ├── test_session.py
│       └── ...
├── integration/
│   ├── test_game_flow.py
│   ├── test_api_challenges.py
│   ├── test_api_game.py
│   └── test_api_leaderboard.py
└── challenges/
    └── test_challenge_validation.py
```

---

## Services to Test

### ChallengeLoaderService (Phase 2.1)
- ✓ Load from YAML
- ✓ Cache functionality (memory + database)
- ✓ Validation logic
- ✓ Error handling (missing files, invalid YAML)

### LLMClient + MockLLMClient (Phase 2.2)
- ✓ API integration
- ✓ Token counting accuracy
- ✓ Error handling and retries
- ✓ Mock client for testing

### ValidatorService (Phase 2.3)
- ✓ Test case validation (code execution)
- ✓ Exact match validation
- ✓ Pattern match validation
- ✓ Code extraction from markdown
- ✓ Output comparison (int, float, list, dict)

### ScoringService (Phase 2.4)
- ✓ Attempt recording
- ✓ Score calculation
- ✓ Cumulative token tracking
- ✓ Leaderboard queries
- ✓ Completion time logic
- ✓ Weather delay handling

---

## Integration Tests

### Complete Game Flow
```python
@pytest.mark.asyncio
async def test_complete_game_flow(db_session):
    # 1. Load challenge
    challenge = await challenge_loader.get_challenge("hole-001")
    
    # 2. Submit attempt (wrong answer)
    llm_response = await llm_client.complete("Bad prompt")
    validation = await validator.validate(challenge, llm_response.response_text)
    assert not validation.is_correct
    
    # 3. Submit attempt (correct answer)
    llm_response = await llm_client.complete("Good prompt")
    validation = await validator.validate(challenge, llm_response.response_text)
    assert validation.is_correct
    
    # 4. Record scores
    attempt = await scoring.record_attempt(...)
    score = await scoring.get_score(...)
    assert score.completed_at is not None
```

### API Endpoints (Phase 3)
- GET /api/challenges
- GET /api/challenges/{id}
- POST /api/game/start
- POST /api/game/submit
- GET /api/leaderboard/*

---

## Test Fixtures

```python
@pytest.fixture
async def db_session():
    """Create test database session"""
    # Setup test database
    # Yield session
    # Cleanup

@pytest.fixture
def mock_challenge():
    """Sample challenge for testing"""
    return {
        "id": "test-001",
        "validation": {"type": "test_cases", ...}
    }

@pytest.fixture
def mock_llm_client():
    """MockLLMClient for predictable responses"""
    return MockLLMClient(mock_response="def add(a, b): return a + b")
```

---

## Running Tests

```bash
# All tests
pytest tests/

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# With coverage
pytest --cov=app tests/

# Specific service
pytest tests/unit/services/test_scoring.py -v
```

---

## Coverage Requirements

| Component | Target Coverage | Priority |
|-----------|----------------|----------|
| Models | >90% | High |
| Services | >80% | High |
| API endpoints | 100% | Critical |
| Utils | >70% | Medium |

---

## Test Examples

### Unit Test - MockLLMClient
```python
@pytest.mark.asyncio
async def test_llm_completion():
    client = MockLLMClient(mock_response="Hello")
    response = await client.complete("Say hello")
    assert response.response_text == "Hello"
    assert response.total_tokens > 0
```

### Unit Test - Validator
```python
@pytest.mark.asyncio
async def test_exact_match():
    validator = ValidatorService()
    challenge = create_mock_challenge(validation_type="exact_match", criteria="42")
    result = await validator.validate(challenge, "42")
    assert result.is_correct
```

### Unit Test - Scoring
```python
@pytest.mark.asyncio
async def test_record_attempt(db_session):
    scoring = ScoringService(db_session)
    attempt = await scoring.record_attempt(
        user_id=1, session_id="s1", challenge_id="h1",
        prompt="test", response="output",
        input_tokens=5, output_tokens=10, is_correct=False
    )
    assert attempt.attempt_number == 1
    assert attempt.total_tokens == 15
```

---

## CI/CD Integration

```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest --cov=app tests/
```

---

**Status**: Awaiting Phase 7 implementation  
**Reference**: See individual phase docs for service-specific test examples  
**Last Updated**: 2026-09-21
