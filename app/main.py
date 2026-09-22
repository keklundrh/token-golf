"""
Token Golf - FastAPI Application Entry Point

Phase 0: Minimal app with health check
Phase 1.2: Configuration management integrated
Phase 2.1: Challenge loader service integrated
Phase 3.1: Challenge API endpoints
Phase 3.2: Game API endpoints
Phase 3.3: Leaderboard API endpoints
Phase 4: Frontend integration - static files and template routes
Phase 6: Session timeout enforcement
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

import yaml
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select

from app.api import challenges_router, game_router, leaderboard_router
from app.config import get_settings
from app.database import async_session_factory, close_db, init_db
from app.models import Challenge, Score, Session, SessionParticipant, User
from app.services import ChallengeLoaderService, SessionManager

# Load settings
settings = get_settings()

# Configure logging
logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Background task handle for session timeout checker
_timeout_task = None


async def check_expired_sessions_loop():
    """
    Background task to periodically mark expired sessions as DNF.

    Runs every 5 minutes to check for sessions that have exceeded their timeout.
    This ensures sessions are marked DNF even if no API calls are made.
    """
    while True:
        try:
            await asyncio.sleep(300)  # Check every 5 minutes
            logger.debug("Running expired session check...")

            async with async_session_factory() as session:
                manager = SessionManager(session)
                marked_count = await manager.mark_expired_sessions()

                if marked_count > 0:
                    logger.info(f"Background task: marked {marked_count} expired sessions as DNF")

        except asyncio.CancelledError:
            logger.info("Expired session checker task cancelled")
            break
        except Exception as e:
            logger.error(f"Error in expired session checker: {e}", exc_info=True)
            # Continue running despite errors


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

    # Start background task for session timeout checking
    global _timeout_task
    _timeout_task = asyncio.create_task(check_expired_sessions_loop())
    logger.info("Started background task for session timeout checking")

    logger.info("Token Golf startup complete")

    yield

    # Shutdown
    logger.info("Token Golf shutting down...")

    # Cancel background task
    if _timeout_task:
        _timeout_task.cancel()
        try:
            await _timeout_task
        except asyncio.CancelledError:
            pass

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


# ============================================================================
# Custom Exception Handlers
# ============================================================================


def is_api_request(request: Request) -> bool:
    """Check if request is for an API endpoint (expects JSON response)."""
    return request.url.path.startswith("/api/") or request.headers.get("accept", "").startswith("application/json")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Global HTTP exception handler.
    Returns JSON for API requests, HTML for web requests.
    """
    # API requests get JSON
    if is_api_request(request):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    # Web requests get HTML pages
    # 404 Not Found
    if exc.status_code == 404:
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

    # 503 Service Unavailable (LLM Weather Delay)
    elif exc.status_code == 503:
        try:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "title": "Weather Delay",
                    "icon": "&#9788;&#65039;&#9729;&#65039;",
                    "heading": "Weather Delay",
                    "status_code": 503,
                    "message": "The LLM service is temporarily unavailable.",
                    "detail": exc.detail,
                    "show_retry": True,
                    "back_text": "Return to Clubhouse",
                },
                status_code=503,
            )
        except Exception as e:
            logger.error(f"Error rendering 503 template: {e}")
            return JSONResponse(
                status_code=503,
                content={"detail": exc.detail},
            )

    # 400 Bad Request / Validation Errors
    elif exc.status_code == 400:
        try:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "title": "Invalid Request",
                    "icon": "&#9888;&#65039;",
                    "heading": "Penalty Stroke",
                    "status_code": 400,
                    "message": "There was a problem with your request.",
                    "detail": exc.detail,
                    "back_text": "Try Again",
                },
                status_code=400,
            )
        except Exception as e:
            logger.error(f"Error rendering 400 template: {e}")
            return JSONResponse(
                status_code=400,
                content={"detail": exc.detail},
            )

    # 401 Unauthorized
    elif exc.status_code == 401:
        try:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "title": "Unauthorized",
                    "icon": "&#128274;",
                    "heading": "Access Denied",
                    "status_code": 401,
                    "message": "You need to sign in to access this.",
                    "detail": exc.detail,
                    "back_url": "/",
                    "back_text": "Sign In",
                },
                status_code=401,
            )
        except Exception as e:
            logger.error(f"Error rendering 401 template: {e}")
            return JSONResponse(
                status_code=401,
                content={"detail": exc.detail},
            )

    # Other HTTP errors - use generic error template
    else:
        try:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "title": f"Error {exc.status_code}",
                    "status_code": exc.status_code,
                    "message": str(exc.detail),
                },
                status_code=exc.status_code,
            )
        except Exception as e:
            logger.error(f"Error rendering error template: {e}")
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
            )


