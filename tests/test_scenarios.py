"""Integration tests for all 6 deterministic demo scenarios — Build Spec §12 & Solution Spec §26."""

import os
import pytest
import numpy as np
import cv2

from backend.services.screening_orchestrator import ScreeningOrchestrator
from backend.services.screening_service import ScreeningService
from backend.models.user import User, UserRole


def create_dummy_image(filepath: str):
    img = np.ones((600, 800, 3), dtype=np.uint8) * 200
    cv2.putText(img, "PASSPORT TEST", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
    cv2.imwrite(filepath, img)


def test_demo_scenarios_end_to_end(db_session):
    orchestrator = ScreeningOrchestrator(db_session)
    service = ScreeningService(db_session)

    scenarios = [
        ("genuine", "low_concern"),
        ("altered_dob", "high_concern"),
        ("expired", "review_required"),
        ("wrong_face", "high_concern"),
        ("poor_capture", "quality_failed"),
        ("unknown_document", "review_required"),
    ]

    dummy_path = "test_doc_scenario.jpg"
    create_dummy_image(dummy_path)

    try:
        user = db_session.query(User).filter_by(username="test_officer_scenarios").first()
        if not user:
            user = User(username="test_officer_scenarios", email="officer_scenario@test.com", password_hash="pw", role=UserRole.OFFICER)
            db_session.add(user)
            db_session.commit()

        for scenario, expected_concern_or_status in scenarios:
            session = service.create_session(user, notes=f"scenario:{scenario}")

            with open(dummy_path, "rb") as f:
                content = f.read()

            doc = service.save_document(
                session_id=session.id,
                file_content=content,
                filename="doc.jpg",
                mime_type="image/jpeg",
            )

            res = orchestrator.process_screening(session.id, user.id)

            if scenario == "poor_capture":
                assert res["status"] == "recapture_required", f"Scenario {scenario} failed, got status {res.get('status')}"
            else:
                assert res["status"] == "completed", f"Scenario {scenario} failed, got status {res.get('status')}"
                assert res["concern_level"] == expected_concern_or_status, f"Scenario '{scenario}' failed: expected {expected_concern_or_status}, got {res.get('concern_level')}"

    finally:
        if os.path.exists(dummy_path):
            os.remove(dummy_path)
