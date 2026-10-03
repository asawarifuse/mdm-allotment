from sqlalchemy.orm import Session

from app.models.course import Course
from app.models.preference import Preference
from app.models.student import Student
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

    student = db.query(Student).filter(Student.uid == uid).first()
    if not student:
        raise ValueError("Student not found")

    for cid in course_ids:
        course = db.query(Course).filter(Course.id == cid).first()
        if not course:
            raise ValueError(f"Course id {cid} does not exist")
        if course.branch_name == student.parent_branch:
            raise ValueError(
                f"You cannot prefer '{course.course_name}' — it is offered by your own branch "
                f"({student.parent_branch})."
            )

    for rank, cid in enumerate(course_ids, start=1):
        db.add(Preference(student_uid=uid, course_id=cid, rank=rank))

    write_audit(db, uid, "student", "submit_preferences", target=uid,
                new_value=str(course_ids))
    db.commit()
    return get_preferences(db, uid)