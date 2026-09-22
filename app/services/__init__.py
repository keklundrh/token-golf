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
    - ScoringService: Record attempts and calculate scores
    - SessionManager: Manage session lifecycle and timeout enforcement
"""

from app.services.challenge_loader import ChallengeLoaderService
from app.services.course_loader import CourseLoaderService
from app.services.llm_client import LLMClient, LLMResponse, MockLLMClient
from app.services.scoring import ScoringService
from app.services.session_manager import SessionManager
from app.services.validator import ValidatorService, ValidationResult

__all__ = [
    "ChallengeLoaderService",
    "CourseLoaderService",
    "LLMClient",
    "LLMResponse",
    "MockLLMClient",
    "ScoringService",
    "SessionManager",
    "ValidatorService",
    "ValidationResult",
]
