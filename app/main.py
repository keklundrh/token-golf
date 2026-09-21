"""
Token Golf - FastAPI Application Entry Point

Phase 0: Minimal app with health check
Phase 1.2: Configuration management integrated
Phase 2.1: Challenge loader service integrated
Phase 3.1: Challenge API endpoints
Phase 3.2: Game API endpoints
Phase 3.3: Leaderboard API endpoints
Phase 4: Frontend integration - static files and template routes
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api import challenges_router, game_router, leaderboard_router
from app.config import get_settings
from app.database import async_session_factory, close_db, init_db
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

    # Create tables if needed (dev convenience; use Alembic in production)
    await init_db()
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

# Configure static files
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
else:
    logger.warning(f"Static directory not found: {static_dir}")

# Configure Jinja2 templates
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


# Custom exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Custom 404 page handler"""
    # Check if request is for API (JSON response) or web page (HTML response)
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=404,
            content={"detail": "API endpoint not found"},
        )

    # Return HTML 404 page for web requests
    try:
        return templates.TemplateResponse(
            "404.html",
            {"request": request},
            status_code=404,
        )
    except Exception as e:
        logger.error(f"Error rendering 404 template: {e}")
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html>
            <head><title>404 - Not Found</title></head>
            <body>
                <h1>404 - Page Not Found</h1>
                <p>The page you're looking for doesn't exist.</p>
                <p><a href="/">Go to Home</a></p>
            </body>
            </html>
            """,
            status_code=404,
        )


# Include API routers
app.include_router(challenges_router)
app.include_router(game_router)
app.include_router(leaderboard_router)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Home page - lobby/index"""
    try:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "version": "0.1.0",
                "status": "Phase 4 - Frontend Integration",
            },
        )
    except Exception as e:
        logger.error(f"Error rendering index template: {e}")
        # Fallback to simple HTML if template doesn't exist yet
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html>
            <head><title>Token Golf</title></head>
            <body>
                <h1>Welcome to Token Golf!</h1>
                <p>Frontend templates are being set up.</p>
                <p>API is available at <a href="/docs">/docs</a></p>
            </body>
            </html>
            """,
            status_code=200,
        )


@app.get("/game/{session_id}", response_class=HTMLResponse)
async def game_page(request: Request, session_id: str):
    """Game page - active game session"""
    try:
        return templates.TemplateResponse(
            "game.html",
            {
                "request": request,
                "session_id": session_id,
            },
        )
    except Exception as e:
        logger.error(f"Error rendering game template: {e}")
        return HTMLResponse(
            content=f"""
            <!DOCTYPE html>
            <html>
            <head><title>Token Golf - Game</title></head>
            <body>
                <h1>Game Session: {session_id}</h1>
                <p>Game template is being set up.</p>
                <p><a href="/">Back to Home</a></p>
            </body>
            </html>
            """,
            status_code=200,
        )


@app.get("/leaderboard", response_class=HTMLResponse)
async def leaderboard_page(request: Request):
    """Leaderboard page - global rankings"""
    try:
        return templates.TemplateResponse(
            "leaderboard.html",
            {
                "request": request,
            },
        )
    except Exception as e:
        logger.error(f"Error rendering leaderboard template: {e}")
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html>
            <head><title>Token Golf - Leaderboard</title></head>
            <body>
                <h1>Leaderboard</h1>
                <p>Leaderboard template is being set up.</p>
                <p><a href="/">Back to Home</a></p>
            </body>
            </html>
            """,
            status_code=200,
        )


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
