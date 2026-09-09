# Contributing to Token Golf

Thank you for your interest in contributing to Token Golf! This document provides guidelines and information for contributors.

## Development Workflow

### Git Flow

We use a simplified git flow workflow:

- **`main`**: Production-ready code only. Protected branch.
- **`dev`**: Integration branch for all development work.
- **`feature/*`**: Feature branches created from `dev`.
- **`hotfix/*`**: Emergency fixes created from `main`.

### Creating a Feature

```bash
# Ensure dev is up to date
git checkout dev
git pull origin dev

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes, commit regularly
git add .
git commit -m "Clear description of changes"

# Push to remote
git push origin feature/your-feature-name

# Create PR to merge into dev
```

### Commit Messages

Write clear, descriptive commit messages:

```
Add token counting service

- Implement TokenCountingService class
- Add tests for token calculation
- Update API to use new service

Refs #123
```

**Format:**
- First line: Brief summary (50 chars or less)
- Blank line
- Detailed explanation if needed (wrap at 72 chars)
- Reference relevant issues

### Pull Requests

1. **Create PR against `dev` branch** (not `main`)
2. **Fill out PR template** with:
   - Description of changes
   - Testing performed
   - Related issues
3. **Ensure all checks pass**:
   - Tests pass
   - Linting passes
   - No merge conflicts
4. **Request review** from at least one team member
5. **Address feedback** promptly
6. **Squash commits** if requested before merge

## Code Standards

### Python Style

Follow **PEP 8** with these specifics:

- **Line length**: 88 characters (Black default)
- **Imports**: Organized with `isort`
- **Type hints**: Use type hints for all function signatures
- **Docstrings**: Google-style docstrings for public APIs

**Example:**
```python
from typing import List, Optional

def calculate_score(
    attempts: List[Attempt],
    challenge_id: str
) -> Optional[Score]:
    """
    Calculate the total score for a user on a challenge.
    
    Args:
        attempts: List of user attempts on the challenge
        challenge_id: Unique challenge identifier
        
    Returns:
        Score object if attempts exist, None otherwise
        
    Raises:
        ValueError: If attempts list is empty after filtering
    """
    # Implementation
```

### Code Organization

- **One class per file** (generally)
- **Small, focused functions** (< 50 lines)
- **Avoid deep nesting** (< 4 levels)
- **Use descriptive names** (no abbreviations unless obvious)
- **Comments only for "why"**, not "what"

### Testing

- **Write tests for all new features**
- **Maintain >80% coverage**
- **Test edge cases and error conditions**
- **Use meaningful test names**

**Example:**
```python
def test_token_counting_includes_system_prompt():
    """System prompt tokens should be included in total count."""
    # Arrange
    service = TokenCountingService()
    prompt = "Test prompt"
    system = "You are a helpful assistant."
    
    # Act
    result = service.count_tokens(prompt, system_prompt=system)
    
    # Assert
    assert result.total_tokens > len(prompt.split())
    assert result.system_tokens > 0
```

### Frontend Standards

- **Server-side rendering first** - Use htmx for interactivity
- **Minimal JavaScript** - Only when necessary
- **Semantic HTML** - Use appropriate HTML5 elements
- **Accessible** - Follow WCAG 2.1 AA guidelines
- **Responsive** - Works on laptop and projection screens

## Architecture Decisions

All significant architecture decisions must be documented in ADRs (Architecture Decision Records).

### When to Write an ADR

Write an ADR when deciding:
- Technology choices (frameworks, libraries, databases)
- Architectural patterns
- API designs
- Data models
- Deployment strategies
- Breaking changes

### ADR Process

1. **Copy template**: `cp docs/ADRs/template.md docs/ADRs/NNN-title.md`
2. **Fill out template** with context, decision, and consequences
3. **Discuss with team** (if collaborative)
4. **Commit ADR** with your changes
5. **Reference ADR** in related code/docs

See `docs/ADRs/template.md` for the ADR template.

## Testing Guidelines

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/unit/test_scoring.py

# With coverage
pytest --cov=app tests/

