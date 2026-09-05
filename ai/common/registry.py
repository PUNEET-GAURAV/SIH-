"""AI module registry — resolves adapters based on availability and config."""

import logging
from typing import Optional, List

from backend.config import get_settings
from ai.common.mock_adapters import (
    MockDocumentClassifier, MockOCRProvider, MockForensicDetector,
    MockFaceVerifier, MockPADDetector, MockAdapterSuite,
)
from ai.document_classifier.classifier import HeuristicDocumentClassifier
from ai.mrz.parser import ICAOMRZParser as MRZParser
from ai.template.validator import TemplateValidator
from ai.forensics.copy_move import CopyMoveDetector

logger = logging.getLogger("docshield.ai")


class ModelRegistry:
    """Central registry for AI model adapters.

    Determines which implementation (real/mock) to use based on
    model availability and MOCK_MODE setting.
    """

    _instance = None

    def __init__(self):
        self._classifiers = {}
        self._ocr_providers = {}
        self._forensic_detectors = {}
        self._face_verifiers = {}
        self._pad_detectors = {}
        self._mrz_parser = MRZParser()
        self._template_validator = TemplateValidator()
        self._initialized = False

    @classmethod
    def get_instance(cls) -> "ModelRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def initialize(self):
        """Initialize all available adapters. Called once at startup."""
        if self._initialized:
            return

        settings = get_settings()
        logger.info(f"Initializing model registry (mock_mode={settings.mock_mode})")

        # Register mock adapters (always available)
        self._register_mock_adapters()

        # Register default classical/heuristic real adapters
        self._classifiers["heuristic"] = HeuristicDocumentClassifier()
        self._forensic_detectors["copy_move"] = CopyMoveDetector()

        # Register heavy real adapters (if available and not in mock mode)
        if not settings.mock_mode:
            self._register_real_adapters()

        self._initialized = True

    def _register_mock_adapters(self):
        """Register all mock implementations."""
        self._classifiers["mock"] = MockDocumentClassifier()
        self._ocr_providers["mock"] = MockOCRProvider()
        self._face_verifiers["mock"] = MockFaceVerifier()
        self._pad_detectors["mock"] = MockPADDetector()
        self._forensic_detectors["mock"] = MockForensicDetector()
        logger.info("Mock adapters registered")

    def _register_real_adapters(self):
        """Try to register real model implementations."""
        # OCR
        try:
            from ai.ocr.paddleocr_provider import PaddleOCRProvider
            self._ocr_providers["real"] = PaddleOCRProvider()
            logger.info("PaddleOCR provider loaded")
        except (ImportError, Exception) as e:
            logger.warning(f"PaddleOCR unavailable: {e}")

        # Face
        try:
            from ai.face.insightface_verifier import InsightFaceVerifier
            self._face_verifiers["real"] = InsightFaceVerifier()
            logger.info("InsightFace verifier loaded")
        except (ImportError, Exception) as e:
            logger.warning(f"InsightFace unavailable: {e}")

        # Forensic CNN
        try:
            from ai.forensics.manipulation_cnn import ManipulationCNN
            self._forensic_detectors["manipulation_cnn"] = ManipulationCNN()
            logger.info("Manipulation CNN loaded")
        except (ImportError, Exception) as e:
            logger.warning(f"Manipulation CNN unavailable: {e}")

        # PAD
        try:
            from ai.face.pad_detector import ClassicalPADDetector
            self._pad_detectors["real"] = ClassicalPADDetector()
            logger.info("Classical PAD loaded")
        except (ImportError, Exception) as e:
            logger.warning(f"PAD detector unavailable: {e}")

    def get_classifier(self):
        settings = get_settings()
        if settings.mock_mode:
            return self._classifiers.get("mock")
        return self._classifiers.get("heuristic") or self._classifiers.get("mock")

    def get_ocr_provider(self):
        settings = get_settings()
        if settings.mock_mode:
            return self._ocr_providers.get("mock")
        return self._ocr_providers.get("real") or self._ocr_providers.get("mock")

    def get_mrz_parser(self):
        return self._mrz_parser

    def get_template_validator(self):
        return self._template_validator

    def get_face_verifier(self):
        settings = get_settings()
        if settings.mock_mode:
            return self._face_verifiers.get("mock")
        return self._face_verifiers.get("real") or self._face_verifiers.get("mock")

    def get_pad_detector(self):
        settings = get_settings()
        if settings.mock_mode:
            return self._pad_detectors.get("mock")
        return self._pad_detectors.get("real") or self._pad_detectors.get("mock")

    def get_forensic_detectors(self) -> list:
        settings = get_settings()
        if settings.mock_mode:
            return [self._forensic_detectors.get("mock")]
        detectors = []
        if "copy_move" in self._forensic_detectors:
            detectors.append(self._forensic_detectors["copy_move"])
        if "manipulation_cnn" in self._forensic_detectors:
            detectors.append(self._forensic_detectors["manipulation_cnn"])
        if not detectors:
            detectors.append(self._forensic_detectors.get("mock"))
        return detectors

    def get_scenario_suite(self, scenario_name: str) -> MockAdapterSuite:
        return MockAdapterSuite(scenario_name)
