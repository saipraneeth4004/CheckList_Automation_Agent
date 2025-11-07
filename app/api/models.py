"""
Pydantic models for API request/response schemas
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


# Request Models
class ChatMessage(BaseModel):
    """Chat message model"""
    message: str = Field(..., description="User message")
    session_id: str = Field(..., description="Session ID")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class GenerateDocumentRequest(BaseModel):
    """Request to generate a document"""
    session_id: str = Field(..., description="Session ID")
    checklist_item_id: str = Field(..., description="Checklist item ID")
    user_data: Dict[str, Any] = Field(default_factory=dict, description="User-provided data")
    filename: Optional[str] = Field(None, description="Custom filename")


class ValidationRequest(BaseModel):
    """Request to validate uploaded files"""
    session_id: str = Field(..., description="Session ID")


# Response Models
class FileInfo(BaseModel):
    """File information model"""
    filename: str
    size: int
    size_mb: float
    extension: str
    uploaded_at: Optional[str] = None


class ChecklistItemResult(BaseModel):
    """Result for a single checklist item"""
    id: str
    name: str
    description: str
    status: str
    confidence: float
    matched_files: List[str]
    issues: List[str]
    recommendations: List[str]
    validation_details: Dict[str, Any]


class ValidationSummary(BaseModel):
    """Summary of validation results"""
    total_items: int
    complete: int
    incomplete: int
    missing: int
    completion_rate: float
    overall_status: str
    high_priority_complete: int
    high_priority_total: int


class ValidationResponse(BaseModel):
    """Complete validation response"""
    success: bool
    session_id: str
    folder_path: Optional[str] = None
    total_files: int
    file_names: List[str]
    checklist_results: List[ChecklistItemResult]
    summary: ValidationSummary
    error: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model"""
    success: bool
    session_id: str
    message: str
    suggestions: Optional[List[str]] = None
    error: Optional[str] = None


class DocumentGenerationResponse(BaseModel):
    """Response for document generation"""
    success: bool
    session_id: str
    filename: str
    file_path: Optional[str] = None
    download_url: Optional[str] = None
    error: Optional[str] = None


class SessionResponse(BaseModel):
    """Session information response"""
    success: bool
    session_id: str
    created_at: str
    files_count: int
    has_validation_results: bool


class ChecklistInfoResponse(BaseModel):
    """Checklist information response"""
    total_items: int
    high_priority: int
    medium_priority: int
    low_priority: int
    items: List[Dict[str, Any]]


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: str


class UploadResponse(BaseModel):
    """File upload response"""
    success: bool
    session_id: str
    uploaded_files: List[FileInfo]
    total_files: int
    error: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response"""
    success: bool = False
    error: str
    detail: Optional[str] = None
