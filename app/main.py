"""
Token Golf - FastAPI Application Entry Point

Phase 0: Minimal app with health check
Phase 1.2: Configuration management integrated
Phase 2.1: Challenge loader service integrated
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import async_session_factory, close_db
from app.services import ChallengeLoaderService

# Load settings
settings = get_settings()

# Configure logging
logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Token Golf starting up...")

    # Preload challenges if configured
    if settings.preload_challenges:
        logger.info("Preloading challenges...")
        try:
            async with async_session_factory() as session:
                challenges_dir = Path(settings.challenges_dir)
                loader = ChallengeLoaderService(session, challenges_dir)
                count = await loader.preload_all_challenges()
                logger.info(f"Successfully preloaded {count} challenges")
        except Exception as e:
            logger.error(f"Failed to preload challenges: {e}")
            # Don't fail startup in development
            if settings.is_production:
                raise
    else:
        logger.info("Challenge preload disabled (PRELOAD_CHALLENGES=false)")

    logger.info("Token Golf startup complete")

    yield

    # Shutdown
    logger.info("Token Golf shutting down...")
    await close_db()
    logger.info("Token Golf shutdown complete")


app = FastAPI(
    title="Token Golf",
    description="AI Token Optimization Game - Teaching token efficiency through competition",
    version="0.1.0",
    debug=settings.debug,
    docs_url="/docs" if settings.enable_docs else None,
    redoc_url="/redoc" if settings.enable_docs else None,
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """Root endpoint - welcome message"""
    return {
        "message": "Welcome to Token Golf!",
        "version": "0.1.0",
        "status": "Phase 2.1 - Challenge Loader Complete",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration"""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "token-golf",
            "version": "0.1.0",
            "environment": settings.env,
            "database": "sqlite" if settings.using_sqlite else "postgresql",
        },
        status_code=200,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
