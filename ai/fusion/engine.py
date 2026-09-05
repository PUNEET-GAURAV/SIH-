"""Evidence Fusion Engine — Build Spec §3, Solution Spec §12.

Rule-based, confidence/reliability/applicability-aware.
This is the core product novelty. No ML, fully unit-testable.

Key rules:
- Poor quality reduces reliability of downstream signals, never increases concern
- Signals sharing a root cause are not double-counted
- NOT_APPLICABLE and UNAVAILABLE signals are excluded, not treated as negative
- Contradictions are surfaced explicitly, not silently resolved
- Output is concern level + recommendation, never a probability-of-fraud number
"""

import logging
from dataclasses import dataclass, field
from typing import Optional

from backend.config import get_pipeline_config

logger = logging.getLogger("docshield.fusion")


@dataclass
class FusionInput:
    """A signal for the fusion engine to consider."""
    signal: str
    status: str
    confidence: float = 0.0
    reliability: float = 1.0
    applicable: bool = True
    source: str = ""
    dimension: str = ""  # document_consistency, structural_conformity, manipulation_evidence, identity_consistency
    explanation: str = ""
    root_cause_group: Optional[str] = None  # For grouping correlated signals
    is_mock: bool = False


@dataclass
class DimensionResult:
    """Assessment result for a single dimension."""
    dimension: str
    status: str
    signals: list = field(default_factory=list)
    weighted_score: float = 0.0
    explanation: str = ""


@dataclass
class FusionResult:
    """Output of the fusion engine."""
    concern_level: str  # low_concern, review_required, high_concern
    recommendation: str  # clear, request_recapture, secondary_inspection, escalate
    dimension_results: dict = field(default_factory=dict)
    contradictions: list = field(default_factory=list)
    summary: str = ""
    fusion_details: dict = field(default_factory=dict)
    is_mock: bool = False


