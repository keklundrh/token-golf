"""
Unit tests for ValidatorService

Tests validation types (test_cases, exact_match, pattern_match),
code execution, and output comparison.
"""

import pytest
import yaml
from unittest.mock import MagicMock

from app.services.validator import ValidatorService, ValidationResult
from app.models.challenge import Challenge
from datetime import datetime


class TestValidationResult:
    """Test ValidationResult model."""

    def test_validation_result_success(self):
        """Test creating successful validation result."""
        result = ValidationResult(
            is_correct=True,
            feedback="All tests passed",
        )

        assert result.is_correct is True
        assert result.feedback == "All tests passed"
        assert result.test_results is None
        assert result.error_message is None

    def test_validation_result_failure(self):
        """Test creating failed validation result."""
        result = ValidationResult(
            is_correct=False,
            feedback="Test failed",
            error_message="Syntax error",
        )

        assert result.is_correct is False
        assert result.feedback == "Test failed"
        assert result.error_message == "Syntax error"


class TestValidatorServiceInit:
    """Test ValidatorService initialization."""

    def test_init(self):
        """Test validator service initialization."""
        validator = ValidatorService()
        assert validator is not None


class TestValidateTestCases:
    """Test test_cases validation type."""

    @pytest.mark.asyncio
    async def test_validate_simple_function_pass(self):
        """Test validating simple function that passes all tests."""
        validator = ValidatorService()

        config_yaml = yaml.dump({
            "id": "test-001",
            "name": "Add Function",
            "validation": {
                "type": "test_cases",
                "criteria": [
                    {
                        "name": "Test 1",
                        "input": {"args": [2, 3]},
                        "expected_output": 5,
                    },
                    {
                        "name": "Test 2",
                        "input": {"args": [10, 20]},
                        "expected_output": 30,
                    },
                ],
            },
        })

        challenge = Challenge(
            id="test-001",
            name="Test",
            difficulty="easy",
            task_type="coding",
            config_yaml=config_yaml,
            created_at=datetime.utcnow()
        )

        response = """
def add(a, b):
    return a + b
"""

        result = await validator.validate(challenge, response)

        assert result.is_correct is True
        assert result.test_results is not None
        assert len(result.test_results) == 2
        assert all(t["passed"] for t in result.test_results)

    @pytest.mark.asyncio
    async def test_validate_function_with_failures(self):
        """Test validating function that fails some tests."""
        validator = ValidatorService()

        config_yaml = yaml.dump({
            "id": "test-001",
            "name": "Multiply",
            "validation": {
                "type": "test_cases",
                "criteria": [
                    {
                        "name": "Test 1",
                        "input": {"args": [2, 3]},
                        "expected_output": 6,
                    },
                    {
                        "name": "Test 2",
                        "input": {"args": [4, 5]},
                        "expected_output": 20,
                    },
                ],
            },
        })

        challenge = Challenge(
            id="test-001",
            name="Test",
            difficulty="easy",
            task_type="coding",
            config_yaml=config_yaml,
            created_at=datetime.utcnow()
        )

        # Wrong implementation
        response = """
def multiply(a, b):
    return a + b  # Wrong!
"""

        result = await validator.validate(challenge, response)

        assert result.is_correct is False
        assert "Passed 0/2" in result.feedback
        assert len(result.test_results) == 2
        assert not any(t["passed"] for t in result.test_results)

    @pytest.mark.asyncio
    async def test_validate_with_markdown_code_block(self):
        """Test validating code wrapped in markdown code block."""
        validator = ValidatorService()

        config_yaml = yaml.dump({
            "id": "test-001",
            "name": "Test",
            "validation": {
                "type": "test_cases",
                "criteria": [
                    {
                        "name": "Test 1",
                        "input": {"args": [5]},
                        "expected_output": 10,
                    },
                ],
            },
        })

        challenge = Challenge(
            id="test-001",
            name="Test",
            difficulty="easy",
            task_type="coding",
            config_yaml=config_yaml,
            created_at=datetime.utcnow()
        )

        response = """
```python
def double(x):
    return x * 2
```
"""

        result = await validator.validate(challenge, response)

        assert result.is_correct is True
        assert result.test_results[0]["passed"] is True

    @pytest.mark.asyncio
    async def test_validate_syntax_error(self):
        """Test validating code with syntax errors."""
        validator = ValidatorService()

        config_yaml = yaml.dump({
            "id": "test-001",
            "name": "Test",
            "validation": {
                "type": "test_cases",
                "criteria": [
                    {
                        "name": "Test 1",
                        "input": {"args": [5]},
                        "expected_output": 10,
                    },
                ],
            },
        })

        challenge = Challenge(
            id="test-001",
            name="Test",
            difficulty="easy",
            task_type="coding",
            config_yaml=config_yaml,
            created_at=datetime.utcnow()
        )

        response = """
def broken(:
    return x
"""

        result = await validator.validate(challenge, response)

        assert result.is_correct is False
        assert result.test_results[0]["passed"] is False
        assert "error" in result.test_results[0]

    @pytest.mark.asyncio
    async def test_validate_with_kwargs_input(self):
        """Test validation with kwargs input format."""
        validator = ValidatorService()

        config_yaml = yaml.dump({
            "id": "test-001",
            "name": "Test",
            "validation": {
                "type": "test_cases",
                "criteria": [
                    {
                        "name": "Test kwargs",
                        "input": {"kwargs": {"name": "Alice", "age": 30}},
                        "expected_output": "Alice is 30 years old",
                    },
                ],
            },
        })

        challenge = Challenge(
            id="test-001",
            name="Test",
            difficulty="easy",
            task_type="coding",
            config_yaml=config_yaml,
            created_at=datetime.utcnow()
        )

        response = """
def greet(name, age):
    return f"{name} is {age} years old"
"""

        result = await validator.validate(challenge, response)

        assert result.is_correct is True
        assert result.test_results[0]["passed"] is True

    @pytest.mark.asyncio
    async def test_validate_no_test_cases(self):
        """Test validation with no test cases defined."""
        validator = ValidatorService()

        config_yaml = yaml.dump({
            "id": "test-001",
            "name": "Test",
            "validation": {
                "type": "test_cases",
                "criteria": [],
            },
        })

        challenge = Challenge(
            id="test-001",
            name="Test",
            difficulty="easy",
            task_type="coding",
            config_yaml=config_yaml,
            created_at=datetime.utcnow()
        )

        result = await validator.validate(challenge, "def test(): pass")

        assert result.is_correct is False
        assert "No test cases defined" in result.error_message


