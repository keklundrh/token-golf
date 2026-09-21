"""
Token Golf - Service Layer

Business logic services for the Token Golf application.

Services:
    - ChallengeLoaderService: Load and manage challenge definitions
    - LLMClient: Interact with LLM providers (Claude API)
    - LLMResponse: Structured LLM response with token counts
    - MockLLMClient: Mock client for testing
    - ValidatorService: Validate LLM responses against challenge criteria
    - ValidationResult: Structured validation result
"""

from app.services.challenge_loader import ChallengeLoaderService
from app.services.llm_client import LLMClient, LLMResponse, MockLLMClient
from app.services.validator import ValidatorService, ValidationResult

__all__ = [
    "ChallengeLoaderService",
    "LLMClient",
    "LLMResponse",
    "MockLLMClient",
    "ValidatorService",
    "ValidationResult",
]