class FusionEngine:
    """Rule-based evidence fusion engine.

    Processes all evidence signals and produces an overall
    concern level and recommendation for the officer.
    """

    # Status severity mapping
    STATUS_SEVERITY = {
        # Document consistency
        "pass": 0.0,
        "review": 0.55,
        "fail": 1.0,
        # Structural
        "conforming": 0.0,
        "deviation": 0.7,
        "unknown": 0.50,
        # Manipulation
        "low": 0.1,
        "medium": 0.5,
        "high": 0.9,
        # Identity
        "match": 0.0,
        "uncertain": 0.4,
        "mismatch": 0.9,
        # Generic
        "success": 0.0,
        "mismatch_detected": 0.8,
        "inconsistency": 0.7,
    }

    # Signal to dimension mapping
    SIGNAL_DIMENSIONS = {
        "mrz_checksum": "document_consistency",
        "mrz_viz_mismatch": "document_consistency",
        "mrz_date_logic": "document_consistency",
        "mrz_country_code": "document_consistency",
        "ocr_consistency": "document_consistency",
        "field_format": "document_consistency",
        "template_alignment": "structural_conformity",
        "field_position": "structural_conformity",
        "aspect_ratio": "structural_conformity",
        "geometric_anomaly": "structural_conformity",
        "copy_move": "manipulation_evidence",
        "manipulation_cnn": "manipulation_evidence",
        "compression_anomaly": "manipulation_evidence",
        "face_similarity": "identity_consistency",
        "face_quality": "identity_consistency",
        "pad_assessment": "identity_consistency",
        "quality_gate": "capture_quality",
    }

    def __init__(self, config: Optional[dict] = None):
        pipeline_config = get_pipeline_config()
        fusion_config = config or pipeline_config.get("fusion", {})
        self.weights = fusion_config.get("weights", {
            "document_consistency": 0.9,
            "structural_conformity": 0.7,
            "manipulation_evidence": 0.8,
            "identity_consistency": 0.8,
        })
        thresholds = fusion_config.get("concern_thresholds", {})
        self.review_threshold = thresholds.get("review_required", 0.4)
        self.high_threshold = thresholds.get("high_concern", 0.7)
        reliability_config = fusion_config.get("reliability_degradation", {})
        self.poor_quality_factor = reliability_config.get("poor_quality_factor", 0.5)

    def fuse(self, signals: list[FusionInput], quality_reliability: float = 1.0) -> FusionResult:
        """Run the fusion engine over all signals.

        Args:
            signals: List of FusionInput signals from all pipeline stages
            quality_reliability: Overall quality reliability factor (0-1)

        Returns:
            FusionResult with concern level and recommendation
        """
        # Step 1: Filter out non-applicable and unavailable signals
        active_signals = [s for s in signals if s.applicable and s.status not in ("not_applicable", "unavailable")]

        if not active_signals:
            return FusionResult(
                concern_level="review_required",
                recommendation="secondary_inspection",
                summary="No applicable signals available for assessment. Manual review required.",
                fusion_details={"reason": "no_active_signals"},
            )

        # Step 2: Apply quality degradation to reliability
        for s in active_signals:
            if quality_reliability < 1.0 and s.dimension != "capture_quality":
                s.reliability = s.reliability * quality_reliability

        # Step 3: Group signals by root cause to avoid double-counting
        grouped = self._group_by_root_cause(active_signals)

        # Step 4: Score each dimension
        dimension_results = self._score_dimensions(grouped)

        # Step 5: Detect contradictions
        contradictions = self._detect_contradictions(dimension_results)

        # Step 6: Compute overall concern
        overall_score = self._compute_overall_score(dimension_results)

        # Step 7: Determine concern level and recommendation
        concern_level = self._score_to_concern(overall_score)
        recommendation = self._concern_to_recommendation(concern_level, contradictions, quality_reliability)

        # Step 8: Generate summary
        summary = self._generate_summary(dimension_results, contradictions, concern_level)

        is_mock = any(s.is_mock for s in signals)

        return FusionResult(
            concern_level=concern_level,
            recommendation=recommendation,
            dimension_results={k: {
                "dimension": v.dimension,
                "status": v.status,
                "weighted_score": v.weighted_score,
                "explanation": v.explanation,
                "signal_count": len(v.signals),
            } for k, v in dimension_results.items()},
            contradictions=contradictions,
            summary=summary,
            fusion_details={
                "overall_score": overall_score,
                "active_signal_count": len(active_signals),
                "quality_reliability": quality_reliability,
            },
            is_mock=is_mock,
        )

    def _group_by_root_cause(self, signals: list[FusionInput]) -> list[FusionInput]:
        """Group signals by root cause and downweight duplicates.

        Signals that share a root_cause_group are not independently counted.
        The highest-severity signal in each group is kept at full weight;
        others in the same group get their reliability halved.
        """
        groups = {}
        for s in signals:
            group_key = (s.dimension, s.root_cause_group) if s.root_cause_group else (s.dimension, s.signal)
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(s)

        result = []
        for group_key, group_signals in groups.items():
            if len(group_signals) == 1:
                result.append(group_signals[0])
            else:
                # Sort by severity (highest first)
                sorted_sigs = sorted(
                    group_signals,
                    key=lambda s: self.STATUS_SEVERITY.get(s.status, 0.5),
                    reverse=True
                )
                # Keep the primary signal at full weight
                result.append(sorted_sigs[0])
                # Downweight the rest
                for s in sorted_sigs[1:]:
                    s.reliability *= 0.5
                    result.append(s)

        return result

    def _score_dimensions(self, signals: list[FusionInput]) -> dict[str, DimensionResult]:
        """Score each assessment dimension from its contributing signals."""
        dimensions = {}

        for s in signals:
            dim = s.dimension or self.SIGNAL_DIMENSIONS.get(s.signal, "other")
            if dim not in dimensions:
                dimensions[dim] = DimensionResult(dimension=dim, status="unknown")
            dimensions[dim].signals.append(s)

        for dim_name, dim_result in dimensions.items():
            if not dim_result.signals:
                continue

            # Weighted average severity
            total_weight = 0.0
            weighted_severity = 0.0
            explanations = []

            for s in dim_result.signals:
                severity = self.STATUS_SEVERITY.get(s.status, 0.5)
                weight = (s.confidence or 0.5) * (s.reliability or 0.5)
                weighted_severity += severity * weight
                total_weight += weight
                if s.explanation:
                    explanations.append(s.explanation)

            max_severity = max(self.STATUS_SEVERITY.get(s.status, 0.5) for s in dim_result.signals)

            if total_weight > 0:
                avg_score = weighted_severity / total_weight
                dim_result.weighted_score = max(avg_score, max_severity * 0.85)
            else:
                dim_result.weighted_score = max_severity

            # Determine dimension status
            if dim_result.weighted_score < 0.3:
                dim_result.status = "pass"
            elif dim_result.weighted_score < 0.6:
                dim_result.status = "review"
            else:
                dim_result.status = "concern"

            dim_result.explanation = " | ".join(explanations) if explanations else "No specific findings."

        return dimensions

    def _detect_contradictions(self, dimensions: dict[str, DimensionResult]) -> list[dict]:
        """Detect contradictions between dimensions.

        E.g., structural PASS + forensic HIGH is a contradiction that must be surfaced.
        """
        contradictions = []

        dim_statuses = {k: v.status for k, v in dimensions.items()}

        # Check structural vs forensic contradiction
        struct_status = dim_statuses.get("structural_conformity")
        forensic_status = dim_statuses.get("manipulation_evidence")
        if struct_status == "pass" and forensic_status == "concern":
            contradictions.append({
                "type": "structural_vs_forensic",
                "description": "Structural conformity appears normal but manipulation evidence shows concern. "
                               "This contradiction requires manual investigation.",
                "dimensions": ["structural_conformity", "manipulation_evidence"],
            })

        # Check document consistency vs identity
        doc_status = dim_statuses.get("document_consistency")
        id_status = dim_statuses.get("identity_consistency")
        if doc_status == "pass" and id_status == "concern":
            contradictions.append({
                "type": "document_vs_identity",
                "description": "Document appears internally consistent but face verification shows concern. "
                               "The document photo may not match the live face presented.",
                "dimensions": ["document_consistency", "identity_consistency"],
            })

        if doc_status == "concern" and id_status == "pass":
            contradictions.append({
                "type": "identity_vs_document",
                "description": "Face appears to match but document shows consistency issues. "
                               "Investigate document alterations.",
                "dimensions": ["document_consistency", "identity_consistency"],
            })

        return contradictions

    def _compute_overall_score(self, dimensions: dict[str, DimensionResult]) -> float:
        """Compute weighted overall concern score."""
        if not dimensions:
            return 0.5

        max_dim_score = max((d.weighted_score for k, d in dimensions.items() if k != "capture_quality"), default=0.0)

        total_weight = 0.0
        weighted_score = 0.0

        for dim_name, dim_result in dimensions.items():
            if dim_name == "capture_quality":
                continue  # Quality doesn't directly contribute to concern
            weight = self.weights.get(dim_name, 0.5)
            weighted_score += dim_result.weighted_score * weight
            total_weight += weight

        avg_score = (weighted_score / total_weight) if total_weight > 0 else 0.5
        return max(avg_score, max_dim_score)

    def _score_to_concern(self, score: float) -> str:
        """Map overall score to concern level."""
        if score >= self.high_threshold:
            return "high_concern"
        elif score >= self.review_threshold:
            return "review_required"
        else:
            return "low_concern"

    def _concern_to_recommendation(
        self, concern: str, contradictions: list, quality_reliability: float
    ) -> str:
        """Map concern level to a recommendation."""
        if quality_reliability < 0.5:
            return "request_recapture"
        if concern == "high_concern":
            return "escalate" if contradictions else "secondary_inspection"
        elif concern == "review_required":
            return "secondary_inspection"
        else:
            return "clear"

    def _generate_summary(
        self, dimensions: dict[str, DimensionResult],
        contradictions: list, concern: str
    ) -> str:
        """Generate a human-readable summary for the officer."""
        parts = []

        concern_labels = {
            "low_concern": "Low concern",
            "review_required": "Review required",
            "high_concern": "High concern",
        }
        parts.append(f"Overall assessment: {concern_labels.get(concern, concern)}.")

        # Summarize each dimension
        dim_labels = {
            "document_consistency": "Document consistency",
            "structural_conformity": "Structural conformity",
            "manipulation_evidence": "Manipulation evidence",
            "identity_consistency": "Identity consistency",
        }
        for dim_name, dim_result in dimensions.items():
            label = dim_labels.get(dim_name, dim_name)
            if dim_result.status == "concern":
                parts.append(f"⚠ {label}: Issues detected.")
            elif dim_result.status == "review":
                parts.append(f"⚡ {label}: Requires review.")
            elif dim_result.status == "pass":
                parts.append(f"✓ {label}: No issues found.")

        if contradictions:
            parts.append(f"⚠ {len(contradictions)} contradiction(s) detected between dimensions — see details.")

        parts.append("This is an AI screening result — not an authenticity determination.")

        return " ".join(parts)
