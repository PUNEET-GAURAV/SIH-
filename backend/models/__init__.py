"""Models package — import all models so Alembic can discover them."""

from backend.models.base import Base, TimestampMixin
from backend.models.user import User, UserRole
from backend.models.screening import (
    ScreeningSession, SessionStatus, QualityStatus,
    Document, OCRField, MRZResult, TemplateResult,
    ForensicResult, BarcodeResult,
)
from backend.models.evidence import (
    FaceVerification, Evidence, ScreeningAssessment,
    AuditLog, OfficerDecision,
    ConcernLevel, Recommendation, DecisionAction, IdentityStatus,
)

__all__ = [
    "Base", "TimestampMixin",
    "User", "UserRole",
    "ScreeningSession", "SessionStatus", "QualityStatus",
    "Document", "OCRField", "MRZResult", "TemplateResult",
    "ForensicResult", "BarcodeResult",
    "FaceVerification", "Evidence", "ScreeningAssessment",
    "AuditLog", "OfficerDecision",
    "ConcernLevel", "Recommendation", "DecisionAction", "IdentityStatus",
]
