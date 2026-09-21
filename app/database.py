"""
Token Golf - Database Configuration and Dependencies

Provides database engine, session factory, and FastAPI dependency
for database session injection.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings

settings = get_settings()

# Create async engine
engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    # Connection pool settings
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
)

# Create async session factory
async_session_factory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database session injection.

    Yields an async database session that automatically handles
    transaction lifecycle and cleanup.

    Usage:
        @app.get("/api/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            # Use db here
            pass

    Yields:
        AsyncSession: Database session

    Example:
        from fastapi import Depends
        from sqlalchemy.ext.asyncio import AsyncSession
        from app.database import get_db

        @app.get("/api/challenges/{id}")
        async def get_challenge(
            challenge_id: str,
            db: AsyncSession = Depends(get_db)
        ):
            loader = ChallengeLoaderService(db, settings.challenges_dir)
            challenge = await loader.get_challenge(challenge_id)
            return challenge
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database (create tables if needed).

    Note: In production, use Alembic migrations instead.
    This is mainly for testing.
    """
    from app.models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Close database engine and dispose of connection pool.

    Called during application shutdown.
    """
    await engine.dispose()
