"""
Token Golf - Validator Service

Validates LLM responses against challenge criteria.
Supports multiple validation types with extensible architecture.

MVP supports: test_cases, exact_match
Future: pattern_match, semantic_similarity, custom_script
"""

import logging
import re
import sys
from io import StringIO
from typing import Any, Optional

import yaml
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ValidationResult(BaseModel):
    """
    Result of validating an LLM response against challenge criteria.

    Used to determine if a challenge attempt was successful.
    """

    is_correct: bool = Field(
        ..., description="Whether the response passed validation"
    )

    feedback: Optional[str] = Field(
        None, description="Human-readable feedback on validation"
    )

    test_results: Optional[list[dict]] = Field(
        None, description="Individual test case results (for coding challenges)"
    )

    error_message: Optional[str] = Field(
        None, description="Error message if validation failed"
    )


class ValidatorService:
    """
    Service for validating LLM responses against challenge criteria.

    Supports multiple validation types:
    - test_cases: Run code against test inputs (MVP)
    - exact_match: String comparison (MVP)
    - pattern_match: Regex matching (Post-MVP)
    - semantic_similarity: Embeddings comparison (Post-MVP)
    - custom_script: Execute custom validator (Post-MVP)

    Usage:
        validator = ValidatorService()

        result = await validator.validate(
            challenge=challenge_object,
            response="def add(a, b): return a + b"
        )

        if result.is_correct:
            print("Challenge passed!")
    """

    async def validate(
        self,
        challenge: Any,
        response: str,
    ) -> ValidationResult:
        """
        Validate an LLM response against challenge criteria.

        Args:
            challenge: Challenge object with config_yaml
            response: LLM response text to validate

        Returns:
            ValidationResult with pass/fail and feedback

        Raises:
            ValueError: If challenge config is invalid
        """
        # Parse challenge config
        try:
            config = yaml.safe_load(challenge.config_yaml)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse challenge config: {e}")
            return ValidationResult(
                is_correct=False,
                error_message=f"Invalid challenge configuration: {e}"
            )

        # Get validation config
        if "validation" not in config:
            return ValidationResult(
                is_correct=False,
                error_message="Challenge missing validation configuration"
            )

        validation_config = config["validation"]
        validation_type = validation_config.get("type")

        # Route to appropriate validator
        if validation_type == "test_cases":
            return await self._validate_test_cases(validation_config, response)
        elif validation_type == "exact_match":
            return await self._validate_exact_match(validation_config, response)
        elif validation_type == "pattern_match":
            return await self._validate_pattern_match(validation_config, response)
        else:
            return ValidationResult(
                is_correct=False,
                error_message=f"Unsupported validation type: {validation_type}"
            )

    # ========================================================================
    # MVP Validation Types
    # ========================================================================

    async def _validate_test_cases(
        self,
        validation_config: dict,
        response: str,
    ) -> ValidationResult:
        """
        Validate by running code against test cases.

        Executes the LLM-generated code with test inputs and compares
        outputs to expected values.

        Args:
            validation_config: Validation configuration from challenge
            response: LLM response (should be executable Python code)

        Returns:
            ValidationResult with test results
        """
        criteria = validation_config.get("criteria", [])

        if not criteria:
            return ValidationResult(
                is_correct=False,
                error_message="No test cases defined"
            )

        # Extract code from response (handle markdown code blocks)
        code = self._extract_code(response)

        # Run test cases
        test_results = []
        all_passed = True

        for i, test_case in enumerate(criteria):
            test_name = test_case.get("name", f"Test {i + 1}")
            test_input = test_case.get("input", {})
            expected_output = test_case.get("expected_output")
            timeout_ms = test_case.get("timeout_ms", 1000)

            logger.debug(f"Running test case: {test_name}")

            # Run test
            try:
                actual_output = await self._execute_code(
                    code=code,
                    test_input=test_input,
                    timeout_ms=timeout_ms
                )

                # Compare outputs
                passed = self._compare_outputs(actual_output, expected_output)

                test_results.append({
                    "name": test_name,
                    "passed": passed,
                    "expected": expected_output,
                    "actual": actual_output,
                })

                if not passed:
                    all_passed = False

            except Exception as e:
                logger.warning(f"Test case '{test_name}' failed with error: {e}")
                test_results.append({
                    "name": test_name,
                    "passed": False,
                    "error": str(e),
                })
                all_passed = False

        # Build feedback
        passed_count = sum(1 for t in test_results if t.get("passed", False))
        total_count = len(test_results)

        feedback = f"Passed {passed_count}/{total_count} test cases"

        return ValidationResult(
            is_correct=all_passed,
            feedback=feedback,
            test_results=test_results,
        )

    async def _validate_exact_match(
        self,
        validation_config: dict,
        response: str,
    ) -> ValidationResult:
        """
        Validate by exact string matching.

        Compares LLM response to expected string(s).
        Supports multiple acceptable answers.

        Args:
            validation_config: Validation configuration
            response: LLM response text

        Returns:
            ValidationResult with match status
        """
        criteria = validation_config.get("criteria")

        if not criteria:
            return ValidationResult(
                is_correct=False,
                error_message="No match criteria defined"
            )

        # Handle dict format (expected_answer, case_sensitive, trim_whitespace)
        if isinstance(criteria, dict):
            expected_answer = criteria.get("expected_answer")
            if not expected_answer:
                return ValidationResult(
                    is_correct=False,
                    error_message="No 'expected_answer' in criteria"
                )

            case_sensitive = criteria.get("case_sensitive", False)
            trim_whitespace = criteria.get("trim_whitespace", True)

            # Normalize based on criteria settings
            test_response = response
            test_expected = expected_answer

            if trim_whitespace:
                test_response = test_response.strip()
                test_expected = test_expected.strip()

            if not case_sensitive:
                test_response = test_response.lower()
                test_expected = test_expected.lower()

            if test_response == test_expected:
                return ValidationResult(
                    is_correct=True,
                    feedback=f"Response matches expected answer"
                )
            else:
                return ValidationResult(
                    is_correct=False,
                    feedback=f"Response does not match. Expected: '{expected_answer}', Got: '{response}'"
                )

        # Handle legacy format (simple string or list of strings)
        normalized_response = response.strip().lower()

        # Support multiple acceptable answers
        if isinstance(criteria, list):
            acceptable_answers = [str(c).strip().lower() for c in criteria]
        else:
            acceptable_answers = [str(criteria).strip().lower()]

        # Check if response matches any acceptable answer
        for answer in acceptable_answers:
            if normalized_response == answer:
                return ValidationResult(
                    is_correct=True,
                    feedback=f"Response matches expected: '{answer}'"
                )

        # No match found
        return ValidationResult(
            is_correct=False,
            feedback=f"Response does not match. Expected one of: {acceptable_answers}",
        )

    # ========================================================================
    # Post-MVP Validation Types
    # ========================================================================

    async def _validate_pattern_match(
        self,
        validation_config: dict,
        response: str,
    ) -> ValidationResult:
        """
        Validate by regex pattern matching.

        NOTE: Post-MVP feature, basic implementation for future use.

        Args:
            validation_config: Validation configuration
            response: LLM response text

        Returns:
            ValidationResult with match status
        """
        pattern = validation_config.get("pattern")

        if not pattern:
            return ValidationResult(
                is_correct=False,
                error_message="No pattern defined"
            )

        try:
            if re.search(pattern, response, re.MULTILINE | re.DOTALL):
                return ValidationResult(
                    is_correct=True,
                    feedback="Response matches pattern"
                )
            else:
                return ValidationResult(
                    is_correct=False,
                    feedback=f"Response does not match pattern: {pattern}"
                )
        except re.error as e:
            return ValidationResult(
                is_correct=False,
                error_message=f"Invalid regex pattern: {e}"
            )

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _extract_code(self, response: str) -> str:
        """
        Extract code from LLM response.

        Handles responses with or without markdown code blocks.

        Args:
            response: LLM response text

        Returns:
            Extracted code
        """
        # Try to extract from markdown code block
        code_block_pattern = r"```(?:python)?\n(.*?)\n```"
        matches = re.findall(code_block_pattern, response, re.DOTALL)

        if matches:
            # Use first code block
            return matches[0].strip()

        # No code block found, use entire response
        return response.strip()

    async def _execute_code(
        self,
        code: str,
        test_input: dict,
        timeout_ms: int = 1000,
    ) -> Any:
        """
        Execute Python code with test inputs.

        NOTE: This is a simplified execution for MVP.
        Production should use proper sandboxing (docker, etc.)

        Args:
            code: Python code to execute
            test_input: Dictionary of input parameters
            timeout_ms: Timeout in milliseconds (currently not enforced)

        Returns:
            Output from code execution

        Raises:
            Exception: If code execution fails
        """
        # Create execution namespace
        namespace = {}

        # Execute code to define functions/variables
        try:
            exec(code, namespace)
        except Exception as e:
            raise ValueError(f"Code execution failed: {e}")

        # Find the main function to call
        # Look for common patterns: main(), solve(), answer(), or first function
        function_name = None

        for name in ["main", "solve", "answer", "run"]:
            if name in namespace and callable(namespace[name]):
                function_name = name
                break

        # If no standard name, find first callable
        if not function_name:
            for name, obj in namespace.items():
                if callable(obj) and not name.startswith("_"):
                    function_name = name
                    break

        if not function_name:
            raise ValueError("No callable function found in code")

        # Call the function with test inputs
        func = namespace[function_name]

        try:
            # Handle different input formats
            if test_input:
                # If single 'args' key, unpack it
                if "args" in test_input:
                    result = func(*test_input["args"])
                # If single 'kwargs' key, unpack it
                elif "kwargs" in test_input:
                    result = func(**test_input["kwargs"])
                # Otherwise pass as kwargs
                else:
                    result = func(**test_input)
            else:
                # No input, call with no args
                result = func()

            return result

        except Exception as e:
            raise ValueError(f"Function execution failed: {e}")

    def _compare_outputs(self, actual: Any, expected: Any) -> bool:
        """
        Compare actual and expected outputs.

        Handles different types and does approximate matching for floats.

        Args:
            actual: Actual output from code
            expected: Expected output from test case

        Returns:
            True if outputs match
        """
        # Handle None
        if actual is None and expected is None:
            return True

        # Handle floats with tolerance
        if isinstance(actual, float) and isinstance(expected, (int, float)):
            return abs(actual - expected) < 1e-6

        # Handle lists/tuples
        if isinstance(actual, (list, tuple)) and isinstance(expected, (list, tuple)):
            if len(actual) != len(expected):
                return False
            return all(self._compare_outputs(a, e) for a, e in zip(actual, expected))

        # Handle dicts
        if isinstance(actual, dict) and isinstance(expected, dict):
            if set(actual.keys()) != set(expected.keys()):
                return False
            return all(self._compare_outputs(actual[k], expected[k]) for k in actual.keys())

        # Default: use equality
        return actual == expected
