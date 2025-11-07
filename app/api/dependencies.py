"""
FastAPI dependencies and utilities
"""

from fastapi import HTTPException, status
from app.core.session import get_session_manager, SessionManager
from app.core.config import get_settings, Settings
from app.core.storage import StorageManager


def get_session_manager_dependency() -> SessionManager:
    """Dependency to get session manager"""
    settings = get_settings()
    return get_session_manager(settings.session_timeout_minutes)


def get_storage_manager_dependency() -> StorageManager:
    """Dependency to get storage manager"""
    settings = get_settings()
    return StorageManager(
        settings.get_upload_path(),
        settings.get_generated_path()
    )


def validate_session(session_id: str, session_manager: SessionManager):
    """Validate that a session exists"""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    return session


def get_settings_dependency() -> Settings:
    """Dependency to get settings"""
    return get_settings()
