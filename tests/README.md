# Token Golf - Testing Guide

This directory contains the test suite for Token Golf, covering unit tests, integration tests, and end-to-end testing.

## Table of Contents

- [Quick Start](#quick-start)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Test Fixtures](#test-fixtures)
- [Coverage Requirements](#coverage-requirements)

## Quick Start

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only (fast)
pytest -m unit

# Integration tests only
pytest -m integration

# End-to-end tests only
pytest -m e2e
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html
```

View coverage report: `open htmlcov/index.html`

## Test Structure

### Directory Organization

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── test_integration.py      # Integration tests (API + DB)
├── test_models.py           # Model unit tests (TODO)
├── test_services.py         # Service layer tests (TODO)
├── test_api.py              # API endpoint tests (TODO)
└── README.md                # This file
```

### Test Markers

Tests are categorized using pytest markers defined in `pytest.ini`:

- `@pytest.mark.unit` - Fast, isolated tests with no external dependencies
- `@pytest.mark.integration` - Tests requiring database or API interaction
- `@pytest.mark.e2e` - Full end-to-end user flow tests
- `@pytest.mark.slow` - Tests that take significant time to run
- `@pytest.mark.auth` - Authentication/authorization specific tests
- `@pytest.mark.challenge` - Challenge loading and validation tests
- `@pytest.mark.session` - Game session management tests
- `@pytest.mark.leaderboard` - Leaderboard and scoring tests

### Example Test Organization

```python
@pytest.mark.unit
@pytest.mark.challenge
async def test_challenge_validation():
    """Unit test for challenge config validation"""
    pass

@pytest.mark.integration
@pytest.mark.auth
async def test_auth_flow(client: TestClient):
    """Integration test for authentication flow"""
    pass
```

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_integration.py

# Run specific test function
pytest tests/test_integration.py::test_auth_flow_new_user

# Run tests matching pattern
pytest -k "auth"

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf
```

### Filtering by Markers

```bash
# Run only unit tests
pytest -m unit

# Run integration but not slow tests
pytest -m "integration and not slow"

# Run auth-related tests
pytest -m auth
```

### Coverage Analysis

```bash
# Generate coverage report
pytest --cov=app --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=app --cov-report=html

# Fail if coverage below threshold
pytest --cov=app --cov-fail-under=80
```

### Parallel Execution

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel (4 workers)
pytest -n 4
```

## Writing Tests

### Test Structure Guidelines

1. **Arrange-Act-Assert** pattern:

```python
async def test_example(db_session: AsyncSession):
    # Arrange: Set up test data
    user = User(username="test", ...)
    db_session.add(user)
    await db_session.commit()

    # Act: Perform the action
    result = await some_function(user.id)

    # Assert: Verify the result
    assert result is not None
    assert result.username == "test"
```

2. **Use descriptive test names**:

```python
# Good
async def test_auth_flow_rejects_invalid_password()

# Bad
async def test_auth()
```

3. **One logical assertion per test** (when possible):

```python
# Good - focused test
async def test_user_creation_sets_created_at():
    user = User(username="test", ...)
    assert user.created_at is not None

# Separate test for different concern
async def test_user_creation_defaults_to_active():
    user = User(username="test", ...)
    assert user.is_active is True
```

4. **Use fixtures for common setup**:

```python
# Use existing fixtures from conftest.py
async def test_with_user(sample_user: User):
    assert sample_user.username == "test-user"
```

### Async Test Guidelines

All async tests must use `@pytest.mark.asyncio`:

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_operation()
    assert result is not None
```

### Database Testing

Use the `db_session` fixture for database tests:

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_database_operation(db_session: AsyncSession):
    # Create test data
    user = User(username="test", password_hash="hash")
    db_session.add(user)
    await db_session.commit()

    # Query and verify
    result = await db_session.execute(
        select(User).where(User.username == "test")
    )
    found_user = result.scalar_one_or_none()
    assert found_user is not None
```

### API Testing

Use the `client` fixture for API endpoint tests:

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_api_endpoint(client: TestClient):
    response = client.get("/api/challenges")

    assert response.status_code == 200
    assert "challenges" in response.json()
```

## Test Fixtures

Fixtures are defined in `conftest.py` and are automatically available to all tests.

### Configuration Fixtures

- `test_settings`: Test configuration with in-memory database

### Database Fixtures

- `db_engine`: Fresh database engine for each test
- `db_session`: Database session with automatic rollback

### API Fixtures

- `client`: FastAPI TestClient with database override

### User Fixtures

- `sample_user`: Single test user with known credentials
- `multiple_users`: List of test users for leaderboard testing

### Challenge Fixtures

- `challenge_loader`: ChallengeLoaderService instance
- `sample_challenge`: Single challenge (hole-001)
- `all_challenges`: All challenges loaded from YAML

### Session Fixtures

- `sample_session`: Active game session with participant
- `expired_session`: Expired session for timeout testing

### Creating Custom Fixtures

Add new fixtures to `conftest.py`:

```python
@pytest_asyncio.fixture
async def custom_fixture(db_session: AsyncSession) -> MyModel:
    """
    Create custom test data.

    Args:
        db_session: Database session

    Returns:
        MyModel instance
    """
    instance = MyModel(field="value")
    db_session.add(instance)
    await db_session.commit()
    await db_session.refresh(instance)
    return instance
```

## Coverage Requirements

### Target Coverage

- **Overall**: 80% minimum
- **Critical paths** (auth, scoring, validation): 90% minimum
- **Models**: 85% minimum
- **Services**: 85% minimum
- **API endpoints**: 80% minimum

### Checking Coverage

```bash
# Terminal report with missing lines
pytest --cov=app --cov-report=term-missing

# HTML report (more detailed)
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

### Coverage Tips

1. **Focus on critical code paths** first
2. **Don't test framework code** (FastAPI internals, SQLAlchemy)
3. **Test error cases** as well as success cases
4. **Mock external services** (Anthropic API, etc.)

### Excluded from Coverage

These lines are excluded (see `pytest.ini`):

- `pragma: no cover` comments
- `def __repr__` methods
- `if TYPE_CHECKING:` blocks
- `if __name__ == "__main__":`
- Abstract methods

## Adding New Tests

### 1. Choose Test Type

- **Unit test**: Testing single function/class in isolation
- **Integration test**: Testing multiple components together
- **E2E test**: Testing complete user flow

### 2. Create Test File

```bash
# For new feature area
touch tests/test_feature_name.py
```

### 3. Write Test

```python
"""
Feature Name - Tests

Description of what this test file covers.
"""

import pytest
from app.models.example import Example


@pytest.mark.unit
@pytest.mark.asyncio
async def test_feature():
    """
    Test specific behavior.

    Flow:
    1. Setup
    2. Action
    3. Verification
    """
    # Arrange
    data = Example(value=42)

    # Act
    result = data.process()

    # Assert
    assert result == 84
```

### 4. Add Appropriate Markers

```python
@pytest.mark.unit           # or integration, e2e
@pytest.mark.feature_area   # auth, challenge, session, etc.
@pytest.mark.asyncio        # for async tests
async def test_something():
    pass
```

### 5. Run and Verify

```bash
# Run new test
pytest tests/test_feature_name.py -v

# Check coverage
pytest tests/test_feature_name.py --cov=app.feature_module
```

## Best Practices

### Do's

- Use descriptive test names that explain what is being tested
- Use fixtures for common setup to reduce duplication
- Test both success and failure cases
- Use appropriate markers to categorize tests
- Keep tests independent (no test should depend on another)
- Clean up resources (fixtures handle this automatically)
- Write docstrings explaining complex test scenarios

### Don'ts

- Don't test framework internals (FastAPI, SQLAlchemy)
- Don't make tests depend on execution order
- Don't use real external services (mock them)
- Don't commit commented-out tests (remove or fix them)
- Don't write tests with no assertions
- Don't use `sleep()` - use proper async/await patterns

## Continuous Integration

### GitHub Actions (TODO)

Tests will run automatically on:

- Pull requests
- Pushes to main branch
- Scheduled daily runs

### CI Configuration

```yaml
# .github/workflows/test.yml (TODO)
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: pytest --cov=app --cov-fail-under=80
```

## Troubleshooting

### Common Issues

**Issue**: Tests fail with "database is locked"

```bash
# Solution: Use asyncio_mode = auto in pytest.ini
# Already configured in this project
```

**Issue**: Fixtures not found

```bash
# Solution: Ensure conftest.py is in tests/ directory
# and pytest is run from project root
pytest  # Run from /path/to/token-golf/
```

**Issue**: Import errors

```bash
# Solution: Install package in development mode
pip install -e .
```

**Issue**: Async warnings

```bash
# Solution: Add @pytest.mark.asyncio to async test functions
```

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio documentation](https://pytest-asyncio.readthedocs.io/)
- [FastAPI testing guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy testing guide](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)

## Next Steps

1. Complete placeholder tests in `test_integration.py`
2. Add unit tests for models (`test_models.py`)
3. Add service layer tests (`test_services.py`)
4. Add API endpoint tests (`test_api.py`)
5. Set up CI/CD pipeline
6. Add performance/load tests
