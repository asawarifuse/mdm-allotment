from sqlalchemy.orm import Session

from app.models.course import Course
from app.models.preference import Preference
from app.services.audit import write_audit


def get_preferences(db: Session, uid: str) -> list[Preference]:
    return (
        db.query(Preference)
        .filter(Preference.student_uid == uid)
        .order_by(Preference.rank)
        .all()
    )


def submit_preferences(db: Session, uid: str, course_ids: list[int]) -> list[Preference]:
    if get_preferences(db, uid):
        raise ValueError("Preferences already submitted and locked")

    if len(course_ids) != 6 or len(set(course_ids)) != 6:
        raise ValueError("Exactly 6 unique courses required")

    existing_ids = {c.id for c in db.query(Course.id).all()}
    for cid in course_ids:
        if cid not in existing_ids:
            raise ValueError(f"Course id {cid} does not exist")

    for rank, cid in enumerate(course_ids, start=1):
        db.add(Preference(student_uid=uid, course_id=cid, rank=rank))

    write_audit(db, uid, "student", "submit_preferences", target=uid,
                new_value=str(course_ids))
    db.commit()
    return get_preferences(db, uid)