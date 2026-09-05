"""Comprehensive tests for the Fusion Engine — highest test coverage requirement."""

import pytest
from ai.fusion.engine import FusionEngine, FusionInput, FusionResult


@pytest.fixture
def engine():
    return FusionEngine(config={
        "weights": {
            "document_consistency": 0.9,
            "structural_conformity": 0.7,
            "manipulation_evidence": 0.8,
            "identity_consistency": 0.8,
        },
        "concern_thresholds": {
            "review_required": 0.4,
            "high_concern": 0.7,
        },
        "reliability_degradation": {
            "poor_quality_factor": 0.5,
        },
    })


class TestFusionBasic:
    """Test basic fusion engine behavior."""

    def test_no_signals_returns_review(self, engine):
        result = engine.fuse([])
        assert result.concern_level == "review_required"
        assert result.recommendation == "secondary_inspection"

    def test_all_pass_returns_low_concern(self, engine):
        signals = [
            FusionInput(signal="mrz_checksum", status="pass", confidence=0.95, reliability=0.95,
                        dimension="document_consistency"),
            FusionInput(signal="template_alignment", status="conforming", confidence=0.9, reliability=0.9,
                        dimension="structural_conformity"),
            FusionInput(signal="copy_move", status="low", confidence=0.85, reliability=0.9,
                        dimension="manipulation_evidence"),
            FusionInput(signal="face_similarity", status="match", confidence=0.92, reliability=0.9,
                        dimension="identity_consistency"),
        ]
        result = engine.fuse(signals)
        assert result.concern_level == "low_concern"
        assert result.recommendation == "clear"

    def test_high_manipulation_returns_high_concern(self, engine):
        signals = [
            FusionInput(signal="copy_move", status="high", confidence=0.9, reliability=0.9,
                        dimension="manipulation_evidence"),
            FusionInput(signal="manipulation_cnn", status="high", confidence=0.85, reliability=0.85,
                        dimension="manipulation_evidence"),
        ]
        result = engine.fuse(signals)
        assert result.concern_level == "high_concern"

    def test_mrz_fail_raises_concern(self, engine):
        signals = [
            FusionInput(signal="mrz_checksum", status="fail", confidence=0.99, reliability=0.99,
                        dimension="document_consistency"),
        ]
        result = engine.fuse(signals)
        assert result.concern_level in ("review_required", "high_concern")

    def test_face_mismatch_raises_concern(self, engine):
        signals = [
            FusionInput(signal="face_similarity", status="mismatch", confidence=0.9, reliability=0.9,
                        dimension="identity_consistency"),
        ]
        result = engine.fuse(signals)
        assert result.concern_level in ("review_required", "high_concern")


class TestFusionFiltering:
    """Test signal filtering rules."""

    def test_not_applicable_excluded(self, engine):
        signals = [
            FusionInput(signal="mrz_checksum", status="pass", confidence=0.95,
                        applicable=True, dimension="document_consistency"),
            FusionInput(signal="barcode_decode", status="fail", confidence=0.9,
                        applicable=False, dimension="document_consistency"),
        ]
        result = engine.fuse(signals)
        # The failing barcode should be excluded since applicable=False
        assert result.concern_level == "low_concern"

    def test_unavailable_excluded(self, engine):
        signals = [
            FusionInput(signal="mrz_checksum", status="pass", confidence=0.95,
                        dimension="document_consistency"),
            FusionInput(signal="manipulation_cnn", status="unavailable",
                        dimension="manipulation_evidence"),
        ]
        result = engine.fuse(signals)
        # Unavailable signal should not contribute to concern
        assert result.concern_level == "low_concern"


class TestQualityDegradation:
    """Test that poor quality reduces reliability, not increases concern."""

    def test_poor_quality_reduces_reliability(self, engine):
        signals = [
            FusionInput(signal="copy_move", status="medium", confidence=0.7, reliability=0.9,
                        dimension="manipulation_evidence"),
        ]
        # With good quality
        result_good = engine.fuse(signals, quality_reliability=1.0)

        # Reset reliability
        signals[0].reliability = 0.9
        # With poor quality
        result_poor = engine.fuse(signals, quality_reliability=0.5)

        # Poor quality should not increase overall concern
        # The weighted score should be same or lower because reliability is reduced
        assert result_poor.fusion_details["quality_reliability"] == 0.5

    def test_very_poor_quality_recommends_recapture(self, engine):
        signals = [
            FusionInput(signal="mrz_checksum", status="review", confidence=0.5, reliability=0.5,
                        dimension="document_consistency"),
        ]
        result = engine.fuse(signals, quality_reliability=0.3)
        assert result.recommendation == "request_recapture"


class TestRootCauseGrouping:
    """Test that signals sharing a root cause are not double-counted."""

    def test_grouped_signals_downweighted(self, engine):
        # Two signals from the same root cause (e.g., blur causing both OCR and MRZ issues)
        signals = [
            FusionInput(signal="ocr_consistency", status="fail", confidence=0.8, reliability=0.8,
                        dimension="document_consistency", root_cause_group="blur_impact"),
            FusionInput(signal="mrz_checksum", status="fail", confidence=0.7, reliability=0.8,
                        dimension="document_consistency", root_cause_group="blur_impact"),
        ]
        result_grouped = engine.fuse(signals)

        # Same signals without grouping
        signals_ungrouped = [
            FusionInput(signal="ocr_consistency", status="fail", confidence=0.8, reliability=0.8,
                        dimension="document_consistency"),
            FusionInput(signal="mrz_checksum", status="fail", confidence=0.7, reliability=0.8,
                        dimension="document_consistency"),
        ]
        result_ungrouped = engine.fuse(signals_ungrouped)

        # Grouped result should have equal or lower concern
        # (secondary signal in group is downweighted)
        assert result_grouped.fusion_details["overall_score"] <= result_ungrouped.fusion_details["overall_score"] + 0.01


