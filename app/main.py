"""
Token Golf - FastAPI Application Entry Point

Phase 0: Minimal app with health check
Phase 1.2: Configuration management integrated
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.config import get_settings

# Load settings
settings = get_settings()

app = FastAPI(
    title="Token Golf",
    description="AI Token Optimization Game - Teaching token efficiency through competition",
    version="0.1.0",
    debug=settings.debug,
    docs_url="/docs" if settings.enable_docs else None,
    redoc_url="/redoc" if settings.enable_docs else None,
)


@app.get("/")
async def root():
    """Root endpoint - welcome message"""
    return {
        "message": "Welcome to Token Golf!",
        "version": "0.1.0",
        "status": "Phase 0 - Container Foundation Complete",
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
