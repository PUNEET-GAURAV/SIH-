"""Copy-Move Detection — SIFT/ORB descriptor matching + geometric verification.

Classical CV, no training data required. Detects duplicated regions
that may indicate copy-paste manipulation.

Build Spec §3: each detector is a separate class implementing ForensicDetector.
"""

import logging
from typing import Optional

import cv2
import numpy as np

from ai.common.interfaces import ForensicDetector, ForensicSignal
from backend.config import get_pipeline_config

logger = logging.getLogger("docshield.forensics.copymove")


class CopyMoveDetector(ForensicDetector):
    """Detects copy-move forgery using feature matching.

    Method: ORB descriptor extraction → BFMatcher → geometric (affine)
    verification → spatial clustering.

    Known limitation: repetitive legitimate security patterns (guilloché,
    repeated micro-text) can cause false positives. These are downweighted
    via minimum cluster distance filtering.
    """

    def __init__(self, config: Optional[dict] = None):
        pipeline_config = get_pipeline_config()
        cm_config = config or pipeline_config.get("forensics", {}).get("copy_move", {})
        self.min_matches = cm_config.get("min_matches", 10)
        self.distance_ratio = cm_config.get("distance_ratio", 0.75)
        self.min_cluster_size = cm_config.get("min_cluster_size", 5)
        self.ransac_threshold = cm_config.get("ransac_threshold", 5.0)

    @property
    def detector_type(self) -> str:
        return "copy_move"

    def analyze(self, image: np.ndarray, context: Optional[dict] = None) -> list[ForensicSignal]:
        """Analyze an image for copy-move manipulation.

        Args:
            image: BGR image
            context: Optional context (quality info, etc.)

        Returns:
            List of ForensicSignal items
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Extract ORB keypoints and descriptors
            orb = cv2.ORB_create(nfeatures=2000)
            keypoints, descriptors = orb.detectAndCompute(gray, None)

            if descriptors is None or len(keypoints) < self.min_matches:
                return [ForensicSignal(
                    detector_type="copy_move",
                    signal="copy_move",
                    status="low",
                    confidence=0.8,
                    reliability=0.7,
                    explanation="Insufficient features detected for copy-move analysis.",
                    model_version="copymove_orb_v1",
                )]

            # Self-matching: match descriptors against themselves
            bf = cv2.BFMatcher(cv2.NORM_HAMMING)
            matches = bf.knnMatch(descriptors, descriptors, k=5)

            # Filter: keep matches that are not self-matches and pass ratio test
            good_matches = []
            for match_group in matches:
                for i, m in enumerate(match_group):
                    if i == 0:
                        continue  # Skip self-match (distance 0)
                    if m.distance > 0:
                        # Ratio test against the next match
                        if i + 1 < len(match_group):
                            ratio = m.distance / match_group[i + 1].distance if match_group[i + 1].distance > 0 else 1.0
                        else:
                            ratio = 0.5
                        if ratio < self.distance_ratio:
                            # Ensure it's not matching a neighboring keypoint
                            pt1 = keypoints[m.queryIdx].pt
                            pt2 = keypoints[m.trainIdx].pt
                            dist = np.sqrt((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2)
                            if dist > 20:  # Minimum spatial distance
                                good_matches.append(m)
                        break

            if len(good_matches) < self.min_matches:
                return [ForensicSignal(
                    detector_type="copy_move",
                    signal="copy_move",
                    status="low",
                    confidence=0.7,
                    reliability=0.8,
                    explanation="No significant copy-move patterns detected.",
                    model_version="copymove_orb_v1",
                    details={"match_count": len(good_matches)},
                )]

            # Geometric verification with RANSAC
            src_pts = np.float32([keypoints[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([keypoints[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

            M, mask = cv2.estimateAffinePartial2D(src_pts, dst_pts, method=cv2.RANSAC,
                                                   ransacReprojThreshold=self.ransac_threshold)

            if mask is None:
                return [ForensicSignal(
                    detector_type="copy_move",
                    signal="copy_move",
                    status="low",
                    confidence=0.6,
                    reliability=0.7,
                    explanation="Feature matches found but no consistent geometric transform detected.",
                    model_version="copymove_orb_v1",
                )]

            inlier_count = int(mask.sum())

            if inlier_count < self.min_cluster_size:
                return [ForensicSignal(
                    detector_type="copy_move",
                    signal="copy_move",
                    status="low",
                    confidence=0.65,
                    reliability=0.75,
                    explanation="Few geometrically consistent matches. No strong copy-move evidence.",
                    model_version="copymove_orb_v1",
                    details={"inlier_count": inlier_count},
                )]

            # Compute bounding region of matched areas
            inlier_pts_src = src_pts[mask.ravel() == 1].reshape(-1, 2)
            inlier_pts_dst = dst_pts[mask.ravel() == 1].reshape(-1, 2)

            region_src = self._bounding_box(inlier_pts_src)
            region_dst = self._bounding_box(inlier_pts_dst)

            # Determine severity based on inlier count
            if inlier_count >= self.min_matches * 2:
                status = "high"
                confidence = min(0.95, 0.6 + inlier_count * 0.01)
            elif inlier_count >= self.min_matches:
                status = "medium"
                confidence = min(0.8, 0.5 + inlier_count * 0.01)
            else:
                status = "low"
                confidence = 0.5

            # Adjust reliability based on quality context
            reliability = 0.85
            if context and context.get("quality_reliability", 1.0) < 1.0:
                reliability *= context["quality_reliability"]

            return [ForensicSignal(
                detector_type="copy_move",
                signal="copy_move",
                status=status,
                confidence=confidence,
                reliability=reliability,
                explanation=f"Possible copy-move region detected with {inlier_count} geometrically "
                            f"consistent feature matches. This may indicate duplicated content but "
                            f"could also be caused by repetitive document patterns.",
                region=region_src,
                model_version="copymove_orb_v1",
                details={
                    "inlier_count": inlier_count,
                    "total_matches": len(good_matches),
                    "source_region": region_src,
                    "destination_region": region_dst,
                },
            )]

        except Exception as e:
            logger.error(f"Copy-move detection error: {e}", exc_info=True)
            return [ForensicSignal(
                detector_type="copy_move",
                signal="copy_move",
                status="uncertain",
                confidence=0.0,
                reliability=0.0,
                explanation=f"Copy-move detection encountered an error: {str(e)}",
                model_version="copymove_orb_v1",
            )]

    def _bounding_box(self, points: np.ndarray) -> list:
        """Compute bounding box [x, y, w, h] from a set of points."""
        x_min, y_min = points.min(axis=0).astype(int)
        x_max, y_max = points.max(axis=0).astype(int)
        return [int(x_min), int(y_min), int(x_max - x_min), int(y_max - y_min)]
