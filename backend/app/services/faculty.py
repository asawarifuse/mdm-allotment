from sqlalchemy.orm import Session

from app.models.course import Course, CourseSeat
from app.models.preference import Preference
from app.models.student import Student
from app.services.audit import write_audit


def get_faculty_course(db: Session, branch: str) -> Course | None:
    return db.query(Course).filter(Course.branch_name == branch).first()


def get_students_who_selected(db: Session, course_id: int) -> list[dict]:
    rows = (
        db.query(Preference, Student)
        .join(Student, Student.uid == Preference.student_uid)
        .filter(Preference.course_id == course_id)
        .order_by(Preference.rank, Student.cgpa.desc())
        .all()
    )
    return [
        {
            "uid": s.uid,
            "name": s.name,
            "cgpa": s.cgpa,
            "parent_branch": s.parent_branch,
            "rank": p.rank,
        }
        for p, s in rows
    ]


def get_seats(db: Session, course_id: int) -> list[dict]:
    seats = (
        db.query(CourseSeat)
        .filter(CourseSeat.course_id == course_id)
        .order_by(CourseSeat.branch)
        .all()
    )
    return [
        {
            "branch": s.branch,
            "seats": s.seats,
            "filled_seats": s.filled_seats,
            "available": s.seats - s.filled_seats,
        }
        for s in seats
    ]


def update_seat(db: Session, course_id: int, branch: str, seats: int, actor_id: str) -> dict:
    if seats < 0:
        raise ValueError("Seats cannot be negative")
    row = (
        db.query(CourseSeat)
        .filter(CourseSeat.course_id == course_id, CourseSeat.branch == branch)
        .first()
    )
    if not row:
        raise ValueError(f"No seat row for course {course_id} branch {branch}")
    if row.filled_seats > 0:
        raise ValueError("Cannot edit seats after allotment has started for this course")

    old = row.seats
    row.seats = seats
    write_audit(db, actor_id, "branch_admin", "edit_seats",
                target=f"course={course_id},branch={branch}",
                old_value=old, new_value=seats)
    db.commit()
    return {"course_id": course_id, "branch": branch, "seats": seats, "old": old}