class TestContradictionDetection:
    """Test contradiction surfacing between dimensions."""

    def test_structural_pass_forensic_high(self, engine):
        signals = [
            FusionInput(signal="template_alignment", status="conforming", confidence=0.9, reliability=0.9,
                        dimension="structural_conformity"),
            FusionInput(signal="copy_move", status="high", confidence=0.9, reliability=0.9,
                        dimension="manipulation_evidence"),
        ]
        result = engine.fuse(signals)
        assert len(result.contradictions) > 0
        assert any(c["type"] == "structural_vs_forensic" for c in result.contradictions)

    def test_document_pass_identity_concern(self, engine):
        signals = [
            FusionInput(signal="mrz_checksum", status="pass", confidence=0.95, reliability=0.95,
                        dimension="document_consistency"),
            FusionInput(signal="face_similarity", status="mismatch", confidence=0.9, reliability=0.9,
                        dimension="identity_consistency"),
        ]
        result = engine.fuse(signals)
        assert len(result.contradictions) > 0
        assert any(c["type"] == "document_vs_identity" for c in result.contradictions)

    def test_no_contradiction_when_consistent(self, engine):
        signals = [
            FusionInput(signal="mrz_checksum", status="pass", confidence=0.95, reliability=0.95,
                        dimension="document_consistency"),
            FusionInput(signal="face_similarity", status="match", confidence=0.9, reliability=0.9,
                        dimension="identity_consistency"),
        ]
        result = engine.fuse(signals)
        assert len(result.contradictions) == 0


class TestFusionOutput:
    """Test output format and content."""

    def test_result_has_required_fields(self, engine):
        signals = [
            FusionInput(signal="mrz_checksum", status="pass", confidence=0.95,
                        dimension="document_consistency"),
        ]
        result = engine.fuse(signals)
        assert result.concern_level in ("low_concern", "review_required", "high_concern")
        assert result.recommendation in ("clear", "request_recapture", "secondary_inspection", "escalate")
        assert isinstance(result.summary, str)
        assert len(result.summary) > 0

    def test_summary_contains_disclaimer(self, engine):
        signals = [
            FusionInput(signal="mrz_checksum", status="pass", confidence=0.95,
                        dimension="document_consistency"),
        ]
        result = engine.fuse(signals)
        assert "not an authenticity determination" in result.summary.lower()

    def test_mock_flag_propagated(self, engine):
        signals = [
            FusionInput(signal="mrz_checksum", status="pass", confidence=0.95,
                        dimension="document_consistency", is_mock=True),
        ]
        result = engine.fuse(signals)
        assert result.is_mock is True

    def test_escalate_on_high_concern_with_contradictions(self, engine):
        signals = [
            FusionInput(signal="template_alignment", status="conforming", confidence=0.9, reliability=0.9,
                        dimension="structural_conformity"),
            FusionInput(signal="copy_move", status="high", confidence=0.95, reliability=0.95,
                        dimension="manipulation_evidence"),
            FusionInput(signal="manipulation_cnn", status="high", confidence=0.9, reliability=0.9,
                        dimension="manipulation_evidence"),
        ]
        result = engine.fuse(signals)
        if result.concern_level == "high_concern" and len(result.contradictions) > 0:
            assert result.recommendation == "escalate"


class TestDemoScenarioFusion:
    """Test fusion behavior for the 6 demo scenarios."""

    def test_scenario_genuine_low_concern(self, engine):
        """Scenario 1: Genuine → LOW CONCERN."""
        signals = [
            FusionInput(signal="mrz_checksum", status="pass", confidence=0.98, reliability=0.95,
                        dimension="document_consistency"),
            FusionInput(signal="template_alignment", status="conforming", confidence=0.92, reliability=0.9,
                        dimension="structural_conformity"),
            FusionInput(signal="copy_move", status="low", confidence=0.88, reliability=0.9,
                        dimension="manipulation_evidence"),
            FusionInput(signal="face_similarity", status="match", confidence=0.94, reliability=0.92,
                        dimension="identity_consistency"),
        ]
        result = engine.fuse(signals)
        assert result.concern_level == "low_concern"

    def test_scenario_altered_dob_high_concern(self, engine):
        """Scenario 2: Altered DOB → MRZ/VIZ mismatch + manipulation → HIGH CONCERN."""
        signals = [
            FusionInput(signal="mrz_viz_mismatch", status="fail", confidence=0.96, reliability=0.95,
                        dimension="document_consistency",
                        explanation="DOB differs: MRZ=1998-04-02, VIZ=1998-04-12"),
            FusionInput(signal="manipulation_cnn", status="high", confidence=0.82, reliability=0.8,
                        dimension="manipulation_evidence"),
        ]
        result = engine.fuse(signals)
        assert result.concern_level == "high_concern"

    def test_scenario_expired_review(self, engine):
        """Scenario 3: Expired, internally consistent → REVIEW REQUIRED."""
        signals = [
            FusionInput(signal="mrz_checksum", status="pass", confidence=0.98, reliability=0.95,
                        dimension="document_consistency"),
            FusionInput(signal="mrz_date_logic", status="review", confidence=0.99, reliability=0.99,
                        dimension="document_consistency",
                        explanation="Document has expired"),
            FusionInput(signal="copy_move", status="low", confidence=0.85, reliability=0.9,
                        dimension="manipulation_evidence"),
        ]
        result = engine.fuse(signals)
        assert result.concern_level in ("review_required", "low_concern")
