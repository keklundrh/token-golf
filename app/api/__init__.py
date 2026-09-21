"""
Token Golf - API Layer

REST API endpoints for the Token Golf application.

Modules:
    - challenges: Challenge listing and retrieval endpoints
"""

from app.api.challenges import router as challenges_router

__all__ = ["challenges_router"]
