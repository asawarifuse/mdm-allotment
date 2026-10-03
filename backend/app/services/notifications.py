from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.services.audit import write_audit


def create(db: Session, actor_id: str, actor_role: str, data: dict) -> Notification:
    n = Notification(
        recipient_uid=data.get("recipient_uid"),
        branch=data.get("branch"),
        title=data["title"],
        message=data["message"],
        created_by=actor_id,
    )
    db.add(n)
    write_audit(db, actor_id, actor_role, "send_notification",
                target=f"recipient={data.get('recipient_uid')},branch={data.get('branch')}",
                new_value=data["title"])
    db.commit()
    db.refresh(n)
    return n


def list_for_student(db: Session, uid: str, branch: str) -> list[Notification]:
    return (
        db.query(Notification)
        .filter(
            (Notification.recipient_uid == uid) |
            (Notification.branch == branch) |
            (Notification.recipient_uid.is_(None) & Notification.branch.is_(None))
        )
        .order_by(Notification.created_at.desc())
        .all()
    )


def mark_read(db: Session, notification_id: int, uid: str) -> bool:
    n = db.query(Notification).filter(Notification.id == notification_id).first()
    if not n:
        return False
    if n.recipient_uid and n.recipient_uid != uid:
        return False
    if not n.read_at:
        n.read_at = datetime.now(timezone.utc)
        db.commit()
    return True