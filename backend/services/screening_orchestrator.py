"""Screening pipeline orchestrator — Build Spec §5.

Coordinates the full screening pipeline:
create session → capture → quality gate → preprocess → classify
→ [OCR, MRZ, Barcode] concurrently → deterministic validation
→ [template, forensics] concurrently → face branch (independent)
→ fusion → persist report → audit
"""

import logging
import time
from typing import Optional, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np
from sqlalchemy.orm import Session

from backend.config import get_settings, get_pipeline_config
from backend.models import (
    ScreeningSession, SessionStatus, Document, QualityStatus,
    OCRField, MRZResult as DBMRZResult, TemplateResult as DBTemplateResult,
    ForensicResult as DBForensicResult, FaceVerification as DBFaceVerification,
    Evidence, ScreeningAssessment,
)
from backend.services.screening_service import ScreeningService
from backend.services.audit_service import AuditService
from ai.quality.quality_gate import QualityGate, PerspectiveCorrector
from ai.common.registry import ModelRegistry
from ai.fusion.engine import FusionEngine, FusionInput

logger = logging.getLogger("docshield.orchestrator")


class ScreeningOrchestrator:
    """Orchestrates the full document screening pipeline."""

    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.config = get_pipeline_config()
        self.screening_service = ScreeningService(db)
        self.audit_service = AuditService(db)
        self.quality_gate = QualityGate()
        self.perspective_corrector = PerspectiveCorrector()
        self.registry = ModelRegistry.get_instance()
        self.registry.initialize()
        self.fusion_engine = FusionEngine()
        self._executor = ThreadPoolExecutor(max_workers=4)

    def process_screening(self, session_id: str, actor_id: str) -> dict:
        """Run the full screening pipeline for a session."""
        start_time = time.time()
        session = self.screening_service.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        if not session.documents:
            raise ValueError("No documents uploaded for this session")

        document = session.documents[0]

        # Check if a deterministic demo scenario is specified in notes or settings
        scenario_name = self._detect_scenario(session)

        try:
            self._update_stage(session_id, "quality_gate")
            self.audit_service.log_event(
                session_id, actor_id, "processing_started",
                {"document_id": document.id, "scenario": scenario_name}
            )

            # Check if running mock mode or deterministic scenario
            if self.settings.mock_mode or scenario_name:
                return self._run_mock_pipeline(session_id, actor_id, document, scenario_name or "genuine", start_time)

            # === Real Pipeline Execution ===
            image = cv2.imread(document.file_path)
            if image is None:
                self._update_status(session_id, SessionStatus.ERROR)
                return {"status": "error", "message": "Could not load document image"}

            # Stage 1: Quality Gate
            quality_result = self.quality_gate.assess(image)
            self._persist_quality(document, quality_result)

            if quality_result.status == "recapture_required":
                self._update_status(session_id, SessionStatus.QUALITY_FAILED, "quality_gate")
                self._add_evidence(
                    session_id, "quality_gate", quality_result.status,
                    quality_result.explanation, 1.0, 1.0, True,
                    "quality_gate", "quality_v1", is_mock=False
                )
                self.audit_service.log_event(session_id, actor_id, "quality_failed", {"status": quality_result.status})
                return {
                    "status": "recapture_required",
                    "quality": quality_result.__dict__,
                    "elapsed_seconds": time.time() - start_time,
                }

            quality_reliability = 1.0 if quality_result.status == "accept" else 0.7

            # Stage 2: Preprocessing
            self._update_stage(session_id, "preprocessing")
            corrected = self.perspective_corrector.correct(image)

            # Stage 3: Document Classification
            self._update_stage(session_id, "classification")
            classifier = self.registry.get_classifier()
            cls_result = classifier.classify(corrected)
            self._persist_classification(document, cls_result.__dict__)

            # Stage 4: OCR + MRZ (concurrent)
            self._update_stage(session_id, "extraction")
            ocr_provider = self.registry.get_ocr_provider()
            mrz_parser = self.registry.get_mrz_parser()

            future_ocr = self._executor.submit(ocr_provider.extract, corrected)
            # MRZ parsing relies on OCR raw text or detected zone
            ocr_res = future_ocr.result()
            mrz_res = mrz_parser.parse(ocr_res.raw_text)

            self._persist_ocr_and_mrz(session_id, document, ocr_res, mrz_res)

            # Stage 5: Template Validation + Forensics (concurrent)
            self._update_stage(session_id, "analysis")
            template_validator = self.registry.get_template_validator()
            forensic_detectors = self.registry.get_forensic_detectors()

            future_template = self._executor.submit(
                template_validator.validate, corrected, cls_result.document_type
            )
            forensic_futures = [
                self._executor.submit(detector.analyze, corrected, {"document_type": cls_result.document_type})
                for detector in forensic_detectors
            ]

            tpl_res = future_template.result()
            forensic_signals = []
            for fut in forensic_futures:
                forensic_signals.extend(fut.result())

            self._persist_analysis(session_id, document, tpl_res, forensic_signals)

            # Stage 6: Face Verification + PAD (if live photo present)
            self._update_stage(session_id, "face_verification")
            face_result = None
            if session.live_face_path:
                live_img = cv2.imread(session.live_face_path)
                if live_img is not None:
                    face_verifier = self.registry.get_face_verifier()
                    pad_detector = self.registry.get_pad_detector()

                    # Extract doc portrait photo crop or use full image
                    face_res = face_verifier.compare(live_img, corrected)
                    pad_res = pad_detector.assess([live_img])
                    face_result = {
                        "verifier": face_res,
                        "pad": pad_res,
                    }
                    self._persist_face(session_id, face_result)

            # Stage 7: Evidence Fusion
            self._update_stage(session_id, "fusion")
            fusion_signals = self._collect_fusion_inputs(
                quality_result, cls_result, mrz_res, ocr_res, tpl_res, forensic_signals, face_result, quality_reliability
            )
            fusion_result = self.fusion_engine.fuse(fusion_signals, quality_reliability)
            self._persist_assessment(session_id, fusion_result)

            # Stage 8: Complete
            self._update_status(session_id, SessionStatus.COMPLETED, "completed")
            self.audit_service.log_event(
                session_id, actor_id, "processing_completed",
                {"concern_level": fusion_result.concern_level}
            )

            elapsed = time.time() - start_time
            return {
                "status": "completed",
                "concern_level": fusion_result.concern_level,
                "recommendation": fusion_result.recommendation,
                "elapsed_seconds": elapsed,
            }

        except Exception as e:
            logger.error(f"Pipeline error for session {session_id}: {e}", exc_info=True)
            self._update_status(session_id, SessionStatus.ERROR)
            self.audit_service.log_event(session_id, actor_id, "processing_error", {"error": str(e)})
            return {"status": "error", "message": str(e)}

    def _run_mock_pipeline(self, session_id: str, actor_id: str, document, scenario_name: str, start_time: float) -> dict:
        """Run deterministic mock pipeline based on selected scenario."""
        suite = self.registry.get_scenario_suite(scenario_name)

        q_res = suite.get_quality()
        self._persist_quality(document, q_res)

        if q_res.status == "recapture_required":
            self._update_status(session_id, SessionStatus.QUALITY_FAILED, "quality_gate")
            self._add_evidence(
                session_id, "quality_gate", q_res.status, q_res.explanation,
                1.0, 1.0, True, "quality_gate", "quality_v1", is_mock=True
            )
            self.audit_service.log_event(session_id, actor_id, "quality_failed", {"status": q_res.status, "scenario": scenario_name})
            return {
                "status": "recapture_required",
                "quality": q_res.__dict__,
                "elapsed_seconds": time.time() - start_time,
            }

        quality_reliability = 1.0

        cls_res = suite.get_classification()
        self._persist_classification(document, cls_res.__dict__)

        mrz_res = suite.get_mrz()
        ocr_res = suite.get_ocr()
        self._persist_ocr_and_mrz(session_id, document, ocr_res, mrz_res)

        tpl_res = suite.get_template()
        forensics_res = suite.get_forensics()
        self._persist_analysis(session_id, document, tpl_res, forensics_res)

        face_res = suite.get_face()
        pad_res = suite.get_pad()
        self._persist_face(session_id, {"verifier": face_res, "pad": pad_res})

        fusion_inputs = self._collect_fusion_inputs(
            q_res, cls_res, mrz_res, ocr_res, tpl_res, forensics_res, {"verifier": face_res, "pad": pad_res}, quality_reliability
        )

        fusion_result = self.fusion_engine.fuse(fusion_inputs, quality_reliability)
        self._persist_assessment(session_id, fusion_result)

        self._update_status(session_id, SessionStatus.COMPLETED, "completed")
        self.audit_service.log_event(
            session_id, actor_id, "processing_completed",
            {"concern_level": fusion_result.concern_level, "scenario": scenario_name}
        )

        return {
            "status": "completed",
            "concern_level": fusion_result.concern_level,
            "recommendation": fusion_result.recommendation,
            "elapsed_seconds": time.time() - start_time,
        }

    def _detect_scenario(self, session: ScreeningSession) -> Optional[str]:
        """Detect demo scenario from session notes/metadata or return None."""
        if session.notes and session.notes.startswith("scenario:"):
            return session.notes.split(":", 1)[1].strip()
        return None

    def _update_stage(self, session_id: str, stage: str):
        self.screening_service.update_session_status(session_id, SessionStatus.PROCESSING, stage)

    def _update_status(self, session_id: str, status: SessionStatus, stage: Optional[str] = None):
        self.screening_service.update_session_status(session_id, status, stage)

    def _persist_quality(self, document: Document, result):
        status_map = {
            "accept": QualityStatus.ACCEPT,
            "process_with_degraded_confidence": QualityStatus.DEGRADED,
            "recapture_required": QualityStatus.RECAPTURE_REQUIRED,
        }
        document.quality_status = status_map.get(result.status, QualityStatus.PENDING)
        document.quality_details = {
            "blur_score": result.blur_score,
            "glare_ratio": result.glare_ratio,
            "resolution": list(result.resolution),
            "corner_count": result.corner_count,
            "issues": result.issues,
        }
        self.db.commit()

    def _persist_classification(self, document: Document, result: dict):
        document.document_type = result.get("document_type", "unknown")
        document.classification_confidence = result.get("confidence", 0.0)
        self.db.commit()

    def _persist_ocr_and_mrz(self, session_id: str, document: Document, ocr_res, mrz_res):
        # Save OCR fields
        for f in ocr_res.fields:
            ocr_field = OCRField(
                document_id=document.id,
                field_name=f.get("field_name", "unknown"),
                field_value=f.get("value", ""),
                confidence=f.get("confidence", 0.0),
                bbox=f.get("bbox"),
                source="ocr",
                is_mock=ocr_res.is_mock,
            )
            self.db.add(ocr_field)

        # Save MRZ
        parsed_dict = {
            "document_type": mrz_res.document_type,
            "country_code": mrz_res.country_code,
            "surname": mrz_res.surname,
            "given_names": mrz_res.given_names,
            "document_number": mrz_res.document_number,
            "nationality": mrz_res.nationality,
            "date_of_birth": mrz_res.date_of_birth,
            "sex": mrz_res.sex,
            "expiry_date": mrz_res.expiry_date,
            "optional_data": mrz_res.optional_data,
            "is_valid": mrz_res.is_valid,
            "issues": mrz_res.issues,
        }
        db_mrz = DBMRZResult(
            document_id=document.id,
            raw_mrz=mrz_res.raw_mrz,
            parsed_fields=parsed_dict,
            checksum_results=mrz_res.checksum_results,
            overall_status=mrz_res.overall_status,
            is_mock=mrz_res.is_mock,
        )
        self.db.add(db_mrz)
        self.db.commit()

    def _persist_analysis(self, session_id: str, document: Document, tpl_res, forensic_signals):
        # Save template result
        db_tpl = DBTemplateResult(
            document_id=document.id,
            template_id=tpl_res.template_id,
            template_version=tpl_res.template_version,
            alignment_score=tpl_res.alignment_score,
            status=tpl_res.status,
            deviations=tpl_res.deviations,
            is_mock=tpl_res.is_mock,
        )
        self.db.add(db_tpl)

        # Save forensic results
        for sig in forensic_signals:
            db_for = DBForensicResult(
                document_id=document.id,
                detector_type=sig.detector_type,
                signal=sig.signal,
                status=sig.status,
                confidence=sig.confidence,
                reliability=sig.reliability,
                applicable=sig.applicable,
                region=sig.region,
                explanation=sig.explanation,
                model_version=sig.model_version,
                is_mock=sig.is_mock,
            )
            self.db.add(db_for)

        self.db.commit()

    def _persist_face(self, session_id: str, face_result: dict):
        verifier = face_result.get("verifier")
        pad = face_result.get("pad")

        pad_details_dict = pad.details if pad and pad.details else {}
        if pad:
            pad_details_dict["confidence"] = pad.confidence

        db_face = DBFaceVerification(
            session_id=session_id,
            similarity_score=verifier.similarity_score if verifier else 0.0,
            identity_status=verifier.identity_status if verifier else "not_available",
            face_quality=verifier.face_quality if verifier else {},
            pad_status=pad.status if pad else "uncertain",
            pad_details=pad_details_dict,
            explanation=verifier.explanation if verifier else "",
            is_mock=(verifier.is_mock if verifier else False) or (pad.is_mock if pad else False),
        )
        self.db.add(db_face)
        self.db.commit()

    def _persist_assessment(self, session_id: str, fusion_res):
        from backend.models.evidence import ConcernLevel, Recommendation

        concern_map = {
            "low_concern": ConcernLevel.LOW_CONCERN,
            "review_required": ConcernLevel.REVIEW_REQUIRED,
            "high_concern": ConcernLevel.HIGH_CONCERN,
        }
        rec_map = {
            "clear": Recommendation.CLEAR,
            "request_recapture": Recommendation.REQUEST_RECAPTURE,
            "secondary_inspection": Recommendation.SECONDARY_INSPECTION,
            "escalate": Recommendation.ESCALATE,
        }

        assessment = ScreeningAssessment(
            session_id=session_id,
            concern_level=concern_map.get(fusion_res.concern_level, ConcernLevel.REVIEW_REQUIRED),
            recommendation=rec_map.get(fusion_res.recommendation, Recommendation.SECONDARY_INSPECTION),
            summary=fusion_res.summary,
            fusion_details=fusion_res.fusion_details,
            dimension_results=fusion_res.dimension_results,
            contradictions=fusion_res.contradictions,
            is_mock=fusion_res.is_mock,
        )
        self.db.add(assessment)
        self.db.commit()

    def _add_evidence(self, session_id, signal, status, explanation,
                      confidence, reliability, applicable, source, model_version,
                      value=None, region=None, is_mock=False):
        ev = Evidence(
            session_id=session_id,
            signal=signal,
            status=status,
            value=value,
            confidence=confidence,
            reliability=reliability,
            applicable=applicable,
            source=source,
            region=region,
            explanation=explanation,
            model_version=model_version,
            is_mock=is_mock,
        )
        self.db.add(ev)
        self.db.commit()

    def _collect_fusion_inputs(self, q_res, cls_res, mrz_res, ocr_res, tpl_res, forensic_signals, face_result, quality_reliability) -> List[FusionInput]:
        inputs = []

        # MRZ checksum
        inputs.append(FusionInput(
            signal="mrz_checksum",
            status=mrz_res.overall_status,
            confidence=0.98 if mrz_res.is_valid else 0.40,
            reliability=1.0,
            applicable=mrz_res.overall_status != "unavailable",
            source="mrz_parser",
            dimension="document_consistency",
            explanation=" | ".join(mrz_res.issues) if mrz_res.issues else "MRZ check digits and expiration validated.",
            is_mock=mrz_res.is_mock,
        ))

        # MRZ vs VIZ cross check
        if mrz_res.is_valid and ocr_res.fields:
            ocr_dob = next((f["value"] for f in ocr_res.fields if f["field_name"] == "date_of_birth"), None)
            if ocr_dob and mrz_res.date_of_birth and ocr_dob != mrz_res.date_of_birth:
                inputs.append(FusionInput(
                    signal="mrz_viz_mismatch",
                    status="mismatch_detected",
                    confidence=0.95,
                    reliability=0.95,
                    applicable=True,
                    source="cross_validator",
                    dimension="document_consistency",
                    explanation=f"MRZ DOB ({mrz_res.date_of_birth}) does not match OCR VIZ DOB ({ocr_dob}).",
                    root_cause_group="dob_alteration",
                    is_mock=ocr_res.is_mock,
                ))

        # MRZ date logic (expiration check)
        if mrz_res.expiry_date:
            try:
                from datetime import datetime
                exp_date = datetime.strptime(mrz_res.expiry_date, "%Y-%m-%d").date()
                if exp_date < datetime.now().date():
                    inputs.append(FusionInput(
                        signal="mrz_date_logic",
                        status="review",
                        confidence=0.99,
                        reliability=1.0,
                        applicable=True,
                        source="mrz_parser",
                        dimension="document_consistency",
                        explanation=f"Document expired on {mrz_res.expiry_date}.",
                        is_mock=mrz_res.is_mock,
                    ))
            except Exception:
                pass

        # Template / Unknown mode
        if cls_res.is_unknown_mode or tpl_res.status == "unknown":
            inputs.append(FusionInput(
                signal="template_alignment",
                status="unknown",
                confidence=0.50,
                reliability=0.80,
                applicable=True,
                source="classifier",
                dimension="structural_conformity",
                explanation="Document type is unknown. Mandatory manual review required.",
                is_mock=cls_res.is_mock,
            ))
        else:
            inputs.append(FusionInput(
                signal="template_alignment",
                status=tpl_res.status,
                confidence=tpl_res.alignment_score,
                reliability=0.85,
                applicable=True,
                source="template_validator",
                dimension="structural_conformity",
                explanation=" | ".join(tpl_res.deviations) if tpl_res.deviations else "Document geometric layout matches reference template.",
                is_mock=tpl_res.is_mock,
            ))

        # Forensics
        for sig in forensic_signals:
            inputs.append(FusionInput(
                signal=sig.signal,
                status=sig.status,
                confidence=sig.confidence,
                reliability=sig.reliability,
                applicable=sig.applicable,
                source=sig.detector_type,
                dimension="manipulation_evidence",
                explanation=sig.explanation,
                root_cause_group="dob_alteration" if sig.status == "high" and sig.region else None,
                is_mock=sig.is_mock,
            ))

        # Face
        if face_result:
            verifier = face_result.get("verifier")
            if verifier:
                inputs.append(FusionInput(
                    signal="face_similarity",
                    status=verifier.identity_status,
                    confidence=verifier.similarity_score,
                    reliability=0.90,
                    applicable=verifier.identity_status != "not_available",
                    source="face_verifier",
                    dimension="identity_consistency",
                    explanation=verifier.explanation,
                    is_mock=verifier.is_mock,
                ))

        return inputs
