import hashlib
import json

from sqlalchemy.orm import Session

from app.models.audit import AuditLog


GENESIS_HASH = "0" * 64


def _compute_hash(prev_hash: str, payload: dict) -> str:
    body = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256((prev_hash + body).encode()).hexdigest()


def write_audit(
    db: Session,
    actor_id: str,
    actor_role: str,
    action: str,
    target: str | None = None,
    old_value=None,
    new_value=None,
) -> AuditLog:
    last = db.query(AuditLog).order_by(AuditLog.id.desc()).first()
    prev_hash = last.entry_hash if last else GENESIS_HASH
    payload = {
        "actor_id": actor_id,
        "actor_role": actor_role,
        "action": action,
        "target": target,
        "old_value": str(old_value) if old_value is not None else None,
        "new_value": str(new_value) if new_value is not None else None,
    }
    entry = AuditLog(
        actor_id=actor_id,
        actor_role=actor_role,
        action=action,
        target=target,
        old_value=payload["old_value"],
        new_value=payload["new_value"],
        prev_hash=prev_hash,
        entry_hash=_compute_hash(prev_hash, payload),
    )
    db.add(entry)
    db.flush()
    return entry