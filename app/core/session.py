"""
Session management for handling user sessions and uploaded files
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import uuid
import shutil
from dataclasses import dataclass, field


@dataclass
class SessionData:
    """Data structure for session information"""
    session_id: str
    created_at: datetime
    last_accessed: datetime
    upload_folder: Path
    files: List[str] = field(default_factory=list)
    validation_results: Optional[Dict[str, Any]] = None
    chat_history: List[Dict[str, str]] = field(default_factory=list)
    generated_documents: List[str] = field(default_factory=list)


class SessionManager:
    """Manages user sessions and their associated data"""
    
    def __init__(self, session_timeout_minutes: int = 60):
        self.sessions: Dict[str, SessionData] = {}
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
    
    def create_session(self, upload_base_dir: Path) -> str:
        """Create a new session and return session ID"""
        session_id = str(uuid.uuid4())
        session_folder = upload_base_dir / session_id
        session_folder.mkdir(parents=True, exist_ok=True)
        
        session_data = SessionData(
            session_id=session_id,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            upload_folder=session_folder
        )
        
        self.sessions[session_id] = session_data
        return session_id
    
    def get_session(self, session_id: str) -> Optional[SessionData]:
        """Retrieve session data by ID"""
        session = self.sessions.get(session_id)
        if session:
            session.last_accessed = datetime.now()
            return session
        return None
    
    def update_session(self, session_id: str, **kwargs) -> bool:
        """Update session data"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)
        
        return True
    
    def add_file(self, session_id: str, filename: str) -> bool:
        """Add a file to session's file list"""
        session = self.get_session(session_id)
        if session:
            if filename not in session.files:
                session.files.append(filename)
            return True
        return False
    
    def add_chat_message(self, session_id: str, role: str, content: str) -> bool:
        """Add a chat message to session history"""
        session = self.get_session(session_id)
        if session:
            session.chat_history.append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
            return True
        return False
    
    def add_generated_document(self, session_id: str, filename: str) -> bool:
        """Add a generated document to session"""
        session = self.get_session(session_id)
        if session:
            if filename not in session.generated_documents:
                session.generated_documents.append(filename)
            return True
        return False
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions and their files"""
        now = datetime.now()
        expired_sessions = []
        
        for session_id, session_data in self.sessions.items():
            if now - session_data.last_accessed > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.delete_session(session_id)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session and its associated files"""
        session = self.sessions.get(session_id)
        if session:
            # Delete session folder and files
            if session.upload_folder.exists():
                shutil.rmtree(session.upload_folder, ignore_errors=True)
            
            # Remove from sessions dict
            del self.sessions[session_id]
            return True
        return False
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        return len(self.sessions)


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager(session_timeout_minutes: int = 60) -> SessionManager:
    """Get or create global session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager(session_timeout_minutes)
    return _session_manager
