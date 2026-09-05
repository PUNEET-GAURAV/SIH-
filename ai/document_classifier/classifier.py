"""Document classifier — heuristic-based for MVP.

Build Spec §3: for MVP, a rule/heuristic classifier over 2 known classes
is acceptable — do not over-invest here relative to forensics/fusion.

Classes: passport (TD3), id_card (TD1), UNKNOWN.
"""

import logging
from typing import Optional

import cv2
import numpy as np

from ai.common.interfaces import DocumentClassifier, ClassificationResult
from backend.config import get_pipeline_config

logger = logging.getLogger("docshield.classifier")


class HeuristicDocumentClassifier(DocumentClassifier):
    """Heuristic document classifier using aspect ratio + MRZ detection.

    For MVP, uses:
    - Aspect ratio analysis (TD3 passports ~1.42:1, TD1 cards ~1.58:1)
    - MRZ line detection (2 lines for TD3, 3 lines for TD1)
    - Edge/structure heuristics
    """

    def __init__(self, config: Optional[dict] = None):
        pipeline_config = get_pipeline_config()
        self.config = config or pipeline_config.get("classification", {})
        self.min_confidence = self.config.get("min_confidence", 0.7)

        # TD3 Passport: ISO/IEC 7810 ID-3 size = 125mm × 88mm → ratio ~1.42
        # TD1 ID card: ISO/IEC 7810 ID-1 size = 85.6mm × 53.98mm → ratio ~1.586
        self.td3_ratio = 1.42
        self.td1_ratio = 1.586
        self.ratio_tolerance = 0.15

    def classify(self, image: np.ndarray) -> ClassificationResult:
        """Classify a document image by type.

        Args:
            image: BGR document image (preferably after perspective correction)

        Returns:
            ClassificationResult with type and confidence
        """
        h, w = image.shape[:2]
        aspect_ratio = max(w, h) / min(w, h) if min(w, h) > 0 else 0

        # Score each type
        scores = {}

        # Aspect ratio scoring
        td3_ar_diff = abs(aspect_ratio - self.td3_ratio)
        td1_ar_diff = abs(aspect_ratio - self.td1_ratio)

        if td3_ar_diff < self.ratio_tolerance:
            scores["passport_td3"] = max(0, 1.0 - td3_ar_diff / self.ratio_tolerance) * 0.5
        if td1_ar_diff < self.ratio_tolerance:
            scores["id_card_td1"] = max(0, 1.0 - td1_ar_diff / self.ratio_tolerance) * 0.5

        # MRZ detection bonus
        mrz_lines = self._detect_mrz_region(image)
        if mrz_lines == 2:
            scores["passport_td3"] = scores.get("passport_td3", 0) + 0.35
        elif mrz_lines == 3:
            scores["id_card_td1"] = scores.get("id_card_td1", 0) + 0.35

        # Size heuristic (passports are larger)
        total_pixels = h * w
        if total_pixels > 500000:  # Likely passport-sized or larger
            scores["passport_td3"] = scores.get("passport_td3", 0) + 0.1

        if not scores:
            return ClassificationResult(
                document_type="unknown",
                confidence=0.0,
                is_unknown_mode=True,
                model_version="heuristic_classifier_v1",
            )

        # Pick the best
        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]

        if best_score < self.min_confidence:
            return ClassificationResult(
                document_type="unknown",
                confidence=best_score,
                is_unknown_mode=True,
                model_version="heuristic_classifier_v1",
            )

        return ClassificationResult(
            document_type=best_type,
            confidence=best_score,
            is_unknown_mode=False,
            model_version="heuristic_classifier_v1",
        )

    def _detect_mrz_region(self, image: np.ndarray) -> int:
        """Detect MRZ-like region at the bottom of the document.

        Returns estimated number of MRZ lines (0, 2, or 3).
        """
        h, w = image.shape[:2]
        # MRZ is typically in the bottom 30% of the document
        bottom_region = image[int(h * 0.65):, :]

        if bottom_region.size == 0:
            return 0

        gray = cv2.cvtColor(bottom_region, cv2.COLOR_BGR2GRAY)
        # Apply threshold to find dark text on light background
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Find horizontal runs (MRZ chars are monospaced, creating strong horizontal structure)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(w // 4, 1), 1))
        horizontal = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        # Count distinct horizontal lines
        contours, _ = cv2.findContours(horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter contours by width (MRZ lines span most of the document width)
        mrz_lines = 0
        for cnt in contours:
            x, y, cw, ch = cv2.boundingRect(cnt)
            if cw > w * 0.5 and ch < h * 0.1:
                mrz_lines += 1

        return min(mrz_lines, 3)
