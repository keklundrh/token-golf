"""
Token Golf - Test Fixtures

Pytest fixtures for integration and unit testing.
Provides database sessions, test clients, and sample data.
"""

import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import AsyncGenerator
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from passlib.hash import bcrypt
import hashlib
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import Settings, get_settings
from app.database import get_db
from app.main import app
from app.models import Base
from app.models.challenge import Challenge
from app.models.session import Session, SessionParticipant
from app.models.user import User
from app.services.challenge_loader import ChallengeLoaderService


# ============================================================================
# Test Configuration
# ============================================================================

@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """
    Test settings with in-memory database.

    Returns:
        Settings configured for testing
    """
    settings = Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        debug=True,
        challenges_dir=str(Path(__file__).parent.parent / "challenges"),
    )
    return settings


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest_asyncio.fixture(scope="function")
async def db_engine(test_settings: Settings) -> AsyncGenerator[AsyncEngine, None]:
    """
    Create test database engine.

    Creates a fresh in-memory SQLite database for each test function.

    Yields:
        AsyncEngine for testing
    """
    engine = create_async_engine(
        test_settings.database_url,
        echo=test_settings.debug,
        future=True,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create test database session.

    Provides a clean database session for each test.
    Automatically rolls back transactions after test.

    Yields:
        AsyncSession for testing
    """
    async_session_factory = sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async with async_session_factory() as session:
        yield session
        await session.rollback()


# ============================================================================
# API Client Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def client(db_session: AsyncSession) -> TestClient:
    """
    FastAPI test client with dependency override.

    Overrides the database dependency to use test database session.

    Args:
        db_session: Test database session

    Returns:
        TestClient for API testing
    """
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# ============================================================================
# User Fixtures
# ============================================================================

def _hash_password(password: str) -> str:
    """Hash password using same method as game API."""
    salt = "token-golf-mvp-salt"
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


@pytest_asyncio.fixture
async def sample_user(db_session: AsyncSession) -> User:
    """
    Create a sample test user.

    Creates a user with known credentials for auth testing.

    Args:
        db_session: Database session

    Returns:
        User object
    """
    user = User(
        username="test-user",
        password_hash=_hash_password("test-password"),
        created_at=datetime.utcnow(),
        is_active=True,
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest_asyncio.fixture
async def multiple_users(db_session: AsyncSession) -> list[User]:
    """
    Create multiple test users for leaderboard testing.

    Args:
        db_session: Database session

    Returns:
        List of User objects
    """
    users = [
        User(
            username=f"player-{i}",
            password_hash=_hash_password(f"password-{i}"),
            created_at=datetime.utcnow(),
            is_active=True,
        )
        for i in range(1, 4)
    ]

    for user in users:
        db_session.add(user)

    await db_session.commit()

    for user in users:
        await db_session.refresh(user)

    return users


# ============================================================================
# Challenge Fixtures
# ============================================================================

@pytest_asyncio.fixture
async def challenge_loader(
    db_session: AsyncSession,
    test_settings: Settings,
) -> ChallengeLoaderService:
    """
    Create challenge loader service for testing.

    Args:
        db_session: Database session
        test_settings: Test settings

    Returns:
        ChallengeLoaderService instance
    """
    loader = ChallengeLoaderService(
        db_session,
        test_settings.challenges_dir,
    )
    return loader


@pytest_asyncio.fixture
async def sample_challenge(
    db_session: AsyncSession,
    challenge_loader: ChallengeLoaderService,
) -> Challenge:
    """
    Load a sample challenge for testing.

    Loads hole-001 from YAML files.

    Args:
        db_session: Database session
        challenge_loader: Challenge loader service

    Returns:
        Challenge object
    """
    challenge = await challenge_loader.get_challenge("hole-001")

    if not challenge:
        raise ValueError("Failed to load sample challenge hole-001")

    return challenge


@pytest_asyncio.fixture
async def all_challenges(
    db_session: AsyncSession,
    challenge_loader: ChallengeLoaderService,
) -> list[Challenge]:
    """
    Load all challenges for testing.

    Args:
        db_session: Database session
        challenge_loader: Challenge loader service

    Returns:
        List of all Challenge objects
    """
    count = await challenge_loader.preload_all_challenges()
    challenges = await challenge_loader.list_challenges()

    return challenges


# ============================================================================
# Session Fixtures
# ============================================================================

@pytest_asyncio.fixture
async def sample_session(
    db_session: AsyncSession,
    sample_user: User,
) -> Session:
    """
    Create a sample game session.

    Creates an active session for testing.

    Args:
        db_session: Database session
        sample_user: Test user

    Returns:
        Session object
    """
    session_id = str(uuid4())
    created_at = datetime.utcnow()
    timeout_hours = 3

    session = Session(
        id=session_id,
        course_id="beginner-course",
        created_at=created_at,
        timeout_hours=timeout_hours,
        status="active",
        expires_at=Session.calculate_expires_at(created_at, timeout_hours),
    )

    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    # Add user as participant
    participant = SessionParticipant(
        session_id=session.id,
        user_id=sample_user.id,
        joined_at=datetime.utcnow(),
    )

    db_session.add(participant)
    await db_session.commit()

    return session


@pytest_asyncio.fixture
async def expired_session(
    db_session: AsyncSession,
    sample_user: User,
) -> Session:
    """
    Create an expired session for timeout testing.

    Args:
        db_session: Database session
        sample_user: Test user

    Returns:
        Expired Session object
    """
    session_id = str(uuid4())
    created_at = datetime.utcnow() - timedelta(hours=4)
    timeout_hours = 3

    session = Session(
        id=session_id,
        course_id="beginner-course",
        created_at=created_at,
        timeout_hours=timeout_hours,
        status="active",
        expires_at=Session.calculate_expires_at(created_at, timeout_hours),
    )

    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    # Add user as participant
    participant = SessionParticipant(
        session_id=session.id,
        user_id=sample_user.id,
        joined_at=datetime.utcnow(),
    )

    db_session.add(participant)
    await db_session.commit()

    return session


# ============================================================================
# Event Loop Configuration
# ============================================================================

@pytest.fixture(scope="session")
def event_loop_policy():
    """
    Set event loop policy for async tests.

    Required for pytest-asyncio to work correctly.
    """
    return asyncio.get_event_loop_policy()
