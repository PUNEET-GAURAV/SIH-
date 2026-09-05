"""Mock adapters for all AI modules — deterministic, labeled is_mock=True.

Supports 6 deterministic demo scenarios per Solution Spec §26 & Build Spec §11:
1. genuine
2. altered_dob
3. expired
4. wrong_face
5. poor_capture
6. unknown_document
"""

import logging
import numpy as np
from typing import Optional, List

from ai.common.interfaces import (
    DocumentClassifier, ClassificationResult,
    OCRProvider, OCRResult,
    ForensicDetector, ForensicSignal,
    FaceVerifier, FaceResult,
    PADDetector, PADResult,
    QualityResult, TemplateMatchResult, MRZResult,
)

logger = logging.getLogger("docshield.mocks")


class MockAdapterSuite:
    """Provides mock responses for all pipeline stages given a scenario name."""

    def __init__(self, scenario: str = "genuine"):
        self.scenario = scenario.lower()

    def get_quality(self) -> QualityResult:
        if self.scenario == "poor_capture":
            return QualityResult(
                status="recapture_required",
                blur_score=28.5,
                glare_ratio=0.18,
                resolution=(800, 600),
                corner_count=2,
                perspective_distortion=0.35,
                issues=[
                    "High motion blur detected (Laplacian variance 28.5 < min 100.0)",
                    "Severe specular glare detected (18.0% of document area)",
                    "Only 2 corners detected (document boundary incomplete)",
                ],
                explanation="Quality gate failed: document image is blurred and has specular glare covering critical fields.",
                is_mock=True,
            )
        else:
            return QualityResult(
                status="accept",
                blur_score=420.0,
                glare_ratio=0.01,
                resolution=(1920, 1080),
                corner_count=4,
                perspective_distortion=0.02,
                document_area_ratio=0.82,
                issues=[],
                explanation="Quality gate passed: sharpness, lighting, and geometric resolution meet all thresholds.",
                is_mock=True,
            )

    def get_classification(self) -> ClassificationResult:
        if self.scenario == "unknown_document":
            return ClassificationResult(
                document_type="unknown",
                confidence=0.15,
                is_unknown_mode=True,
                model_version="mock_classifier_v1",
                is_mock=True,
            )
        elif self.scenario == "expired":
            return ClassificationResult(
                document_type="id_card_td1",
                confidence=0.96,
                is_unknown_mode=False,
                model_version="mock_classifier_v1",
                is_mock=True,
            )
        else:
            return ClassificationResult(
                document_type="passport_td3",
                confidence=0.98,
                is_unknown_mode=False,
                model_version="mock_classifier_v1",
                is_mock=True,
            )

    def get_mrz(self) -> MRZResult:
        if self.scenario == "unknown_document":
            return MRZResult(
                raw_mrz="",
                overall_status="unavailable",
                is_valid=False,
                issues=["No MRZ zone detected on document."],
                is_mock=True,
            )
        elif self.scenario == "expired":
            return MRZResult(
                raw_mrz="I1UTOD00000000<0<<<<<<<<<<<<<<<\n8805125M2101150UTO<<<<<<<<<<<4\nDOE<<JOHN<<<<<<<<<<<<<<<<<<<<<<",
                document_type="I",
                country_code="UTO",
                surname="DOE",
                given_names="JOHN",
                document_number="D00000000",
                nationality="UTO",
                date_of_birth="1988-05-12",
                sex="M",
                expiry_date="2021-01-15",
                checksum_results={
                    "doc_number": {"valid": True},
                    "dob": {"valid": True},
                    "expiry": {"valid": True},
                    "composite": {"valid": True},
                },
                overall_status="review",
                is_valid=True,
                issues=["Document is expired (expiry: 2021-01-15)"],
                is_mock=True,
            )
        else:
            # Genuine, altered_dob, wrong_face
            return MRZResult(
                raw_mrz="P<UTODOE<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\nP123456784UTO8805125M3005123<<<<<<<<<<<<<<02",
                document_type="P",
                country_code="UTO",
                surname="DOE",
                given_names="JOHN",
                document_number="P12345678",
                nationality="UTO",
                date_of_birth="1988-05-12",
                sex="M",
                expiry_date="2030-05-12",
                checksum_results={
                    "doc_number": {"valid": True},
                    "dob": {"valid": True},
                    "expiry": {"valid": True},
                    "composite": {"valid": True},
                },
                overall_status="pass",
                is_valid=True,
                issues=[],
                is_mock=True,
            )

    def get_ocr(self) -> OCRResult:
        if self.scenario == "unknown_document":
            return OCRResult(
                fields=[
                    {"field_name": "raw_header", "value": "MEMBERSHIP CARD", "confidence": 0.85, "bbox": [100, 40, 200, 30]},
                ],
                raw_text="MEMBERSHIP CARD\nID: 998877\nISSUED: 2023",
                status="success",
                model_version="mock_ocr_v1",
                is_mock=True,
            )
        elif self.scenario == "altered_dob":
            return OCRResult(
                fields=[
                    {"field_name": "surname", "value": "DOE", "confidence": 0.96, "bbox": [120, 60, 100, 25]},
                    {"field_name": "given_names", "value": "JOHN", "confidence": 0.95, "bbox": [120, 90, 100, 25]},
                    {"field_name": "document_number", "value": "P12345678", "confidence": 0.94, "bbox": [120, 120, 150, 25]},
                    {"field_name": "date_of_birth", "value": "1995-05-12", "confidence": 0.89, "bbox": [120, 150, 120, 25]}, # Mismatch with MRZ 1988-05-12!
                    {"field_name": "expiry_date", "value": "2030-05-12", "confidence": 0.93, "bbox": [120, 180, 120, 25]},
                ],
                raw_text="PASSPORT\nSurname: DOE\nGiven Names: JOHN\nDoc No: P12345678\nDOB: 1995-05-12\nExpiry: 2030-05-12",
                status="success",
                model_version="mock_ocr_v1",
                is_mock=True,
            )
        elif self.scenario == "expired":
            return OCRResult(
                fields=[
                    {"field_name": "surname", "value": "DOE", "confidence": 0.96, "bbox": [120, 60, 100, 25]},
                    {"field_name": "given_names", "value": "JOHN", "confidence": 0.95, "bbox": [120, 90, 100, 25]},
                    {"field_name": "document_number", "value": "D00000000", "confidence": 0.94, "bbox": [120, 120, 150, 25]},
                    {"field_name": "date_of_birth", "value": "1988-05-12", "confidence": 0.91, "bbox": [120, 150, 120, 25]},
                    {"field_name": "expiry_date", "value": "2021-01-15", "confidence": 0.92, "bbox": [120, 180, 120, 25]},
                ],
                raw_text="NATIONAL ID\nSurname: DOE\nGiven Names: JOHN\nDoc No: D00000000\nDOB: 1988-05-12\nExpiry: 2021-01-15",
                status="success",
                model_version="mock_ocr_v1",
                is_mock=True,
            )
        else:
            return OCRResult(
                fields=[
                    {"field_name": "surname", "value": "DOE", "confidence": 0.96, "bbox": [120, 60, 100, 25]},
                    {"field_name": "given_names", "value": "JOHN", "confidence": 0.95, "bbox": [120, 90, 100, 25]},
                    {"field_name": "document_number", "value": "P12345678", "confidence": 0.94, "bbox": [120, 120, 150, 25]},
                    {"field_name": "date_of_birth", "value": "1988-05-12", "confidence": 0.93, "bbox": [120, 150, 120, 25]},
                    {"field_name": "expiry_date", "value": "2030-05-12", "confidence": 0.93, "bbox": [120, 180, 120, 25]},
                ],
                raw_text="PASSPORT\nSurname: DOE\nGiven Names: JOHN\nDoc No: P12345678\nDOB: 1988-05-12\nExpiry: 2030-05-12",
                status="success",
                model_version="mock_ocr_v1",
                is_mock=True,
            )

    def get_template(self) -> TemplateMatchResult:
        if self.scenario == "unknown_document":
            return TemplateMatchResult(
                template_id=None,
                alignment_score=0.12,
                status="unknown",
                deviations=["No matching reference template found for document structure."],
                is_mock=True,
            )
        else:
            return TemplateMatchResult(
                template_id="passport_td3_std",
                template_version="1.0",
                alignment_score=0.96,
                status="conforming",
                deviations=[],
                is_mock=True,
            )

    def get_forensics(self) -> List[ForensicSignal]:
        if self.scenario == "altered_dob":
            return [
                ForensicSignal(
                    detector_type="sift_copy_move",
                    signal="copy_move_clusters",
                    status="high",
                    confidence=0.91,
                    reliability=0.85,
                    applicable=True,
                    region=[120, 150, 120, 25],
                    explanation="Identified cloned feature clusters on Date of Birth field area, indicating copy-move manipulation.",
                    model_version="copy_move_v1",
                    is_mock=True,
                ),
                ForensicSignal(
                    detector_type="localized_manipulation_cnn",
                    signal="manipulation_cnn_score",
                    status="high",
                    confidence=0.88,
                    reliability=0.80,
                    applicable=True,
                    region=[120, 150, 120, 25],
                    explanation="High local patch artifact score (0.88) near the date of birth text boundary.",
                    model_version="efficientnet_b0_v1",
                    is_mock=True,
                ),
            ]
        else:
            return [
                ForensicSignal(
                    detector_type="sift_copy_move",
                    signal="copy_move_clusters",
                    status="low",
                    confidence=0.05,
                    reliability=0.85,
                    applicable=True,
                    explanation="No suspicious copy-move feature clusters detected.",
                    model_version="copy_move_v1",
                    is_mock=True,
                ),
                ForensicSignal(
                    detector_type="localized_manipulation_cnn",
                    signal="manipulation_cnn_score",
                    status="low",
                    confidence=0.08,
                    reliability=0.80,
                    applicable=True,
                    explanation="CNN patch evaluation indicates uniform natural noise background.",
                    model_version="efficientnet_b0_v1",
                    is_mock=True,
                ),
            ]

    def get_face(self) -> FaceResult:
        if self.scenario == "wrong_face":
            return FaceResult(
                similarity_score=0.22,
                identity_status="mismatch",
                face_quality={"live_det_score": 0.99, "doc_det_score": 0.97},
                explanation="Live capture face does not match document portrait photo (ArcFace cosine similarity 0.22 < threshold 0.60).",
                model_version="arcface_v1",
                is_mock=True,
            )
        else:
            return FaceResult(
                similarity_score=0.88,
                identity_status="match",
                face_quality={"live_det_score": 0.99, "doc_det_score": 0.98},
                explanation="Live face matches document portrait photo (ArcFace cosine similarity 0.88 >= threshold 0.60).",
                model_version="arcface_v1",
                is_mock=True,
            )

    def get_pad(self) -> PADResult:
        return PADResult(
            status="genuine",
            confidence=0.94,
            explanation="Presentation Attack Detection passed — genuine live capture.",
            tested_attacks=["print_photo", "screen_display", "replay_attack"],
            model_version="classical_pad_v1",
            is_mock=True,
        )


