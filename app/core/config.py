"""
Core configuration management for the application
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Configuration
    google_api_key: str
    
    # Application Info
    app_name: str = "Monthly Close Checklist Automation Agent"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Server Configuration
    fastapi_host: str = "0.0.0.0"
    fastapi_port: int = 8000
    streamlit_port: int = 8501
    
    # File Upload Settings
    max_upload_size_mb: int = 100
    allowed_extensions: str = ".xlsx,.xls,.csv,.pdf,.txt"
    
    # Storage Paths
    upload_dir: str = "./uploads"
    generated_dir: str = "./generated"
    sample_data_dir: str = "./sample_data"
    
    # Session Settings
    session_timeout_minutes: int = 60
    
    # AI Model Settings
    gemini_model: str = "gemini-1.5-flash"
    temperature: float = 0.7
    max_tokens: int = 2048
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """Return allowed extensions as a list"""
        return [ext.strip() for ext in self.allowed_extensions.split(",")]
    
    def get_upload_path(self) -> Path:
        """Get and create upload directory"""
        path = Path(self.upload_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def get_generated_path(self) -> Path:
        """Get and create generated directory"""
        path = Path(self.generated_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def get_sample_data_path(self) -> Path:
        """Get sample data directory"""
        return Path(self.sample_data_dir)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
