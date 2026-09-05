"""Template / Structural Validation — Stage 4 of the pipeline.

Compares a normalized document image against known template metadata:
field bounding boxes, photo/MRZ zones, aspect ratio, geometric tolerance.

Build Spec §3: homography-based alignment against 1-2 stored reference templates.
"""

import logging
from typing import Optional

import cv2
import numpy as np

from ai.common.interfaces import TemplateMatchResult
from backend.config import get_pipeline_config

logger = logging.getLogger("docshield.template")


# Template metadata for known document types
TEMPLATE_REGISTRY = {
    "passport_td3": {
        "id": "passport_td3",
        "version": "v1",
        "aspect_ratio": 1.42,
        "dimensions": (1000, 704),  # normalized reference size (w, h)
        "zones": {
            "photo": {"bbox": [30, 180, 270, 350], "required": True},
            "mrz": {"bbox": [30, 560, 940, 130], "required": True},
            "name": {"bbox": [310, 180, 650, 50], "required": True},
            "document_number": {"bbox": [310, 240, 300, 40], "required": False},
            "nationality": {"bbox": [310, 290, 300, 40], "required": False},
            "dob": {"bbox": [310, 340, 300, 40], "required": False},
            "sex": {"bbox": [310, 390, 100, 40], "required": False},
            "expiry": {"bbox": [310, 440, 300, 40], "required": False},
        },
    },
    "id_card_td1": {
        "id": "id_card_td1",
        "version": "v1",
        "aspect_ratio": 1.586,
        "dimensions": (856, 540),  # normalized reference size (w, h)
        "zones": {
            "photo": {"bbox": [20, 100, 200, 250], "required": True},
            "mrz": {"bbox": [20, 380, 816, 140], "required": True},
            "name": {"bbox": [240, 100, 580, 45], "required": True},
            "document_number": {"bbox": [240, 155, 300, 35], "required": False},
            "dob": {"bbox": [240, 200, 300, 35], "required": False},
        },
    },
}


class TemplateValidator:
    """Validates document structure against known templates."""

    def __init__(self, config: Optional[dict] = None):
        pipeline_config = get_pipeline_config()
        self.config = config or pipeline_config.get("template", {})
        self.alignment_tolerance = self.config.get("alignment_tolerance", 0.05)
        self.aspect_ratio_tolerance = self.config.get("aspect_ratio_tolerance", 0.03)
        self.field_position_tolerance = self.config.get("field_position_tolerance", 15)

    def validate(self, image: np.ndarray, document_type: str) -> TemplateMatchResult:
        """Validate a document image against its template.

        Args:
            image: BGR document image (after perspective correction)
            document_type: Classified document type

        Returns:
            TemplateMatchResult with alignment score and deviations
        """
        if document_type not in TEMPLATE_REGISTRY:
            return TemplateMatchResult(
                status="unknown",
                deviations=[{
                    "type": "no_template",
                    "description": "No template available for this document type. "
                                   "Structural validation is disabled.",
                }],
            )

        template = TEMPLATE_REGISTRY[document_type]

        h, w = image.shape[:2]
        aspect_ratio = w / h if h > 0 else 0

        deviations = []
        checks_passed = 0
        total_checks = 0

        # Check aspect ratio
        total_checks += 1
        expected_ar = template["aspect_ratio"]
        ar_diff = abs(aspect_ratio - expected_ar)
        if ar_diff > self.aspect_ratio_tolerance:
            deviations.append({
                "type": "aspect_ratio",
                "expected": expected_ar,
                "actual": round(aspect_ratio, 3),
                "deviation": round(ar_diff, 3),
                "description": f"Aspect ratio {aspect_ratio:.3f} deviates from expected {expected_ar:.3f}. "
                               "This could indicate cropping, different edition, or perspective residual.",
            })
        else:
            checks_passed += 1

        # Normalize image to template dimensions for zone comparison
        ref_w, ref_h = template["dimensions"]
        normalized = cv2.resize(image, (ref_w, ref_h))

        # Check zone presence and positioning
        gray = cv2.cvtColor(normalized, cv2.COLOR_BGR2GRAY)

        for zone_name, zone_info in template.get("zones", {}).items():
            total_checks += 1
            bbox = zone_info["bbox"]
            is_required = zone_info.get("required", False)

            # Extract zone region
            x, y, zw, zh = bbox
            if x + zw > ref_w or y + zh > ref_h:
                continue

            zone_region = gray[y:y + zh, x:x + zw]
            if zone_region.size == 0:
                continue

            # Check if zone has expected content (text/face)
            has_content = self._check_zone_content(zone_region, zone_name)

            if has_content:
                checks_passed += 1
            elif is_required:
                deviations.append({
                    "type": "missing_zone",
                    "zone": zone_name,
                    "bbox": bbox,
                    "description": f"Expected content in '{zone_name}' zone not detected. "
                                   "This could indicate a different document edition, print variant, "
                                   "or structural anomaly.",
                })

        # Compute alignment score
        alignment_score = checks_passed / total_checks if total_checks > 0 else 0.0

        if alignment_score >= 0.8 and not deviations:
            status = "conforming"
        elif deviations:
            status = "deviation"
        else:
            status = "conforming"

        return TemplateMatchResult(
            template_id=template["id"],
            template_version=template["version"],
            alignment_score=alignment_score,
            status=status,
            deviations=deviations,
        )

    def _check_zone_content(self, zone: np.ndarray, zone_name: str) -> bool:
        """Check if a zone region has expected content."""
        if zone.size == 0:
            return False

        # For photo zones, check for face-like content (higher variance)
        if zone_name == "photo":
            return zone.std() > 30  # Photos have more variance than blank areas

        # For text zones, check for text-like edges
        edges = cv2.Canny(zone, 50, 150)
        edge_ratio = np.sum(edges > 0) / zone.size
        return edge_ratio > 0.02  # At least 2% edge pixels