@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    """
    Handle 500 Internal Server Error.
    Shows golf-themed "Weather Delay" page.
    """
    logger.error(f"Internal server error: {exc}", exc_info=True)

    # API requests get JSON
    if is_api_request(request):
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "message": "The course is experiencing technical difficulties.",
            },
        )

    # Web requests get HTML
    try:
        return templates.TemplateResponse(
            "500.html",
            {
                "request": request,
                "error_message": str(exc) if settings.debug else None,
            },
            status_code=500,
        )
    except Exception as e:
        logger.error(f"Error rendering 500 template: {e}")
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html>
            <head><title>500 - Server Error</title></head>
            <body>
                <h1>500 - Server Error</h1>
                <p>Something went wrong. Please try again later.</p>
                <p><a href="/">Go to Home</a></p>
            </body>
            </html>
            """,
            status_code=500,
        )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Catch-all exception handler for unhandled exceptions.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    # API requests get JSON
    if is_api_request(request):
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An unexpected error occurred",
                "message": str(exc) if settings.debug else "Please try again later.",
            },
        )

    # Web requests get HTML
    try:
        return templates.TemplateResponse(
            "500.html",
            {
                "request": request,
                "error_message": str(exc) if settings.debug else None,
            },
            status_code=500,
        )
    except Exception as e:
        logger.error(f"Error rendering 500 template: {e}")
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html>
            <head><title>500 - Server Error</title></head>
            <body>
                <h1>500 - Server Error</h1>
                <p>Something went wrong. Please try again later.</p>
                <p><a href="/">Go to Home</a></p>
            </body>
            </html>
            """,
            status_code=500,
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
async def game_page(request: Request, session_id: str, challenge: Optional[str] = None):
    """Game page - active game session with optional challenge selection"""
    try:
        async with async_session_factory() as db:
            # Fetch session
            result = await db.execute(
                select(Session).where(Session.id == session_id)
            )
            session = result.scalar_one_or_none()

            if not session:
                raise HTTPException(status_code=404, detail="Session not found")

            # Get user from session participants
            result = await db.execute(
                select(User)
                .join(SessionParticipant)
                .where(SessionParticipant.session_id == session_id)
                .limit(1)
            )
            user = result.scalar_one_or_none()

            # Get course and determine which challenge to load
            challenges_dir = Path(settings.challenges_dir)
            loader = ChallengeLoaderService(db, challenges_dir)
            course = await loader.get_course(session.course_id)

            # Load requested challenge, or first challenge if none specified
            challenge_obj = None
            if course and course.get("holes"):
                # Use query param if provided, otherwise use first challenge
                target_challenge_id = challenge if challenge else course["holes"][0]

                # Validate that the challenge is in the course
                if target_challenge_id in course["holes"]:
                    result = await db.execute(
                        select(Challenge).where(Challenge.id == target_challenge_id)
                    )
                    challenge_obj = result.scalar_one_or_none()
                else:
                    # If invalid challenge, fall back to first
                    result = await db.execute(
                        select(Challenge).where(Challenge.id == course["holes"][0])
                    )
                    challenge_obj = result.scalar_one_or_none()

            # Parse challenge config if available
            challenge_data = None
            if challenge_obj:
                try:
                    challenge_data = yaml.safe_load(challenge_obj.config_yaml)
                except Exception as e:
                    logger.error(f"Error parsing challenge config: {e}")
                    challenge_data = {}

            # If no challenge found, provide empty placeholder
            # (the real data loads via API on page load)
            if not challenge_obj:
                challenge_obj = type('obj', (object,), {
                    'id': 'loading',
                    'name': 'Loading...',
                    'difficulty': 'medium',
                    'task_type': 'loading',
                })()
                challenge_data = {
                    'description': 'Loading challenge...',
                    'metadata': {}
                }

            # Create placeholder user stats (actual data loads via API)
            user_stats = {
                'total_tokens': 0,
                'attempts': 0,
                'rank': '-',
                'status': 'in_progress'
            }

            # Create placeholder leaderboard (actual data loads via API)
            leaderboard = []

            # Create placeholder comparison data (actual data loads via API)
            comparison_data = None

            # Create placeholder stats (actual data loads via API)
            stats = {
                'best_score': None,
                'average_score': None,
                'median_score': None,
                'total_attempts': 0
            }

            return templates.TemplateResponse(
                "game.html",
                {
                    "request": request,
                    "session_id": session_id,
                    "session": session,
                    "user": user,
                    "user_stats": user_stats,
                    "challenge": challenge_obj,
                    "challenge_data": challenge_data,
                    "leaderboard": leaderboard,
                    "comparison_data": comparison_data,
                    "stats": stats,
                },
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rendering game template: {e}", exc_info=True)
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
