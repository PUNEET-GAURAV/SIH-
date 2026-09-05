"""Mock OCR Provider — deterministic mock outputs for demo/testing."""

import logging
from typing import Optional

import numpy as np

from ai.common.interfaces import OCRProvider, OCRResult

logger = logging.getLogger("docshield.ocr.mock")


class MockOCRProvider(OCRProvider):
    """Mock OCR provider returning deterministic results.

    All outputs carry is_mock=True. Used when PaddleOCR is unavailable
    or when MOCK_MODE=true.
    """

    def extract(self, image: np.ndarray) -> OCRResult:
        """Return mock OCR results."""
        return OCRResult(
            fields=[
                {"field_name": "surname", "value": "DEMO_SURNAME", "confidence": 0.95, "bbox": [100, 50, 200, 30]},
                {"field_name": "given_names", "value": "DEMO_GIVEN", "confidence": 0.93, "bbox": [100, 85, 200, 30]},
                {"field_name": "document_number", "value": "D0000000", "confidence": 0.90, "bbox": [100, 120, 150, 25]},
                {"field_name": "date_of_birth", "value": "01/01/1990", "confidence": 0.88, "bbox": [100, 155, 120, 25]},
                {"field_name": "expiry_date", "value": "01/01/2030", "confidence": 0.87, "bbox": [100, 190, 120, 25]},
                {"field_name": "nationality", "value": "UTO", "confidence": 0.92, "bbox": [300, 120, 80, 25]},
            ],
            raw_text="DEMO / MOCK OCR RESULT — not from a real OCR engine",
            status="success",
            model_version="mock_ocr_v1",
            is_mock=True,
        )