class TestValidateExactMatch:
    """Test exact_match validation type."""

    @pytest.mark.asyncio
    async def test_exact_match_success(self):
        """Test exact match validation passes for matching text."""
        validator = ValidatorService()

        config_yaml = yaml.dump({
            "id": "test-001",
            "name": "Test",
            "validation": {
                "type": "exact_match",
                "criteria": {
                    "expected_answer": "42",
                },
            },
        })

        challenge = Challenge(
            id="test-001",
            name="Test",
            difficulty="easy",
            task_type="question_answering",
            config_yaml=config_yaml,
            created_at=datetime.utcnow()
        )

        result = await validator.validate(challenge, "42")

        assert result.is_correct is True
        assert "matches expected answer" in result.feedback

    @pytest.mark.asyncio
    async def test_exact_match_failure(self):
        """Test exact match validation fails for different text."""
        validator = ValidatorService()

        config_yaml = yaml.dump({
            "id": "test-001",
            "name": "Test",
            "validation": {
                "type": "exact_match",
                "criteria": {
                    "expected_answer": "Paris",
                },
            },
        })

        challenge = Challenge(
            id="test-001",
            name="Test",
            difficulty="easy",
            task_type="question_answering",
            config_yaml=config_yaml,
            created_at=datetime.utcnow()
        )

        result = await validator.validate(challenge, "London")

        assert result.is_correct is False
        assert "does not match" in result.feedback

    @pytest.mark.asyncio
    async def test_exact_match_case_insensitive(self):
        """Test exact match with case_sensitive=False."""
        validator = ValidatorService()

        config_yaml = yaml.dump({
            "id": "test-001",
            "name": "Test",
            "validation": {
                "type": "exact_match",
                "criteria": {
                    "expected_answer": "Hello",
                    "case_sensitive": False,
                },
            },
        })

        challenge = Challenge(
            id="test-001",
            name="Test",
            difficulty="easy",
            task_type="question_answering",
            config_yaml=config_yaml,
            created_at=datetime.utcnow()
        )

        result = await validator.validate(challenge, "hello")

        assert result.is_correct is True

    @pytest.mark.asyncio
    async def test_exact_match_case_sensitive(self):
        """Test exact match with case_sensitive=True."""
        validator = ValidatorService()

        config_yaml = yaml.dump({
            "id": "test-001",
            "name": "Test",
            "validation": {
                "type": "exact_match",
                "criteria": {
                    "expected_answer": "Hello",
                    "case_sensitive": True,
                },
            },
        })

        challenge = Challenge(
            id="test-001",
            name="Test",
            difficulty="easy",
            task_type="question_answering",
            config_yaml=config_yaml,
            created_at=datetime.utcnow()
        )

        result = await validator.validate(challenge, "hello")

        assert result.is_correct is False

    @pytest.mark.asyncio
    async def test_exact_match_trim_whitespace(self):
        """Test exact match trims whitespace by default."""
        validator = ValidatorService()

        config_yaml = yaml.dump({
            "id": "test-001",
            "name": "Test",
            "validation": {
                "type": "exact_match",
                "criteria": {
                    "expected_answer": "answer",
                    "trim_whitespace": True,
                },
            },
        })

        challenge = Challenge(
            id="test-001",
            name="Test",
            difficulty="easy",
            task_type="question_answering",
            config_yaml=config_yaml,
            created_at=datetime.utcnow()
        )

        result = await validator.validate(challenge, "  answer  ")

        assert result.is_correct is True

    @pytest.mark.asyncio
    async def test_exact_match_legacy_format(self):
        """Test exact match with legacy string criteria format."""
        validator = ValidatorService()

        config_yaml = yaml.dump({
            "id": "test-001",
            "name": "Test",
            "validation": {
                "type": "exact_match",
                "criteria": "simple answer",
            },
        })

        challenge = Challenge(
            id="test-001",
            name="Test",
            difficulty="easy",
            task_type="question_answering",
            config_yaml=config_yaml,
            created_at=datetime.utcnow()
        )

        result = await validator.validate(challenge, "Simple Answer")

        assert result.is_correct is True

    @pytest.mark.asyncio
    async def test_exact_match_multiple_acceptable(self):
        """Test exact match with multiple acceptable answers."""
        validator = ValidatorService()

        config_yaml = yaml.dump({
            "id": "test-001",
            "name": "Test",
            "validation": {
                "type": "exact_match",
                "criteria": ["yes", "yeah", "yep"],
            },
        })

        challenge = Challenge(
            id="test-001",
            name="Test",
            difficulty="easy",
            task_type="question_answering",
            config_yaml=config_yaml,
            created_at=datetime.utcnow()
        )

        result = await validator.validate(challenge, "Yeah")

        assert result.is_correct is True


