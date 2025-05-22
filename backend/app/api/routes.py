# backend/app/api/routes.py
import os
import uuid
import shutil
from typing import List, Dict, Optional
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core import config
from app.core.database import (
    save_document, 
    get_document, 
    get_all_documents,
    get_documents_by_ids
)
from app.services.document_processing import process_document
from app.services.query_engine import process_user_query

router = APIRouter()

# Request/Response Models
class QueryRequest(BaseModel):
    question: str
    document_ids: Optional[List[int]] = None

class DocumentResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    is_processed: bool
    processing_error: Optional[str] = None
    page_count: Optional[int] = None
    created_at: str
    updated_at: str

# Routes
@router.post("/documents/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """Upload a document and start processing it"""
    # Validate file type
    allowed_types = [".pdf"]
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Create unique filename
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(config.UPLOAD_DIR, unique_filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    # Save document to database
    doc_id = save_document(
        filename=unique_filename,
        original_filename=file.filename,
        file_path=file_path,
        file_type=file_extension,
        file_size=file_size
    )
    
    # Process document in background
    background_tasks.add_task(process_document, doc_id)
    
    return {"id": doc_id, "filename": file.filename, "status": "processing"}

@router.get("/documents")
async def get_documents():
    """Get all documents"""
    documents = get_all_documents()
    return {"documents": documents}

@router.get("/documents/{doc_id}")
async def get_document_by_id(doc_id: int):
    """Get a document by ID"""
    document = get_document(doc_id)
    
    if not document:
        raise HTTPException(
            status_code=404,
            detail=f"Document with ID {doc_id} not found"
        )
    
    return document

@router.post("/query")
async def query_documents(query_request: QueryRequest):
    """Query documents with a question"""
    if not query_request.question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )
    
    # Process the query
    result = process_user_query(
        question=query_request.question,
        doc_ids=query_request.document_ids
    )
    
    return result

@router.post("/documents/{doc_id}/process")
async def reprocess_document(
    doc_id: int,
    background_tasks: BackgroundTasks
):
    """Reprocess a document if needed"""
    document = get_document(doc_id)
    
    if not document:
        raise HTTPException(
            status_code=404,
            detail=f"Document with ID {doc_id} not found"
        )
    
    # Start processing in background
    background_tasks.add_task(process_document, doc_id)
    
    return {"id": doc_id, "status": "processing"}

@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: int):
    """Delete a document (not implemented yet)"""
    # This would need to:
    # 1. Delete the document file
    # 2. Delete any vector embeddings
    # 3. Remove from database
    # For now, just return a not implemented response
    return JSONResponse(
        status_code=501,
        content={"message": "Delete functionality not implemented yet"}
    )

@router.get("/status")
async def check_status():
    """API status check"""
    return {"status": "ok", "version": "1.0.0"}