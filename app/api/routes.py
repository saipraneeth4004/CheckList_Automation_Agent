"""
FastAPI routes for the checklist automation API
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from fastapi.responses import FileResponse
from typing import List
from pathlib import Path
import shutil

from app.api.models import (
    ValidationResponse, ChatMessage, ChatResponse, GenerateDocumentRequest,
    DocumentGenerationResponse, SessionResponse, ChecklistInfoResponse,
    HealthResponse, UploadResponse, FileInfo, ChecklistItemResult,
    ValidationSummary, ValidationRequest
)
from app.api.dependencies import (
    get_session_manager_dependency, get_storage_manager_dependency,
    get_settings_dependency, validate_session
)
from app.core.session import SessionManager
from app.core.storage import StorageManager
from app.core.config import Settings
from app.validation.checklist_validator import ChecklistValidator
from app.validation.checklist_config import get_checklist_summary
from app.ai.gemini_client import GeminiClient
from app.ai.langchain_agent import ChecklistAgent
from app.ai.document_generator import DocumentGenerator

from datetime import datetime

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(settings: Settings = Depends(get_settings_dependency)):
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.now().isoformat()
    )


@router.post("/session/create", response_model=SessionResponse)
async def create_session(
    session_manager: SessionManager = Depends(get_session_manager_dependency),
    settings: Settings = Depends(get_settings_dependency)
):
    """Create a new session"""
    session_id = session_manager.create_session(settings.get_upload_path())
    session = session_manager.get_session(session_id)
    
    return SessionResponse(
        success=True,
        session_id=session_id,
        created_at=session.created_at.isoformat(),
        files_count=0,
        has_validation_results=False
    )


@router.get("/session/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager_dependency)
):
    """Get session information"""
    session = validate_session(session_id, session_manager)
    
    return SessionResponse(
        success=True,
        session_id=session_id,
        created_at=session.created_at.isoformat(),
        files_count=len(session.files),
        has_validation_results=session.validation_results is not None
    )


@router.post("/upload/{session_id}", response_model=UploadResponse)
async def upload_files(
    session_id: str,
    files: List[UploadFile] = File(...),
    session_manager: SessionManager = Depends(get_session_manager_dependency),
    storage_manager: StorageManager = Depends(get_storage_manager_dependency),
    settings: Settings = Depends(get_settings_dependency)
):
    """Upload files for validation"""
    session = validate_session(session_id, session_manager)
    
    uploaded_files = []
    allowed_extensions = settings.allowed_extensions_list
    max_size = settings.max_upload_size_mb * 1024 * 1024  # Convert to bytes
    
    for file in files:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_ext} not allowed. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Read file content
        content = await file.read()
        
        # Validate file size
        if len(content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File {file.filename} exceeds maximum size of {settings.max_upload_size_mb}MB"
            )
        
        # Save file
        file_path = storage_manager.save_uploaded_file(content, file.filename, session_id)
        session_manager.add_file(session_id, file.filename)
        
        # Get file info
        file_info = storage_manager.get_file_info(file_path)
        uploaded_files.append(FileInfo(**file_info))
    
    return UploadResponse(
        success=True,
        session_id=session_id,
        uploaded_files=uploaded_files,
        total_files=len(uploaded_files)
    )


@router.post("/validate/{session_id}", response_model=ValidationResponse)
async def validate_files(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager_dependency),
    storage_manager: StorageManager = Depends(get_storage_manager_dependency)
):
    """Validate uploaded files against checklist"""
    session = validate_session(session_id, session_manager)
    
    if not session.files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files uploaded for validation"
        )
    
    # Run validation
    validator = ChecklistValidator()
    folder_path = session.upload_folder
    
    validation_result = validator.validate_folder(folder_path)
    
    if not validation_result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=validation_result.get("error", "Validation failed")
        )
    
    # Store validation results in session
    session_manager.update_session(session_id, validation_results=validation_result)
    
    # Convert to response model
    checklist_results = [
        ChecklistItemResult(**result) 
        for result in validation_result["checklist_results"]
    ]
    
    summary = ValidationSummary(**validation_result["summary"])
    
    return ValidationResponse(
        success=True,
        session_id=session_id,
        folder_path=str(folder_path),
        total_files=validation_result["total_files"],
        file_names=validation_result["file_names"],
        checklist_results=checklist_results,
        summary=summary
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(
    chat_message: ChatMessage,
    session_manager: SessionManager = Depends(get_session_manager_dependency)
):
    """Chat with AI assistant"""
    session = validate_session(chat_message.session_id, session_manager)
    
    try:
        # Initialize AI client
        ai_client = GeminiClient()
        
        # Get context from session
        context = ""
        if session.validation_results:
            context = f"Current validation results: {session.validation_results.get('summary', {})}"
        
        if chat_message.context:
            context += f"\nAdditional context: {chat_message.context}"
        
        # Generate response
        response = ai_client.chat(chat_message.message, context if context else None)
        
        # Store in chat history
        session_manager.add_chat_message(chat_message.session_id, "user", chat_message.message)
        session_manager.add_chat_message(chat_message.session_id, "assistant", response)
        
        return ChatResponse(
            success=True,
            session_id=chat_message.session_id,
            message=response
        )
    
    except Exception as e:
        return ChatResponse(
            success=False,
            session_id=chat_message.session_id,
            message="",
            error=str(e)
        )


@router.post("/generate-document", response_model=DocumentGenerationResponse)
async def generate_document(
    request: GenerateDocumentRequest,
    session_manager: SessionManager = Depends(get_session_manager_dependency),
    settings: Settings = Depends(get_settings_dependency)
):
    """Generate a missing document"""
    session = validate_session(request.session_id, session_manager)
    
    try:
        # Initialize document generator
        output_dir = settings.get_generated_path() / request.session_id
        doc_generator = DocumentGenerator(output_dir)
        
        # Generate document based on type
        if request.checklist_item_id == "bank_reconciliation":
            file_path = doc_generator.generate_bank_reconciliation(
                request.user_data, 
                request.filename
            )
        elif request.checklist_item_id == "ar_aging":
            file_path = doc_generator.generate_ar_aging(
                request.user_data,
                request.filename
            )
        elif request.checklist_item_id == "ap_aging":
            file_path = doc_generator.generate_ap_aging(
                request.user_data,
                request.filename
            )
        elif request.checklist_item_id == "accruals":
            file_path = doc_generator.generate_accrual_journal(
                request.user_data,
                request.filename
            )
        elif request.checklist_item_id == "expense_analysis":
            file_path = doc_generator.generate_expense_analysis(
                request.user_data,
                request.filename
            )
        elif request.checklist_item_id == "prepayments":
            file_path = doc_generator.generate_prepayments_schedule(
                request.user_data,
                request.filename
            )
        elif request.checklist_item_id == "revenue_recognition":
            file_path = doc_generator.generate_revenue_schedule(
                request.user_data,
                request.filename
            )
        elif request.checklist_item_id == "fixed_assets":
            file_path = doc_generator.generate_fixed_assets_register(
                request.user_data,
                request.filename
            )
        elif request.checklist_item_id == "intercompany":
            file_path = doc_generator.generate_intercompany_reconciliation(
                request.user_data,
                request.filename
            )
        else:
            # Generic template with better defaults
            columns = request.user_data.get("columns", ["Date", "Description", "Amount", "Category", "Notes"])
            file_path = doc_generator.generate_generic_template(
                request.checklist_item_id,
                columns,
                request.filename
            )
        
        # Add to session
        session_manager.add_generated_document(request.session_id, file_path.name)
        
        return DocumentGenerationResponse(
            success=True,
            session_id=request.session_id,
            filename=file_path.name,
            file_path=str(file_path),
            download_url=f"/download/{request.session_id}/{file_path.name}"
        )
    
    except Exception as e:
        return DocumentGenerationResponse(
            success=False,
            session_id=request.session_id,
            filename="",
            error=str(e)
        )


@router.get("/download/{session_id}/{filename}")
async def download_file(
    session_id: str,
    filename: str,
    session_manager: SessionManager = Depends(get_session_manager_dependency),
    settings: Settings = Depends(get_settings_dependency)
):
    """Download a generated file"""
    session = validate_session(session_id, session_manager)
    
    file_path = settings.get_generated_path() / session_id / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {filename} not found"
        )
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.get("/checklist/info", response_model=ChecklistInfoResponse)
async def get_checklist_info():
    """Get information about the checklist"""
    summary = get_checklist_summary()
    return ChecklistInfoResponse(**summary)


@router.get("/checklist/analyze/{session_id}")
async def analyze_checklist(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager_dependency)
):
    """Get AI analysis of checklist results"""
    session = validate_session(session_id, session_manager)
    
    if not session.validation_results:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No validation results available. Please validate files first."
        )
    
    try:
        ai_client = GeminiClient()
        analysis = ai_client.analyze_checklist_results(session.validation_results)
        
        return {
            "success": True,
            "session_id": session_id,
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating analysis: {str(e)}"
        )


@router.get("/checklist/guidance/{session_id}/{item_id}")
async def get_item_guidance(
    session_id: str,
    item_id: str,
    session_manager: SessionManager = Depends(get_session_manager_dependency)
):
    """Get guidance for completing a specific checklist item"""
    session = validate_session(session_id, session_manager)
    
    if not session.validation_results:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No validation results available. Please validate files first."
        )
    
    # Find the checklist item result
    checklist_results = session.validation_results.get("checklist_results", [])
    item_result = next((item for item in checklist_results if item["id"] == item_id), None)
    
    if not item_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Checklist item {item_id} not found"
        )
    
    try:
        ai_client = GeminiClient()
        
        # Get guidance
        guidance = ai_client.generate_completion_guidance(item_result)
        
        # Get follow-up questions
        questions = ai_client.ask_followup_questions(item_result)
        
        return {
            "success": True,
            "session_id": session_id,
            "item_id": item_id,
            "item_name": item_result["name"],
            "status": item_result["status"],
            "guidance": guidance,
            "questions": questions,
            "issues": item_result.get("issues", []),
            "recommendations": item_result.get("recommendations", [])
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating guidance: {str(e)}"
        )
