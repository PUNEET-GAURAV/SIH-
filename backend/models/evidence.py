"""Evidence, assessment, face verification, audit, and officer decision models."""

import enum
from datetime import datetime, timezone

from sqlalchemy import Column, String, Float, Boolean, ForeignKey, Text, Enum, JSON, DateTime
from sqlalchemy.orm import relationship

from backend.models.base import Base, TimestampMixin, generate_uuid, utc_now


class ConcernLevel(str, enum.Enum):
    LOW_CONCERN = "low_concern"
    REVIEW_REQUIRED = "review_required"
    HIGH_CONCERN = "high_concern"


class Recommendation(str, enum.Enum):
    CLEAR = "clear"
    REQUEST_RECAPTURE = "request_recapture"
    SECONDARY_INSPECTION = "secondary_inspection"
    ESCALATE = "escalate"


class DecisionAction(str, enum.Enum):
    CLEAR = "clear"
    SECONDARY_INSPECTION = "secondary_inspection"
    ESCALATE = "escalate"
    REQUEST_RECAPTURE = "request_recapture"


class IdentityStatus(str, enum.Enum):
    MATCH = "match"
    UNCERTAIN = "uncertain"
    MISMATCH = "mismatch"
    NOT_AVAILABLE = "not_available"


class FaceVerification(Base):
    __tablename__ = "face_verifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("screening_sessions.id"), nullable=False, unique=True, index=True)
    similarity_score = Column(Float, nullable=True)
    face_quality = Column(JSON, nullable=True)
    pad_status = Column(String(20), nullable=True)
    pad_details = Column(JSON, nullable=True)
    identity_status = Column(Enum(IdentityStatus), nullable=True, default=IdentityStatus.NOT_AVAILABLE)
    explanation = Column(Text, nullable=True)
    model_version = Column(String(50), nullable=True)
    is_mock = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    session = relationship("ScreeningSession", back_populates="face_verification")


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("screening_sessions.id"), nullable=False, index=True)
    signal = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)
    value = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    reliability = Column(Float, nullable=True)
    applicable = Column(Boolean, default=True)
    source = Column(String(50), nullable=True)
    region = Column(JSON, nullable=True)
    explanation = Column(Text, nullable=True)
    model_version = Column(String(50), nullable=True)
    preprocessing_version = Column(String(50), nullable=True)
    is_mock = Column(Boolean, default=False)
    timestamp = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    session = relationship("ScreeningSession", back_populates="evidence")


class ScreeningAssessment(Base):
    __tablename__ = "screening_assessments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("screening_sessions.id"), nullable=False, unique=True, index=True)
    concern_level = Column(Enum(ConcernLevel), nullable=True)
    recommendation = Column(Enum(Recommendation), nullable=True)
    contradictions = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)
    fusion_details = Column(JSON, nullable=True)
    dimension_results = Column(JSON, nullable=True)  # per-dimension results
    is_mock = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    session = relationship("ScreeningSession", back_populates="assessment")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("screening_sessions.id"), nullable=False, index=True)
    actor_id = Column(String(36), nullable=False)
    event_type = Column(String(50), nullable=False)
    payload_hash = Column(String(64), nullable=True)
    previous_hash = Column(String(64), nullable=True)
    entry_hash = Column(String(64), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    session = relationship("ScreeningSession", back_populates="audit_logs")


class OfficerDecision(Base):
    __tablename__ = "officer_decisions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("screening_sessions.id"), nullable=False, unique=True, index=True)
    officer_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    decision = Column(Enum(DecisionAction), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    session = relationship("ScreeningSession", back_populates="officer_decision")
