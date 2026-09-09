"""
Token Golf - FastAPI Application Entry Point

This is a minimal FastAPI application for Phase 0.
Full functionality will be added in Phase 1.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Token Golf",
    description="AI Token Optimization Game - Teaching token efficiency through competition",
    version="0.1.0",
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
