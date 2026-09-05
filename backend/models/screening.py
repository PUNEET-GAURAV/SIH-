"""Screening session and document models — core entities."""

import enum

from sqlalchemy import Column, String, Float, Integer, Boolean, ForeignKey, Text, Enum, JSON
from sqlalchemy.orm import relationship

from backend.models.base import Base, TimestampMixin, generate_uuid


class SessionStatus(str, enum.Enum):
    CREATED = "created"
    PROCESSING = "processing"
    QUALITY_FAILED = "quality_failed"
    COMPLETED = "completed"
    ERROR = "error"


class QualityStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPT = "accept"
    DEGRADED = "process_with_degraded_confidence"
    RECAPTURE_REQUIRED = "recapture_required"


class ScreeningSession(Base, TimestampMixin):
    __tablename__ = "screening_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    officer_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    status = Column(Enum(SessionStatus), nullable=False, default=SessionStatus.CREATED)
    pipeline_stage = Column(String(50), nullable=True)
    mock_mode = Column(Boolean, nullable=False, default=False)
    notes = Column(Text, nullable=True)
    live_face_path = Column(String(500), nullable=True)

    # Relationships
    documents = relationship("Document", back_populates="session", cascade="all, delete-orphan")
    face_verification = relationship("FaceVerification", back_populates="session", uselist=False, cascade="all, delete-orphan")
    evidence = relationship("Evidence", back_populates="session", cascade="all, delete-orphan")
    assessment = relationship("ScreeningAssessment", back_populates="session", uselist=False, cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="session", cascade="all, delete-orphan")
    officer_decision = relationship("OfficerDecision", back_populates="session", uselist=False, cascade="all, delete-orphan")


class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("screening_sessions.id"), nullable=False, index=True)

    # File info
    file_path = Column(String(500), nullable=True)
    file_hash = Column(String(64), nullable=True)
    original_filename = Column(String(255), nullable=True)
    mime_type = Column(String(100), nullable=True)
    file_size = Column(Integer, nullable=True)

    # Quality assessment
    quality_status = Column(Enum(QualityStatus), nullable=False, default=QualityStatus.PENDING)
    quality_details = Column(JSON, nullable=True)

    # Classification
    document_type = Column(String(50), nullable=True)  # passport_td3, id_card_td1, unknown
    classification_confidence = Column(Float, nullable=True)

    # Preprocessed
    preprocessed_path = Column(String(500), nullable=True)

    # Relationships
    session = relationship("ScreeningSession", back_populates="documents")
    ocr_fields = relationship("OCRField", back_populates="document", cascade="all, delete-orphan")
    mrz_result = relationship("MRZResult", back_populates="document", uselist=False, cascade="all, delete-orphan")
    template_result = relationship("TemplateResult", back_populates="document", uselist=False, cascade="all, delete-orphan")
    forensic_results = relationship("ForensicResult", back_populates="document", cascade="all, delete-orphan")
    barcode_result = relationship("BarcodeResult", back_populates="document", uselist=False, cascade="all, delete-orphan")


class OCRField(Base):
    __tablename__ = "ocr_fields"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, index=True)
    field_name = Column(String(100), nullable=False)
    field_value = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    bbox = Column(JSON, nullable=True)  # [x, y, w, h]
    source = Column(String(50), nullable=True)  # ocr, mrz, barcode
    is_mock = Column(Boolean, default=False)

    document = relationship("Document", back_populates="ocr_fields")


class MRZResult(Base):
    __tablename__ = "mrz_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, unique=True, index=True)
    raw_mrz = Column(Text, nullable=True)
    parsed_fields = Column(JSON, nullable=True)
    checksum_results = Column(JSON, nullable=True)
    overall_status = Column(String(20), nullable=True)  # PASS, REVIEW, FAIL
    is_mock = Column(Boolean, default=False)

    document = relationship("Document", back_populates="mrz_result")


class TemplateResult(Base):
    __tablename__ = "template_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, unique=True, index=True)
    template_id = Column(String(50), nullable=True)
    template_version = Column(String(20), nullable=True)
    alignment_score = Column(Float, nullable=True)
    deviations = Column(JSON, nullable=True)
    status = Column(String(20), nullable=True)  # CONFORMING, DEVIATION, UNKNOWN
    is_mock = Column(Boolean, default=False)

    document = relationship("Document", back_populates="template_result")


class ForensicResult(Base):
    __tablename__ = "forensic_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, index=True)
    detector_type = Column(String(50), nullable=False)  # copy_move, manipulation_cnn, geometric
    signal = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=True)
    reliability = Column(Float, nullable=True)
    applicable = Column(Boolean, default=True)
    region = Column(JSON, nullable=True)  # [x, y, w, h]
    explanation = Column(Text, nullable=True)
    details = Column(JSON, nullable=True)
    model_version = Column(String(50), nullable=True)
    is_mock = Column(Boolean, default=False)

    document = relationship("Document", back_populates="forensic_results")


class BarcodeResult(Base):
    __tablename__ = "barcode_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, unique=True, index=True)
    barcode_type = Column(String(50), nullable=True)
    decoded_data = Column(JSON, nullable=True)
    status = Column(String(20), nullable=True)  # DECODED, NOT_APPLICABLE, UNCERTAIN
    is_mock = Column(Boolean, default=False)

    document = relationship("Document", back_populates="barcode_result")
