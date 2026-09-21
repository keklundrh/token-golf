"""
Token Golf - API Layer

REST API endpoints for the Token Golf application.

Modules:
    - challenges: Challenge listing and retrieval endpoints
    - game: Game session and attempt submission endpoints
    - leaderboard: Leaderboard views (global, per-hole, session)
"""

from app.api.challenges import router as challenges_router
from app.api.game import router as game_router
from app.api.leaderboard import router as leaderboard_router

__all__ = ["challenges_router", "game_router", "leaderboard_router"]
