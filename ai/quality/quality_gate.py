"""Capture Quality Gate — Stage 1 of the pipeline.

Pure OpenCV/scikit-image, no model dependency.
Checks: blur, glare, resolution, corners, perspective, document area.
Build Spec §3: must run in <200ms on a 12MP image on CPU.
"""

import logging
from typing import Optional

import cv2
import numpy as np

from ai.common.interfaces import QualityResult
from backend.config import get_pipeline_config

logger = logging.getLogger("docshield.quality")


class QualityGate:
    """Evaluates capture quality of a document image.

    States:
    - ACCEPT: quality is adequate for all downstream processing
    - PROCESS_WITH_DEGRADED_CONFIDENCE: quality issues present, reduce reliability
    - RECAPTURE_REQUIRED: quality too poor, request new capture
    """

    def __init__(self, config: Optional[dict] = None):
        pipeline_config = get_pipeline_config()
        self.config = config or pipeline_config.get("quality", {})
        self.min_resolution = self.config.get("min_resolution", 640)
        self.max_blur_score = self.config.get("max_blur_score", 100.0)
        self.max_glare_ratio = self.config.get("max_glare_ratio", 0.15)
        self.min_corner_count = self.config.get("min_corner_count", 4)
        self.min_document_area_ratio = self.config.get("min_document_area_ratio", 0.1)

    def assess(self, image: np.ndarray) -> QualityResult:
        """Assess the quality of a captured document image.

        Args:
            image: BGR image as numpy array

        Returns:
            QualityResult with status and detailed metrics
        """
        issues = []
        h, w = image.shape[:2]

        # Resolution check
        min_dim = min(h, w)
        if min_dim < self.min_resolution:
            issues.append(f"Resolution too low: {w}x{h} (minimum {self.min_resolution}px)")

        # Blur detection (Laplacian variance)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        if blur_score < self.max_blur_score:
            issues.append(f"Image appears blurry (score: {blur_score:.1f}, threshold: {self.max_blur_score})")

        # Glare detection (overexposed pixel ratio)
        glare_mask = gray > 250
        glare_ratio = float(np.sum(glare_mask)) / (h * w)
        if glare_ratio > self.max_glare_ratio:
            issues.append(f"Glare detected: {glare_ratio:.1%} overexposed pixels")

        # Document boundary detection (corner detection)
        corners = self._detect_document_corners(gray)
        corner_count = len(corners) if corners is not None else 0

        # Document area ratio (approximate using contours)
        doc_area_ratio = self._estimate_document_area(gray, h, w)

        # Perspective distortion estimate
        perspective_distortion = self._estimate_perspective(corners, h, w) if corner_count >= 4 else 0.5

        # Determine overall status
        critical_issues = sum([
            min_dim < self.min_resolution // 2,
            blur_score < self.max_blur_score / 3,
            glare_ratio > self.max_glare_ratio * 2,
            corner_count < 2,
        ])
        minor_issues = len(issues)

        if critical_issues > 0:
            status = "recapture_required"
        elif minor_issues > 0:
            status = "process_with_degraded_confidence"
        else:
            status = "accept"

        explanation_parts = []
        if status == "accept":
            explanation_parts.append("Image quality is adequate for processing.")
        elif status == "recapture_required":
            explanation_parts.append("Image quality is too poor for reliable processing. Please recapture.")
        else:
            explanation_parts.append("Image quality has issues but processing will proceed with reduced confidence.")
        explanation_parts.extend(issues)

        return QualityResult(
            status=status,
            blur_score=float(blur_score),
            glare_ratio=float(glare_ratio),
            resolution=(w, h),
            corner_count=corner_count,
            perspective_distortion=float(perspective_distortion),
            document_area_ratio=float(doc_area_ratio),
            issues=issues,
            explanation="\n".join(explanation_parts),
        )

    def _detect_document_corners(self, gray: np.ndarray) -> Optional[np.ndarray]:
        """Detect document corners using edge detection and contour analysis."""
        # Edge detection
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)

        # Dilate edges to close gaps
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)

        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None

        # Get the largest contour
        largest = max(contours, key=cv2.contourArea)

        # Approximate polygon
        peri = cv2.arcLength(largest, True)
        approx = cv2.approxPolyDP(largest, 0.02 * peri, True)

        if len(approx) >= 4:
            return approx.reshape(-1, 2)
        return None

    def _estimate_document_area(self, gray: np.ndarray, h: int, w: int) -> float:
        """Estimate the document area as a ratio of the total frame."""
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return 0.0

        largest = max(contours, key=cv2.contourArea)
        doc_area = cv2.contourArea(largest)
        total_area = h * w

        return doc_area / total_area if total_area > 0 else 0.0

    def _estimate_perspective(self, corners: Optional[np.ndarray], h: int, w: int) -> float:
        """Estimate perspective distortion from detected corners."""
        if corners is None or len(corners) < 4:
            return 0.5  # Unknown

        # Sort corners: top-left, top-right, bottom-right, bottom-left
        sorted_corners = self._sort_corners(corners[:4])
        if sorted_corners is None:
            return 0.3

        tl, tr, br, bl = sorted_corners

        # Check if the quadrilateral is roughly rectangular
        top_width = np.linalg.norm(tr - tl)
        bottom_width = np.linalg.norm(br - bl)
        left_height = np.linalg.norm(bl - tl)
        right_height = np.linalg.norm(br - tr)

        width_ratio = min(top_width, bottom_width) / max(top_width, bottom_width) if max(top_width, bottom_width) > 0 else 0
        height_ratio = min(left_height, right_height) / max(left_height, right_height) if max(left_height, right_height) > 0 else 0

        distortion = 1.0 - (width_ratio * height_ratio)
        return float(distortion)

    def _sort_corners(self, corners: np.ndarray) -> Optional[np.ndarray]:
        """Sort 4 corners in order: TL, TR, BR, BL."""
        if len(corners) < 4:
            return None

        pts = corners[:4].astype(np.float32)
        # Sum and diff to find corners
        s = pts.sum(axis=1)
        d = np.diff(pts, axis=1).flatten()

        tl = pts[np.argmin(s)]
        br = pts[np.argmax(s)]
        tr = pts[np.argmin(d)]
        bl = pts[np.argmax(d)]

        return np.array([tl, tr, br, bl], dtype=np.float32)


