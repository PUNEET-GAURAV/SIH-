"""Officer decision and audit routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas import APIResponse, OfficerDecisionCreate, AuditLogResponse
from backend.services.screening_service import ScreeningService
from backend.services.audit_service import AuditService
from backend.utils.security import get_current_user
from backend.models.user import User
from backend.models.evidence import OfficerDecision, DecisionAction

router = APIRouter(tags=["officer"])


@router.post("/officer/decision")
def submit_decision(
    payload: OfficerDecisionCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit an officer decision for a screening session."""
    service = ScreeningService(db)
    audit = AuditService(db)

    session = service.get_session(payload.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        decision_action = DecisionAction(payload.decision)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid decision. Must be one of: {[d.value for d in DecisionAction]}",
        )

    # Check for existing decision
    existing = db.query(OfficerDecision).filter(
        OfficerDecision.session_id == payload.session_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Decision already submitted for this session")

    decision = OfficerDecision(
        session_id=payload.session_id,
        officer_id=user.id,
        decision=decision_action,
        notes=payload.notes,
    )
    db.add(decision)
    db.commit()
    db.refresh(decision)

    audit.log_event(
        session_id=payload.session_id,
        actor_id=user.id,
        event_type="officer_decision",
        payload={"decision": payload.decision, "notes": payload.notes},
    )

    return APIResponse(data={
        "id": decision.id,
        "session_id": decision.session_id,
        "decision": decision.decision.value,
        "notes": decision.notes,
        "created_at": decision.created_at.isoformat(),
    }).model_dump()


@router.get("/audit/{session_id}")
def get_audit_trail(
    session_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the audit trail for a session."""
    audit = AuditService(db)
    entries = audit.get_audit_trail(session_id)
    return APIResponse(data=[
        AuditLogResponse.model_validate(e).model_dump()
        for e in entries
    ]).model_dump()


@router.get("/audit/{session_id}/verify")
def verify_audit(
    session_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Verify the integrity of the audit chain for a session."""
    audit = AuditService(db)
    result = audit.verify_chain(session_id)
    return APIResponse(data=result).model_dump()