class TestValidatePatternMatch:
    """Test pattern_match validation type."""

    @pytest.mark.asyncio
    async def test_pattern_match_success(self):
        """Test pattern match validation with matching pattern."""
        validator = ValidatorService()

        config_yaml = yaml.dump({
            "id": "test-001",
            "name": "Test",
            "validation": {
                "type": "pattern_match",
                "pattern": r"\d{3}-\d{4}",
            },
        })

        challenge = Challenge(
            id="test-001",
            name="Test",
            difficulty="easy",
            task_type="extraction",
            config_yaml=config_yaml,
            created_at=datetime.utcnow()
        )

        result = await validator.validate(challenge, "123-4567")

        assert result.is_correct is True

    @pytest.mark.asyncio
    async def test_pattern_match_failure(self):
        """Test pattern match validation with non-matching pattern."""
        validator = ValidatorService()

        config_yaml = yaml.dump({
            "id": "test-001",
            "name": "Test",
            "validation": {
                "type": "pattern_match",
                "pattern": r"\d{3}-\d{4}",
            },
        })

        challenge = Challenge(
            id="test-001",
            name="Test",
            difficulty="easy",
            task_type="extraction",
            config_yaml=config_yaml,
            created_at=datetime.utcnow()
        )

        result = await validator.validate(challenge, "invalid")

        assert result.is_correct is False

    @pytest.mark.asyncio
    async def test_pattern_match_invalid_regex(self):
        """Test pattern match with invalid regex pattern."""
        validator = ValidatorService()

        config_yaml = yaml.dump({
            "id": "test-001",
            "name": "Test",
            "validation": {
                "type": "pattern_match",
                "pattern": r"[invalid(regex",
            },
        })

        challenge = Challenge(
            id="test-001",
            name="Test",
            difficulty="easy",
            task_type="extraction",
            config_yaml=config_yaml,
            created_at=datetime.utcnow()
        )

        result = await validator.validate(challenge, "test")

        assert result.is_correct is False
        assert "Invalid regex pattern" in result.error_message


class TestValidationEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_invalid_yaml_config(self):
        """Test validation with invalid YAML config."""
        validator = ValidatorService()

        challenge = Challenge(
            id="test-001",
            name="Test",
            difficulty="easy",
            task_type="coding",
            config_yaml="invalid: yaml: :",
            created_at=datetime.utcnow()
        )

        result = await validator.validate(challenge, "test")

        assert result.is_correct is False
        assert "Invalid challenge configuration" in result.error_message

    @pytest.mark.asyncio
    async def test_missing_validation_config(self):
        """Test validation with missing validation config."""
        validator = ValidatorService()

        config_yaml = yaml.dump({
            "id": "test-001",
            "name": "Test",
        })

        challenge = Challenge(
            id="test-001",
            name="Test",
            difficulty="easy",
            task_type="coding",
            config_yaml=config_yaml,
            created_at=datetime.utcnow()
        )

        result = await validator.validate(challenge, "test")

        assert result.is_correct is False
        assert "missing validation configuration" in result.error_message

    @pytest.mark.asyncio
    async def test_unsupported_validation_type(self):
        """Test validation with unsupported validation type."""
        validator = ValidatorService()

        config_yaml = yaml.dump({
            "id": "test-001",
            "name": "Test",
            "validation": {
                "type": "unsupported_type",
            },
        })

        challenge = Challenge(
            id="test-001",
            name="Test",
            difficulty="easy",
            task_type="coding",
            config_yaml=config_yaml,
            created_at=datetime.utcnow()
        )

        result = await validator.validate(challenge, "test")

        assert result.is_correct is False
        assert "Unsupported validation type" in result.error_message


class TestCompareOutputs:
    """Test output comparison helper."""

    def test_compare_none(self):
        """Test comparing None values."""
        validator = ValidatorService()

        assert validator._compare_outputs(None, None) is True
        assert validator._compare_outputs(None, 5) is False
        assert validator._compare_outputs(5, None) is False

    def test_compare_floats(self):
        """Test comparing floats with tolerance."""
        validator = ValidatorService()

        assert validator._compare_outputs(1.0, 1.0) is True
        assert validator._compare_outputs(1.0, 1.0000001) is True
        assert validator._compare_outputs(1.0, 2.0) is False

    def test_compare_lists(self):
        """Test comparing lists."""
        validator = ValidatorService()

        assert validator._compare_outputs([1, 2, 3], [1, 2, 3]) is True
        assert validator._compare_outputs([1, 2], [1, 2, 3]) is False
        assert validator._compare_outputs([1, 2, 3], [3, 2, 1]) is False

    def test_compare_dicts(self):
        """Test comparing dictionaries."""
        validator = ValidatorService()

        assert validator._compare_outputs({"a": 1}, {"a": 1}) is True
        assert validator._compare_outputs({"a": 1}, {"a": 2}) is False
        assert validator._compare_outputs({"a": 1}, {"b": 1}) is False

    def test_compare_primitives(self):
        """Test comparing primitive types."""
        validator = ValidatorService()

        assert validator._compare_outputs(42, 42) is True
        assert validator._compare_outputs("hello", "hello") is True
        assert validator._compare_outputs(True, True) is True
        assert validator._compare_outputs(42, 43) is False


class TestExtractCode:
    """Test code extraction from responses."""

    def test_extract_from_markdown_code_block(self):
        """Test extracting code from markdown code block."""
        validator = ValidatorService()

        response = """
```python
def test():
    return 42
```
"""

        code = validator._extract_code(response)

        assert "def test():" in code
        assert "return 42" in code
        assert "```" not in code

    def test_extract_without_code_block(self):
        """Test extracting code without markdown."""
        validator = ValidatorService()

        response = "def test():\n    return 42"

        code = validator._extract_code(response)

        assert code == "def test():\n    return 42"

    def test_extract_from_multiple_code_blocks(self):
        """Test extracting from multiple code blocks uses first."""
        validator = ValidatorService()

        response = """
```python
def first():
    pass
```

```python
def second():
    pass
```
"""

        code = validator._extract_code(response)

        assert "def first():" in code
        assert "def second():" not in code
