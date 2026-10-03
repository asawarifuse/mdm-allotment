from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.notification import NotificationCreate, NotificationOut
from app.services import notifications as notif_service
from app.services import transparency as transparency_service
from app.utils.deps import require_role

router = APIRouter(tags=["notifications"])


def _to_out(n) -> NotificationOut:
    return NotificationOut(
        id=n.id, title=n.title, message=n.message, branch=n.branch,
        created_by=n.created_by,
        created_at=n.created_at.isoformat() if n.created_at else "",
        read=bool(n.read_at),
    )


@router.post("/admin/notifications", response_model=NotificationOut)
def send_notification(
    body: NotificationCreate,
    user: dict = Depends(require_role("main_admin", "branch_admin")),
    db: Session = Depends(get_db),
):
    if user["role"] == "branch_admin":
        if body.branch and body.branch.upper() != user.get("branch", "").upper():
            raise HTTPException(403, "Branch admins can only send to their own branch")
        body.branch = user.get("branch")

    n = notif_service.create(db, user["sub"], user["role"], body.model_dump())
    return _to_out(n)


@router.get("/student/notifications", response_model=list[NotificationOut])
def my_notifications(
    user: dict = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    branch = user.get("branch") or ""
    return [_to_out(n) for n in notif_service.list_for_student(db, user["sub"], branch)]


@router.post("/student/notifications/{nid}/read")
def mark_read(
    nid: int,
    user: dict = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    ok = notif_service.mark_read(db, nid, user["sub"])
    if not ok:
        raise HTTPException(404, "Not found")
    return {"ok": True}


@router.get("/student/transparency")
def transparency(
    user: dict = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    return transparency_service.get_transparency(db, user["sub"])