# Watch mode
pytest-watch
```

### Test Structure

```
tests/
├── unit/               # Unit tests for individual components
│   ├── test_services.py
│   ├── test_validators.py
│   └── test_models.py
├── integration/        # Integration tests for API endpoints
│   ├── test_api_challenges.py
│   ├── test_api_game.py
│   └── test_api_leaderboard.py
└── challenges/         # Challenge validation tests
    └── test_challenge_suite.py
```

### Test Coverage

Maintain high test coverage:
- **Services**: 90%+ coverage
- **API endpoints**: 80%+ coverage
- **Validators**: 100% coverage (critical path)
- **Models**: 70%+ coverage

## Challenge Contributions

### Creating New Challenges

1. **Read the spec**: Review `docs/CHALLENGE_FORMAT.md`
2. **Copy template**: Use existing challenge as starting point
3. **Write YAML**: Create `challenges/hole-XXX/challenge.yaml`
4. **Add assets**: Place context files in `assets/` subdirectory
5. **Test locally**: Solve your own challenge, verify validation
6. **Validate**: Run `python scripts/validate_challenges.py`
7. **Submit PR**: Include your testing results

### Challenge Guidelines

- **Start with outline**: Plan before writing YAML
- **Clear requirements**: No ambiguity in task description
- **Fair validation**: Deterministic, unambiguous success criteria
- **Token efficiency**: Challenge should teach token optimization
- **Progressive difficulty**: Ensure challenge fits difficulty level
- **Test thoroughly**: Try multiple solution approaches

### Challenge Review Checklist

Before submitting a challenge PR:

- [ ] YAML passes validation script
- [ ] Task description is clear and unambiguous
- [ ] Validation criteria are deterministic
- [ ] Token estimates are realistic (tested with actual attempts)
- [ ] Context files are necessary and appropriately sized
- [ ] Difficulty classification matches actual difficulty
- [ ] All asset files are included and referenced correctly
- [ ] Challenge has been solved at least once
- [ ] Metadata is complete and accurate

## Development Setup

### Prerequisites

- Python 3.11+
- pip and venv
- Git
- Claude API key (for development)

### Initial Setup

```bash
# Clone repository
git clone <repo-url>
cd token-golf

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Setup pre-commit hooks
pre-commit install

# Copy environment template
cp .env.example .env
# Edit .env and add your Claude API key

# Run database migrations (when available)
# alembic upgrade head

# Run development server
uvicorn app.main:app --reload

# Visit http://localhost:8000
```

### Development Tools

We use these tools (enforced via pre-commit hooks):

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pytest**: Testing

Run all checks:
```bash
# Auto-format
black app/ tests/
isort app/ tests/

# Lint
flake8 app/ tests/

# Type check
mypy app/

# Test
pytest
```

Or use pre-commit:
```bash
pre-commit run --all-files
```

## Documentation

### Code Documentation

- **Docstrings**: All public functions, classes, methods
- **Type hints**: All function parameters and return values
- **Comments**: Only for non-obvious "why" explanations

### Project Documentation

Update these when relevant:
- `README.md`: User-facing changes, new features
- `CLAUDE.md`: Context for AI assistants
- `docs/ARCHITECTURE.md`: Architectural changes
- `docs/CHALLENGE_FORMAT.md`: Challenge format changes
- `docs/ADRs/`: New architecture decisions

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open an issue with reproduction steps
- **Features**: Open an issue with use case description
- **Security**: Email security@tokengolf.example (DO NOT open public issue)

## Code of Conduct

### Our Standards

- **Be respectful** of differing viewpoints and experiences
- **Accept constructive criticism** gracefully
- **Focus on what's best** for the project and community
- **Show empathy** towards other community members

### Unacceptable Behavior

- Harassment, trolling, or discriminatory comments
- Personal attacks or insults
- Publishing others' private information
- Other conduct inappropriate in a professional setting

## Recognition

Contributors will be recognized in:
- `CONTRIBUTORS.md` file
- Release notes for significant contributions
- Challenge metadata (for challenge authors)

Thank you for contributing to Token Golf!
