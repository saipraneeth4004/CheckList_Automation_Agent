"""
FastAPI main application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.api.routes import router
from app.core.session import get_session_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    settings = get_settings()
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    print(f"📁 Upload directory: {settings.upload_dir}")
    print(f"📁 Generated directory: {settings.generated_dir}")
    
    # Ensure directories exist
    settings.get_upload_path()
    settings.get_generated_path()
    
    yield
    
    # Shutdown
    print("🛑 Shutting down application")
    # Cleanup expired sessions
    session_manager = get_session_manager()
    session_manager.cleanup_expired_sessions()


# Create FastAPI app
app = FastAPI(
    title="Monthly Close Checklist Automation Agent",
    description="AI-powered month-end checklist validation and assistance",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1", tags=["checklist"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Monthly Close Checklist Automation Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


@app.get("/health")
async def health():
    """Simple health check"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        reload=settings.debug
    )