class PerspectiveCorrector:
    """Corrects perspective distortion using detected document corners."""

    def correct(self, image: np.ndarray, corners: Optional[np.ndarray] = None) -> np.ndarray:
        """Apply perspective correction to a document image.

        Args:
            image: BGR input image
            corners: Optional pre-detected corners [TL, TR, BR, BL]

        Returns:
            Perspective-corrected BGR image
        """
        if corners is None:
            corners = self._detect_corners(image)

        if corners is None or len(corners) < 4:
            # Cannot correct — return original
            logger.warning("Could not detect document corners for perspective correction")
            return image

        # Sort corners
        pts = self._sort_corners(corners[:4].astype(np.float32))
        if pts is None:
            return image

        tl, tr, br, bl = pts

        # Compute target dimensions
        width_top = np.linalg.norm(tr - tl)
        width_bottom = np.linalg.norm(br - bl)
        max_width = int(max(width_top, width_bottom))

        height_left = np.linalg.norm(bl - tl)
        height_right = np.linalg.norm(br - tr)
        max_height = int(max(height_left, height_right))

        if max_width <= 0 or max_height <= 0:
            return image

        # Destination points
        dst = np.array([
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1],
        ], dtype=np.float32)

        # Compute and apply perspective transform
        M = cv2.getPerspectiveTransform(pts, dst)
        corrected = cv2.warpPerspective(image, M, (max_width, max_height))

        return corrected

    def _detect_corners(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Detect document corners in the image."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None

        largest = max(contours, key=cv2.contourArea)
        peri = cv2.arcLength(largest, True)
        approx = cv2.approxPolyDP(largest, 0.02 * peri, True)

        if len(approx) >= 4:
            return approx.reshape(-1, 2).astype(np.float32)
        return None

    def _sort_corners(self, corners: np.ndarray) -> Optional[np.ndarray]:
        """Sort corners to TL, TR, BR, BL order."""
        if len(corners) < 4:
            return None
        pts = corners[:4].astype(np.float32)
        s = pts.sum(axis=1)
        d = np.diff(pts, axis=1).flatten()
        tl = pts[np.argmin(s)]
        br = pts[np.argmax(s)]
        tr = pts[np.argmin(d)]
        bl = pts[np.argmax(d)]
        return np.array([tl, tr, br, bl], dtype=np.float32)
