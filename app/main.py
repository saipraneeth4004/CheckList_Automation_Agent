"""
FastAPI Main Application

This module initializes and configures the FastAPI application
for the Monthly Close Checklist Automation Agent.

Features:
- Application lifecycle management (startup/shutdown)
- CORS configuration
- API route registration
- Health check endpoints
- Session cleanup management
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import get_settings
from app.core.session import get_session_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle application startup and shutdown events.

    Startup Tasks:
    - Load application settings
    - Print startup information
    - Ensure required directories exist

    Shutdown Tasks:
    - Cleanup expired sessions
    """

    # -------------------------
    # Startup
    # -------------------------
    settings = get_settings()

    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    print(f"📁 Upload directory: {settings.upload_dir}")
    print(f"📁 Generated directory: {settings.generated_dir}")

    # Ensure required directories exist
    settings.get_upload_path()
    settings.get_generated_path()

    yield

    # -------------------------
    # Shutdown
    # -------------------------
    print("🛑 Shutting down application")

    # Cleanup expired sessions
    session_manager = get_session_manager()
    session_manager.cleanup_expired_sessions()


# =========================================================
# FastAPI Application Initialization
# =========================================================
app = FastAPI(
    title="Monthly Close Checklist Automation Agent",
    description=(
        "AI-powered month-end checklist validation "
        "and automation assistance platform."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# =========================================================
# CORS Middleware Configuration
# =========================================================
app.add_middleware(
    CORSMiddleware,

    # NOTE:
    # Replace "*" with allowed frontend domains in production.
    allow_origins=["*"],

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# API Route Registration
# =========================================================
app.include_router(
    router,
    prefix="/api/v1",
    tags=["checklist"],
)


# =========================================================
# Root Endpoint
# =========================================================
@app.get("/")
async def root():
    """
    Root endpoint for API metadata.

    Returns:
        dict: Basic application information and useful links.
    """

    return {
        "message": "Monthly Close Checklist Automation Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


# =========================================================
# Health Check Endpoint
# =========================================================
@app.get("/health")
async def health():
    """
    Health check endpoint.

    Returns:
        dict: API health status.
    """

    return {"status": "healthy"}


# =========================================================
# Application Entry Point
# =========================================================
if __name__ == "__main__":
    import uvicorn

    settings = get_settings()

    uvicorn.run(
        "app.main:app",
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        reload=settings.debug,
    )
