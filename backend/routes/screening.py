"""Screening routes — thin request/response layer. Logic in services."""

import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session

from backend.database import get_db, SessionLocal
from backend.config import get_settings
from backend.schemas import APIResponse, ScreeningCreate
from backend.services.screening_service import ScreeningService
from backend.services.audit_service import AuditService
from backend.services.screening_orchestrator import ScreeningOrchestrator
from backend.utils.security import get_current_user
from backend.models.user import User
from backend.models.screening import SessionStatus

router = APIRouter(prefix="/screening", tags=["screening"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}


@router.post("/create")
def create_screening(
    payload: ScreeningCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new screening session."""
    service = ScreeningService(db)
    audit = AuditService(db)

    session = service.create_session(user, notes=payload.notes)
    audit.log_event(
        session_id=session.id,
        actor_id=user.id,
        event_type="session_created",
        payload={"notes": payload.notes},
    )

    return APIResponse(data={
        "id": session.id,
        "status": session.status.value,
        "mock_mode": session.mock_mode,
        "created_at": session.created_at.isoformat(),
    }).model_dump()


@router.post("/{session_id}/document")
async def upload_document(
    session_id: str,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a document image for screening."""
    settings = get_settings()
    service = ScreeningService(db)
    audit = AuditService(db)

    # Validate session exists
    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Validate file type
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {ext} not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Validate file size
    content = await file.read()
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds {settings.max_file_size_mb}MB limit",
        )

    doc = service.save_document(
        session_id=session_id,
        file_content=content,
        filename=file.filename or "document",
        mime_type=file.content_type or "image/jpeg",
    )

    audit.log_event(
        session_id=session_id,
        actor_id=user.id,
        event_type="document_uploaded",
        payload={"document_id": doc.id, "filename": file.filename, "file_hash": doc.file_hash},
    )

    return APIResponse(data={
        "document_id": doc.id,
        "filename": doc.original_filename,
        "file_size": doc.file_size,
        "file_hash": doc.file_hash,
        "quality_status": doc.quality_status.value,
    }).model_dump()


@router.post("/{session_id}/face")
async def upload_face(
    session_id: str,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a live face photo for screening."""
    settings = get_settings()
    service = ScreeningService(db)
    audit = AuditService(db)

    # Validate session exists
    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Validate file type
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {ext} not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Validate file size
    content = await file.read()
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds {settings.max_file_size_mb}MB limit",
        )

    face_path = service.save_live_face(
        session_id=session_id,
        file_content=content,
        filename=file.filename or "face",
    )

    audit.log_event(
        session_id=session_id,
        actor_id=user.id,
        event_type="face_uploaded",
        payload={"filename": file.filename},
    )

    return APIResponse(data={
        "face_path": face_path,
        "message": "Live face photo uploaded successfully",
    }).model_dump()


@router.get("/{session_id}")
def get_screening(
    session_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get full screening session details."""
    service = ScreeningService(db)
    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return APIResponse(data=service.session_to_detail_dict(session)).model_dump()


@router.get("/{session_id}/evidence")
def get_evidence(
    session_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all evidence items for a session."""
    service = ScreeningService(db)
    evidence = service.get_session_evidence(session_id)
    items = [{
        "id": e.id,
        "signal": e.signal,
        "status": e.status,
        "value": e.value,
        "confidence": e.confidence,
        "reliability": e.reliability,
        "applicable": e.applicable,
        "source": e.source,
        "region": e.region,
        "explanation": e.explanation,
        "model_version": e.model_version,
        "is_mock": e.is_mock,
        "timestamp": e.timestamp.isoformat() if e.timestamp else None,
    } for e in evidence]

    return APIResponse(data=items).model_dump()


@router.get("")
def list_screenings(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List screening sessions for the current officer."""
    service = ScreeningService(db)
    sessions = service.list_sessions(officer_id=user.id)
    return APIResponse(data=[{
        "id": s.id,
        "status": s.status.value,
        "pipeline_stage": s.pipeline_stage,
        "mock_mode": s.mock_mode,
        "created_at": s.created_at.isoformat() if s.created_at else None,
        "updated_at": s.updated_at.isoformat() if s.updated_at else None,
    } for s in sessions]).model_dump()


def _run_pipeline_background(session_id: str, actor_id: str):
    """Background task to run the screening pipeline."""
    db = SessionLocal()
    try:
        orchestrator = ScreeningOrchestrator(db)
        orchestrator.process_screening(session_id, actor_id)
    finally:
        db.close()


@router.post("/{session_id}/process")
def process_screening(
    session_id: str,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Run the full screening pipeline. Processing runs in background; poll GET /screening/{id} for status."""
    service = ScreeningService(db)
    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not session.documents:
        raise HTTPException(status_code=400, detail="No documents uploaded for this session")

    if session.status.value == "processing":
        raise HTTPException(status_code=400, detail="Session is already being processed")

    # Update to processing state immediately
    service.update_session_status(session_id, SessionStatus.PROCESSING, "queued")

    # Run pipeline in background
    background_tasks.add_task(_run_pipeline_background, session_id, user.id)

    return APIResponse(data={
        "session_id": session_id,
        "status": "processing",
        "message": "Pipeline started. Poll GET /screening/{session_id} for progress.",
    }).model_dump()
