"""Face Verifier implementation — InsightFace / ArcFace cosine similarity.

Build Spec §3 & §4: Wraps InsightFace (RetinaFace detector + ArcFace embedding).
If InsightFace weights/packages are unavailable, returns unavailable/mock result cleanly.
"""

import logging
import numpy as np
from typing import Optional

from ai.common.interfaces import FaceVerifier, FaceResult

logger = logging.getLogger("docshield.face.insightface")


class InsightFaceVerifier(FaceVerifier):
    """InsightFace (RetinaFace + ArcFace) face verifier."""

    def __init__(self, match_threshold: float = 0.60):
        self.match_threshold = match_threshold
        self._app = None
        self._initialized = False

    def _ensure_initialized(self):
        if self._initialized:
            return
        try:
            import sys
            import onnx
            try:
                from onnx import _mapping
            except ImportError:
                class MappingMock:
                    NP_TYPE_TO_TENSOR_TYPE = {}
                onnx._mapping = MappingMock()
                sys.modules['onnx.mapping'] = onnx._mapping
            
            from insightface.app import FaceAnalysis
            app = FaceAnalysis(name="buffalo_l", providers=['CPUExecutionProvider'])
            app.prepare(ctx_id=0, det_size=(640, 640))
            self._app = app
            self._initialized = True
            logger.info("InsightFace app initialized.")
        except Exception as e:
            logger.warning(f"Failed to initialize InsightFace: {e}")
            self._app = None
            self._initialized = False

    def compare(self, live_image: np.ndarray, doc_photo: np.ndarray) -> FaceResult:
        """Compare live face image with document portrait photo using ArcFace embeddings."""
        self._ensure_initialized()
        if self._app is None:
            return FaceResult(
                similarity_score=0.0,
                identity_status="not_available",
                explanation="InsightFace model unavailable. Operating in mock/unavailable mode.",
                model_version="arcface_v1",
                is_mock=False,
            )

        try:
            faces_live = self._app.get(live_image)
            faces_doc = self._app.get(doc_photo)

            if not faces_live:
                return FaceResult(
                    similarity_score=0.0,
                    identity_status="uncertain",
                    explanation="No face detected in live capture image.",
                    model_version="arcface_v1",
                    is_mock=False,
                )

            if not faces_doc:
                return FaceResult(
                    similarity_score=0.0,
                    identity_status="uncertain",
                    explanation="No face detected in document portrait photo.",
                    model_version="arcface_v1",
                    is_mock=False,
                )

            emb1 = faces_live[0].embedding
            emb2 = faces_doc[0].embedding

            # Cosine similarity
            sim = float(np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))

            if sim >= self.match_threshold:
                status = "match"
                explanation = f"Face match confirmed (ArcFace cosine similarity {sim:.3f} >= threshold {self.match_threshold})."
            elif sim >= 0.40:
                status = "uncertain"
                explanation = f"Face match uncertain (ArcFace cosine similarity {sim:.3f}). Manual review advised."
            else:
                status = "mismatch"
                explanation = f"Face mismatch detected (ArcFace cosine similarity {sim:.3f} < threshold {self.match_threshold})."

            return FaceResult(
                similarity_score=sim,
                identity_status=status,
                face_quality={
                    "live_det_score": float(faces_live[0].det_score),
                    "doc_det_score": float(faces_doc[0].det_score),
                },
                explanation=explanation,
                model_version="arcface_v1",
                is_mock=False,
            )
        except Exception as e:
            logger.error(f"Error during InsightFace comparison: {e}")
            return FaceResult(
                similarity_score=0.0,
                identity_status="not_available",
                explanation=f"Error executing face verification: {e}",
                model_version="arcface_v1",
                is_mock=False,
            )
