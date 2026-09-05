"""AI adapter interfaces — Build Spec §4.

Business logic never imports a concrete model library directly.
Each interface has: mock implementation, real implementation (when available),
and optionally an ONNX implementation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional
import numpy as np


# === Shared Result Types ===

@dataclass
class SignalResult:
    """Base evidence signal matching Solution Spec §13."""
    signal: str
    status: str  # pass, fail, uncertain, not_applicable, unavailable
    value: Optional[str] = None
    confidence: Optional[float] = None
    reliability: Optional[float] = None
    applicable: bool = True
    source: Optional[str] = None
    region: Optional[list] = None  # [x, y, w, h]
    explanation: Optional[str] = None
    model_version: Optional[str] = None
    preprocessing_version: Optional[str] = None
    is_mock: bool = False
    details: Optional[dict] = None


@dataclass
class QualityResult:
    """Result from the capture quality gate."""
    status: str  # accept, process_with_degraded_confidence, recapture_required
    blur_score: float = 0.0
    glare_ratio: float = 0.0
    resolution: tuple = (0, 0)
    corner_count: int = 0
    perspective_distortion: float = 0.0
    document_area_ratio: float = 0.0
    issues: list = field(default_factory=list)
    explanation: str = ""
    is_mock: bool = False


@dataclass
class ClassificationResult:
    """Result from document classification."""
    document_type: str  # passport_td3, id_card_td1, unknown
    confidence: float = 0.0
    is_unknown_mode: bool = False
    model_version: str = ""
    is_mock: bool = False


@dataclass
class OCRResult:
    """Result from OCR extraction."""
    fields: list = field(default_factory=list)  # list of {field_name, value, confidence, bbox}
    raw_text: str = ""
    status: str = "success"  # success, uncertain, unavailable
    model_version: str = ""
    is_mock: bool = False


@dataclass
class MRZResult:
    """Result from MRZ parsing and validation."""
    raw_mrz: str = ""
    document_type: str = ""
    country_code: str = ""
    surname: str = ""
    given_names: str = ""
    document_number: str = ""
    nationality: str = ""
    date_of_birth: str = ""
    sex: str = ""
    expiry_date: str = ""
    optional_data: str = ""
    checksum_results: dict = field(default_factory=dict)
    overall_status: str = "uncertain"  # pass, review, fail, uncertain, unavailable
    is_valid: bool = False
    issues: list = field(default_factory=list)
    is_mock: bool = False


@dataclass
class TemplateMatchResult:
    """Result from template/structural validation."""
    template_id: Optional[str] = None
    template_version: Optional[str] = None
    alignment_score: float = 0.0
    status: str = "unknown"  # conforming, deviation, unknown
    deviations: list = field(default_factory=list)
    is_mock: bool = False


@dataclass
class ForensicSignal:
    """A single forensic detection signal."""
    detector_type: str
    signal: str
    status: str  # low, medium, high, uncertain, unavailable
    confidence: float = 0.0
    reliability: float = 0.0
    applicable: bool = True
    region: Optional[list] = None
    explanation: str = ""
    heatmap: Optional[np.ndarray] = None
    model_version: str = ""
    details: Optional[dict] = None
    is_mock: bool = False


@dataclass
class FaceResult:
    """Result from face verification."""
    similarity_score: float = 0.0
    identity_status: str = "not_available"  # match, uncertain, mismatch, not_available
    face_quality: dict = field(default_factory=dict)
    explanation: str = ""
    model_version: str = ""
    is_mock: bool = False


@dataclass
class PADResult:
    """Result from Presentation Attack Detection."""
    status: str = "uncertain"  # genuine, attack_detected, uncertain, unavailable
    confidence: float = 0.0
    attack_type: Optional[str] = None
    details: dict = field(default_factory=dict)
    explanation: str = ""
    tested_attacks: list = field(default_factory=list)
    model_version: str = ""
    is_mock: bool = False


# === Adapter Interfaces ===

class DocumentClassifier(ABC):
    """Classifies document type from an image."""

    @abstractmethod
    def classify(self, image: np.ndarray) -> ClassificationResult:
        """Classify a document image.

        Args:
            image: BGR image as numpy array

        Returns:
            ClassificationResult with type and confidence
        """
        pass


class OCRProvider(ABC):
    """Extracts text and fields from a document image."""

    @abstractmethod
    def extract(self, image: np.ndarray) -> OCRResult:
        """Extract text fields from a document image.

        Args:
            image: BGR image as numpy array

        Returns:
            OCRResult with extracted fields
        """
        pass


class MRZParser(ABC):
    """Parses and validates Machine Readable Zone text.

    Note: MRZ parsing is pure deterministic Python — no ML.
    The ABC is kept for interface consistency but no mock is needed;
    the real parser is always available.
    """

    @abstractmethod
    def parse(self, mrz_text: str) -> MRZResult:
        """Parse MRZ text and validate checksums.

        Args:
            mrz_text: Raw MRZ string (1-3 lines)

        Returns:
            MRZResult with parsed fields and checksum validation
        """
        pass


class ForensicDetector(ABC):
    """Base interface for all forensic detectors."""

    @abstractmethod
    def analyze(self, image: np.ndarray, context: Optional[dict] = None) -> list[ForensicSignal]:
        """Analyze an image for manipulation evidence.

        Args:
            image: BGR image as numpy array
            context: Optional context (template info, quality info, etc.)

        Returns:
            List of ForensicSignal evidence items
        """
        pass

    @property
    @abstractmethod
    def detector_type(self) -> str:
        """Unique identifier for this detector type."""
        pass


class FaceVerifier(ABC):
    """Compares a live face against a document photo."""

    @abstractmethod
    def compare(self, live_image: np.ndarray, doc_photo: np.ndarray) -> FaceResult:
        """Compare live face image to document photo.

        Args:
            live_image: BGR image of live face
            doc_photo: BGR image of document photo

        Returns:
            FaceResult with similarity and identity status
        """
        pass


class PADDetector(ABC):
    """Presentation Attack Detection."""

    @abstractmethod
    def assess(self, frames: list[np.ndarray]) -> PADResult:
        """Assess presentation attack from one or more frames.

        Args:
            frames: List of BGR images (single frame or video frames)

        Returns:
            PADResult with attack assessment
        """
        pass
