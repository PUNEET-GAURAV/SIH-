"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field
import uuid


# === API Envelope (Build Spec §13) ===

class APIResponse(BaseModel):
    """Standard API response envelope."""
    success: bool = True
    data: Any = None
    error: Optional[dict] = None
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class APIError(BaseModel):
    """Error detail within the envelope."""
    code: str
    message: str
    retryable: bool = False


# === Auth Schemas ===

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8)
    full_name: str = Field(default="", max_length=255)
    role: str = Field(default="officer")


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# === Screening Schemas ===

class ScreeningCreate(BaseModel):
    notes: Optional[str] = None


class ScreeningResponse(BaseModel):
    id: str
    officer_id: str
    status: str
    pipeline_stage: Optional[str] = None
    mock_mode: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ScreeningDetailResponse(BaseModel):
    id: str
    officer_id: str
    status: str
    pipeline_stage: Optional[str] = None
    mock_mode: bool
    notes: Optional[str] = None
    documents: list[dict] = []
    face_verification: Optional[dict] = None
    assessment: Optional[dict] = None
    evidence: list[dict] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# === Evidence Schemas (Solution Spec §13) ===

class EvidenceItem(BaseModel):
    signal: str
    status: str
    value: Optional[str] = None
    confidence: Optional[float] = None
    reliability: Optional[float] = None
    applicable: bool = True
    source: Optional[str] = None
    region: Optional[list] = None
    explanation: Optional[str] = None
    model_version: Optional[str] = None
    preprocessing_version: Optional[str] = None
    is_mock: bool = False
    timestamp: Optional[datetime] = None


class AssessmentResponse(BaseModel):
    concern_level: Optional[str] = None
    recommendation: Optional[str] = None
    contradictions: Optional[list] = None
    summary: Optional[str] = None
    dimension_results: Optional[dict] = None
    is_mock: bool = False


# === Document Schemas ===

class DocumentResponse(BaseModel):
    id: str
    session_id: str
    original_filename: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    quality_status: str
    quality_details: Optional[dict] = None
    document_type: Optional[str] = None
    classification_confidence: Optional[float] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# === Audit Schemas ===

class AuditLogResponse(BaseModel):
    id: str
    session_id: str
    actor_id: str
    event_type: str
    payload_hash: Optional[str] = None
    previous_hash: Optional[str] = None
    entry_hash: str
    timestamp: datetime

    model_config = {"from_attributes": True}


class AuditVerifyResponse(BaseModel):
    valid: bool
    total_entries: int
    first_broken_link: Optional[int] = None
    message: str


# === Officer Decision ===

class OfficerDecisionCreate(BaseModel):
    session_id: str
    decision: str  # clear, secondary_inspection, escalate, request_recapture
    notes: Optional[str] = None
