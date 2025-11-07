"""
File storage utilities for handling file operations
"""

from pathlib import Path
from typing import List, Optional
import shutil
import hashlib
from datetime import datetime


class StorageManager:
    """Manages file storage operations"""
    
    def __init__(self, base_upload_dir: Path, base_generated_dir: Path):
        self.upload_dir = base_upload_dir
        self.generated_dir = base_generated_dir
        
        # Ensure directories exist
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.generated_dir.mkdir(parents=True, exist_ok=True)
    
    def save_uploaded_file(self, file_content: bytes, filename: str, session_id: str) -> Path:
        """Save an uploaded file and return its path"""
        session_dir = self.upload_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = session_dir / filename
        
        # Write file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return file_path
    
    def save_generated_file(self, file_path: Path, session_id: str) -> Path:
        """Save a generated file to the generated directory"""
        session_gen_dir = self.generated_dir / session_id
        session_gen_dir.mkdir(parents=True, exist_ok=True)
        
        destination = session_gen_dir / file_path.name
        shutil.copy2(file_path, destination)
        
        return destination
    
    def get_session_files(self, session_id: str) -> List[Path]:
        """Get all files for a session"""
        session_dir = self.upload_dir / session_id
        if not session_dir.exists():
            return []
        
        return list(session_dir.glob('*'))
    
    def get_generated_files(self, session_id: str) -> List[Path]:
        """Get all generated files for a session"""
        session_gen_dir = self.generated_dir / session_id
        if not session_gen_dir.exists():
            return []
        
        return list(session_gen_dir.glob('*'))
    
    def get_file_info(self, file_path: Path) -> dict:
        """Get information about a file"""
        if not file_path.exists():
            return {}
        
        stat = file_path.stat()
        
        return {
            "filename": file_path.name,
            "size": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "extension": file_path.suffix,
            "path": str(file_path)
        }
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of a file"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def delete_session_files(self, session_id: str):
        """Delete all files for a session"""
        # Delete uploaded files
        session_upload_dir = self.upload_dir / session_id
        if session_upload_dir.exists():
            shutil.rmtree(session_upload_dir, ignore_errors=True)
        
        # Delete generated files
        session_gen_dir = self.generated_dir / session_id
        if session_gen_dir.exists():
            shutil.rmtree(session_gen_dir, ignore_errors=True)
    
    def get_total_storage_size(self, session_id: Optional[str] = None) -> dict:
        """Get storage size information"""
        if session_id:
            upload_size = sum(f.stat().st_size for f in self.get_session_files(session_id))
            generated_size = sum(f.stat().st_size for f in self.get_generated_files(session_id))
        else:
            upload_size = sum(f.stat().st_size for f in self.upload_dir.rglob('*') if f.is_file())
            generated_size = sum(f.stat().st_size for f in self.generated_dir.rglob('*') if f.is_file())
        
        return {
            "upload_size_mb": round(upload_size / (1024 * 1024), 2),
            "generated_size_mb": round(generated_size / (1024 * 1024), 2),
            "total_size_mb": round((upload_size + generated_size) / (1024 * 1024), 2)
        }
