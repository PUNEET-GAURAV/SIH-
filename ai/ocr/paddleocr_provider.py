"""PaddleOCR Provider implementation — wraps PaddleOCR with fallback to mock or unavailable."""

import logging
import numpy as np
from typing import Optional

from ai.common.interfaces import OCRProvider, OCRResult

logger = logging.getLogger("docshield.ocr.paddle")


class PaddleOCRProvider(OCRProvider):
    """Real OCR Provider wrapping PaddleOCR."""

    def __init__(self, lang: str = "en"):
        self.lang = lang
        self._ocr = None
        self._initialized = False

    def _ensure_initialized(self):
        if self._initialized:
            return
        try:
            from paddleocr import PaddleOCR
            # Suppress excessive debug logs
            self._ocr = PaddleOCR(use_angle_cls=True, lang=self.lang, show_log=False)
            self._initialized = True
            logger.info("PaddleOCR engine initialized successfully.")
        except Exception as e:
            logger.warning(f"Failed to initialize PaddleOCR: {e}")
            self._ocr = None
            self._initialized = False

    def extract(self, image: np.ndarray) -> OCRResult:
        """Extract text using PaddleOCR."""
        self._ensure_initialized()
        if self._ocr is None:
            return OCRResult(
                fields=[],
                raw_text="",
                status="unavailable",
                model_version="paddleocr_v2",
                is_mock=False,
            )

        try:
            result = self._ocr.ocr(image, cls=True)
            if not result or not result[0]:
                return OCRResult(fields=[], raw_text="", status="success", model_version="paddleocr_v2")

            fields = []
            raw_lines = []
            for line in result[0]:
                bbox, (text, conf) = line
                raw_lines.append(text)
                fields.append({
                    "field_name": "raw_text_box",
                    "value": text,
                    "confidence": float(conf),
                    "bbox": [int(bbox[0][0]), int(bbox[0][1]), int(bbox[2][0] - bbox[0][0]), int(bbox[2][1] - bbox[0][1])],
                })

            raw_text = "\n".join(raw_lines)
            return OCRResult(
                fields=fields,
                raw_text=raw_text,
                status="success",
                model_version="paddleocr_v2",
                is_mock=False,
            )
        except Exception as e:
            logger.error(f"PaddleOCR extraction error: {e}")
            return OCRResult(
                fields=[],
                raw_text="",
                status="unavailable",
                model_version="paddleocr_v2",
                is_mock=False,
            )
