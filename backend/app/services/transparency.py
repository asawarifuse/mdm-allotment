from sqlalchemy.orm import Session

from app.models.allotment import Allotment
from app.models.course import Course, CourseSeat
from app.models.preference import Preference
from app.models.student import Student


def get_transparency(db: Session, uid: str) -> dict:
    student = db.query(Student).filter(Student.uid == uid).first()
    if not student:
        return {"error": "student not found"}

    # rank within branch by CGPA
    branch_students = (
        db.query(Student.uid, Student.cgpa)
        .filter(Student.parent_branch == student.parent_branch)
        .order_by(Student.cgpa.desc())
        .all()
    )
    total_in_branch = len(branch_students)
    rank_in_branch = next(
        (i + 1 for i, (u, _) in enumerate(branch_students) if u == uid), None
    )

    # their preferences
    prefs = (
        db.query(Preference)
        .filter(Preference.student_uid == uid)
        .order_by(Preference.rank)
        .all()
    )

    # for each preference, show if they got in + cutoff reason
    details = []
    for p in prefs:
        course = db.query(Course).filter(Course.id == p.course_id).first()
        if not course:
            continue

        seat_row = (
            db.query(CourseSeat)
            .filter(CourseSeat.course_id == course.id,
                    CourseSeat.branch == student.parent_branch)
            .first()
        )

        # who got in from same branch for this course (sorted by CGPA desc)
        admitted = (
            db.query(Allotment, Student)
            .join(Student, Student.uid == Allotment.student_uid)
            .filter(Allotment.course_id == course.id,
                    Allotment.branch == student.parent_branch)
            .order_by(Student.cgpa.desc())
            .all()
        )
        cutoff_cgpa = admitted[-1][1].cgpa if admitted else None

        allotted_here = (
            db.query(Allotment)
            .filter(Allotment.student_uid == uid,
                    Allotment.course_id == course.id)
            .first()
        )

        details.append({
            "rank": p.rank,
            "course_id": course.id,
            "course_name": course.course_name,
            "offering_branch": course.branch_name,
            "seats_for_your_branch": seat_row.seats if seat_row else 0,
            "admitted_from_your_branch": len(admitted),
            "cutoff_cgpa": cutoff_cgpa,
            "you_got_this": bool(allotted_here),
            "explanation": _explain(student.cgpa, cutoff_cgpa, bool(allotted_here), seat_row),
        })

    allotment = db.query(Allotment).filter(Allotment.student_uid == uid).first()
    allotted_course = None
    if allotment:
        c = db.query(Course).filter(Course.id == allotment.course_id).first()
        if c:
            allotted_course = {
                "course_id": c.id,
                "course_name": c.course_name,
                "offering_branch": c.branch_name,
                "choice_number": allotment.choice_number,
            }

    return {
        "uid": student.uid,
        "name": student.name,
        "cgpa": student.cgpa,
        "parent_branch": student.parent_branch,
        "rank_in_branch": rank_in_branch,
        "total_in_branch": total_in_branch,
        "allotted_course": allotted_course,
        "preference_details": details,
    }


def _explain(my_cgpa: float, cutoff: float | None, got: bool, seat_row) -> str:
    if got:
        return "You were allotted this course."
    if cutoff is None:
        return "No seats were filled from your branch."
    if seat_row and seat_row.seats == 0:
        return "No seats were reserved for your branch in this course."
    if my_cgpa >= cutoff:
        return f"Your CGPA ({my_cgpa}) matched the cutoff ({cutoff}), but seats filled before your rank."
    return f"Cutoff CGPA from your branch was {cutoff}. Yours ({my_cgpa}) was below."