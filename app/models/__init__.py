"""
Token Golf - Database Models

SQLAlchemy ORM models for the Token Golf application.
All models use SQLAlchemy 2.0+ declarative style with type hints.

Models:
    - User: Players with auto-generated usernames
    - Session: Game sessions with timeout
    - SessionParticipant: Join table for users and sessions
    - Challenge: Individual challenges loaded from YAML
    - Attempt: Each prompt submission
    - Score: Aggregated scores per user/session/challenge
"""

from app.models.attempt import Attempt
from app.models.base import Base
from app.models.challenge import Challenge
from app.models.score import Score
from app.models.session import Session, SessionParticipant
from app.models.user import User

# Export all models for easy importing
__all__ = [
    "Base",
    "User",
    "Session",
    "SessionParticipant",
    "Challenge",
    "Attempt",
    "Score",
]
