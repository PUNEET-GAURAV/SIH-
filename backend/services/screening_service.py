"""Screening service — business logic for session and document management."""

import hashlib
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from backend.config import get_settings
from backend.models import (
    ScreeningSession, SessionStatus, Document, QualityStatus,
    Evidence, ScreeningAssessment, FaceVerification, AuditLog,
)
from backend.models.user import User


class ScreeningService:
    """Business logic for screening sessions."""

    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()

    def create_session(self, officer: User, notes: Optional[str] = None) -> ScreeningSession:
        """Create a new screening session."""
        session = ScreeningSession(
            officer_id=officer.id,
            status=SessionStatus.CREATED,
            mock_mode=self.settings.mock_mode,
            notes=notes,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session(self, session_id: str) -> Optional[ScreeningSession]:
        """Get a screening session by ID with all relationships loaded."""
        return (
            self.db.query(ScreeningSession)
            .options(
                joinedload(ScreeningSession.documents),
                joinedload(ScreeningSession.face_verification),
                joinedload(ScreeningSession.assessment),
                joinedload(ScreeningSession.evidence),
            )
            .filter(ScreeningSession.id == session_id)
            .first()
        )

    def list_sessions(self, officer_id: Optional[str] = None, limit: int = 50) -> list[ScreeningSession]:
        """List screening sessions, optionally filtered by officer."""
        query = self.db.query(ScreeningSession).order_by(ScreeningSession.created_at.desc())
        if officer_id:
            query = query.filter(ScreeningSession.officer_id == officer_id)
        return query.limit(limit).all()

    def save_document(
        self,
        session_id: str,
        file_content: bytes,
        filename: str,
        mime_type: str,
    ) -> Document:
        """Save an uploaded document to disk and create the DB record."""
        session = self.db.query(ScreeningSession).filter(ScreeningSession.id == session_id).first()
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Generate a unique file path
        upload_dir = self.settings.upload_path / session_id
        upload_dir.mkdir(parents=True, exist_ok=True)
        ext = Path(filename).suffix.lower()
        safe_name = f"{uuid.uuid4()}{ext}"
        file_path = upload_dir / safe_name

        # Write file
        with open(file_path, "wb") as f:
            f.write(file_content)

        # Compute hash
        file_hash = hashlib.sha256(file_content).hexdigest()

        doc = Document(
            session_id=session_id,
            file_path=str(file_path),
            file_hash=file_hash,
            original_filename=filename,
            mime_type=mime_type,
            file_size=len(file_content),
            quality_status=QualityStatus.PENDING,
        )
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def save_live_face(
        self,
        session_id: str,
        file_content: bytes,
        filename: str,
    ) -> str:
        """Save an uploaded live face photo to disk and update session."""
        session = self.db.query(ScreeningSession).filter(ScreeningSession.id == session_id).first()
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Generate a unique file path
        upload_dir = self.settings.upload_path / session_id
        upload_dir.mkdir(parents=True, exist_ok=True)
        ext = Path(filename).suffix.lower()
        safe_name = f"face_{uuid.uuid4()}{ext}"
        file_path = upload_dir / safe_name

        # Write file
        with open(file_path, "wb") as f:
            f.write(file_content)

        session.live_face_path = str(file_path)
        self.db.commit()
        return str(file_path)

    def update_session_status(self, session_id: str, status: SessionStatus, stage: Optional[str] = None):
        """Update session status and pipeline stage."""
        session = self.db.query(ScreeningSession).filter(ScreeningSession.id == session_id).first()
        if session:
            session.status = status
            if stage:
                session.pipeline_stage = stage
            session.updated_at = datetime.now(timezone.utc)
            self.db.commit()

    def get_session_evidence(self, session_id: str) -> list[Evidence]:
        """Get all evidence items for a session."""
        return (
            self.db.query(Evidence)
            .filter(Evidence.session_id == session_id)
            .order_by(Evidence.timestamp)
            .all()
        )

    def session_to_detail_dict(self, session: ScreeningSession) -> dict:
        """Convert a session with relationships to a detailed dict."""
        docs = []
        for doc in (session.documents or []):
            doc_dict = {
                "id": doc.id,
                "session_id": doc.session_id,
                "original_filename": doc.original_filename,
                "mime_type": doc.mime_type,
                "file_size": doc.file_size,
                "quality_status": doc.quality_status.value if doc.quality_status else None,
                "quality_details": doc.quality_details,
                "document_type": doc.document_type,
                "classification_confidence": doc.classification_confidence,
                "created_at": doc.created_at.isoformat() if doc.created_at else None,
                "ocr_fields": [
                    {
                        "field_name": f.field_name,
                        "field_value": f.field_value,
                        "confidence": f.confidence,
                        "bbox": f.bbox,
                        "source": f.source,
                        "is_mock": f.is_mock,
                    } for f in (doc.ocr_fields or [])
                ],
                "mrz_result": {
                    "raw_mrz": doc.mrz_result.raw_mrz,
                    "parsed_fields": doc.mrz_result.parsed_fields,
                    "checksum_results": doc.mrz_result.checksum_results,
                    "overall_status": doc.mrz_result.overall_status,
                    "is_mock": doc.mrz_result.is_mock,
                } if doc.mrz_result else None,
                "template_result": {
                    "template_id": doc.template_result.template_id,
                    "template_version": doc.template_result.template_version,
                    "alignment_score": doc.template_result.alignment_score,
                    "deviations": doc.template_result.deviations,
                    "status": doc.template_result.status,
                    "is_mock": doc.template_result.is_mock,
                } if doc.template_result else None,
                "forensic_results": [
                    {
                        "detector_type": f.detector_type,
                        "signal": f.signal,
                        "status": f.status,
                        "confidence": f.confidence,
                        "reliability": f.reliability,
                        "applicable": f.applicable,
                        "region": f.region,
                        "explanation": f.explanation,
                        "model_version": f.model_version,
                        "is_mock": f.is_mock,
                    } for f in (doc.forensic_results or [])
                ],
            }
            docs.append(doc_dict)

        face = None
        if session.face_verification:
            fv = session.face_verification
            face = {
                "similarity_score": fv.similarity_score,
                "face_quality": fv.face_quality,
                "pad_status": fv.pad_status,
                "identity_status": fv.identity_status.value if fv.identity_status else None,
                "explanation": fv.explanation,
                "is_mock": fv.is_mock,
            }

        assessment = None
        if session.assessment:
            a = session.assessment
            assessment = {
                "concern_level": a.concern_level.value if a.concern_level else None,
                "recommendation": a.recommendation.value if a.recommendation else None,
                "contradictions": a.contradictions,
                "summary": a.summary,
                "dimension_results": a.dimension_results,
                "is_mock": a.is_mock,
            }

        evidence_list = []
        for ev in (session.evidence or []):
            evidence_list.append({
                "id": ev.id,
                "signal": ev.signal,
                "status": ev.status,
                "value": ev.value,
                "confidence": ev.confidence,
                "reliability": ev.reliability,
                "applicable": ev.applicable,
                "source": ev.source,
                "region": ev.region,
                "explanation": ev.explanation,
                "model_version": ev.model_version,
                "is_mock": ev.is_mock,
                "timestamp": ev.timestamp.isoformat() if ev.timestamp else None,
            })

        return {
            "id": session.id,
            "officer_id": session.officer_id,
            "status": session.status.value if session.status else None,
            "pipeline_stage": session.pipeline_stage,
            "mock_mode": session.mock_mode,
            "notes": session.notes,
            "documents": docs,
            "face_verification": face,
            "assessment": assessment,
            "evidence": evidence_list,
            "created_at": session.created_at.isoformat() if session.created_at else None,
            "updated_at": session.updated_at.isoformat() if session.updated_at else None,
        }
