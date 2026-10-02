from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.course import Course
from app.schemas.preference import (
    PreferenceSubmit, PreferenceOut, PreferenceStatus,
)
from app.services import preferences as pref_service
from app.utils.deps import require_role

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.post("", response_model=PreferenceStatus)
def submit(
    body: PreferenceSubmit,
    user: dict = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    try:
        prefs = pref_service.submit_preferences(db, user["sub"], body.course_ids)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return _to_status(prefs, db)


@router.get("/me", response_model=PreferenceStatus)
def my_preferences(
    user: dict = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    prefs = pref_service.get_preferences(db, user["sub"])
    return _to_status(prefs, db)


def _to_status(prefs, db) -> PreferenceStatus:
    if not prefs:
        return PreferenceStatus(submitted=False, submitted_at=None, preferences=[])
    course_ids = [p.course_id for p in prefs]
    courses = {c.id: c for c in db.query(Course).filter(Course.id.in_(course_ids)).all()}
    items = [
        PreferenceOut(
            rank=p.rank,
            course_id=p.course_id,
            course_name=courses[p.course_id].course_name,
            branch_name=courses[p.course_id].branch_name,
        )
        for p in prefs
    ]
    return PreferenceStatus(
        submitted=True,
        submitted_at=prefs[0].submitted_at.isoformat() if prefs[0].submitted_at else None,
        preferences=items,
    )