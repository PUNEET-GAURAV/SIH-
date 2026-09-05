"""AI common package."""
from ai.common.interfaces import (
    SignalResult, QualityResult, ClassificationResult,
    OCRResult, MRZResult, TemplateMatchResult, ForensicSignal,
    FaceResult, PADResult,
    DocumentClassifier, OCRProvider, MRZParser,
    ForensicDetector, FaceVerifier, PADDetector,
)

__all__ = [
    "SignalResult", "QualityResult", "ClassificationResult",
    "OCRResult", "MRZResult", "TemplateMatchResult", "ForensicSignal",
    "FaceResult", "PADResult",
    "DocumentClassifier", "OCRProvider", "MRZParser",
    "ForensicDetector", "FaceVerifier", "PADDetector",
]
