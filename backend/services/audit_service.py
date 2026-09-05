"""Audit service — hash-chained, append-only audit log."""

import hashlib
import json
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from backend.models.evidence import AuditLog


class AuditService:
    """Manages the tamper-evident, hash-chained audit log."""

    HASH_ALGORITHM = "sha256"

    def __init__(self, db: Session):
        self.db = db

    def _compute_hash(self, event_data: str, previous_hash: str) -> str:
        """Compute H_n = hash(event_n + H_{n-1})."""
        combined = event_data + previous_hash
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()

    def _get_last_hash(self, session_id: str) -> str:
        """Get the hash of the last audit entry for this session, or genesis hash."""
        last_entry = (
            self.db.query(AuditLog)
            .filter(AuditLog.session_id == session_id)
            .order_by(AuditLog.timestamp.desc())
            .first()
        )
        if last_entry:
            return last_entry.entry_hash
        return hashlib.sha256(b"genesis").hexdigest()

    def log_event(
        self,
        session_id: str,
        actor_id: str,
        event_type: str,
        payload: Optional[dict] = None,
    ) -> AuditLog:
        """Append an event to the audit chain."""
        payload_str = json.dumps(payload or {}, sort_keys=True)
        payload_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

        previous_hash = self._get_last_hash(session_id)
        event_data = json.dumps({
            "session_id": session_id,
            "actor_id": actor_id,
            "event_type": event_type,
            "payload_hash": payload_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }, sort_keys=True)

        entry_hash = self._compute_hash(event_data, previous_hash)

        entry = AuditLog(
            session_id=session_id,
            actor_id=actor_id,
            event_type=event_type,
            payload_hash=payload_hash,
            previous_hash=previous_hash,
            entry_hash=entry_hash,
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def get_audit_trail(self, session_id: str) -> list[AuditLog]:
        """Get ordered audit trail for a session."""
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.session_id == session_id)
            .order_by(AuditLog.timestamp.asc())
            .all()
        )

    def verify_chain(self, session_id: str) -> dict:
        """Verify the integrity of the audit chain. Returns verification result."""
        entries = self.get_audit_trail(session_id)

        if not entries:
            return {
                "valid": True,
                "total_entries": 0,
                "first_broken_link": None,
                "message": "No audit entries found for this session.",
            }

        genesis_hash = hashlib.sha256(b"genesis").hexdigest()

        for i, entry in enumerate(entries):
            expected_previous = entries[i - 1].entry_hash if i > 0 else genesis_hash
            if entry.previous_hash != expected_previous:
                return {
                    "valid": False,
                    "total_entries": len(entries),
                    "first_broken_link": i,
                    "message": f"Chain broken at entry {i}: expected previous_hash "
                               f"{expected_previous[:16]}... but found {entry.previous_hash[:16]}...",
                }

        return {
            "valid": True,
            "total_entries": len(entries),
            "first_broken_link": None,
            "message": f"Audit chain is intact. {len(entries)} entries verified.",
        }