# Simple wrapper classes for single adapters
class MockDocumentClassifier(DocumentClassifier):
    def __init__(self, scenario: str = "genuine"):
        self.suite = MockAdapterSuite(scenario)

    def classify(self, image: np.ndarray) -> ClassificationResult:
        return self.suite.get_classification()


class MockOCRProvider(OCRProvider):
    def __init__(self, scenario: str = "genuine"):
        self.suite = MockAdapterSuite(scenario)

    def extract(self, image: np.ndarray) -> OCRResult:
        return self.suite.get_ocr()


class MockForensicDetector(ForensicDetector):
    def __init__(self, scenario: str = "genuine", detector_name: str = "mock_forensic"):
        self._detector_type = detector_name
        self.suite = MockAdapterSuite(scenario)

    @property
    def detector_type(self) -> str:
        return self._detector_type

    def analyze(self, image: np.ndarray, context=None) -> List[ForensicSignal]:
        return self.suite.get_forensics()


class MockFaceVerifier(FaceVerifier):
    def __init__(self, scenario: str = "genuine"):
        self.suite = MockAdapterSuite(scenario)

    def compare(self, live_image: np.ndarray, doc_photo: np.ndarray) -> FaceResult:
        return self.suite.get_face()


class MockPADDetector(PADDetector):
    def __init__(self, scenario: str = "genuine"):
        self.suite = MockAdapterSuite(scenario)

    def assess(self, frames: list[np.ndarray]) -> PADResult:
        return self.suite.get_pad()
